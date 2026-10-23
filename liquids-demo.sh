#!/usr/bin/env bash
set -euo pipefail
exec python3 "$(dirname "$(readlink -f "$0")")/tools/launch_liquids_demo.py" "$@"
