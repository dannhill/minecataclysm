// Behavioral conformance probes against the unmodified production transport.
#include "cwm/ipc_transport.hpp"
#include "cwm/cwm_protocol.hpp"
#include <sys/wait.h>
#include <chrono>
#include <iostream>
#include <functional>
#include <array>

using namespace cdda::cwm;

int main() {
    int failures = 0;
    auto check = [&](const char *name, const std::function<bool()> &probe) {
        bool ok = probe();
        std::cout << (ok ? "PASS " : "FAIL ") << name << std::endl;
        failures += !ok;
    };
    MessageBuilder builder(1, 1);
    auto payload = builder.build_hello_request("takeover");
    auto frame = FrameEncoder::encode(payload.data(), payload.size());

    check("fragmented_frame", [&] {
        FrameDecoder decoder;
        std::vector<uint8_t> out;
        for (size_t i = 0; i < frame.size(); ++i) {
            decoder.append(&frame[i], 1);
            if (decoder.pop_frame(out) != (i == frame.size() - 1)) return false;
        }
        return out == payload && decoder.pending_bytes() == 0;
    });
    check("concatenated_frames", [&] {
        FrameDecoder decoder;
        decoder.append(frame.data(), frame.size());
        decoder.append(frame.data(), frame.size());
        std::vector<uint8_t> out;
        return decoder.pop_frame(out) && out == payload && decoder.pop_frame(out) && out == payload && !decoder.pop_frame(out);
    });
    check("final_frame_before_eof_is_delivered", [&] {
        int fd[2];
        if (::socketpair(AF_UNIX, SOCK_STREAM, 0, fd)) return false;
        IpcConnection receiver(fd[0]);
        ::send(fd[1], frame.data(), frame.size(), MSG_NOSIGNAL);
        ::close(fd[1]);
        std::vector<std::vector<uint8_t>> incoming;
        receiver.poll_and_receive(incoming, 500);
        return incoming.size() == 1 && incoming[0] == payload;
    });
    check("oversized_frame_cannot_abort_receiver", [&] {
        // The child invokes the same API as the CDDA/Luanti event loops.
        pid_t pid = ::fork();
        if (pid == 0) {
            int fd[2];
            ::socketpair(AF_UNIX, SOCK_STREAM, 0, fd);
            IpcConnection receiver(fd[0]);
            uint32_t header = htonl(MAX_FRAME_SIZE + 1);
            ::send(fd[1], &header, sizeof(header), MSG_NOSIGNAL);
            std::vector<std::vector<uint8_t>> incoming;
            const bool alive = receiver.poll_and_receive(incoming, 500);
            ::close(fd[1]);
            ::_exit(!alive && !receiver.is_valid() ? 0 : 2);
        }
        int status;
        ::waitpid(pid, &status, 0);
        std::cout << "OBS oversized_receiver_wait_status=" << status << std::endl;
        return WIFEXITED(status) && WEXITSTATUS(status) == 0;
    });
    check("slow_peer_does_not_block_visual_thread_over_50ms", [&] {
        int fd[2];
        if (::socketpair(AF_UNIX, SOCK_STREAM, 0, fd)) return false;
        int buffer_size = 4096;
        ::setsockopt(fd[0], SOL_SOCKET, SO_SNDBUF, &buffer_size, sizeof(buffer_size));
        IpcConnection sender(fd[0]);
        std::vector<uint8_t> body(512 * 1024, 1);
        auto start = std::chrono::steady_clock::now();
        bool sent = sender.send_message(body.data(), body.size());
        double milliseconds = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - start).count();
        ::close(fd[1]);
        std::cout << "OBS slow_peer_ms=" << milliseconds << " sent=" << sent << std::endl;
        return milliseconds < 50.0;
    });
    return failures ? 1 : 0;
}
