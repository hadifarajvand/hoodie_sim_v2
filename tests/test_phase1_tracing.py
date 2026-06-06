from __future__ import annotations

import csv
import subprocess
import tempfile
import unittest
from pathlib import Path

from phase1_trace_validation import audit_trace_dir, validate_trace_dir


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venvmac" / "bin" / "python"


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_valid_trace_fixture(output_dir: Path) -> None:
    _write_csv(
        output_dir / "task_lifecycle.csv",
        [
            {
                "task_id": 1,
                "episode_id": 0,
                "arrival_time": 0,
                "source_node": 0,
                "queue_enter_time": 0,
                "service_start_time": 1,
                "service_end_time": 3,
                "completion_time": 3,
                "drop_time": "",
                "selected_action": 0,
                "processing_node": 0,
                "latency": 3.0,
                "waiting_time": 1.0,
                "service_time": 2.0,
                "final_status": "completed",
                "drop_reason": "",
            },
            {
                "task_id": 2,
                "episode_id": 0,
                "arrival_time": 0,
                "source_node": 1,
                "queue_enter_time": 0,
                "service_start_time": "",
                "service_end_time": "",
                "completion_time": "",
                "drop_time": 4,
                "selected_action": 1,
                "processing_node": 1,
                "latency": 4.0,
                "waiting_time": "",
                "service_time": "",
                "final_status": "dropped",
                "drop_reason": "timeout",
            },
            {
                "task_id": 3,
                "episode_id": 0,
                "arrival_time": 1,
                "source_node": 2,
                "queue_enter_time": "",
                "service_start_time": "",
                "service_end_time": "",
                "completion_time": "",
                "drop_time": "",
                "selected_action": "",
                "processing_node": "",
                "latency": "",
                "waiting_time": "",
                "service_time": "",
                "final_status": "pending",
                "drop_reason": "",
            },
        ],
    )
    _write_csv(
        output_dir / "queue_trace.csv",
        [
            {
                "episode_id": 0,
                "time": 0,
                "node_id": 0,
                "queue_type": "private",
                "queue_length": 1.0,
                "arrivals": 1,
                "departures": 0,
                "drops": 0,
                "cpu_allocated": 1.0,
            },
        ],
    )
    _write_csv(
        output_dir / "action_trace.csv",
        [
            {
                "episode_id": 0,
                "time": 0,
                "agent_id": 0,
                "observation_shape": "[2, 3]",
                "selected_action": 0,
                "target_node": 0,
                "reward_received": 1.0,
            },
        ],
    )
    _write_csv(
        output_dir / "episode_metrics.csv",
        [
            {
                "episode_id": 0,
                "total_tasks": 3,
                "completed_tasks": 1,
                "dropped_tasks": 1,
                "pending_tasks": 1,
                "average_latency": 3.5,
                "average_waiting_time": 1.0,
                "average_service_time": 2.0,
                "drop_ratio": 1 / 3,
                "average_queue_length": 1.0,
                "total_reward": -1.0,
                "mean_reward": -1.0,
            }
        ],
    )


def _write_inconsistent_trace_fixture(output_dir: Path) -> None:
    _write_valid_trace_fixture(output_dir)
    rows = []
    with (output_dir / "task_lifecycle.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    rows[0]["selected_action"] = ""
    rows[1]["selected_action"] = ""
    with (output_dir / "task_lifecycle.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


class Phase1TracingTests(unittest.TestCase):
    def test_validation_rejects_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                validate_trace_dir(tmp)

    def test_validator_reports_complete_audit_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "traces"
            _write_valid_trace_fixture(trace_dir)
            audit = audit_trace_dir(trace_dir)
            self.assertEqual(audit["errors"], [])
            self.assertEqual(audit["warnings"], [])
            summary = audit["summary"]
            self.assertEqual(summary["total_tasks_from_metrics"], 3)
            self.assertEqual(summary["unique_lifecycle_task_ids"], 3)
            self.assertTrue(summary["task_count_consistent"])
            self.assertTrue(summary["unique_task_count_consistent"])
            self.assertEqual(summary["selected_action_present"], 2)
            self.assertEqual(summary["selected_action_missing"], 1)
            self.assertEqual(summary["selected_action_by_final_status"]["completed"]["missing"], 0)
            self.assertEqual(summary["selected_action_by_final_status"]["dropped"]["missing"], 0)
            self.assertEqual(summary["selected_action_by_final_status"]["pending"]["missing"], 1)
            self.assertEqual(validate_trace_dir(trace_dir), [])

    def test_validator_flags_count_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "traces"
            _write_valid_trace_fixture(trace_dir)
            with (trace_dir / "episode_metrics.csv").open("w", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "episode_id",
                        "total_tasks",
                        "completed_tasks",
                        "dropped_tasks",
                        "pending_tasks",
                        "average_latency",
                        "average_waiting_time",
                        "average_service_time",
                        "drop_ratio",
                        "average_queue_length",
                        "total_reward",
                        "mean_reward",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "episode_id": 0,
                        "total_tasks": 4,
                        "completed_tasks": 1,
                        "dropped_tasks": 1,
                        "pending_tasks": 1,
                        "average_latency": 3.5,
                        "average_waiting_time": 1.0,
                        "average_service_time": 2.0,
                        "drop_ratio": 0.25,
                        "average_queue_length": 1.0,
                        "total_reward": -1.0,
                        "mean_reward": -1.0,
                    }
                )
            errors = validate_trace_dir(trace_dir)
            self.assertIn("task count mismatch across episode_metrics", errors)
            self.assertIn("unique task_id count does not match episode_metrics total_tasks", errors)

    def test_validator_reports_missing_selected_action_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "traces"
            _write_inconsistent_trace_fixture(trace_dir)
            audit = audit_trace_dir(trace_dir)
            self.assertTrue(audit["warnings"])
            self.assertIn(
                "completed or dropped tasks are missing selected_action coverage",
                audit["warnings"],
            )
            self.assertEqual(audit["summary"]["selected_action_by_final_status"]["completed"]["missing"], 1)
            self.assertEqual(audit["summary"]["selected_action_by_final_status"]["dropped"]["missing"], 1)

    def test_one_epoch_run_emits_trace_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "traces"
            log_dir = Path(tmp) / "logs"
            cmd = [
                str(PYTHON),
                "main.py",
                "--epochs",
                "1",
                "--log_folder",
                str(log_dir),
                "--trace_output_dir",
                str(trace_dir),
            ]
            result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            expected = {
                "task_lifecycle.csv",
                "queue_trace.csv",
                "action_trace.csv",
                "episode_metrics.csv",
            }
            produced = {p.name for p in trace_dir.glob("*.csv")}
            self.assertTrue(expected.issubset(produced))
            audit = audit_trace_dir(trace_dir)
            self.assertEqual(audit["errors"], [], msg="\n".join(audit["errors"]))
            self.assertTrue(audit["summary"]["task_count_consistent"])


if __name__ == "__main__":
    unittest.main()
