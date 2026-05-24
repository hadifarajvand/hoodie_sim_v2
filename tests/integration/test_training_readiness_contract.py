from __future__ import annotations

from pathlib import Path
import json
import unittest

from src.analysis.training_readiness_contract import build_training_readiness_contract_report
from src.analysis.training_readiness_contract.runner import _feature_053_readiness_verified


class TrainingReadinessContractIntegrationTests(unittest.TestCase):
    def test_feature_053_readiness_gate_is_satisfied_by_the_committed_artifact(self) -> None:
        feature_053 = json.loads(
            Path("artifacts/analysis/exposure-matrix-paper-mechanism-rerun-with-outcome-evidence/exposure-matrix-paper-mechanism-rerun-report.json").read_text(encoding="utf-8")
        )
        self.assertTrue(_feature_053_readiness_verified(feature_053))

    def test_report_ready_path_matches_contract(self) -> None:
        payload = build_training_readiness_contract_report().to_dict()
        tag_names = [entry["name"] for entry in payload["prerequisite_tags_verified"]]
        self.assertEqual(
            tag_names,
            [
                "branch",
                "not_main",
                "main_contains_feature_053",
                "main_contains_054a_hygiene",
                "main_is_branch_base",
                "feature_diff_contains_only_approved_paths",
                "no_feature_037_053_artifact_rewrites",
                "agents_stable_not_modified",
                "pointer_local_only_not_in_committed_diff",
            ],
        )
        self.assertTrue(all(entry["verified"] for entry in payload["prerequisite_tags_verified"]))
        self.assertTrue(payload["feature_053_readiness_verified"])
        self.assertTrue(payload["evidence_chain_ready_for_training_contract"])
        self.assertTrue(payload["training_execution_allowed_next"])
        self.assertEqual(payload["recommended_next_feature"], "Feature 055 — Paper-Default Training Smoke Run")
        self.assertEqual(payload["final_verdict"], "training_readiness_contract_ready_for_smoke_run")


if __name__ == "__main__":
    unittest.main()
