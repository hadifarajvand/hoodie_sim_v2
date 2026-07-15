#!/usr/bin/env python3
"""Run each active pytest file as bounded shard and summarize results."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
TEST_LIST = ROOT / "artifacts/hoodie/implementation_run/tests/active_test_files.txt"
SHARD_DIR = ROOT / "artifacts/hoodie/implementation_run/tests/shards"
COLLECTION_DIR = ROOT / "artifacts/hoodie/implementation_run/tests/collection"
RESULTS_JSON = ROOT / "artifacts/hoodie/implementation_run/tests/shard_results.json"
SUMMARY_TXT = ROOT / "artifacts/hoodie/implementation_run/tests/shard_summary.txt"
DEFAULT_TIMEOUT = 300


@dataclass
class ShardResult:
    test_file: str
    safe_name: str
    status: str
    exit_code: int | None
    duration_seconds: float
    log_path: str
    command: list[str]
    stdout_tail: str
    stderr_tail: str


def safe_name(path: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "__", path)
    if len(slug) > 180:
        digest = hashlib.sha1(path.encode("utf-8")).hexdigest()[:10]
        slug = f"{slug[:160]}__{digest}"
    return slug


def read_test_files() -> list[str]:
    lines = TEST_LIST.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip()]


def tail(text: str, limit: int = 4000) -> str:
    return text[-limit:]


def run_file(test_file: str) -> ShardResult:
    shard_name = safe_name(test_file)
    log_path = SHARD_DIR / f"{shard_name}.log"
    command = [sys.executable, "-m", "pytest", "-q", test_file, "--tb=short"]
    start = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
            env=os.environ.copy(),
        )
        duration = time.monotonic() - start
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        log_path.write_text(stdout + ("\n" if stdout and stderr else "") + stderr, encoding="utf-8")
        if completed.returncode == 0:
            status = "pass"
        elif "collected 0 items" in stdout.lower() or "collected 0 items" in stderr.lower():
            status = "collection_error"
        else:
            status = "fail"
        return ShardResult(
            test_file=test_file,
            safe_name=shard_name,
            status=status,
            exit_code=completed.returncode,
            duration_seconds=round(duration, 3),
            log_path=str(log_path.relative_to(ROOT)),
            command=command,
            stdout_tail=tail(stdout),
            stderr_tail=tail(stderr),
        )
    except subprocess.TimeoutExpired as exc:
        duration = time.monotonic() - start
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        log_path.write_text(stdout + ("\n" if stdout and stderr else "") + stderr + "\n[TIMEOUT]\n", encoding="utf-8")
        return ShardResult(
            test_file=test_file,
            safe_name=shard_name,
            status="timeout",
            exit_code=None,
            duration_seconds=round(duration, 3),
            log_path=str(log_path.relative_to(ROOT)),
            command=command,
            stdout_tail=tail(stdout),
            stderr_tail=tail(stderr),
        )
    except BaseException as exc:  # noqa: BLE001
        duration = time.monotonic() - start
        log_path.write_text(f"[CRASH] {type(exc).__name__}: {exc}\n", encoding="utf-8")
        return ShardResult(
            test_file=test_file,
            safe_name=shard_name,
            status="crash",
            exit_code=None,
            duration_seconds=round(duration, 3),
            log_path=str(log_path.relative_to(ROOT)),
            command=command,
            stdout_tail="",
            stderr_tail=f"{type(exc).__name__}: {exc}",
        )


def write_json_atomic(path: Path, payload: object) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def summarize(results: Iterable[ShardResult]) -> str:
    items = list(results)
    counts: dict[str, int] = {}
    for result in items:
        counts[result.status] = counts.get(result.status, 0) + 1
    lines = [f"total={len(items)}"]
    for key in ["pass", "fail", "collection_error", "timeout", "crash"]:
        lines.append(f"{key}={counts.get(key, 0)}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--failed-only", action="store_true")
    args = parser.parse_args()

    SHARD_DIR.mkdir(parents=True, exist_ok=True)
    COLLECTION_DIR.mkdir(parents=True, exist_ok=True)

    files = read_test_files()
    if args.failed_only and RESULTS_JSON.exists():
        prior = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
        failed = {entry["test_file"] for entry in prior.get("results", []) if entry["status"] != "pass"}
        files = [path for path in files if path in failed]

    results: list[ShardResult] = []
    for test_file in files:
        results.append(run_file(test_file))

    payload = {"results": [asdict(result) for result in results]}
    write_json_atomic(RESULTS_JSON, payload)
    SUMMARY_TXT.write_text(summarize(results), encoding="utf-8")
    print(SUMMARY_TXT.read_text(encoding="utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
