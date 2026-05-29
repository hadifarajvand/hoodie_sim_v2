from __future__ import annotations

import unittest

from src.analysis.full_hoodie_mechanism_fidelity_batch import build_full_hoodie_mechanism_fidelity_batch_report


class FullHOODIEMechanismFidelityBatchSchemaTests(unittest.TestCase):
    def test_report_schema(self) -> None:
        payload = build_full_hoodie_mechanism_fidelity_batch_report().to_dict()
        self.assertEqual(payload["final_verdict"], "full_hoodie_mechanism_fidelity_batch_passed")
        self.assertEqual(payload["remaining_blockers"], [])
        self.assertTrue(payload["feature_068_verified"])


if __name__ == "__main__":
    unittest.main()

