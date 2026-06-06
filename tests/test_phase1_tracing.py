from __future__ import annotations

import csv
import subprocess
import tempfile
import unittest
from pathlib import Path

from phase1_trace_validation import validate_trace_dir


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venvmac" / "bin" / "python"


class Phase1TracingTests(unittest.TestCase):
    def test_validation_rejects_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                validate_trace_dir(tmp)

    def test_one_epoch_run_emits_trace_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "traces"
            log_dir = Path(tmp) / "logs"
            cmd = [
                str(PYTHON),
                "main.py",
                "--epochs",
                "1",
                "--log_folder",
                str(log_dir),
                "--trace_output_dir",
                str(trace_dir),
            ]
            result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            expected = {
                "task_lifecycle.csv",
                "queue_trace.csv",
                "action_trace.csv",
                "episode_metrics.csv",
            }
            produced = {p.name for p in trace_dir.glob("*.csv")}
            self.assertTrue(expected.issubset(produced))
            errors = validate_trace_dir(trace_dir)
            self.assertEqual(errors, [], msg="\n".join(errors))


if __name__ == "__main__":
    unittest.main()

