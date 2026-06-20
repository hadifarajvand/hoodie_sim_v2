from __future__ import annotations

from pathlib import Path
import tempfile

from src.analysis.completion_path_deadline_feasibility_repair.feasibility import build_task_feasibility_summary
from src.analysis.deadline_timeout_feasible_workload_calibration.calibration import build_calibration_profile, ensure_calibrated_trace_bank
from src.environment.trace_source import TraceSource


def _build_task_records(trace: dict) -> dict[str, dict]:
    records: dict[str, dict] = {}
    for task in trace["tasks"]:
        records[f"{trace['trace_id']}:0:{task['task_id']}"] = {
            "trace_id": trace["trace_id"],
            "episode_id": 0,
            "task_id": task["task_id"],
            "selected_action": "horizontal",
            "arrival_slot": task["arrival_slot"],
            "absolute_deadline_slot": task["absolute_deadline_slot"],
            "timeout_length": task["timeout_length"],
            "task_size": task["size"],
            "processing_density": task["processing_density"],
            "queue_load": 0,
        }
    return records


def test_calibrated_trace_bank_has_nontrivial_feasibility():
    profile = build_calibration_profile(Path(tempfile.gettempdir()) / "deadline-timeout-feasible-workload-calibration-test")
    ensure_calibrated_trace_bank(profile, 43)
    trace = TraceSource.from_trace_bank(f"{profile.profile_name}-43", root_path=profile.trace_root).load()
    summary = build_task_feasibility_summary(_build_task_records(trace), record_sample_limit=5)

    overall_feasible_ratio = (summary["total_task_count"] - summary["all_actions_infeasible_task_count"]) / summary["total_task_count"]

    assert summary["total_task_count"] > 0
    assert overall_feasible_ratio >= 0.20
    assert summary["local_feasible_task_count"] > 0
    assert summary["horizontal_feasible_task_count"] > 0
    assert summary["vertical_feasible_task_count"] > 0
    assert summary["all_actions_infeasible_task_count"] < summary["total_task_count"]
