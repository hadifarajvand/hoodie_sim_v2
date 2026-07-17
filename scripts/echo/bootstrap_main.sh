#!/usr/bin/env bash
set -euo pipefail

EXPECTED_REPOSITORY="hadifarajvand/hoodie_sim_v2"
EXPECTED_HTTPS="https://github.com/${EXPECTED_REPOSITORY}.git"
EXPECTED_SSH="git@github.com:${EXPECTED_REPOSITORY}.git"
EXPECTED_BRANCH="main"
DEFAULT_RUN_ROOT="/Volumes/ADATA-1TB-External/echo_outputs"

fail() {
  printf 'ECHO_MAIN_BOOTSTRAP_FAILED: %s\n' "$1" >&2
  exit 1
}

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)"
cd "$repo_root"

origin_url="$(git remote get-url origin 2>/dev/null || true)"
case "$origin_url" in
  "$EXPECTED_HTTPS"|"$EXPECTED_SSH") ;;
  *) fail "origin is '$origin_url'; expected canonical repository" ;;
esac

branch="$(git branch --show-current)"
[[ "$branch" == "$EXPECTED_BRANCH" ]] || fail "branch is '$branch'; expected '$EXPECTED_BRANCH'"

if [[ -n "$(git status --porcelain)" ]]; then
  git status --short --branch >&2
  fail "working tree is dirty"
fi

bash scripts/echo/verify_single_repository.sh

command -v python3.11 >/dev/null 2>&1 || fail "python3.11 is required; install Python 3.11 before continuing"
python_bin="python3.11"

if [[ -x .venv/bin/python ]]; then
  venv_version="$(.venv/bin/python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  if [[ "$venv_version" != "3.11" ]]; then
    backup_dir=".venv.backup-$(date +%Y%m%d-%H%M%S)"
    mv .venv "$backup_dir"
    printf 'Preserved incompatible virtual environment at %s\n' "$repo_root/$backup_dir"
  fi
fi

if [[ ! -d .venv ]]; then
  "$python_bin" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'

run_root="${ECHO_RUN_ROOT:-$DEFAULT_RUN_ROOT}"
[[ "$run_root" = /* ]] || fail "run root must be absolute"
[[ -d "$(dirname "$run_root")" ]] || fail "run-root parent does not exist: $(dirname "$run_root")"
mkdir -p "$run_root"
[[ -w "$run_root" ]] || fail "run root is not writable: $run_root"

repo_real="$(python -c 'from pathlib import Path; print(Path(".").resolve())')"
run_real="$(RUN_ROOT_CHECK="$run_root" python -c 'from pathlib import Path; import os; print(Path(os.environ["RUN_ROOT_CHECK"]).resolve())')"
case "$run_real" in
  "$repo_real"|"$repo_real"/*) fail "run root must stay outside the repository" ;;
esac

printf 'ECHO_MAIN_BOOTSTRAP_READY\n'
printf 'repository=%s\n' "$EXPECTED_REPOSITORY"
printf 'branch=%s\n' "$EXPECTED_BRANCH"
printf 'sha=%s\n' "$(git rev-parse HEAD)"
printf 'python=%s\n' "$(python --version 2>&1)"
printf 'venv=%s\n' "$repo_root/.venv"
printf 'run_root=%s\n' "$run_real"
printf 'next_prompt=%s\n' "$repo_root/docs/echo/TRAINED_PILOT_AGENT_PROMPT.md"
