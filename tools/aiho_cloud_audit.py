#!/usr/bin/env python3
"""Bounded technical eligibility audit for lixin-jnu/AIHO.

This script does not modify the upstream repository. It runs the exact upstream
programs, then creates explicitly labelled diagnostic copies for seed control
and for one confirmed LFU membership defect.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import pickle
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path.cwd()
AIHO = ROOT / "aiho"
RESULTS = ROOT / "aiho-audit-results"
RESULTS.mkdir(parents=True, exist_ok=True)
DATA_FILES = [
    "data/data.pk",
    "data/function.pk",
    "data/eua-bsc500.pk",
    "data/eua-bsc500-hop.pk",
]
SCRIPTS = ["local_only.py", "local_cloud.py", "local_cloud_edge.py"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_sample(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, bytes):
        return {"type": "bytes", "length": len(value)}
    if isinstance(value, dict):
        keys = list(value.keys())[:5]
        return {"type": "dict", "length": len(value), "sample_keys": [repr(k) for k in keys]}
    if isinstance(value, (list, tuple)):
        sample = []
        for item in list(value)[:2]:
            sample.append(safe_sample(item))
        return {"type": type(value).__name__, "length": len(value), "sample": sample}
    shape = getattr(value, "shape", None)
    dtype = getattr(value, "dtype", None)
    if shape is not None:
        return {"type": type(value).__name__, "shape": list(shape), "dtype": str(dtype)}
    return {"type": type(value).__name__, "repr": repr(value)[:300]}


def audit_data() -> dict[str, Any]:
    report: dict[str, Any] = {}
    for rel in DATA_FILES:
        path = AIHO / rel
        item: dict[str, Any] = {
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else None,
            "sha256": sha256(path) if path.exists() else None,
        }
        if path.exists():
            started = time.perf_counter()
            try:
                with path.open("rb") as f:
                    value = pickle.load(f)
                item["load_ok"] = True
                item["load_seconds"] = round(time.perf_counter() - started, 6)
                item["object"] = safe_sample(value)
            except Exception as exc:  # pragma: no cover - diagnostic path
                item["load_ok"] = False
                item["error"] = f"{type(exc).__name__}: {exc}"
        report[rel] = item
    return report


def audit_source() -> dict[str, Any]:
    report: dict[str, Any] = {}
    for rel in SCRIPTS:
        path = AIHO / rel
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text, filename=rel)
        opened = re.findall(r'open\(r?["\']([^"\']+)["\']', text)
        top_level_calls = []
        for node in tree.body:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                top_level_calls.append(ast.unparse(node.value)[:300])
        report[rel] = {
            "sha256": sha256(path),
            "line_count": len(text.splitlines()),
            "functions": [n.name for n in tree.body if isinstance(n, ast.FunctionDef)],
            "classes": [n.name for n in tree.body if isinstance(n, ast.ClassDef)],
            "opened_paths": opened,
            "top_level_calls": top_level_calls,
            "has_numpy_seed": "np.random.seed" in text,
            "lfu_membership_bug_pattern": "def inCache(self, key):\n        if key in self.f2kv:" in text,
            "hardcoded_node_count_125": bool(re.search(r"\bn\s*=\s*125\b", text)),
            "hardcoded_return_t_200": "if t == 200:" in text,
        }
    return report


def parse_time_v(stderr: str) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    patterns = {
        "max_rss_kb": r"Maximum resident set size \(kbytes\):\s*(\d+)",
        "user_seconds": r"User time \(seconds\):\s*([0-9.]+)",
        "system_seconds": r"System time \(seconds\):\s*([0-9.]+)",
        "cpu_percent": r"Percent of CPU this job got:\s*([^\n]+)",
        "exit_status_time": r"Exit status:\s*(\d+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, stderr)
        if match:
            value = match.group(1).strip()
            parsed[key] = float(value) if key in {"user_seconds", "system_seconds"} else int(value) if key in {"max_rss_kb", "exit_status_time"} else value
    return parsed


def parse_numeric_stdout(stdout: str) -> list[float]:
    values: list[float] = []
    for line in stdout.splitlines():
        line = line.strip()
        try:
            values.append(float(line))
        except ValueError:
            continue
    return values


def run_script(path: Path, label: str, timeout_seconds: int = 1800) -> dict[str, Any]:
    out_path = RESULTS / f"{label}.stdout.txt"
    err_path = RESULTS / f"{label}.stderr.txt"
    cmd = [
        "timeout", "--signal=TERM", str(timeout_seconds),
        "/usr/bin/time", "-v", sys.executable, "-u", str(path),
    ]
    started = time.perf_counter()
    proc = subprocess.run(
        cmd,
        cwd=AIHO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    wall = time.perf_counter() - started
    out_path.write_text(proc.stdout, encoding="utf-8")
    err_path.write_text(proc.stderr, encoding="utf-8")
    result = {
        "label": label,
        "script": str(path.relative_to(AIHO)),
        "command": cmd,
        "returncode": proc.returncode,
        "wall_seconds": round(wall, 6),
        "timed_out": proc.returncode == 124,
        "numeric_stdout": parse_numeric_stdout(proc.stdout),
        "stdout_tail": proc.stdout.splitlines()[-20:],
        "stderr_tail": proc.stderr.splitlines()[-30:],
    }
    result.update(parse_time_v(proc.stderr))
    return result


def make_seeded_copy(seed: int, fix_lfu: bool = False) -> Path:
    source = AIHO / "local_cloud_edge.py"
    text = source.read_text(encoding="utf-8")
    injection = f"import numpy as np\nnp.random.seed({seed})  # audit-only deterministic seed"
    text = text.replace("import numpy as np", injection, 1)
    suffix = f"seed_{seed}" + ("_lfu_fixed" if fix_lfu else "")
    if fix_lfu:
        old = "def inCache(self, key):\n        if key in self.f2kv:"
        new = "def inCache(self, key):\n        if key in self.k2f:"
        if old not in text:
            raise RuntimeError("Expected LFU defect pattern not found")
        text = text.replace(old, new, 1)
    destination = AIHO / f"audit_local_cloud_edge_{suffix}.py"
    destination.write_text(text, encoding="utf-8")
    return destination


def main() -> int:
    metadata = {
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "upstream_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=AIHO, text=True).strip(),
        "pip_freeze": subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True).splitlines(),
    }
    before_hashes = {rel: sha256(AIHO / rel) for rel in DATA_FILES}
    data_report = audit_data()
    source_report = audit_source()

    runs: list[dict[str, Any]] = []
    for script in SCRIPTS:
        runs.append(run_script(AIHO / script, f"original_{Path(script).stem}"))

    seeded_runs: list[dict[str, Any]] = []
    for seed in (101, 202, 303):
        copy = make_seeded_copy(seed, fix_lfu=False)
        seeded_runs.append(run_script(copy, f"aiho_seed_{seed}"))

    fixed_copy = make_seeded_copy(101, fix_lfu=True)
    fixed_run = run_script(fixed_copy, "aiho_seed_101_lfu_fixed")

    after_hashes = {rel: sha256(AIHO / rel) for rel in DATA_FILES}
    data_unchanged = before_hashes == after_hashes

    original_ok = all(r["returncode"] == 0 for r in runs)
    seeded_ok = all(r["returncode"] == 0 for r in seeded_runs)
    outputs_complete = all(len(r["numeric_stdout"]) >= 3 for r in runs + seeded_runs + [fixed_run])
    max_rss_kb = max([r.get("max_rss_kb", 0) for r in runs + seeded_runs + [fixed_run]] or [0])
    total_wall_seconds = sum(r["wall_seconds"] for r in runs + seeded_runs + [fixed_run])
    all_data_ok = all(item.get("exists") and item.get("load_ok") for item in data_report.values())
    technical_eligible = bool(
        original_ok
        and seeded_ok
        and fixed_run["returncode"] == 0
        and outputs_complete
        and all_data_ok
        and data_unchanged
        and max_rss_kb < 8 * 1024 * 1024
        and total_wall_seconds < 7200
    )

    summary = {
        "metadata": metadata,
        "data": data_report,
        "source": source_report,
        "runs": runs,
        "seeded_aiho_runs": seeded_runs,
        "lfu_fixed_diagnostic": fixed_run,
        "data_unchanged": data_unchanged,
        "max_rss_kb": max_rss_kb,
        "total_wall_seconds": round(total_wall_seconds, 6),
        "technical_eligible": technical_eligible,
        "eligibility_conditions": {
            "original_scripts_exit_zero": original_ok,
            "controlled_seed_runs_exit_zero": seeded_ok,
            "expected_numeric_outputs_present": outputs_complete,
            "all_serialized_data_load": all_data_ok,
            "input_data_not_modified": data_unchanged,
            "peak_rss_under_8gb": max_rss_kb < 8 * 1024 * 1024,
            "total_audit_runtime_under_2h": total_wall_seconds < 7200,
        },
    }
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# AIHO Cloud Eligibility Audit",
        "",
        f"- Upstream commit: `{metadata['upstream_commit']}`",
        f"- Technical eligibility: **{technical_eligible}**",
        f"- Total measured run time: **{total_wall_seconds:.3f} s**",
        f"- Peak RSS: **{max_rss_kb / 1024:.2f} MiB**",
        f"- Input data unchanged: **{data_unchanged}**",
        "",
        "## Exact upstream runs",
        "",
        "| Run | Exit | Wall s | Peak MiB | Numeric outputs |",
        "|---|---:|---:|---:|---|",
    ]
    for r in runs:
        md.append(f"| {r['label']} | {r['returncode']} | {r['wall_seconds']:.3f} | {r.get('max_rss_kb', 0)/1024:.2f} | `{r['numeric_stdout']}` |")
    md.extend(["", "## Controlled-seed AIHO runs", "", "| Seed | Exit | Wall s | Peak MiB | Numeric outputs |", "|---:|---:|---:|---:|---|"])
    for r in seeded_runs:
        seed = r["label"].rsplit("_", 1)[-1]
        md.append(f"| {seed} | {r['returncode']} | {r['wall_seconds']:.3f} | {r.get('max_rss_kb', 0)/1024:.2f} | `{r['numeric_stdout']}` |")
    md.extend([
        "",
        "## LFU diagnostic",
        "",
        "The upstream `LFUCache.inCache` checks function IDs against the frequency-index dictionary (`f2kv`) instead of the key-to-frequency dictionary (`k2f`). The fixed run changes only that membership test and is not treated as an upstream reproduction.",
        "",
        f"- Seed-101 upstream outputs: `{seeded_runs[0]['numeric_stdout']}`",
        f"- Seed-101 LFU-fixed outputs: `{fixed_run['numeric_stdout']}`",
        "",
        "## Automated gate",
        "",
    ])
    for key, value in summary["eligibility_conditions"].items():
        md.append(f"- {key}: **{value}**")
    (RESULTS / "REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps({
        "technical_eligible": technical_eligible,
        "total_wall_seconds": total_wall_seconds,
        "max_rss_kb": max_rss_kb,
        "result_dir": str(RESULTS),
    }, indent=2))
    return 0 if technical_eligible else 2


if __name__ == "__main__":
    raise SystemExit(main())
