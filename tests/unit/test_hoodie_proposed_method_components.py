from __future__ import annotations

import math
import unittest

from src.analysis.hoodie_proposed_method.action_model import HybridActionDecision
from src.analysis.hoodie_proposed_method.communication_model import EdgeControllerBroker, PubSubRecoveryMetadata
from src.analysis.hoodie_proposed_method.formulas import (
    compute_private_cost,
    compute_public_cost,
    compute_reward,
    paper_action_vector,
)
from src.analysis.hoodie_proposed_method.queue_model import OffloadingQueueTiming, PrivateQueueTiming, PublicQueueTiming
from src.analysis.hoodie_proposed_method.reward_model import private_cost, public_cost, reward_from_task_outcome


class HoodieProposedMethodComponentTests(unittest.TestCase):
    def test_action_vector_and_hybrid_action_decision_follow_the_paper_shape(self) -> None:
        self.assertEqual(paper_action_vector(1, "local"), (1, "local"))
        self.assertEqual(paper_action_vector(0, "horizontal"), (0, "horizontal"))
        self.assertEqual(paper_action_vector(False, "vertical"), (0, "vertical"))

        decision = HybridActionDecision(primary_decision=0, destination_kind="horizontal", destination_id="EA-2")
        self.assertTrue(decision.is_offloading)
        self.assertEqual(decision.to_vector(), (0, "horizontal"))

        with self.assertRaises(ValueError):
            HybridActionDecision(primary_decision=1, destination_kind="horizontal", destination_id="EA-2")

    def test_queue_timing_wrappers_compute_completion_and_delay_fields(self) -> None:
        private_timing = PrivateQueueTiming(
            arrival_slot=3,
            previous_max_completion_slot=4,
            processing_completion_slot=8,
            timeout_slot=7,
        )
        self.assertEqual(private_timing.waiting_start_slot, 5)
        self.assertEqual(private_timing.waiting_time, 2)
        self.assertEqual(private_timing.completion_slot, 7)
        self.assertTrue(private_timing.timed_out)

        offloading_timing = OffloadingQueueTiming(
            arrival_slot=3,
            transmission_completion_slot=6,
            timeout_slot=7,
            link_rate_kind="horizontal",
        )
        self.assertEqual(offloading_timing.completion_slot, 6)
        self.assertFalse(offloading_timing.timed_out)
        self.assertEqual(offloading_timing.transfer_delay, 3)

        public_timing = PublicQueueTiming(
            arrival_slot=3,
            destination_completion_slot=8,
            timeout_slot=7,
            destination_kind="edge_public",
        )
        self.assertEqual(public_timing.completion_slot, 7)
        self.assertTrue(public_timing.timed_out)
        self.assertEqual(public_timing.destination_delay, 4)

    def test_reward_helpers_and_pubsub_metadata_are_explicit(self) -> None:
        self.assertEqual(compute_private_cost(psi_priv=9, t=4), 6)
        self.assertEqual(compute_public_cost(destination_completion_slot=10, arrival_slot=4), 7)
        self.assertEqual(compute_reward(task_present=True, terminal_status="completed_private", phi_value=5, drop_cost=40), -5.0)
        self.assertEqual(compute_reward(task_present=True, terminal_status="dropped_timeout", phi_value=None, drop_cost=40), -40.0)
        self.assertTrue(math.isnan(compute_reward(task_present=False, terminal_status="pending", phi_value=None, drop_cost=40)))

        self.assertEqual(private_cost(9, 4), 6)
        self.assertEqual(public_cost(10, 4), 7)
        outcome = reward_from_task_outcome(task_present=True, terminal_status="completed_public", phi_value=7, drop_cost=12)
        self.assertEqual(outcome.reward_value, -7.0)

        broker = EdgeControllerBroker(broker_id="broker-1", managed_agent_ids=("EA-1", "EA-2"))
        metadata = broker.route("EA-1", "EA-2", slot=5, delayed=True, stale=False, recovery_window=2)
        self.assertIsInstance(metadata, PubSubRecoveryMetadata)
        self.assertEqual(metadata.to_dict()["broker_id"], "broker-1")
        self.assertEqual(metadata.recovery_window, 2)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
