from __future__ import annotations

import argparse
import csv
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


def validate_trace_dir(output_dir: str | Path) -> list[str]:
    output_dir = Path(output_dir)
    errors: list[str] = []
    task_rows = _read_csv(output_dir / "task_lifecycle.csv")
    queue_rows = _read_csv(output_dir / "queue_trace.csv")
    action_rows = _read_csv(output_dir / "action_trace.csv")
    episode_rows = _read_csv(output_dir / "episode_metrics.csv")

    task_ids = [_as_int(row.get("task_id")) for row in task_rows]
    if len(task_ids) != len(set(task_ids)):
        errors.append("task_id uniqueness violated")

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
        if queue_enter is not None and service_start is not None and service_start < queue_enter:
            errors.append(f"service_start_time < queue_enter_time for task {row.get('task_id')}")
        if arrival is not None and completion is not None and completion < arrival:
            errors.append(f"completion_time < arrival_time for task {row.get('task_id')}")

    for row in queue_rows:
        qlen = _as_float(row.get("queue_length"))
        if qlen is not None and qlen < 0:
            errors.append(f"negative queue_length at node {row.get('node_id')} time {row.get('time')}")

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

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir")
    args = parser.parse_args()
    errors = validate_trace_dir(args.output_dir)
    if errors:
        for err in errors:
            print(err)
        return 1
    print("validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

