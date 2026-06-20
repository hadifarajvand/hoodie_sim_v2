from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from src.analysis.deadline_timeout_feasible_workload_calibration.config import DeadlineTimeoutCalibrationConfig
from src.analysis.deadline_timeout_feasible_workload_calibration import runner as feature_069_runner

from .config import CALIBRATION_PROFILE_NAME, RECORD_SAMPLE_LIMIT


def load_feature_069_compact_report(path: Path) -> dict[str, Any]:
    import json

    return json.loads(path.read_text(encoding="utf-8"))


@contextmanager
def _raw_payload_patch() -> Iterator[None]:
    original_compact = feature_069_runner.compact_deadline_timeout_calibration_payload
    original_generate_figures = feature_069_runner.generate_figures
    feature_069_runner.compact_deadline_timeout_calibration_payload = lambda report: report
    feature_069_runner.generate_figures = lambda payload, figures_dir: []
    try:
        yield
    finally:
        feature_069_runner.compact_deadline_timeout_calibration_payload = original_compact
        feature_069_runner.generate_figures = original_generate_figures


def load_feature_069_raw_report(config: Any | None = None) -> dict[str, Any]:
    for cached_path in (
        Path("/tmp/hoodie_feature069_delivery93/report_payload.json"),
        Path("/private/tmp/hoodie_feature069_delivery93/report_payload.json"),
    ):
        if cached_path.exists():
            return load_feature_069_compact_report(cached_path)
    calibration_config = config or DeadlineTimeoutCalibrationConfig()
    with _raw_payload_patch():
        return feature_069_runner.build_deadline_timeout_feasible_workload_calibration_report(calibration_config)


def build_metric_universe_definitions() -> dict[str, Any]:
    return {
        "u_full_decisions": {
            "name": "U_full_decisions",
            "description": "All evaluation decisions / slots / tasks in the full evaluation probe.",
            "members": ["decision_count", "evaluation_action_distribution", "evaluation_decision_count"],
            "count_source": "evaluation_decision_count",
        },
        "u_unique_tasks": {
            "name": "U_unique_tasks",
            "description": "Unique task identities by (trace_id, episode_id, task_id).",
            "members": ["unique_task_count", "task_records"],
            "count_source": "len(task_records)",
        },
        "u_selected_action_tasks": {
            "name": "U_selected_action_tasks",
            "description": "Tasks grouped by the action actually selected by the evaluated policy.",
            "members": ["selected_action_feasible_task_count", "selected_action_infeasible_task_count"],
            "count_source": "selected_action_feasible_task_count + selected_action_infeasible_task_count",
        },
        "u_hypothetical_action_feasibility": {
            "name": "U_hypothetical_action_feasibility",
            "description": "For each unique task, feasibility if action were local / horizontal / vertical.",
            "members": ["hypothetical_local_feasible_task_count", "hypothetical_horizontal_feasible_task_count", "hypothetical_vertical_feasible_task_count"],
            "count_source": "per-action hypothetical feasibility over unique tasks",
        },
        "u_reward_events": {
            "name": "U_reward_events",
            "description": "Actual reward-bearing events emitted by evaluation, with missing reward events recovered from terminal task evidence.",
            "members": ["reward_event_count", "raw_event_reward_total", "canonical_task_reward_total"],
            "count_source": "reward_event_count",
        },
        "u_terminal_events": {
            "name": "U_terminal_events",
            "description": "Actual terminal outcome events emitted by evaluation, with duplicate lifecycle-only events excluded from terminal task counts.",
            "members": ["terminal_task_count", "raw_terminal_event_count", "terminal_event_coverage_ratio"],
            "count_source": "terminal_task_count",
        },
        "feasible_task_count_definition": {
            "name": "feasible_task_count",
            "universe": "U_selected_action_tasks",
            "definition": "selected_action_feasible_task_count",
        },
        "completed_feasible_task_count_definition": {
            "name": "completed_feasible_task_count",
            "universe": "U_selected_action_tasks",
            "definition": "completed_selected_action_feasible_count",
        },
        "reward_event_count_definition": {
            "name": "reward_event_count",
            "universe": "U_reward_events",
            "definition": "recovered raw reward-bearing events after reconciliation repair",
        },
        "terminal_event_count_definition": {
            "name": "terminal_event_count",
            "universe": "U_terminal_events",
            "definition": "canonical terminal outcome events after deduplication",
        },
        "calibration_profile_name": CALIBRATION_PROFILE_NAME,
        "record_sample_limit": RECORD_SAMPLE_LIMIT,
    }
