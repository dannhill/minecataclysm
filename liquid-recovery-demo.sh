#!/usr/bin/env bash
set -euo pipefail
exec python3 "$(dirname "$(readlink -f "$0")")/tools/launch_liquid_recovery_demo.py" "$@"
