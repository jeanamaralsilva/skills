#!/usr/bin/env bash
# cortex.sh - terminal launcher for the cortex memory network.
#
# Thin wrapper (no logic of its own, to stay DRY): locate a Python 3 and exec
# cortex.py next to this script, forwarding every argument untouched.
#
#   ./cortex.sh remember "we use snake_case in Python" --kind convention --tags naming
#   ./cortex.sh search "naming convention"
#   ./cortex.sh stats
#
# Tip: alias it so any agent shell can call `cortex ...`:
#   alias cortex="$(pwd)/cortex.sh"
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
    py=python3
elif command -v python >/dev/null 2>&1; then
    py=python
else
    echo "cortex.sh: no python3 / python on PATH" >&2
    exit 127
fi

exec "$py" "$here/cortex.py" "$@"
