from __future__ import annotations

import json
import unittest

import numpy as np

from environment.environment import Environment
from environment.task import Task
from environment.task_generator import TaskGenerator
from environment.queues import ProcessingQueue
from main import _select_action_for_slot, _should_record_action_trace
from phase1_tracing import TraceRecorder


def _base_hyperparameters() -> dict[str, object]:
    with open("hyperparameters/hyperparameters.json") as f:
        return json.load(f)


class PaperFaithfulTaskCharacteristicTests(unittest.TestCase):
    def setUp(self):
        Task.next_task_id = 1
        Task.trace_recorder = None

    def test_no_task_arrival_does_not_call_choose_action(self):
        class _FailingPolicy:
            def choose_action(self, *args, **kwargs):
                raise AssertionError("choose_action should not be called when x_n_t=0")

        action, made = _select_action_for_slot(_FailingPolicy(), np.zeros(2), np.zeros(2), x_n_t=0)
        self.assertEqual(action, 0)
        self.assertFalse(made)

    def test_action_trace_decision_uses_decision_time_indicator_only(self):
        class _DummyPolicy:
            def choose_action(self, *args, **kwargs):
                return 1

        self.assertTrue(_should_record_action_trace(1))
        self.assertFalse(_should_record_action_trace(0))
        action, made = _select_action_for_slot(_DummyPolicy(), np.zeros(2), np.zeros(2), x_n_t=1)
        self.assertEqual(action, 1)
        self.assertTrue(made)

    def test_no_task_arrival_exposes_zero_indicator_in_paper_state(self):
        hp = _base_hyperparameters()
        trace = TraceRecorder(trace_level="summary")
        env = Environment(
            static_frequency=hp["static_frequency"],
            number_of_servers=hp["number_of_servers"],
            private_cpu_capacities=hp["private_cpu_capacities"],
            public_cpu_capacities=hp["public_cpu_capacities"],
            connection_matrix=hp["connection_matrix"],
            cloud_computational_capacity=hp["cloud_computational_capacity"],
            episode_time=1,
            task_arrive_probabilities=[0.0] * hp["number_of_servers"],
            task_size_mins=hp["task_size_mins"],
            task_size_maxs=hp["task_size_maxs"],
            task_size_distributions=hp["task_size_distributions"],
            timeout_delay_mins=hp["timeout_delay_mins"],
            timeout_delay_maxs=hp["timeout_delay_maxs"],
            timeout_delay_distributions=hp["timeout_delay_distributions"],
            priotiry_mins=hp["priotiry_mins"],
            priotiry_maxs=hp["priotiry_maxs"],
            priotiry_distributions=hp["priotiry_distributions"],
            computational_density_mins=hp["computational_density_mins"],
            computational_density_maxs=hp["computational_density_maxs"],
            computational_density_distributions=hp["computational_density_distributions"],
            drop_penalty_mins=hp["drop_penalty_mins"],
            drop_penalty_maxs=hp["drop_penalty_maxs"],
            drop_penalty_distributions=hp["drop_penalty_distributions"],
            trace_recorder=trace,
        )
        env.reset()
        state = env.get_paper_state(0)
        self.assertEqual(state["x_n_t"], 0)
        self.assertIsNone(state["task_id"])
        self.assertIsNone(state["eta_n"])

    def test_generated_task_size_belongs_to_h(self):
        generator = TaskGenerator(
            id=1,
            episode_time=3,
            task_arrive_probability=1.0,
            size_min=2.0,
            size_max=5.0,
            size_distribution="uniform",
            timeout_delay_min=20,
            timeout_delay_max=20,
            timeout_delay_distribution="constant",
            priotiry_min=1,
            priotiry_max=1,
            priotiry_distribution="constant",
            computational_density_min=0.297,
            computational_density_max=0.297,
            computational_density_distribution="constant",
            drop_penalty_min=40,
            drop_penalty_max=40,
            drop_penalty_distribution="constant",
        )
        np.random.seed(7)
        generator.reset()
        support = {round(v, 1) for v in np.arange(2.0, 5.0 + 0.0001, 0.1)}
        sizes = []
        for _ in range(3):
            task = generator.step()
            self.assertIsNotNone(task)
            sizes.append(round(float(task.input_data_size), 1))
        self.assertTrue(all(size in support for size in sizes))

    def test_deadline_slot_equals_arrival_plus_timeout_minus_one(self):
        task = Task(
            size=2.0,
            arrival_time=3,
            timeout_delay=10,
            computational_density=0.297,
            input_data_size=2.0,
            processing_density=0.297,
            timeout=10,
            source_node_id=2,
        )
        self.assertEqual(task.deadline_slot, 12)
        self.assertEqual(task.absolute_deadline, 12)

    def test_task_is_dropped_only_after_allowed_deadline_slot_has_passed(self):
        task = Task(
            size=2.0,
            arrival_time=3,
            timeout_delay=10,
            computational_density=0.297,
            input_data_size=2.0,
            processing_density=0.297,
            timeout=10,
            source_node_id=2,
        )
        queue = ProcessingQueue(1.0)
        queue.current_task = task
        queue.current_time = 12
        self.assertFalse(queue.current_task_is_timed_out())
        queue.current_time = 13
        self.assertTrue(queue.current_task_is_timed_out())
