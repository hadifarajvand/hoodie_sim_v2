from __future__ import annotations

import unittest
from unittest import mock

from src.analysis.topology_timeout_reward_fidelity import runner


class TopologyTimeoutRewardFidelityScopeGuardTests(unittest.TestCase):
    def test_validate_scope_accepts_only_allowed_feature_paths(self) -> None:
        allowed = [
            "specs/070-topology-timeout-reward-fidelity/tasks.md",
            "src/analysis/topology_timeout_reward_fidelity/report.py",
            "tests/unit/test_topology_timeout_reward_fidelity_report.py",
        ]
        self.assertEqual(runner.validate_scope(allowed), allowed)

    def test_validate_scope_rejects_forbidden_paths(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "outside approved Feature 070 scope"):
            runner.validate_scope(
                [
                    "specs/070-topology-timeout-reward-fidelity/tasks.md",
                    "src/environment/gym_adapter.py",
                    "artifacts/generated/output.json",
                    "poetry.lock",
                ]
            )

    def test_build_report_blocks_dirty_forbidden_paths_from_git_state(self) -> None:
        with mock.patch.object(runner, "_tracked_paths", return_value=["src/agents/rogue.py"]):
            with mock.patch.object(runner, "_staged_paths", return_value=[]):
                with mock.patch.object(runner, "_diff_paths", return_value=[]):
                    with self.assertRaisesRegex(RuntimeError, "outside approved Feature 070 scope"):
                        runner.build_report()


if __name__ == "__main__":
    unittest.main()
