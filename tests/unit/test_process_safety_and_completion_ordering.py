from __future__ import annotations

import os
from pathlib import Path
import unittest
from unittest.mock import patch

from src.hoodie.experiments.process_safety import assert_safe_owned_child_pid, clear_owned_child_registry, record_owned_child_pid
from src.hoodie.experiments.production_campaign import validate_training_outputs_before_completion, validate_completed_training_job, validate_evaluation_outputs_before_completion, validate_completed_evaluation_job
from src.hoodie.experiments.job_matrix import ProductionJobRow


class ProcessSafetyTests(unittest.TestCase):
    def tearDown(self) -> None:
        clear_owned_child_registry()

    def test_rejects_current_parent_and_unrecorded_pid(self) -> None:
        current = os.getpid()
        parent = os.getppid()
        with self.assertRaises(ValueError):
            assert_safe_owned_child_pid(current, "worker")
        with self.assertRaises(ValueError):
            assert_safe_owned_child_pid(parent, "worker")
        with self.assertRaises(ValueError):
            assert_safe_owned_child_pid(999999, "worker")

    def test_rejects_bad_command_and_reused_metadata(self) -> None:
        record_owned_child_pid(4321, "Mon Jan  1 00:00:00 2024", "worker --job pilot")
        with patch("src.hoodie.experiments.process_safety._process_metadata") as meta:
            meta.return_value = type("M", (), {"pid": 4321, "ppid": os.getpid(), "pgid": 1000, "sid": 1001, "start_time": "Mon Jan  1 00:00:00 2024", "command": "codex agent host"})()
            with self.assertRaises(ValueError):
                assert_safe_owned_child_pid(4321, "worker")
        with patch("src.hoodie.experiments.process_safety._process_metadata") as meta:
            meta.return_value = type("M", (), {"pid": 4321, "ppid": os.getpid(), "pgid": 1000, "sid": 1001, "start_time": "Mon Jan  1 00:00:01 2024", "command": "worker --job pilot"})()
            with self.assertRaises(ValueError):
                assert_safe_owned_child_pid(4321, "worker")


class CompletionOrderingTests(unittest.TestCase):
    def _row(self, job_type: str = "training") -> ProductionJobRow:
        return ProductionJobRow(
            campaign_id="c",
            panel_id="figure_8a",
            scientific_unit_id="u",
            job_id="j",
            job_type=job_type,
            independent_variable="learning_rate",
            independent_value=1e-6,
            series_name="s",
            policy="HOODIE",
            variant="hoodie_lstm",
            seed=7,
            topology_contract={"agent_counts": [4]},
            physical_contract={"backend": "cpu"},
            workload_contract={"training_episodes": 3, "slots_per_episode": 10, "drain_slots": 0},
            training_contract={"training_episodes": 3, "slots_per_episode": 10, "drain_slots": 0},
            evaluation_contract={"validation_episodes": 2, "slots_per_episode": 10, "drain_slots": 0},
            trace_bank_id="bank",
            checkpoint_dependency=None,
            config_hash="x",
            source_contract_hash="y",
        )

    def test_training_validator_requires_precompletion_outputs_only(self) -> None:
        job_dir = Path(self.id()).resolve()
        job_dir.mkdir(parents=True, exist_ok=True)
        try:
            rows = ["episode_or_step,loss"] + [f"{index},{index + 1}" for index in range(3)]
            (job_dir / "training_history.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
            (job_dir / "checkpoint_selection.json").write_text("{}", encoding="utf-8")
            (job_dir / "provenance.json").write_text("{}", encoding="utf-8")
            validate_training_outputs_before_completion(job_dir, self._row())
            with self.assertRaises(ValueError):
                validate_completed_training_job(job_dir, self._row())
        finally:
            for child in job_dir.iterdir():
                child.unlink()
            job_dir.rmdir()

    def test_evaluation_validator_requires_precompletion_outputs_only(self) -> None:
        job_dir = Path(self.id()).resolve()
        job_dir.mkdir(parents=True, exist_ok=True)
        try:
            (job_dir / "task_records.csv").write_text("task_id\n1\n", encoding="utf-8")
            (job_dir / "evaluation_metrics.csv").write_text("trace_id,average_delay\n1,2\n", encoding="utf-8")
            (job_dir / "provenance.json").write_text("{}", encoding="utf-8")
            validate_evaluation_outputs_before_completion(job_dir, self._row("evaluation"))
            with self.assertRaises(ValueError):
                validate_completed_evaluation_job(job_dir, self._row("evaluation"))
        finally:
            for child in job_dir.iterdir():
                child.unlink()
            job_dir.rmdir()


class SourceScanTests(unittest.TestCase):
    def test_no_broad_kill_paths(self) -> None:
        text = Path("src").read_text() if Path("src").is_file() else ""
        repo_text = "\n".join(p.read_text(encoding="utf-8") for p in Path("src/hoodie/experiments").rglob("*.py"))
        self.assertNotIn("killall", repo_text)
        self.assertNotIn("pkill", repo_text)


if __name__ == "__main__":
    unittest.main()
