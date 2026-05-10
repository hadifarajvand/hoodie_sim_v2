from __future__ import annotations

import unittest

from src.analysis.baseline_rebuild_sensitivity_audit.runner import BaselineRebuildSensitivityAuditRunner


class BaselineRebuildSensitivityAuditFinalDiffIntegrationTest(unittest.TestCase):
    def test_report_and_artifact_surface_remain_isolated(self) -> None:
        report = BaselineRebuildSensitivityAuditRunner().run()
        payload = report.to_dict()

        self.assertEqual(report.metadata["feature_id"], "022-baseline-rebuild-sensitivity-audit")
        self.assertEqual(payload["source_gate_status"]["passed"], True)
        self.assertEqual(set(payload), {
            "metadata",
            "source_gate_status",
            "sensitivity_dimensions",
            "seeds_scenarios_episode_lengths_used",
            "fairness_controls",
            "included_baselines",
            "reused_metrics",
            "per_setting_baseline_signatures",
            "collapse_stability_indicators",
            "sensitivity_classification",
            "limitations",
            "no_training_disclaimer",
            "no_policy_redesign_disclaimer",
            "no_metric_change_disclaimer",
            "no_paper_validity_disclaimer",
            "reproducibility",
            "overall_status",
        })
        self.assertIn(report.overall_status, {"robust_collapse_reduced", "fragile_collapse_reduced", "collapse_unchanged", "collapse_worsened", "inconclusive"})


if __name__ == "__main__":
    unittest.main()
