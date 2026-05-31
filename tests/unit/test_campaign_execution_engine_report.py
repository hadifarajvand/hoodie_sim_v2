from __future__ import annotations

from collections import Counter
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from src.analysis.campaign_execution_engine import report as campaign_report_module
from src.analysis.campaign_execution_engine.config import (
    DEADLINE_PRESSURE_LEVELS,
    FEATURE_NAME,
    READY_STATUS,
    REQUIRED_POLICY_IDS,
    REQUIRED_SCENARIO_IDS,
    RUNTIME_MODE,
    SEED_IDS,
    TOPOLOGY_MODE,
    WORKLOAD_LEVELS,
)
from src.analysis.campaign_execution_engine.report import (
    build_campaign_execution_grid,
    build_campaign_execution_rows,
    build_feature_078_report,
    build_execution_seed_plan,
    render_feature_078_report,
    validate_execution_rows,
)
from src.analysis.proposed_method_integration_readiness.model import PROPOSED_METHOD_POLICY_ID


class CampaignExecutionEngineReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = build_feature_078_report()

    def test_report_is_ready(self) -> None:
        self.assertEqual(self.report.feature_id, "078-campaign-execution-engine")
        self.assertEqual(self.report.status, READY_STATUS)
        self.assertTrue(self.report.passed)

    def test_row_count_matches_formula(self) -> None:
        self.assertEqual(self.report.seed_count, len(SEED_IDS))
        self.assertEqual(self.report.expected_row_count, 441 * self.report.seed_count)
        self.assertEqual(self.report.actual_row_count, self.report.expected_row_count)
        self.assertEqual(len(self.report.result_rows), self.report.expected_row_count)

    def test_dimension_coverage_is_complete(self) -> None:
        self.assertEqual(tuple(REQUIRED_POLICY_IDS), REQUIRED_POLICY_IDS)
        self.assertEqual(tuple(REQUIRED_SCENARIO_IDS), REQUIRED_SCENARIO_IDS)
        self.assertEqual({row.policy_id for row in self.report.result_rows}, set(REQUIRED_POLICY_IDS))
        self.assertEqual({row.scenario_id for row in self.report.result_rows}, set(REQUIRED_SCENARIO_IDS))
        self.assertEqual({row.seed_id for row in self.report.result_rows}, set(SEED_IDS))
        self.assertEqual({row.workload_level for row in self.report.result_rows}, set(WORKLOAD_LEVELS))
        self.assertEqual({row.deadline_pressure_level for row in self.report.result_rows}, set(DEADLINE_PRESSURE_LEVELS))

    def test_all_rows_are_action_bound_and_paper_faithful(self) -> None:
        self.assertTrue(all(not row.compatibility_mode_used for row in self.report.result_rows))
        self.assertTrue(all(row.topology_mode == TOPOLOGY_MODE for row in self.report.result_rows))
        self.assertTrue(all(row.runtime_mode == RUNTIME_MODE for row in self.report.result_rows))
        self.assertTrue(all(row.execution_runtime_path_used for row in self.report.result_rows))
        self.assertTrue(all(row.scenario_source for row in self.report.result_rows))
        self.assertTrue(all(row.policy_source for row in self.report.result_rows))
        self.assertTrue(all(row.workload_modifier_state for row in self.report.result_rows))
        self.assertTrue(all(row.deadline_modifier_state for row in self.report.result_rows))
        self.assertTrue(all(row.execution_provenance for row in self.report.result_rows))
        self.assertTrue(all("runtime_path=" in row.execution_provenance for row in self.report.result_rows))
        self.assertTrue(all("scenario_source=" in row.execution_provenance for row in self.report.result_rows))
        self.assertTrue(all("policy_source=" in row.execution_provenance for row in self.report.result_rows))
        self.assertTrue(all("seed_id=" in row.execution_provenance for row in self.report.result_rows))
        proposed_row = next(row for row in self.report.result_rows if row.policy_id == PROPOSED_METHOD_POLICY_ID)
        self.assertIn(PROPOSED_METHOD_POLICY_ID, proposed_row.policy_source)
        self.assertNotIn("PROPOSED_DCQ", proposed_row.policy_source)
        self.assertNotIn("proposed_deadline_queueing", proposed_row.policy_source)

    def test_build_helpers_are_consistent(self) -> None:
        seeds = build_execution_seed_plan()
        grid = build_campaign_execution_grid(seeds)
        rows = build_campaign_execution_rows(seed_plan=seeds)
        self.assertEqual(len(grid), len(rows))
        self.assertEqual(len(rows), self.report.actual_row_count)
        validate_execution_rows(rows)

    def test_rendered_report_contains_claim_boundary_and_no_overclaims(self) -> None:
        rendered = render_feature_078_report(self.report)
        self.assertIn("Feature 078 Campaign Execution Engine Report", rendered)
        self.assertIn("No training claim is made.", rendered)
        self.assertIn("No superiority claim is made.", rendered)
        self.assertIn("No final evaluation claim is made.", rendered)
        self.assertIn("No statistical significance claim is made.", rendered)
        self.assertIn("No full paper reproduction claim is made.", rendered)
        self.assertIn("No statistical summary claim is made.", rendered)
        self.assertIn("No ranking claim is made.", rendered)
        self.assertIn("No winner claim is made.", rendered)
        self.assertNotIn("winner:", rendered.lower())
        self.assertNotIn("statistical summary", rendered.lower().replace("no statistical summary claim is made.", ""))

    def test_runtime_helper_is_invoked_for_every_cell(self) -> None:
        campaign_report_module._feature_076_report.cache_clear()
        fake_feature_076 = SimpleNamespace(passed=True)
        with (
            patch.object(campaign_report_module, "_feature_076_report", return_value=fake_feature_076),
            patch.object(campaign_report_module, "build_action_bound_outcome", wraps=campaign_report_module.build_action_bound_outcome) as mocked_outcome,
        ):
            report = campaign_report_module.build_feature_078_report()
        self.assertEqual(mocked_outcome.call_count, report.actual_row_count)

    def test_rows_are_not_copied_from_feature_076(self) -> None:
        campaign_report_module._feature_076_report.cache_clear()
        fake_feature_076 = SimpleNamespace(passed=True, rows=(SimpleNamespace(selected_action_id="sentinel_action"),))
        with patch.object(campaign_report_module, "_feature_076_report", return_value=fake_feature_076):
            report = campaign_report_module.build_feature_078_report()
        first_row = report.result_rows[0]
        self.assertNotEqual(first_row.selected_action_id, "sentinel_action")
        self.assertIn("runtime_path=", first_row.execution_provenance)

    def test_result_row_counts_are_non_negative(self) -> None:
        for row in self.report.result_rows[:25]:
            self.assertGreaterEqual(row.completed_count, 0)
            self.assertGreaterEqual(row.dropped_timeout_count, 0)
            self.assertGreaterEqual(row.dropped_unavailable_count, 0)
            self.assertGreaterEqual(row.deadline_violation_count, 0)
            self.assertGreaterEqual(row.illegal_action_rejection_count, 0)
            self.assertGreaterEqual(row.completion_rate, 0.0)
            self.assertGreaterEqual(row.timeout_drop_rate, 0.0)
            self.assertGreaterEqual(row.unavailable_drop_rate, 0.0)
            self.assertGreaterEqual(row.deadline_violation_rate, 0.0)

    def test_all_rows_have_single_campaign_cell_identity(self) -> None:
        keys = Counter(
            (row.policy_id, row.scenario_id, row.seed_id, row.workload_level, row.deadline_pressure_level)
            for row in self.report.result_rows
        )
        self.assertTrue(all(count == 1 for count in keys.values()))
        self.assertEqual(len(keys), self.report.actual_row_count)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
