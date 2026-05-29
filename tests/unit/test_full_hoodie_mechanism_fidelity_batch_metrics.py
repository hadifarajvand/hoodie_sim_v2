from __future__ import annotations

import unittest

from src.analysis.full_hoodie_mechanism_fidelity_batch import build_full_hoodie_mechanism_fidelity_batch_report


class FullHOODIEMechanismFidelityBatchMetricsTests(unittest.TestCase):
    def test_metric_flags(self) -> None:
        payload = build_full_hoodie_mechanism_fidelity_batch_report().to_dict()
        self.assertTrue(payload["neighbor_graph_operational"])
        self.assertTrue(payload["congestion_control_operational"])
        self.assertTrue(payload["delayed_reward_pipeline_operational"])
        self.assertTrue(payload["synchronization_barriers_operational"])
        self.assertTrue(payload["coordination_pipeline_operational"])


if __name__ == "__main__":
    unittest.main()

