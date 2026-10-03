// CDDA-Mineclonia CWM Protocol Helper Functions
// Licensed under Apache-2.0
#pragma once

#include "cwm_generated.h"
#include <flatbuffers/flatbuffers.h>
#include <string>
#include <vector>
#include <chrono>

namespace cdda::cwm {

constexpr uint16_t PROTOCOL_VERSION_MAJOR = 1;
constexpr uint16_t PROTOCOL_VERSION_MINOR = 0;

inline uint64_t current_time_ms() {
    using namespace std::chrono;
    return duration_cast<milliseconds>(steady_clock::now().time_since_epoch()).count();
}

class MessageBuilder {
public:
    explicit MessageBuilder(uint64_t sequence_number = 0, uint64_t world_revision = 0)
        : sequence_number_(sequence_number), world_revision_(world_revision) {}

    flatbuffers::FlatBufferBuilder& builder() {
        return fbb_;
    }

    std::vector<uint8_t> finish_message(CDDA::CWM::Payload payload_type, flatbuffers::Offset<void> payload_offset) {
        auto msg = CDDA::CWM::CreateCwmMessage(
            fbb_,
            sequence_number_,
            world_revision_,
            current_time_ms(),
            payload_type,
            payload_offset
        );
        fbb_.Finish(msg);
        const uint8_t* ptr = fbb_.GetBufferPointer();
        size_t size = fbb_.GetSize();
        std::vector<uint8_t> result(ptr, ptr + size);
        fbb_.Clear();
        return result;
    }

    std::vector<uint8_t> build_hello_request(const std::string& build_id) {
        auto b_id = fbb_.CreateString(build_id);
        auto hello = CDDA::CWM::CreateHelloRequest(fbb_, PROTOCOL_VERSION_MAJOR, PROTOCOL_VERSION_MINOR, b_id);
        return finish_message(CDDA::CWM::Payload::HelloRequest, hello.Union());
    }

    std::vector<uint8_t> build_hello_response(bool accepted, const std::string& server_build_id, const std::string& reject_reason = "") {
        auto b_id = fbb_.CreateString(server_build_id);
        auto reason = fbb_.CreateString(reject_reason);
        auto resp = CDDA::CWM::CreateHelloResponse(fbb_, PROTOCOL_VERSION_MAJOR, PROTOCOL_VERSION_MINOR, b_id, accepted, reason);
        return finish_message(CDDA::CWM::Payload::HelloResponse, resp.Union());
    }

    std::vector<uint8_t> build_move_request(uint64_t command_id, CDDA::CWM::MoveDirection dir) {
        auto req = CDDA::CWM::CreateMoveRequest(fbb_, command_id, dir);
        return finish_message(CDDA::CWM::Payload::MoveRequest, req.Union());
    }

    std::vector<uint8_t> build_interact_request(uint64_t command_id, int32_t x, int32_t y, int32_t z, CDDA::CWM::InteractAction action) {
        CDDA::CWM::Coord3i coord(x, y, z);
        auto req = CDDA::CWM::CreateInteractRequest(fbb_, command_id, &coord, action);
        return finish_message(CDDA::CWM::Payload::InteractRequest, req.Union());
    }

    std::vector<uint8_t> build_command_ack(uint64_t command_id, bool accepted, const std::string& err_msg = "") {
        auto err = fbb_.CreateString(err_msg);
        auto ack = CDDA::CWM::CreateCommandAck(fbb_, command_id, accepted, err);
        return finish_message(CDDA::CWM::Payload::CommandAck, ack.Union());
    }

    std::vector<uint8_t> build_tile_delta(int32_t x, int32_t y, int32_t z, uint16_t material_id, uint32_t state_flags = 0, uint8_t light_level = 15, uint8_t orientation = 0) {
        CDDA::CWM::Coord3i coord(x, y, z);
        CDDA::CWM::CwmBlock block(state_flags, material_id, light_level, orientation);
        auto delta = CDDA::CWM::CreateTileDelta(fbb_, &coord, &block);
        return finish_message(CDDA::CWM::Payload::TileDelta, delta.Union());
    }

private:
    flatbuffers::FlatBufferBuilder fbb_{2048};
    uint64_t sequence_number_{0};
    uint64_t world_revision_{0};
};

class MessageVerifier {
public:
    static bool verify(const uint8_t* data, size_t size) {
        if (!data || size < 4) return false;
        flatbuffers::Verifier verifier(data, size);
        return CDDA::CWM::VerifyCwmMessageBuffer(verifier);
    }

    static const CDDA::CWM::CwmMessage* parse(const uint8_t* data, size_t size) {
        if (!verify(data, size)) return nullptr;
        return CDDA::CWM::GetCwmMessage(data);
    }
};

} // namespace cdda::cwm
