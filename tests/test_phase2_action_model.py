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

    def test_invalid_multiple_destinations_for_offload(self):
        action = self.model.validate_explicit_choice(1, "offload", destination_node_ids=[0, 2])
        self.assertFalse(action.is_valid)
        self.assertIn("exactly one destination", action.invalid_reason)

    def test_action_space_generation(self):
        action_space = self.model.build_action_space(1)
        self.assertEqual(len(action_space), 4)
        self.assertEqual([a.destination_type for a in action_space], ["local", "offload_pending", "offload_pending", "offload_pending"])
        self.assertEqual([a.destination_node_id for a in action_space], [None, None, None, None])
        self.assertEqual(action_space[0].raw_action_id, 0)
        self.assertEqual(action_space[-1].raw_action_id, 3)
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
        self.assertEqual(self.matchmaker.match_action(1, 3), 1)
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
        transmitted_task, _ = server.offloading_queue.step()
        self.assertIsNotNone(transmitted_task)
        self.assertEqual(transmitted_task.get_target_server_id(), 2)
        self.assertEqual(transmitted_task.routing_metadata["paper_destination_node_id"], 2)
        self.assertEqual(transmitted_task.routing_metadata["paper_d_nk_2"], [0, 1, 0])
        self.assertEqual(transmitted_task.routing_metadata["dm2_timing"], "offloading_queue_exit")
        self.assertFalse(transmitted_task.routing_metadata["dm2_pending"])


if __name__ == "__main__":
    unittest.main()
