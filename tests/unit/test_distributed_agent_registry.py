from __future__ import annotations

import unittest

from src.analysis.distributed_multi_agent_hoodie_training import DistributedAgentRegistry


class DistributedAgentRegistryTests(unittest.TestCase):
    def test_registry_builds_one_agent_per_edge_agent(self) -> None:
        registry = DistributedAgentRegistry.build([str(i) for i in range(1, 21)])
        summary = registry.summary()
        self.assertEqual(summary["agent_count"], 20)
        self.assertFalse(summary["shared_network_instance_detected"])
        self.assertEqual(summary["optimizer_count"], 20)
        self.assertEqual(summary["replay_buffer_count"], 20)


if __name__ == "__main__":
    unittest.main()

