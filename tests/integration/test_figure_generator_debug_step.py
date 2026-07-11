from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.figure_generator import generate_debug_step_figures


class FigureGeneratorDebugStepTests(unittest.TestCase):
    def test_generate_debug_step_figures_writes_all_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = generate_debug_step_figures(tmpdir)
            self.assertEqual(set(outputs), {"Figure 8", "Figure 9", "Figure 10", "Figure 11"})
            for figure_id, output_path in outputs.items():
                path = Path(output_path)
                self.assertTrue(path.exists(), f"missing output for {figure_id}")
                self.assertGreater(path.stat().st_size, 0, f"empty output for {figure_id}")


if __name__ == "__main__":
    unittest.main()
