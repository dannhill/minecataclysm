// CWM Protocol Serialization Unit Tests
#include <cassert>
#include <iostream>
#include <vector>
#include "cwm/cwm_protocol.hpp"

using namespace cdda::cwm;

void test_hello_roundtrip() {
    MessageBuilder builder(1, 100);
    auto bytes = builder.build_hello_request("luanti_client_test_build_v1");

    assert(MessageVerifier::verify(bytes.data(), bytes.size()));
    const auto* msg = MessageVerifier::parse(bytes.data(), bytes.size());
    assert(msg != nullptr);
    assert(msg->sequence_number() == 1);
    assert(msg->world_revision() == 100);
    assert(msg->payload_type() == CDDA::CWM::Payload::HelloRequest);

    const auto* hello = msg->payload_as_HelloRequest();
    assert(hello != nullptr);
    assert(hello->protocol_version_major() == PROTOCOL_VERSION_MAJOR);
    assert(hello->protocol_version_minor() == PROTOCOL_VERSION_MINOR);
    assert(hello->build_id()->str() == "luanti_client_test_build_v1");
    std::cout << "[PASS] test_hello_roundtrip" << std::endl;
}

void test_move_request_roundtrip() {
    MessageBuilder builder(42, 105);
    auto bytes = builder.build_move_request(999, CDDA::CWM::MoveDirection::NORTH);

    assert(MessageVerifier::verify(bytes.data(), bytes.size()));
    const auto* msg = MessageVerifier::parse(bytes.data(), bytes.size());
    assert(msg != nullptr);
    assert(msg->sequence_number() == 42);
    assert(msg->world_revision() == 105);
    assert(msg->payload_type() == CDDA::CWM::Payload::MoveRequest);

    const auto* move = msg->payload_as_MoveRequest();
    assert(move != nullptr);
    assert(move->command_id() == 999);
    assert(move->direction() == CDDA::CWM::MoveDirection::NORTH);
    std::cout << "[PASS] test_move_request_roundtrip" << std::endl;
}

void test_pickup_request_roundtrip() {
    MessageBuilder builder(7, 123);
    auto bytes = builder.build_interact_request(
        77, 12, -4, 1, CDDA::CWM::InteractAction::PICKUP,
        3, "bottle_plastic", 17, true);

    assert(MessageVerifier::verify(bytes.data(), bytes.size()));
    const auto *msg = MessageVerifier::parse(bytes.data(), bytes.size());
    assert(msg && msg->payload_type() == CDDA::CWM::Payload::InteractRequest);

    const auto *req = msg->payload_as_InteractRequest();
    assert(req && req->command_id() == 77);
    assert(req->target_coord()->x() == 12 && req->target_coord()->y() == -4 &&
           req->target_coord()->z() == 1);
    assert(req->action() == CDDA::CWM::InteractAction::PICKUP);
    assert(req->pickup_stack_index() == 3);
    assert(req->pickup_type_id() && req->pickup_type_id()->str() == "bottle_plastic");
    assert(req->pickup_charges() == 17);
    assert(req->pickup_count_by_charges());
    std::cout << "[PASS] test_pickup_request_roundtrip" << std::endl;
}

void test_attack_request_roundtrip() {
    const uint64_t target = (uint64_t(1) << 63) | 187;
    MessageBuilder builder(11, 124, {101, 102, 103});
    const auto bytes = builder.build_attack_request(78, target);
    const auto* msg = MessageVerifier::parse(bytes.data(), bytes.size());
    assert(msg && msg->payload_type() == CDDA::CWM::Payload::AttackRequest);
    assert(msg->session_id() == 101 && msg->player_id() == 102 && msg->connection_id() == 103);
    const auto* req = msg->payload_as_AttackRequest();
    assert(req && req->command_id() == 78 && req->target_entity_id() == target);
    std::cout << "[PASS] test_attack_request_roundtrip" << std::endl;
}

void test_tile_delta_roundtrip() {
    MessageBuilder builder(10, 200);
    auto bytes = builder.build_tile_delta(15, -20, 1, 404, 0x01, 14, 2);

    assert(MessageVerifier::verify(bytes.data(), bytes.size()));
    const auto* msg = MessageVerifier::parse(bytes.data(), bytes.size());
    assert(msg != nullptr);
    assert(msg->payload_type() == CDDA::CWM::Payload::TileDelta);

    const auto* delta = msg->payload_as_TileDelta();
    assert(delta != nullptr);
    assert(delta->coord()->x() == 15);
    assert(delta->coord()->y() == -20);
    assert(delta->coord()->z() == 1);
    assert(delta->block()->material_id() == 404);
    assert(delta->block()->state_flags() == 0x01);
    assert(delta->block()->light_level() == 14);
    assert(delta->block()->orientation() == 2);
    std::cout << "[PASS] test_tile_delta_roundtrip" << std::endl;
}


void test_ground_item_snapshot_roundtrip() {
    flatbuffers::FlatBufferBuilder fbb;
    auto item = CDDA::CWM::CreateGroundItemStateDirect(fbb, 2, "bottle_plastic", "plastic bottle", 7, true);
    std::vector<flatbuffers::Offset<CDDA::CWM::GroundItemState>> items{item};
    CDDA::CWM::Coord3i coord(10, 20, 0);
    auto tile = CDDA::CWM::CreateGroundItemTileState(fbb, &coord, fbb.CreateVector(items));
    auto tiles = fbb.CreateVector(std::vector<flatbuffers::Offset<CDDA::CWM::GroundItemTileState>>{tile});
    CDDA::CWM::WorldSnapshotBuilder sb(fbb);
    sb.add_ground_item_tiles(tiles);
    auto snapshot = sb.Finish();
    auto msg = CDDA::CWM::CreateCwmMessage(fbb, 11, 300, 0, CDDA::CWM::Payload::WorldSnapshot, snapshot.Union());
    fbb.Finish(msg);

    const auto *parsed = MessageVerifier::parse(fbb.GetBufferPointer(), fbb.GetSize());
    assert(parsed && parsed->payload_as_WorldSnapshot());
    const auto *ground = parsed->payload_as_WorldSnapshot()->ground_item_tiles();
    assert(ground && ground->size() == 1 && ground->Get(0)->items()->size() == 1);
    const auto *got = ground->Get(0)->items()->Get(0);
    assert(got->stack_index() == 2 && got->type_id()->str() == "bottle_plastic");
    assert(got->name()->str() == "plastic bottle" && got->charges() == 7 && got->count_by_charges());
    std::cout << "[PASS] test_ground_item_snapshot_roundtrip" << std::endl;
}

void test_malformed_buffer_rejected() {
    std::vector<uint8_t> corrupted = {0xDE, 0xAD, 0xBE, 0xEF, 0x00, 0x01, 0x02};
    assert(!MessageVerifier::verify(corrupted.data(), corrupted.size()));
    assert(MessageVerifier::parse(corrupted.data(), corrupted.size()) == nullptr);

    assert(!MessageVerifier::verify(nullptr, 0));
    std::cout << "[PASS] test_malformed_buffer_rejected" << std::endl;
}

int main() {
    std::cout << "Running CWM Serialization Unit Tests..." << std::endl;
    test_hello_roundtrip();
    test_move_request_roundtrip();
    test_pickup_request_roundtrip();
    test_attack_request_roundtrip();
    test_tile_delta_roundtrip();
    test_ground_item_snapshot_roundtrip();
    test_malformed_buffer_rejected();
    std::cout << "All CWM Serialization tests passed successfully!" << std::endl;
    return 0;
}
