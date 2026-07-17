#!/usr/bin/env bash
set -euo pipefail

EXPECTED_REPOSITORY="hadifarajvand/hoodie_sim_v2"
EXPECTED_BRANCH="echo/verified-figures-5-8"
EXPECTED_HTTPS="https://github.com/${EXPECTED_REPOSITORY}.git"
EXPECTED_SSH="git@github.com:${EXPECTED_REPOSITORY}.git"

fail() {
  printf 'ACTIVE_BRANCH_SYNC_FAILED: %s\n' "$1" >&2
  exit 1
}

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)"
cd "$repo_root"

origin_url="$(git remote get-url origin 2>/dev/null || true)"
case "$origin_url" in
  "$EXPECTED_HTTPS"|"$EXPECTED_SSH") ;;
  *) fail "origin is '$origin_url'; expected canonical repository" ;;
esac

if [[ -n "$(git status --porcelain)" ]]; then
  git status --short --branch >&2
  fail "working tree is dirty; preserve or commit the changes before syncing"
fi

git fetch --prune origin "$EXPECTED_BRANCH"

current_branch="$(git branch --show-current)"
if [[ "$current_branch" != "$EXPECTED_BRANCH" ]]; then
  if git show-ref --verify --quiet "refs/heads/$EXPECTED_BRANCH"; then
    git switch "$EXPECTED_BRANCH"
  else
    git switch --track -c "$EXPECTED_BRANCH" "origin/$EXPECTED_BRANCH"
  fi
fi

git merge --ff-only "origin/$EXPECTED_BRANCH"
bash scripts/echo/verify_single_repository.sh

local_sha="$(git rev-parse HEAD)"
remote_sha="$(git rev-parse "origin/$EXPECTED_BRANCH")"
[[ "$local_sha" == "$remote_sha" ]] || fail "local and remote SHAs differ"

printf 'ACTIVE_BRANCH_SYNC_COMPLETE\n'
printf 'sha=%s\n' "$local_sha"
