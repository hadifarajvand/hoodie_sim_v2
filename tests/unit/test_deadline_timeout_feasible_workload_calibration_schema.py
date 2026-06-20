from __future__ import annotations

from src.analysis.deadline_timeout_feasible_workload_calibration.calibration import build_calibration_change_log
from src.analysis.deadline_timeout_feasible_workload_calibration.config import DeadlineTimeoutCalibrationConfig


def test_calibration_config_uses_required_lightweight_budget():
    config = DeadlineTimeoutCalibrationConfig()

    assert config.training_budgets == (50, 100)
    assert config.max_training_budget == 100
    assert config.evaluation_episode_count == 100
    assert config.evaluation_episode_count_per_checkpoint == 100
    assert config.episode_length == 110
    assert config.training_5000_run is False
    assert config.calibration_profile_name == "paper_aligned_feasible_v1"


def test_calibration_change_log_is_explicit_and_named():
    entries = build_calibration_change_log()

    assert entries
    assert all({"field_name", "before_value", "after_value", "reason", "paper_alignment_note"} <= set(entry) for entry in entries)
    assert any(entry["field_name"] == "task_size_mbits" for entry in entries)
    assert any(entry["field_name"] == "timeout_length" for entry in entries)
