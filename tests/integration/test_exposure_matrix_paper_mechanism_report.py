from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.exposure_matrix_paper_mechanism_alignment import build_exposure_matrix_paper_mechanism_report, write_exposure_matrix_paper_mechanism_report


class ExposureMatrixPaperMechanismReportIntegrationTests(unittest.TestCase):
    def test_report_write_outputs_json_and_markdown(self) -> None:
        report = build_exposure_matrix_paper_mechanism_report()
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path, md_path = write_exposure_matrix_paper_mechanism_report(report, output_dir=tmpdir)
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            payload = json.loads(Path(json_path).read_text(encoding="utf-8"))
            self.assertEqual(payload["feature_id"], "049-exposure-matrix-paper-mechanism-alignment")
            self.assertIn("exposure_matrix_rerun_summary", payload)
            self.assertIn("observation_vector_audit", payload)
            self.assertIn("paper_formula_unit_audit", payload)
            self.assertIn("training_readiness_decision", payload)

    def test_report_includes_no_drift_flags(self) -> None:
        payload = build_exposure_matrix_paper_mechanism_report().to_dict()
        for flag in (
            "no_runtime_repair_performed",
            "no_training_started",
            "no_optimizer_step",
            "no_replay_training",
            "no_target_update_execution",
            "no_dependency_drift",
            "no_policy_drift",
            "no_reward_timing_change",
            "no_timeout_contract_drift",
            "no_capacity_contract_drift",
            "no_transmission_contract_drift",
            "no_action_legality_drift",
            "no_action_selection_drift",
            "no_curve_fitting",
            "no_simulator_output_tuning",
            "no_paper_reproduction_claim",
        ):
            self.assertTrue(payload[flag])


if __name__ == "__main__":
    unittest.main()
