// Behavioral tests of bounded framing/transport. Checks remain active in Release.
#include "cwm/ipc_transport.hpp"
#include <chrono>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <thread>

using namespace cdda::cwm;
#define CHECK(...) do { if (!(__VA_ARGS__)) throw std::runtime_error(#__VA_ARGS__); } while (false)

struct Pair {
    int fd[2];
    Pair() { CHECK(::socketpair(AF_UNIX, SOCK_STREAM, 0, fd) == 0); }
    ~Pair() { for (int f : fd) if (f >= 0) ::close(f); }
    int take(int i) { return std::exchange(fd[i], -1); }
};
void raw_send(int fd, const std::vector<uint8_t>& bytes) {
    size_t offset = 0;
    while (offset < bytes.size()) {
        const ssize_t n = ::send(fd, bytes.data() + offset, bytes.size() - offset, MSG_NOSIGNAL);
        CHECK(n > 0); offset += n;
    }
}
void bounded(const IpcConnection& c, const IpcLimits& limits) {
    const auto& w = c.last_work();
    CHECK(w.read_bytes <= limits.read_bytes_per_pump);
    CHECK(w.written_bytes <= limits.write_bytes_per_pump);
    CHECK(w.delivered_frames <= limits.frames_per_pump);
    CHECK(w.delivered_bytes <= std::max(limits.dispatch_bytes_per_pump, limits.max_frame_bytes));
    CHECK(w.read_calls <= limits.syscalls_per_direction);
    CHECK(w.write_calls <= limits.syscalls_per_direction);
    CHECK(c.pending_input_bytes() <= limits.max_input_bytes);
    CHECK(c.queued_output_bytes() <= limits.max_output_bytes);
    CHECK(c.queued_output_frames() <= limits.max_output_frames);
}

int main() {
    int failures = 0;
    auto test = [&](const char* name, const std::function<void()>& f) {
        try { f(); std::cout << "PASS " << name << std::endl; }
        catch (const std::exception& e) { ++failures; std::cout << "FAIL " << name << ": " << e.what() << std::endl; }
    };
    test("decoder_limits_prefix_and_compaction", [] {
        FrameDecoder d(64, 68);
        std::vector<uint8_t> body(20, 7), out;
        const auto frame = FrameEncoder::encode(body.data(), body.size());
        for (int i = 0; i < 200; ++i) {
            d.append(frame.data(), frame.size());
            if (i % 2) { CHECK(d.pop_frame(out) && out == body); CHECK(d.pop_frame(out) && out == body); }
        }
        CHECK(!d.pending_bytes());
        uint32_t bad = htonl(65);
        d.append(reinterpret_cast<uint8_t*>(&bad), 3);
        bool caught = false;
        try { d.append(reinterpret_cast<uint8_t*>(&bad) + 3, 1); } catch (const FramingError&) { caught = true; }
        CHECK(caught && d.pending_bytes() == 3);
        d.reset();
        caught = false;
        std::vector<uint8_t> excess(69, 1);
        try { d.append(excess.data(), excess.size()); } catch (const FramingError&) { caught = true; }
        CHECK(caught && !d.pending_bytes());
        caught = false;
        try { FrameEncoder::encode(nullptr, 1); } catch (const FramingError&) { caught = true; }
        CHECK(caught);
    });
    test("fragmented_coalesced_eof_across_dispatch_budgets", [] {
        Pair p; IpcLimits l; l.frames_per_pump = 3; l.dispatch_bytes_per_pump = 5;
        IpcConnection receiver(p.take(0), l);
        std::vector<std::vector<uint8_t>> expected, actual;
        for (int i = 1; i <= 17; ++i) {
            expected.push_back(std::vector<uint8_t>(i % 5 + 1, static_cast<uint8_t>(i)));
            const auto frame = FrameEncoder::encode(expected.back().data(), expected.back().size());
            for (uint8_t byte : frame) raw_send(p.fd[1], {byte});
        }
        ::close(p.take(1));
        for (int i = 0; i < 100 && receiver.is_valid(); ++i) {
            receiver.poll_and_receive(actual); bounded(receiver, l);
        }
        CHECK(actual == expected);
        CHECK(!receiver.is_valid() && receiver.close_reason() == IpcCloseReason::PeerEof);
    });
    test("complete_frame_then_truncated_header_or_body", [] {
        for (size_t partial : {size_t(1), size_t(3), size_t(4), size_t(7)}) {
            Pair p; IpcConnection receiver(p.take(0));
            const std::vector<uint8_t> body{1, 2, 3, 4};
            const auto frame = FrameEncoder::encode(body.data(), body.size());
            raw_send(p.fd[1], frame);
            raw_send(p.fd[1], std::vector<uint8_t>(frame.begin(), frame.begin() + partial));
            ::close(p.take(1));
            std::vector<std::vector<uint8_t>> actual;
            CHECK(!receiver.poll_and_receive(actual, 100));
            CHECK(actual == std::vector<std::vector<uint8_t>>{body});
            CHECK(receiver.close_reason() == IpcCloseReason::TruncatedFrame);
            CHECK(!receiver.pending_input_bytes());
        }
    });
    test("zero_oversized_prefix_rejected_without_body_or_process_failure", [] {
        for (uint32_t size : {0u, 65u, MAX_FRAME_SIZE + 1, UINT32_MAX}) {
            Pair p; IpcLimits l; l.max_frame_bytes = 64; l.max_input_bytes = 68;
            IpcConnection receiver(p.take(0), l);
            uint32_t prefix = htonl(size);
            CHECK(::send(p.fd[1], &prefix, 4, MSG_NOSIGNAL) == 4);
            std::vector<std::vector<uint8_t>> actual;
            CHECK(!receiver.poll_and_receive(actual, 100));
            CHECK(receiver.close_reason() == IpcCloseReason::InvalidFrame);
            CHECK(actual.empty() && !receiver.pending_input_bytes());
            CHECK(receiver.last_work().read_bytes == 4);
        }
    });
    test("output_byte_and_frame_overflow_closes_and_clears", [] {
        for (bool bytes : {false, true}) {
            Pair p; IpcLimits l; l.max_output_bytes = bytes ? 12 : 1000; l.max_output_frames = bytes ? 10 : 2;
            IpcConnection sender(p.take(0), l);
            const uint8_t body[] = {1, 2};
            CHECK(sender.send_message(body, 2)); CHECK(sender.send_message(body, 2));
            CHECK(sender.queued_output_bytes() == 12 && sender.queued_output_frames() == 2);
            CHECK(!sender.send_message(body, 2));
            CHECK(!sender.is_valid() && sender.close_reason() == IpcCloseReason::OutputLimit);
            CHECK(!sender.queued_output_bytes() && !sender.queued_output_frames());
        }
    });
    test("slow_reader_partial_writes_resume_fifo_and_bounded_pumps", [] {
        Pair p; int size = 4096;
        CHECK(::setsockopt(p.fd[0], SOL_SOCKET, SO_SNDBUF, &size, sizeof(size)) == 0);
        IpcLimits l; l.read_bytes_per_pump = 16384; l.write_bytes_per_pump = 16384;
        IpcConnection sender(p.take(0), l), receiver(p.take(1), l);
        std::vector<std::vector<uint8_t>> expected, actual, ignore;
        const auto start = std::chrono::steady_clock::now();
        for (int i = 0; i < 3; ++i) {
            expected.emplace_back(512 * 1024, static_cast<uint8_t>(i + 1));
            CHECK(sender.send_message(expected.back().data(), expected.back().size()));
        }
        CHECK(std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - start).count() < 50);
        for (int i = 0; i < 100; ++i) {
            const auto begin = std::chrono::steady_clock::now();
            CHECK(sender.poll_and_receive(ignore)); bounded(sender, l);
            CHECK(std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - begin).count() < 50);
        }
        CHECK(sender.queued_output_bytes() > 0 && sender.is_valid());
        for (int i = 0; i < 10000 && actual.size() < expected.size(); ++i) {
            CHECK(sender.poll_and_receive(ignore)); bounded(sender, l);
            CHECK(receiver.poll_and_receive(actual)); bounded(receiver, l);
        }
        CHECK(actual == expected && !sender.queued_output_bytes());
    });
    test("maximum_legal_frame_and_receive_flood_are_bounded", [] {
        Pair p; IpcLimits l; l.frames_per_pump = 2;
        IpcConnection sender(p.take(0), l), receiver(p.take(1), l);
        std::vector<uint8_t> large(MAX_FRAME_SIZE, 42);
        CHECK(sender.send_message(large.data(), large.size()));
        const uint8_t small = 13;
        for (int i = 0; i < 100; ++i) CHECK(sender.send_message(&small, 1));
        std::vector<std::vector<uint8_t>> actual, ignore;
        for (int i = 0; i < 2000 && actual.size() < 101; ++i) {
            CHECK(sender.poll_and_receive(ignore)); bounded(sender, l);
            CHECK(receiver.poll_and_receive(actual)); bounded(receiver, l);
        }
        CHECK(actual.size() == 101 && actual.front() == large);
        for (size_t i = 1; i < actual.size(); ++i) CHECK(actual[i] == std::vector<uint8_t>{small});
    });
    test("write_failure_does_not_discard_large_final_inbound_frame", [] {
        Pair p; IpcLimits l; l.read_bytes_per_pump = 4096;
        IpcConnection receiver(p.take(0), l);
        std::vector<uint8_t> body(128 * 1024, 17);
        raw_send(p.fd[1], FrameEncoder::encode(body.data(), body.size()));
        ::close(p.take(1));
        const uint8_t reply = 3;
        CHECK(receiver.send_message(&reply, 1));
        std::vector<std::vector<uint8_t>> actual;
        for (int i = 0; i < 100 && receiver.is_valid(); ++i) {
            receiver.poll_and_receive(actual); bounded(receiver, l);
        }
        CHECK(actual == std::vector<std::vector<uint8_t>>{body});
        CHECK(receiver.close_reason() == IpcCloseReason::PeerEof);
    });
    test("half_close_delivers_final_frame", [] {
        Pair p; IpcConnection receiver(p.take(0));
        const std::vector<uint8_t> body{8};
        raw_send(p.fd[1], FrameEncoder::encode(body.data(), body.size()));
        CHECK(::shutdown(p.fd[1], SHUT_WR) == 0);
        std::vector<std::vector<uint8_t>> actual;
        CHECK(!receiver.poll_and_receive(actual, 100));
        CHECK(actual == std::vector<std::vector<uint8_t>>{body});
        CHECK(receiver.close_reason() == IpcCloseReason::PeerEof);
    });
    test("move_preserves_partial_input_and_queued_output", [] {
        Pair p; IpcConnection original(p.take(0));
        const std::vector<uint8_t> body{4, 5};
        auto frame = FrameEncoder::encode(body.data(), body.size());
        raw_send(p.fd[1], {frame[0], frame[1]});
        std::vector<std::vector<uint8_t>> actual;
        CHECK(original.poll_and_receive(actual));
        CHECK(original.send_message(body.data(), body.size()));
        IpcConnection moved(std::move(original));
        CHECK(!original.is_valid() && !original.pending_input_bytes());
        IpcConnection assigned(-1); assigned = std::move(moved);
        raw_send(p.fd[1], std::vector<uint8_t>(frame.begin() + 2, frame.end()));
        CHECK(assigned.poll_and_receive(actual, 100));
        CHECK(actual == std::vector<std::vector<uint8_t>>{body});
        std::vector<uint8_t> reply(frame.size());
        CHECK(::recv(p.fd[1], reply.data(), reply.size(), 0) == static_cast<ssize_t>(reply.size()));
        CHECK(reply == frame);
    });
    test("additional_peer_cannot_replace_active_connection", [] {
        const std::string path = "/tmp/cwm-limits-" + std::to_string(::getpid()) + ".sock";
        IpcServer server(path); CHECK(server.start());
        auto first = IpcClient::connect_unix(path, 0); CHECK(first);
        CHECK(server.poll_accept(100));
        const int active = server.client()->native_handle();
        auto second = IpcClient::connect_unix(path, 0); CHECK(second);
        CHECK(!server.poll_accept(100)); CHECK(server.client()->native_handle() == active);
        std::vector<std::vector<uint8_t>> incoming;
        CHECK(!second->poll_and_receive(incoming, 100));
        const uint8_t body = 9; CHECK(first->send_message(&body, 1));
        CHECK(first->poll_and_receive(incoming));
        CHECK(server.client()->poll_and_receive(incoming, 100));
        CHECK(incoming == std::vector<std::vector<uint8_t>>{{body}});
    });
    test("invalid_socket_paths_and_connect_never_wait_on_visual_thread", [] {
        const std::string long_path(200, 'x');
        IpcServer server(long_path); CHECK(!server.start());
        CHECK(!IpcClient::connect_unix(long_path, 0));
        const auto start = std::chrono::steady_clock::now();
        CHECK(!IpcClient::connect_unix("/tmp/cwm-missing-" + std::to_string(::getpid()), 0));
        CHECK(std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - start).count() < 50);
    });
    return failures ? 1 : 0;
}
