from __future__ import annotations

from pathlib import Path
import unittest


FEATURE_DIR = Path("specs/085-hoodie-paper-baseline-fidelity-audit")


class HoodieRuntimeEvaluationRunnerAuditMatrixTests(unittest.TestCase):
    def test_baseline_mapping_matrix_uses_mleo_and_retires_mqo(self) -> None:
        matrix = (FEATURE_DIR / "baseline-mapping-matrix.md").read_text(encoding="utf-8")
        self.assertIn("Minimum Latency Estimate Offloader", matrix)
        self.assertIn("`MLEO`", matrix)
        self.assertIn("Legacy `MQO` label", matrix)
        self.assertIn("retired", matrix.lower())

    def test_formula_mapping_matrix_covers_required_rows(self) -> None:
        matrix = (FEATURE_DIR / "formula-mapping-matrix.md").read_text(encoding="utf-8")
        for needle in (
            "task_completion_delay",
            "task_drop_ratio",
            "reward calculation",
            "vertical offload delay",
            "horizontal offload delay",
            "DQN interface",
            "DDQN interface",
            "Dueling interface",
            "LSTM interface",
        ):
            self.assertIn(needle, matrix)


if __name__ == "__main__":
    unittest.main()
