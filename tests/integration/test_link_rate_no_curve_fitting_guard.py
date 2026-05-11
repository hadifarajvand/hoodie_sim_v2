from __future__ import annotations

import unittest

from src.analysis.link_rate_transmission_delay_contract.report import build_link_rate_contract_report


class LinkRateNoCurveFittingGuardTest(unittest.TestCase):
    def test_validation_artifact_does_not_claim_curve_fitting(self) -> None:
        report = build_link_rate_contract_report().to_dict()
        self.assertTrue(report["no_curve_fitting"])
        self.assertTrue(report["no_topology_fabrication"])
        self.assertTrue(report["no_policy_or_metric_redesign"])
        self.assertTrue(report["no_training_or_dependency_drift"])
        self.assertIn("monotonic delay checks pass", report["validation_summary"])


if __name__ == "__main__":
    unittest.main()
