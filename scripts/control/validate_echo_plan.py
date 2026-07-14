#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict, deque
from pathlib import Path

PLAN_VERSION = "ECHO-MEP-v4.2"
EXPECTED_PHASE_TOTALS = [6, 23, 20, 12, 12]
EXPECTED_STATUS = {"VERIFIED_COMPLETE": 5, "READY": 2, "BLOCKED": 66}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True)
    parser.add_argument("--json")
    args = parser.parse_args()

    plan_path = Path(args.plan)
    text = plan_path.read_text(encoding="utf-8")
    errors: list[str] = []

    if PLAN_VERSION not in text:
        fail(errors, f"missing plan version {PLAN_VERSION}")

    registry_pattern = re.compile(
        r"^\| ([A-Z]+-\d{3}) \| (READY|BLOCKED|VERIFIED_COMPLETE) \| ([^|]+) \| ([^|]+) \|$",
        re.M,
    )
    registry_rows = registry_pattern.findall(text)
    registry_ids = [row[0] for row in registry_rows]
    card_ids = re.findall(r"^### ([A-Z]+-\d{3}) —", text, re.M)

    if len(registry_ids) != 73 or len(set(registry_ids)) != 73:
        fail(errors, f"registry IDs: {len(registry_ids)} total/{len(set(registry_ids))} unique")
    if len(card_ids) != 73 or len(set(card_ids)) != 73:
        fail(errors, f"card IDs: {len(card_ids)} total/{len(set(card_ids))} unique")
    if set(registry_ids) != set(card_ids):
        fail(errors, "registry/card ID sets differ")

    status_counts = Counter(row[1] for row in registry_rows)
    if dict(status_counts) != EXPECTED_STATUS:
        fail(errors, f"status counts mismatch: {dict(status_counts)}")

    phase_counts = []
    for phase in range(5):
        match = re.search(rf"^### Phase {phase} — .+ \((\d+)\)$", text, re.M)
        phase_counts.append(int(match.group(1)) if match else -1)
    if phase_counts != EXPECTED_PHASE_TOTALS:
        fail(errors, f"phase totals mismatch: {phase_counts}")

    id_set = set(registry_ids)
    dependencies: dict[str, list[str]] = {}
    for task_id, _status, dep_text, _title in registry_rows:
        deps = [] if dep_text.strip() == "NONE" else [value.strip() for value in dep_text.split(",")]
        dependencies[task_id] = deps
        for dep in deps:
            if dep not in id_set:
                fail(errors, f"{task_id}: missing dependency {dep}")
            if dep == task_id:
                fail(errors, f"{task_id}: self dependency")

    indegree = {task_id: 0 for task_id in registry_ids}
    graph: dict[str, list[str]] = defaultdict(list)
    for task_id, deps in dependencies.items():
        for dep in deps:
            graph[dep].append(task_id)
            indegree[task_id] += 1
    queue = deque([task_id for task_id, degree in indegree.items() if degree == 0])
    visited = 0
    while queue:
        task_id = queue.popleft()
        visited += 1
        for child in graph[task_id]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    if visited != len(registry_ids):
        fail(errors, "dependency graph contains a cycle")

    allowed_write_lines = [
        line[len("- **Allowed writes:**") :]
        for line in text.splitlines()
        if line.startswith("- **Allowed writes:**")
    ]
    if len(allowed_write_lines) != 73:
        fail(errors, f"allowed-write card count mismatch: {len(allowed_write_lines)}")
    for line in allowed_write_lines:
        if "*" in line:
            fail(errors, f"wildcard permission detected: {line}")

    required_contracts = [
        "BASE-005 — Extract neutral synchronized multi-EA kernel and remove ECHO contamination",
        "ECHO-001 — Attach ECHO adapter to frozen neutral hooks",
        "ECHO-009 — Implement size-specific N+2 canonical action space",
        "ECHO-012 — Implement Equations (51)–(54) size-specific normalized state",
        "ECHO-015 — Implement Equations (61)–(67) masked DDQL with within-run parameter sharing",
        "| ECHO-011 | BLOCKED | ECHO-010, EVAL-001 |",
        "It must not execute `BASE-001` in the same invocation",
        "## 11. Exact reviewer/controller prompt",
        "Permanent deletion",
    ]
    for contract in required_contracts:
        if contract not in text:
            fail(errors, f"missing required contract: {contract}")

    for task_id, status, _deps, _title in registry_rows:
        if status != "READY":
            continue
        card_match = re.search(
            rf"^### {re.escape(task_id)} —.*?(?=^### [A-Z]+-\d{{3}} —|\Z)",
            text,
            re.M | re.S,
        )
        if not card_match:
            fail(errors, f"missing card body for READY task {task_id}")
            continue
        body = card_match.group(0)
        writes_match = re.search(r"^- \*\*Allowed writes:\*\* (.+)$", body, re.M)
        command_match = re.search(r"^- \*\*Exact command:\*\*\n```bash\n(.*?)\n```", body, re.M | re.S)
        if not writes_match or not command_match:
            fail(errors, f"{task_id}: missing writes or command")
            continue
        writes = set(re.findall(r"`([^`]+)`", writes_match.group(1)))
        command = command_match.group(1)
        referenced = re.findall(r"(?:python3\s+|pytest\s+)([\w./-]+\.py)", command)
        for ref in referenced:
            if not Path(ref).exists() and ref not in writes:
                fail(errors, f"{task_id}: command references absent uncreated file {ref}")

    report = {
        "plan": str(plan_path),
        "plan_version": PLAN_VERSION,
        "result": "PASS" if not errors else "FAIL",
        "registry_task_count": len(registry_ids),
        "card_task_count": len(card_ids),
        "phase_totals": phase_counts,
        "status_totals": dict(status_counts),
        "errors": errors,
    }
    if args.json:
        output_path = Path(args.json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
