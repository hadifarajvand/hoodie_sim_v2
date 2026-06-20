from __future__ import annotations

import unittest

from src.analysis.terminal_lifecycle_accounting_50_100_comparison.diagnostics import build_claim_safety_status
from src.analysis.terminal_lifecycle_accounting_50_100_comparison.model import ClaimSafetyStatus


class TerminalLifecycleAccounting50_100ComparisonClaimSafetyTests(unittest.TestCase):
    def test_claim_safety_pass_rejects_unsupported_claims(self) -> None:
        with self.assertRaises(ValueError):
            ClaimSafetyStatus(
                paper_reproduction_claim_made=True,
                performance_superiority_claim_made=False,
                baseline_superiority_claim_made=False,
                claim_safety_passed=True,
            )

    def test_claim_safety_status_reports_false_claims(self) -> None:
        status = build_claim_safety_status()
        self.assertTrue(status["claim_safety_passed"])
        self.assertFalse(status["paper_reproduction_claim_made"])
        self.assertFalse(status["performance_superiority_claim_made"])
        self.assertFalse(status["baseline_superiority_claim_made"])


if __name__ == "__main__":
    unittest.main()
