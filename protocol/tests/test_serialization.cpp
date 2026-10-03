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
    test_tile_delta_roundtrip();
    test_malformed_buffer_rejected();
    std::cout << "All CWM Serialization tests passed successfully!" << std::endl;
    return 0;
}
