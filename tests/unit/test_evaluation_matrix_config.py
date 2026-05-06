from __future__ import annotations

import unittest
from pathlib import Path

from src.evaluation.matrix_config import EvaluationMatrixConfig


class EvaluationMatrixConfigTests(unittest.TestCase):
    def test_config_accepts_valid_values(self) -> None:
        config = EvaluationMatrixConfig(
            policy_names=("FLC", "ADAPTIVE"),
            scenario_names=("paper_default", "moderate"),
            seeds=(1, 2),
            output_dir=Path("/tmp/matrix"),
            episode_length=10,
        )

        self.assertEqual(config.policy_names, ("FLC", "ADAPTIVE"))
        self.assertEqual(config.scenario_names, ("paper_default", "moderate"))
        self.assertEqual(config.seeds, (1, 2))
        self.assertEqual(config.output_dir, Path("/tmp/matrix"))
        self.assertEqual(config.ordering_key(), (("FLC", "ADAPTIVE"), ("paper_default", "moderate"), (1, 2)))

    def test_config_rejects_empty_lists(self) -> None:
        with self.assertRaises(ValueError):
            EvaluationMatrixConfig(policy_names=(), scenario_names=("paper_default",), seeds=(1,), output_dir=None)
        with self.assertRaises(ValueError):
            EvaluationMatrixConfig(policy_names=("FLC",), scenario_names=(), seeds=(1,), output_dir=None)
        with self.assertRaises(ValueError):
            EvaluationMatrixConfig(policy_names=("FLC",), scenario_names=("paper_default",), seeds=(), output_dir=None)

    def test_config_rejects_non_integer_seeds(self) -> None:
        with self.assertRaises(TypeError):
            EvaluationMatrixConfig(
                policy_names=("FLC",),
                scenario_names=("paper_default",),
                seeds=(1, 2.5),  # type: ignore[arg-type]
                output_dir=None,
            )

    def test_config_rejects_invalid_episode_length(self) -> None:
        with self.assertRaises(ValueError):
            EvaluationMatrixConfig(
                policy_names=("FLC",),
                scenario_names=("paper_default",),
                seeds=(1,),
                output_dir=None,
                episode_length=0,
            )


if __name__ == "__main__":
    unittest.main()
