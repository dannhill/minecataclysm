// CDDA-Mineclonia CWM Protocol Helper Functions
// Licensed under Apache-2.0
#pragma once

#include "cwm_generated.h"
#include <flatbuffers/flatbuffers.h>
#include <string>
#include <vector>
#include <chrono>

namespace cdda::cwm {

constexpr uint16_t PROTOCOL_VERSION_MAJOR = 2;
constexpr uint16_t PROTOCOL_VERSION_MINOR = 30;

struct Identity { uint64_t session{0}, player{0}, connection{0}; };

inline uint64_t current_time_ms() {
    using namespace std::chrono;
    return duration_cast<milliseconds>(steady_clock::now().time_since_epoch()).count();
}

class MessageBuilder {
public:
    explicit MessageBuilder(uint64_t sequence_number = 0, uint64_t world_revision = 0,
                            Identity identity = {})
        : sequence_number_(sequence_number), world_revision_(world_revision), identity_(identity) {}

    flatbuffers::FlatBufferBuilder& builder() {
        return fbb_;
    }

    std::vector<uint8_t> build_quickbar_swap(uint64_t id, uint8_t source, uint8_t target,
            const std::string& expected_source, const std::string& expected_target) {
        auto p = CDDA::CWM::CreateQuickbarSwapRequestDirect(fbb_, id, source, target,
            expected_source.c_str(), expected_target.c_str());
        return finish_message(CDDA::CWM::Payload::QuickbarSwapRequest, p.Union());
    }
    std::vector<uint8_t> build_inventory_arrange(uint64_t id, uint64_t view, uint32_t item, uint32_t before) {
        auto p = CDDA::CWM::CreateInventoryArrangeRequest(fbb_, id, view, item, before);
        return finish_message(CDDA::CWM::Payload::InventoryArrangeRequest, p.Union());
    }
    std::vector<uint8_t> build_quickbar_bind(uint64_t id, uint8_t slot, uint64_t view, uint32_t item,
                                           const std::string& expected) {
        const auto request = CDDA::CWM::CreateQuickbarBindRequestDirect(fbb_, id, slot, view, item, expected.c_str());
        return finish_message(CDDA::CWM::Payload::QuickbarBindRequest, request.Union());
    }
    std::vector<uint8_t> build_quickbar_use(uint64_t id, uint8_t slot, const std::string& binding,
                                          CDDA::CWM::EquipmentAction action) {
        const auto request = CDDA::CWM::CreateQuickbarUseRequestDirect(fbb_, id, slot, binding.c_str(), action);
        return finish_message(CDDA::CWM::Payload::QuickbarUseRequest, request.Union());
    }

    std::vector<uint8_t> finish_message(CDDA::CWM::Payload payload_type, flatbuffers::Offset<void> payload_offset) {
        auto msg = CDDA::CWM::CreateCwmMessage(
            fbb_,
            sequence_number_,
            world_revision_,
            current_time_ms(),
            payload_type,
            payload_offset, identity_.session, identity_.player, identity_.connection
        );
        fbb_.Finish(msg);
        const uint8_t* ptr = fbb_.GetBufferPointer();
        size_t size = fbb_.GetSize();
        std::vector<uint8_t> result(ptr, ptr + size);
        fbb_.Clear();
        return result;
    }

    std::vector<uint8_t> build_mission_query(uint64_t query) {
        return finish_message(CDDA::CWM::Payload::MissionQueryRequest, CDDA::CWM::CreateMissionQueryRequest(fbb_,query).Union());
    }
    std::vector<uint8_t> build_mission_track(uint64_t command,uint64_t view,int mission,int expected) {
        return finish_message(CDDA::CWM::Payload::MissionTrackRequest, CDDA::CWM::CreateMissionTrackRequest(fbb_,command,view,mission,expected).Union());
    }
    std::vector<uint8_t> build_hello_request(const std::string& build_id, uint64_t client_id = 1) {
        auto b_id = fbb_.CreateString(build_id);
        auto hello = CDDA::CWM::CreateHelloRequest(fbb_, PROTOCOL_VERSION_MAJOR, PROTOCOL_VERSION_MINOR, b_id, client_id);
        return finish_message(CDDA::CWM::Payload::HelloRequest, hello.Union());
    }

    std::vector<uint8_t> build_hello_response(bool accepted, const std::string& server_build_id, const std::string& reject_reason = "", uint64_t next_command_id = 1) {
        auto b_id = fbb_.CreateString(server_build_id);
        auto reason = fbb_.CreateString(reject_reason);
        auto resp = CDDA::CWM::CreateHelloResponse(fbb_, PROTOCOL_VERSION_MAJOR, PROTOCOL_VERSION_MINOR, b_id, accepted, reason, next_command_id);
        return finish_message(CDDA::CWM::Payload::HelloResponse, resp.Union());
    }

    std::vector<uint8_t> build_move_request(uint64_t command_id, CDDA::CWM::MoveDirection dir) {
        auto req = CDDA::CWM::CreateMoveRequest(fbb_, command_id, dir);
        return finish_message(CDDA::CWM::Payload::MoveRequest, req.Union());
    }

    std::vector<uint8_t> build_interact_request(uint64_t command_id, int32_t x, int32_t y, int32_t z,
            CDDA::CWM::InteractAction action, uint32_t pickup_stack_index = 0,
            const std::string &pickup_type_id = {}, int32_t pickup_charges = 0,
            bool pickup_count_by_charges = false) {
        CDDA::CWM::Coord3i coord(x, y, z);
        auto req = CDDA::CWM::CreateInteractRequestDirect(
            fbb_, command_id, &coord, action, pickup_stack_index,
            pickup_type_id.empty() ? nullptr : pickup_type_id.c_str(),
            pickup_charges, pickup_count_by_charges);
        return finish_message(CDDA::CWM::Payload::InteractRequest, req.Union());
    }

    std::vector<uint8_t> build_movement_mode_request(uint64_t command_id, CDDA::CWM::MovementMode mode) {
        const auto req = CDDA::CWM::CreateMovementModeRequest(fbb_, command_id, mode);
        return finish_message(CDDA::CWM::Payload::MovementModeRequest, req.Union());
    }

    std::vector<uint8_t> build_ranged_request(uint64_t id, uint64_t weapon, uint64_t target, CDDA::CWM::RangedAction action) {
        auto req = CDDA::CWM::CreateRangedRequest(fbb_, id, weapon, target, action);
        return finish_message(CDDA::CWM::Payload::RangedRequest, req.Union());
    }
    std::vector<uint8_t> build_cancel_reload(uint64_t id, uint64_t token) {
        auto req = CDDA::CWM::CreateCancelReloadRequest(fbb_, id, token);
        return finish_message(CDDA::CWM::Payload::CancelReloadRequest, req.Union());
    }
    std::vector<uint8_t> build_cancel_disassembly(uint64_t id, uint64_t token) {
        auto req = CDDA::CWM::CreateCancelDisassemblyRequest(fbb_, id, token);
        return finish_message(CDDA::CWM::Payload::CancelDisassemblyRequest, req.Union());
    }
    std::vector<uint8_t> build_cancel_reading(uint64_t id, uint64_t token) {
        auto req = CDDA::CWM::CreateCancelReadingRequest(fbb_, id, token);
        return finish_message(CDDA::CWM::Payload::CancelReadingRequest, req.Union());
    }
    std::vector<uint8_t> build_trade_offer(uint64_t request, uint64_t trade, uint64_t quote, uint32_t item, int quantity) {
        return finish_message(CDDA::CWM::Payload::TradeOfferRequest,CDDA::CWM::CreateTradeOfferRequest(fbb_,request,trade,quote,item,quantity).Union());
    }
    std::vector<uint8_t> build_trade_commit(uint64_t command, uint64_t trade, uint64_t quote) {
        return finish_message(CDDA::CWM::Payload::TradeCommitRequest,CDDA::CWM::CreateTradeCommitRequest(fbb_,command,trade,quote).Union());
    }
    std::vector<uint8_t> build_trade_cancel(uint64_t trade) {
        return finish_message(CDDA::CWM::Payload::TradeCancelRequest,CDDA::CWM::CreateTradeCancelRequest(fbb_,trade).Union());
    }
    std::vector<uint8_t> build_talk_request(uint64_t id, uint64_t target) {
        auto req = CDDA::CWM::CreateTalkRequest(fbb_, id, target);
        return finish_message(CDDA::CWM::Payload::TalkRequest, req.Union());
    }
    std::vector<uint8_t> build_attack_request(uint64_t command_id, uint64_t target_entity_id) {
        const auto req = CDDA::CWM::CreateAttackRequest(fbb_, command_id, target_entity_id);
        return finish_message(CDDA::CWM::Payload::AttackRequest, req.Union());
    }

    std::vector<uint8_t> build_crafting_query(uint64_t query_id, const std::string& search, uint32_t batch, CDDA::CWM::CraftingFilter filter = CDDA::CWM::CraftingFilter::ALL) {
        const auto text = fbb_.CreateString(search);
        const auto request = CDDA::CWM::CreateCraftingQueryRequest(fbb_, query_id, text, batch, filter);
        return finish_message(CDDA::CWM::Payload::CraftingQueryRequest, request.Union());
    }
    std::vector<uint8_t> build_crafting_favorite(uint64_t id, uint64_t view, uint32_t entry, bool favorite, bool expected) {
        const auto request = CDDA::CWM::CreateCraftingFavoriteRequest(fbb_,id,view,entry,favorite,expected);
        return finish_message(CDDA::CWM::Payload::CraftingFavoriteRequest,request.Union());
    }
    std::vector<uint8_t> build_crafting_request(uint64_t id, uint64_t view, uint32_t entry) {
        const auto request = CDDA::CWM::CreateCraftingRequest(fbb_, id, view, entry);
        return finish_message(CDDA::CWM::Payload::CraftingRequest, request.Union());
    }
    std::vector<uint8_t> build_cancel_crafting(uint64_t id, uint64_t token) {
        const auto request = CDDA::CWM::CreateCancelCraftingRequest(fbb_, id, token);
        return finish_message(CDDA::CWM::Payload::CancelCraftingRequest, request.Union());
    }
    std::vector<uint8_t> build_item_transfer(uint64_t command, uint64_t view, uint32_t item,
            int quantity, uint32_t destination, CDDA::CWM::ItemTransferAction action) {
        auto request = CDDA::CWM::CreateItemTransferRequest(fbb_, command, view, item, quantity, destination, action);
        return finish_message(CDDA::CWM::Payload::ItemTransferRequest, request.Union());
    }
    std::vector<uint8_t> build_cancel_item_transfer(uint64_t command, uint64_t token) {
        auto request = CDDA::CWM::CreateCancelItemTransferRequest(fbb_, command, token);
        return finish_message(CDDA::CWM::Payload::CancelItemTransferRequest, request.Union());
    }
    std::vector<uint8_t> build_inventory_query(uint64_t query_id, const CDDA::CWM::Coord3i* external = nullptr) {
        const auto request = CDDA::CWM::CreateInventoryQueryRequest(fbb_, query_id, external);
        return finish_message(CDDA::CWM::Payload::InventoryQueryRequest, request.Union());
    }
    std::vector<uint8_t> build_equipment_request(uint64_t command_id, uint64_t view_id,
            uint32_t item_id, CDDA::CWM::EquipmentAction action) {
        const auto request = CDDA::CWM::CreateEquipmentRequest(fbb_, command_id, view_id, item_id, action);
        return finish_message(CDDA::CWM::Payload::EquipmentRequest, request.Union());
    }

    std::vector<uint8_t> build_cancel_first_aid(uint64_t command_id, uint64_t token) {
        const auto request = CDDA::CWM::CreateCancelFirstAidRequest(fbb_, command_id, token);
        return finish_message(CDDA::CWM::Payload::CancelFirstAidRequest, request.Union());
    }

    std::vector<uint8_t> build_cancel_consumption(uint64_t command_id, uint64_t token) {
        const auto request = CDDA::CWM::CreateCancelConsumptionRequest(fbb_, command_id, token);
        return finish_message(CDDA::CWM::Payload::CancelConsumptionRequest, request.Union());
    }
    std::vector<uint8_t> build_command_ack(uint64_t command_id, bool accepted, const std::string& err_msg = "", uint64_t result_revision = 0) {
        auto err = fbb_.CreateString(err_msg);
        auto ack = CDDA::CWM::CreateCommandAck(fbb_, command_id, accepted, err, result_revision);
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
    Identity identity_;
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
