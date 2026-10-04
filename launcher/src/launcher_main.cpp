// All entry points exec the same supervisor; start.sh owns sockets and children.
#include <cstdlib>
#include <iostream>
#include <vector>
#include <unistd.h>
#ifndef CWM_PROJECT_ROOT
#error CWM_PROJECT_ROOT must identify the integration checkout
#endif
int main(int argc, char** argv) {
    const char* root = std::getenv("CWM_PROJECT_ROOT");
    const std::string script = std::string(root ? root : CWM_PROJECT_ROOT) + "/start.sh";
    std::vector<char*> arguments{const_cast<char*>(script.c_str())};
    for (int i = 1; i < argc; ++i) arguments.push_back(argv[i]);
    arguments.push_back(nullptr);
    execv(script.c_str(), arguments.data());
    std::cerr << "Unable to execute supervisor " << script << '\n';
    return 127;
}
