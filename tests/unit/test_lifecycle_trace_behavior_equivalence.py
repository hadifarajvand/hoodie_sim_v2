from __future__ import annotations

import unittest

from src.analysis.passive_runtime_lifecycle_trace_instrumentation import PassiveRuntimeLifecycleTraceConfig, run_passive_runtime_lifecycle_trace_instrumentation


class LifecycleTraceBehaviorEquivalenceTests(unittest.TestCase):
    def test_trace_enabled_does_not_change_rewards_or_finalized_tasks(self) -> None:
        report = run_passive_runtime_lifecycle_trace_instrumentation()
        checks = {item["name"]: item for item in report.behavior_equivalence_checks}
        self.assertTrue(checks["same_rewards"]["verified"])
        self.assertTrue(checks["same_finalized_tasks"]["verified"])
        self.assertTrue(checks["same_terminal_flags"]["verified"])
        self.assertTrue(checks["same_outcomes"]["verified"])

    def test_trace_enabled_does_not_change_action_masks_or_legality(self) -> None:
        report = run_passive_runtime_lifecycle_trace_instrumentation()
        checks = {item["name"]: item for item in report.behavior_equivalence_checks}
        self.assertTrue(checks["same_action_sequence"]["verified"])
        self.assertTrue(checks["same_queue_load"]["verified"])

    def test_behavior_equivalence_checks_are_deduplicated_by_name(self) -> None:
        report = run_passive_runtime_lifecycle_trace_instrumentation()
        names = [item["name"] for item in report.behavior_equivalence_checks]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(
            names,
            [
                "same_rewards",
                "same_finalized_tasks",
                "same_terminal_flags",
                "same_queue_load",
                "same_action_sequence",
                "same_outcomes",
            ],
        )

    def test_config_defaults_match_paper_default_runtime(self) -> None:
        config = PassiveRuntimeLifecycleTraceConfig()
        self.assertEqual(config.episode_length, 110)
        self.assertEqual(config.timeout_slots, 20)
        self.assertEqual(config.seeds, [0, 1, 2])
        self.assertEqual(config.strategies[0], "environment_default_policy_probe")


if __name__ == "__main__":
    unittest.main()
