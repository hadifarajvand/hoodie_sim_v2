from __future__ import annotations

import unittest

from src.environment.paper_pubsub import PubSubController, PubSubLoadSnapshot
from src.environment.paper_recovery import recover_load_snapshot


class PaperPubSubRecoveryTests(unittest.TestCase):
    def test_recovery_uses_previous_snapshot(self) -> None:
        controller = PubSubController(controller_id="ctrl-1", last_known_by_agent={})
        delivered = PubSubLoadSnapshot("1", "ctrl-1", 3, 4, {"queue": 1}, "delivered", "load-sharing_snapshot")
        controller.publish(delivered)
        missing = PubSubLoadSnapshot("1", "ctrl-1", 5, None, None, "delayed", "load-sharing_snapshot")
        recovered = recover_load_snapshot(current_snapshot=missing.load_snapshot, previous_snapshot=delivered.load_snapshot, previous_forecast_input=None)
        self.assertTrue(recovered.recovery_used)
        self.assertTrue(recovered.previous_load_snapshot_used)
        self.assertIsNotNone(recovered.recovered_load_snapshot)


if __name__ == "__main__":
    unittest.main()

