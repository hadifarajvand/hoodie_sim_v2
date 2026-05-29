from __future__ import annotations

import unittest

from src.analysis.full_hoodie_mechanism_fidelity_batch import build_full_hoodie_mechanism_fidelity_batch_report


class FullHOODIEMechanismFidelityBatchBehaviorEquivalenceTests(unittest.TestCase):
    def test_no_placeholder_claims(self) -> None:
        payload = build_full_hoodie_mechanism_fidelity_batch_report().to_dict()
        self.assertFalse(payload["remaining_blockers"])
        self.assertEqual(payload["recommended_next_feature"], "Feature 070 — Paper-Scale Experimental Reproduction Batch")


if __name__ == "__main__":
    unittest.main()

