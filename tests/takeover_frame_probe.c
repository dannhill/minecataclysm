/* Test-only swap timestamps and isolated Unix-socket routing; no engine edits. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <errno.h>

static void record_swap(void) {
    static FILE *log;
    if (!log) {
        const char *path = getenv("M55_FRAME_LOG");
        if (path) { log = fopen(path, "a"); if (log) setvbuf(log, NULL, _IOLBF, 0); }
    }
    if (log) {
        struct timespec ts;
        clock_gettime(CLOCK_MONOTONIC, &ts);
        fprintf(log, "%lld\n", (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec);
    }
}

void SDL_GL_SwapWindow(void *window) {
    static void (*original)(void *);
    if (!original) original = dlsym(RTLD_NEXT, "SDL_GL_SwapWindow");
    original(window);
    record_swap();
}

void glXSwapBuffers(void *display, unsigned long drawable) {
    static void (*original)(void *, unsigned long);
    if (!original) original = dlsym(RTLD_NEXT, "glXSwapBuffers");
    original(display, drawable);
    record_swap();
}

int connect(int fd, const struct sockaddr *address, socklen_t length) {
    static int (*original)(int, const struct sockaddr *, socklen_t);
    if (!original) original = dlsym(RTLD_NEXT, "connect");
    const char *replacement = getenv("M55_SOCKET_PATH");
    if (replacement && address && address->sa_family == AF_UNIX &&
        length >= sizeof(struct sockaddr_un)) {
        const struct sockaddr_un *old = (const struct sockaddr_un *)address;
        if (!strcmp(old->sun_path, "/tmp/cwm_bench_ipc.sock")) {
            struct sockaddr_un isolated = *old;
            if (strlen(replacement) >= sizeof(isolated.sun_path)) { errno = ENAMETOOLONG; return -1; }
            strcpy(isolated.sun_path, replacement);
            return original(fd, (const struct sockaddr *)&isolated, sizeof(isolated));
        }
    }
    return original(fd, address, length);
}
