// Shared bounded framing, FIFO queue and dispatch budget base class for POSIX and Windows transports.
// Licensed under Apache-2.0
#pragma once

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <deque>
#include <stdexcept>
#include <utility>
#include <vector>
#include "cwm_framing.hpp"
#include "cwm_transport.hpp"
#include "ipc_limits.hpp"

namespace cdda::cwm {

class FramedTransportBase : public CwmTransport {
public:
    explicit FramedTransportBase(IpcLimits limits = {})
        : limits_(limits), decoder_(limits.max_frame_bytes, limits.max_input_bytes) {
        if (!limits.max_output_bytes || !limits.max_output_frames ||
            !limits.read_bytes_per_pump || !limits.write_bytes_per_pump ||
            !limits.frames_per_pump || !limits.dispatch_bytes_per_pump ||
            !limits.syscalls_per_direction) {
            throw std::invalid_argument("Invalid CWM transport limits");
        }
    }

    FramedTransportBase(const FramedTransportBase&) = delete;
    FramedTransportBase& operator=(const FramedTransportBase&) = delete;

    FramedTransportBase(FramedTransportBase&& other) noexcept
        : limits_(other.limits_),
          decoder_(std::move(other.decoder_)),
          output_(std::move(other.output_)),
          output_bytes_(std::exchange(other.output_bytes_, 0)),
          output_offset_(std::exchange(other.output_offset_, 0)),
          read_eof_(other.read_eof_),
          write_failed_(other.write_failed_),
          dispatch_blocked_(other.dispatch_blocked_),
          reason_(other.reason_),
          work_(other.work_) {
        other.decoder_.reset();
    }

    FramedTransportBase& operator=(FramedTransportBase&& other) noexcept {
        if (this != &other) {
            using std::swap;
            swap(limits_, other.limits_);
            swap(decoder_, other.decoder_);
            swap(output_, other.output_);
            swap(output_bytes_, other.output_bytes_);
            swap(output_offset_, other.output_offset_);
            swap(read_eof_, other.read_eof_);
            swap(write_failed_, other.write_failed_);
            swap(dispatch_blocked_, other.dispatch_blocked_);
            swap(reason_, other.reason_);
            swap(work_, other.work_);
        }
        return *this;
    }

    IpcCloseReason close_reason() const override { return reason_; }
    size_t pending_input_bytes() const override { return decoder_.pending_bytes(); }
    size_t queued_output_bytes() const override { return output_bytes_; }
    size_t queued_output_frames() const override { return output_.size(); }
    const IpcWork& last_work() const override { return work_; }

    bool send_message(const uint8_t* data, size_t size) override {
        if (!is_valid() || read_eof_ || write_failed_) return false;
        if (!data || !size || size > limits_.max_frame_bytes) {
            close(IpcCloseReason::InvalidFrame);
            return false;
        }
        const size_t wire_size = size + sizeof(uint32_t);
        if (output_.size() >= limits_.max_output_frames ||
            wire_size > limits_.max_output_bytes - output_bytes_) {
            close(IpcCloseReason::OutputLimit);
            return false;
        }
        output_.push_back(FrameEncoder::encode(data, size));
        output_bytes_ += wire_size;
        return true;
    }

protected:
    bool dispatch_full() const {
        return dispatch_blocked_ || work_.delivered_frames >= limits_.frames_per_pump ||
               work_.delivered_bytes >= limits_.dispatch_bytes_per_pump;
    }

    void drain(std::vector<std::vector<uint8_t>>& frames) {
        while (!dispatch_full()) {
            const size_t size = decoder_.next_frame_size();
            if (!size) return;
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

    void reset_framed_state() {
        decoder_.reset();
        output_.clear();
        output_bytes_ = output_offset_ = 0;
    }

    void clear_output_on_write_error() {
        write_failed_ = true;
        output_.clear();
        output_bytes_ = output_offset_ = 0;
    }

    IpcLimits limits_;
    FrameDecoder decoder_;
    std::deque<std::vector<uint8_t>> output_;
    size_t output_bytes_{0}, output_offset_{0};
    bool read_eof_{false}, write_failed_{false};
    bool dispatch_blocked_{false};
    IpcCloseReason reason_{IpcCloseReason::None};
    IpcWork work_;
};

} // namespace cdda::cwm
