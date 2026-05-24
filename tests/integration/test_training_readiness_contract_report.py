from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.analysis.training_readiness_contract import build_training_readiness_contract_report, run_training_readiness_contract


class TrainingReadinessContractReportIntegrationTests(unittest.TestCase):
    def test_report_written_to_artifacts(self) -> None:
        report = run_training_readiness_contract()
        json_path = Path("artifacts/analysis/training-readiness-contract/training-readiness-contract-report.json")
        md_path = Path("artifacts/analysis/training-readiness-contract/training-readiness-contract-report.md")
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["feature_id"], report.feature_id)
        self.assertEqual(payload["final_verdict"], "training_readiness_contract_ready_for_smoke_run")

    def test_report_payload_round_trip(self) -> None:
        payload = build_training_readiness_contract_report().to_dict()
        self.assertFalse(payload["remaining_blockers"])
        self.assertEqual(payload["recommended_next_feature"], "Feature 055 — Paper-Default Training Smoke Run")


if __name__ == "__main__":
    unittest.main()
