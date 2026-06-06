from __future__ import annotations

import unittest

import numpy as np

from environment.task import Task
from environment.task_generator import TaskGenerator


class Phase1TaskPropertyTests(unittest.TestCase):
    def setUp(self):
        Task.next_task_id = 1
        Task.trace_recorder = None

    def test_generated_task_has_hoodie_aligned_fields(self):
        generator = TaskGenerator(
            id=7,
            episode_time=10,
            task_arrive_probability=1.0,
            size_min=2.0,
            size_max=2.0,
            size_distribution="uniform",
            timeout_delay_min=20,
            timeout_delay_max=20,
            timeout_delay_distribution="uniform",
            priotiry_min=1,
            priotiry_max=1,
            priotiry_distribution="uniform",
            computational_density_min=0.297,
            computational_density_max=0.297,
            computational_density_distribution="uniform",
            drop_penalty_min=40,
            drop_penalty_max=40,
            drop_penalty_distribution="uniform",
        )
        np.random.seed(42)
        generator.reset()
        task = generator.step()
        self.assertIsNotNone(task)
        self.assertEqual(task.task_id, 1)
        self.assertEqual(task.source_node_id, 7)
        self.assertEqual(task.service_id, 7)
        self.assertEqual(task.input_data_size, 2.0)
        self.assertEqual(task.processing_density, 0.297)
        self.assertAlmostEqual(task.required_cpu_cycles, 2.0 * 0.297)
        self.assertEqual(task.arrival_time, 0)
        self.assertEqual(task.timeout, 20)
        self.assertEqual(task.absolute_deadline, 20)
        self.assertEqual(task.routing_metadata, {})

    def test_required_cpu_cycles_matches_paper_formula(self):
        task = Task(
            size=3.5,
            arrival_time=4,
            timeout_delay=20,
            computational_density=0.297,
            origin_server_id=2,
            input_data_size=3.5,
            processing_density=0.297,
            timeout=20,
            source_node_id=2,
        )
        self.assertAlmostEqual(task.required_cpu_cycles, 3.5 * 0.297)
        self.assertEqual(task.absolute_deadline, 24)

    def test_task_generation_reproducible_under_fixed_seed(self):
        generator_a = TaskGenerator(
            id=1,
            episode_time=10,
            task_arrive_probability=1.0,
            size_min=2.0,
            size_max=5.0,
            size_distribution="uniform",
            timeout_delay_min=20,
            timeout_delay_max=20,
            timeout_delay_distribution="uniform",
            priotiry_min=1,
            priotiry_max=1,
            priotiry_distribution="uniform",
            computational_density_min=0.297,
            computational_density_max=0.297,
            computational_density_distribution="uniform",
            drop_penalty_min=40,
            drop_penalty_max=40,
            drop_penalty_distribution="uniform",
        )
        generator_b = TaskGenerator(
            id=1,
            episode_time=10,
            task_arrive_probability=1.0,
            size_min=2.0,
            size_max=5.0,
            size_distribution="uniform",
            timeout_delay_min=20,
            timeout_delay_max=20,
            timeout_delay_distribution="uniform",
            priotiry_min=1,
            priotiry_max=1,
            priotiry_distribution="uniform",
            computational_density_min=0.297,
            computational_density_max=0.297,
            computational_density_distribution="uniform",
            drop_penalty_min=40,
            drop_penalty_max=40,
            drop_penalty_distribution="uniform",
        )
        np.random.seed(123)
        task_a = generator_a.step()
        Task.next_task_id = 1
        np.random.seed(123)
        task_b = generator_b.step()
        self.assertEqual(task_a.input_data_size, task_b.input_data_size)
        self.assertEqual(task_a.processing_density, task_b.processing_density)
        self.assertEqual(task_a.timeout, task_b.timeout)

    def test_invalid_fields_are_rejected(self):
        with self.assertRaises(ValueError):
            Task(
                size=0.0,
                arrival_time=0,
                timeout_delay=20,
                computational_density=0.297,
                input_data_size=0.0,
                processing_density=0.297,
                timeout=20,
            )
        with self.assertRaises(ValueError):
            Task(
                size=2.0,
                arrival_time=-1,
                timeout_delay=20,
                computational_density=0.297,
                input_data_size=2.0,
                processing_density=0.297,
                timeout=20,
            )
        with self.assertRaises(ValueError):
            Task(
                size=2.0,
                arrival_time=0,
                timeout_delay=-1,
                computational_density=0.297,
                input_data_size=2.0,
                processing_density=0.297,
                timeout=-1,
            )


if __name__ == "__main__":
    unittest.main()
