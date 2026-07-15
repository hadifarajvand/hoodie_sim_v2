from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.reproducibility_bundle import (
    ReproducibilityBundleBuilder,
    ReproducibilityBundleConfig,
    _file_sha256,
)


class ReproducibilityBundleTests(unittest.TestCase):
    def _write_sample_matrix_output(self, output_dir: Path, include_summary: bool = True) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "FLC-paper_default-1.json").write_text(
            json.dumps({"policy_name": "FLC", "scenario_name": "paper_default", "seed": 1}),
            encoding="utf-8",
        )
        if include_summary:
            (output_dir / "matrix-summary.csv").write_text(
                "policy_name,scenario_name,seed,trace_id\nFLC,paper_default,1,trace-1\n",
                encoding="utf-8",
            )
        trace_dir = output_dir / "traces"
        trace_dir.mkdir(parents=True, exist_ok=True)
        (trace_dir / "trace-1.json").write_text(json.dumps({"trace_id": "trace-1"}), encoding="utf-8")

    def _config(self, matrix_dir: Path, bundle_dir: Path, timestamp: str | None = "2026-05-06T00:00:00+00:00"):
        return ReproducibilityBundleConfig(
            matrix_output_dir=matrix_dir,
            bundle_output_dir=bundle_dir,
            policy_names=("FLC",),
            scenario_names=("paper_default",),
            seeds=(1,),
            created_at_override=timestamp,
        )

    def test_checksum_calculation_and_relative_indexing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            matrix_dir = root / "matrix"
            bundle_dir = root / "bundle"
            self._write_sample_matrix_output(matrix_dir)
            builder = ReproducibilityBundleBuilder(self._config(matrix_dir, bundle_dir))

            outputs = builder.build()

            manifest = json.loads(outputs["manifest.json"].read_text(encoding="utf-8"))
            artifact_files = manifest["artifact_files"]
            self.assertGreater(len(artifact_files), 0)
            run_artifact = next(item for item in artifact_files if item["relative_path"] == "FLC-paper_default-1.json")
            expected_hash = hashlib.sha256((matrix_dir / "FLC-paper_default-1.json").read_bytes()).hexdigest()
            self.assertEqual(run_artifact["sha256"], expected_hash)
            index = json.loads(outputs["artifact-index.json"].read_text(encoding="utf-8"))
            self.assertEqual(index["run_json_files"], ["FLC-paper_default-1.json"])
            self.assertEqual(index["trace_files"], ["traces/trace-1.json"])
            self.assertEqual(index["matrix_summary_csv"], ["matrix-summary.csv"])

    def test_missing_matrix_summary_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            matrix_dir = root / "matrix"
            bundle_dir = root / "bundle"
            self._write_sample_matrix_output(matrix_dir, include_summary=False)
            builder = ReproducibilityBundleBuilder(self._config(matrix_dir, bundle_dir))

            outputs = builder.build()

            summary = json.loads(outputs["validation-summary.json"].read_text(encoding="utf-8"))
            self.assertFalse(summary["passed"])
            self.assertIn("matrix-summary.csv", summary["missing_artifacts"])

    def test_deterministic_timestamp_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            matrix_dir = root / "matrix"
            bundle_dir_one = root / "bundle-one"
            bundle_dir_two = root / "bundle-two"
            self._write_sample_matrix_output(matrix_dir)

            config_one = self._config(matrix_dir, bundle_dir_one)
            config_two = self._config(matrix_dir, bundle_dir_two)
            first = ReproducibilityBundleBuilder(config_one).build()
            second = ReproducibilityBundleBuilder(config_two).build()

            first_snapshot = {path.name: path.read_text(encoding="utf-8") for path in sorted(first.values())}
            second_snapshot = {path.name: path.read_text(encoding="utf-8") for path in sorted(second.values())}
            self.assertEqual(first_snapshot, second_snapshot)

    def test_file_sha256_helper_matches_hashlib(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample.txt"
            path.write_text("hello world", encoding="utf-8")
            self.assertEqual(_file_sha256(path), hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
