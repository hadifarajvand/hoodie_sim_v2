from __future__ import annotations

import json
import sys
from pathlib import Path

repo_path = str(Path(__file__).resolve().parents[2])
if repo_path not in sys.path:
    sys.path.insert(0, repo_path)

from src.analysis.task_arrival_completion_timing_audit import (
    run_task_arrival_completion_timing_audit,
    write_artifacts,
)


class TestTaskArrivalCompletionTimingAudit:
    @classmethod
    def setup_class(cls) -> None:
        cls.report = run_task_arrival_completion_timing_audit()
        cls.json_path, cls.md_path = write_artifacts(cls.report)

    def test_diagnostic_type(self) -> None:
        assert self.report["diagnostic_type"] == "task_arrival_completion_timing_audit"

    def test_bounded_constraint_format(self) -> None:
        assert "episodes x" in self.report["bounded_constraint"]
        assert "slots" in self.report["bounded_constraint"]

    def test_config_is_paper_default(self) -> None:
        cfg = self.report["config_summary"]
        assert cfg["state_dim"] == 74
        assert cfg["action_count"] == 22
        assert cfg["full_campaign_enabled"] is False

    def test_observability_matrix_exists(self) -> None:
        obs = self.report["observability_matrix"]
        assert "first_arrival_slot" in obs
        assert "first_service_start_slot" in obs
        assert "first_completion_slot" in obs
        assert "first_drop_slot" in obs
        assert "action_distribution" in obs
        assert "queue_lengths" in obs
        assert "reward_events" in obs

    def test_first_arrival_slot_observable(self) -> None:
        obs = self.report["observability_matrix"]["first_arrival_slot"]
        assert obs["observable"] is True

    def test_first_service_start_slot_not_observable(self) -> None:
        obs = self.report["observability_matrix"]["first_service_start_slot"]
        assert obs["observable"] is False

    def test_queue_lengths_not_observable(self) -> None:
        obs = self.report["observability_matrix"]["queue_lengths"]
        assert obs["observable"] is False

    def test_metrics_present(self) -> None:
        m = self.report["metrics"]
        assert m["episodes_completed"] > 0
        assert m["episode_length"] == 200
        assert m["total_transition_count"] > 0
        assert "completed_task_count" in m
        assert "dropped_task_count" in m
        assert "pending_at_horizon_count" in m

    def test_inferred_findings_present(self) -> None:
        findings = self.report["inferred_findings"]
        assert "what_is_proven" in findings
        assert "what_is_not_observable" in findings
        assert "most_likely_next_hypothesis" in findings

    def test_verdict_valid(self) -> None:
        assert self.report["verdict"] in (
            "audit_explains_zero_completion",
            "audit_needs_deeper_instrumentation",
            "audit_failed",
        )

    def test_recommended_next_step_present(self) -> None:
        assert self.report["recommended_next_step"] in (
            "bounded horizon extension plan",
            "minimal trainer instrumentation plan",
            "minimal repair plan",
            "explicit full-campaign approval gate",
        )

    def test_json_artifact_written(self) -> None:
        assert self.json_path.exists()
        assert self.json_path.stat().st_size > 0
        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        assert data["diagnostic_type"] == "task_arrival_completion_timing_audit"
        assert "observability_matrix" in data

    def test_md_artifact_written(self) -> None:
        assert self.md_path.exists()
        assert self.md_path.stat().st_size > 0
        content = self.md_path.read_text(encoding="utf-8")
        assert "# Task-Arrival Completion Timing Audit Evidence" in content
        assert "## Observability Matrix" in content