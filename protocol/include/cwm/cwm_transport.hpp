// Transport-independent CWM message boundary. Payloads contain no backend types.
#pragma once
#include <cstdint>
#include <cstddef>
#include <vector>

namespace cdda::cwm {
enum class IpcCloseReason {
    None, LocalClose, PeerEof, TruncatedFrame, InvalidFrame, OutputLimit, IoError
};
struct IpcWork {
    size_t read_bytes{0}, written_bytes{0}, delivered_frames{0}, delivered_bytes{0};
    size_t read_calls{0}, write_calls{0};
};
class CwmTransport {
public:
    virtual ~CwmTransport() = default;
    virtual bool is_valid() const = 0;
    virtual bool send_message(const uint8_t*, size_t) = 0;
    // False may still accompany final complete messages; consume them first.
    virtual bool poll_and_receive(std::vector<std::vector<uint8_t>>&, int timeout_ms = 0) = 0;
    virtual void close(IpcCloseReason = IpcCloseReason::LocalClose) = 0;
    virtual IpcCloseReason close_reason() const = 0;
    virtual size_t pending_input_bytes() const = 0;
    virtual size_t queued_output_bytes() const = 0;
    virtual size_t queued_output_frames() const = 0;
    virtual const IpcWork& last_work() const = 0;
};
class CwmListener {
public:
    virtual ~CwmListener() = default;
    virtual bool start() = 0;
    virtual void stop() = 0;
    virtual bool poll_accept(int timeout_ms = 0) = 0;
    virtual bool has_client() const = 0;
    virtual CwmTransport* client() = 0;
};
}
