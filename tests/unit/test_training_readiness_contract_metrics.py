from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import unittest

from src.analysis.training_readiness_contract import build_training_readiness_contract_report
from src.analysis.training_readiness_contract.model import TrainingReadinessContractReport
from src.analysis.training_readiness_contract.runner import _feature_053_readiness_verified


class TrainingReadinessContractMetricsTests(unittest.TestCase):
    def test_contract_locks_and_readiness_are_true_on_the_passing_path(self) -> None:
        payload = build_training_readiness_contract_report().to_dict()
        for key in [
            "paper_default_config_locked",
            "observation_contract_locked",
            "action_contract_locked",
            "legality_contract_locked",
            "reward_contract_locked",
            "timeout_contract_locked",
            "capacity_contract_locked",
            "transmission_contract_locked",
            "queue_contract_locked",
            "metric_contract_locked",
            "seed_contract_locked",
            "artifact_contract_locked",
        ]:
            self.assertTrue(payload[key])
        self.assertTrue(payload["feature_053_readiness_verified"])
        self.assertFalse(payload["evidence_chain_ready_for_training_contract"])
        self.assertFalse(payload["training_execution_allowed_next"])
        self.assertIn("evidence_chain_prerequisite_blocked", payload["remaining_blockers"])
        self.assertIn("prerequisite_tags_failed", payload["remaining_blockers"])
        self.assertEqual(payload["final_verdict"], "evidence_chain_prerequisite_blocked")
        self.assertEqual(payload["recommended_next_feature"], "prerequisite evidence repair before training")

    def test_training_cannot_be_allowed_when_any_contract_gate_is_false(self) -> None:
        payload = build_training_readiness_contract_report().to_dict()
        payload["paper_default_config_locked"] = False
        payload["training_execution_allowed_next"] = True
        payload["remaining_blockers"] = ["paper_default_config_contract_blocked"]
        with self.assertRaises(ValueError):
            TrainingReadinessContractReport(**payload)

    def test_blocked_reports_cannot_route_to_feature_055(self) -> None:
        payload = build_training_readiness_contract_report().to_dict()
        payload["training_execution_allowed_next"] = False
        payload["remaining_blockers"] = ["behavior_drift_detected"]
        payload["final_verdict"] = "behavior_drift_detected"
        payload["recommended_next_feature"] = "Feature 055 — Paper-Default Training Smoke Run"
        with self.assertRaises(ValueError):
            TrainingReadinessContractReport(**payload)

    def test_feature_053_readiness_gate_requires_each_declared_field(self) -> None:
        feature_053 = json.loads(
            Path("artifacts/analysis/exposure-matrix-paper-mechanism-rerun-with-outcome-evidence/exposure-matrix-paper-mechanism-rerun-report.json").read_text(encoding="utf-8")
        )
        self.assertTrue(_feature_053_readiness_verified(feature_053))
        cases = [
            ("paper_mechanism_alignment_ready", False),
            ("final_verdict", "not-the-right-verdict"),
            ("remaining_blockers", ["unexpected_blocker"]),
            ("observation_vector_alignment_status", "partial"),
            ("formula_unit_alignment_status", "partial"),
            ("exposure_matrix_alignment_status", "partial"),
            ("selected_action_outcome_alignment_status", "partial"),
            ("training_readiness_contract_status", "partial"),
            ("behavior_equivalence_passed", False),
            ("recommended_next_feature", "Feature 999 — Broken"),
        ]
        for field_name, bad_value in cases:
            mutated = deepcopy(feature_053)
            mutated[field_name] = bad_value
            self.assertFalse(_feature_053_readiness_verified(mutated), msg=field_name)


if __name__ == "__main__":
    unittest.main()
