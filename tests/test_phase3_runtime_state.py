from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import numpy as np

from environment.queues import OffloadingQueue, ProcessingQueue
from training.trace_dataset import load_trace_dataset, summary_to_dict


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venvmac" / "bin" / "python"


def _write_paper_state_trace(trace_dir: Path) -> None:
    trace_dir.mkdir(parents=True, exist_ok=True)
    (trace_dir / "paper_state_trace.csv").write_text(
        "episode_id,time,agent_id,task_id,eta_n,w_priv_n,w_off_n,l_pub_n_prev_json,active_load_vector_json,L_t_json,predicted_next_load_json,predicted_next_load_method,paper_lstm_forecast,unavailable_fields_json,approximation_warnings_json,state_vector_json,state_dim\n"
        "0,0,0,1,5,2,1,\"[0,0]\",\"[1,0]\",\"[[1,0],[0,0]]\",\"[1,0]\",persistence_baseline,False,\"[]\",\"[]\",\"[5,2,1,0,0,1,1,0]\",8\n"
        "0,1,0,1,5,1,0,\"[1,0]\",\"[0,1]\",\"[[1,0],[0,1]]\",\"[0,1]\",persistence_baseline,False,\"[]\",\"[]\",\"[5,1,0,1,0,1,0,1]\",8\n"
    )
    (trace_dir / "action_trace.csv").write_text(
        "episode_id,time,agent_id,observation_shape,selected_action,target_node,reward_received,raw_action_id,first_stage_decision,destination_node_id,destination_type,is_valid,invalid_reason,adjacency_allowed,cloud_target,d_n_1,d_nk_2\n"
        "0,0,0,\"[8]\",1,1,-4,1,offload,1,horizontal_edge,True,,True,False,1,\"{\\\"1\\\": 1}\"\n"
        "0,1,0,\"[8]\",0,0,0,0,local,,local,True,,True,False,0,\"{}\"\n"
    )
    (trace_dir / "task_lifecycle.csv").write_text(
        "task_id,episode_id,arrival_time,source_node,queue_enter_time,service_start_time,service_end_time,completion_time,drop_time,selected_action,processing_node,latency,waiting_time,service_time,final_status,drop_reason\n"
        "1,0,0,0,0,1,2,2,,1,1,2,1,1,completed,\n"
    )
    (trace_dir / "queue_trace.csv").write_text(
        "episode_id,time,node_id,queue_type,queue_length,arrivals,departures,drops,cpu_allocated\n"
        "0,0,0,private,1,0,0,0,1\n"
    )
    (trace_dir / "episode_metrics.csv").write_text(
        "episode_id,total_tasks,completed_tasks,dropped_tasks,pending_tasks,average_latency,average_waiting_time,average_service_time,drop_ratio,average_queue_length,total_reward,mean_reward\n"
        "0,1,1,0,0,2,1,1,0,1,-4,-4\n"
    )


class Phase3RuntimeStateTests(unittest.TestCase):
    def test_processing_queue_waiting_time_comes_from_remaining_work_not_queue_length(self):
        queue = ProcessingQueue(0.5)
        queue.add_task(
            __import__("environment.task", fromlist=["Task"]).Task(
                size=2,
                arrival_time=0,
                timeout_delay=10,
                computational_density=1,
                drop_penalty=1,
                origin_server_id=0,
                task_id=1,
            ),
            current_time=0,
        )
        queue.add_task(
            __import__("environment.task", fromlist=["Task"]).Task(
                size=2,
                arrival_time=0,
                timeout_delay=10,
                computational_density=1,
                drop_penalty=1,
                origin_server_id=0,
                task_id=2,
            ),
            current_time=0,
        )
        self.assertEqual(queue.get_queue_length(), 4)
        self.assertEqual(queue.get_waiting_time(), 8)

    def test_offloading_queue_waiting_time_comes_from_remaining_work_not_queue_length(self):
        queue = OffloadingQueue({1: 1.0})
        task1 = __import__("environment.task", fromlist=["Task"]).Task(
            size=3,
            arrival_time=0,
            timeout_delay=10,
            computational_density=1,
            drop_penalty=1,
            origin_server_id=0,
            target_server_id=1,
            task_id=1,
        )
        task2 = __import__("environment.task", fromlist=["Task"]).Task(
            size=2,
            arrival_time=0,
            timeout_delay=10,
            computational_density=1,
            drop_penalty=1,
            origin_server_id=0,
            target_server_id=1,
            task_id=2,
        )
        queue.add_task(task1, current_time=0)
        queue.add_task(task2, current_time=0)
        self.assertEqual(queue.get_queue_length(), 5)
        self.assertEqual(queue.get_waiting_time(), 5)

    def test_runtime_state_trace_is_exported_and_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "runtime_trace"
            log_dir = Path(tmp) / "logs"
            out_dir = Path(tmp) / "out"
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
            self.assertTrue((trace_dir / "paper_state_trace.csv").exists())

            transitions, summary = load_trace_dataset(trace_dir)
            self.assertTrue(summary.paper_state_trace_present)
            self.assertEqual(summary.state_source, "runtime_paper_state_trace")
            self.assertEqual(summary.next_state_source, "runtime_paper_state_trace")
            self.assertGreater(summary.state_dim, 2)
            self.assertTrue(transitions)
            self.assertEqual(transitions[0].state.shape, transitions[0].next_state.shape)

    def test_loader_prefers_paper_state_trace(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "trace"
            _write_paper_state_trace(trace_dir)
            transitions, summary = load_trace_dataset(trace_dir)
            self.assertTrue(summary.paper_state_trace_present)
            self.assertEqual(summary.state_source, "runtime_paper_state_trace")
            self.assertEqual(summary.waiting_time_source, "runtime_queue_waiting_time")
            self.assertEqual(summary.load_history_source, "runtime_active_load_matrix")
            self.assertEqual(summary.predicted_next_load_method, "persistence_baseline")
            self.assertFalse(summary.paper_lstm_forecast)
            self.assertEqual(summary.state_dim, 8)
            self.assertEqual(len(transitions), 2)
            self.assertTrue(np.array_equal(transitions[0].next_state, transitions[1].state))
            self.assertFalse(np.array_equal(transitions[0].state, transitions[0].next_state))

    def test_gap_closure_artifacts_are_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "trace"
            out_dir = Path(tmp) / "out"
            _write_paper_state_trace(trace_dir)
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
                    "11",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            for filename in [
                "dataset_summary.json",
                "phase3_runtime_state_report.json",
                "phase3_runtime_state_report.md",
                "sample_paper_state_trace.csv",
                "state_source_contract.json",
                "gap_closure_matrix.csv",
            ]:
                self.assertTrue((out_dir / filename).exists(), filename)

            contract = json.loads((out_dir / "state_source_contract.json").read_text())
            self.assertIn("next_state_not_copy", contract)
            self.assertIn("waiting_time_not_queue_length_proxy", contract)
            self.assertIn("active_load_matrix_not_queue_length_history", contract)


if __name__ == "__main__":
    unittest.main()
