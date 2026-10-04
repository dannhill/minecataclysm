#!/usr/bin/env bash
set -Eeuo pipefail
PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ "${1:-}" == --help || "${1:-}" == -h ]]; then
    cat <<'HELP'
Confronto terreno CDDA: campo, bosco, strada/casa e riva d'acqua.
  F7     Cambia A (attuale) / B (materiali e vegetazione)
  F8     Attiva/disattiva la nebbia, indipendentemente da A/B
  WASD   Cammina; mouse per guardare; Esc per uscire
Ogni avvio crea una nuova scena isolata, senza usare il salvataggio normale.
HELP
    exit 0
fi
PLAY_ROOT="$PROJECT_DIR/artifacts/terrain-prototype/plays"
mkdir -p -- "$PLAY_ROOT"
PLAY_DIR="$(mktemp -d "$PLAY_ROOT/run-XXXXXX")"
cat > "$PLAY_DIR/client.conf" <<'CONFIG'
fullscreen = false
screen_w = 1280
screen_h = 720
fps_max = 60
fps_max_unfocused = 60
vsync = false
enable_update_checker = false
enable_shaders = true
enable_dynamic_shadows = false
enable_fog = true
viewing_range = 160
mouse_sensitivity = 0.2
cdda_terrain_comparison = true
keymap_quicktune_next = KEY_F7
keymap_quicktune_prev = KEY_F8
keymap_toggle_profiler =
debug_log_level = info
CONFIG
printf 'Confronto terreno: F7 cambia A/B, F8 nebbia. Scena isolata: %s\n' "$PLAY_DIR"
exec env CDDA_USERDIR="$PLAY_DIR/cdda" CDDA_WORLD=terrain_comparison \
    CDDA_CHARACTER= CDDA_TERRAIN_DEMO=1 LUANTI_WORLD="$PLAY_DIR/luanti" \
    LUANTI_CONFIG="$PLAY_DIR/client.conf" LOG_DIR="$PLAY_DIR/logs" \
    "$PROJECT_DIR/start.sh" --name "Terrain tester" "$@"
