#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

LEGACY_CAMPAIGN_ID="figures-8-11-7587c7c6382c"
TRAINING_SHARDS="${HOODIE_TRAINING_SHARDS:-17}"
EVALUATION_SHARDS="${HOODIE_EVALUATION_SHARDS:-48}"
MAX_CAPTURE_BYTES="${HOODIE_MAX_COMMAND_CAPTURE_BYTES:-2097152}"
MIN_FREE_GB="${HOODIE_MIN_FREE_GB:-20}"
MIN_FREE_FRACTION="${HOODIE_MIN_FREE_FRACTION:-0.10}"

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

validate_storage_thresholds() {
  python - "$MIN_FREE_GB" "$MIN_FREE_FRACTION" "${CI:-false}" <<'PY'
import sys
minimum_gb = int(sys.argv[1])
minimum_fraction = float(sys.argv[2])
ci = sys.argv[3].lower() == "true"
if minimum_gb <= 0:
    raise SystemExit("HOODIE_MIN_FREE_GB must be positive")
if not 0.0 < minimum_fraction < 1.0:
    raise SystemExit("HOODIE_MIN_FREE_FRACTION must be in (0, 1)")
if not ci and minimum_gb < 20:
    raise SystemExit("non-CI execution may not reserve less than 20 GiB")
if not ci and minimum_fraction < 0.10:
    raise SystemExit("non-CI execution may not reserve less than 10% free space")
PY
}

require_external_run_root() {
  validate_storage_thresholds
  [[ -n "${HOODIE_RUN_ROOT:-}" ]] || fail "HOODIE_RUN_ROOT must be set to an absolute path on large external storage"
  [[ "$HOODIE_RUN_ROOT" = /* ]] || fail "HOODIE_RUN_ROOT must be absolute"

  RUN_ROOT="$(python - "$ROOT_DIR" "$HOODIE_RUN_ROOT" "$MIN_FREE_GB" "$MIN_FREE_FRACTION" <<'PY'
from pathlib import Path
import shutil
import sys
repo = Path(sys.argv[1]).resolve()
root = Path(sys.argv[2]).expanduser().resolve()
minimum_gb = int(sys.argv[3])
minimum_fraction = float(sys.argv[4])
if root == repo or repo in root.parents:
    raise SystemExit("HOODIE_RUN_ROOT must be outside the Git repository")
root.mkdir(parents=True, exist_ok=True)
usage = shutil.disk_usage(root)
required = max(minimum_gb * 1024**3, int(usage.total * minimum_fraction))
if usage.free < required:
    raise SystemExit(
        f"insufficient free storage: free={usage.free}, required={required}"
    )
print(root)
PY
  )" || fail "external run-root validation failed"
  export HOODIE_RUN_ROOT="$RUN_ROOT"

  STATE_DIR="${HOODIE_STATE_DIR:-$RUN_ROOT/implementation_run/corrected_campaign}"
  MATRIX_PATH="${HOODIE_MATRIX_PATH:-$STATE_DIR/expected_production_job_matrix.json}"
  SHARD_PLAN_PATH="${HOODIE_SHARD_PLAN_PATH:-$STATE_DIR/shard_plan.json}"
  CAMPAIGN_ENV_PATH="${HOODIE_CAMPAIGN_ENV_PATH:-$STATE_DIR/campaign.env}"
  VALIDATION_MARKER="${HOODIE_VALIDATION_MARKER:-$STATE_DIR/validation-complete.json}"
  AUDIT_DIR="${HOODIE_AUDIT_DIR:-$RUN_ROOT/audits/repository}"
  BUNDLE_ROOT="${HOODIE_BUNDLE_ROOT:-$RUN_ROOT/distributed/corrected/input}"
  TRAINING_RESULTS_DIR="${HOODIE_TRAINING_RESULTS_DIR:-$RUN_ROOT/distributed/corrected/results-training}"
  EVALUATION_RESULTS_DIR="${HOODIE_EVALUATION_RESULTS_DIR:-$RUN_ROOT/distributed/corrected/results-evaluation}"
  CAMPAIGN_ROOT="$RUN_ROOT/campaigns"
  mkdir -p "$STATE_DIR" "$AUDIT_DIR"
}

require_external_run_root

run_bounded() {
  local output="$1"
  shift
  python scripts/hoodie/run_bounded_command.py \
    --output "$output" \
    --max-bytes "$MAX_CAPTURE_BYTES" \
    -- "$@"
}

require_clean_worktree() {
  local dirty
  dirty="$(git status --porcelain=v1 --untracked-files=all)"
  [[ -z "$dirty" ]] || {
    printf '%s\n' "$dirty" >&2
    fail "working tree must be clean before validation or execution"
  }
}

require_empty_or_absent() {
  local path="$1"
  if [[ -d "$path" ]] && [[ -n "$(find "$path" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]]; then
    fail "refusing to overwrite nonempty runtime directory: $path"
  fi
}

load_campaign_id() {
  if [[ -n "${HOODIE_CAMPAIGN_ID:-}" ]]; then
    CAMPAIGN_ID="$HOODIE_CAMPAIGN_ID"
  elif [[ -f "$CAMPAIGN_ENV_PATH" ]]; then
    # shellcheck disable=SC1090
    source "$CAMPAIGN_ENV_PATH"
    CAMPAIGN_ID="${CAMPAIGN_ID:-}"
  else
    fail "No corrected campaign is planned. Run '$0 validate' first."
  fi
  [[ -n "$CAMPAIGN_ID" ]] || fail "CAMPAIGN_ID is empty"
  [[ "$CAMPAIGN_ID" != "$LEGACY_CAMPAIGN_ID" ]] || fail "Refusing to operate on the paused legacy campaign"
  [[ "$CAMPAIGN_ID" == figures-8-11-corrected-* ]] || fail "Unexpected corrected campaign ID: $CAMPAIGN_ID"
  export CAMPAIGN_ID
}

require_validated_head() {
  require_clean_worktree
  load_campaign_id
  [[ -f "$VALIDATION_MARKER" ]] || fail "validation marker is missing; run '$0 validate'"
  python - "$VALIDATION_MARKER" "$(git rev-parse HEAD)" "$CAMPAIGN_ID" <<'PY'
import json
import pathlib
import sys
payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["validated_head"] == sys.argv[2], payload
assert payload["campaign_id"] == sys.argv[3], payload
assert payload["repository_audit_passed"] is True, payload
assert payload["full_test_suite_passed"] is True, payload
assert payload["production_started"] is False, payload
PY
}

plan_campaign() {
  local output="$STATE_DIR/plan-output.json"
  run_bounded "$output" python -m hoodie.experiments plan \
    --matrix "$MATRIX_PATH" \
    --shard-plan "$SHARD_PLAN_PATH" \
    --campaign-root "$CAMPAIGN_ROOT" \
    --training-shards "$TRAINING_SHARDS" \
    --evaluation-shards "$EVALUATION_SHARDS"
  CAMPAIGN_ID="$(python - "$output" <<'PY'
import json
import pathlib
import sys
payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
print(payload["campaign_id"])
PY
  )"
  [[ "$CAMPAIGN_ID" != "$LEGACY_CAMPAIGN_ID" ]] || fail "Planner resolved the paused legacy campaign"
  [[ "$CAMPAIGN_ID" == figures-8-11-corrected-* ]] || fail "Planner returned an unexpected campaign ID: $CAMPAIGN_ID"
  printf 'CAMPAIGN_ID=%q\n' "$CAMPAIGN_ID" > "$CAMPAIGN_ENV_PATH"
  export CAMPAIGN_ID
}

storage_check() {
  python - "$RUN_ROOT" "$MIN_FREE_GB" "$MIN_FREE_FRACTION" <<'PY'
from pathlib import Path
import json
import os
import shutil
import sys
root = Path(sys.argv[1])
minimum_gb = int(sys.argv[2])
minimum_fraction = float(sys.argv[3])
usage = shutil.disk_usage(root)
required = max(minimum_gb * 1024**3, int(usage.total * minimum_fraction))
checkpoint_count = 0
checkpoint_bytes = 0
largest = 0
for directory, _subdirs, filenames in os.walk(root):
    if "checkpoint.pt" not in filenames:
        continue
    path = Path(directory) / "checkpoint.pt"
    try:
        size = path.stat().st_size
    except FileNotFoundError:
        continue
    checkpoint_count += 1
    checkpoint_bytes += size
    largest = max(largest, size)
payload = {
    "run_root": str(root),
    "free_bytes": usage.free,
    "total_bytes": usage.total,
    "required_free_bytes": required,
    "checkpoint_count": checkpoint_count,
    "checkpoint_bytes": checkpoint_bytes,
    "largest_checkpoint_bytes": largest,
    "passed": usage.free >= required,
}
print(json.dumps(payload, sort_keys=True))
if not payload["passed"]:
    raise SystemExit(1)
PY
}

validate() {
  require_clean_worktree
  bash -n scripts/hoodie/corrected_campaign.sh
  bash -n scripts/hoodie/run_shard_worker.sh

  run_bounded "$STATE_DIR/pip-install.txt" python -m pip install -e ".[dev]"
  run_bounded "$STATE_DIR/repository-audit.txt" \
    python scripts/audit/full_repository_audit.py \
      --check \
      --output-dir "$AUDIT_DIR"
  run_bounded "$STATE_DIR/compileall.txt" python -m compileall -q src hoodie scripts
  run_bounded "$STATE_DIR/preflight.json" python -m hoodie.experiments preflight

  plan_campaign

  run_bounded "$STATE_DIR/contract-validation.json" \
    python -m hoodie.experiments validate-contracts \
      --campaign-id "$CAMPAIGN_ID" \
      --matrix "$MATRIX_PATH"
  run_bounded "$STATE_DIR/pytest-full.txt" python -m pytest -q
  storage_check > "$STATE_DIR/storage-check.json"

  python - "$MATRIX_PATH" "$SHARD_PLAN_PATH" "$VALIDATION_MARKER" "$CAMPAIGN_ID" "$(git rev-parse HEAD)" <<'PY'
import hashlib
import json
import pathlib
import sys
matrix_path = pathlib.Path(sys.argv[1])
plan_path = pathlib.Path(sys.argv[2])
marker_path = pathlib.Path(sys.argv[3])
campaign_id = sys.argv[4]
head = sys.argv[5]
matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
plan = json.loads(plan_path.read_text(encoding="utf-8"))
training = [row for row in matrix if row["job_type"] == "training"]
evaluation = [row for row in matrix if row["job_type"] == "evaluation"]
assert len(matrix) == 305, len(matrix)
assert len(training) == 17, len(training)
assert len(evaluation) == 288, len(evaluation)
assert plan["total_jobs"] == 305
assert plan["training_jobs"] == 17
assert plan["evaluation_jobs"] == 288
assert plan["campaign_id"] == campaign_id
assert campaign_id.startswith("figures-8-11-corrected-")
assert campaign_id != "figures-8-11-7587c7c6382c"
assert all(
    row["physical_contract"].get("backend") == "worker-selected"
    for row in matrix
)
payload = {
    "validated_head": head,
    "campaign_id": campaign_id,
    "matrix_sha256": hashlib.sha256(matrix_path.read_bytes()).hexdigest(),
    "shard_plan_sha256": hashlib.sha256(plan_path.read_bytes()).hexdigest(),
    "training_jobs": 17,
    "evaluation_jobs": 288,
    "total_jobs": 305,
    "repository_audit_passed": True,
    "full_test_suite_passed": True,
    "production_started": False,
}
marker_path.write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(json.dumps(payload, sort_keys=True))
PY
  printf 'Validated corrected campaign %s at %s\n' "$CAMPAIGN_ID" "$(git rev-parse HEAD)"
}

export_training() {
  require_validated_head
  storage_check
  local destination="$BUNDLE_ROOT/$CAMPAIGN_ID/training"
  require_empty_or_absent "$destination"
  run_bounded "$STATE_DIR/export-training.json" \
    python -m hoodie.experiments export-shards \
      --campaign-id "$CAMPAIGN_ID" \
      --plan "$SHARD_PLAN_PATH" \
      --output-dir "$destination" \
      --phase training
  printf 'Training bundles: %s\n' "$destination"
}

import_training() {
  require_validated_head
  [[ -d "$TRAINING_RESULTS_DIR" ]] || fail "Training results directory is missing: $TRAINING_RESULTS_DIR"
  run_bounded "$STATE_DIR/import-training.json" \
    python -m hoodie.experiments import-results-directory \
      --campaign-id "$CAMPAIGN_ID" \
      --results-dir "$TRAINING_RESULTS_DIR"
  local audit="$STATE_DIR/backend-audit.json"
  run_bounded "$audit" python -m hoodie.experiments backend-audit \
    --campaign-id "$CAMPAIGN_ID"
  python - "$audit" <<'PY'
import json
import pathlib
import sys
payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
backends = [
    value for value in payload.get("checkpoint_backends", [])
    if value != "legacy_unknown"
]
assert payload.get("checkpoint_count") == 17, payload
assert "legacy_unknown" not in payload.get("checkpoint_backends", []), payload
assert len(set(backends)) == 1, payload
print(json.dumps({
    "status": "training-backend-compatible",
    "backend": backends[0],
    "checkpoint_count": 17,
}))
PY
  run_bounded "$STATE_DIR/shard-status-after-training.json" \
    python -m hoodie.experiments shard-status --campaign-id "$CAMPAIGN_ID"
}

export_evaluation() {
  require_validated_head
  storage_check
  [[ -f "$STATE_DIR/backend-audit.json" ]] || fail "Import and audit all training results before exporting evaluation shards"
  local destination="$BUNDLE_ROOT/$CAMPAIGN_ID/evaluation"
  require_empty_or_absent "$destination"
  run_bounded "$STATE_DIR/export-evaluation.json" \
    python -m hoodie.experiments export-shards \
      --campaign-id "$CAMPAIGN_ID" \
      --plan "$SHARD_PLAN_PATH" \
      --output-dir "$destination" \
      --phase evaluation
  printf 'Evaluation bundles: %s\n' "$destination"
}

import_evaluation() {
  require_validated_head
  [[ -d "$EVALUATION_RESULTS_DIR" ]] || fail "Evaluation results directory is missing: $EVALUATION_RESULTS_DIR"
  run_bounded "$STATE_DIR/import-evaluation.json" \
    python -m hoodie.experiments import-results-directory \
      --campaign-id "$CAMPAIGN_ID" \
      --results-dir "$EVALUATION_RESULTS_DIR"
  run_bounded "$STATE_DIR/shard-status-after-evaluation.json" \
    python -m hoodie.experiments shard-status --campaign-id "$CAMPAIGN_ID"
}

status() {
  require_validated_head
  python -m hoodie.experiments shard-status --campaign-id "$CAMPAIGN_ID"
}

finalize() {
  require_validated_head
  run_bounded "$STATE_DIR/finalize.json" \
    python -m hoodie.experiments finalize --campaign-id "$CAMPAIGN_ID"
}

case "${1:-}" in
  validate) validate ;;
  storage-check) storage_check ;;
  export-training) export_training ;;
  import-training) import_training ;;
  export-evaluation) export_evaluation ;;
  import-evaluation) import_evaluation ;;
  status) status ;;
  finalize) finalize ;;
  *)
    cat >&2 <<USAGE
Usage: $0 {validate|storage-check|export-training|import-training|export-evaluation|import-evaluation|status|finalize}

HOODIE_RUN_ROOT must be an absolute path outside the Git repository. Non-CI
execution reserves at least 20 GiB and 10% free space. This script never operates
on $LEGACY_CAMPAIGN_ID and never starts a worker by itself. Workers use
scripts/hoodie/run_shard_worker.sh.
USAGE
    exit 2
    ;;
esac
