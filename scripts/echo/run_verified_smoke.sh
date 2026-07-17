#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

OUTPUT_ROOT="${1:-${ECHO_OUTPUT_ROOT:-}}"
if [[ -z "$OUTPUT_ROOT" ]]; then
  cat >&2 <<'EOF'
Usage: bash scripts/echo/run_verified_smoke.sh /absolute/path/to/output

The path must be outside this Git repository. The smoke writes only bounded,
explicitly labelled non-paper outputs.
EOF
  exit 2
fi

case "$OUTPUT_ROOT" in
  /*) ;;
  *) echo "ECHO_OUTPUT_ROOT_MUST_BE_ABSOLUTE" >&2; exit 2 ;;
esac

RESOLVED_OUTPUT="$(python - "$ROOT_DIR" "$OUTPUT_ROOT" <<'PY'
from pathlib import Path
import sys
repo = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).expanduser().resolve()
if out == repo or repo in out.parents:
    raise SystemExit("ECHO output root must be outside the Git repository")
out.mkdir(parents=True, exist_ok=True)
probe = out / ".echo-write-probe"
probe.write_bytes(b"echo-verified-smoke")
if probe.read_bytes() != b"echo-verified-smoke":
    raise SystemExit("output-root write/read probe failed")
probe.unlink()
print(out)
PY
)"

python -m pip install -e '.[dev]'
python -m pytest -q \
  tests/unit/test_echo_verified_control.py \
  tests/integration/test_echo_verified_smoke.py
python -m src.echo_verified.smoke --output-root "$RESOLVED_OUTPUT"

printf 'ECHO_VERIFIED_SMOKE_COMPLETE\noutput=%s\nsha=%s\n' \
  "$RESOLVED_OUTPUT" "$(git rev-parse HEAD 2>/dev/null || printf unknown)"
