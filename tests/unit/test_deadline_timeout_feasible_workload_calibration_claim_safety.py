from __future__ import annotations

from src.analysis.deadline_timeout_feasible_workload_calibration.diagnostics import build_claim_safety_status


def test_claim_safety_blocks_superiority_and_reproduction_claims():
    status = build_claim_safety_status()

    assert status["claim_safety_passed"] is True
    assert status["paper_reproduction_claim_made"] is False
    assert status["performance_superiority_claim_made"] is False
    assert status["baseline_superiority_claim_made"] is False
