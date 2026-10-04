#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CDDA_BIN="${CDDA_BIN:-$PROJECT_DIR/cdda/build/src/cdda-server}"
LUANTI_BIN="${LUANTI_BIN:-$PROJECT_DIR/luanti/bin/luanti}"
CDDA_USERDIR="${CDDA_USERDIR:-$PROJECT_DIR/user/cdda}"
CDDA_WORLD="${CDDA_WORLD:-cdda_voxel}"
CDDA_CHARACTER="${CDDA_CHARACTER:-}"
LUANTI_WORLD="${LUANTI_WORLD:-$PROJECT_DIR/worlds/cdda-presentation}"
LOG_DIR="${LOG_DIR:-$PROJECT_DIR/artifacts/runtime/$(date -u +%Y%m%dT%H%M%SZ)-$$}"

for binary in "$CDDA_BIN" "$LUANTI_BIN"; do
    if [[ ! -x "$binary" ]]; then
        printf '[Launcher] Executable missing: %s\n' "$binary" >&2
        exit 1
    fi
done

RUNTIME_DIR="$(mktemp -d /tmp/cdda-voxel.XXXXXX)"
SOCKET_PATH="$RUNTIME_DIR/cwm.sock"
SERVER_PID=""
CLIENT_PID=""

cleanup() {
    local status=$?
    trap - EXIT INT TERM
    for pid in "$CLIENT_PID" "$SERVER_PID"; do
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            kill -TERM "$pid" 2>/dev/null || true
        fi
    done
    for pid in "$CLIENT_PID" "$SERVER_PID"; do
        if [[ -n "$pid" ]]; then wait "$pid" 2>/dev/null || true; fi
    done
    rm -rf -- "$RUNTIME_DIR"
    exit "$status"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

mkdir -p -- "$LOG_DIR" "$CDDA_USERDIR" "$LUANTI_WORLD"
if [[ ! -e "$PROJECT_DIR/luanti/games/cdda_voxel" ]]; then
    mkdir -p -- "$PROJECT_DIR/luanti/games"
    ln -s -- "$PROJECT_DIR/game" "$PROJECT_DIR/luanti/games/cdda_voxel"
fi
CLIENT_CONFIG="$RUNTIME_DIR/client.conf"
BASE_CONFIG="${LUANTI_CONFIG:-$HOME/.minetest/minetest.conf}"
if [[ -f "$BASE_CONFIG" ]]; then cp -- "$BASE_CONFIG" "$CLIENT_CONFIG"; else : > "$CLIENT_CONFIG"; fi
printf '\n' >> "$CLIENT_CONFIG"
cat "$PROJECT_DIR/game/minetest.conf" >> "$CLIENT_CONFIG"
if [[ "${CDDA_REALTIME:-0}" == 1 ]]; then
    printf '\nkeymap_quicktune_next = KEY_F7\nkeymap_quicktune_prev = KEY_F8\n' >> "$CLIENT_CONFIG"
fi
printf '\nbind_address = 127.0.0.1\ncwm_socket_path = %s\n' "$SOCKET_PATH" >> "$CLIENT_CONFIG"

# This is a disposable presentation world. Existing user worlds are untouched.
if [[ ! -f "$LUANTI_WORLD/world.mt" ]]; then
    cat > "$LUANTI_WORLD/world.mt" <<'WORLD'
gameid = cdda_voxel
backend = sqlite3
player_backend = sqlite3
auth_backend = sqlite3
load_mod_cdda_nodes = true
load_mod_cdda_entities = true
WORLD
fi

printf '[Launcher] Starting CDDA; logs: %s\n' "$LOG_DIR"
cd -- "$PROJECT_DIR"
SERVER_ARGS=()
if [[ -n "$CDDA_CHARACTER" ]]; then SERVER_ARGS+=(--character "$CDDA_CHARACTER"); fi
if [[ "${CDDA_TERRAIN_DEMO:-0}" == 1 ]]; then SERVER_ARGS+=(--terrain-demo); fi
if [[ "${CDDA_REALTIME:-0}" == 1 ]]; then SERVER_ARGS+=(--realtime); fi
stdbuf -oL -eL "$CDDA_BIN" --socket "$SOCKET_PATH" --world "$CDDA_WORLD" "${SERVER_ARGS[@]}" \
    --userdir "$CDDA_USERDIR" --datadir "$PROJECT_DIR/cdda/data" \
    > "$LOG_DIR/cdda.log" 2>&1 &
SERVER_PID=$!

# A private socket plus the post-initialization message proves this process
# finished booting; a stale shared socket or a fixed sleep does not.
ready=false
for ((attempt = 0; attempt < 600; ++attempt)); do
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
        if wait "$SERVER_PID"; then server_status=0; else server_status=$?; fi
        printf '[Launcher] CDDA stopped during startup (exit %s).\n' "$server_status" >&2
        tail -n 30 "$LOG_DIR/cdda.log" >&2
        if [[ "$server_status" != 0 ]]; then exit "$server_status"; fi
        exit 1
    fi
    if [[ -S "$SOCKET_PATH" ]] && grep -qF 'CWM IPC server listening on:' "$LOG_DIR/cdda.log"; then
        ready=true
        break
    fi
    sleep 0.1
done
if [[ "$ready" != true ]]; then
    printf '[Launcher] CDDA did not become ready within 60 seconds. See %s/cdda.log\n' "$LOG_DIR" >&2
    exit 1
fi

printf '[Launcher] CDDA ready. Opening the CDDA Voxel presentation world.\n'
"$LUANTI_BIN" --go --world "$LUANTI_WORLD" --gameid cdda_voxel \
    --config "$CLIENT_CONFIG" --logfile "$LOG_DIR/luanti-engine.log" "$@" \
    > "$LOG_DIR/luanti.log" 2>&1 &
CLIENT_PID=$!

while kill -0 "$CLIENT_PID" 2>/dev/null; do
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
        printf '[Launcher] CDDA stopped while playing. See %s/cdda.log\n' "$LOG_DIR" >&2
        exit 1
    fi
    sleep 0.2
done
if wait "$CLIENT_PID"; then exit 0; else exit "$?"; fi
