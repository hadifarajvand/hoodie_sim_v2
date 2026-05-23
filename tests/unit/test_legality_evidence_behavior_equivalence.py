from __future__ import annotations

import unittest

from src.analysis.legality_evidence_expansion.runner import LegalityEvidenceConfig, _behavior_equivalence_checks, _run_episode


class LegalityEvidenceBehaviorEquivalenceUnitTests(unittest.TestCase):
    def test_behavior_equivalence_same_actions(self) -> None:
        config = LegalityEvidenceConfig()
        baseline = _run_episode(config, "environment_default_policy_probe", 0, trace_enabled=False)
        capture = _run_episode(config, "environment_default_policy_probe", 0, trace_enabled=True)
        checks = _behavior_equivalence_checks(baseline, capture)
        self.assertTrue(next(check.verified for check in checks if check.name == "same_action_sequence"))

    def test_behavior_equivalence_same_rewards(self) -> None:
        config = LegalityEvidenceConfig()
        baseline = _run_episode(config, "force_local_legal_probe", 1, trace_enabled=False)
        capture = _run_episode(config, "force_local_legal_probe", 1, trace_enabled=True)
        checks = _behavior_equivalence_checks(baseline, capture)
        self.assertTrue(next(check.verified for check in checks if check.name == "same_rewards"))

    def test_behavior_equivalence_same_terminal_outcomes(self) -> None:
        config = LegalityEvidenceConfig()
        baseline = _run_episode(config, "force_horizontal_legal_probe", 2, trace_enabled=False)
        capture = _run_episode(config, "force_horizontal_legal_probe", 2, trace_enabled=True)
        checks = _behavior_equivalence_checks(baseline, capture)
        self.assertTrue(next(check.verified for check in checks if check.name == "same_terminal_outcomes"))

    def test_behavior_equivalence_same_queue_progression(self) -> None:
        config = LegalityEvidenceConfig()
        baseline = _run_episode(config, "mixed_legal_round_robin_probe", 0, trace_enabled=False)
        capture = _run_episode(config, "mixed_legal_round_robin_probe", 0, trace_enabled=True)
        checks = _behavior_equivalence_checks(baseline, capture)
        self.assertTrue(next(check.verified for check in checks if check.name == "same_queue_progression"))


if __name__ == "__main__":
    unittest.main()
