from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

import numpy as np

from environment.environment import Environment
from environment.action_model import TopologyAdapter, TwoStageActionModel
from environment.matchmaker import Matchmaker
from environment.server import Server
from environment.queues import OffloadingQueue, ProcessingQueue
from environment.task import Task
from phase1_tracing import TraceRecorder


class Phase2ActionModelTests(unittest.TestCase):
    def setUp(self):
        self.topology = TopologyAdapter.from_connection_matrix(
            np.array(
                [
                    [0, 1, 0, 0],
                    [1, 0, 1, 0],
                    [0, 1, 0, 0],
                    [0, 0, 0, 0],
                ]
            ),
            cloud_node_id=4,
        )
        self.model = TwoStageActionModel(self.topology)
        self.matchmaker = Matchmaker(
            id=1,
            offloading_servers=np.array([0, 2]),
            cloud_id=4,
            topology=self.topology,
        )

    def test_local_action_is_valid(self):
        action = self.model.validate_explicit_choice(1, "local")
        self.assertTrue(action.is_valid)
        self.assertEqual(action.first_stage_decision, "local")
        self.assertEqual(action.destination_type, "local")
        self.assertIsNone(action.destination_node_id)
        self.assertFalse(action.cloud_target)
        self.assertEqual(action.d_n_1, 1)
        self.assertEqual(action.d_nk_2, {})
        self.assertEqual(action.paper_d_nk_2, (0, 0, 0, 0))
        self.assertEqual(action.dm2_timing, "not_applicable")
        self.assertFalse(action.requires_separate_dm2_at_offloading_queue_exit)

    def test_local_action_inserts_task_into_private_queue(self):
        queue = ProcessingQueue(1.0)
        task = Task(size=1.0, arrival_time=0, timeout_delay=10, computational_density=0.297, drop_penalty=40, origin_server_id=1, task_id=11)
        queue.add_task(task, current_time=0)
        self.assertFalse(queue.current_task.is_empty())
        self.assertEqual(queue.current_task.task_id, 11)

    def test_offload_action_does_not_insert_task_into_private_queue(self):
        server = Server(
            id=1,
            private_queue_computational_capacity=1,
            public_queues_computational_capacity=1,
            outbound_connections=np.array([1, 0, 1, 0]),
            inbound_connections=np.array([1, 0, 1, 0]),
            cloud_node_id=4,
            cloud_offloading_capacity=1,
        )
        task = Task(size=2.0, arrival_time=0, timeout_delay=10, computational_density=0.297, drop_penalty=40, origin_server_id=1, task_id=12)
        action = self.model.validate_explicit_choice(1, "offload")
        server.step(action, task, current_time=0)
        self.assertTrue(server.processing_queue.current_task.is_empty())
        self.assertFalse(server.offloading_queue.current_task.is_empty())

    def test_valid_horizontal_action(self):
        action = self.model.validate_explicit_choice(1, "offload", destination_node_id=2)
        self.assertTrue(action.is_valid)
        self.assertEqual(action.first_stage_decision, "offload")
        self.assertEqual(action.destination_type, "offload_pending")
        self.assertIsNone(action.destination_node_id)
        self.assertTrue(action.adjacency_allowed)
        self.assertFalse(action.cloud_target)
        self.assertEqual(action.d_n_1, 0)
        self.assertEqual(action.d_nk_2, {})
        self.assertEqual(action.paper_d_nk_2, (0, 0, 0, 0))
        self.assertEqual(action.dm2_timing, "offloading_queue_exit")
        self.assertTrue(action.requires_separate_dm2_at_offloading_queue_exit)

    def test_invalid_horizontal_action_to_non_neighbor(self):
        action = self.model.validate_explicit_choice(1, "offload", destination_node_id=3)
        self.assertFalse(action.is_valid)
        self.assertIn("DM2 destination", action.invalid_reason)
        self.assertFalse(action.adjacency_allowed)

    def test_invalid_self_offload(self):
        action = self.model.validate_explicit_choice(1, "offload", destination_node_id=1)
        self.assertFalse(action.is_valid)
        self.assertIn("self-offload", action.invalid_reason)

    def test_valid_vertical_cloud_action(self):
        action = self.model.validate_explicit_choice(1, "offload", destination_node_id=4)
        self.assertTrue(action.is_valid)
        self.assertEqual(action.destination_type, "offload_pending")
        self.assertIsNone(action.destination_node_id)
        self.assertFalse(action.cloud_target)
        self.assertEqual(action.d_n_1, 0)
        self.assertEqual(action.paper_d_nk_2, (0, 0, 0, 0))
        self.assertEqual(action.dm2_timing, "offloading_queue_exit")
        self.assertTrue(action.requires_separate_dm2_at_offloading_queue_exit)

    def test_invalid_missing_destination_for_offload(self):
        action = self.model.validate_explicit_choice(1, "offload")
        self.assertTrue(action.is_valid)
        self.assertEqual(action.destination_type, "offload_pending")
        self.assertIsNone(action.destination_node_id)
        self.assertEqual(action.d_n_1, 0)
        self.assertEqual(action.paper_d_nk_2, (0, 0, 0, 0))
        self.assertTrue(action.requires_separate_dm2_at_offloading_queue_exit)
        self.assertFalse(hasattr(action, "dm2_action_id"))

    def test_invalid_multiple_destinations_for_offload(self):
        action = self.model.validate_explicit_choice(1, "offload", destination_node_ids=[0, 2])
        self.assertFalse(action.is_valid)
        self.assertIn("at most one destination placeholder", action.invalid_reason)

    def test_action_space_generation(self):
        action_space = self.model.build_action_space(1)
        self.assertEqual(len(action_space), 2)
        self.assertEqual([a.destination_type for a in action_space], ["local", "offload_pending"])
        self.assertEqual([a.destination_node_id for a in action_space], [None, None])
        self.assertEqual(action_space[0].raw_action_id, 0)
        self.assertEqual(action_space[-1].raw_action_id, 1)
        self.assertTrue(all(len(a.paper_destination_nodes) == 4 for a in action_space))
        self.assertTrue(all(sum(a.paper_d_nk_2) == 0 for a in action_space))
        self.assertNotIn(1, [a.destination_node_id for a in action_space if a.destination_type == "offload_pending"])
        self.assertNotIn(3, [a.destination_node_id for a in action_space if a.destination_type == "offload_pending"])

    def test_paper_destination_vector_validation_rejects_multiple_active_destinations(self):
        action = self.model.validate_explicit_choice(1, "offload", destination_node_id=2)
        invalid = type(action)(
            **{**action.__dict__, "paper_d_nk_2": (1, 1, 0, 0)}
        )
        with self.assertRaisesRegex(ValueError, "all-zero paper destination vector"):
            self.model.validate_paper_action_contract(invalid)

    def test_legacy_compatibility_and_invalid_raw_action_rejection(self):
        self.assertEqual(self.matchmaker.match_action(1, 0), 1)
        self.assertEqual(self.matchmaker.match_action(1, 1), 1)
        with self.assertRaisesRegex(ValueError, "outside the valid action space"):
            self.matchmaker.match_action(1, 99)

    def test_trace_compatibility_exposes_new_action_fields(self):
        recorder = TraceRecorder()
        recorder.start_episode(0)
        recorder.note_action(
            episode_id=0,
            time=1,
            agent_id=1,
            x_n_t=1,
            observation_shape=[2, 3],
            selected_action=3,
            target_node=None,
            reward_received=1.0,
            first_stage_decision="offload",
            destination_node_id=None,
            destination_type="offload_pending",
            is_valid=True,
            invalid_reason=None,
            adjacency_allowed=True,
            cloud_target=False,
            d_n_1=0,
            d_nk_2={},
            paper_destination_nodes=(0, 2, 3, 4),
            paper_d_nk_2=(0, 0, 0, 0),
            dm2_timing="offloading_queue_exit",
            requires_separate_dm2_at_offloading_queue_exit=True,
            paper_u_n_t=2,
            dm2_pending=True,
        )
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "trace"
            recorder.export(trace_dir)
            with (trace_dir / "action_trace.csv").open(newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 1)
            row = rows[0]
            for field in [
                "raw_action_id",
                "first_stage_decision",
                "destination_node_id",
                "destination_type",
                "is_valid",
                "invalid_reason",
                "adjacency_allowed",
                "cloud_target",
                "d_n_1",
                "d_nk_2",
                "paper_destination_nodes",
                "paper_d_nk_2",
                "dm2_timing",
                "requires_separate_dm2_at_offloading_queue_exit",
                "paper_u_n_t",
                "dm2_pending",
            ]:
                self.assertIn(field, row)

    def test_paper_queue_arrival_count_records_local_and_offloaded_arrivals(self):
        local_recorder = TraceRecorder(trace_level="full")
        local_env = Environment(
            static_frequency=0,
            number_of_servers=2,
            private_cpu_capacities=[1, 1],
            public_cpu_capacities=[1, 1],
            connection_matrix=np.array([[0, 1], [1, 0]]),
            cloud_computational_capacity=1,
            episode_time=2,
            task_arrive_probabilities=[1.0, 1.0],
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
            trace_recorder=local_recorder,
        )
        local_env.reset()
        local_env.step(np.asarray([0, 0], dtype=int))
        self.assertEqual(local_env.last_paper_queue_arrivals, [1, 1, 0])
        local_rows = {(row.node_id, row.queue_type): row for row in local_recorder.queue_traces}
        self.assertEqual(local_rows[(0, "private")].paper_u_n_t, 1)
        self.assertEqual(local_rows[(1, "private")].paper_u_n_t, 1)

        offload_recorder = TraceRecorder(trace_level="full")
        offload_env = Environment(
            static_frequency=0,
            number_of_servers=2,
            private_cpu_capacities=[1, 1],
            public_cpu_capacities=[1, 1],
            connection_matrix=np.array([[0, 1], [1, 0]]),
            cloud_computational_capacity=1,
            episode_time=2,
            task_arrive_probabilities=[1.0, 0.0],
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
            trace_recorder=offload_recorder,
        )
        offload_env.reset()
        offload_env.step(np.asarray([1, 0], dtype=int))
        self.assertEqual(offload_env.last_paper_queue_arrivals, [0, 0, 0])
        offload_env.step(np.asarray([1, 0], dtype=int))
        self.assertEqual(offload_env.last_paper_queue_arrivals, [0, 1, 0])
        offload_rows = {(row.time, row.node_id, row.queue_type): row for row in offload_recorder.queue_traces}
        self.assertEqual(offload_rows[(1, 0, "private")].paper_u_n_t, 0)
        self.assertEqual(offload_rows[(1, 0, "offloading")].paper_u_n_t, 0)
        self.assertEqual(offload_rows[(2, 1, "public:0")].paper_u_n_t, 1)

        cloud_recorder = TraceRecorder(trace_level="full")
        cloud_env = Environment(
            static_frequency=0,
            number_of_servers=2,
            private_cpu_capacities=[1, 1],
            public_cpu_capacities=[1, 1],
            connection_matrix=np.array([[0, 0], [0, 0]]),
            cloud_computational_capacity=1,
            episode_time=3,
            task_arrive_probabilities=[1.0, 0.0],
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
            trace_recorder=cloud_recorder,
        )
        cloud_env.reset()
        cloud_env.step(np.asarray([1, 0], dtype=int))
        self.assertEqual(cloud_env.last_paper_queue_arrivals, [0, 0, 0])
        cloud_env.step(np.asarray([1, 0], dtype=int))
        self.assertEqual(cloud_env.last_paper_queue_arrivals, [0, 0, 1])
        cloud_rows = {(row.time, row.node_id, row.queue_type): row for row in cloud_recorder.queue_traces}
        self.assertEqual(cloud_rows[(2, 2, "cloud")].paper_u_n_t, 1)

    def test_private_queue_fifos_tasks_in_arrival_order(self):
        queue = ProcessingQueue(1.0)
        task_a = Task(size=1.0, arrival_time=0, timeout_delay=10, computational_density=0.297, drop_penalty=40, origin_server_id=1, task_id=21)
        task_b = Task(size=1.0, arrival_time=1, timeout_delay=10, computational_density=0.297, drop_penalty=40, origin_server_id=1, task_id=22)
        queue.add_task(task_a, current_time=0)
        queue.add_task(task_b, current_time=1)
        self.assertEqual([task.task_id for task in queue.get_pending_tasks()], [21, 22])

    def test_paper_w_priv_matches_latest_previous_completion_slot_formula(self):
        queue = ProcessingQueue(1.0)
        queue.paper_latest_private_scheduled_completion_slot = 10
        task = Task(size=1.0, arrival_time=5, timeout_delay=10, computational_density=0.297, drop_penalty=40, origin_server_id=1, task_id=31)
        queue.add_task(task, current_time=5)
        self.assertEqual(task.routing_metadata["paper_w_priv"], 6)
        self.assertEqual(task.routing_metadata["paper_psi_priv"], min(5 + 6 + 1 - 1, task.deadline_slot))

    def test_two_local_tasks_use_scheduled_private_completion_history(self):
        queue = ProcessingQueue(1.0)
        first = Task(size=1.0, arrival_time=0, timeout_delay=20, computational_density=0.297, drop_penalty=40, origin_server_id=1, task_id=32)
        second = Task(size=1.0, arrival_time=1, timeout_delay=20, computational_density=0.297, drop_penalty=40, origin_server_id=1, task_id=33)
        queue.add_task(first, current_time=0)
        first_scheduled = first.routing_metadata["paper_psi_priv"]
        queue.add_task(second, current_time=1)
        self.assertEqual(second.routing_metadata["paper_w_priv"], max(0, first_scheduled - 1 + 1))
        self.assertGreaterEqual(queue.paper_latest_private_scheduled_completion_slot, second.routing_metadata["paper_psi_priv"])

    def test_successful_private_task_records_paper_psi_priv_completion_slot(self):
        queue = ProcessingQueue(1.0)
        task = Task(size=1.0, arrival_time=0, timeout_delay=20, computational_density=0.297, drop_penalty=40, origin_server_id=1, task_id=41)
        queue.add_task(task, current_time=0)
        scheduled = queue.current_task.routing_metadata["paper_psi_priv"]
        scheduled_service = queue.current_task.routing_metadata["paper_private_service_time"]
        queue.step()
        self.assertEqual(queue.paper_latest_private_completion_slot, 1)
        self.assertEqual(queue.current_task.routing_metadata["paper_psi_priv"], scheduled)
        self.assertEqual(queue.current_task.routing_metadata["paper_private_final_status"], "completed")
        self.assertEqual(queue.current_task.routing_metadata["paper_private_queue_enter_time"], 0)
        self.assertEqual(queue.current_task.routing_metadata["paper_private_service_time"], scheduled_service)
        self.assertNotEqual(queue.current_task.routing_metadata["paper_private_service_time"], queue.current_task.service_time)

    def test_timed_out_private_task_records_deadline_slot_as_paper_psi_priv(self):
        queue = ProcessingQueue(1.0)
        task = Task(size=1.0, arrival_time=0, timeout_delay=1, computational_density=0.297, drop_penalty=40, origin_server_id=1, task_id=51)
        queue.add_task(task, current_time=0)
        queue.current_time = 1
        queue.step()
        self.assertEqual(queue.current_task.routing_metadata["paper_psi_priv"], queue.current_task.deadline_slot)
        self.assertEqual(queue.current_task.routing_metadata["paper_private_final_status"], "dropped")

    def test_no_private_task_at_slot_has_no_private_completion_slot(self):
        queue = ProcessingQueue(1.0)
        self.assertEqual(queue.paper_latest_private_completion_slot, -1)
        self.assertEqual(queue.paper_latest_private_scheduled_completion_slot, -1)

    def test_private_trace_contains_paper_private_fields(self):
        recorder = TraceRecorder(trace_level="full")
        recorder.start_episode(0)
        queue = ProcessingQueue(1.0)
        Task.trace_recorder = recorder
        task = Task(size=1.0, arrival_time=0, timeout_delay=3, computational_density=0.297, drop_penalty=40, origin_server_id=1, task_id=61)
        queue.add_task(task, current_time=0)
        queue.step()
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "trace"
            recorder.export(trace_dir)
            with (trace_dir / "task_lifecycle.csv").open(newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertTrue(rows)
            row = rows[0]
            for field in [
                "paper_w_priv",
                "paper_psi_priv",
                "paper_private_queue_enter_time",
                "paper_private_service_time",
                "paper_private_deadline_slot",
                "paper_private_final_status",
            ]:
                self.assertIn(field, row)

    def test_dm2_destination_is_resolved_at_offloading_queue_exit(self):
        server = Server(
            id=1,
            private_queue_computational_capacity=1,
            public_queues_computational_capacity=1,
            outbound_connections=np.array([1, 0, 1, 0]),
            inbound_connections=np.array([1, 0, 1, 0]),
            cloud_node_id=4,
            cloud_offloading_capacity=1,
        )
        task = Task(
            size=1.0,
            arrival_time=0,
            timeout_delay=10,
            priotiry=1,
            computational_density=0.297,
            drop_penalty=40,
            origin_server_id=1,
            task_id=99,
        )
        task.routing_metadata["dm2_action_id"] = 2
        task.routing_metadata["paper_destination_nodes"] = [0, 2, 4]
        task.routing_metadata["paper_d_nk_2"] = [0, 0, 0]
        task.routing_metadata["paper_destination_node_id"] = None
        task.routing_metadata["dm2_pending"] = True
        task.routing_metadata["dm2_timing"] = "offloading_queue_exit"
        task.routing_metadata["requires_separate_dm2_at_offloading_queue_exit"] = True

        server.offloading_queue.add_task(task, current_time=0)
        self.assertIsNone(server.offloading_queue.current_task.get_target_server_id())
        self.assertEqual(server.offloading_queue.current_task.paper_w_off, 0)
        self.assertEqual(server.offloading_queue.current_task.paper_off_final_status, "scheduled")
        transmitted_task, _ = server.offloading_queue.step()
        self.assertIsNotNone(transmitted_task)
        self.assertEqual(transmitted_task.get_target_server_id(), 0)
        self.assertEqual(transmitted_task.routing_metadata["paper_destination_node_id"], 0)
        self.assertEqual(transmitted_task.routing_metadata["paper_d_nk_2"], [1, 0, 0])
        self.assertEqual(transmitted_task.routing_metadata["dm2_timing"], "offloading_queue_exit")
        self.assertFalse(transmitted_task.routing_metadata["dm2_pending"])
        self.assertEqual(transmitted_task.routing_metadata["paper_off_rate_type"], "horizontal")
        self.assertEqual(transmitted_task.routing_metadata["paper_off_rate_value"], 1.0)
        self.assertEqual(transmitted_task.routing_metadata["paper_off_final_status"], "transmitted")
        self.assertEqual(transmitted_task.paper_psi_off, transmitted_task.routing_metadata["paper_psi_off"])

    def test_cloud_dm2_destination_counts_as_cloud_not_horizontal(self):
        env = Environment(
            static_frequency=0,
            number_of_servers=2,
            private_cpu_capacities=[1, 1],
            public_cpu_capacities=[1, 1],
            connection_matrix=np.array([[0, 1], [1, 0]]),
            cloud_computational_capacity=1,
            episode_time=2,
            task_arrive_probabilities=[1.0, 0.0],
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
        )
        env.reset()
        env.servers[0].offloading_queue.resolve_dm2_destination = lambda task: env.number_of_servers
        env.step(np.asarray([1, 0], dtype=int))
        env.step(np.asarray([1, 0], dtype=int))
        self.assertGreaterEqual(env.actions[0]["cloud"], 1)
        self.assertEqual(env.actions[0]["horisontal"], 0)

    def test_offloading_queue_enqueue_keeps_destination_pending_and_records_wait(self):
        queue = OffloadingQueue({0: 1.0, 2: 2.0, 4: 10.0})
        task = Task(
            size=2.0,
            arrival_time=0,
            timeout_delay=10,
            priotiry=1,
            computational_density=0.297,
            drop_penalty=40,
            origin_server_id=1,
            task_id=88,
        )
        task.routing_metadata["dm2_pending"] = True
        task.routing_metadata["paper_destination_node_id"] = None
        task.routing_metadata["paper_d_nk_2"] = [0, 0, 0]
        queue.add_task(task, current_time=3)
        self.assertIsNone(queue.current_task.get_target_server_id())
        self.assertIsNone(queue.current_task.routing_metadata["paper_destination_node_id"])
        self.assertTrue(queue.current_task.routing_metadata["dm2_pending"])
        self.assertEqual(queue.current_task.routing_metadata["paper_w_off"], 0)
        self.assertIsNone(queue.current_task.routing_metadata["paper_psi_off"])
        self.assertEqual(queue.paper_latest_offloading_scheduled_completion_slot, -1)
        self.assertEqual(queue.current_task.routing_metadata["paper_off_rate_type"], None)
        self.assertEqual(queue.current_task.routing_metadata["paper_off_final_status"], "scheduled")
        self.assertNotEqual(queue.current_task.routing_metadata["paper_off_final_status"], "transmitted")

    def test_offloading_queue_step_records_horizontal_and_vertical_rate_metadata(self):
        horizontal_queue = OffloadingQueue({0: 1.0, 2: 2.0, 4: 10.0})
        horizontal_task = Task(
            size=1.0,
            arrival_time=0,
            timeout_delay=10,
            priotiry=1,
            computational_density=0.297,
            drop_penalty=40,
            origin_server_id=1,
            task_id=89,
        )
        horizontal_task.routing_metadata["dm2_pending"] = True
        horizontal_task.routing_metadata["paper_destination_nodes"] = [0, 2, 4]
        horizontal_task.routing_metadata["paper_destination_node_id"] = None
        horizontal_task.routing_metadata["paper_d_nk_2"] = [0, 0, 0]
        horizontal_queue.add_task(horizontal_task, current_time=0)
        horizontal_queue.resolve_dm2_destination = lambda task: 2
        transmitted_task, _ = horizontal_queue.step()
        self.assertEqual(transmitted_task.routing_metadata["paper_off_rate_type"], "horizontal")
        self.assertEqual(transmitted_task.routing_metadata["paper_off_rate_value"], 2.0)
        self.assertEqual(transmitted_task.routing_metadata["paper_off_destination_node_id"], 2)
        self.assertEqual(transmitted_task.paper_off_final_status, "transmitted")

        vertical_queue = OffloadingQueue({0: 1.0, 2: 2.0, 4: 10.0})
        vertical_task = Task(
            size=1.0,
            arrival_time=0,
            timeout_delay=10,
            priotiry=1,
            computational_density=0.297,
            drop_penalty=40,
            origin_server_id=1,
            task_id=90,
        )
        vertical_task.routing_metadata["dm2_pending"] = True
        vertical_task.routing_metadata["paper_destination_nodes"] = [0, 2, 4]
        vertical_task.routing_metadata["paper_destination_node_id"] = None
        vertical_task.routing_metadata["paper_d_nk_2"] = [0, 0, 0]
        vertical_queue.add_task(vertical_task, current_time=0)
        vertical_queue.resolve_dm2_destination = lambda task: 4
        transmitted_task, _ = vertical_queue.step()
        self.assertEqual(transmitted_task.routing_metadata["paper_off_rate_type"], "vertical")
        self.assertEqual(transmitted_task.routing_metadata["paper_off_rate_value"], 10.0)
        self.assertEqual(transmitted_task.routing_metadata["paper_off_destination_node_id"], 4)
        self.assertNotEqual(transmitted_task.routing_metadata["paper_off_rate_value"], 1.0)

    def test_offloading_queue_updates_scheduled_history_immediately_after_dm2_resolution(self):
        queue = OffloadingQueue({0: 1.0, 2: 1.0, 4: 10.0})
        first = Task(
            size=3.0,
            arrival_time=0,
            timeout_delay=20,
            priotiry=1,
            computational_density=0.297,
            drop_penalty=40,
            origin_server_id=1,
            task_id=94,
        )
        first.routing_metadata["dm2_pending"] = True
        first.routing_metadata["paper_destination_nodes"] = [0, 2, 4]
        first.routing_metadata["paper_destination_node_id"] = None
        first.routing_metadata["paper_d_nk_2"] = [0, 0, 0]
        queue.add_task(first, current_time=0)
        queue.resolve_dm2_destination = lambda task: 2
        queue.step()
        first_psi = queue.current_task.routing_metadata["paper_psi_off"]
        self.assertIsNotNone(first_psi)
        self.assertEqual(queue.paper_latest_offloading_scheduled_completion_slot, first_psi)

        second = Task(
            size=1.0,
            arrival_time=1,
            timeout_delay=20,
            priotiry=1,
            computational_density=0.297,
            drop_penalty=40,
            origin_server_id=1,
            task_id=95,
        )
        second.routing_metadata["dm2_pending"] = True
        second.routing_metadata["paper_destination_nodes"] = [0, 2, 4]
        second.routing_metadata["paper_destination_node_id"] = None
        second.routing_metadata["paper_d_nk_2"] = [0, 0, 0]
        queue.add_task(second, current_time=1)
        self.assertEqual(second.routing_metadata["paper_w_off"], max(0, first_psi - 1 + 1))

    def test_offloading_queue_does_not_reupdate_scheduled_history_for_same_multi_slot_task(self):
        queue = OffloadingQueue({0: 1.0, 2: 1.0, 4: 10.0})
        task = Task(
            size=3.0,
            arrival_time=0,
            timeout_delay=20,
            priotiry=1,
            computational_density=0.297,
            drop_penalty=40,
            origin_server_id=1,
            task_id=96,
        )
        task.routing_metadata["dm2_pending"] = True
        task.routing_metadata["paper_destination_nodes"] = [0, 2, 4]
        task.routing_metadata["paper_destination_node_id"] = None
        task.routing_metadata["paper_d_nk_2"] = [0, 0, 0]
        queue.add_task(task, current_time=0)
        queue.resolve_dm2_destination = lambda task: 2
        queue.step()
        first_history = queue.paper_latest_offloading_scheduled_completion_slot
        queue.step()
        self.assertEqual(queue.paper_latest_offloading_scheduled_completion_slot, first_history)
        self.assertTrue(queue.current_task.paper_off_scheduled_history_recorded)

    def test_timed_out_offloading_task_records_deadline_slot_as_paper_psi_off(self):
        queue = OffloadingQueue({0: 1.0, 2: 2.0, 4: 10.0})
        task = Task(
            size=1.0,
            arrival_time=0,
            timeout_delay=1,
            priotiry=1,
            computational_density=0.297,
            drop_penalty=40,
            origin_server_id=1,
            task_id=91,
        )
        task.routing_metadata["dm2_pending"] = True
        queue.add_task(task, current_time=0)
        queue.current_time = 1
        queue.step()
        self.assertEqual(queue.current_task.routing_metadata["paper_psi_off"], queue.current_task.deadline_slot)
        self.assertEqual(queue.current_task.routing_metadata["paper_off_final_status"], "dropped")

    def test_offloading_queue_in_transmission_status_remains_until_transmit_completes(self):
        queue = OffloadingQueue({0: 1.0, 2: 1.0, 4: 10.0})
        task = Task(
            size=3.0,
            arrival_time=0,
            timeout_delay=20,
            priotiry=1,
            computational_density=0.297,
            drop_penalty=40,
            origin_server_id=1,
            task_id=97,
        )
        task.routing_metadata["dm2_pending"] = True
        task.routing_metadata["paper_destination_nodes"] = [0, 2, 4]
        task.routing_metadata["paper_destination_node_id"] = None
        task.routing_metadata["paper_d_nk_2"] = [0, 0, 0]
        queue.add_task(task, current_time=0)
        queue.resolve_dm2_destination = lambda task: 2
        transmited_task, _ = queue.step()
        self.assertIsNone(transmited_task)
        self.assertEqual(queue.current_task.paper_off_final_status, "in_transmission")

    def test_offloading_queue_transmission_completion_sets_transmitted_status_and_trace(self):
        recorder = TraceRecorder(trace_level="full")
        recorder.start_episode(0)
        queue = OffloadingQueue({0: 1.0, 2: 2.0, 4: 10.0})
        Task.trace_recorder = recorder
        task = Task(
            size=1.0,
            arrival_time=0,
            timeout_delay=10,
            priotiry=1,
            computational_density=0.297,
            drop_penalty=40,
            origin_server_id=1,
            task_id=98,
        )
        task.routing_metadata["dm2_pending"] = True
        task.routing_metadata["paper_destination_nodes"] = [0, 2, 4]
        task.routing_metadata["paper_destination_node_id"] = None
        task.routing_metadata["paper_d_nk_2"] = [0, 0, 0]
        queue.add_task(task, current_time=0)
        queue.resolve_dm2_destination = lambda task: 2
        transmitted_task, _ = queue.step()
        self.assertIsNotNone(transmitted_task)
        self.assertEqual(transmitted_task.paper_off_final_status, "transmitted")
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "trace"
            recorder.export(trace_dir)
            with (trace_dir / "task_lifecycle.csv").open(newline="") as f:
                rows = list(csv.DictReader(f))
            row = next(row for row in rows if row["task_id"] == "98")
            self.assertEqual(row["paper_off_final_status"], "transmitted")
            self.assertEqual(row["paper_psi_off"], str(transmitted_task.paper_psi_off))
            self.assertNotEqual(row["final_status"], "completed")

    def test_offloading_transmission_does_not_mark_task_completed_before_public_queue(self):
        recorder = TraceRecorder(trace_level="full")
        recorder.start_episode(0)
        Task.trace_recorder = recorder
        queue = OffloadingQueue({0: 1.0, 2: 2.0, 4: 10.0})
        task = Task(
            size=1.0,
            arrival_time=0,
            timeout_delay=10,
            priotiry=1,
            computational_density=0.297,
            drop_penalty=40,
            origin_server_id=1,
            task_id=99,
        )
        task.routing_metadata["dm2_pending"] = True
        task.routing_metadata["paper_destination_nodes"] = [0, 2, 4]
        task.routing_metadata["paper_destination_node_id"] = None
        task.routing_metadata["paper_d_nk_2"] = [0, 0, 0]
        queue.add_task(task, current_time=0)
        queue.resolve_dm2_destination = lambda task: 2
        transmitted_task, _ = queue.step()
        self.assertIsNotNone(transmitted_task)
        record = recorder.task_records[99]
        self.assertEqual(record.paper_off_final_status, "transmitted")
        self.assertEqual(record.final_status, "pending")
        events = recorder.resolve_delayed_reward_candidates(0)
        self.assertEqual(events, [])
        recorder.note_service_end(transmitted_task, episode_id=0, time=3, node_id=2, queue_type="public")
        events = recorder.resolve_delayed_reward_candidates(0)
        self.assertEqual(len(events), 1)
        self.assertEqual(recorder.task_records[99].final_status, "completed")

    def test_vertical_offloading_rate_is_configurable_in_environment(self):
        env = Environment(
            static_frequency=0,
            number_of_servers=2,
            private_cpu_capacities=[1, 1],
            public_cpu_capacities=[1, 1],
            connection_matrix=np.array([[0, 1], [1, 0]]),
            cloud_computational_capacity=3,
            episode_time=2,
            task_arrive_probabilities=[1.0, 0.0],
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
        self.assertEqual(env.vertical_offloading_rate, 7.0)
        self.assertEqual(env.servers[0].offloading_queue.vertical_offloading_rate, 7.0)

    def test_vertical_offload_uses_r_v_not_cloud_cpu_capacity(self):
        server = Server(
            id=1,
            private_queue_computational_capacity=1,
            public_queues_computational_capacity=1,
            outbound_connections=np.array([1, 0, 1, 0]),
            inbound_connections=np.array([1, 0, 1, 0]),
            cloud_node_id=4,
            cloud_offloading_capacity=3,
            vertical_offloading_rate=10.0,
        )
        task = Task(
            size=1.0,
            arrival_time=0,
            timeout_delay=10,
            priotiry=1,
            computational_density=0.297,
            drop_penalty=40,
            origin_server_id=1,
            task_id=93,
        )
        task.routing_metadata["dm2_pending"] = True
        task.routing_metadata["paper_destination_nodes"] = [0, 2, 4]
        task.routing_metadata["paper_destination_node_id"] = None
        task.routing_metadata["paper_d_nk_2"] = [0, 0, 0]
        server.offloading_queue.add_task(task, current_time=0)
        server.offloading_queue.resolve_dm2_destination = lambda task: 4
        transmitted_task, _ = server.offloading_queue.step()
        self.assertEqual(transmitted_task.routing_metadata["paper_off_rate_type"], "vertical")
        self.assertEqual(transmitted_task.routing_metadata["paper_off_rate_value"], 10.0)
        self.assertNotEqual(transmitted_task.routing_metadata["paper_off_rate_value"], 3)

    def test_offloading_trace_contains_paper_off_fields(self):
        recorder = TraceRecorder(trace_level="full")
        recorder.start_episode(0)
        queue = OffloadingQueue({0: 1.0, 2: 2.0, 4: 10.0})
        Task.trace_recorder = recorder
        task = Task(
            size=1.0,
            arrival_time=0,
            timeout_delay=10,
            priotiry=1,
            computational_density=0.297,
            drop_penalty=40,
            origin_server_id=1,
            task_id=92,
        )
        task.routing_metadata["dm2_pending"] = True
        task.routing_metadata["paper_destination_nodes"] = [0, 2, 4]
        queue.add_task(task, current_time=0)
        queue.resolve_dm2_destination = lambda task: 2
        queue.step()
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "trace"
            recorder.export(trace_dir)
            with (trace_dir / "task_lifecycle.csv").open(newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertTrue(rows)
            row = rows[0]
            for field in [
                "paper_w_off",
                "paper_psi_off",
                "paper_off_queue_enter_time",
                "paper_off_transmission_time",
                "paper_off_deadline_slot",
                "paper_off_rate_type",
                "paper_off_rate_value",
                "paper_off_destination_node_id",
                "paper_off_final_status",
            ]:
                self.assertIn(field, row)

    def test_offloading_queue_add_task_does_not_resolve_dm2_destination(self):
        server = Server(
            id=1,
            private_queue_computational_capacity=1,
            public_queues_computational_capacity=1,
            outbound_connections=np.array([1, 0, 1, 0]),
            inbound_connections=np.array([1, 0, 1, 0]),
            cloud_node_id=4,
            cloud_offloading_capacity=1,
        )
        task = Task(
            size=1.0,
            arrival_time=0,
            timeout_delay=10,
            priotiry=1,
            computational_density=0.297,
            drop_penalty=40,
            origin_server_id=1,
            task_id=100,
        )
        task.routing_metadata["dm2_pending"] = True
        task.routing_metadata["paper_destination_node_id"] = None
        task.routing_metadata["paper_d_nk_2"] = [0, 0, 0]

        called = {"resolve": 0}

        def _spy(task_arg):
            called["resolve"] += 1
            return 0

        server.offloading_queue.resolve_dm2_destination = _spy
        server.offloading_queue.add_task(task, current_time=0)
        self.assertEqual(called["resolve"], 0)
        self.assertIsNone(server.offloading_queue.current_task.get_target_server_id())
        self.assertIsNone(server.offloading_queue.current_task.routing_metadata["paper_destination_node_id"])
        self.assertTrue(server.offloading_queue.current_task.routing_metadata["dm2_pending"])
        self.assertEqual(server.offloading_queue.current_task.routing_metadata["paper_d_nk_2"], [0, 0, 0])

    def test_offloading_queue_step_resolves_dm2_destination(self):
        server = Server(
            id=1,
            private_queue_computational_capacity=1,
            public_queues_computational_capacity=1,
            outbound_connections=np.array([1, 0, 1, 0]),
            inbound_connections=np.array([1, 0, 1, 0]),
            cloud_node_id=4,
            cloud_offloading_capacity=1,
        )
        task = Task(
            size=1.0,
            arrival_time=0,
            timeout_delay=10,
            priotiry=1,
            computational_density=0.297,
            drop_penalty=40,
            origin_server_id=1,
            task_id=101,
        )
        task.routing_metadata["dm2_pending"] = True
        task.routing_metadata["paper_destination_node_id"] = None
        task.routing_metadata["paper_d_nk_2"] = [0, 0, 0]
        server.offloading_queue.resolve_dm2_destination = lambda task_arg: 2
        server.offloading_queue.add_task(task, current_time=0)
        transmitted_task, _ = server.offloading_queue.step()
        self.assertIsNotNone(transmitted_task.get_target_server_id())
        self.assertEqual(transmitted_task.routing_metadata["paper_destination_node_id"], 2)
        self.assertEqual(transmitted_task.routing_metadata["paper_d_nk_2"], [0, 1, 0])
        self.assertFalse(transmitted_task.routing_metadata["dm2_pending"])


if __name__ == "__main__":
    unittest.main()
