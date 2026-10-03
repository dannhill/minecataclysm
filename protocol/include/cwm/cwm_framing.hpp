// CDDA-Mineclonia CWM Framing
// Licensed under Apache-2.0
#pragma once

#include <cstdint>
#include <vector>
#include <cstddef>
#include <cstring>
#include <stdexcept>
#include <arpa/inet.h>

namespace cdda::cwm {

constexpr uint32_t MAX_FRAME_SIZE = 16 * 1024 * 1024; // 16 MB max frame size

// Encapsulates a length-prefixed frame: [4-byte big-endian length][payload]
class FrameEncoder {
public:
    static std::vector<uint8_t> encode(const uint8_t* data, size_t size) {
        if (size > MAX_FRAME_SIZE) {
            throw std::runtime_error("Payload exceeds MAX_FRAME_SIZE");
        }
        std::vector<uint8_t> buffer(sizeof(uint32_t) + size);
        uint32_t net_len = htonl(static_cast<uint32_t>(size));
        std::memcpy(buffer.data(), &net_len, sizeof(uint32_t));
        if (size > 0 && data != nullptr) {
            std::memcpy(buffer.data() + sizeof(uint32_t), data, size);
        }
        return buffer;
    }
};

class FrameDecoder {
public:
    void append(const uint8_t* data, size_t size) {
        buffer_.insert(buffer_.end(), data, data + size);
    }

    // Attempts to extract the next complete frame payload.
    // Returns true if a frame was extracted into out_payload, false if incomplete.
    bool pop_frame(std::vector<uint8_t>& out_payload) {
        if (buffer_.size() < sizeof(uint32_t)) {
            return false;
        }

        uint32_t net_len = 0;
        std::memcpy(&net_len, buffer_.data(), sizeof(uint32_t));
        uint32_t frame_len = ntohl(net_len);

        if (frame_len > MAX_FRAME_SIZE) {
            buffer_.clear();
            throw std::runtime_error("Incoming frame exceeds MAX_FRAME_SIZE, connection corrupted");
        }

        size_t total_needed = sizeof(uint32_t) + frame_len;
        if (buffer_.size() < total_needed) {
            return false;
        }

        out_payload.assign(buffer_.begin() + sizeof(uint32_t), buffer_.begin() + total_needed);
        buffer_.erase(buffer_.begin(), buffer_.begin() + total_needed);
        return true;
    }

    void reset() {
        buffer_.clear();
    }

    size_t pending_bytes() const {
        return buffer_.size();
    }

private:
    std::vector<uint8_t> buffer_;
};

} // namespace cdda::cwm
