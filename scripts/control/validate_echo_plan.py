#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict, deque
from pathlib import Path

PLAN_VERSION = "ECHO-MEP-v4.3"
EXPECTED_PHASE_TOTALS = [6, 23, 20, 12, 12]
EXPECTED_STATUS = {"VERIFIED_COMPLETE": 5, "READY": 2, "BLOCKED": 66}
EXPECTED_SNAPSHOT_SHA = "3a3382e0ab0a49fb10bda7cc1740ea3a771032d7962e1957fa105eae5a5c06cc"
EXPECTED_REVISION = "280"


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    if "within-run parameter sharing" in text:
        fail(errors, "stale within-run parameter-sharing text remains")
    if "ECHO-MEP-v4.2" in text:
        fail(errors, "stale v4.2 reference remains")

    registry_pattern = re.compile(r"^\| ([A-Z]+-\d{3}) \| (READY|BLOCKED|VERIFIED_COMPLETE) \| ([^|]+) \| ([^|]+) \|$", re.M)
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

    allowed_write_lines = [line[len("- **Allowed writes:**") :] for line in text.splitlines() if line.startswith("- **Allowed writes:**")]
    if len(allowed_write_lines) != 73:
        fail(errors, f"allowed-write card count mismatch: {len(allowed_write_lines)}")
    for line in allowed_write_lines:
        if "*" in line:
            fail(errors, f"wildcard permission detected: {line}")

    live_dir = Path("research/authority/echo/live")
    metadata = json.loads((live_dir / "source_metadata.json").read_text(encoding="utf-8"))
    next_task = json.loads(Path("artifacts/control/NEXT_TASK.json").read_text(encoding="utf-8"))
    execution_state = json.loads(Path("artifacts/control/EXECUTION_STATE.json").read_text(encoding="utf-8"))

    if metadata.get("google_drive_revision_id") != EXPECTED_REVISION:
        fail(errors, f"source metadata revision mismatch: {metadata.get('google_drive_revision_id')}")
    if metadata.get("normalized_sha256") != EXPECTED_SNAPSHOT_SHA:
        fail(errors, "source metadata snapshot sha mismatch")
    if metadata.get("tab_title") is not None:
        fail(errors, "source metadata tab title not null")
    if metadata.get("tab_title_asserted") is not False:
        fail(errors, "source metadata tab title asserted")

    if not re.search(r"\| Google Drive current revision \| `280` \|", text):
        fail(errors, "missing Drive revision 280 contract")
    if metadata.get("normalized_sha256") != EXPECTED_SNAPSHOT_SHA:
        fail(errors, "missing snapshot SHA contract")
    if metadata.get("equation_count") != 67:
        fail(errors, "missing equation-count contract")
    if metadata.get("algorithm_1_line_count") != 23:
        fail(errors, "missing Algorithm 1 line contract")
    if metadata.get("algorithm_2_line_count") != 14:
        fail(errors, "missing Algorithm 2 line contract")
    if "No tab title may be asserted." not in text and "No tab title is asserted." not in text:
        fail(errors, "missing no-tab-title contract")
    if "independent per-EA learner" not in text and "independent per-EA learners" not in text:
        fail(errors, "missing independent per-EA learner contract")
    if "within-run parameter sharing" in text or "shared parameters within run" in text:
        fail(errors, "parameter-sharing clause remains")
    if "N+2" not in text:
        fail(errors, "missing N+2 contract")
    if "checkpoint identity" not in text and "per-(N, EA, training_seed, method, config_hash)" not in text:
        fail(errors, "missing checkpoint lineage contract")
    if "BASE-005" not in text or "ECHO-001" not in text or "EVAL-001" not in text:
        fail(errors, "missing task-card override contracts")
    if "Permanent deletion" not in text:
        fail(errors, "missing permanent-deletion contract")

    if next_task.get("task_id") is not None:
        fail(errors, "NEXT_TASK.task_id must be null")
    if next_task.get("authorization_status") != "PENDING_INDEPENDENT_REVIEW":
        fail(errors, f"unexpected NEXT_TASK authorization status: {next_task.get('authorization_status')}")
    if execution_state.get("plan_version") != PLAN_VERSION:
        fail(errors, f"execution state plan version mismatch: {execution_state.get('plan_version')}")
    if execution_state.get("reconciliation_status") != "IMPLEMENTED_PENDING_INDEPENDENT_REVIEW":
        fail(errors, f"execution state reconciliation status mismatch: {execution_state.get('reconciliation_status')}")
    if execution_state.get("execution_paused") is not True:
        fail(errors, "execution_paused must remain true")
    if execution_state.get("attempts", {}).get("SRC-001") != 3:
        fail(errors, f"SRC-001 attempt mismatch: {execution_state.get('attempts', {}).get('SRC-001')}")

    for task_id, status, _deps, _title in registry_rows:
        if status != "READY":
            continue
        card_match = re.search(rf"^### {re.escape(task_id)} —.*?(?=^### [A-Z]+-\d{{3}} —|\Z)", text, re.M | re.S)
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

    manifest_hash = sha256(live_dir / "ECHO_PROPOSED_METHOD.md")
    if manifest_hash != EXPECTED_SNAPSHOT_SHA:
        fail(errors, f"snapshot sha mismatch: {manifest_hash}")

    report = {
        "plan": str(plan_path),
        "plan_version": PLAN_VERSION,
        "result": "PASS" if not errors else "FAIL",
        "registry_task_count": len(registry_ids),
        "card_task_count": len(card_ids),
        "phase_totals": phase_counts,
        "status_totals": dict(status_counts),
        "source_revision": EXPECTED_REVISION,
        "snapshot_sha256": EXPECTED_SNAPSHOT_SHA,
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
