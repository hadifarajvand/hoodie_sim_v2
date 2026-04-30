from __future__ import annotations

import unittest

from src.evaluation.config import EvaluationConfig
from src.evaluation.runner import EvaluationRunner
from src.policies.flc import FullLocalComputingPolicy


class TraceReplayReproducibilityTests(unittest.TestCase):
    def test_identical_seed_replays_produce_identical_results(self) -> None:
        config = EvaluationConfig(policy_name="FLC", seed=23, trace_id="replay-trace", episode_count=3)
        runner_one = EvaluationRunner(policy=FullLocalComputingPolicy(), config=config)
        runner_two = EvaluationRunner(policy=FullLocalComputingPolicy(), config=config)

        self.assertEqual(runner_one.run(), runner_two.run())


if __name__ == "__main__":
    unittest.main()
