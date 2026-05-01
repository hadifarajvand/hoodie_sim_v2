from __future__ import annotations

import unittest

from src.environment.traffic_config import TrafficConfig
from src.environment.traffic_observer import TrafficObserver, summarize_traffic
from src.evaluation.trace_protocol import EvaluationTrace, TraceTaskBlueprint


class TrafficObserverTests(unittest.TestCase):
    def _config(self) -> TrafficConfig:
        return TrafficConfig(
            scenario_name="paper_default",
            number_of_agents=2,
            episode_length=4,
            arrival_probability=0.5,
            slot_duration_seconds=0.1,
            timeout_slots=20,
            task_size_mbits_min=2.0,
            task_size_mbits_max=5.0,
            task_size_mbits_step=0.1,
            processing_density_gcycles_per_mbit=0.297,
        )

    def _trace(self) -> EvaluationTrace:
        return EvaluationTrace(
            trace_id="known-trace",
            seed=31,
            tasks=(
                TraceTaskBlueprint(1, 1, 0, 2.0, 0.297, 20, 20),
                TraceTaskBlueprint(2, 2, 1, 2.1, 0.297, 20, 21),
                TraceTaskBlueprint(3, 1, 3, 2.2, 0.297, 20, 23),
            ),
            metadata={"mode": "traffic"},
        )

    def test_summary_counts_and_observed_probability(self) -> None:
        config = self._config()
        trace = self._trace()

        summary = summarize_traffic(trace, config, seed=31)

        self.assertEqual(summary.scenario_name, "paper_default")
        self.assertEqual(summary.seed, 31)
        self.assertEqual(summary.configured_arrival_probability, 0.5)
        self.assertEqual(summary.total_arrivals, 3)
        self.assertEqual(summary.arrivals_per_slot, (1, 1, 0, 1))
        self.assertEqual(summary.arrivals_per_agent, {"1": 2, "2": 1})
        self.assertEqual(summary.task_size_mbits_range, (2.0, 5.0))
        self.assertEqual(summary.observed_arrival_probability, 3 / (2 * 4))

    def test_rolling_window_summary_is_clipped_to_available_history(self) -> None:
        config = self._config()
        trace = self._trace()

        summary = TrafficObserver.summarize(trace, config, seed=31, window_slots=2)

        self.assertEqual(summary.total_arrivals, 1)
        self.assertEqual(summary.arrivals_per_slot, (0, 1))
        self.assertEqual(summary.arrivals_per_agent, {"1": 1, "2": 0})
        self.assertEqual(summary.observed_arrival_probability, 1 / (2 * 2))


if __name__ == "__main__":
    unittest.main()
