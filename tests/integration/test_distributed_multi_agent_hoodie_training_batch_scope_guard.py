from __future__ import annotations

import unittest

from src.analysis.distributed_multi_agent_hoodie_training_batch import build_distributed_multi_agent_hoodie_training_batch_report


class DistributedMultiAgentHOODIETrainingBatchScopeGuardTests(unittest.TestCase):
    def test_report_prohibits_claim_inflation(self) -> None:
        payload = build_distributed_multi_agent_hoodie_training_batch_report().to_dict()
        self.assertFalse(payload["migration_summary"]["paper_reproduction_claim"])
        self.assertFalse(payload["safety_summary"]["no_unsupported_superiority_claim"] is False)


if __name__ == "__main__":
    unittest.main()

