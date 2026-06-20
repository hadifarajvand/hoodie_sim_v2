from __future__ import annotations

import pytest

from src.analysis.final_review_release_gate_batch.model import ClaimSafetyStatus, FinalReviewReleaseGateBatchReport
from src.analysis.final_review_release_gate_batch.runner import build_final_review_release_gate_batch_report


def test_gate_report_keeps_claims_within_descriptive_bounds() -> None:
    report = build_final_review_release_gate_batch_report().to_dict()
    assert report["claim_safety_status"]["claim_safety_passed"] is True
    assert report["claim_safety_status"]["paper_reproduction_claim_made"] is False
    assert report["claim_safety_status"]["performance_superiority_claim_made"] is False
    assert report["claim_safety_status"]["baseline_superiority_claim_made"] is False
    assert report["final_verdict"] == "final_review_release_gate_blocked"
    assert report["recommended_next_action"] != "release_ready_for_thesis_drafting"


def test_unsupported_claims_cannot_pass_safety_validation() -> None:
    with pytest.raises(ValueError):
        ClaimSafetyStatus(
            paper_reproduction_claim_made=True,
            performance_superiority_claim_made=False,
            baseline_superiority_claim_made=False,
            claim_safety_passed=True,
        )


def test_ready_verdict_rejects_unsupported_claims() -> None:
    base = build_final_review_release_gate_batch_report().to_dict()
    bad_claims = dict(base["claim_safety_status"])
    bad_claims["paper_reproduction_claim_made"] = True
    with pytest.raises(ValueError):
        FinalReviewReleaseGateBatchReport(
            **{
                **base,
                "claim_safety_status": bad_claims,
                "final_verdict": "final_review_release_gate_ready",
                "remaining_blockers": [],
                "recommended_next_action": "release_ready_for_thesis_drafting",
            }
        )
