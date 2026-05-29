from __future__ import annotations

import unittest

from src.analysis.full_hoodie_mechanism_fidelity_batch import build_full_hoodie_mechanism_fidelity_batch_report


class FullHOODIEMechanismFidelityBatchIntegrationTests(unittest.TestCase):
    def test_passes(self) -> None:
        payload = build_full_hoodie_mechanism_fidelity_batch_report().to_dict()
        self.assertEqual(payload["final_verdict"], "full_hoodie_mechanism_fidelity_batch_passed")
        self.assertEqual(payload["remaining_blockers"], [])


if __name__ == "__main__":
    unittest.main()

