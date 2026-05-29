from __future__ import annotations

import unittest

from src.analysis.paper_baseline_suite_batch.runner import build_paper_baseline_suite_batch_report


class BaselinePolicyRegistryTests(unittest.TestCase):
    def test_registry_has_six_baselines(self) -> None:
        payload = build_paper_baseline_suite_batch_report().to_dict()
        self.assertEqual(payload["baseline_count"], 6)
        self.assertEqual(payload["implemented_baselines"], ["RO", "FLC", "VO", "HO", "BCO", "MLEO"])


if __name__ == "__main__":
    unittest.main()

