from __future__ import annotations

import unittest

from src.analysis.evaluation_instrumentation_reward_state_diagnostic.model import ClaimSafetyStatus, DiagnosticDecision


class EvaluationInstrumentationRewardStateDiagnosticClaimSafetyTests(unittest.TestCase):
    def test_claim_safety_pass_blocks_unsupported_claims(self) -> None:
        with self.assertRaises(ValueError):
            ClaimSafetyStatus(
                paper_reproduction_claim_made=True,
                performance_superiority_claim_made=False,
                baseline_superiority_claim_made=False,
                claim_safety_passed=True,
            )

    def test_diagnostic_decision_rejects_unknown_choice(self) -> None:
        with self.assertRaises(ValueError):
            DiagnosticDecision(recommended_next_action="not_allowed", decision_reason="bad")


if __name__ == "__main__":
    unittest.main()
