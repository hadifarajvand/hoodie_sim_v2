from __future__ import annotations

import ast
from pathlib import Path
import unittest

from src.reference_model import ReferenceLifecycleKernel


FORBIDDEN_NAMES = (
    "HoodieGymEnvironment",
    "SlotEngine",
    "src/environment",
    "src.policies",
    "src/training",
    "src.metrics",
    "artifacts/campaigns",
    "campaign runner",
    "environment",
    "policies",
    "training",
    "metrics",
    "campaigns",
)

FORBIDDEN_IMPORT_PREFIXES = (
    "environment",
    "src.environment",
    "policies",
    "src.policies",
    "training",
    "src.training",
    "metrics",
    "src.metrics",
    "campaign",
)


def _is_forbidden_module(module_name: str) -> bool:
    return any(
        module_name == forbidden or module_name.startswith(f"{forbidden}.")
        for forbidden in FORBIDDEN_IMPORT_PREFIXES
    )


class ReferenceTaskLifecycleKernelFlowTest(unittest.TestCase):
    def test_forbidden_module_helper(self) -> None:
        self.assertTrue(_is_forbidden_module("src.environment"))
        self.assertTrue(_is_forbidden_module("src.environment.slot_engine"))
        self.assertTrue(_is_forbidden_module("src.policies"))
        self.assertTrue(_is_forbidden_module("src.training.loop"))
        self.assertTrue(_is_forbidden_module("src.metrics.report"))
        self.assertTrue(_is_forbidden_module("environment"))
        self.assertFalse(_is_forbidden_module("src.reference_model"))
        self.assertFalse(_is_forbidden_module("dataclasses"))
        self.assertFalse(_is_forbidden_module("enum"))

    def test_repository_scope_guard(self) -> None:
        source_dir = Path("src/reference_model")
        source_files = sorted(source_dir.glob("*.py"))
        self.assertTrue(source_files, "reference model source files must exist")
        for path in source_files:
            text = path.read_text()
            for forbidden in FORBIDDEN_NAMES:
                self.assertNotIn(forbidden, text, f"forbidden reference found in {path}: {forbidden}")
            tree = ast.parse(text, filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertFalse(
                            _is_forbidden_module(alias.name),
                            f"forbidden import in {path}: {alias.name}",
                        )
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    self.assertFalse(
                        _is_forbidden_module(module),
                        f"forbidden from-import in {path}: {module}",
                    )
        kernel = ReferenceLifecycleKernel()
        self.assertIsNotNone(kernel)

    def test_imports_reference_model_without_simulator_modules(self) -> None:
        from src.reference_model import (
            ActionInput,
            ActionType,
            TaskIdentity,
            TaskWorkload,
        )

        identity = TaskIdentity("task-1", "ea-1", "ea-2")
        workload = TaskWorkload(10, 5, 2)
        action = ActionInput(ActionType.LOCAL_COMPUTE, "ea-1")
        kernel = ReferenceLifecycleKernel()
        ledger = kernel.process(identity, workload, action)
        self.assertEqual(ledger.task_id, "task-1")

    def test_timeout_and_reward_flow(self) -> None:
        from src.reference_model import ActionInput, ActionType, TaskIdentity, TaskWorkload

        identity = TaskIdentity("task-2", "ea-1", "cloud")
        workload = TaskWorkload(10, 2, 2)
        action = ActionInput(ActionType.LOCAL_COMPUTE, "ea-1")
        kernel = ReferenceLifecycleKernel()
        ledger = kernel.process_timeout(identity, workload, action)
        self.assertEqual(ledger.events[-1].event_type.value, "reward_emitted")
        self.assertEqual(ledger.events[-2].event_type.value, "dropped_timeout")


if __name__ == "__main__":
    unittest.main()
