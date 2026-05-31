from __future__ import annotations

from dataclasses import replace
import unittest

from src.analysis.campaign_execution_engine.config import (
    DEADLINE_PRESSURE_LEVELS,
    DEPENDENCY_FEATURES,
    READY_STATUS,
    REQUIRED_POLICY_IDS,
    REQUIRED_SCENARIO_IDS,
    RUNTIME_MODE,
    SEED_IDS,
    TOPOLOGY_MODE,
    WORKLOAD_LEVELS,
)
from src.analysis.campaign_execution_engine.model import (
    CampaignExecutionGridCell,
    CampaignExecutionReport,
    CampaignExecutionResultRow,
    CampaignExecutionSeed,
)
from src.analysis.campaign_execution_engine.report import build_feature_078_report, build_execution_seed_plan


class CampaignExecutionEngineModelTests(unittest.TestCase):
    def test_seed_rejects_empty_identifier(self) -> None:
        with self.assertRaises(ValueError):
            CampaignExecutionSeed(seed_id="", seed_value=1, source="deterministic")

    def test_grid_cell_rejects_invalid_topology(self) -> None:
        with self.assertRaises(ValueError):
            CampaignExecutionGridCell(
                policy_id=REQUIRED_POLICY_IDS[0],
                scenario_id=REQUIRED_SCENARIO_IDS[0],
                seed_id=SEED_IDS[0],
                workload_level=WORKLOAD_LEVELS[0],
                deadline_pressure_level=DEADLINE_PRESSURE_LEVELS[0],
                topology_mode="compatibility",
                runtime_mode=RUNTIME_MODE,
            )

    def test_grid_cell_rejects_invalid_runtime(self) -> None:
        with self.assertRaises(ValueError):
            CampaignExecutionGridCell(
                policy_id=REQUIRED_POLICY_IDS[0],
                scenario_id=REQUIRED_SCENARIO_IDS[0],
                seed_id=SEED_IDS[0],
                workload_level=WORKLOAD_LEVELS[0],
                deadline_pressure_level=DEADLINE_PRESSURE_LEVELS[0],
                topology_mode=TOPOLOGY_MODE,
                runtime_mode="compatibility",
            )

    def test_result_row_rejects_compatibility_mode(self) -> None:
        row = build_feature_078_report().result_rows[0]
        with self.assertRaises(ValueError):
            replace(row, compatibility_mode_used=True)

    def test_result_row_rejects_empty_selected_action_id(self) -> None:
        row = build_feature_078_report().result_rows[0]
        with self.assertRaises(ValueError):
            replace(row, selected_action_id="")

    def test_result_row_rejects_empty_execution_runtime_path(self) -> None:
        row = build_feature_078_report().result_rows[0]
        with self.assertRaises(ValueError):
            replace(row, execution_runtime_path_used="")

    def test_result_row_rejects_empty_provenance(self) -> None:
        row = build_feature_078_report().result_rows[0]
        with self.assertRaises(ValueError):
            replace(row, execution_provenance="")

    def test_report_rejects_wrong_dependency_features(self) -> None:
        report = build_feature_078_report()
        with self.assertRaises(ValueError):
            replace(report, dependency_features=("076-combined-baseline-proposed-comparative-readiness",))

    def test_report_rejects_row_count_mismatch(self) -> None:
        report = build_feature_078_report()
        with self.assertRaises(ValueError):
            replace(report, actual_row_count=report.actual_row_count - 1)

    def test_report_rejects_bad_status_for_passed_report(self) -> None:
        report = build_feature_078_report()
        with self.assertRaises(ValueError):
            replace(report, status="campaign_execution_engine_with_blockers")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
