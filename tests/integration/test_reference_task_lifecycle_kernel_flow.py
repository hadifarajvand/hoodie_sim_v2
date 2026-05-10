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


class ReferenceTaskLifecycleKernelFlowTest(unittest.TestCase):
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
                        root = alias.name.split(".")[0]
                        self.assertNotIn(root, FORBIDDEN_IMPORT_PREFIXES, f"forbidden import in {path}: {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    root = module.split(".")[0]
                    self.assertNotIn(root, FORBIDDEN_IMPORT_PREFIXES, f"forbidden from-import in {path}: {module}")
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
