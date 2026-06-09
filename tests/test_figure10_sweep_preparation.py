from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import scripts.prepare_figure10_baseline_sweeps as sweep_prep


ROOT = Path(__file__).resolve().parents[1]


class Figure10SweepPreparationTests(unittest.TestCase):
    def test_script_prints_baseline_only_commands_and_writes_small_configs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            with (
                patch.object(sweep_prep, "ROOT", tmp_path),
                patch.object(sweep_prep, "SWEEP_ROOT", tmp_path / "artifacts" / "figure10_validation" / "sweep_configs" / "baseline-only"),
                patch.object(sweep_prep, "RUN_ROOT", tmp_path / "artifacts" / "figure10_validation" / "sweeps" / "baseline-only"),
            ):
                buf = io.StringIO()
                generated = sweep_prep._build_sweep_configs()
                with redirect_stdout(buf):
                    code = sweep_prep.main()
                stdout = buf.getvalue()
                self.assertEqual(code, 0)
                self.assertIn("baseline-only", stdout)
                self.assertIn("HOODIE is intentionally excluded", stdout)
                self.assertIn("task_arrival_probability", stdout)
                self.assertIn("private_cpu_ghz", stdout)
                self.assertIn("timeout_slots", stdout)
                self.assertIn("--episodes 200", stdout)
                self.assertIn("--policies RO,FLC,VO,HO,BCO,MLEO", stdout)
                self.assertNotIn("HOODIE,RO", stdout)
                sweep_config_root = tmp_path / "artifacts" / "figure10_validation" / "sweep_configs" / "baseline-only"
                written_configs = list(sweep_config_root.rglob("config.yml"))
                self.assertTrue(written_configs)
                self.assertTrue(any(path.parent.name == "0.5" for path in generated["task_arrival_probability"]))
                self.assertIn("trace_level:", written_configs[0].read_text())
                self.assertIn("summary", written_configs[0].read_text())
                self.assertTrue(written_configs[0].with_name("hyperparameters.json").exists())

    def test_script_does_not_reference_simulator_entry_points(self):
        source = (ROOT / "scripts" / "prepare_figure10_baseline_sweeps.py").read_text()
        self.assertNotIn("subprocess.run", source)
        self.assertNotIn("os.system", source)
        self.assertNotIn("training.train_phase3", source)

    def test_audit_mentions_baseline_only_and_no_simulation(self):
        audit = (ROOT / "artifacts" / "paper-contract-audit" / "phase5_3" / "figure10_sweep_workflow_audit.md").read_text()
        self.assertIn("baseline-only", audit)
        self.assertIn("HOODIE is intentionally excluded", audit)
        self.assertIn("not full official HOODIE Figure 10 reproduction", audit)
        self.assertIn("does not run any simulation", audit)
        self.assertIn("generated sweep outputs", audit.lower())

    def test_gitignore_contains_sweep_and_large_trace_patterns(self):
        gitignore = (ROOT / ".gitignore").read_text()
        self.assertIn("artifacts/figure10_validation/sweeps/", gitignore)
        self.assertIn("artifacts/figure10_validation/plots/", gitignore)
        self.assertIn("artifacts/figure10_validation/runs/*/runs/", gitignore)
        self.assertIn("paper_state_trace.csv", gitignore)
        self.assertIn("queue_trace.csv", gitignore)
        self.assertIn("mleo_candidate_latency_trace.csv", gitignore)

    def test_manual_sweep_commands_cover_all_groups(self):
        output = sweep_prep.main.__wrapped__ if hasattr(sweep_prep.main, "__wrapped__") else None
        self.assertIsNone(output)
        cfg = json.loads((ROOT / "artifacts" / "paper-contract-audit" / "phase5_3" / "figure10_sweep_workflow_status.json").read_text())
        self.assertEqual(cfg["sweep_groups"], ["task_arrival_probability", "private_cpu_ghz", "timeout_slots"])


if __name__ == "__main__":
    unittest.main()
