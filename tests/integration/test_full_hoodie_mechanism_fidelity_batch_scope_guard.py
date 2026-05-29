from __future__ import annotations

import unittest
from unittest import mock

from src.analysis.full_hoodie_mechanism_fidelity_batch import build_full_hoodie_mechanism_fidelity_batch_report


class FullHOODIEMechanismFidelityBatchScopeGuardTests(unittest.TestCase):
    def test_prerequisite_gate_blocks_when_feature_068_missing(self) -> None:
        import src.analysis.full_hoodie_mechanism_fidelity_batch.runner as runner

        with mock.patch.object(runner, "_feature_068_verified", return_value=False):
            payload = build_full_hoodie_mechanism_fidelity_batch_report().to_dict()
        self.assertIn("feature_068_prerequisite_blocked", payload["remaining_blockers"])
        self.assertNotEqual(payload["final_verdict"], "full_hoodie_mechanism_fidelity_batch_passed")


if __name__ == "__main__":
    unittest.main()

