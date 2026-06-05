from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from src.analysis.hoodie_paper_faithful_runtime import generate_runtime_artifacts, validate_runtime_artifacts


class HoodiePaperFaithfulRuntimeCoreIntegrationTests(unittest.TestCase):
    def test_runtime_core_generates_required_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            report = generate_runtime_artifacts(output_dir)
            required = [
                "runtime_config.json",
                "arrival_diagnostics.json",
                "arrival_diagnostics.csv",
                "task_lifecycle_trace.json",
                "task_lifecycle_trace.csv",
                "queue_dynamics_trace.json",
                "queue_dynamics_trace.csv",
                "public_queue_active_set_trace.json",
                "public_queue_active_set_trace.csv",
                "state_snapshot_sample.json",
                "reward_events.json",
                "reward_events.csv",
                "runtime_degeneracy_diagnostics.json",
                "runtime_core_validation_report.json",
                "runtime_core_validation_report.md",
            ]
            for name in required:
                self.assertTrue((output_dir / name).exists(), name)
            self.assertEqual(report["phase"], "090-A runtime core only")

    def test_runtime_core_exercises_paths_and_public_sharing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            generate_runtime_artifacts(output_dir)
            active = (output_dir / "public_queue_active_set_trace.json").read_text(encoding="utf-8")
            self.assertIn("active_public_queue_count", active)
            self.assertIn("cpu_share_per_active_queue_ghz", active)

    def test_runtime_core_drain_phase_collects_rewards(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            generate_runtime_artifacts(output_dir)
            report = validate_runtime_artifacts(output_dir)
            self.assertTrue(report["passed"])

    def test_runtime_core_public_queue_active_set_non_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            generate_runtime_artifacts(output_dir)
            payload = (output_dir / "public_queue_active_set_trace.json").read_text(encoding="utf-8")
            self.assertIn("\"active_public_queue_count\":", payload)


if __name__ == "__main__":
    unittest.main()

