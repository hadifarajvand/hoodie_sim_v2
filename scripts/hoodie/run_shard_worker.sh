#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "Usage: $0 <bundle-dir> <persistent-work-dir> [max-runtime-seconds]" >&2
  exit 2
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

BUNDLE_DIR="$(cd "$1" && pwd)"
WORK_DIR="$2"
MAX_RUNTIME="${3:-}"
MANIFEST="$BUNDLE_DIR/shard_manifest.json"
[[ -f "$MANIFEST" ]] || { echo "Missing shard manifest: $MANIFEST" >&2; exit 1; }
mkdir -p "$WORK_DIR"

readarray -t IDENTIFIERS < <(python - "$MANIFEST" <<'PY'
import json
import pathlib
import sys
payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
print(payload["campaign_id"])
print(payload["shard_id"])
print(payload["phase"])
print(payload["source_commit"])
PY
)
CAMPAIGN_ID="${IDENTIFIERS[0]}"
SHARD_ID="${IDENTIFIERS[1]}"
PHASE="${IDENTIFIERS[2]}"
SOURCE_COMMIT="${IDENTIFIERS[3]}"

[[ "$CAMPAIGN_ID" == figures-8-11-corrected-* ]] || {
  echo "Refusing unexpected campaign: $CAMPAIGN_ID" >&2
  exit 1
}
[[ "$CAMPAIGN_ID" != "figures-8-11-7587c7c6382c" ]] || {
  echo "Refusing paused legacy campaign" >&2
  exit 1
}

CURRENT_COMMIT="$(git rev-parse HEAD)"
[[ "$CURRENT_COMMIT" == "$SOURCE_COMMIT" ]] || {
  echo "Worker commit mismatch: expected $SOURCE_COMMIT, got $CURRENT_COMMIT" >&2
  exit 1
}

python - <<'PY'
import json
import platform
import torch
print(json.dumps({
    "python": platform.python_version(),
    "pytorch": torch.__version__,
    "cuda_available": torch.cuda.is_available(),
    "mps_available": bool(getattr(torch.backends, "mps", None) and torch.backends.mps.is_available()),
}, sort_keys=True))
PY

COMMAND=(python -m hoodie.experiments run-shard --bundle "$BUNDLE_DIR" --work-dir "$WORK_DIR")
if [[ -n "$MAX_RUNTIME" ]]; then
  COMMAND+=(--max-runtime-seconds "$MAX_RUNTIME")
fi
"${COMMAND[@]}" | tee "$WORK_DIR/${SHARD_ID}-last-run.json"

RESULT_DIR="$WORK_DIR/results/$SHARD_ID"
RESULT_BUNDLE="$RESULT_DIR/result_bundle.json"
[[ -f "$RESULT_BUNDLE" ]] || {
  echo "Shard did not produce a result bundle: $RESULT_BUNDLE" >&2
  exit 1
}
STATUS="$(python - "$RESULT_BUNDLE" <<'PY'
import json
import pathlib
import sys
payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
print(payload.get("status", "unknown"))
PY
)"

if [[ "$STATUS" != "completed" ]]; then
  cat >&2 <<EOF
Shard $SHARD_ID ($PHASE) is $STATUS.
Preserve this exact work directory and run the same command again to resume it.
Do not import this result bundle until status is completed.
EOF
  exit 3
fi

printf 'Completed shard: %s\nResult directory: %s\n' "$SHARD_ID" "$RESULT_DIR"
