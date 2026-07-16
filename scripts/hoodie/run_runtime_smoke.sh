#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

if [[ -n "$(git status --porcelain=v1 --untracked-files=all)" ]]; then
  git status --short --branch >&2
  echo "SMOKE_REFUSED_DIRTY_WORKTREE" >&2
  exit 2
fi

python -m pip install -e '.[dev]'
python scripts/hoodie/runtime_smoke.py
python -m pytest -q \
  tests_supported/hoodie/unit/test_experiment_correctness_v2.py \
  tests_supported/hoodie/unit/test_destination_action_fidelity.py \
  tests/unit/test_run_root_validation.py

printf 'HOODIE_RUNTIME_SMOKE_SUCCEEDED sha=%s\n' "$(git rev-parse HEAD)"
