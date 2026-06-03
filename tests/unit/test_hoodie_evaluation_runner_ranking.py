from __future__ import annotations

import unittest

from src.analysis.hoodie_evaluation_runner.model import MetricRow
from src.analysis.hoodie_evaluation_runner.ranking import build_metric_rankings


class HoodieEvaluationRunnerRankingTests(unittest.TestCase):
    def test_metric_ranking_is_metric_by_metric_and_deterministic(self) -> None:
        rows = (
            MetricRow("ALPHA", "ALL", "ALL", "ALL", None, 5, 0, 0, 0, 0, 2.0, -10.0, -10.0, 0.5, 0.0, 0.0, 0.0, 0.8, 0.6, False),
            MetricRow("BETA", "ALL", "ALL", "ALL", None, 5, 0, 0, 0, 0, 1.5, -8.0, -8.0, 0.5, 0.0, 0.0, 0.0, 0.8, 0.6, False),
            MetricRow("GAMMA", "ALL", "ALL", "ALL", None, 4, 1, 0, 0, 0, 1.0, -6.0, -6.0, 0.4, 0.1, 0.0, 0.0, 0.7, 0.6, False),
        )
        rankings = build_metric_rankings(rows)
        self.assertEqual([row.policy for row in rankings["completion_rate"]], ["BETA", "ALPHA", "GAMMA"])
        self.assertEqual([row.policy for row in rankings["average_delay"]], ["GAMMA", "BETA", "ALPHA"])
        self.assertEqual([row.policy for row in rankings["total_reward"]], ["GAMMA", "BETA", "ALPHA"])
        self.assertEqual(rankings["completion_rate"][0].direction, "higher_is_better")
        self.assertEqual(rankings["average_delay"][0].direction, "lower_is_better")


if __name__ == "__main__":
    unittest.main()
