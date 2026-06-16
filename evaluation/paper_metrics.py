from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np

from environment.paper_horizon import PAPER_ACTION_SLOTS, PAPER_DRAIN_SLOTS, PAPER_TOTAL_SLOTS

REQUIRED_FILES = (
    "task_lifecycle.csv",
    "action_trace.csv",
    "episode_metrics.csv",
)

OPTIONAL_FILES = (
    "delayed_reward_event_trace.csv",
    "queue_trace.csv",
    "run_horizon_report.json",
    "run_horizon_trace.csv",
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _safe_float(value: Any) -> float | None:
    if value in (None, "", "None"):
        return None
    try:
        result = float(value)
    except Exception:
        return None
    if not np.isfinite(result):
        return None
    return float(result)


def _safe_int(value: Any) -> int | None:
    if value in (None, "", "None"):
        return None
    try:
        return int(float(value))
    except Exception:
        return None


def _safe_text(value: Any) -> str:
    if value in (None, "", "None"):
        return ""
    return str(value)


def _parse_bool(value: Any) -> bool | None:
    if value in (None, "", "None"):
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def _parse_json(value: Any, default: Any) -> Any:
    if value in (None, "", "None"):
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return default


def _mean_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    return float(mean(values))


def _percentile_or_none(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    return float(np.percentile(np.asarray(values, dtype=np.float64), percentile))


def _count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = _safe_text(row.get(key))
        if value == "":
            continue
        counts[value] = counts.get(value, 0) + 1
    return counts


def _action_slot(time_value: int | None) -> bool:
    return time_value is not None and 0 <= time_value < PAPER_ACTION_SLOTS


def _drain_slot(time_value: int | None) -> bool:
    return time_value is not None and PAPER_ACTION_SLOTS <= time_value < PAPER_TOTAL_SLOTS


def _missing_required_files(trace_dir: Path) -> list[str]:
    return [name for name in REQUIRED_FILES if not (trace_dir / name).exists()]


def _extract_counts(task_rows: list[dict[str, str]]) -> dict[str, int]:
    completed = 0
    dropped = 0
    pending = 0
    for row in task_rows:
        status = _safe_text(row.get("final_status")).strip().lower()
        if status == "completed":
            completed += 1
        elif status == "dropped":
            dropped += 1
        else:
            pending += 1
    total = len(task_rows)
    terminal = completed + dropped
    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "dropped_tasks": dropped,
        "pending_tasks": pending,
        "terminal_tasks": terminal,
    }


def _compute_latency_delay(task_rows: list[dict[str, str]], delayed_reward_rows: list[dict[str, str]]) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    completed_rows = [row for row in task_rows if _safe_text(row.get("final_status")).strip().lower() == "completed"]
    latencies = [_safe_float(row.get("latency")) for row in completed_rows]
    latencies = [value for value in latencies if value is not None]
    average_latency = _mean_or_none(latencies)
    delay_values = [_safe_float(row.get("delay")) for row in delayed_reward_rows]
    delay_values = [value for value in delay_values if value is not None]
    delay_source = "delayed_reward_event_trace" if delay_values else "task_lifecycle_latency_fallback"
    if not delay_values:
        delay_values = latencies.copy()
        if not delayed_reward_rows:
            warnings.append("delayed_reward_event_trace missing; delay falls back to task_lifecycle latency")
        elif not delay_values:
            warnings.append("delayed_reward_event_trace present but no finite delay values; delay falls back to task_lifecycle latency")
    average_delay = _mean_or_none(delay_values)
    waiting_values = [_safe_float(row.get("waiting_time")) for row in completed_rows]
    waiting_values = [value for value in waiting_values if value is not None]
    service_values = [_safe_float(row.get("service_time")) for row in completed_rows]
    service_values = [value for value in service_values if value is not None]
    return {
        "average_latency": average_latency,
        "p50_latency": _percentile_or_none(latencies, 50.0),
        "p95_latency": _percentile_or_none(latencies, 95.0),
        "max_latency": max(latencies) if latencies else None,
        "average_delay": average_delay,
        "p50_delay": _percentile_or_none(delay_values, 50.0),
        "p95_delay": _percentile_or_none(delay_values, 95.0),
        "max_delay": max(delay_values) if delay_values else None,
        "delay_source": delay_source,
        "average_waiting_time": _mean_or_none(waiting_values),
        "p95_waiting_time": _percentile_or_none(waiting_values, 95.0),
        "average_service_time": _mean_or_none(service_values),
        "p95_service_time": _percentile_or_none(service_values, 95.0),
    }, warnings


def _compute_reward(delayed_reward_rows: list[dict[str, str]]) -> dict[str, Any]:
    rewards = [_safe_float(row.get("reward")) for row in delayed_reward_rows]
    rewards = [value for value in rewards if value is not None]
    if rewards:
        return {
            "reward_count": len(rewards),
            "reward_sum": float(sum(rewards)),
            "reward_mean": float(mean(rewards)),
            "reward_min": float(min(rewards)),
            "reward_max": float(max(rewards)),
            "reward_source": "delayed_reward_event_trace",
        }
    return {
        "reward_count": 0,
        "reward_sum": 0.0,
        "reward_mean": None,
        "reward_min": None,
        "reward_max": None,
        "reward_source": "unavailable",
    }


def _compute_actions(action_rows: list[dict[str, str]]) -> dict[str, Any]:
    selected_action_counts: dict[str, int] = {}
    first_stage_decision_counts: dict[str, int] = {}
    destination_type_counts: dict[str, int] = {}
    destination_node_counts: dict[str, int] = {}
    invalid_action_count = 0
    valid_action_count = 0
    action_rows_during_drain_count = 0
    normal_selected_actions_during_drain_count = 0
    for row in action_rows:
        selected_action = _safe_text(row.get("selected_action"))
        if selected_action != "":
            selected_action_counts[selected_action] = selected_action_counts.get(selected_action, 0) + 1
        first_stage_decision = _safe_text(row.get("first_stage_decision"))
        if first_stage_decision != "":
            first_stage_decision_counts[first_stage_decision] = first_stage_decision_counts.get(first_stage_decision, 0) + 1
        destination_type = _safe_text(row.get("destination_type"))
        if destination_type != "":
            destination_type_counts[destination_type] = destination_type_counts.get(destination_type, 0) + 1
        destination_node = _safe_text(row.get("destination_node_id"))
        if destination_node != "":
            destination_node_counts[destination_node] = destination_node_counts.get(destination_node, 0) + 1
        time_value = _safe_int(row.get("time"))
        if _drain_slot(time_value):
            action_rows_during_drain_count += 1
            if selected_action != "":
                normal_selected_actions_during_drain_count += 1
        is_valid = _parse_bool(row.get("is_valid"))
        if is_valid is False:
            invalid_action_count += 1
        else:
            valid_action_count += 1
    return {
        "action_rows": len(action_rows),
        "selected_action_counts": selected_action_counts,
        "first_stage_decision_counts": first_stage_decision_counts,
        "destination_type_counts": destination_type_counts,
        "destination_node_counts": destination_node_counts,
        "invalid_action_count": invalid_action_count,
        "valid_action_count": valid_action_count,
        "action_rows_during_drain_count": action_rows_during_drain_count,
        "normal_selected_actions_during_drain_count": normal_selected_actions_during_drain_count,
    }


def _compute_public_queue_throw(task_rows: list[dict[str, str]], queue_rows: list[dict[str, str]]) -> dict[str, Any]:
    public_queue_throw_bits = 0.0
    public_queue_throw_events = 0
    paper_m_pub_present = False
    for row in task_rows:
        value = _safe_float(row.get("paper_m_pub"))
        if value is None:
            continue
        paper_m_pub_present = True
        if value > 0:
            public_queue_throw_events += 1
        public_queue_throw_bits += value
    if not paper_m_pub_present:
        for row in queue_rows:
            value = _safe_float(row.get("paper_m_pub"))
            if value is None:
                continue
            paper_m_pub_present = True
            if value > 0:
                public_queue_throw_events += 1
            public_queue_throw_bits += value
    return {
        "throw_count_proxy": 0,  # filled later
        "throw_ratio_proxy": 0.0,  # filled later
        "timeout_drop_count": 0,
        "timeout_drop_ratio": 0.0,
        "public_queue_throw_bits": float(public_queue_throw_bits),
        "public_queue_throw_events": public_queue_throw_events,
    }


def _compute_horizon(trace_dir: Path) -> tuple[dict[str, Any], list[str]]:
    horizon_report_path = trace_dir / "run_horizon_report.json"
    if not horizon_report_path.exists():
        return {
            "paper_action_slots": None,
            "paper_drain_slots": None,
            "paper_total_slots": None,
            "observed_action_slots": None,
            "observed_drain_slots": None,
            "observed_total_slots": None,
            "horizon_contract_passed": None,
            "task_generation_during_drain_count": None,
            "decision_rows_during_drain_count": None,
            "queue_rows_during_drain_count": None,
            "completions_during_drain_count": None,
            "drops_during_drain_count": None,
        }, ["run_horizon_report.json missing; horizon-aware metrics degraded"]
    try:
        report = json.loads(horizon_report_path.read_text())
    except Exception as exc:
        raise ValueError(f"invalid run_horizon_report.json: {exc}") from exc
    return {
        "paper_action_slots": report.get("paper_action_slots"),
        "paper_drain_slots": report.get("paper_drain_slots"),
        "paper_total_slots": report.get("paper_total_slots"),
        "observed_action_slots": report.get("observed_action_slots"),
        "observed_drain_slots": report.get("observed_drain_slots"),
        "observed_total_slots": report.get("observed_total_slots"),
        "horizon_contract_passed": report.get("horizon_contract_passed"),
        "task_generation_during_drain_count": report.get("task_generation_during_drain_count"),
        "decision_rows_during_drain_count": report.get("decision_rows_during_drain_count"),
        "queue_rows_during_drain_count": report.get("queue_rows_during_drain_count"),
        "completions_during_drain_count": report.get("completions_during_drain_count"),
        "drops_during_drain_count": report.get("drops_during_drain_count"),
    }, []


def _cross_check_episode_metrics(task_counts: dict[str, int], trace_dir: Path) -> tuple[dict[str, Any], list[str]]:
    episode_rows = _read_csv(trace_dir / "episode_metrics.csv")
    if not episode_rows:
        return {
            "present": False,
            "cross_check_passed": False,
            "severe_mismatch": False,
            "differences": {},
            "episode_metrics_total_tasks": None,
            "episode_metrics_completed_tasks": None,
            "episode_metrics_dropped_tasks": None,
            "episode_metrics_pending_tasks": None,
            "episode_metrics_drop_ratio": None,
        }, ["episode_metrics.csv missing; cross-check unavailable"]
    def _sum(key: str) -> int:
        return sum(_safe_int(row.get(key)) or 0 for row in episode_rows)
    total_tasks = _sum("total_tasks")
    completed_tasks = _sum("completed_tasks")
    dropped_tasks = _sum("dropped_tasks")
    pending_tasks = _sum("pending_tasks")
    drop_ratios = [_safe_float(row.get("drop_ratio")) for row in episode_rows]
    drop_ratios = [value for value in drop_ratios if value is not None]
    aggregated_drop_ratio = float(sum(dropped_tasks for _ in [0]) / total_tasks) if total_tasks else 0.0
    differences = {
        "total_tasks": total_tasks - task_counts["total_tasks"],
        "completed_tasks": completed_tasks - task_counts["completed_tasks"],
        "dropped_tasks": dropped_tasks - task_counts["dropped_tasks"],
        "pending_tasks": pending_tasks - task_counts["pending_tasks"],
        "drop_ratio": (float(sum(drop_ratios) / len(drop_ratios)) if drop_ratios else None) - float(task_counts["dropped_tasks"] / task_counts["total_tasks"]) if task_counts["total_tasks"] else 0.0,
    }
    cross_check_passed = all(
        abs(value) < 1e-9 if isinstance(value, float) else value == 0
        for value in differences.values()
        if value is not None
    )
    severe_mismatch = any(abs(value) > 1e-9 for key, value in differences.items() if value is not None and key == "drop_ratio") or any(
        value != 0 for key, value in differences.items() if key != "drop_ratio" and value is not None
    )
    return {
        "present": True,
        "cross_check_passed": cross_check_passed,
        "severe_mismatch": severe_mismatch,
        "differences": differences,
        "episode_metrics_total_tasks": total_tasks,
        "episode_metrics_completed_tasks": completed_tasks,
        "episode_metrics_dropped_tasks": dropped_tasks,
        "episode_metrics_pending_tasks": pending_tasks,
        "episode_metrics_drop_ratio": float(sum(drop_ratios) / len(drop_ratios)) if drop_ratios else None,
        "episode_metrics_drop_ratio_aggregated": aggregated_drop_ratio,
    }, []


def compute_paper_facing_metrics(trace_dir: str | Path) -> dict[str, Any]:
    trace_dir = Path(trace_dir)
    missing_required = _missing_required_files(trace_dir)
    if missing_required:
        raise ValueError(f"missing required trace files: {missing_required}")

    task_rows = _read_csv(trace_dir / "task_lifecycle.csv")
    action_rows = _read_csv(trace_dir / "action_trace.csv")
    episode_rows = _read_csv(trace_dir / "episode_metrics.csv")
    delayed_reward_rows = _read_csv(trace_dir / "delayed_reward_event_trace.csv")
    queue_rows = _read_csv(trace_dir / "queue_trace.csv")

    warnings: list[str] = []
    counts = _extract_counts(task_rows)
    counts["terminal_tasks"] = counts["completed_tasks"] + counts["dropped_tasks"]
    ratios = {
        "completion_ratio": float(counts["completed_tasks"] / counts["total_tasks"]) if counts["total_tasks"] else 0.0,
        "drop_ratio": float(counts["dropped_tasks"] / counts["total_tasks"]) if counts["total_tasks"] else 0.0,
        "pending_ratio": float(counts["pending_tasks"] / counts["total_tasks"]) if counts["total_tasks"] else 0.0,
        "terminal_drop_ratio": float(counts["dropped_tasks"] / counts["terminal_tasks"]) if counts["terminal_tasks"] else 0.0,
    }

    timeout_drop_count = 0
    for row in task_rows:
        if _safe_text(row.get("final_status")).strip().lower() != "dropped":
            continue
        drop_reason = _safe_text(row.get("drop_reason")).lower()
        if "timeout" in drop_reason:
            timeout_drop_count += 1
    throw_metrics = _compute_public_queue_throw(task_rows, queue_rows)
    throw_metrics["throw_count_proxy"] = counts["dropped_tasks"]
    throw_metrics["throw_ratio_proxy"] = ratios["drop_ratio"]
    throw_metrics["timeout_drop_count"] = timeout_drop_count
    throw_metrics["timeout_drop_ratio"] = float(timeout_drop_count / counts["total_tasks"]) if counts["total_tasks"] else 0.0
    if not any(_safe_float(row.get("paper_m_pub")) is not None for row in task_rows + queue_rows):
        warnings.append(
            "throw_ratio_proxy uses dropped task count because exact paper throw semantics are only available when paper_m_pub/public queue traces are present."
        )

    latency_delay, latency_warnings = _compute_latency_delay(task_rows, delayed_reward_rows)
    warnings.extend(latency_warnings)
    reward = _compute_reward(delayed_reward_rows)
    if reward["reward_source"] == "unavailable":
        warnings.append("delayed_reward_event_trace unavailable; reward summary degraded")

    actions = _compute_actions(action_rows)
    horizon, horizon_warnings = _compute_horizon(trace_dir)
    warnings.extend(horizon_warnings)

    episode_cross_check, episode_warnings = _cross_check_episode_metrics(counts, trace_dir)
    warnings.extend(episode_warnings)

    validation_errors = validate_paper_facing_metrics_report(
        {
            "paper_claims_made": False,
            "official_reproduction_claimed": False,
            "counts": counts,
            "ratios": ratios,
            "horizon": horizon,
            "actions": actions,
            "episode_metrics_cross_check": episode_cross_check,
            "public_queue_throw": throw_metrics,
            "status": "passed",
            "validation_errors": [],
        }
    )
    status = "passed"
    if warnings:
        status = "degraded"
    if validation_errors:
        status = "failed"

    metric_definitions = {
        "count_metrics": {
            "total_tasks": "number of rows in task_lifecycle.csv",
            "completed_tasks": "count where final_status == completed",
            "dropped_tasks": "count where final_status == dropped",
            "pending_tasks": "count where final_status is neither completed nor dropped",
            "terminal_tasks": "completed_tasks + dropped_tasks",
        },
        "ratio_metrics": {
            "completion_ratio": "completed_tasks / total_tasks",
            "drop_ratio": "dropped_tasks / total_tasks",
            "pending_ratio": "pending_tasks / total_tasks",
            "terminal_drop_ratio": "dropped_tasks / terminal_tasks",
        },
        "throw_proxy": {
            "throw_count_proxy": "dropped_tasks",
            "throw_ratio_proxy": "drop_ratio",
            "timeout_drop_count": "dropped rows whose drop_reason contains timeout",
            "timeout_drop_ratio": "timeout_drop_count / total_tasks",
            "public_queue_throw_bits": "sum of paper_m_pub across available task_lifecycle/queue_trace rows",
            "public_queue_throw_events": "count rows where paper_m_pub > 0",
            "note": "throw_ratio_proxy uses dropped task count because exact paper throw semantics are only available when paper_m_pub/public queue traces are present.",
        },
        "latency_delay": {
            "average_latency": "mean of finite completed-task latency values",
            "average_delay": "mean delay values from delayed_reward_event_trace when available, else latency fallback",
        },
        "reward": {
            "reward_source": "delayed_reward_event_trace when available, otherwise unavailable",
        },
        "horizon": {
            "paper_action_slots": PAPER_ACTION_SLOTS,
            "paper_drain_slots": PAPER_DRAIN_SLOTS,
            "paper_total_slots": PAPER_TOTAL_SLOTS,
        },
    }

    report = {
        "model": "Model 14 — Paper-Facing Evaluation Metrics Contract",
        "status": status,
        "paper_claims_made": False,
        "official_reproduction_claimed": False,
        "trace_dir": str(trace_dir),
        "metric_definitions": metric_definitions,
        "warnings": sorted(set(warnings)),
        "counts": counts,
        "ratios": ratios,
        "latency_delay": latency_delay,
        "waiting_service": {
            "average_waiting_time": latency_delay["average_waiting_time"],
            "p95_waiting_time": latency_delay["p95_waiting_time"],
            "average_service_time": latency_delay["average_service_time"],
            "p95_service_time": latency_delay["p95_service_time"],
        },
        "reward": reward,
        "actions": actions,
        "horizon": horizon,
        "public_queue_throw": throw_metrics,
        "episode_metrics_cross_check": episode_cross_check,
        "validation_errors": validation_errors,
    }
    return report


def validate_paper_facing_metrics_report(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("paper_claims_made") is not False:
        errors.append("paper_claims_made must be False")
    if report.get("official_reproduction_claimed") is not False:
        errors.append("official_reproduction_claimed must be False")
    counts = report.get("counts") or {}
    ratios = report.get("ratios") or {}
    total_tasks = counts.get("total_tasks")
    completed_tasks = counts.get("completed_tasks", 0)
    dropped_tasks = counts.get("dropped_tasks", 0)
    pending_tasks = counts.get("pending_tasks", 0)
    terminal_tasks = counts.get("terminal_tasks", completed_tasks + dropped_tasks)
    if total_tasks is not None and total_tasks < 0:
        errors.append("total_tasks must be non-negative")
    if total_tasks is not None and completed_tasks + dropped_tasks + pending_tasks != total_tasks:
        errors.append("completed + dropped + pending must equal total_tasks")
    for key, value in ratios.items():
        if value is None:
            continue
        if not (0.0 <= float(value) <= 1.0):
            errors.append(f"{key} must be within [0, 1]")
    public_queue_throw = report.get("public_queue_throw") or {}
    throw_ratio_proxy = public_queue_throw.get("throw_ratio_proxy")
    drop_ratio = ratios.get("drop_ratio")
    if throw_ratio_proxy is not None and drop_ratio is not None and abs(float(throw_ratio_proxy) - float(drop_ratio)) > 1e-9:
        errors.append("throw_ratio_proxy must match drop_ratio")
    horizon = report.get("horizon") or {}
    if horizon.get("horizon_contract_passed") is False:
        errors.append("horizon_contract_passed is False")
    actions = report.get("actions") or {}
    if int(actions.get("normal_selected_actions_during_drain_count", 0)) > 0:
        errors.append("normal_selected_actions_during_drain_count must be zero")
    episode_cross_check = report.get("episode_metrics_cross_check") or {}
    if episode_cross_check.get("severe_mismatch"):
        errors.append("episode_metrics cross-check mismatch is severe")
    if terminal_tasks is not None and terminal_tasks < 0:
        errors.append("terminal_tasks must be non-negative")
    return errors


def write_paper_facing_metrics_report(trace_dir: str | Path, output_path: str | Path | None = None) -> dict[str, Any]:
    trace_dir = Path(trace_dir)
    report = compute_paper_facing_metrics(trace_dir)
    validation_errors = validate_paper_facing_metrics_report(report)
    report["validation_errors"] = validation_errors
    if validation_errors:
        report["status"] = "failed"
    elif report.get("warnings"):
        report["status"] = "degraded"
    else:
        report["status"] = "passed"
    destination = Path(output_path) if output_path is not None else trace_dir / "paper_facing_metrics_report.json"
    destination.write_text(json.dumps(report, indent=2, sort_keys=True))
    return report
