from __future__ import annotations

from pathlib import Path

from src.analysis.state_profile_decision_time_integration_recovery.report import write_state_representation_repair_outputs
from tests.unit.test_state_profile_decision_time_integration_recovery_schema import make_repair_payload


def test_report_writer_emits_expected_artifacts(tmp_path: Path) -> None:
    payload = make_repair_payload()
    report_json_path, report_md_path, summary_path = write_state_representation_repair_outputs(payload, output_dir=tmp_path)

    assert report_json_path.exists()
    assert report_md_path.exists()
    assert summary_path.exists()
    assert (tmp_path / "state-feature-coverage-audit.json").exists()
    assert (tmp_path / "state-normalization-audit.json").exists()
    assert (tmp_path / "legacy-vs-new-state-profile-comparison.json").exists()
    assert (tmp_path / "state-profile-50-100-comparison.json").exists()
    assert (tmp_path / "action-collapse-diagnostics.json").exists()
    assert (tmp_path / "selected-action-feasibility-diagnostics.json").exists()
    assert (tmp_path / "policy-effect-after-state-repair.json").exists()
    assert (tmp_path / "reconciliation-after-state-repair.json").exists()
    assert (tmp_path / "replay-state-alignment-audit.json").exists()
    assert (tmp_path / "diagnostic-decision.json").exists()
    assert (tmp_path / "figure-manifest.json").exists()
    assert "safe_to_proceed_to_reward_function_alignment" in report_md_path.read_text(encoding="utf-8")
