from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venvmac" / "bin" / "python"


class Figure10ValidationRunbookTests(unittest.TestCase):
    def test_runbook_prints_baseline_and_full_commands_without_plots(self):
        result = subprocess.run(
            [str(PYTHON), "scripts/prepare_figure10_baseline_validation.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        stdout = result.stdout
        self.assertIn("RO,FLC,VO,HO,BCO,MLEO", stdout)
        self.assertNotIn("HOODIE,RO,FLC,VO,HO,BCO,MLEO", stdout.split("Baseline-only validation")[1].split("Tiny smoke run")[0])
        self.assertIn("--hoodie-checkpoint-dir <PATH_TO_TRAINED_HOODIE_CHECKPOINT_DIR>", stdout)
        self.assertIn("--strict-readiness", stdout)
        self.assertIn("git check-ignore -v artifacts/figure10_validation/runs/baseline-200-seed42/figure10_policy_metrics_raw.csv || true", stdout)
        self.assertNotIn("figure10_generate_figures.py", stdout)
        self.assertNotIn("savefig", stdout.lower())


if __name__ == "__main__":
    unittest.main()
