from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

import numpy as np

from phase1_tracing import TraceRecorder
from reward_contract import compute_delayed_reward
from training.trace_dataset import load_trace_dataset


class Model7RewardContractTests(unittest.TestCase):
    def test_central_reward_convention(self):
        completed = compute_delayed_reward(final_status="completed", arrival_time=2, completion_time=7, drop_penalty=40)
        self.assertEqual(completed.delay, 5)
        self.assertEqual(completed.reward, -5.0)
        self.assertEqual(completed.reward_timing_convention, "completion_minus_arrival")
        self.assertEqual(completed.reward_reason, "completed")

        dropped = compute_delayed_reward(final_status="dropped", arrival_time=2, completion_time=None, drop_penalty=40)
        self.assertEqual(dropped.reward, -40.0)
        self.assertEqual(dropped.reward_reason, "dropped")

    def test_trace_dataset_fallback_uses_central_reward_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp)
            (trace_dir / "task_lifecycle.csv").write_text(
                "task_id,episode_id,arrival_time,source_node,queue_enter_time,service_start_time,service_end_time,completion_time,drop_time,selected_action,processing_node,latency,waiting_time,service_time,final_status,drop_reason,drop_penalty,input_data_size\n"
                "1,0,0,0,0,1,3,3,,1,1,3,1,2,completed,,40,5\n"
                "2,0,1,1,1,,,,5,2,2,,,,dropped,timeout,40,7\n"
            )
            (trace_dir / "queue_trace.csv").write_text("episode_id,time,node_id,queue_type,queue_length\n0,0,0,private,1\n")
            (trace_dir / "action_trace.csv").write_text(
                "episode_id,time,agent_id,observation_shape,selected_action,target_node,reward_received\n"
                "0,0,0,\"[3]\",1,1,-3\n"
            )
            (trace_dir / "episode_metrics.csv").write_text("episode_id,total_tasks,completed_tasks,dropped_tasks,pending_tasks,average_latency,average_waiting_time,average_service_time,drop_ratio,average_queue_length,total_reward,mean_reward\n0,2,1,1,0,3,1,2,0.5,1,-43,-21.5\n")
            transitions, _ = load_trace_dataset(trace_dir)
        self.assertEqual(len(transitions), 2)
        self.assertEqual(transitions[0].reward, -3.0)
        self.assertEqual(transitions[1].reward, -40.0)

    def test_delayed_reward_event_trace_is_preferred(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp)
            (trace_dir / "paper_state_trace.csv").write_text(
                "episode_id,time,agent_id,x_n_t,task_id,eta_n,w_priv_n,w_off_n,l_pub_n_prev_json,active_load_vector_json,L_t_json,predicted_next_load_json,predicted_next_load_method,paper_lstm_forecast,unavailable_fields_json,approximation_warnings_json,state_vector_json,state_dim\n"
                "0,1,0,1,1,1,0,0,\"[0,0,0]\",\"[0,0,0]\",\"[[0,0,0],[0,0,0],[0,0,0],[0,0,0]]\",\"[0,0,0]\",persistence_baseline,False,\"[]\",\"[]\",\"[1,0,0]\",3\n"
            )
            (trace_dir / "action_trace.csv").write_text(
                "episode_id,time,agent_id,selected_action,reward_received,policy_name,raw_action_id,first_stage_decision,destination_node_id,destination_type,is_valid,invalid_reason,adjacency_allowed,cloud_target,d_n_1,d_nk_2\n"
                "0,1,0,1,-7,HOODIE,1,offload,1,horizontal_edge,True,,True,False,0,\"{\\\"1\\\": 1}\"\n"
            )
            (trace_dir / "task_lifecycle.csv").write_text(
                "task_id,episode_id,arrival_time,source_node,queue_enter_time,service_start_time,service_end_time,completion_time,drop_time,selected_action,processing_node,latency,waiting_time,service_time,final_status,drop_reason,drop_penalty,input_data_size\n"
                "1,0,1,0,1,1,3,3,,1,1,3,1,2,completed,,40,5\n"
            )
            (trace_dir / "delayed_reward_event_trace.csv").write_text(
                "task_id,episode_id,source_agent,decision_time,final_status,completion_time,drop_time,delay,reward,drop_penalty,reward_reason,paired_transition_found,replay_inserted,replay_pairing_status,reward_timing_convention\n"
                "1,0,0,1,completed,3,,2,-7,40,completed,True,True,paired,completion_minus_arrival\n"
            )
            (trace_dir / "queue_trace.csv").write_text("episode_id,time,node_id,queue_type,queue_length\n0,0,0,private,1\n")
            (trace_dir / "episode_metrics.csv").write_text("episode_id,total_tasks,completed_tasks,dropped_tasks,pending_tasks,average_latency,average_waiting_time,average_service_time,drop_ratio,average_queue_length,total_reward,mean_reward\n0,1,1,0,0,3,1,2,0,1,-7,-7\n")
            transitions, summary = load_trace_dataset(trace_dir)
        self.assertEqual(transitions[0].reward, -7.0)
        self.assertIn("used delayed_reward_event_trace for reward reconstruction", summary.notes)

    def test_pending_transition_pairing(self):
        recorder = TraceRecorder()
        recorder.start_episode(0)
        recorder.note_pending_transition(
            task_id=99,
            episode_id=0,
            source_agent=0,
            arrival_time=0,
            decision_time=0,
            state_at_decision=np.array([1.0, 2.0], dtype=np.float32),
            lstm_state_at_decision=np.array([[1.0]], dtype=np.float32),
            action_at_decision=1,
            selected_target_node=1,
            raw_action_id=1,
            first_stage_decision="offload",
            destination_type="horizontal_edge",
            destination_node_id=1,
            immediate_next_state_after_action=np.array([2.0, 3.0], dtype=np.float32),
            immediate_next_lstm_state_after_action=np.array([[2.0]], dtype=np.float32),
            created_by_policy="HOODIE",
            replay_pairing_status="pending",
        )
        recorder.note_task_arrival(
            type("TaskLike", (), {"task_id": 99, "drop_penalty": 40})(),
            episode_id=0,
            source_node=0,
            arrival_time=0,
        )
        recorder.task_records[99].final_status = "completed"
        recorder.task_records[99].arrival_time = 0
        recorder.task_records[99].completion_time = 4
        recorder.task_records[99].drop_penalty = 40
        events = recorder.resolve_delayed_reward_candidates(0)
        self.assertEqual(len(events), 1)
        self.assertTrue(events[0]["paired_transition_found"])
        self.assertEqual(events[0]["replay_pairing_status"], "paired")
        self.assertEqual(events[0]["reward"], -4.0)
        self.assertEqual(len(recorder.delayed_reward_event_traces), 1)
        persisted = recorder.delayed_reward_event_traces[0]
        self.assertEqual(persisted.task_id, 99)
        self.assertEqual(persisted.reward, -4.0)
        self.assertEqual(persisted.reward_timing_convention, "completion_minus_arrival")
        self.assertTrue(persisted.paired_transition_found)
        repeat = recorder.resolve_delayed_reward_candidates(0)
        self.assertEqual(repeat, [])
        self.assertEqual(len(recorder.delayed_reward_event_traces), 1)

        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp)
            recorder.export(trace_dir)
            path = trace_dir / "delayed_reward_event_trace.csv"
            self.assertTrue(path.exists())
            with path.open(newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 1)
            row = rows[0]
            self.assertEqual(row["task_id"], "99")
            self.assertEqual(float(row["reward"]), -4.0)
            self.assertEqual(row["replay_pairing_status"], "paired")
            self.assertEqual(row["reward_timing_convention"], "completion_minus_arrival")

    def test_episode_metrics_from_lifecycle_and_rewards(self):
        recorder = TraceRecorder()
        recorder.start_episode(0)
        completed = recorder.ensure_task(1)
        completed.episode_id = 0
        completed.final_status = "completed"
        completed.arrival_time = 0
        completed.completion_time = 3
        completed.latency = 3
        completed.waiting_time = 1
        completed.service_time = 2
        dropped = recorder.ensure_task(2)
        dropped.episode_id = 0
        dropped.final_status = "dropped"
        dropped.arrival_time = 0
        dropped.drop_penalty = 40
        pending = recorder.ensure_task(3)
        pending.episode_id = 0
        pending.final_status = "pending"
        recorder.note_delayed_reward_event(
            task_id=1,
            episode_id=0,
            source_agent=0,
            decision_time=0,
            final_status="completed",
            completion_time=3,
            drop_time=None,
            delay=3,
            reward=-3.0,
            drop_penalty=None,
            reward_reason="completed",
            paired_transition_found=True,
            replay_inserted=True,
            replay_pairing_status="paired",
            reward_timing_convention="completion_minus_arrival",
        )
        recorder.note_delayed_reward_event(
            task_id=2,
            episode_id=0,
            source_agent=0,
            decision_time=0,
            final_status="dropped",
            completion_time=None,
            drop_time=1,
            delay=None,
            reward=-40.0,
            drop_penalty=40.0,
            reward_reason="dropped",
            paired_transition_found=False,
            replay_inserted=False,
            replay_pairing_status="unpaired",
            reward_timing_convention="completion_minus_arrival",
        )
        metric = recorder.finalize_episode(0, total_reward=0.0, mean_reward=0.0)
        self.assertEqual(metric.total_tasks, 3)
        self.assertEqual(metric.completed_tasks, 1)
        self.assertEqual(metric.dropped_tasks, 1)
        self.assertEqual(metric.pending_tasks, 1)
        self.assertAlmostEqual(metric.drop_ratio, 1 / 3)
        self.assertEqual(metric.total_reward, -43.0)
        self.assertEqual(metric.mean_reward, -21.5)


if __name__ == "__main__":
    unittest.main()
