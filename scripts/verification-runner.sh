#!/usr/bin/env bash
set -euo pipefail

if [ -f package.json ] && grep -q '"test"' package.json; then
  npm test
elif [ -d .venv ] && [ -x .venv/bin/python ]; then
  .venv/bin/python -m pytest
else
  python3 -m pytest
fi

