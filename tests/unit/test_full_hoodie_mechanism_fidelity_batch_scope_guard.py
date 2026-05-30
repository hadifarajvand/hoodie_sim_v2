from __future__ import annotations

import unittest
from unittest import mock

from src.analysis.full_hoodie_mechanism_fidelity_batch import runner


class FullHoodieMechanismFidelityBatchScopeGuardTests(unittest.TestCase):
    def test_validate_scope_accepts_only_allowed_feature_paths(self) -> None:
        allowed = [
            "specs/069-full-hoodie-mechanism-fidelity-batch/spec.md",
            "src/analysis/full_hoodie_mechanism_fidelity_batch/report.py",
            "tests/unit/test_full_hoodie_mechanism_fidelity_batch_report.py",
        ]
        self.assertEqual(runner.validate_scope(allowed), allowed)

    def test_validate_scope_rejects_forbidden_paths(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "outside approved Feature 069 scope"):
            runner.validate_scope(
                [
                    "specs/069-full-hoodie-mechanism-fidelity-batch/spec.md",
                    "src/environment/gym_adapter.py",
                    "artifacts/generated/output.json",
                    "poetry.lock",
                ]
            )

    def test_run_blocks_dirty_forbidden_paths_from_git_state(self) -> None:
        with mock.patch.object(runner, "_tracked_paths", return_value=["src/agents/rogue.py"]):
            with mock.patch.object(runner, "_staged_paths", return_value=[]):
                with mock.patch.object(runner, "_diff_paths", return_value=[]):
                    with self.assertRaisesRegex(RuntimeError, "outside approved Feature 069 scope"):
                        runner.build_report()


if __name__ == "__main__":
    unittest.main()
