from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import numpy as np

from training.trace_dataset import load_trace_dataset, summary_to_dict


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venvmac" / "bin" / "python"


def _write_trace_fixture(trace_dir: Path) -> None:
    trace_dir.mkdir(parents=True, exist_ok=True)
    (trace_dir / "task_lifecycle.csv").write_text(
        "task_id,episode_id,arrival_time,source_node,queue_enter_time,service_start_time,service_end_time,completion_time,drop_time,selected_action,processing_node,latency,waiting_time,service_time,final_status,drop_reason,input_data_size\n"
            "1,0,0,0,0,1,3,3,,1,1,3,1,2,completed,,5\n"
        "2,0,1,1,1,,,,5,2,2,,,,dropped,timeout,7\n"
    )
    (trace_dir / "queue_trace.csv").write_text(
        "episode_id,time,node_id,queue_type,queue_length,arrivals,departures,drops,cpu_allocated\n"
        "0,0,0,private,1,1,0,0,1\n"
        "0,0,0,offloading,2,0,0,0,1\n"
        "0,0,0,public:1,3,0,0,0,1\n"
        "0,0,1,private,4,0,0,0,1\n"
        "0,0,1,offloading,1,0,0,0,1\n"
        "0,0,1,public:0,2,0,0,0,1\n"
        "0,0,2,cloud,6,0,0,0,1\n"
        "0,1,0,private,1,0,0,0,1\n"
        "0,1,0,offloading,2,0,0,0,1\n"
        "0,1,0,public:1,4,0,0,0,1\n"
        "0,1,1,private,3,0,0,0,1\n"
        "0,1,1,offloading,2,0,0,0,1\n"
        "0,1,1,public:0,5,0,0,0,1\n"
        "0,1,2,cloud,7,0,0,0,1\n"
    )
    (trace_dir / "action_trace.csv").write_text(
        "episode_id,time,agent_id,observation_shape,selected_action,target_node,reward_received,raw_action_id,first_stage_decision,destination_node_id,destination_type,is_valid,invalid_reason,adjacency_allowed,cloud_target,d_n_1,d_nk_2\n"
        "0,0,0,\"[3, 5]\",1,1,-3,1,offload,1,horizontal_edge,True,,True,False,1,\"{\\\"1\\\": 1}\"\n"
        "0,1,1,\"[3, 5]\",2,2,-40,2,offload,2,vertical_cloud,True,,True,True,1,\"{\\\"2\\\": 1}\"\n"
    )
    (trace_dir / "episode_metrics.csv").write_text(
        "episode_id,total_tasks,completed_tasks,dropped_tasks,pending_tasks,average_latency,average_waiting_time,average_service_time,drop_ratio,average_queue_length,total_reward,mean_reward\n"
        "0,2,1,1,0,3,1,2,0.5,1,-43,-21.5\n"
    )


class Phase3StateRewardTests(unittest.TestCase):
    def test_paper_state_and_delayed_reward_are_reconstructed(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "trace"
            _write_trace_fixture(trace_dir)
            transitions, summary = load_trace_dataset(trace_dir)

            self.assertEqual(len(transitions), 2)
            self.assertTrue(summary.reconstructed)
            self.assertEqual(summary.state_dim, len(transitions[0].state))
            self.assertGreater(summary.missing_optional_fields["paper_state_predicted_next_load"], 0)

            completed, dropped = transitions
            self.assertEqual(completed.task_id, 1)
            self.assertEqual(completed.eta_n, 5.0)
            self.assertEqual(completed.first_stage_decision, "offload")
            self.assertEqual(completed.destination_type, "horizontal_edge")
            self.assertTrue(completed.is_valid)
            self.assertAlmostEqual(completed.reward, -4.0)
            self.assertTrue(np.isfinite(completed.state).any())
            self.assertIsNotNone(completed.l_pub_n_prev)
            self.assertIsNotNone(completed.load_history)

            self.assertEqual(dropped.task_id, 2)
            self.assertEqual(dropped.reward, -40.0)
            self.assertEqual(dropped.destination_type, "vertical_cloud")
            self.assertTrue(dropped.cloud_target)
            self.assertEqual(dropped.d_n_1, 1)
            self.assertEqual(dropped.d_nk_2, {2: 1})

    def test_replay_tuple_contains_phase2_action_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "trace"
            _write_trace_fixture(trace_dir)
            transitions, _ = load_trace_dataset(trace_dir)
            transition = transitions[0]

            self.assertIsNotNone(transition.raw_action_id)
            self.assertIsNotNone(transition.first_stage_decision)
            self.assertIsNotNone(transition.destination_node_id)
            self.assertIsNotNone(transition.destination_type)
            self.assertIsNotNone(transition.adjacency_allowed)
            self.assertIsNotNone(transition.cloud_target)
            self.assertIsNotNone(transition.d_n_1)
            self.assertIsNotNone(transition.d_nk_2)
            self.assertEqual(transition.state.shape, transition.next_state.shape)

    def test_smoke_training_run_creates_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "trace"
            out_dir = Path(tmp) / "out"
            _write_trace_fixture(trace_dir)
            result = subprocess.run(
                [
                    str(PYTHON),
                    "-m",
                    "training.train_phase3",
                    "--trace-dir",
                    str(trace_dir),
                    "--output-dir",
                    str(out_dir),
                    "--epochs",
                    "1",
                    "--batch-size",
                    "1",
                    "--checkpoint-every",
                    "1",
                    "--seed",
                    "7",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            for filename in ["dataset_summary.json", "training_metrics.json", "phase3_model.chkpt", "phase3_training_report.json"]:
                self.assertTrue((out_dir / filename).exists(), filename)

            dataset_summary = json.loads((out_dir / "dataset_summary.json").read_text())
            self.assertEqual(dataset_summary["state_dim"], len(load_trace_dataset(trace_dir)[0][0].state))
            metrics = json.loads((out_dir / "training_metrics.json").read_text())
            self.assertEqual(metrics["epochs"], 1)
            self.assertEqual(metrics["transitions_used"], 2)


if __name__ == "__main__":
    unittest.main()
