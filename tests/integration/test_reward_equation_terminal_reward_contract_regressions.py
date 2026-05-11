from __future__ import annotations

import importlib
import unittest


class RewardEquationTerminalRewardContractRegressionIntegrationTest(unittest.TestCase):
    def test_existing_regression_modules_are_importable(self) -> None:
        modules = [
            "tests.integration.test_offload_instrumentation_trace_regression",
            "tests.integration.test_offload_instrumentation_no_behavior_change",
            "tests.unit.test_offload_instrumentation_feature019_regression",
            "tests.unit.test_offload_instrumentation_feature024_regression",
        ]
        for module_name in modules:
            module = importlib.import_module(module_name)
            self.assertIsNotNone(module)


if __name__ == "__main__":
    unittest.main()
