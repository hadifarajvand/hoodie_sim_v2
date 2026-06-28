#!/usr/bin/env bash
set -euo pipefail

pwd
git rev-parse --show-toplevel 2>/dev/null || true
git status --short
echo
git diff --stat

