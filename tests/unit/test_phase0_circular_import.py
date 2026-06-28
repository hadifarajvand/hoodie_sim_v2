"""
Phase 0, Part 1: Verify circular import between gym_adapter and evaluation is fixed.

The circular import chain:
  gym_adapter.py → src.evaluation.trace_protocol
  → src.evaluation.__init__ → multi_agent_runner.py
  → src.environment.gym_adapter → (partially initialized → ImportError)

This test verifies both modules can be imported without circular import errors.
"""

import unittest


class TestCircularImportFix(unittest.TestCase):
    """Verify that the circular import between gym_adapter and evaluation is resolved."""

    def test_import_gym_adapter_directly(self) -> None:
        """Importing gym_adapter directly should not raise ImportError."""
        try:
            from src.environment.gym_adapter import HoodieGymEnvironment  # noqa: F811
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"ImportError importing gym_adapter: {e}")

    def test_import_evaluation_trace_protocol(self) -> None:
        """Importing evaluation.trace_protocol should not raise ImportError."""
        try:
            from src.evaluation.trace_protocol import EvaluationTrace  # noqa: F811
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"ImportError importing evaluation.trace_protocol: {e}")

    def test_import_evaluation_package(self) -> None:
        """Importing the evaluation package should not raise ImportError."""
        try:
            import src.evaluation  # noqa: F811
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"ImportError importing src.evaluation: {e}")

    def test_import_both_in_order(self) -> None:
        """Importing gym_adapter then evaluation should work."""
        try:
            from src.environment.gym_adapter import HoodieGymEnvironment  # noqa: F811
            from src.evaluation.trace_protocol import EvaluationTrace  # noqa: F811
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"ImportError importing both modules: {e}")

    def test_import_evaluation_then_gym_adapter(self) -> None:
        """Importing evaluation then gym_adapter should work."""
        try:
            from src.evaluation.trace_protocol import EvaluationTrace  # noqa: F811
            from src.environment.gym_adapter import HoodieGymEnvironment  # noqa: F811
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"ImportError importing evaluation then gym_adapter: {e}")


if __name__ == "__main__":
    unittest.main()
