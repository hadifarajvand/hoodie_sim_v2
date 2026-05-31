from __future__ import annotations

import unittest

from src.analysis.controlled_evaluation_batch_readiness.report import build_feature_073_report, render_feature_073_report


class ControlledEvaluationBatchReadinessIntegrationReportTests(unittest.TestCase):
    def test_rendered_report_includes_claim_boundary_and_regression_evidence(self) -> None:
        report = build_feature_073_report()
        rendered = render_feature_073_report(report)
        self.assertIn("Feature 073 - Controlled Evaluation Batch Readiness", rendered)
        self.assertIn("controlled_evaluation_batch_readiness_ready", rendered)
        self.assertIn("Feature 068R regression", rendered)
        self.assertIn("Feature 072 regression", rendered)
        self.assertIn("Feature 074 - Baseline Policy Comparative Evaluation Readiness", rendered)
        self.assertIn("No final evaluation claim is made", rendered)
        self.assertIn("No performance superiority claim is made", rendered)
        self.assertIn("No full paper reproduction claim is made", rendered)
        self.assertIn("expected outputs are independent", rendered.lower())
        self.assertIn("actual outputs are computed from feature 070 and feature 071 helpers", rendered.lower())
        self.assertIn("horizontal legality is computed from feature 070 figure 7 neighbor map", rendered.lower())
        self.assertIn("local/private metrics are computed from feature 071 helpers", rendered.lower())
        self.assertIn("cloud terminal status respects paper-mode deadline semantics", rendered.lower())
        self.assertIn("compatibility mode is excluded from the default batch", rendered.lower())
