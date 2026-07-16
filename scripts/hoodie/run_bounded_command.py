#!/usr/bin/env python3
"""Run a command while retaining only a bounded diagnostic tail.

The child is never signalled by this wrapper. Scientific progress belongs in
atomic progress/status files, not unbounded stdout logs.
"""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path
import subprocess
import sys
import time


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-bytes", type=int, default=2 * 1024 * 1024)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        parser.error("a command is required after --")
    if args.max_bytes <= 0:
        parser.error("--max-bytes must be positive")
    return args


def main() -> int:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    process = subprocess.Popen(
        args.command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,
    )
    assert process.stdout is not None

    chunks: deque[bytes] = deque()
    retained = 0
    observed = 0
    while True:
        block = process.stdout.read(64 * 1024)
        if not block:
            break
        observed += len(block)
        chunks.append(block)
        retained += len(block)
        while retained > args.max_bytes and chunks:
            excess = retained - args.max_bytes
            head = chunks[0]
            if len(head) <= excess:
                chunks.popleft()
                retained -= len(head)
            else:
                chunks[0] = head[excess:]
                retained -= excess

    return_code = process.wait()
    payload = b"".join(chunks)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(args.output)

    summary = {
        "command": args.command[0],
        "exit_code": return_code,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "observed_output_bytes": observed,
        "retained_output_bytes": len(payload),
        "output": str(args.output),
    }
    import json

    print(json.dumps(summary, sort_keys=True))
    if return_code != 0 and payload:
        text = payload.decode("utf-8", errors="replace").splitlines()
        for line in text[-100:]:
            print(line, file=sys.stderr)
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
