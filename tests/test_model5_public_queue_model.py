from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

import numpy as np

from environment.environment import Environment
from environment.queues import PublicQueueManager
from environment.task import Task
from phase1_tracing import TraceRecorder


class Model5PublicQueueModelTests(unittest.TestCase):
    def test_public_enqueue_records_paper_u_pub_and_queue_metadata(self):
        manager = PublicQueueManager(id=0, computational_capacity=4.0, supporting_servers=np.array([1]))
        task = Task(
            size=3.0,
            arrival_time=2,
            timeout_delay=10,
            computational_density=0.297,
            drop_penalty=40,
            origin_server_id=1,
            target_server_id=0,
            task_id=77,
        )
        manager.add_tasks([task], current_time=5)

        queued = manager.public_queues[1].current_task
        self.assertEqual(queued.paper_u_pub, 77)
        self.assertEqual(queued.paper_eta_pub, 3.0)
        self.assertEqual(queued.paper_public_queue_source_id, 1)
        self.assertEqual(queued.paper_public_queue_node_id, 0)
        self.assertEqual(queued.paper_public_queue_enter_time, 5)
        self.assertEqual(queued.paper_l_pub_before, 0.0)
        self.assertEqual(queued.paper_l_pub_after, 3.0)
        self.assertEqual(queued.paper_l_pub, 3.0)
        self.assertEqual(queued.paper_m_pub, 0.0)
        self.assertIsNone(queued.paper_psi_tilde_pub)
        self.assertEqual(queued.paper_public_final_status, "scheduled")

    def test_public_cpu_is_equally_shared_across_active_queues(self):
        recorder = TraceRecorder(trace_level="full")
        recorder.start_episode(0)
        Task.trace_recorder = recorder
        manager = PublicQueueManager(id=0, computational_capacity=4.0, supporting_servers=np.array([1, 2]))
        first = Task(size=10.0, arrival_time=0, timeout_delay=10, computational_density=0.297, drop_penalty=40, origin_server_id=1, target_server_id=0, task_id=81)
        second = Task(size=10.0, arrival_time=0, timeout_delay=10, computational_density=0.297, drop_penalty=40, origin_server_id=2, target_server_id=0, task_id=82)
        manager.add_tasks([first, second], current_time=0)

        manager.step()
        self.assertEqual(manager.public_queues[1].current_task.paper_public_active_queue_count, 2)
        self.assertEqual(manager.public_queues[2].current_task.paper_public_active_queue_count, 2)
        self.assertEqual(manager.public_queues[1].current_task.paper_public_service_capacity_share, 2.0)
        self.assertEqual(manager.public_queues[2].current_task.paper_public_service_capacity_share, 2.0)

    def test_public_timeout_sets_deadline_slot_and_exports_paper_fields(self):
        recorder = TraceRecorder(trace_level="full")
        recorder.start_episode(0)
        Task.trace_recorder = recorder
        manager = PublicQueueManager(id=0, computational_capacity=1.0, supporting_servers=np.array([1]))
        task = Task(
            size=1.0,
            arrival_time=0,
            timeout_delay=1,
            computational_density=0.297,
            drop_penalty=40,
            origin_server_id=1,
            target_server_id=0,
            task_id=83,
        )
        manager.add_tasks([task], current_time=0)
        manager.public_queues[1].current_time = 0
        manager.public_queues[1].get_first_non_empty_element()

        record = recorder.task_records[83]
        self.assertEqual(record.paper_m_pub, 1.0)
        self.assertEqual(record.paper_psi_pub, record.paper_public_deadline_slot)
        self.assertEqual(record.paper_public_final_status, "dropped")

        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "trace"
            recorder.export(trace_dir)
            with (trace_dir / "task_lifecycle.csv").open(newline="") as f:
                rows = list(csv.DictReader(f))
            row = next(row for row in rows if row["task_id"] == "83")
            self.assertEqual(row["paper_public_final_status"], "dropped")
            self.assertEqual(row["paper_psi_pub"], row["paper_public_deadline_slot"])
            self.assertIn("paper_m_pub", row)

    def test_public_state_vector_uses_zero_for_unsupported_queues(self):
        env = Environment(
            static_frequency=0,
            number_of_servers=2,
            private_cpu_capacities=[1, 1],
            public_cpu_capacities=[1, 1],
            connection_matrix=np.array([[0, 1], [1, 0]]),
            cloud_computational_capacity=3,
            episode_time=1,
            task_arrive_probabilities=[0.0, 0.0],
            task_size_mins=[1.0, 1.0],
            task_size_maxs=[1.0, 1.0],
            task_size_distributions=["constant", "constant"],
            timeout_delay_mins=[10, 10],
            timeout_delay_maxs=[10, 10],
            timeout_delay_distributions=["constant", "constant"],
            priotiry_mins=[1, 1],
            priotiry_maxs=[1, 1],
            priotiry_distributions=["constant", "constant"],
            computational_density_mins=[0.297, 0.297],
            computational_density_maxs=[0.297, 0.297],
            computational_density_distributions=["constant", "constant"],
            drop_penalty_mins=[40, 40],
            drop_penalty_maxs=[40, 40],
            drop_penalty_distributions=["constant", "constant"],
            vertical_offloading_rate=7.0,
        )
        state = env.get_paper_state(0)
        self.assertFalse(np.isnan(state["l_pub_n_prev"]).any())
        self.assertTrue(np.all(state["l_pub_n_prev"] == 0))
        self.assertFalse(np.isnan(state["L_t"]).any())

    def test_cloud_public_queue_traces_are_recorded_per_source(self):
        recorder = TraceRecorder(trace_level="full")
        recorder.start_episode(0)
        Task.trace_recorder = recorder
        env = Environment(
            static_frequency=0,
            number_of_servers=2,
            private_cpu_capacities=[1, 1],
            public_cpu_capacities=[1, 1],
            connection_matrix=np.array([[0, 1], [1, 0]]),
            cloud_computational_capacity=3,
            episode_time=1,
            task_arrive_probabilities=[0.0, 0.0],
            task_size_mins=[1.0, 1.0],
            task_size_maxs=[1.0, 1.0],
            task_size_distributions=["constant", "constant"],
            timeout_delay_mins=[10, 10],
            timeout_delay_maxs=[10, 10],
            timeout_delay_distributions=["constant", "constant"],
            priotiry_mins=[1, 1],
            priotiry_maxs=[1, 1],
            priotiry_distributions=["constant", "constant"],
            computational_density_mins=[0.297, 0.297],
            computational_density_maxs=[0.297, 0.297],
            computational_density_distributions=["constant", "constant"],
            drop_penalty_mins=[40, 40],
            drop_penalty_maxs=[40, 40],
            drop_penalty_distributions=["constant", "constant"],
            vertical_offloading_rate=7.0,
            trace_recorder=recorder,
        )
        cloud_task_a = Task(size=1.0, arrival_time=0, timeout_delay=10, computational_density=0.297, drop_penalty=40, origin_server_id=0, target_server_id=2, task_id=90)
        cloud_task_b = Task(size=1.0, arrival_time=0, timeout_delay=10, computational_density=0.297, drop_penalty=40, origin_server_id=1, target_server_id=2, task_id=91)
        env.cloud.add_offloaded_tasks([cloud_task_a, cloud_task_b], current_time=0)
        env._record_queue_traces()
        cloud_rows = [row for row in recorder.queue_traces if row.queue_type.startswith("cloud_public:")]
        self.assertTrue(cloud_rows)
        self.assertEqual({row.paper_public_queue_source_id for row in cloud_rows}, {0, 1})
        self.assertTrue(all(row.paper_public_queue_node_id == 2 for row in cloud_rows))


if __name__ == "__main__":
    unittest.main()
