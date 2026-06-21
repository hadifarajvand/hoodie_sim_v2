from __future__ import annotations

import pytest

from src.analysis.state_representation_deadline_queue_feasibility_repair.diagnostics import build_claim_safety_status, build_diagnostic_decision
from src.analysis.state_representation_deadline_queue_feasibility_repair.model import ClaimSafetyStatus, DiagnosticDecision


def test_claim_safety_blocks_superiority_claims() -> None:
    status = build_claim_safety_status()
    assert status["claim_safety_passed"] is True
    assert status["paper_reproduction_claim_made"] is False
    assert status["performance_superiority_claim_made"] is False
    assert status["baseline_superiority_claim_made"] is False

    decision = build_diagnostic_decision(
        state_dim_match=True,
        no_nan_or_inf=True,
        state_feature_coverage_complete=True,
        reward_reconciliation_passed=True,
        terminal_reconciliation_passed=True,
        completion_count_nonzero=True,
        fixed_policy_completion_present=True,
        action_collapse_reduced=True,
        selected_action_feasibility_improved=True,
        queue_feature_coverage_complete=True,
    )
    assert decision["recommended_next_action"] == "safe_to_proceed_to_reward_function_alignment"


def test_invalid_final_verdict_is_rejected() -> None:
    with pytest.raises(ValueError):
        DiagnosticDecision("fix_policy_exploration_next", "", [])

    claim = ClaimSafetyStatus(False, False, False, True)
    assert claim.to_dict()["claim_safety_passed"] is True

