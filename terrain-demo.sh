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
exec python3 "$PROJECT_DIR/tools/launch_demo.py" terrain "$@"
