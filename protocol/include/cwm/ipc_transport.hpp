// CDDA-Mineclonia IPC Transport (POSIX Unix Domain Socket)
// Licensed under Apache-2.0
#pragma once

#include <algorithm>
#include <cerrno>
#include <deque>
#include <memory>
#include <string>
#include <utility>
#include <vector>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <fcntl.h>
#include <poll.h>
#include "cwm_framing.hpp"
#include "cwm_transport.hpp"
#include <arpa/inet.h>
#include <sys/stat.h>

namespace cdda::cwm {

struct IpcLimits {
    size_t max_frame_bytes{MAX_FRAME_SIZE};
    size_t max_input_bytes{MAX_FRAME_SIZE + 4};
    size_t max_output_bytes{32 * 1024 * 1024};
    size_t max_output_frames{128};
    size_t read_bytes_per_pump{256 * 1024};
    size_t write_bytes_per_pump{256 * 1024};
    size_t frames_per_pump{8};
    size_t dispatch_bytes_per_pump{1024 * 1024};
    size_t syscalls_per_direction{64};
};

inline bool configure_ipc_fd(int fd) {
    const int flags = ::fcntl(fd, F_GETFL, 0);
    const int fdflags = ::fcntl(fd, F_GETFD, 0);
    return flags >= 0 && fdflags >= 0 &&
           ::fcntl(fd, F_SETFL, flags | O_NONBLOCK) == 0 &&
           ::fcntl(fd, F_SETFD, fdflags | FD_CLOEXEC) == 0;
}

inline bool ipc_would_block(int error) {
#if EAGAIN != EWOULDBLOCK
    return error == EAGAIN || error == EWOULDBLOCK;
#else
    return error == EAGAIN;
#endif
}

class IpcConnection : public CwmTransport {
public:
    explicit IpcConnection(int fd, IpcLimits limits = {}) try
        : fd_(fd), limits_(limits), decoder_(limits.max_frame_bytes, limits.max_input_bytes) {
        if (!limits.max_output_bytes || !limits.max_output_frames ||
            !limits.read_bytes_per_pump || !limits.write_bytes_per_pump ||
            !limits.frames_per_pump || !limits.dispatch_bytes_per_pump ||
            !limits.syscalls_per_direction)
            throw std::invalid_argument("Invalid CWM transport limits");
        if (fd_ >= 0 && !configure_ipc_fd(fd_)) close_fd(IpcCloseReason::IoError);
    } catch (...) {
        if (fd >= 0) ::close(fd);
        throw;
    }
    ~IpcConnection() { close_fd(); }
    IpcConnection(const IpcConnection&) = delete;
    IpcConnection& operator=(const IpcConnection&) = delete;

    IpcConnection(IpcConnection&& other) noexcept
        : fd_(std::exchange(other.fd_, -1)), limits_(other.limits_),
          decoder_(std::move(other.decoder_)), output_(std::move(other.output_)),
          output_bytes_(std::exchange(other.output_bytes_, 0)),
          output_offset_(std::exchange(other.output_offset_, 0)),
          read_eof_(other.read_eof_), write_failed_(other.write_failed_),
          dispatch_blocked_(other.dispatch_blocked_), reason_(other.reason_), work_(other.work_) {
        other.decoder_.reset();
    }
    IpcConnection& operator=(IpcConnection&& other) noexcept {
        if (this != &other) {
            IpcConnection moved(std::move(other));
            using std::swap;
            swap(fd_, moved.fd_); swap(limits_, moved.limits_);
            swap(decoder_, moved.decoder_); swap(output_, moved.output_);
            swap(output_bytes_, moved.output_bytes_); swap(output_offset_, moved.output_offset_);
            swap(read_eof_, moved.read_eof_); swap(write_failed_, moved.write_failed_);
            swap(dispatch_blocked_, moved.dispatch_blocked_);
            swap(reason_, moved.reason_); swap(work_, moved.work_);
        }
        return *this;
    }

    bool is_valid() const { return fd_ >= 0; }
    int native_handle() const { return fd_; }
    IpcCloseReason close_reason() const { return reason_; }
    size_t pending_input_bytes() const { return decoder_.pending_bytes(); }
    // Counts retained allocations, including the already-written part of the head frame.
    size_t queued_output_bytes() const { return output_bytes_; }
    size_t queued_output_frames() const { return output_.size(); }
    const IpcWork& last_work() const { return work_; }

    void close(IpcCloseReason reason = IpcCloseReason::LocalClose) override { close_fd(reason); }
    void close_fd(IpcCloseReason reason = IpcCloseReason::LocalClose) {
        if (fd_ >= 0 || reason != IpcCloseReason::LocalClose) reason_ = reason;
        if (fd_ >= 0) { ::close(fd_); fd_ = -1; }
        decoder_.reset(); output_.clear(); output_bytes_ = output_offset_ = 0;
    }

    // True means accepted into the bounded FIFO, not delivered to the peer.
    // Only poll_and_receive pumps socket writes. No peer-dependent wait here.
    bool send_message(const uint8_t* data, size_t size) {
        if (!is_valid() || read_eof_ || write_failed_) return false;
        if (!data || !size || size > limits_.max_frame_bytes) {
            close_fd(IpcCloseReason::InvalidFrame); return false;
        }
        const size_t wire_size = size + sizeof(uint32_t);
        if (output_.size() >= limits_.max_output_frames ||
            wire_size > limits_.max_output_bytes - output_bytes_) {
            // Never discard a delta while keeping the session apparently coherent.
            close_fd(IpcCloseReason::OutputLimit); return false;
        }
        output_.push_back(FrameEncoder::encode(data, size));
        output_bytes_ += wire_size;
        return true;
    }

    // Bounded nonblocking I/O when timeout_ms == 0 (both runtime callers).
    // IMPORTANT: false may accompany final complete frames. Consume out_frames
    // before handling disconnect. EOF with remaining complete frames drains over
    // successive pumps. An incomplete tail is then classified as truncation.
    bool poll_and_receive(std::vector<std::vector<uint8_t>>& out_frames, int timeout_ms = 0) {
        work_ = {};
        dispatch_blocked_ = false;
        if (!is_valid()) return false;
        try {
            drain(out_frames);
            if (!dispatch_full() && !read_eof_) {
                pollfd pfd{fd_, static_cast<short>(POLLIN | (output_.empty() ? 0 : POLLOUT)), 0};
                const int ready = ::poll(&pfd, 1, work_.delivered_frames ? 0 : std::max(0, timeout_ms));
                if (ready < 0 && errno != EINTR) {
                    close_fd(IpcCloseReason::IoError); return false;
                }
                if (ready > 0 && (pfd.revents & POLLNVAL)) {
                    close_fd(IpcCloseReason::IoError); return false;
                }
                // HUP/ERR may accompany readable final bytes. recv establishes EOF.
                if (ready > 0 && (pfd.revents & (POLLIN | POLLHUP | POLLERR))) {
                    uint8_t buf[65536];
                    while (!dispatch_full() && work_.read_bytes < limits_.read_bytes_per_pump &&
                           work_.read_calls < limits_.syscalls_per_direction) {
                        size_t count = std::min({sizeof(buf), decoder_.remaining_capacity(),
                            limits_.read_bytes_per_pump - work_.read_bytes});
                        if (decoder_.pending_bytes() < 4)
                            count = std::min(count, 4 - decoder_.pending_bytes());
                        if (!count) throw FramingError("CWM input buffer exhausted");
                        ++work_.read_calls;
                        const ssize_t n = ::recv(fd_, buf, count, 0);
                        if (n > 0) {
                            work_.read_bytes += static_cast<size_t>(n);
                            decoder_.append(buf, static_cast<size_t>(n));
                            drain(out_frames);
                        } else if (n == 0) { read_eof_ = true; break; }
                        else if (ipc_would_block(errno)) {
                            if (write_failed_) { close_fd(IpcCloseReason::IoError); return false; }
                            break;
                        } else if (errno != EINTR) {
                            close_fd(IpcCloseReason::IoError); return false;
                        }
                    }
                }
                if (ready == 0 && write_failed_) {
                    close_fd(IpcCloseReason::IoError); return false;
                }
            }
            if (read_eof_ && !decoder_.next_frame_size()) {
                close_fd(decoder_.pending_bytes() ? IpcCloseReason::TruncatedFrame : IpcCloseReason::PeerEof);
                return false;
            }
            if (!read_eof_ && !write_failed_) flush_output();
            // On a failed write retain inbound bytes until recv drains them;
            // a large final frame may require several bounded pumps.
            return is_valid();
        } catch (const FramingError&) {
            close_fd(IpcCloseReason::InvalidFrame);
            return false;
        }
    }

private:
    bool dispatch_full() const {
        return dispatch_blocked_ || work_.delivered_frames >= limits_.frames_per_pump ||
               work_.delivered_bytes >= limits_.dispatch_bytes_per_pump;
    }
    void drain(std::vector<std::vector<uint8_t>>& frames) {
        while (!dispatch_full()) {
            const size_t size = decoder_.next_frame_size();
            if (!size) return;
            // Permit one legal large frame, otherwise bound the dispatch bytes.
            if (work_.delivered_frames && size > limits_.dispatch_bytes_per_pump - work_.delivered_bytes) {
                dispatch_blocked_ = true;
                return;
            }
            std::vector<uint8_t> payload;
            decoder_.pop_frame(payload);
            frames.push_back(std::move(payload));
            ++work_.delivered_frames;
            work_.delivered_bytes += size;
        }
    }
    void flush_output() {
        while (!output_.empty() && work_.written_bytes < limits_.write_bytes_per_pump &&
               work_.write_calls < limits_.syscalls_per_direction) {
            auto& head = output_.front();
            const size_t count = std::min(head.size() - output_offset_,
                limits_.write_bytes_per_pump - work_.written_bytes);
            ++work_.write_calls;
            const ssize_t n = ::send(fd_, head.data() + output_offset_, count, MSG_NOSIGNAL);
            if (n > 0) {
                output_offset_ += static_cast<size_t>(n);
                work_.written_bytes += static_cast<size_t>(n);
                if (output_offset_ == head.size()) {
                    output_bytes_ -= head.size(); output_.pop_front(); output_offset_ = 0;
                }
            } else if (n < 0 && ipc_would_block(errno)) return;
            else if (n < 0 && errno == EINTR) continue;
            else {
                write_failed_ = true;
                output_.clear(); output_bytes_ = output_offset_ = 0;
                return;
            }
        }
    }
    int fd_{-1};
    IpcLimits limits_;
    FrameDecoder decoder_;
    std::deque<std::vector<uint8_t>> output_;
    size_t output_bytes_{0}, output_offset_{0};
    bool read_eof_{false}, write_failed_{false};
    bool dispatch_blocked_{false};
    IpcCloseReason reason_{IpcCloseReason::None};
    IpcWork work_;
};

class IpcServer : public CwmListener {
public:
    explicit IpcServer(const std::string& socket_path, IpcLimits limits = {})
        : socket_path_(socket_path), limits_(limits) {}
    ~IpcServer() { stop(); }
    bool start() {
        stop();
        sockaddr_un addr{};
        if (socket_path_.empty() || socket_path_.size() >= sizeof(addr.sun_path)) return false;
        server_fd_ = ::socket(AF_UNIX, SOCK_STREAM, 0);
        if (server_fd_ < 0) return false;
        if (!configure_ipc_fd(server_fd_)) { stop(); return false; }
        addr.sun_family = AF_UNIX;
        std::memcpy(addr.sun_path, socket_path_.c_str(), socket_path_.size() + 1);
        if (::bind(server_fd_, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) { stop(); return false; }
        bound_ = true;
        if (::chmod(socket_path_.c_str(), 0600) < 0 || ::listen(server_fd_, 4) < 0) { stop(); return false; }
        return true;
    }
    void stop() {
        active_client_.reset();
        if (server_fd_ >= 0) {
            ::close(server_fd_); server_fd_ = -1;
            if (bound_) ::unlink(socket_path_.c_str());
            bound_ = false;
        }
    }
    // Single-client ownership: an additional live peer cannot replace it.
    bool poll_accept(int timeout_ms = 0) {
        if (server_fd_ < 0) return false;
        pollfd pfd{server_fd_, POLLIN, 0};
        if (::poll(&pfd, 1, std::max(0, timeout_ms)) > 0 && (pfd.revents & POLLIN)) {
            const int fd = ::accept(server_fd_, nullptr, nullptr);
            if (fd >= 0) {
                if (has_client()) { ::close(fd); return false; }
                active_client_ = std::make_unique<IpcConnection>(fd, limits_);
                return has_client();
            }
        }
        return false;
    }
    bool has_client() const { return active_client_ && active_client_->is_valid(); }
    IpcConnection* client() { return active_client_.get(); }
private:
    std::string socket_path_;
    IpcLimits limits_;
    int server_fd_{-1};
    bool bound_{false};
    std::unique_ptr<IpcConnection> active_client_;
};

class IpcClient {
public:
    static std::unique_ptr<IpcConnection> connect_unix(const std::string& socket_path,
                                                     int timeout_ms = 2000) {
        sockaddr_un addr{};
        if (socket_path.empty() || socket_path.size() >= sizeof(addr.sun_path)) return nullptr;
        const int fd = ::socket(AF_UNIX, SOCK_STREAM, 0);
        if (fd < 0) return nullptr;
        auto connection = std::make_unique<IpcConnection>(fd);
        if (!connection->is_valid()) return nullptr;
        addr.sun_family = AF_UNIX;
        std::memcpy(addr.sun_path, socket_path.c_str(), socket_path.size() + 1);
        if (::connect(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) == 0) return connection;
        if (errno != EINPROGRESS || timeout_ms <= 0) return nullptr;
        pollfd pfd{fd, POLLOUT, 0};
        if (::poll(&pfd, 1, timeout_ms) <= 0) return nullptr;
        int error = 0;
        socklen_t size = sizeof(error);
        if (::getsockopt(fd, SOL_SOCKET, SO_ERROR, &error, &size) < 0 || error) return nullptr;
        return connection;
    }
};

} // namespace cdda::cwm
