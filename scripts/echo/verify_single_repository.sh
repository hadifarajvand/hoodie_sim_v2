#!/usr/bin/env bash
set -euo pipefail

EXPECTED_REPOSITORY="hadifarajvand/hoodie_sim_v2"
EXPECTED_HTTPS="https://github.com/${EXPECTED_REPOSITORY}.git"
EXPECTED_SSH="git@github.com:${EXPECTED_REPOSITORY}.git"
EXPECTED_BRANCH="echo/verified-figures-5-8"

fail() {
  printf 'SINGLE_REPOSITORY_GUARD_FAILED: %s\n' "$1" >&2
  exit 1
}

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" 
cd "$repo_root"

origin_url="$(git remote get-url origin 2>/dev/null || true)"
[[ -n "$origin_url" ]] || fail "origin remote is missing"

case "$origin_url" in
  "$EXPECTED_HTTPS"|"$EXPECTED_SSH") ;;
  *) fail "origin points to '$origin_url'; expected '$EXPECTED_HTTPS' or '$EXPECTED_SSH'" ;;
esac

push_url="$(git remote get-url --push origin 2>/dev/null || true)"
case "$push_url" in
  "$EXPECTED_HTTPS"|"$EXPECTED_SSH") ;;
  *) fail "origin push URL points to '$push_url'; expected the canonical repository" ;;
esac

branch="$(git branch --show-current)"
[[ "$branch" == "$EXPECTED_BRANCH" ]] || fail "active branch is '$branch'; expected '$EXPECTED_BRANCH'"

common_dir="$(git rev-parse --git-common-dir)"
git_dir="$(git rev-parse --git-dir)"

printf 'SINGLE_REPOSITORY_GUARD_PASSED\n'
printf 'repository=%s\n' "$EXPECTED_REPOSITORY"
printf 'origin=%s\n' "$origin_url"
printf 'branch=%s\n' "$branch"
printf 'worktree_root=%s\n' "$repo_root"
printf 'git_dir=%s\n' "$git_dir"
printf 'git_common_dir=%s\n' "$common_dir"
