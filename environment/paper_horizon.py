from __future__ import annotations

from dataclasses import dataclass, asdict
import csv
from pathlib import Path
from typing import Any

PAPER_ACTION_SLOTS = 100
PAPER_DRAIN_SLOTS = 10
PAPER_TOTAL_SLOTS = PAPER_ACTION_SLOTS + PAPER_DRAIN_SLOTS


def is_action_slot(t: int) -> bool:
    return 0 <= int(t) < PAPER_ACTION_SLOTS


def is_drain_slot(t: int) -> bool:
    return PAPER_ACTION_SLOTS <= int(t) < PAPER_TOTAL_SLOTS


def slot_phase(t: int) -> str:
    if is_action_slot(t):
        return "action"
    if is_drain_slot(t):
        return "drain"
    return "outside"


def validate_paper_horizon(action_slots: int = PAPER_ACTION_SLOTS, drain_slots: int = PAPER_DRAIN_SLOTS) -> dict[str, int]:
    action_slots = int(action_slots)
    drain_slots = int(drain_slots)
    if action_slots <= 0:
        raise ValueError("action_slots must be > 0")
    if drain_slots < 0:
        raise ValueError("drain_slots must be >= 0")
    total_slots = action_slots + drain_slots
    return {
        "paper_action_slots": action_slots,
        "paper_drain_slots": drain_slots,
        "paper_total_slots": total_slots,
    }


@dataclass
class RunHorizonTraceRecord:
    episode_id: int
    time: int
    slot_phase: str
    paper_action_slot: bool
    paper_drain_slot: bool
    task_generation_allowed: bool
    decision_allowed: bool


def _safe_int(value: Any) -> int | None:
    if value in (None, "", "None"):
        return None
    try:
        return int(float(value))
    except Exception:
        return None


def _safe_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return False


def _read_csv(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _time_values_from_rows(rows: list[dict[str, Any]]) -> set[int]:
    values: set[int] = set()
    for row in rows:
        for key in ("time", "arrival_time", "completion_time", "drop_time"):
            value = _safe_int(row.get(key))
            if value is not None:
                values.add(value)
    return values


def _is_drain_event_from_action(row: dict[str, Any]) -> bool:
    if "slot_phase" in row:
        return str(row.get("slot_phase")) == "drain"
    return _safe_int(row.get("time")) is not None and _safe_int(row.get("time")) >= PAPER_ACTION_SLOTS


def build_run_horizon_report(trace_dir: str | Path) -> dict[str, Any]:
    trace_dir = Path(trace_dir)
    horizon_rows = _read_csv(trace_dir / "run_horizon_trace.csv")
    task_rows = _read_csv(trace_dir / "task_lifecycle.csv")
    action_rows = _read_csv(trace_dir / "action_trace.csv")
    queue_rows = _read_csv(trace_dir / "queue_trace.csv")
    delayed_reward_rows = _read_csv(trace_dir / "delayed_reward_event_trace.csv")

    all_times = set()
    for rows in (horizon_rows, task_rows, action_rows, queue_rows, delayed_reward_rows):
        all_times.update(_time_values_from_rows(rows))
    observed_total_slots = max(all_times) + 1 if all_times else PAPER_TOTAL_SLOTS
    observed_action_slots = sum(1 for row in horizon_rows if str(row.get("slot_phase")) == "action") if horizon_rows else min(observed_total_slots, PAPER_ACTION_SLOTS)
    observed_drain_slots = sum(1 for row in horizon_rows if str(row.get("slot_phase")) == "drain") if horizon_rows else max(0, observed_total_slots - PAPER_ACTION_SLOTS)

    task_generation_during_drain_count = 0
    for row in task_rows:
        arrival_time = _safe_int(row.get("arrival_time"))
        if arrival_time is not None and is_drain_slot(arrival_time):
            task_generation_during_drain_count += 1
    decision_rows_during_drain_count = 0
    for row in action_rows:
        time_value = _safe_int(row.get("time"))
        selected_action = row.get("selected_action")
        if time_value is not None and is_drain_slot(time_value) and selected_action not in (None, "", "None"):
            decision_rows_during_drain_count += 1
    queue_rows_during_drain_count = sum(1 for row in queue_rows if is_drain_slot(_safe_int(row.get("time")) or -1))
    completions_during_drain_count = 0
    drops_during_drain_count = 0
    for row in delayed_reward_rows:
        status = str(row.get("final_status"))
        time_value = _safe_int(row.get("completion_time")) if status == "completed" else _safe_int(row.get("drop_time"))
        if time_value is not None and is_drain_slot(time_value):
            if status == "completed":
                completions_during_drain_count += 1
            elif status == "dropped":
                drops_during_drain_count += 1

    horizon_contract_passed = (
        observed_action_slots == PAPER_ACTION_SLOTS
        and observed_drain_slots == PAPER_DRAIN_SLOTS
        and task_generation_during_drain_count == 0
        and decision_rows_during_drain_count == 0
    )
    report = {
        "paper_action_slots": PAPER_ACTION_SLOTS,
        "paper_drain_slots": PAPER_DRAIN_SLOTS,
        "paper_total_slots": PAPER_TOTAL_SLOTS,
        "observed_action_slots": observed_action_slots,
        "observed_drain_slots": observed_drain_slots,
        "observed_total_slots": observed_total_slots,
        "task_generation_slots_min": min((t for t in (_safe_int(r.get("arrival_time")) for r in task_rows) if t is not None), default=None),
        "task_generation_slots_max": max((t for t in (_safe_int(r.get("arrival_time")) for r in task_rows) if t is not None), default=None),
        "task_generation_during_drain_count": task_generation_during_drain_count,
        "decision_rows_during_drain_count": decision_rows_during_drain_count,
        "queue_rows_during_drain_count": queue_rows_during_drain_count,
        "completions_during_drain_count": completions_during_drain_count,
        "drops_during_drain_count": drops_during_drain_count,
        "horizon_contract_passed": horizon_contract_passed,
        "paper_claims_made": False,
    }
    return report


def validate_run_horizon_trace(trace_dir: str | Path) -> dict[str, Any]:
    report = build_run_horizon_report(trace_dir)
    if not report["horizon_contract_passed"]:
        raise ValueError("paper run horizon contract failed")
    return report
