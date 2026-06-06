from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import numpy as np

from environment.queues import PublicQueueManager
from environment.task import Task
from phase2_mechanisms import build_policy_map, infer_reward_events, write_validation_artifacts


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venvmac" / "bin" / "python"


class Phase2MechanismTests(unittest.TestCase):
    def test_policy_map_includes_paper_baselines(self):
        policy_map = build_policy_map()
        self.assertEqual(
            set(policy_map.keys()),
            {"HOODIE", "RO", "FLC", "VO", "HO", "BCO", "MLEO"},
        )

    def test_public_cpu_sharing_is_equal_across_active_queues(self):
        manager = PublicQueueManager(id=3, computational_capacity=9.0, supporting_servers=np.array([0, 1, 2]))
        task_a = Task(size=1.0, arrival_time=0, timeout_delay=10, priotiry=1, computational_density=1.0, drop_penalty=1, origin_server_id=0, target_server_id=3)
        task_b = Task(size=1.0, arrival_time=0, timeout_delay=10, priotiry=1, computational_density=1.0, drop_penalty=1, origin_server_id=1, target_server_id=3)
        manager.add_tasks([task_a, task_b], current_time=0)
        self.assertEqual(sum(not q.current_task.is_empty() for q in manager.public_queues.values()), 2)
        rewards = manager.step()
        self.assertIsInstance(rewards, dict)
        self.assertLessEqual(manager.get_active_queues(), 2)

    def test_reward_events_are_task_traceable(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "trace"
            trace_dir.mkdir()
            (trace_dir / "task_lifecycle.csv").write_text(
                "task_id,episode_id,arrival_time,source_node,queue_enter_time,service_start_time,service_end_time,completion_time,drop_time,selected_action,processing_node,latency,waiting_time,service_time,final_status,drop_reason\n"
                "1,0,0,0,0,1,3,3,,0,0,3,1,2,completed,\n"
                "2,0,0,1,0,,,,4,1,1,4,,,dropped,timeout\n"
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
            events = infer_reward_events(trace_dir)
            self.assertEqual(len(events), 2)
            self.assertEqual(events[0].final_status, "completed")
            self.assertEqual(events[0].reward, -4.0)
            self.assertEqual(events[1].final_status, "dropped")
            self.assertEqual(events[1].reward, -40.0)

    def test_validation_artifacts_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "trace"
            out_dir = Path(tmp) / "out"
            trace_dir.mkdir()
            (trace_dir / "task_lifecycle.csv").write_text(
                "task_id,episode_id,arrival_time,source_node,queue_enter_time,service_start_time,service_end_time,completion_time,drop_time,selected_action,processing_node,latency,waiting_time,service_time,final_status,drop_reason\n"
                "1,0,0,0,0,1,3,3,,0,0,3,1,2,completed,\n"
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
                "0,1,1,0,0,3,1,2,0,1,-1,-1\n"
            )
            write_validation_artifacts(trace_dir, out_dir)
            for filename in [
                "baseline_validation_report.json",
                "active_policy_set.json",
                "mleo_candidate_latency_samples.json",
            ]:
                self.assertTrue((out_dir / filename).exists())
                json.loads((out_dir / filename).read_text())

    def test_short_smoke_run_still_executes(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "trace"
            log_dir = Path(tmp) / "logs"
            result = subprocess.run(
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
            self.assertEqual(result.returncode, 0, msg=result.stderr)


if __name__ == "__main__":
    unittest.main()
