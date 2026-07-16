#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

LEGACY_CAMPAIGN_ID="figures-8-11-7587c7c6382c"
STATE_DIR="${HOODIE_STATE_DIR:-artifacts/hoodie/implementation_run/corrected_campaign}"
MATRIX_PATH="${HOODIE_MATRIX_PATH:-$STATE_DIR/expected_production_job_matrix.json}"
SHARD_PLAN_PATH="${HOODIE_SHARD_PLAN_PATH:-$STATE_DIR/shard_plan.json}"
CAMPAIGN_ENV_PATH="${HOODIE_CAMPAIGN_ENV_PATH:-$STATE_DIR/campaign.env}"
BUNDLE_ROOT="${HOODIE_BUNDLE_ROOT:-artifacts/hoodie/distributed/corrected/input}"
TRAINING_RESULTS_DIR="${HOODIE_TRAINING_RESULTS_DIR:-artifacts/hoodie/distributed/corrected/results-training}"
EVALUATION_RESULTS_DIR="${HOODIE_EVALUATION_RESULTS_DIR:-artifacts/hoodie/distributed/corrected/results-evaluation}"
TRAINING_SHARDS="${HOODIE_TRAINING_SHARDS:-17}"
EVALUATION_SHARDS="${HOODIE_EVALUATION_SHARDS:-48}"

mkdir -p "$STATE_DIR"

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
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

plan_campaign() {
  local output="$STATE_DIR/plan-output.json"
  python -m hoodie.experiments plan \
    --matrix "$MATRIX_PATH" \
    --shard-plan "$SHARD_PLAN_PATH" \
    --campaign-root artifacts/hoodie/campaigns \
    --training-shards "$TRAINING_SHARDS" \
    --evaluation-shards "$EVALUATION_SHARDS" | tee "$output"
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

validate() {
  bash -n scripts/hoodie/corrected_campaign.sh
  bash -n scripts/hoodie/run_shard_worker.sh
  python -m pip install -e ".[dev]"
  python -m compileall -q src hoodie
  python -m hoodie.experiments preflight | tee "$STATE_DIR/preflight.json"
  plan_campaign
  python -m hoodie.experiments validate-contracts \
    --campaign-id "$CAMPAIGN_ID" \
    --matrix "$MATRIX_PATH" | tee "$STATE_DIR/contract-validation.json"
  python -m pytest tests_supported/hoodie -q | tee "$STATE_DIR/pytest-supported.txt"
  python - "$MATRIX_PATH" "$SHARD_PLAN_PATH" <<'PY'
import json
import pathlib
import sys
matrix = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
plan = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
training = [row for row in matrix if row["job_type"] == "training"]
evaluation = [row for row in matrix if row["job_type"] == "evaluation"]
assert len(matrix) == 305, len(matrix)
assert len(training) == 17, len(training)
assert len(evaluation) == 288, len(evaluation)
assert plan["total_jobs"] == 305
assert plan["training_jobs"] == 17
assert plan["evaluation_jobs"] == 288
assert plan["campaign_id"].startswith("figures-8-11-corrected-")
assert plan["campaign_id"] != "figures-8-11-7587c7c6382c"
assert all(
    row["physical_contract"].get("backend") == "worker-selected"
    for row in matrix
)
print(json.dumps({"status": "validated", "campaign_id": plan["campaign_id"], "jobs": 305}))
PY
  printf '\nValidated corrected campaign: %s\n' "$CAMPAIGN_ID"
}

export_training() {
  load_campaign_id
  rm -rf "$BUNDLE_ROOT/training"
  python -m hoodie.experiments export-shards \
    --campaign-id "$CAMPAIGN_ID" \
    --plan "$SHARD_PLAN_PATH" \
    --output-dir "$BUNDLE_ROOT/training" \
    --phase training
  printf 'Training bundles: %s\n' "$BUNDLE_ROOT/training"
}

import_training() {
  load_campaign_id
  [[ -d "$TRAINING_RESULTS_DIR" ]] || fail "Training results directory is missing: $TRAINING_RESULTS_DIR"
  python -m hoodie.experiments import-results-directory \
    --campaign-id "$CAMPAIGN_ID" \
    --results-dir "$TRAINING_RESULTS_DIR"
  local audit="$STATE_DIR/backend-audit.json"
  python -m hoodie.experiments backend-audit \
    --campaign-id "$CAMPAIGN_ID" | tee "$audit"
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
  python -m hoodie.experiments shard-status --campaign-id "$CAMPAIGN_ID"
}

export_evaluation() {
  load_campaign_id
  [[ -f "$STATE_DIR/backend-audit.json" ]] || fail "Import and audit all training results before exporting evaluation shards"
  rm -rf "$BUNDLE_ROOT/evaluation"
  python -m hoodie.experiments export-shards \
    --campaign-id "$CAMPAIGN_ID" \
    --plan "$SHARD_PLAN_PATH" \
    --output-dir "$BUNDLE_ROOT/evaluation" \
    --phase evaluation
  printf 'Evaluation bundles: %s\n' "$BUNDLE_ROOT/evaluation"
}

import_evaluation() {
  load_campaign_id
  [[ -d "$EVALUATION_RESULTS_DIR" ]] || fail "Evaluation results directory is missing: $EVALUATION_RESULTS_DIR"
  python -m hoodie.experiments import-results-directory \
    --campaign-id "$CAMPAIGN_ID" \
    --results-dir "$EVALUATION_RESULTS_DIR"
  python -m hoodie.experiments shard-status --campaign-id "$CAMPAIGN_ID"
}

status() {
  load_campaign_id
  python -m hoodie.experiments shard-status --campaign-id "$CAMPAIGN_ID"
}

finalize() {
  load_campaign_id
  python -m hoodie.experiments finalize --campaign-id "$CAMPAIGN_ID"
}

case "${1:-}" in
  validate) validate ;;
  export-training) export_training ;;
  import-training) import_training ;;
  export-evaluation) export_evaluation ;;
  import-evaluation) import_evaluation ;;
  status) status ;;
  finalize) finalize ;;
  *)
    cat >&2 <<USAGE
Usage: $0 {validate|export-training|import-training|export-evaluation|import-evaluation|status|finalize}

The script never operates on $LEGACY_CAMPAIGN_ID and never starts a worker by itself.
Worker execution must use scripts/hoodie/run_shard_worker.sh on assigned compute.
USAGE
    exit 2
    ;;
esac
