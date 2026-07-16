#!/usr/bin/env bash
set -euo pipefail

BRANCH="chatgpt/experiment-correctness-20260716"
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

if [[ -n "$(git status --porcelain=v1 --untracked-files=all)" ]]; then
  git status --short --branch >&2
  echo "LOCAL_WORKTREE_DIRTY: refusing to fetch, reset, clean, stash, overwrite, or launch the agent." >&2
  exit 2
fi

if [[ -z "${HOODIE_RUN_ROOT:-}" ]]; then
  echo "HOODIE_RUN_ROOT must be set to an absolute path outside the repository." >&2
  exit 3
fi

python - "$ROOT" "$HOODIE_RUN_ROOT" <<'PY'
from pathlib import Path
import shutil
import sys
repo = Path(sys.argv[1]).resolve()
root = Path(sys.argv[2]).expanduser().resolve()
if not root.is_absolute() or root == repo or repo in root.parents:
    raise SystemExit("HOODIE_RUN_ROOT must be absolute and outside the repository")
root.mkdir(parents=True, exist_ok=True)
usage = shutil.disk_usage(root)
required = max(20 * 1024**3, int(usage.total * 0.10))
if usage.free < required:
    raise SystemExit(
        f"insufficient external storage: free={usage.free}, required={required}"
    )
print(f"HOODIE_RUN_ROOT={root}")
print(f"free_bytes={usage.free}")
print(f"required_free_bytes={required}")
PY


git fetch origin "$BRANCH"

current_branch="$(git branch --show-current)"
if [[ "$current_branch" != "$BRANCH" ]]; then
  if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    git switch "$BRANCH"
  else
    git switch --track -c "$BRANCH" "origin/$BRANCH"
  fi
fi

git merge --ff-only "origin/$BRANCH"

local_sha="$(git rev-parse HEAD)"
remote_sha="$(git rev-parse "origin/$BRANCH")"
if [[ "$local_sha" != "$remote_sha" ]]; then
  echo "Local and remote SHA differ after fast-forward: local=$local_sha remote=$remote_sha" >&2
  exit 4
fi

prompt_file="docs/runbooks/agent-execution-prompt.md"
[[ -f "$prompt_file" ]] || {
  echo "Missing agent prompt: $prompt_file" >&2
  exit 5
}

agent_bin="${HOODIE_AGENT_BIN:-claude}"
command -v "$agent_bin" >/dev/null 2>&1 || {
  echo "Agent executable not found: $agent_bin" >&2
  echo "Set HOODIE_AGENT_BIN to your local coding-agent executable." >&2
  exit 6
}

printf 'Launching %s on branch %s at %s\n' "$agent_bin" "$BRANCH" "$local_sha"
printf 'External run root: %s\n' "$HOODIE_RUN_ROOT"
printf 'The agent must pass all gates before starting paper-scale work.\n'

exec "$agent_bin" "$(cat "$prompt_file")"
