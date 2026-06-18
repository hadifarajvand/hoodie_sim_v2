from __future__ import annotations

import unittest

from src.analysis.real_torch_trainer_binding_audit import build_real_torch_trainer_binding_audit_report


class RealTorchTrainerBindingAuditBehaviorEquivalenceTests(unittest.TestCase):
    def test_behavior_equivalence_check_names_are_unique(self) -> None:
        payload = build_real_torch_trainer_binding_audit_report().to_dict()
        names = [entry["name"] for entry in payload["prerequisite_tags_verified"]]
        self.assertEqual(len(names), len(set(names)))

    def test_feature_060_runner_is_not_reported_as_real_bound(self) -> None:
        payload = build_real_torch_trainer_binding_audit_report().to_dict()
        binding = payload["feature_060_code_binding_summary"]
        self.assertFalse(binding["runner_imports_torch"])
        self.assertFalse(binding["runner_imports_torchrl"])
        self.assertFalse(binding["runner_imports_real_trainer_candidate"])
        self.assertFalse(binding["runner_instantiates_real_trainer_candidate"])
        self.assertFalse(binding["runner_executes_real_trainer_update_or_fit"])
        self.assertFalse(binding["runner_uses_scalar_fallback_campaign"])

    def test_real_trainer_candidates_are_scanned_but_not_referenced_by_feature_060(self) -> None:
        payload = build_real_torch_trainer_binding_audit_report().to_dict()
        candidate_summary = payload["real_trainer_candidate_summary"]
        names = {
            name
            for candidate in candidate_summary["candidates"]
            for name in candidate["candidate_names"]
        }
        self.assertIn("DDQNTrainer", names)
        self.assertIn("TorchRLHoodieLearner", names)
        self.assertEqual(candidate_summary["feature_060_referenced_candidate_names"], ["DDQNTrainer"])


if __name__ == "__main__":
    unittest.main()
