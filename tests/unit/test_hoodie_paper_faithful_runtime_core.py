from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from src.analysis.hoodie_paper_faithful_runtime import (
    EpisodeConfig,
    generate_runtime_artifacts,
    horizontal_test_policy,
    local_test_policy,
    mixed_test_policy,
    vertical_test_policy,
    validate_runtime_artifacts,
)
from src.analysis.hoodie_paper_faithful_runtime.runtime import run_episode


class HoodiePaperFaithfulRuntimeCoreUnitTests(unittest.TestCase):
    def test_episode_slot_split(self) -> None:
        config = EpisodeConfig.default()
        self.assertEqual(config.slot_count, 110)
        self.assertEqual(config.action_slot_count, 100)
        self.assertEqual(config.drain_slot_count, 10)

    def test_bernoulli_arrival_opportunities(self) -> None:
        config = EpisodeConfig.default()
        result = run_episode(config, "mixed_test_policy", mixed_test_policy)
        self.assertEqual(result["arrival_opportunities"], 2000)
        self.assertGreater(len(result["tasks"]), 0)

    def test_task_record_fields(self) -> None:
        config = EpisodeConfig.default()
        result = run_episode(config, "local_test_policy", local_test_policy)
        task = next(iter(result["tasks"].values()))
        self.assertIsNotNone(task.task_id)
        self.assertIsNotNone(task.source_ea_id)
        self.assertIsNotNone(task.arrival_slot)
        self.assertIsNotNone(task.size_mbits)
        self.assertIsNotNone(task.deadline_slot)
        self.assertIn(task.status, {"completed", "dropped_timeout", "unresolved"})
        self.assertTrue(hasattr(task, "offloading_queue_exit_slot"))

    def test_private_queue_completion_vs_timeout(self) -> None:
        config = EpisodeConfig.default()
        result = run_episode(config, "local_test_policy", local_test_policy)
        statuses = {task.status for task in result["tasks"].values()}
        self.assertIn("completed", statuses)
        self.assertIn("dropped_timeout", statuses)

    def test_offloading_queue_transmission_vs_timeout(self) -> None:
        config = EpisodeConfig.default()
        result = run_episode(config, "vertical_test_policy", vertical_test_policy)
        statuses = {task.status for task in result["tasks"].values()}
        self.assertIn("completed", statuses)
        self.assertIn("dropped_timeout", statuses)

    def test_public_queue_cpu_sharing(self) -> None:
        config = EpisodeConfig.default()
        result = run_episode(config, "mixed_test_policy", mixed_test_policy)
        active_sets = result["active_sets"]
        self.assertTrue(any(aset.active_public_queue_count > 0 for aset in active_sets))
        self.assertTrue(any(aset.active_public_queue_count > 1 for aset in active_sets))
        self.assertTrue(result["public_cpu_used"])

    def test_delayed_reward_collection(self) -> None:
        config = EpisodeConfig.default()
        result = run_episode(config, "mixed_test_policy", mixed_test_policy)
        self.assertTrue(result["reward_events"])
        self.assertTrue(all(event.reward_collection_slot >= event.original_action_slot for event in result["reward_events"]))
        self.assertTrue(any(event.reward_collection_slot > event.original_action_slot for event in result["reward_events"]))

    def test_load_history_matrix_shape(self) -> None:
        config = EpisodeConfig.default()
        result = run_episode(config, "mixed_test_policy", mixed_test_policy)
        snapshot = result["state_snapshots"][0]
        self.assertEqual(snapshot.load_history_matrix_shape, (10, 21))

    def test_runtime_artifact_generation_and_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            report = generate_runtime_artifacts(output_dir)
            self.assertTrue((output_dir / "runtime_config.json").exists())
            self.assertTrue((output_dir / "reward_events.json").exists())
            self.assertTrue(report["public_queue_cpu_sharing_active"])
            self.assertTrue(report["completion_drop_status_separated"])
            result = validate_runtime_artifacts(output_dir)
            self.assertTrue(result["passed"])

    def test_policy_paths_exist(self) -> None:
        config = EpisodeConfig.default()
        task = run_episode(config, "local_test_policy", local_test_policy)["tasks"][1]
        self.assertEqual(task.path_type, "local")
        task = run_episode(config, "horizontal_test_policy", horizontal_test_policy)["tasks"][1]
        self.assertEqual(task.path_type, "horizontal")
        task = run_episode(config, "vertical_test_policy", vertical_test_policy)["tasks"][1]
        self.assertEqual(task.path_type, "vertical")


if __name__ == "__main__":
    unittest.main()
