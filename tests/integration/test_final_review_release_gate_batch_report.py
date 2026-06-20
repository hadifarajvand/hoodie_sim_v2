from __future__ import annotations

import json

from src.analysis.final_review_release_gate_batch.config import REPORT_JSON, REPORT_MD, FINAL_REVIEW_SUMMARY_MD


def test_report_artifacts_are_claim_safe_and_decision_complete() -> None:
    payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))

    assert payload["final_verdict"] == "final_review_release_gate_blocked"
    assert payload["recommended_next_action"] == "audit_reward_and_evaluation_design_before_more_training"
    assert payload["claim_safety_status"]["claim_safety_passed"] is True
    assert payload["claim_safety_status"]["paper_reproduction_claim_made"] is False
    assert payload["claim_safety_status"]["performance_superiority_claim_made"] is False
    assert payload["claim_safety_status"]["baseline_superiority_claim_made"] is False
    assert payload["training_rerun_from_scratch"] is False
    assert payload["training_5000_run"] is False
    assert set(payload["diagnostic_findings"]["questions"]) == {
        "q1_reward_static",
        "q2_action_drift",
        "q3_replay_cap",
        "q4_signal_sufficient",
        "q5_next_step",
    }
    assert "Final Review Summary" in FINAL_REVIEW_SUMMARY_MD.read_text(encoding="utf-8")
    assert "Final Review and Release Gate Batch Report" in REPORT_MD.read_text(encoding="utf-8")
