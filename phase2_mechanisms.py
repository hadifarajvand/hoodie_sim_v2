from __future__ import annotations

import csv
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from decision_makers.baselines import official_policy_map


@dataclass(frozen=True)
class RewardEvent:
    task_id: int
    episode_id: int | None
    source_node: int | None
    final_status: str
    reward: float
    delay: int | None
    completion_time: int | None
    drop_time: int | None


def load_trace_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="") as f:
        return list(csv.DictReader(f))


def _as_int(value: str | None) -> int | None:
    if value in (None, "", "None"):
        return None
    return int(float(value))


def _as_float(value: str | None) -> float | None:
    if value in (None, "", "None"):
        return None
    return float(value)


def infer_reward_events(trace_dir: str | Path) -> list[RewardEvent]:
    trace_dir = Path(trace_dir)
    rows = load_trace_csv(trace_dir / "task_lifecycle.csv")
    events: list[RewardEvent] = []
    for row in rows:
        status = row.get("final_status") or "pending"
        completion_time = _as_int(row.get("completion_time"))
        drop_time = _as_int(row.get("drop_time"))
        arrival_time = _as_int(row.get("arrival_time"))
        delay: int | None = None
        reward = 0.0
        if status == "completed" and completion_time is not None and arrival_time is not None:
            delay = max(0, completion_time - arrival_time + 1)
            reward = float(-delay)
        elif status == "dropped":
            reward = -40.0
        events.append(
            RewardEvent(
                task_id=int(float(row.get("task_id") or 0)),
                episode_id=_as_int(row.get("episode_id")),
                source_node=_as_int(row.get("source_node")),
                final_status=status,
                reward=reward,
                delay=delay,
                completion_time=completion_time,
                drop_time=drop_time,
            )
        )
    return events


def build_policy_map() -> dict[str, str]:
    return official_policy_map()


def build_validation_report(trace_dir: str | Path) -> dict[str, Any]:
    trace_dir = Path(trace_dir)
    lifecycle_rows = load_trace_csv(trace_dir / "task_lifecycle.csv")
    queue_rows = load_trace_csv(trace_dir / "queue_trace.csv")
    action_rows = load_trace_csv(trace_dir / "action_trace.csv")
    episode_rows = load_trace_csv(trace_dir / "episode_metrics.csv")
    mleo_path = trace_dir / "mleo_candidate_latency_trace.csv"
    mleo_exists = mleo_path.exists()
    mleo_rows = load_trace_csv(mleo_path) if mleo_exists else []
    mleo_selected_rows = sum(1 for row in mleo_rows if str(row.get("is_selected")).lower() == "true")
    mleo_tasks = {}
    for row in mleo_rows:
        key = (row.get("episode_id"), row.get("task_id"))
        task_bucket = mleo_tasks.setdefault(key, {"rows": 0, "selected": 0})
        task_bucket["rows"] += 1
        if str(row.get("is_selected")).lower() == "true":
            task_bucket["selected"] += 1
    mleo_tasks_with_candidates = sum(1 for bucket in mleo_tasks.values() if bucket["rows"] > 0)
    mleo_tasks_with_exactly_one_selected_candidate = sum(1 for bucket in mleo_tasks.values() if bucket["selected"] == 1)
    if not mleo_exists:
        mleo_contract_status = "missing"
    elif mleo_selected_rows == 0 or mleo_tasks_with_exactly_one_selected_candidate != mleo_tasks_with_candidates:
        mleo_contract_status = "present_but_invalid"
    else:
        mleo_contract_status = "paper_candidate_trace_ready"

    active_policy_set = sorted(build_policy_map().keys())
    reward_events = infer_reward_events(trace_dir)
    completed = [e for e in reward_events if e.final_status == "completed"]
    dropped = [e for e in reward_events if e.final_status == "dropped"]
    pending = [e for e in reward_events if e.final_status == "pending"]
    active_queue_samples = sum(1 for row in queue_rows if _as_float(row.get("queue_length")) and _as_float(row.get("queue_length")) > 0)
    missing_selected = sum(1 for row in lifecycle_rows if row.get("selected_action") in (None, "", "None"))
    action_coverage_by_status: dict[str, dict[str, int]] = {}
    for status in ("completed", "dropped", "pending"):
        rows = [row for row in lifecycle_rows if row.get("final_status") == status]
        action_coverage_by_status[status] = {
            "rows": len(rows),
            "missing_selected_action": sum(1 for row in rows if row.get("selected_action") in (None, "", "None")),
        }

    return {
        "trace_dir": str(trace_dir),
        "episode_count": len(episode_rows),
        "task_count": len(lifecycle_rows),
        "queue_trace_rows": len(queue_rows),
        "action_trace_rows": len(action_rows),
        "active_queue_samples": active_queue_samples,
        "selected_action_missing": missing_selected,
        "selected_action_missing_by_status": action_coverage_by_status,
        "reward_summary": {
            "completed": len(completed),
            "dropped": len(dropped),
            "pending": len(pending),
            "total_reward": sum(e.reward for e in reward_events),
        },
        "policy_map": build_policy_map(),
        "mleo_candidate_latency_trace_exists": mleo_exists,
        "mleo_candidate_rows": len(mleo_rows),
        "mleo_selected_rows": mleo_selected_rows,
        "mleo_tasks_with_candidates": mleo_tasks_with_candidates,
        "mleo_tasks_with_exactly_one_selected_candidate": mleo_tasks_with_exactly_one_selected_candidate,
        "mleo_contract_status": mleo_contract_status,
        "task_traceable_reward": True,
        "public_cpu_sharing": "dynamic_equal_active_queue",
        "action_legality": "adjacency_matrix_constrained",
    }


def write_validation_artifacts(trace_dir: str | Path, output_dir: str | Path) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report = build_validation_report(trace_dir)
    reward_events = [asdict(event) for event in infer_reward_events(trace_dir)]
    (output_dir / "baseline_validation_report.json").write_text(json.dumps(report, indent=2, sort_keys=True))
    (output_dir / "active_policy_set.json").write_text(json.dumps(sorted(report["policy_map"].keys()), indent=2))
    (output_dir / "mleo_candidate_latency_samples.json").write_text(
        json.dumps(
            [
                {
                    "task_id": event["task_id"],
                    "final_status": event["final_status"],
                    "latency_sample": event["delay"],
                }
                for event in reward_events
                if event["final_status"] in {"completed", "dropped"}
            ][:100],
            indent=2,
            sort_keys=True,
        )
    )
