from __future__ import annotations

import unittest

from src.environment.hoodie_synchronization import HoodieSynchronization


class HoodieSynchronizationTests(unittest.TestCase):
    def test_barrier_reaches_only_after_expected_agents(self) -> None:
        sync = HoodieSynchronization()
        first = sync.register_completion(decision_cycle=1, agent_id="1", expected_agent_count=2)
        second = sync.register_completion(decision_cycle=1, agent_id="2", expected_agent_count=2)
        self.assertFalse(first["barrier_reached"])
        self.assertTrue(second["barrier_reached"])


if __name__ == "__main__":
    unittest.main()

