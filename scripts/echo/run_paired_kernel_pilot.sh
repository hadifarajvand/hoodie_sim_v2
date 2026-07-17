#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /absolute/output/path/outside/repository" >&2
  exit 2
fi
OUTPUT="$1"
[[ "$OUTPUT" = /* ]] || { echo "output path must be absolute" >&2; exit 2; }
resolved="$(python - "$ROOT" "$OUTPUT" <<'PY'
from pathlib import Path
import sys
repo = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).expanduser().resolve()
if out == repo or repo in out.parents:
    raise SystemExit("output path must be outside repository")
print(out)
PY
)"

python -m src.echo_verified.paired_pilot \
  --output-root "$resolved" \
  --seeds 101,202,303 \
  --episodes-per-seed 6

echo "PAIRED_PHYSICAL_KERNEL_PILOT_PASSED output=$resolved"
