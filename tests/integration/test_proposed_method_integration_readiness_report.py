from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.analysis.proposed_method_integration_readiness.report import (
    build_feature_075_report,
    render_feature_075_report,
    write_feature_075_report,
)


class ProposedMethodIntegrationReadinessReportIntegrationTests(unittest.TestCase):
    def test_rendered_report_mentions_action_bound_evidence_required_scenarios_and_claim_boundary(self) -> None:
        report = build_feature_075_report()
        rendered = render_feature_075_report(report)
        self.assertIn("Feature 075 Proposed Method Integration Readiness Report", rendered)
        self.assertIn("proposed_method_integration_readiness_ready", rendered)
        self.assertIn("selected_action_id", rendered)
        self.assertIn("selected_action_family", rendered)
        self.assertIn("candidate_ranking_trace_present", rendered)
        self.assertIn("deadline_slack_evidence_present", rendered)
        self.assertIn("queue_or_load_evidence_present", rendered)
        self.assertIn("topology_legality_enforced", rendered)
        self.assertIn("action_bound_terminal_status", rendered)
        self.assertIn("action_bound_reward_value", rendered)
        self.assertIn("action_bound_metrics_derived", rendered)
        self.assertIn("compatibility_mode_used", rendered)
        self.assertIn("PROPOSED_DCQ", rendered)
        self.assertIn("proposed_deadline_queueing", rendered)
        self.assertIn("light_load_no_deadline_pressure", rendered)
        self.assertIn("tight_deadline_pressure", rendered)
        self.assertIn("legal_horizontal_offload", rendered)
        self.assertIn("illegal_horizontal_destination_attempt", rendered)
        self.assertIn("cloud_vertical_fallback", rendered)
        self.assertIn("timeout_drop_case", rendered)
        self.assertIn("mixed_local_horizontal_cloud_candidates", rendered)
        self.assertIn("No training claim is made.", rendered)
        self.assertIn("No final evaluation claim is made.", rendered)
        self.assertIn("No performance superiority claim is made.", rendered)
        self.assertIn("No statistical significance claim is made.", rendered)
        self.assertIn("No full paper reproduction claim is made.", rendered)
        self.assertIn("Feature 073 controlled scenarios are used as fixtures, not copied final metrics.", rendered)
        self.assertIn("Selected policy actions are bound to controlled outcomes.", rendered)
        self.assertIn("Horizontal selected actions use Feature 070 Figure 7 topology.", rendered)
        self.assertIn("Feature 071 helpers are used for paper-mode terminal and reward behavior.", rendered)
        self.assertIn("Compatibility mode is excluded from the default proposed-method evaluation.", rendered)

    def test_write_feature_075_report_emits_markdown_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = write_feature_075_report(Path(tmpdir))
            self.assertTrue(output.exists())
            self.assertTrue((Path(tmpdir) / "feature-075-proposed-method-integration-readiness-report.json").exists())
            markdown = output.read_text(encoding="utf-8")
            self.assertIn("proposed_method_integration_readiness_ready", markdown)


if __name__ == "__main__":
    unittest.main()
