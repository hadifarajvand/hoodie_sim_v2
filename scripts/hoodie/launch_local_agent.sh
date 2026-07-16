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
  exit 3
fi

prompt_file="docs/runbooks/agent-execution-prompt.md"
[[ -f "$prompt_file" ]] || {
  echo "Missing agent prompt: $prompt_file" >&2
  exit 4
}

validator="scripts/hoodie/validate_run_root.py"
[[ -f "$validator" ]] || {
  echo "Missing output-root validator: $validator" >&2
  exit 5
}

agent_bin="${HOODIE_AGENT_BIN:-claude}"
command -v "$agent_bin" >/dev/null 2>&1 || {
  echo "Claude Code executable not found: $agent_bin" >&2
  echo "Set HOODIE_AGENT_BIN to the Claude Code executable when it is not named 'claude'." >&2
  exit 6
}

candidate_root="${HOODIE_RUN_ROOT:-<not set>}"
printf 'Launching Claude Code through %s on branch %s at %s\n' "$agent_bin" "$BRANCH" "$local_sha"
printf 'Current HOODIE_RUN_ROOT candidate: %s\n' "$candidate_root"
printf 'Claude Code must ask you to provide or confirm the output root, test it, show the result, and obtain your approval before any simulation starts.\n'

exec "$agent_bin" "$(cat "$prompt_file")"
