from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.analysis.load_admission_action_exposure_review.runner import run_load_admission_action_exposure_review


class LoadAdmissionActionExposureSchemaTest(unittest.TestCase):
    def test_report_schema_exactness(self) -> None:
        payload = run_load_admission_action_exposure_review().to_dict()
        self.assertEqual(
            set(payload),
            {
                "feature_id",
                "prerequisite_tags_verified",
                "prior_feature_gates_verified",
                "trace_input_sources",
                "paper_default_runtime_verified",
                "load_pressure_summary",
                "admission_serialization_summary",
                "action_exposure_summary",
                "queue_pressure_summary",
                "offload_path_pressure_summary",
                "budget_comparison_summary",
                "per_strategy_summary",
                "per_action_summary",
                "per_queue_summary",
                "dominant_pressure_sources",
                "diagnosis",
                "recommended_next_feature",
                "no_runtime_repair_performed",
                "no_training_started",
                "no_optimizer_step",
                "no_replay_training",
                "no_target_update_execution",
                "no_dependency_drift",
                "no_environment_contract_drift",
                "no_policy_drift",
                "no_reward_timing_change",
                "no_timeout_contract_drift",
                "no_capacity_contract_drift",
                "no_transmission_contract_drift",
                "no_action_legality_drift",
                "no_curve_fitting",
                "no_simulator_output_tuning",
                "no_paper_reproduction_claim",
                "final_verdict",
            },
        )

    def test_report_schema_and_verdict(self) -> None:
        report = run_load_admission_action_exposure_review()
        payload = report.to_dict()
        self.assertEqual(payload["feature_id"], "046-load-admission-action-exposure-review")
        self.assertEqual(payload["final_verdict"], "load_pressure_explains_completion_weakness")
        self.assertEqual(payload["recommended_next_feature"], "exposure-matrix review")
        self.assertTrue(payload["no_runtime_repair_performed"])
        self.assertTrue(payload["no_paper_reproduction_claim"])

    def test_feature_045_committed_artifact_prerequisites(self) -> None:
        payload = json.loads(Path("artifacts/analysis/completion-root-cause-diagnosis/completion-root-cause-report.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["feature_id"], "045-completion-root-cause-diagnosis")
        self.assertEqual(payload["final_verdict"], "root_cause_identified_configuration_or_load_explanation")
        self.assertEqual(payload["recommended_next_feature"], "load/admission/action-exposure review")
        self.assertTrue(payload["no_runtime_repair_performed"])
        self.assertTrue(payload["no_paper_reproduction_claim"])
        if "no_unrelated_dirty_files" in payload:
            self.assertTrue(payload["no_unrelated_dirty_files"])
        self.assertFalse(payload.get("runtime_repair_verdict_guard", False))

    def test_includes_passive_inputs(self) -> None:
        report = run_load_admission_action_exposure_review()
        sources = report.to_dict()["trace_input_sources"]
        self.assertEqual({item["feature"] for item in sources}, {"044", "045"})

    def test_rejects_non_paper_default_trace(self) -> None:
        from src.analysis.load_admission_action_exposure_review.runner import _paper_default_runtime_verified
        from src.analysis.load_admission_action_exposure_review.config import LoadAdmissionActionExposureConfig

        with self.assertRaises(ValueError):
            _paper_default_runtime_verified({"paper_default_runtime_verified": {"episode_length": 109}}, LoadAdmissionActionExposureConfig())


if __name__ == "__main__":
    unittest.main()
