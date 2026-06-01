from __future__ import annotations

import unittest

from src.analysis.hoodie_proposed_fidelity.config import REQUIRED_COMPONENT_IDS
from src.analysis.hoodie_proposed_fidelity.implementation_scan import observation_by_component_id, scan_current_implementation


class HoodieProposedFidelityImplementationScanTests(unittest.TestCase):
    def test_every_component_has_current_implementation_and_status(self) -> None:
        observations = scan_current_implementation()
        self.assertEqual(len(observations), 19)
        self.assertEqual({observation.component_id for observation in observations}, set(REQUIRED_COMPONENT_IDS))
        for observation in observations:
            self.assertTrue(observation.current_implementation)
            self.assertTrue(observation.implementation_reference)
            self.assertTrue(observation.status)
            self.assertTrue(observation.gap)

    def test_missing_or_partial_components_have_repair_actions(self) -> None:
        observations = {obs.component_id: obs for obs in scan_current_implementation()}
        for component_id in ("system_model", "architecture", "edge_agents", "state_space", "reward_cost", "private_queue", "offloading_queue", "public_queue", "dqn_training", "double_dqn", "dueling_dqn", "lstm_forecast", "replay_memory", "inference", "pubsub_recovery", "metrics", "simulation_parameters"):
            self.assertNotEqual(observations[component_id].status, "implemented")
            self.assertTrue(observations[component_id].required_repair)

    def test_action_space_is_the_only_implemented_component(self) -> None:
        implemented = [observation.component_id for observation in scan_current_implementation() if observation.status == "implemented"]
        self.assertEqual(implemented, ["action_space"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
