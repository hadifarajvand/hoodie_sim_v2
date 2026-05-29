from __future__ import annotations

import unittest

from src.environment.paper_timeout import build_timeout_contract


class PaperTimeoutSemanticsTests(unittest.TestCase):
    def test_deadline_uses_phi_minus_one(self) -> None:
        contract = build_timeout_contract(arrival_slot=10, timeout_phi=5, completion_slot=14)
        self.assertEqual(contract.deadline_slot, 14)
        self.assertFalse(contract.dropped_due_to_timeout)


if __name__ == "__main__":
    unittest.main()

