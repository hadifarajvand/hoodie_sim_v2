from __future__ import annotations

import unittest

from src.environment.traffic_config import TrafficConfig
from src.environment.traffic_observer import summarize_traffic
from src.evaluation.trace_protocol import EvaluationTrace, TraceTaskBlueprint


class ExecutionObserverTests(unittest.TestCase):
    def test_execution_summary_metrics_reflect_compute_budgets(self) -> None:
        config = TrafficConfig(
            scenario_name="paper_default",
            number_of_agents=2,
            episode_length=2,
            arrival_probability=1.0,
            slot_duration_seconds=0.1,
            timeout_slots=20,
            task_size_mbits_min=2.1,
            task_size_mbits_max=2.2,
            task_size_mbits_step=0.1,
            processing_density_gcycles_per_mbit=0.297,
        )
        trace = EvaluationTrace(
            trace_id="observer-trace",
            seed=17,
            tasks=(
                TraceTaskBlueprint(
                    task_id=1,
                    source_agent_id=1,
                    arrival_slot=0,
                    size=2.1,
                    processing_density=0.297,
                    timeout_length=20,
                    absolute_deadline_slot=20,
                ),
                TraceTaskBlueprint(
                    task_id=2,
                    source_agent_id=2,
                    arrival_slot=1,
                    size=2.2,
                    processing_density=0.297,
                    timeout_length=20,
                    absolute_deadline_slot=21,
                ),
            ),
            metadata={"mode": "deterministic_seed", "trace_id": "observer-trace", "seed": "17"},
        )

        summary = summarize_traffic(trace, config, seed=17)

        expected_total_cycles = (2.1 * 0.297) + (2.2 * 0.297)
        self.assertEqual(summary.scenario_name, "paper_default")
        self.assertEqual(summary.seed, 17)
        self.assertEqual(summary.total_arrivals, 2)
        self.assertAlmostEqual(summary.total_cycles_required, expected_total_cycles)
        self.assertAlmostEqual(summary.average_cycles_required, expected_total_cycles / 2.0)
        self.assertAlmostEqual(summary.max_cycles_required, 2.2 * 0.297)
        self.assertEqual(summary.arrivals_per_slot, (1, 1))
        self.assertEqual(summary.arrivals_per_agent, {"1": 1, "2": 1})


if __name__ == "__main__":
    unittest.main()
