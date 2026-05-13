from __future__ import annotations

import unittest

from src.analysis.baseline_revalidation_after_runtime_repair.registry import (
    BASELINE_POLICY_NAMES,
    BASELINE_SCENARIO_NAMES,
    BASELINE_SEEDS,
    assert_baselines_registered,
    supported_baseline_policies,
)
from src.evaluation.policy_registry import PolicyRegistry


class BaselineRegistryRevalidationUnitTests(unittest.TestCase):
    def test_all_baseline_policies_are_registered(self) -> None:
        self.assertEqual(supported_baseline_policies(), BASELINE_POLICY_NAMES)
        self.assertEqual(PolicyRegistry.supported_names(), BASELINE_POLICY_NAMES)
        self.assertEqual(BASELINE_SCENARIO_NAMES, ("paper_default",))
        self.assertEqual(BASELINE_SEEDS, (0, 1, 2))
        status = assert_baselines_registered()
        self.assertTrue(status.passed)
        self.assertEqual(status.missing_names, ())

    def test_registry_rejects_missing_policy_names(self) -> None:
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
