from __future__ import annotations

import unittest

from src.analysis.distributed_multi_agent_hoodie_training_batch import build_distributed_multi_agent_hoodie_training_batch_report


class DistributedMultiAgentHOODIETrainingBatchBehaviorEquivalenceTests(unittest.TestCase):
    def test_no_single_agent_or_legacy_fallback(self) -> None:
        payload = build_distributed_multi_agent_hoodie_training_batch_report().to_dict()
        self.assertFalse(payload["migration_summary"]["legacy_three_action_family_only_detected"])
        self.assertFalse(payload["migration_summary"]["legacy_three_dimensional_state_only_detected"])
        self.assertFalse(payload["per_agent_model_summary"]["shared_network_instance_detected"])


if __name__ == "__main__":
    unittest.main()

