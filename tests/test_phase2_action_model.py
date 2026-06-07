from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

import numpy as np

from environment.action_model import TopologyAdapter, TwoStageActionModel
from environment.matchmaker import Matchmaker
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
        self.assertEqual(action.d_n_1, 0)
        self.assertEqual(action.d_nk_2, {})

    def test_valid_horizontal_action(self):
        action = self.model.validate_explicit_choice(1, "offload", destination_node_id=2)
        self.assertTrue(action.is_valid)
        self.assertEqual(action.first_stage_decision, "offload")
        self.assertEqual(action.destination_type, "horizontal_edge")
        self.assertEqual(action.destination_node_id, 2)
        self.assertTrue(action.adjacency_allowed)
        self.assertFalse(action.cloud_target)
        self.assertEqual(action.d_n_1, 1)
        self.assertEqual(action.d_nk_2, {2: 1})

    def test_invalid_horizontal_action_to_non_neighbor(self):
        action = self.model.validate_explicit_choice(1, "offload", destination_node_id=3)
        self.assertFalse(action.is_valid)
        self.assertIn("neighbor", action.invalid_reason)
        self.assertFalse(action.adjacency_allowed)

    def test_invalid_self_offload(self):
        action = self.model.validate_explicit_choice(1, "offload", destination_node_id=1)
        self.assertFalse(action.is_valid)
        self.assertIn("self-offload", action.invalid_reason)

    def test_valid_vertical_cloud_action(self):
        action = self.model.validate_explicit_choice(1, "offload", destination_node_id=4)
        self.assertTrue(action.is_valid)
        self.assertEqual(action.destination_type, "vertical_cloud")
        self.assertEqual(action.destination_node_id, 4)
        self.assertTrue(action.cloud_target)

    def test_invalid_missing_destination_for_offload(self):
        action = self.model.validate_explicit_choice(1, "offload")
        self.assertFalse(action.is_valid)
        self.assertIn("exactly one destination", action.invalid_reason)

    def test_invalid_multiple_destinations_for_offload(self):
        action = self.model.validate_explicit_choice(1, "offload", destination_node_ids=[0, 2])
        self.assertFalse(action.is_valid)
        self.assertIn("exactly one destination", action.invalid_reason)

    def test_action_space_generation(self):
        action_space = self.model.build_action_space(1)
        self.assertEqual(len(action_space), 4)
        self.assertEqual([a.destination_type for a in action_space], ["local", "horizontal_edge", "horizontal_edge", "vertical_cloud"])
        self.assertEqual([a.destination_node_id for a in action_space], [None, 0, 2, 4])
        self.assertEqual(action_space[0].raw_action_id, 0)
        self.assertEqual(action_space[-1].raw_action_id, 3)
        self.assertNotIn(1, [a.destination_node_id for a in action_space if a.destination_type == "horizontal_edge"])
        self.assertNotIn(3, [a.destination_node_id for a in action_space if a.destination_type == "horizontal_edge"])

    def test_legacy_compatibility_and_invalid_raw_action_rejection(self):
        self.assertEqual(self.matchmaker.match_action(1, 0), 1)
        self.assertEqual(self.matchmaker.match_action(1, 3), 4)
        with self.assertRaisesRegex(ValueError, "outside the valid action space"):
            self.matchmaker.match_action(1, 99)

    def test_trace_compatibility_exposes_new_action_fields(self):
        recorder = TraceRecorder()
        recorder.start_episode(0)
        recorder.note_action(
            episode_id=0,
            time=1,
            agent_id=1,
            observation_shape=[2, 3],
            selected_action=3,
            target_node=4,
            reward_received=1.0,
            first_stage_decision="offload",
            destination_node_id=4,
            destination_type="vertical_cloud",
            is_valid=True,
            invalid_reason=None,
            adjacency_allowed=True,
            cloud_target=True,
            d_n_1=1,
            d_nk_2={4: 1},
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
            ]:
                self.assertIn(field, row)


if __name__ == "__main__":
    unittest.main()
