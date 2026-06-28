#!/usr/bin/env bash
set -euo pipefail

echo "Safe inspection only. This script does not read secret contents."
find . -maxdepth 3 -type f \( \
  -name "AGENTS.md" -o \
  -name "CLAUDE.md" -o \
  -name "opencode.json" -o \
  -name "opencode.jsonc" -o \
  -name "package.json" -o \
  -name "pyproject.toml" -o \
  -name "requirements.txt" -o \
  -name "README.md" -o \
  -name ".graphifyignore" \
\) | sort

