#pragma once
#include "cwm_framing.hpp"
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
}
