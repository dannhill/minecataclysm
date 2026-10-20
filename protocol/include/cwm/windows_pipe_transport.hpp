// Windows local named-pipe backend. Wire framing, budgets and session semantics
// are identical to POSIX. No Windows structures cross the CwmTransport boundary.
#pragma once
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <sddl.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <deque>
#include <memory>
#include <string>
#include <utility>
#include <vector>
#include "ipc_limits.hpp"
#include "cwm_transport.hpp"

namespace cdda::cwm {
inline std::wstring pipe_wide(const std::string &text) {
    const int n = MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, text.data(), int(text.size()), nullptr, 0);
    if (n <= 0) return {};
    std::wstring out(n, L'\0');
    MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, text.data(), int(text.size()), out.data(), n);
    return out;
}
inline bool local_pipe_name(const std::wstring &name) {
    return name.rfind(L"\\\\.\\pipe\\Minecataclysm-", 0) == 0 && name.size() < 240;
}
class IpcConnection : public CwmTransport {
public:
    explicit IpcConnection(HANDLE handle, IpcLimits limits = {}) : handle_(handle), limits_(limits),
        decoder_(limits.max_frame_bytes, limits.max_input_bytes) {
        if (!limits.max_output_bytes || !limits.max_output_frames || !limits.read_bytes_per_pump ||
            !limits.write_bytes_per_pump || !limits.frames_per_pump || !limits.dispatch_bytes_per_pump || !limits.syscalls_per_direction)
            { if (handle_ != INVALID_HANDLE_VALUE) CloseHandle(handle_); throw std::invalid_argument("Invalid CWM transport limits"); }
        read_.hEvent = CreateEventW(nullptr, TRUE, FALSE, nullptr);
        write_.hEvent = CreateEventW(nullptr, TRUE, FALSE, nullptr);
        if (!read_.hEvent || !write_.hEvent) close();
    }
    ~IpcConnection() {
        close();
        if (read_.hEvent) CloseHandle(read_.hEvent);
        if (write_.hEvent) CloseHandle(write_.hEvent);
    }
    IpcConnection(const IpcConnection&) = delete;
    IpcConnection& operator=(const IpcConnection&) = delete;
    bool is_valid() const override { return handle_ != INVALID_HANDLE_VALUE; }
    IpcCloseReason close_reason() const override { return reason_; }
    size_t pending_input_bytes() const override { return decoder_.pending_bytes(); }
    size_t queued_output_bytes() const override { return output_bytes_; }
    size_t queued_output_frames() const override { return output_.size(); }
    const IpcWork &last_work() const override { return work_; }
    void close(IpcCloseReason reason = IpcCloseReason::LocalClose) override {
        if (is_valid() || reason != IpcCloseReason::LocalClose) reason_ = reason;
        if (is_valid()) {
            CancelIoEx(handle_, nullptr);
            DWORD ignored;
            if (reading_) GetOverlappedResult(handle_, &read_, &ignored, TRUE);
            if (writing_) GetOverlappedResult(handle_, &write_, &ignored, TRUE);
            CloseHandle(handle_); handle_ = INVALID_HANDLE_VALUE;
        }
        reading_ = writing_ = false; decoder_.reset(); output_.clear(); output_bytes_ = offset_ = 0;
    }
    bool send_message(const uint8_t *data, size_t size) override {
        if (!is_valid() || eof_ || write_failed_) return false;
        if (!data || !size || size > limits_.max_frame_bytes) { close(IpcCloseReason::InvalidFrame); return false; }
        if (output_.size() >= limits_.max_output_frames || size + 4 > limits_.max_output_bytes - output_bytes_)
            { close(IpcCloseReason::OutputLimit); return false; }
        output_.push_back(FrameEncoder::encode(data, size)); output_bytes_ += size + 4;
        return true;
    }
    bool poll_and_receive(std::vector<std::vector<uint8_t>> &frames, int timeout_ms = 0) override {
        work_ = {}; blocked_ = false;
        if (!is_valid()) return false;
        try {
            drain(frames);
            pump_write();
            if (!is_valid()) return false;
            if (reading_ && timeout_ms > 0 && !work_.delivered_frames)
                WaitForSingleObject(read_.hEvent, DWORD(timeout_ms));
            while (!full() && !eof_ && work_.read_bytes < limits_.read_bytes_per_pump &&
                work_.read_calls < limits_.syscalls_per_direction) {
                DWORD count = 0;
                if (reading_) {
                    if (!GetOverlappedResult(handle_, &read_, &count, FALSE)) {
                        const DWORD error = GetLastError();
                        if (error == ERROR_IO_INCOMPLETE) break;
                        reading_ = false;
                        if (error == ERROR_BROKEN_PIPE || error == ERROR_PIPE_NOT_CONNECTED) { eof_ = true; break; }
                        close(IpcCloseReason::IoError); return false;
                    }
                    reading_ = false;
                } else {
                    size_t wanted = std::min({input_.size(), decoder_.remaining_capacity(), limits_.read_bytes_per_pump - work_.read_bytes});
                    if (decoder_.pending_bytes() < 4) wanted = std::min(wanted, 4 - decoder_.pending_bytes());
                    if (!wanted) throw FramingError("CWM input buffer exhausted");
                    ResetEvent(read_.hEvent); ++work_.read_calls;
                    if (!ReadFile(handle_, input_.data(), DWORD(wanted), &count, &read_)) {
                        const DWORD error = GetLastError();
                        if (error == ERROR_IO_PENDING) { reading_ = true; break; }
                        if (error == ERROR_BROKEN_PIPE || error == ERROR_PIPE_NOT_CONNECTED) { eof_ = true; break; }
                        close(IpcCloseReason::IoError); return false;
                    }
                }
                if (!count) { eof_ = true; break; }
                work_.read_bytes += count; decoder_.append(input_.data(), count); drain(frames);
            }
            if (eof_ && !decoder_.next_frame_size()) {
                close(decoder_.pending_bytes() ? IpcCloseReason::TruncatedFrame : IpcCloseReason::PeerEof); return false;
            }
            return is_valid();
        } catch (const FramingError&) { close(IpcCloseReason::InvalidFrame); return false; }
    }
private:
    bool full() const { return blocked_ || work_.delivered_frames >= limits_.frames_per_pump || work_.delivered_bytes >= limits_.dispatch_bytes_per_pump; }
    void drain(std::vector<std::vector<uint8_t>> &frames) {
        while (!full()) {
            const size_t size = decoder_.next_frame_size(); if (!size) return;
            if (work_.delivered_frames && size > limits_.dispatch_bytes_per_pump - work_.delivered_bytes) { blocked_ = true; return; }
            std::vector<uint8_t> frame; decoder_.pop_frame(frame); frames.push_back(std::move(frame));
            ++work_.delivered_frames; work_.delivered_bytes += size;
        }
    }
    void pump_write() {
        while (!write_failed_ && !output_.empty() && work_.written_bytes < limits_.write_bytes_per_pump && work_.write_calls < limits_.syscalls_per_direction) {
            DWORD count = 0;
            if (writing_) {
                if (!GetOverlappedResult(handle_, &write_, &count, FALSE)) {
                    if (GetLastError() == ERROR_IO_INCOMPLETE) return;
                    writing_ = false; write_failed_ = true; output_.clear(); output_bytes_ = offset_ = 0; return;
                }
                writing_ = false;
            } else {
                const size_t wanted = std::min(output_.front().size() - offset_, limits_.write_bytes_per_pump - work_.written_bytes);
                ResetEvent(write_.hEvent); ++work_.write_calls;
                if (!WriteFile(handle_, output_.front().data() + offset_, DWORD(wanted), &count, &write_)) {
                    if (GetLastError() == ERROR_IO_PENDING) { writing_ = true; return; }
                    writing_ = false; write_failed_ = true; output_.clear(); output_bytes_ = offset_ = 0; return;
                }
            }
            if (!count) { writing_ = false; write_failed_ = true; output_.clear(); output_bytes_ = offset_ = 0; return; }
            work_.written_bytes += count; offset_ += count;
            if (offset_ == output_.front().size()) { output_bytes_ -= output_.front().size(); output_.pop_front(); offset_ = 0; }
        }
    }
    HANDLE handle_{INVALID_HANDLE_VALUE};
    OVERLAPPED read_{}, write_{};
    bool reading_{false}, writing_{false}, eof_{false}, blocked_{false}, write_failed_{false};
    IpcLimits limits_; FrameDecoder decoder_; IpcWork work_;
    IpcCloseReason reason_{IpcCloseReason::None};
    std::array<uint8_t, 65536> input_{};
    std::deque<std::vector<uint8_t>> output_;
    size_t output_bytes_{0}, offset_{0};
};

class IpcServer : public CwmListener {
public:
    explicit IpcServer(const std::string &name, IpcLimits limits = {}) : name_(pipe_wide(name)), limits_(limits) {
        connect_.hEvent = CreateEventW(nullptr, TRUE, FALSE, nullptr);
    }
    ~IpcServer() { stop(); if (connect_.hEvent) CloseHandle(connect_.hEvent); }
    bool start() override { stop(); return connect_.hEvent && local_pipe_name(name_) && listen(); }
    void stop() override {
        active_.reset();
        if (listener_ != INVALID_HANDLE_VALUE) {
            CancelIoEx(listener_, nullptr); DWORD ignored;
            if (pending_) GetOverlappedResult(listener_, &connect_, &ignored, TRUE);
            CloseHandle(listener_); listener_ = INVALID_HANDLE_VALUE;
        }
        pending_ = connected_ = false;
    }
    bool poll_accept(int timeout_ms = 0) override {
        if (has_client()) return false;
        active_.reset();
        if (listener_ == INVALID_HANDLE_VALUE && !listen()) return false;
        if (!connected_ && pending_) {
            if (timeout_ms > 0) WaitForSingleObject(connect_.hEvent, DWORD(timeout_ms));
            DWORD ignored;
            if (!GetOverlappedResult(listener_, &connect_, &ignored, FALSE)) return false;
            pending_ = false; connected_ = true;
        }
        if (!connected_) return false;
        active_ = std::make_unique<IpcConnection>(std::exchange(listener_, INVALID_HANDLE_VALUE), limits_);
        connected_ = false;
        return has_client();
    }
    bool has_client() const override { return active_ && active_->is_valid(); }
    IpcConnection *client() override { return active_.get(); }
private:
    bool listen() {
        // Restrict the endpoint to this Windows account and SYSTEM, in addition
        // to rejecting remote clients. Default Everyone-readable ACLs are avoided.
        HANDLE token = nullptr; DWORD size = 0;
        if (!OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, &token)) return false;
        GetTokenInformation(token, TokenUser, nullptr, 0, &size);
        std::vector<uint8_t> data(size);
        const bool ok = GetTokenInformation(token, TokenUser, data.data(), size, &size); CloseHandle(token);
        LPWSTR sid = nullptr;
        if (!ok || !ConvertSidToStringSidW(reinterpret_cast<TOKEN_USER*>(data.data())->User.Sid, &sid)) return false;
        const std::wstring sddl = L"D:P(A;;GA;;;SY)(A;;GA;;;" + std::wstring(sid) + L")"; LocalFree(sid);
        PSECURITY_DESCRIPTOR descriptor = nullptr;
        if (!ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl.c_str(), SDDL_REVISION_1, &descriptor, nullptr)) return false;
        SECURITY_ATTRIBUTES security{sizeof(security), descriptor, FALSE};
        listener_ = CreateNamedPipeW(name_.c_str(), PIPE_ACCESS_DUPLEX | FILE_FLAG_OVERLAPPED | FILE_FLAG_FIRST_PIPE_INSTANCE,
            PIPE_TYPE_BYTE | PIPE_READMODE_BYTE | PIPE_WAIT | PIPE_REJECT_REMOTE_CLIENTS, 1, 65536, 65536, 0, &security);
        LocalFree(descriptor);
        if (listener_ == INVALID_HANDLE_VALUE) return false;
        ResetEvent(connect_.hEvent);
        connected_ = ConnectNamedPipe(listener_, &connect_) != FALSE;
        if (!connected_) {
            const DWORD error = GetLastError(); connected_ = error == ERROR_PIPE_CONNECTED; pending_ = error == ERROR_IO_PENDING;
            if (!connected_ && !pending_) { CloseHandle(listener_); listener_ = INVALID_HANDLE_VALUE; return false; }
        }
        return true;
    }
    std::wstring name_; IpcLimits limits_; HANDLE listener_{INVALID_HANDLE_VALUE};
    OVERLAPPED connect_{}; bool pending_{false}, connected_{false};
    std::unique_ptr<IpcConnection> active_;
};
class IpcClient {
public:
    static std::unique_ptr<IpcConnection> connect_unix(const std::string &endpoint, int timeout_ms = 2000) {
        const auto name = pipe_wide(endpoint); if (!local_pipe_name(name)) return nullptr;
        HANDLE pipe = CreateFileW(name.c_str(), GENERIC_READ | GENERIC_WRITE, 0, nullptr, OPEN_EXISTING, FILE_FLAG_OVERLAPPED, nullptr);
        if (pipe == INVALID_HANDLE_VALUE && timeout_ms > 0 && GetLastError() == ERROR_PIPE_BUSY && WaitNamedPipeW(name.c_str(), DWORD(timeout_ms)))
            pipe = CreateFileW(name.c_str(), GENERIC_READ | GENERIC_WRITE, 0, nullptr, OPEN_EXISTING, FILE_FLAG_OVERLAPPED, nullptr);
        if (pipe == INVALID_HANDLE_VALUE) return nullptr;
        auto result = std::make_unique<IpcConnection>(pipe); return result->is_valid() ? std::move(result) : nullptr;
    }
};
} // namespace cdda::cwm
