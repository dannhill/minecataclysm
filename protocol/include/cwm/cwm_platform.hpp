// Cross-platform OS abstraction layer for CWM (Linux, Windows, macOS, BSD, and future OSes)
// Licensed under Apache-2.0
#pragma once

#include <cstdlib>
#include <string>
#include <vector>

#if defined(_WIN32) || defined(_WIN64)
    #define CWM_OS_WINDOWS 1
    #define CWM_OS_POSIX 0
    #define CWM_OS_NAME "windows"
#elif defined(__APPLE__) && defined(__MACH__)
    #define CWM_OS_WINDOWS 0
    #define CWM_OS_MACOS 1
    #define CWM_OS_POSIX 1
    #define CWM_OS_NAME "macos"
#elif defined(__linux__)
    #define CWM_OS_WINDOWS 0
    #define CWM_OS_LINUX 1
    #define CWM_OS_POSIX 1
    #define CWM_OS_NAME "linux"
#elif defined(__FreeBSD__) || defined(__NetBSD__) || defined(__OpenBSD__) || defined(__DragonFly__)
    #define CWM_OS_WINDOWS 0
    #define CWM_OS_BSD 1
    #define CWM_OS_POSIX 1
    #define CWM_OS_NAME "bsd"
#elif defined(__unix__) || defined(__unix)
    #define CWM_OS_WINDOWS 0
    #define CWM_OS_POSIX 1
    #define CWM_OS_NAME "unix"
#else
    #define CWM_OS_WINDOWS 0
    #define CWM_OS_POSIX 0
    #define CWM_OS_NAME "unknown"
#endif

#if CWM_OS_WINDOWS
    #ifndef NOMINMAX
        #define NOMINMAX
    #endif
    #include <windows.h>
    #include <shellapi.h>
    #include "windows_pipe_transport.hpp"
#endif

namespace cdda::cwm {

inline bool set_env_var(const char* name, const char* value) {
    if (!name || !value) return false;
#if CWM_OS_WINDOWS
    return ::_putenv_s(name, value) == 0;
#elif CWM_OS_POSIX
    return ::setenv(name, value, 1) == 0;
#else
    (void)name;
    (void)value;
    return false;
#endif
}

// Encapsulates OS-specific process lifecycle hooks (UTF-8 argv normalization,
// supervisor readiness notification, and external stop events).
class PlatformLifecycle {
public:
    PlatformLifecycle() = default;
    ~PlatformLifecycle() {
#if CWM_OS_WINDOWS
        if (stop_event_) {
            ::CloseHandle(stop_event_);
            stop_event_ = nullptr;
        }
#endif
    }
    PlatformLifecycle(const PlatformLifecycle&) = delete;
    PlatformLifecycle& operator=(const PlatformLifecycle&) = delete;

    bool normalize_args(int& argc, const char**& argv) {
#if CWM_OS_WINDOWS
        int wide_argc = 0;
        LPWSTR* wide_argv = ::CommandLineToArgvW(::GetCommandLineW(), &wide_argc);
        if (!wide_argv) return false;
        utf8_storage_.clear();
        utf8_storage_.reserve(static_cast<size_t>(wide_argc));
        for (int i = 0; i < wide_argc; ++i) {
            const int size = ::WideCharToMultiByte(CP_UTF8, 0, wide_argv[i], -1, nullptr, 0, nullptr, nullptr);
            std::string value(size > 0 ? size : 1, '\0');
            if (size > 0) {
                ::WideCharToMultiByte(CP_UTF8, 0, wide_argv[i], -1, value.data(), size, nullptr, nullptr);
                value.pop_back();
            } else {
                value.clear();
            }
            utf8_storage_.push_back(std::move(value));
        }
        ::LocalFree(wide_argv);
        argv_ptrs_.clear();
        argv_ptrs_.reserve(utf8_storage_.size() + 1);
        for (const auto& s : utf8_storage_) argv_ptrs_.push_back(s.c_str());
        argv_ptrs_.push_back(nullptr);
        argc = wide_argc;
        argv = argv_ptrs_.data();
#else
        (void)argc;
        (void)argv;
#endif
        return true;
    }

    // Returns: 1 if consumed and valid, -1 if consumed with error, 0 if not a lifecycle option.
    int consume_arg(const std::string& arg, int& i, int argc, const char* argv[]) {
        if (arg == "--stop-event" && i + 1 < argc) {
            const std::string event_id = argv[++i];
#if CWM_OS_WINDOWS
            const auto name = pipe_wide(event_id);
            stop_event_ = ::OpenEventW(SYNCHRONIZE, FALSE, name.c_str());
            if (!stop_event_) return -1;
#else
            (void)event_id;
#endif
            return 1;
        }
        if (arg == "--ready-event" && i + 1 < argc) {
            ready_event_ = argv[++i];
            return 1;
        }
        return 0;
    }

    bool signal_ready() const {
        if (ready_event_.empty()) return true;
#if CWM_OS_WINDOWS
        const auto name = pipe_wide(ready_event_);
        const HANDLE event = ::OpenEventW(EVENT_MODIFY_STATE, FALSE, name.c_str());
        if (!event) return false;
        const BOOL ok = ::SetEvent(event);
        ::CloseHandle(event);
        return ok != FALSE;
#else
        return true;
#endif
    }

    bool stop_requested() const {
#if CWM_OS_WINDOWS
        if (stop_event_ && ::WaitForSingleObject(stop_event_, 0) == WAIT_OBJECT_0) {
            return true;
        }
#endif
        return false;
    }

private:
#if CWM_OS_WINDOWS
    std::vector<std::string> utf8_storage_;
    std::vector<const char*> argv_ptrs_;
    HANDLE stop_event_{nullptr};
#endif
    std::string ready_event_;
};

} // namespace cdda::cwm
