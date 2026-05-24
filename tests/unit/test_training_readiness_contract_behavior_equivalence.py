from __future__ import annotations

import unittest

from src.analysis.training_readiness_contract import BehaviorEquivalenceSummary, build_training_readiness_contract_report


class TrainingReadinessContractBehaviorEquivalenceTests(unittest.TestCase):
    def test_behavior_equivalence_checks_unique_and_passed(self) -> None:
        payload = build_training_readiness_contract_report().to_dict()
        checks = payload["behavior_equivalence_summary"]["checks"]
        names = [check["name"] for check in checks]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(payload["behavior_equivalence_passed"], payload["behavior_equivalence_summary"]["passed"])
        self.assertTrue(payload["behavior_equivalence_passed"])

    def test_duplicate_check_names_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            BehaviorEquivalenceSummary(
                checks=[
                    {"name": "same_rewards", "verified": True, "details": "first"},
                    {"name": "same_rewards", "verified": True, "details": "duplicate"},
                ],
                passed=True,
            )


if __name__ == "__main__":
    unittest.main()
