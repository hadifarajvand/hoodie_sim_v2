from __future__ import annotations

import unittest

from src.analysis.baseline_fairness_rebuild.runner import BaselineFairnessRebuildRunner


class BaselineFairnessRebuildFinalDiffIntegrationTest(unittest.TestCase):
    def test_report_and_artifact_surface_remain_isolated(self) -> None:
        report = BaselineFairnessRebuildRunner().run()
        payload = report.to_dict()

        self.assertEqual(report.metadata["feature_id"], "021-baseline-fairness-rebuild")
        self.assertEqual(payload["source_gate_status"]["passed"], True)
        self.assertEqual(set(payload), {
            "metadata",
            "source_gate_status",
            "baseline_policies_included",
            "scenarios_traces_used",
            "fairness_controls",
            "metrics_reused",
            "collapse_indicators",
            "anti_collapse_assessment",
            "unchanged_collapse_explanation",
            "limitations",
            "no_training_disclaimer",
            "no_policy_redesign_disclaimer",
            "no_paper_validity_disclaimer",
            "reproducibility_details",
            "overall_status",
        })
        self.assertIn(report.overall_status, {"collapse_reduced", "collapse_unchanged", "collapse_worsened", "inconclusive"})


if __name__ == "__main__":
    unittest.main()
