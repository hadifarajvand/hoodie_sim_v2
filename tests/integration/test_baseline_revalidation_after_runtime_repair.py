from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.baseline_revalidation_after_runtime_repair import (
    BASELINE_POLICY_NAMES,
    BaselineRevalidationRunner,
)
from src.analysis.baseline_revalidation_after_runtime_repair.registry import (
    BASELINE_SCENARIO_NAMES,
    BASELINE_SEEDS,
)


class BaselineRevalidationAfterRuntimeRepairIntegrationTests(unittest.TestCase):
    def _run(self, *, output_dir: Path, evaluation_output_dir: Path, policy_names=BASELINE_POLICY_NAMES, seeds=BASELINE_SEEDS):
        runner = BaselineRevalidationRunner(
            output_dir=output_dir,
            evaluation_output_dir=evaluation_output_dir,
            policy_names=policy_names,
            scenario_names=BASELINE_SCENARIO_NAMES,
            seeds=seeds,
        )
        report = runner.run()
        return report

    def test_all_baselines_run_through_hoodie_gym_environment(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            analysis_dir = tmp / "analysis"
            evaluation_dir = tmp / "evaluation"
            report = self._run(output_dir=analysis_dir, evaluation_output_dir=evaluation_dir)

            self.assertEqual(report.policies_revalidated, list(BASELINE_POLICY_NAMES))
            self.assertEqual(report.scenarios_revalidated, list(BASELINE_SCENARIO_NAMES))
            self.assertEqual(report.seeds_used, list(BASELINE_SEEDS))
            self.assertEqual(report.baseline_result_summary["run_count"], len(BASELINE_POLICY_NAMES) * len(BASELINE_SCENARIO_NAMES) * len(BASELINE_SEEDS))
            self.assertTrue(report.environment_interface_verified)
            self.assertTrue(report.legal_action_mask_verified)
            self.assertTrue(report.deterministic_reproducibility_verified)
            self.assertTrue(report.metric_schema_verified)
            self.assertTrue(report.no_curve_fitting)
            self.assertTrue(report.no_paper_reproduction_claim)

            run_artifacts = sorted(evaluation_dir.glob("*.json"))
            self.assertEqual(len(run_artifacts), len(BASELINE_POLICY_NAMES) * len(BASELINE_SCENARIO_NAMES) * len(BASELINE_SEEDS))
            for path in run_artifacts:
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(payload["scenario_name"], "paper_default")
                self.assertIn(payload["policy_name"], BASELINE_POLICY_NAMES)
                self.assertIn(payload["seed"], BASELINE_SEEDS)
                for action_record in payload["selected_actions"]:
                    self.assertTrue(action_record["legal_action_mask"].get(action_record["action"], False))

    def test_all_baselines_emit_legal_actions_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            report = self._run(output_dir=tmp / "analysis", evaluation_output_dir=tmp / "evaluation")
            for matrix_row in report.baseline_result_summary["scenario_policy_seed_matrix"]:
                self.assertIn(matrix_row["policy_name"], BASELINE_POLICY_NAMES)
                self.assertEqual(matrix_row["scenario_name"], "paper_default")
                self.assertIn(matrix_row["seed"], BASELINE_SEEDS)

            self.assertTrue(report.legal_action_mask_verified)
            self.assertTrue(report.baseline_result_summary["legal_action_mask_verified"])

    def test_random_offloading_is_seed_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            first = self._run(
                output_dir=tmp / "analysis-a",
                evaluation_output_dir=tmp / "evaluation-a",
                policy_names=("RO",),
                seeds=(0,),
            )
            second = self._run(
                output_dir=tmp / "analysis-b",
                evaluation_output_dir=tmp / "evaluation-b",
                policy_names=("RO",),
                seeds=(0,),
            )

            self.assertEqual(first.policies_revalidated, second.policies_revalidated)
            self.assertEqual(first.scenarios_revalidated, second.scenarios_revalidated)
            self.assertEqual(first.seeds_used, second.seeds_used)
            self.assertEqual(first.baseline_result_summary["scenario_policy_seed_matrix"], second.baseline_result_summary["scenario_policy_seed_matrix"])

            first_payload = json.loads(next((tmp / "evaluation-a").glob("RO-paper_default-0.json")).read_text(encoding="utf-8"))
            second_payload = json.loads(next((tmp / "evaluation-b").glob("RO-paper_default-0.json")).read_text(encoding="utf-8"))
            self.assertEqual(first_payload["selected_actions"], second_payload["selected_actions"])
            self.assertEqual(first_payload["final_metrics"], second_payload["final_metrics"])


if __name__ == "__main__":
    unittest.main()
