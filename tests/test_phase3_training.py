from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import numpy as np

from training.replay_buffer import ReplayBuffer, Transition
from training.trace_dataset import load_trace_dataset, summary_to_dict
from training.trainers import DQNTrainer, TrainerConfig


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venvmac" / "bin" / "python"


def _write_realish_trace(trace_dir: Path) -> None:
    trace_dir.mkdir(parents=True, exist_ok=True)
    (trace_dir / "task_lifecycle.csv").write_text(
        "task_id,episode_id,arrival_time,source_node,queue_enter_time,service_start_time,service_end_time,completion_time,drop_time,selected_action,processing_node,latency,waiting_time,service_time,final_status,drop_reason\n"
        "1,0,0,0,0,1,3,3,,0,0,3,1,2,completed,\n"
        "2,0,1,1,1,,,5,5,1,1,4,,,dropped,timeout\n"
    )
    (trace_dir / "queue_trace.csv").write_text(
        "episode_id,time,node_id,queue_type,queue_length,arrivals,departures,drops,cpu_allocated\n"
        "0,0,0,private,1,1,0,0,1\n"
    )
    (trace_dir / "action_trace.csv").write_text(
        "episode_id,time,agent_id,observation_shape,selected_action,target_node,reward_received\n"
        "0,0,0,\"[2, 3]\",0,0,1\n"
    )
    (trace_dir / "episode_metrics.csv").write_text(
        "episode_id,total_tasks,completed_tasks,dropped_tasks,pending_tasks,average_latency,average_waiting_time,average_service_time,drop_ratio,average_queue_length,total_reward,mean_reward\n"
        "0,2,1,1,0,3,1,2,0.5,1,-1,-1\n"
    )


class Phase3TrainingTests(unittest.TestCase):
    def test_replay_buffer_sampling_is_deterministic(self):
        t1 = Transition(np.array([1.0, 2.0], dtype=np.float32), 0, 1.0, np.array([2.0, 3.0], dtype=np.float32), False)
        t2 = Transition(np.array([3.0, 4.0], dtype=np.float32), 1, -1.0, np.array([4.0, 5.0], dtype=np.float32), True)
        a = ReplayBuffer(capacity=10, seed=7)
        b = ReplayBuffer(capacity=10, seed=7)
        for buf in (a, b):
            buf.push(t1)
            buf.push(t2)
        sample_a = a.sample(2)
        sample_b = b.sample(2)
        self.assertEqual([t.action for t in sample_a], [t.action for t in sample_b])

    def test_trace_dataset_summary_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "trace"
            _write_realish_trace(trace_dir)
            transitions, summary = load_trace_dataset(trace_dir)
            self.assertTrue(transitions)
            summary_dict = summary_to_dict(summary)
            self.assertEqual(summary_dict["transitions"], len(transitions))
            self.assertTrue(summary_dict["reconstructed"])
            self.assertEqual(summary_dict["state_dim"], len(transitions[0].state))
            self.assertEqual(summary_dict["action_count"], 2)
            self.assertTrue(summary_dict["required_files_present"]["task_lifecycle.csv"])

    def test_missing_required_fields_fail_clearly(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "trace"
            trace_dir.mkdir(parents=True, exist_ok=True)
            (trace_dir / "broken.json").write_text(json.dumps([{"state": [1, 2], "reward": 1.0}]))
            with self.assertRaises(ValueError):
                load_trace_dataset(trace_dir)

    def test_missing_trace_files_fail_clearly(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "trace"
            trace_dir.mkdir(parents=True, exist_ok=True)
            (trace_dir / "task_lifecycle.csv").write_text(
                "task_id,episode_id,arrival_time,source_node,queue_enter_time,service_start_time,service_end_time,completion_time,drop_time,selected_action,processing_node,latency,waiting_time,service_time,final_status,drop_reason\n"
                "1,0,0,0,0,1,3,3,,0,0,3,1,2,completed,\n"
            )
            with self.assertRaises(ValueError):
                load_trace_dataset(trace_dir)

    def test_algorithm_validation(self):
        with self.assertRaises(ValueError):
            TrainerConfig(
                algorithm="bad",
                input_dim=2,
                action_dim=2,
                hidden_sizes=[8],
                gamma=0.99,
                learning_rate=1e-3,
                batch_size=2,
                target_update_interval=2,
                seed=1,
            ).validate()

    def test_cli_full_training_run_creates_required_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "trace"
            out_dir = Path(tmp) / "out"
            _write_realish_trace(trace_dir)
            result = subprocess.run(
                [
                    str(PYTHON),
                    "-m",
                    "training.train_phase3",
                    "--trace-dir",
                    str(trace_dir),
                    "--output-dir",
                    str(out_dir),
                    "--algorithm",
                    "dqn",
                    "--epochs",
                    "2",
                    "--batch-size",
                    "2",
                    "--seed",
                    "42",
                    "--checkpoint-every",
                    "1",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            for filename in [
                "dataset_summary.json",
                "phase3_training_report.json",
                "training_metrics.json",
                "phase3_model.chkpt",
                "checkpoint_epoch_001.chkpt",
                "checkpoint_epoch_002.chkpt",
            ]:
                self.assertTrue((out_dir / filename).exists(), filename)

            report = json.loads((out_dir / "phase3_training_report.json").read_text())
            self.assertFalse(report["paper_claims_made"])
            self.assertFalse(report["figures_generated"])
            self.assertFalse(report["phase4_evaluation_performed"])

            metrics = json.loads((out_dir / "training_metrics.json").read_text())
            self.assertEqual(metrics["algorithm"], "dqn")
            self.assertEqual(metrics["epochs"], 2)
            self.assertIn("losses_by_epoch", metrics)
            self.assertIn("final_loss", metrics)

            checkpoint = json.loads((out_dir / "phase3_model.chkpt").read_text())
            self.assertEqual(checkpoint["algorithm"], "dqn")
            self.assertEqual(checkpoint["seed"], 42)
            self.assertEqual(checkpoint["state_dim"], len(load_trace_dataset(trace_dir)[0][0].state))
            self.assertEqual(checkpoint["action_count"], 2)
            self.assertEqual(checkpoint["epochs_completed"], 2)

    def test_unsupported_algorithm_fails_clearly(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "trace"
            out_dir = Path(tmp) / "out"
            _write_realish_trace(trace_dir)
            result = subprocess.run(
                [
                    str(PYTHON),
                    "-m",
                    "training.train_phase3",
                    "--trace-dir",
                    str(trace_dir),
                    "--output-dir",
                    str(out_dir),
                    "--algorithm",
                    "unsupported",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unsupported algorithm", result.stderr + result.stdout)

    def test_existing_smoke_behavior_still_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "trace"
            out_dir = Path(tmp) / "out"
            _write_realish_trace(trace_dir)
            result = subprocess.run(
                [
                    str(PYTHON),
                    "-m",
                    "training.train_phase3",
                    "--trace-dir",
                    str(trace_dir),
                    "--output-dir",
                    str(out_dir),
                    "--algorithm",
                    "dqn",
                    "--epochs",
                    "1",
                    "--seed",
                    "42",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue((out_dir / "dataset_summary.json").exists())

    def test_runtime_trace_smoke_loads_real_transitions(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "runtime_trace"
            log_dir = Path(tmp) / "logs"
            smoke = subprocess.run(
                [
                    str(PYTHON),
                    "main.py",
                    "--epochs",
                    "1",
                    "--log_folder",
                    str(log_dir),
                    "--trace_output_dir",
                    str(trace_dir),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(smoke.returncode, 0, msg=smoke.stderr)
            transitions, summary = load_trace_dataset(trace_dir)
            self.assertGreater(summary.episodes, 0)
            self.assertGreater(summary.transitions, 0)
            self.assertIsNotNone(summary.state_dim)
            self.assertIsNotNone(summary.action_count)
            self.assertTrue(transitions)


if __name__ == "__main__":
    unittest.main()
