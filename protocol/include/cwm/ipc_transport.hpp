// CDDA-Mineclonia IPC Transport (POSIX Unix Domain Socket + TCP loopback)
// Licensed under Apache-2.0
#pragma once

#include <string>
#include <vector>
#include <memory>
#include <functional>
#include <cstdint>
#include <sys/socket.h>
#include <sys/un.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <poll.h>
#include "cwm_framing.hpp"

namespace cdda::cwm {

class IpcConnection {
public:
    explicit IpcConnection(int fd) : fd_(fd) {
        set_nonblocking(fd_);
    }

    ~IpcConnection() {
        close_fd();
    }

    // Disable copy
    IpcConnection(const IpcConnection&) = delete;
    IpcConnection& operator=(const IpcConnection&) = delete;

    // Allow move
    IpcConnection(IpcConnection&& other) noexcept : fd_(other.fd_), decoder_(std::move(other.decoder_)) {
        other.fd_ = -1;
    }

    IpcConnection& operator=(IpcConnection&& other) noexcept {
        if (this != &other) {
            close_fd();
            fd_ = other.fd_;
            decoder_ = std::move(other.decoder_);
            other.fd_ = -1;
        }
        return *this;
    }

    bool is_valid() const {
        return fd_ >= 0;
    }

    void close_fd() {
        if (fd_ >= 0) {
            ::close(fd_);
            fd_ = -1;
        }
    }

    int native_handle() const {
        return fd_;
    }

    bool send_message(const uint8_t* data, size_t size) {
        if (fd_ < 0) return false;
        std::vector<uint8_t> frame = FrameEncoder::encode(data, size);
        size_t total_sent = 0;
        while (total_sent < frame.size()) {
            ssize_t n = ::send(fd_, frame.data() + total_sent, frame.size() - total_sent, MSG_NOSIGNAL);
            if (n < 0) {
                if (errno == EAGAIN) {
                    struct pollfd pfd{fd_, POLLOUT, 0};
                    int ret = ::poll(&pfd, 1, 100);
                    if (ret > 0 && (pfd.revents & POLLOUT)) {
                        continue;
                    }
                }
                close_fd();
                return false;
            }
            if (n == 0) {
                close_fd();
                return false;
            }
            total_sent += static_cast<size_t>(n);
        }
        return true;
    }

    // Reads pending data into decoder and returns any complete extracted frames.
    // Returns false if connection was closed or errored.
    bool poll_and_receive(std::vector<std::vector<uint8_t>>& out_frames, int timeout_ms = 0) {
        if (fd_ < 0) return false;

        struct pollfd pfd{fd_, POLLIN, 0};
        int ret = ::poll(&pfd, 1, timeout_ms);
        if (ret < 0) {
            if (errno == EINTR) return true;
            close_fd();
            return false;
        }
        if (ret == 0) {
            // No new data, but check if decoder already has frames
            std::vector<uint8_t> payload;
            while (decoder_.pop_frame(payload)) {
                out_frames.push_back(std::move(payload));
            }
            return true;
        }

        if (pfd.revents & (POLLERR | POLLHUP | POLLNVAL)) {
            close_fd();
            return false;
        }

        if (pfd.revents & POLLIN) {
            uint8_t buf[65536];
            while (true) {
                ssize_t n = ::recv(fd_, buf, sizeof(buf), 0);
                if (n > 0) {
                    decoder_.append(buf, static_cast<size_t>(n));
                } else if (n == 0) {
                    // Connection closed cleanly by remote peer
                    close_fd();
                    return false;
                } else {
                    if (errno == EAGAIN) {
                        break; // all available data consumed
                    }
                    if (errno == EINTR) {
                        continue;
                    }
                    close_fd();
                    return false;
                }
            }
        }

        std::vector<uint8_t> payload;
        while (decoder_.pop_frame(payload)) {
            out_frames.push_back(std::move(payload));
        }
        return true;
    }

private:
    int fd_{-1};
    FrameDecoder decoder_;

    static void set_nonblocking(int fd) {
        int flags = ::fcntl(fd, F_GETFL, 0);
        if (flags >= 0) {
            ::fcntl(fd, F_SETFL, flags | O_NONBLOCK);
        }
    }
};

class IpcServer {
public:
    explicit IpcServer(const std::string& socket_path) : socket_path_(socket_path) {}

    ~IpcServer() {
        stop();
    }

    bool start() {
        stop();
        server_fd_ = ::socket(AF_UNIX, SOCK_STREAM, 0);
        if (server_fd_ < 0) return false;

        ::unlink(socket_path_.c_str());

        struct sockaddr_un addr{};
        addr.sun_family = AF_UNIX;
        std::strncpy(addr.sun_path, socket_path_.c_str(), sizeof(addr.sun_path) - 1);

        if (::bind(server_fd_, reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0) {
            stop();
            return false;
        }

        if (::listen(server_fd_, 4) < 0) {
            stop();
            return false;
        }

        set_nonblocking(server_fd_);
        return true;
    }

    void stop() {
        if (active_client_) {
            active_client_->close_fd();
            active_client_.reset();
        }
        if (server_fd_ >= 0) {
            ::close(server_fd_);
            server_fd_ = -1;
            ::unlink(socket_path_.c_str());
        }
    }

    // Accepts incoming connection if any. Single client model per specification.
    bool poll_accept(int timeout_ms = 0) {
        if (server_fd_ < 0) return false;

        struct pollfd pfd{server_fd_, POLLIN, 0};
        int ret = ::poll(&pfd, 1, timeout_ms);
        if (ret > 0 && (pfd.revents & POLLIN)) {
            int client_fd = ::accept(server_fd_, nullptr, nullptr);
            if (client_fd >= 0) {
                active_client_ = std::make_unique<IpcConnection>(client_fd);
                return true;
            }
        }
        return false;
    }

    bool has_client() const {
        return active_client_ && active_client_->is_valid();
    }

    IpcConnection* client() {
        return active_client_.get();
    }

private:
    std::string socket_path_;
    int server_fd_{-1};
    std::unique_ptr<IpcConnection> active_client_;

    static void set_nonblocking(int fd) {
        int flags = ::fcntl(fd, F_GETFL, 0);
        if (flags >= 0) {
            ::fcntl(fd, F_SETFL, flags | O_NONBLOCK);
        }
    }
};

class IpcClient {
public:
    static std::unique_ptr<IpcConnection> connect_unix(const std::string& socket_path, int timeout_ms = 2000) {
        (void)timeout_ms;
        int fd = ::socket(AF_UNIX, SOCK_STREAM, 0);
        if (fd < 0) return nullptr;

        struct sockaddr_un addr{};
        addr.sun_family = AF_UNIX;
        std::strncpy(addr.sun_path, socket_path.c_str(), sizeof(addr.sun_path) - 1);

        if (::connect(fd, reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0) {
            ::close(fd);
            return nullptr;
        }

        return std::make_unique<IpcConnection>(fd);
    }
};

} // namespace cdda::cwm
