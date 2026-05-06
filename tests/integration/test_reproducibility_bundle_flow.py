from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.reproducibility_bundle import (
    ReproducibilityBundleBuilder,
    ReproducibilityBundleConfig,
)
from src.evaluation.matrix_config import EvaluationMatrixConfig
from src.evaluation.matrix_runner import EvaluationMatrixRunner


class ReproducibilityBundleFlowTests(unittest.TestCase):
    def _matrix_config(self, output_dir: Path) -> EvaluationMatrixConfig:
        return EvaluationMatrixConfig(
            policy_names=("FLC",),
            scenario_names=("paper_default",),
            seeds=(1,),
            output_dir=output_dir,
            episode_length=3,
        )

    def _bundle_config(self, matrix_dir: Path, bundle_dir: Path, timestamp: str) -> ReproducibilityBundleConfig:
        return ReproducibilityBundleConfig(
            matrix_output_dir=matrix_dir,
            bundle_output_dir=bundle_dir,
            policy_names=("FLC",),
            scenario_names=("paper_default",),
            seeds=(1,),
            created_at_override=timestamp,
        )

    def test_bundle_flow_creates_required_files_and_passes_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            matrix_dir = root / "matrix"
            bundle_dir = root / "bundle"
            EvaluationMatrixRunner(self._matrix_config(matrix_dir)).run()

            builder = ReproducibilityBundleBuilder(self._bundle_config(matrix_dir, bundle_dir, "2026-05-06T00:00:00+00:00"))
            outputs = builder.build()

            required = {
                "manifest.json",
                "run-config.json",
                "artifact-index.json",
                "validation-summary.json",
                "README.md",
            }
            self.assertEqual(set(path.name for path in outputs.values()), required)

            summary = json.loads((bundle_dir / "validation-summary.json").read_text(encoding="utf-8"))
            self.assertTrue(summary["passed"])
            manifest = json.loads((bundle_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertGreater(len(manifest["artifact_files"]), 0)
            self.assertTrue(all("sha256" in item for item in manifest["artifact_files"]))

    def test_repeated_bundle_generation_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            matrix_dir = root / "matrix"
            bundle_dir_one = root / "bundle-one"
            bundle_dir_two = root / "bundle-two"
            EvaluationMatrixRunner(self._matrix_config(matrix_dir)).run()

            builder_one = ReproducibilityBundleBuilder(self._bundle_config(matrix_dir, bundle_dir_one, "2026-05-06T00:00:00+00:00"))
            builder_two = ReproducibilityBundleBuilder(self._bundle_config(matrix_dir, bundle_dir_two, "2026-05-06T00:00:00+00:00"))
            outputs_one = builder_one.build()
            outputs_two = builder_two.build()

            snapshot_one = {name: path.read_text(encoding="utf-8") for name, path in outputs_one.items()}
            snapshot_two = {name: path.read_text(encoding="utf-8") for name, path in outputs_two.items()}
            self.assertEqual(snapshot_one, snapshot_two)


if __name__ == "__main__":
    unittest.main()
