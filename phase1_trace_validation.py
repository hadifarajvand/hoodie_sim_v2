from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def _as_int(value: str | None):
    if value in (None, "", "None"):
        return None
    return int(float(value))


def _as_float(value: str | None):
    if value in (None, "", "None"):
        return None
    return float(value)


def _count_present(rows: list[dict[str, str]], field: str) -> int:
    return sum(1 for row in rows if row.get(field) not in (None, "", "None"))


def audit_trace_dir(output_dir: str | Path) -> dict[str, object]:
    output_dir = Path(output_dir)
    task_rows = _read_csv(output_dir / "task_lifecycle.csv")
    queue_rows = _read_csv(output_dir / "queue_trace.csv")
    action_rows = _read_csv(output_dir / "action_trace.csv")
    episode_rows = _read_csv(output_dir / "episode_metrics.csv")

    task_ids = [_as_int(row.get("task_id")) for row in task_rows]
    task_id_set = {task_id for task_id in task_ids if task_id is not None}
    episode_rows_by_id = {(_as_int(row.get("episode_id"))): row for row in episode_rows}
    total_tasks = sum((_as_int(row.get("total_tasks")) or 0) for row in episode_rows)
    completed_tasks = sum((_as_int(row.get("completed_tasks")) or 0) for row in episode_rows)
    dropped_tasks = sum((_as_int(row.get("dropped_tasks")) or 0) for row in episode_rows)
    pending_tasks = sum((_as_int(row.get("pending_tasks")) or 0) for row in episode_rows)
    selected_action_present = _count_present(task_rows, "selected_action")
    selected_action_missing = len(task_rows) - selected_action_present
    selected_action_by_status: dict[str, dict[str, int]] = {}
    for status in ("completed", "dropped", "pending"):
        status_rows = [row for row in task_rows if row.get("final_status") == status]
        selected_action_by_status[status] = {
            "rows": len(status_rows),
            "present": _count_present(status_rows, "selected_action"),
            "missing": len(status_rows) - _count_present(status_rows, "selected_action"),
        }
    completed_missing_selected_action = selected_action_by_status["completed"]["missing"]
    dropped_missing_selected_action = selected_action_by_status["dropped"]["missing"]

    task_count_match = (completed_tasks + dropped_tasks + pending_tasks) == total_tasks
    unique_lifecycle_match = len(task_id_set) == total_tasks

    warnings: list[str] = []
    errors: list[str] = []

    if len(task_ids) != len(task_id_set):
        errors.append("task_id uniqueness violated")
    if not task_count_match:
        errors.append("task count mismatch across episode_metrics")
    if not unique_lifecycle_match:
        errors.append("unique task_id count does not match episode_metrics total_tasks")
    if completed_missing_selected_action or dropped_missing_selected_action:
        warnings.append(
            "completed or dropped tasks are missing selected_action coverage"
        )

    for row in task_rows:
        status = row.get("final_status")
        if status not in {"completed", "dropped", "pending"}:
            errors.append(f"invalid final_status: {status}")
        for field in ("latency", "waiting_time", "service_time"):
            value = _as_float(row.get(field))
            if value is not None and value < 0:
                errors.append(f"negative {field} for task {row.get('task_id')}")
        queue_enter = _as_int(row.get("queue_enter_time"))
        service_start = _as_int(row.get("service_start_time"))
        arrival = _as_int(row.get("arrival_time"))
        completion = _as_int(row.get("completion_time"))
        drop_time = _as_int(row.get("drop_time"))
        service_end = _as_int(row.get("service_end_time"))
        if queue_enter is not None and service_start is not None and service_start < queue_enter:
            errors.append(f"service_start_time < queue_enter_time for task {row.get('task_id')}")
        if service_end is not None and service_start is not None and service_end < service_start:
            errors.append(f"service_end_time < service_start_time for task {row.get('task_id')}")
        if arrival is not None and completion is not None and completion < arrival:
            errors.append(f"completion_time < arrival_time for task {row.get('task_id')}")
        if completion is not None and service_end is not None and completion < service_end:
            errors.append(f"completion_time < service_end_time for task {row.get('task_id')}")
        if row.get("final_status") == "completed":
            if completion is None:
                errors.append(f"completed task missing completion_time for task {row.get('task_id')}")
            if drop_time is not None:
                errors.append(f"completed task has drop_time for task {row.get('task_id')}")
            if service_end is None:
                warnings.append(f"completed task missing service_end_time for task {row.get('task_id')}")
        if row.get("final_status") == "dropped":
            if drop_time is None:
                warnings.append(f"dropped task missing drop_time for task {row.get('task_id')}")
            if row.get("drop_reason") in (None, "", "None"):
                warnings.append(f"dropped task missing drop_reason for task {row.get('task_id')}")
            if completion is not None:
                errors.append(f"dropped task has completion_time for task {row.get('task_id')}")
        if row.get("final_status") == "pending":
            # Pending tasks are allowed to have null terminal fields in the legacy runtime.
            pass

    for row in queue_rows:
        qlen = _as_float(row.get("queue_length"))
        if qlen is not None and qlen < 0:
            errors.append(f"negative queue_length at node {row.get('node_id')} time {row.get('time')}")
        episode_id = _as_int(row.get("episode_id"))
        if episode_id not in episode_rows_by_id:
            warnings.append(f"queue trace references episode_id {episode_id} missing from episode_metrics")

    for row in episode_rows:
        completed = _as_int(row.get("completed_tasks")) or 0
        dropped = _as_int(row.get("dropped_tasks")) or 0
        pending = _as_int(row.get("pending_tasks")) or 0
        total = _as_int(row.get("total_tasks")) or 0
        drop_ratio = _as_float(row.get("drop_ratio"))
        if completed + dropped + pending != total:
            errors.append(f"task count mismatch for episode {row.get('episode_id')}")
        if drop_ratio is not None and not (0.0 <= drop_ratio <= 1.0):
            errors.append(f"drop_ratio out of range for episode {row.get('episode_id')}")

    if not action_rows:
        errors.append("no action traces present")
    for row in action_rows:
        episode_id = _as_int(row.get("episode_id"))
        if episode_id not in episode_rows_by_id:
            warnings.append(f"action trace references episode_id {episode_id} missing from episode_metrics")

    return {
        "summary": {
            "total_tasks_from_metrics": total_tasks,
            "unique_lifecycle_task_ids": len(task_id_set),
            "completed_tasks": completed_tasks,
            "dropped_tasks": dropped_tasks,
            "pending_tasks": pending_tasks,
            "task_count_consistent": task_count_match,
            "unique_task_count_consistent": unique_lifecycle_match,
            "selected_action_present": selected_action_present,
            "selected_action_missing": selected_action_missing,
            "selected_action_by_final_status": selected_action_by_status,
        },
        "warnings": warnings,
        "errors": errors,
    }

def validate_trace_dir(output_dir: str | Path) -> list[str]:
    audit = audit_trace_dir(output_dir)
    errors = list(audit["errors"])
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir")
    args = parser.parse_args()
    audit = audit_trace_dir(args.output_dir)
    print(json.dumps(audit["summary"], indent=2, sort_keys=True))
    for warning in audit["warnings"]:
        print(f"WARNING: {warning}")
    errors = list(audit["errors"])
    if errors:
        for err in errors:
            print(err)
        return 1
    print("validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
