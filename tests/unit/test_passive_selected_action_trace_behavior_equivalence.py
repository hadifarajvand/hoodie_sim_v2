from __future__ import annotations

import unittest

from src.analysis.passive_selected_action_trace_repair import build_passive_selected_action_trace_repair_report


class PassiveSelectedActionTraceBehaviorEquivalenceTests(unittest.TestCase):
    def test_behavior_checks_are_unique(self) -> None:
        payload = build_passive_selected_action_trace_repair_report().to_dict()
        checks = payload["behavior_equivalence_summary"]["checks"]
        names = [check["name"] for check in checks]
        self.assertEqual(len(names), len(set(names)))

    def test_behavior_equivalence_passthrough(self) -> None:
        payload = build_passive_selected_action_trace_repair_report().to_dict()
        self.assertIn("behavior_equivalence_passed", payload)
        self.assertEqual(payload["behavior_equivalence_passed"], payload["behavior_equivalence_summary"]["passed"])
        self.assertEqual(payload["behavior_equivalence_summary"]["passed"], True)


if __name__ == "__main__":
    unittest.main()
