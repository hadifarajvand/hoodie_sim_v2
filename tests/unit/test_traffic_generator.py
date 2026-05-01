from __future__ import annotations

import unittest
from unittest.mock import patch

from src.environment.traffic_config import TrafficConfig
from src.environment.traffic_generator import TrafficGenerator, generate_traffic_evaluation_trace
from src.evaluation.trace_protocol import EvaluationTrace


class TrafficGeneratorTests(unittest.TestCase):
    def _config(self) -> TrafficConfig:
        return TrafficConfig(
            scenario_name="paper_default",
            number_of_agents=3,
            episode_length=2,
            arrival_probability=1.0,
            slot_duration_seconds=0.1,
            timeout_slots=20,
            task_size_mbits_min=2.0,
            task_size_mbits_max=2.3,
            task_size_mbits_step=0.1,
            processing_density_gcycles_per_mbit=0.297,
        )

    def test_same_seed_same_config_produces_identical_traces(self) -> None:
        config = self._config()

        trace_one = TrafficGenerator.generate(config, seed=11)
        trace_two = TrafficGenerator.generate(config, seed=11)

        self.assertEqual(trace_one.evaluation_trace, trace_two.evaluation_trace)
        self.assertEqual(trace_one.to_trace_payload(), trace_two.to_trace_payload())

    def test_generated_task_order_and_fields_are_deterministic(self) -> None:
        config = self._config()
        trace = TrafficGenerator.generate(config, seed=7)

        self.assertEqual(len(trace.records), 6)
        self.assertEqual([blueprint.task_id for blueprint in trace.records], [1, 2, 3, 4, 5, 6])
        self.assertEqual(
            [(blueprint.arrival_slot, blueprint.source_agent_id, blueprint.task_id) for blueprint in trace.records],
            sorted((blueprint.arrival_slot, blueprint.source_agent_id, blueprint.task_id) for blueprint in trace.records),
        )
        for blueprint in trace.records:
            self.assertIsInstance(blueprint.size, float)
            self.assertIsInstance(blueprint.processing_density, float)
            self.assertGreaterEqual(blueprint.arrival_slot, 0)
            self.assertLess(blueprint.arrival_slot, config.episode_length)
            self.assertGreaterEqual(blueprint.source_agent_id, 1)
            self.assertLessEqual(blueprint.source_agent_id, config.number_of_agents)
            self.assertIn(blueprint.size, config.task_size_values)
            self.assertEqual(blueprint.timeout_length, config.timeout_slots)
            self.assertEqual(blueprint.absolute_deadline_slot, blueprint.arrival_slot + config.timeout_slots)

    def test_no_more_than_one_task_per_agent_per_slot_is_generated(self) -> None:
        config = self._config()
        trace = TrafficGenerator.generate(config, seed=13)

        seen: set[tuple[int, int]] = set()
        for blueprint in trace.records:
            key = (blueprint.arrival_slot, blueprint.source_agent_id)
            self.assertNotIn(key, seen)
            seen.add(key)

    def test_threshold_behavior_can_be_controlled(self) -> None:
        config = TrafficConfig(
            scenario_name="paper_default",
            number_of_agents=2,
            episode_length=1,
            arrival_probability=0.5,
            slot_duration_seconds=0.1,
            timeout_slots=20,
            task_size_mbits_min=2.0,
            task_size_mbits_max=2.1,
            task_size_mbits_step=0.1,
            processing_density_gcycles_per_mbit=0.297,
        )

        with patch("src.environment.traffic_generator.Random.random", side_effect=[0.4, 0.6]):
            trace = TrafficGenerator.generate(config, seed=5)

        self.assertEqual(len(trace.records), 1)
        self.assertEqual(trace.records[0].source_agent_id, 1)
        self.assertEqual(trace.records[0].arrival_slot, 0)
        self.assertEqual(trace.records[0].size, 2.1)
        self.assertEqual(trace.records[0].processing_density, 0.297)

    def test_generate_traffic_evaluation_trace_returns_evaluation_trace(self) -> None:
        config = self._config()
        trace = generate_traffic_evaluation_trace(config, seed=19)

        self.assertIsInstance(trace, EvaluationTrace)
        self.assertEqual(trace.metadata["scenario_name"], "paper_default")
        self.assertEqual(trace.metadata["seed"], "19")


if __name__ == "__main__":
    unittest.main()
