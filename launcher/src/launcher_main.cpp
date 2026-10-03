// CDDA-Mineclonia Integration Coordinator & Launcher
// Licensed under Apache-2.0

#include <iostream>
#include <string>
#include <vector>
#include <csignal>
#include <chrono>
#include <thread>
#include <sys/wait.h>
#include <sys/stat.h>
#include <unistd.h>

static pid_t g_cdda_pid = -1;
static pid_t g_luanti_pid = -1;

void handle_signal(int sig) {
    std::cout << "\n[Coordinator] Termination signal received (" << sig << "). Stopping child processes...\n";
    if (g_luanti_pid > 0) {
        kill(g_luanti_pid, SIGTERM);
    }
    if (g_cdda_pid > 0) {
        kill(g_cdda_pid, SIGTERM);
    }
}

bool wait_for_socket(const std::string& path, int timeout_seconds = 15) {
    auto start = std::chrono::steady_clock::now();
    while (std::chrono::duration_cast<std::chrono::seconds>(std::chrono::steady_clock::now() - start).count() < timeout_seconds) {
        struct stat st;
        if (stat(path.c_str(), &st) == 0 && S_ISSOCK(st.st_mode)) {
            return true;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    return false;
}

int main(int argc, char* argv[]) {
    std::string socket_path = "/tmp/cdda_cwm.sock";
    std::string world_name = "cwm_world";
    std::string cdda_bin = "./cdda/build/src/cdda-server";
    std::string luanti_bin = "./luanti/build/bin/luanti";

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--cdda" && i + 1 < argc) cdda_bin = argv[++i];
        else if (arg == "--luanti" && i + 1 < argc) luanti_bin = argv[++i];
        else if (arg == "--world" && i + 1 < argc) world_name = argv[++i];
        else if (arg == "--socket" && i + 1 < argc) socket_path = argv[++i];
    }

    std::signal(SIGINT, handle_signal);
    std::signal(SIGTERM, handle_signal);

    std::cout << "========================================================\n"
              << " CDDA–Mineclonia 3D Integration Coordinator v1.0\n"
              << " Orchestrating CDDA Server and Luanti Client\n"
              << "========================================================\n";

    unlink(socket_path.c_str());

    // 1. Launch Headless CDDA Server
    std::cout << "[Coordinator] Launching CDDA Headless Server: " << cdda_bin << "\n";
    g_cdda_pid = fork();
    if (g_cdda_pid == 0) {
        execl(cdda_bin.c_str(), cdda_bin.c_str(),
              "--socket", socket_path.c_str(),
              "--world", world_name.c_str(),
              nullptr);
        std::cerr << "[Coordinator] Failed to execute cdda-server\n";
        _exit(1);
    }

    // 2. Wait for CDDA Server socket
    std::cout << "[Coordinator] Waiting for CWM socket at: " << socket_path << "...\n";
    if (!wait_for_socket(socket_path, 15)) {
        std::cerr << "[Coordinator] ERROR: Timed out waiting for CDDA CWM socket.\n";
        kill(g_cdda_pid, SIGTERM);
        return 1;
    }
    std::cout << "[Coordinator] CDDA CWM socket is ready!\n";

    // 3. Launch Luanti 3D Presentation Client (if binary exists)
    struct stat st;
    if (stat(luanti_bin.c_str(), &st) == 0 && (st.st_mode & S_IXUSR)) {
        std::cout << "[Coordinator] Launching Luanti Presentation Client: " << luanti_bin << "\n";
        g_luanti_pid = fork();
        if (g_luanti_pid == 0) {
            execl(luanti_bin.c_str(), luanti_bin.c_str(),
                  "--gameid", "cdda_voxel",
                  nullptr);
            std::cerr << "[Coordinator] Failed to execute luanti\n";
            _exit(1);
        }
    } else {
        std::cout << "[Coordinator] Luanti binary not yet compiled; running in headless CDDA monitor mode.\n";
    }

    // 4. Supervisor loop
    int status = 0;
    while (true) {
        pid_t p = waitpid(-1, &status, WNOHANG);
        if (p == g_cdda_pid && p > 0) {
            std::cout << "[Coordinator] CDDA server exited with status " << status << "\n";
            if (g_luanti_pid > 0) kill(g_luanti_pid, SIGTERM);
            break;
        }
        if (p == g_luanti_pid && p > 0) {
            std::cout << "[Coordinator] Luanti client exited with status " << status << "\n";
            if (g_cdda_pid > 0) kill(g_cdda_pid, SIGTERM);
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }

    // Clean up remaining processes
    if (g_cdda_pid > 0) waitpid(g_cdda_pid, nullptr, 0);
    if (g_luanti_pid > 0) waitpid(g_luanti_pid, nullptr, 0);

    unlink(socket_path.c_str());
    std::cout << "[Coordinator] All processes terminated cleanly.\n";
    return 0;
}
