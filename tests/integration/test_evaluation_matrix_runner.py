from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.evaluation.matrix_config import EvaluationMatrixConfig
from src.evaluation.matrix_runner import EvaluationMatrixRunner


class EvaluationMatrixRunnerTests(unittest.TestCase):
    def _config(self, output_dir: Path | None) -> EvaluationMatrixConfig:
        return EvaluationMatrixConfig(
            policy_names=("FLC", "ADAPTIVE"),
            scenario_names=("paper_default", "moderate"),
            seeds=(1, 2),
            output_dir=output_dir,
            episode_length=3,
        )

    def test_small_matrix_runs_deterministically(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            runner = EvaluationMatrixRunner(self._config(output_dir))
            first = runner.run()
            first_snapshot = {
                path.name: path.read_text(encoding="utf-8")
                for path in sorted(output_dir.glob("*.json"))
            }
            first_csv = (output_dir / "matrix-summary.csv").read_text(encoding="utf-8")

            second = EvaluationMatrixRunner(self._config(output_dir)).run()
            second_snapshot = {
                path.name: path.read_text(encoding="utf-8")
                for path in sorted(output_dir.glob("*.json"))
            }
            second_csv = (output_dir / "matrix-summary.csv").read_text(encoding="utf-8")

            self.assertEqual(first, second)
            self.assertEqual(first_snapshot, second_snapshot)
            self.assertEqual(first_csv, second_csv)

    def test_artifacts_contain_policy_scenario_seed_trace_and_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            runner = EvaluationMatrixRunner(self._config(output_dir))
            result = runner.run()

            self.assertEqual(result["count"], 8)
            json_files = sorted(output_dir.glob("*.json"))
            self.assertGreater(len(json_files), 0)

            payload = json.loads(json_files[0].read_text(encoding="utf-8"))
            self.assertIn("policy_name", payload)
            self.assertIn("scenario_name", payload)
            self.assertIn("seed", payload)
            self.assertIn("trace_id", payload)
            self.assertIn("final_metrics", payload)
            self.assertIn("runtime_metadata", payload)
            self.assertIn("config_snapshot", payload)
            self.assertIn("finalized_tasks", payload)

            csv_path = output_dir / "matrix-summary.csv"
            self.assertTrue(csv_path.exists())
            with csv_path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertGreater(len(rows), 0)
            self.assertIn("policy_name", rows[0])
            self.assertIn("scenario_name", rows[0])
            self.assertIn("seed", rows[0])
            self.assertIn("trace_id", rows[0])
            self.assertIn("average_delay", rows[0])

    def test_unsupported_names_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = EvaluationMatrixConfig(
                policy_names=("UNKNOWN",),
                scenario_names=("paper_default",),
                seeds=(1,),
                output_dir=Path(tmpdir),
            )
            with self.assertRaises(ValueError):
                EvaluationMatrixRunner(config).run()

            config = EvaluationMatrixConfig(
                policy_names=("FLC",),
                scenario_names=("unknown",),  # type: ignore[arg-type]
                seeds=(1,),
                output_dir=Path(tmpdir),
            )
            with self.assertRaises(ValueError):
                EvaluationMatrixRunner(config).run()


if __name__ == "__main__":
    unittest.main()
