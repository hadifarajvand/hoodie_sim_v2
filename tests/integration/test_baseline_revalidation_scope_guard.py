from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.analysis.baseline_revalidation_after_runtime_repair import BaselineRevalidationRunner


class BaselineRevalidationScopeGuardIntegrationTests(unittest.TestCase):
    def test_runtime_contract_drift_and_scope_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report = BaselineRevalidationRunner(
                output_dir=Path(tmpdir) / "analysis",
                evaluation_output_dir=Path(tmpdir) / "evaluation",
            ).run()
            payload = report.to_dict()
            summary = payload["baseline_result_summary"]

            self.assertTrue(payload["no_dependency_drift"])
            self.assertTrue(payload["no_training_or_policy_drift"])
            self.assertTrue(payload["no_environment_contract_drift"])
            self.assertTrue(payload["no_reward_timing_change"])
            self.assertTrue(payload["no_execution_time_contract_drift"])
            self.assertTrue(payload["no_transmission_delay_contract_drift"])
            self.assertTrue(payload["no_capacity_sharing_contract_drift"])
            self.assertTrue(payload["no_timeout_contract_drift"])

            self.assertEqual(
                payload["runtime_contracts_verified"],
                [
                    "Feature 032 runtime assumption contract",
                    "Feature 033 execution-time contract",
                    "Feature 034 transmission-delay runtime wiring",
                    "Feature 035 public/cloud capacity-sharing contract",
                    "Feature 036 inclusive timeout/deadline boundary",
                ],
            )
            self.assertIn("src/analysis/baseline_revalidation_after_runtime_repair/runner.py", summary["source_refs"])
            self.assertIn("src/evaluation/policy_registry.py", summary["source_refs"])
            self.assertNotIn("src/training/", "".join(summary["source_refs"]))
            self.assertNotIn("src/models/", "".join(summary["source_refs"]))
            self.assertNotIn("campaign", "".join(summary["source_refs"]))
            self.assertNotIn("dependency", "".join(summary["source_refs"]))


if __name__ == "__main__":
    unittest.main()
