// CDDA-Mineclonia CWM Framing
// Licensed under Apache-2.0
#pragma once

#include <cstdint>
#include <vector>
#include <cstddef>
#include <cstring>
#include <stdexcept>
#include <algorithm>


namespace cdda::cwm {

constexpr uint32_t MAX_FRAME_SIZE = 16 * 1024 * 1024;

class FramingError : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

// [4-byte unsigned big-endian payload length][nonempty payload]
class FrameEncoder {
public:
    static std::vector<uint8_t> encode(const uint8_t* data, size_t size) {
        if (!data || !size || size > MAX_FRAME_SIZE)
            throw FramingError("Invalid CWM payload length or pointer");
        std::vector<uint8_t> buffer(sizeof(uint32_t) + size);
        const uint32_t length = static_cast<uint32_t>(size);
        for (size_t i = 0; i < 4; ++i) buffer[i] = static_cast<uint8_t>(length >> ((3-i)*8));
        std::memcpy(buffer.data() + 4, data, size);
        return buffer;
    }
};

class FrameDecoder {
public:
    explicit FrameDecoder(size_t max_frame = MAX_FRAME_SIZE,
                          size_t max_buffer = MAX_FRAME_SIZE + sizeof(uint32_t))
        : max_frame_(max_frame), max_buffer_(max_buffer) {
        if (!max_frame || max_frame > MAX_FRAME_SIZE || max_buffer < max_frame + 4)
            throw std::invalid_argument("Invalid CWM decoder limits");
    }

    void append(const uint8_t* data, size_t size) {
        if (!size) return;
        if (!data || size > remaining_capacity())
            throw FramingError("CWM input buffer limit exceeded");
        if (pending_bytes() < 4 && pending_bytes() + size >= 4) {
            uint8_t prefix[4];
            const size_t pending = pending_bytes();
            if (pending) std::memcpy(prefix, buffer_.data() + head_, pending);
            std::memcpy(prefix + pending, data, 4 - pending);
            const size_t length = decode_length(prefix);
            if (!length || length > max_frame_)
                throw FramingError("Invalid CWM frame length");
        }
        // Compact only when necessary; do not shift the tail after every frame.
        if (buffer_.size() + size > max_buffer_) compact();
        if (buffer_.size() + size > buffer_.capacity())
            buffer_.reserve(std::min(max_buffer_, std::max(buffer_.size() + size,
                                                         buffer_.capacity() * 2)));
        buffer_.insert(buffer_.end(), data, data + size);
        next_frame_size(); // Validate the leading prefix as soon as available.
    }

    // Zero means incomplete; a zero-length wire frame is invalid.
    size_t next_frame_size() const {
        if (pending_bytes() < sizeof(uint32_t)) return 0;
        const size_t size = decode_length(buffer_.data() + head_);
        if (!size || size > max_frame_)
            throw FramingError("Invalid CWM frame length");
        return pending_bytes() >= 4 + size ? size : 0;
    }

    bool pop_frame(std::vector<uint8_t>& out_payload) {
        const size_t size = next_frame_size();
        if (!size) return false;
        const auto begin = buffer_.begin() + head_ + sizeof(uint32_t);
        out_payload.assign(begin, begin + size);
        head_ += sizeof(uint32_t) + size;
        if (head_ == buffer_.size()) reset();
        return true;
    }

    void reset() { buffer_.clear(); head_ = 0; }
    size_t pending_bytes() const { return buffer_.size() - head_; }
    size_t remaining_capacity() const { return max_buffer_ - pending_bytes(); }

private:
    static uint32_t decode_length(const uint8_t* p) {
        return (uint32_t(p[0]) << 24) | (uint32_t(p[1]) << 16) | (uint32_t(p[2]) << 8) | p[3];
    }
    void compact() {
        buffer_.erase(buffer_.begin(), buffer_.begin() + head_);
        head_ = 0;
    }
    size_t max_frame_, max_buffer_, head_{0};
    std::vector<uint8_t> buffer_;
};

} // namespace cdda::cwm
