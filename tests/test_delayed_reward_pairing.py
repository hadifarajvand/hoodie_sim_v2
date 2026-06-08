from __future__ import annotations

import json
import tempfile
from pathlib import Path
import unittest

import numpy as np

from delayed_reward_runtime import process_delayed_reward_events
from environment.environment import Environment
from environment.task import Task
from phase1_tracing import TraceRecorder
from phase2_mechanisms import build_validation_report
from reward_contract import compute_delayed_reward


def build_env(trace_recorder: TraceRecorder | None = None, timeout: int = 5, size: float = 1.0) -> Environment:
    env = Environment(
        static_frequency=0,
        number_of_servers=1,
        private_cpu_capacities=[1.0],
        public_cpu_capacities=[1.0],
        connection_matrix=[[0, 1]],
        cloud_computational_capacity=1.0,
        episode_time=1,
        task_arrive_probabilities=[0.0],
        task_size_mins=[size],
        task_size_maxs=[size],
        task_size_distributions=["constant"],
        timeout_delay_mins=[timeout],
        timeout_delay_maxs=[timeout],
        timeout_delay_distributions=["constant"],
        priotiry_mins=[1],
        priotiry_maxs=[1],
        priotiry_distributions=["constant"],
        computational_density_mins=[1.0],
        computational_density_maxs=[1.0],
        computational_density_distributions=["constant"],
        drop_penalty_mins=[40],
        drop_penalty_maxs=[40],
        drop_penalty_distributions=["constant"],
        trace_recorder=trace_recorder,
    )
    env.reset()
    env.episode_id = 1
    if trace_recorder is not None:
        trace_recorder.start_episode(1)
    env.current_time = 0
    return env


class FakeAgent:
    def __init__(self) -> None:
        self.calls = []

    def store_transitions(self, **kwargs):
        self.calls.append(kwargs)


class BaselinePolicy:
    pass


class DelayedRewardPairingTests(unittest.TestCase):
    def test_pending_transition_and_reward_resolution(self) -> None:
        recorder = TraceRecorder()
        env = build_env(recorder, timeout=5, size=1.0)
        task = Task(
            size=1.0,
            arrival_time=0,
            timeout_delay=5,
            priotiry=1,
            computational_density=1.0,
            drop_penalty=40,
            origin_server_id=0,
            target_server_id=None,
            task_id=10,
            input_data_size=1.0,
            service_id=1,
            processing_density=1.0,
            timeout=5,
            source_node_id=0,
        )
        env.tasks[0] = task
        recorder.note_task_arrival(task, episode_id=1, source_node=0, arrival_time=0)
        state = np.array([1.0, 2.0], dtype=np.float32)
        lstm_state = np.array([[1.0]], dtype=np.float32)
        next_state = np.array([2.0, 3.0], dtype=np.float32)
        next_lstm_state = np.array([[2.0]], dtype=np.float32)
        recorder.note_pending_transition(
            task_id=10,
            episode_id=1,
            source_agent=0,
            arrival_time=0,
            decision_time=0,
            state_at_decision=state,
            lstm_state_at_decision=lstm_state,
            action_at_decision=0,
            selected_target_node=0,
            raw_action_id=0,
            first_stage_decision="local",
            destination_type="local",
            destination_node_id=None,
            immediate_next_state_after_action=next_state,
            immediate_next_lstm_state_after_action=next_lstm_state,
            created_by_policy="FakeAgent",
            replay_pairing_status="pending",
        )
        env.current_time = 1
        env.servers[0].processing_queue.add_task(task, current_time=0)
        env.servers[0].processing_queue.step()
        events = recorder.resolve_delayed_reward_candidates(1)
        self.assertEqual(len(events), 1)
        self.assertTrue(events[0]["paired_transition_found"])
        self.assertEqual(len(recorder.pending_transition_traces), 1)
        self.assertEqual(len(recorder.delayed_reward_event_traces), 0)
        agents = [FakeAgent()]
        counts = process_delayed_reward_events(agents, recorder, events)
        self.assertEqual(counts["replay_inserted_count"], 1)
        self.assertEqual(len(agents[0].calls), 1)
        call = agents[0].calls[0]
        self.assertTrue(np.allclose(call["state"], state))
        self.assertTrue(np.allclose(call["new_state"], next_state))
        self.assertEqual(call["action"], 0)
        self.assertEqual(call["reward"], -1.0)
        self.assertTrue(call["done"])
        self.assertEqual(len(recorder.delayed_reward_event_traces), 1)
        self.assertTrue(recorder.delayed_reward_event_traces[0].replay_inserted)

    def test_dropped_task_uses_drop_penalty_and_unpaired_event_is_recorded(self) -> None:
        recorder = TraceRecorder()
        env = build_env(recorder, timeout=1, size=5.0)
        task = Task(
            size=5.0,
            arrival_time=0,
            timeout_delay=1,
            priotiry=1,
            computational_density=1.0,
            drop_penalty=40,
            origin_server_id=0,
            target_server_id=None,
            task_id=11,
            input_data_size=5.0,
            service_id=1,
            processing_density=1.0,
            timeout=1,
            source_node_id=0,
        )
        env.tasks[0] = task
        recorder.note_task_arrival(task, episode_id=1, source_node=0, arrival_time=0)
        env.current_time = 1
        env.servers[0].processing_queue.add_task(task, current_time=0)
        env.servers[0].processing_queue.step()
        events = recorder.resolve_delayed_reward_candidates(1)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["reward"], -40.0)
        self.assertEqual(events[0]["reward_reason"], "dropped")

        orphan = Task(
            size=1.0,
            arrival_time=0,
            timeout_delay=1,
            priotiry=1,
            computational_density=1.0,
            drop_penalty=40,
            origin_server_id=0,
            target_server_id=None,
            task_id=12,
            input_data_size=1.0,
            service_id=1,
            processing_density=1.0,
            timeout=1,
            source_node_id=0,
        )
        recorder.note_task_arrival(orphan, episode_id=1, source_node=0, arrival_time=0)
        recorder.note_drop(orphan, episode_id=1, time=1, node_id=0, queue_type="private", reason="timeout")
        orphan_events = recorder.resolve_delayed_reward_candidates(1)
        self.assertTrue(any(not event["paired_transition_found"] for event in orphan_events))

    def test_reward_contract_is_centralized(self) -> None:
        reward = compute_delayed_reward(final_status="completed", arrival_time=2, completion_time=5, drop_penalty=40)
        self.assertEqual(reward.delay, 3)
        self.assertEqual(reward.reward, -3.0)
        self.assertEqual(reward.reward_timing_convention, "completion_minus_arrival")
        drop = compute_delayed_reward(final_status="dropped", arrival_time=2, completion_time=None, drop_penalty=40)
        self.assertEqual(drop.reward, -40.0)

    def test_baseline_runs_emit_events_without_replay(self) -> None:
        recorder = TraceRecorder()
        env = build_env(recorder, timeout=5, size=1.0)
        task = Task(
            size=1.0,
            arrival_time=0,
            timeout_delay=5,
            priotiry=1,
            computational_density=1.0,
            drop_penalty=40,
            origin_server_id=0,
            target_server_id=None,
            task_id=13,
            input_data_size=1.0,
            service_id=1,
            processing_density=1.0,
            timeout=5,
            source_node_id=0,
        )
        env.tasks[0] = task
        recorder.note_task_arrival(task, episode_id=1, source_node=0, arrival_time=0)
        recorder.note_pending_transition(
            task_id=13,
            episode_id=1,
            source_agent=0,
            arrival_time=0,
            decision_time=0,
            state_at_decision=np.array([1.0], dtype=np.float32),
            lstm_state_at_decision=np.array([[1.0]], dtype=np.float32),
            action_at_decision=0,
            selected_target_node=0,
            raw_action_id=0,
            first_stage_decision="local",
            destination_type="local",
            destination_node_id=None,
            immediate_next_state_after_action=np.array([2.0], dtype=np.float32),
            immediate_next_lstm_state_after_action=np.array([[2.0]], dtype=np.float32),
            created_by_policy="BaselinePolicy",
            replay_pairing_status="pending",
        )
        env.current_time = 1
        env.servers[0].processing_queue.add_task(task, current_time=0)
        env.servers[0].processing_queue.step()
        events = recorder.resolve_delayed_reward_candidates(1)
        counts = process_delayed_reward_events([BaselinePolicy()], recorder, events)
        self.assertEqual(counts["replay_inserted_count"], 0)
        self.assertFalse(recorder.delayed_reward_event_traces[0].replay_inserted)

    def test_trace_exports_include_new_files(self) -> None:
        recorder = TraceRecorder()
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir)
            recorder.export(out)
            self.assertTrue((out / "pending_transition_trace.csv").exists())
            self.assertTrue((out / "delayed_reward_event_trace.csv").exists())

    def test_validation_report_delayed_reward_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            trace_dir = Path(tmpdir)
            for name in ("task_lifecycle.csv", "queue_trace.csv", "action_trace.csv", "episode_metrics.csv"):
                (trace_dir / name).write_text("episode_id,time,task_id\n1,0,1\n")
            (trace_dir / "pending_transition_trace.csv").write_text(
                "task_id,episode_id,source_agent,arrival_time,decision_time,state_at_decision_json,lstm_state_at_decision_json,action_at_decision,selected_target_node,raw_action_id,first_stage_decision,destination_type,destination_node_id,immediate_next_state_after_action_json,immediate_next_lstm_state_after_action_json,created_by_policy,replay_pairing_status\n"
                "1,1,0,0,0,\"[1]\",\"[[1]]\",0,0,0,local,local,,\"[2]\",\"[[2]]\",Fake,pending\n"
            )
            (trace_dir / "delayed_reward_event_trace.csv").write_text(
                "task_id,episode_id,source_agent,decision_time,final_status,completion_time,drop_time,delay,reward,drop_penalty,reward_reason,paired_transition_found,replay_inserted,replay_pairing_status,reward_timing_convention\n"
                "1,1,0,0,completed,1,,1,-1.0,,completed,True,True,paired_replay_inserted,completion_minus_arrival\n"
            )
            report = build_validation_report(trace_dir)
            self.assertEqual(report["delayed_reward_contract_status"], "paper_replay_pairing_ready")


if __name__ == "__main__":
    unittest.main()
