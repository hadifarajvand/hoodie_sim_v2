#!/usr/bin/env bash
set -euo pipefail

QUESTION="${*:-}"
GRAPH="${GRAPHIFY_GRAPH:-graphify-out/graph.json}"
TIMEOUT_SEC="${GRAPHIFY_TIMEOUT_SEC:-60}"

if [ -z "$QUESTION" ]; then
  echo "ERROR: missing question" >&2
  echo "Usage: scripts/graphify-query-safe.sh <question>" >&2
  exit 2
fi

if ! command -v graphify >/dev/null 2>&1; then
  echo "ERROR: graphify CLI not found" >&2
  exit 10
fi

if [ ! -f "$GRAPH" ]; then
  echo "ERROR: graph not found: $GRAPH" >&2
  echo "Run first: graphify ." >&2
  exit 11
fi

python3 - "$TIMEOUT_SEC" "$GRAPH" "$QUESTION" <<'EOF'
import subprocess
import sys
import time

timeout = int(sys.argv[1])
graph = sys.argv[2]
question = sys.argv[3]

cmd = ["graphify", "query", question, "--graph", graph]

print("COMMAND:", " ".join(cmd))
start = time.time()

try:
    result = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        timeout=timeout
    )

    print("EXIT_CODE:", result.returncode)
    print("DURATION_SEC:", round(time.time() - start, 2))
    print("--- STDOUT_START ---")
    print(result.stdout[:12000])
    print("--- STDOUT_END ---")
    print("--- STDERR_START ---")
    print(result.stderr[:6000])
    print("--- STDERR_END ---")

    sys.exit(result.returncode)

except subprocess.TimeoutExpired as e:
    print(f"TIMEOUT_AFTER_SEC: {timeout}")

    stdout = e.stdout or ""
    stderr = e.stderr or ""

    if isinstance(stdout, bytes):
        stdout = stdout.decode("utf-8", errors="replace")
    if isinstance(stderr, bytes):
        stderr = stderr.decode("utf-8", errors="replace")

    print("--- PARTIAL_STDOUT_START ---")
    print(stdout[:6000])
    print("--- PARTIAL_STDOUT_END ---")
    print("--- PARTIAL_STDERR_START ---")
    print(stderr[:6000])
    print("--- PARTIAL_STDERR_END ---")

    sys.exit(124)
EOF