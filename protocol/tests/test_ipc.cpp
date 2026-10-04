// CWM IPC Socket Transport Unit Tests
#include <cassert>
#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
#include "cwm/ipc_transport.hpp"
#include "cwm/cwm_protocol.hpp"

using namespace cdda::cwm;

const std::string TEST_SOCKET = "/tmp/test_cdda_cwm_ipc_" + std::to_string(::getpid()) + ".sock";

void test_ipc_handshake_and_exchange() {
    IpcServer server(TEST_SOCKET);
    assert(server.start());

    // Connect client
    auto client = IpcClient::connect_unix(TEST_SOCKET);
    assert(client != nullptr);
    assert(client->is_valid());

    // Accept on server
    assert(server.poll_accept(500));
    assert(server.has_client());

    // Client sends Hello
    MessageBuilder client_builder(1, 0);
    auto hello_bytes = client_builder.build_hello_request("test_client");
    assert(client->send_message(hello_bytes.data(), hello_bytes.size()));
    std::vector<std::vector<uint8_t>> unused;
    assert(client->poll_and_receive(unused)); // Pump the queued Hello.

    // Server receives Hello
    std::vector<std::vector<uint8_t>> server_incoming;
    assert(server.client()->poll_and_receive(server_incoming, 500));
    assert(!server_incoming.empty());

    const auto* msg = MessageVerifier::parse(server_incoming[0].data(), server_incoming[0].size());
    assert(msg != nullptr);
    assert(msg->payload_type() == CDDA::CWM::Payload::HelloRequest);
    assert(msg->payload_as_HelloRequest()->build_id()->str() == "test_client");

    // Server responds with HelloResponse
    MessageBuilder server_builder(1, 1);
    auto resp_bytes = server_builder.build_hello_response(true, "test_cdda_server");
    assert(server.client()->send_message(resp_bytes.data(), resp_bytes.size()));
    assert(server.client()->poll_and_receive(unused));

    // Client receives HelloResponse
    std::vector<std::vector<uint8_t>> client_incoming;
    assert(client->poll_and_receive(client_incoming, 500));
    assert(!client_incoming.empty());

    const auto* resp_msg = MessageVerifier::parse(client_incoming[0].data(), client_incoming[0].size());
    assert(resp_msg != nullptr);
    assert(resp_msg->payload_type() == CDDA::CWM::Payload::HelloResponse);
    assert(resp_msg->payload_as_HelloResponse()->accepted());

    // Server sends TileDelta
    auto delta_bytes = server_builder.build_tile_delta(10, 20, 0, 101, 1, 15, 0);
    assert(server.client()->send_message(delta_bytes.data(), delta_bytes.size()));
    assert(server.client()->poll_and_receive(unused));

    client_incoming.clear();
    assert(client->poll_and_receive(client_incoming, 500));
    assert(!client_incoming.empty());
    const auto* delta_msg = MessageVerifier::parse(client_incoming[0].data(), client_incoming[0].size());
    assert(delta_msg != nullptr);
    assert(delta_msg->payload_type() == CDDA::CWM::Payload::TileDelta);
    assert(delta_msg->payload_as_TileDelta()->block()->material_id() == 101);

    // Client disconnects
    client->close_fd();
    assert(!client->is_valid());

    // Server detects disconnect
    server_incoming.clear();
    bool alive = server.client()->poll_and_receive(server_incoming, 100);
    assert(!alive || !server.client()->is_valid());

    server.stop();
    std::cout << "[PASS] test_ipc_handshake_and_exchange" << std::endl;
}

int main() {
    std::cout << "Running CWM IPC Transport Unit Tests..." << std::endl;
    test_ipc_handshake_and_exchange();
    std::cout << "All CWM IPC Transport tests passed successfully!" << std::endl;
    return 0;
}
