// All entry points exec the same supervisor; start.sh owns sockets and children.
#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <string>
#include <vector>
#if !defined(_WIN32)
#include <unistd.h>
#endif
#ifndef CWM_PROJECT_ROOT
#error CWM_PROJECT_ROOT must identify the integration checkout
#endif
int main(int argc, char** argv) {
    namespace fs = std::filesystem;
    fs::path root_path;
    if (const char* env_root = std::getenv("CWM_PROJECT_ROOT"); env_root && *env_root) {
        root_path = env_root;
    } else if (fs::exists(fs::path(CWM_PROJECT_ROOT) / "start.sh")) {
        root_path = CWM_PROJECT_ROOT;
    } else if (argc > 0 && argv[0]) {
        std::error_code ec;
        for (fs::path cur = fs::weakly_canonical(fs::path(argv[0]), ec).parent_path();
             !cur.empty() && cur != cur.parent_path(); cur = cur.parent_path()) {
            if (fs::exists(cur / "start.sh", ec)) {
                root_path = cur;
                break;
            }
        }
    }
    const std::string script = (root_path / "start.sh").string();
    std::vector<char*> arguments{const_cast<char*>(script.c_str())};
    for (int i = 1; i < argc; ++i) arguments.push_back(argv[i]);
    arguments.push_back(nullptr);
#if !defined(_WIN32)
    execv(script.c_str(), arguments.data());
#endif
    std::cerr << "Unable to execute supervisor " << script << '\n';
    return 127;
}
