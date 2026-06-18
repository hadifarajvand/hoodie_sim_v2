from __future__ import annotations

import unittest

from src.analysis.bind_full_campaign_real_torch_trainer import build_bind_full_campaign_real_torch_trainer_report


class BindFullCampaignRealTorchTrainerMetricsTests(unittest.TestCase):
    def test_repo_venv_torch_and_torchrl_are_checked(self) -> None:
        payload = build_bind_full_campaign_real_torch_trainer_report().to_dict()
        summary = payload["torch_environment_summary"]
        self.assertFalse(summary["repo_venv_python_exists"])
        self.assertTrue(summary["torch_available"])
        self.assertFalse(summary["torchrl_available"])
        self.assertEqual(summary["torch_version"], "2.12.0")

    def test_real_trainer_binding_fields_are_true(self) -> None:
        binding = build_bind_full_campaign_real_torch_trainer_report().to_dict()["real_trainer_binding_summary"]
        self.assertTrue(binding["real_binding_verified"])
        self.assertTrue(binding["torch_import_used"])
        self.assertTrue(binding["real_trainer_import_used"])
        self.assertTrue(binding["real_trainer_instantiated"])
        self.assertTrue(binding["real_trainer_update_or_train_called"])
        self.assertFalse(binding["scalar_fallback_drives_campaign_claim"])

    def test_feature_060_metrics_come_from_real_bound_path(self) -> None:
        payload = build_bind_full_campaign_real_torch_trainer_report().to_dict()
        self.assertEqual(payload["training_metrics_summary"]["optimizer_step_count"], 47)
        self.assertEqual(payload["training_metrics_summary"]["replay_size"], 110)
        self.assertTrue(payload["training_metrics_summary"]["real_trainer_binding"]["real_trainer_update_or_train_called"])


if __name__ == "__main__":
    unittest.main()
