from __future__ import annotations

import csv
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np

from decision_makers.baselines import MinimumLatencyEstimationOffloader
from environment.environment import Environment
from environment.task import Task
from phase1_tracing import TraceRecorder
from phase2_mechanisms import build_validation_report


ROOT = Path(__file__).resolve().parents[1]


def build_tiny_env(trace_recorder: TraceRecorder | None = None) -> Environment:
    env = Environment(
        static_frequency=0,
        number_of_servers=2,
        private_cpu_capacities=[1.0, 1.0],
        public_cpu_capacities=[1.0, 1.0],
        connection_matrix=[[0, 1, 1], [1, 0, 1]],
        cloud_computational_capacity=1.0,
        episode_time=1,
        task_arrive_probabilities=[0.0, 0.0],
        task_size_mins=[1.0, 1.0],
        task_size_maxs=[1.0, 1.0],
        task_size_distributions=["constant", "constant"],
        timeout_delay_mins=[5, 5],
        timeout_delay_maxs=[5, 5],
        timeout_delay_distributions=["constant", "constant"],
        priotiry_mins=[1, 1],
        priotiry_maxs=[1, 1],
        priotiry_distributions=["constant", "constant"],
        computational_density_mins=[1.0, 1.0],
        computational_density_maxs=[1.0, 1.0],
        computational_density_distributions=["constant", "constant"],
        drop_penalty_mins=[40, 40],
        drop_penalty_maxs=[40, 40],
        drop_penalty_distributions=["constant", "constant"],
        trace_recorder=trace_recorder,
    )
    env.reset()
    env.episode_id = 7
    env.current_time = 0
    env.tasks[0] = Task(
        size=1.0,
        arrival_time=0,
        timeout_delay=5,
        priotiry=1,
        computational_density=1.0,
        drop_penalty=40,
        origin_server_id=0,
        target_server_id=None,
        task_id=100,
        input_data_size=1.0,
        service_id=1,
        processing_density=1.0,
        timeout=5,
        source_node_id=0,
    )
    env.tasks[1] = None
    return env


class MleoCandidateLatencyContractTests(unittest.TestCase):
    def test_constructor_no_longer_raises(self) -> None:
        policy = MinimumLatencyEstimationOffloader()
        self.assertIsInstance(policy, MinimumLatencyEstimationOffloader)

    def test_candidate_rows_and_selection_are_emitted(self) -> None:
        recorder = TraceRecorder()
        env = build_tiny_env(recorder)
        policy = MinimumLatencyEstimationOffloader(
            number_of_actions=env.matchmakers[0].get_number_of_actions(),
            env=env,
            source_id=0,
            matchmaker=env.matchmakers[0],
        )
        with patch.object(policy, "_service_time", side_effect=[1, 1, 1, 1, 1]):
            action = policy.choose_action(np.zeros(2), np.zeros(2))
        self.assertIn(action, range(env.matchmakers[0].get_number_of_actions()))
        self.assertEqual(len(recorder.mleo_candidate_latency_traces), 3)
        self.assertEqual(sum(1 for row in recorder.mleo_candidate_latency_traces if row.is_selected), 1)

    def test_latency_components_and_tie_break_are_deterministic(self) -> None:
        recorder = TraceRecorder()
        env = build_tiny_env(recorder)
        env.servers[0].processing_queue.get_waiting_time = lambda: 2
        env.servers[0].offloading_queue.get_waiting_time = lambda: 3
        env.servers[1].estimate_public_queue_wait = lambda source_id: 4
        env.cloud.estimate_public_queue_wait = lambda source_id: 5
        policy = MinimumLatencyEstimationOffloader(
            number_of_actions=env.matchmakers[0].get_number_of_actions(),
            env=env,
            source_id=0,
            matchmaker=env.matchmakers[0],
        )
        with patch.object(policy, "_service_time", side_effect=[1, 1, 1, 1, 1]):
            action = policy.choose_action(np.zeros(2), np.zeros(2))
        rows = recorder.mleo_candidate_latency_traces
        local = next(row for row in rows if row.destination_type == "local")
        horiz = next(row for row in rows if row.destination_type == "horizontal_edge")
        cloud = next(row for row in rows if row.destination_type == "vertical_cloud")
        self.assertEqual(local.private_wait_estimate, 2.0)
        self.assertEqual(local.private_service_estimate, 1.0)
        self.assertEqual(local.total_estimated_latency, 3.0)
        self.assertEqual(horiz.offloading_wait_estimate, 3.0)
        self.assertEqual(horiz.transmission_estimate, 1.0)
        self.assertEqual(horiz.public_wait_estimate, 4.0)
        self.assertEqual(horiz.public_service_estimate, 1.0)
        self.assertEqual(horiz.total_estimated_latency, 9.0)
        self.assertEqual(cloud.offloading_wait_estimate, 3.0)
        self.assertEqual(cloud.transmission_estimate, 1.0)
        self.assertEqual(cloud.cloud_wait_estimate, 5.0)
        self.assertEqual(cloud.cloud_service_estimate, 1.0)
        self.assertEqual(cloud.total_estimated_latency, 10.0)
        self.assertEqual(action, local.raw_action_id)

    def test_validation_report_detects_trace_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            trace_dir = Path(tmpdir)
            for name in ("task_lifecycle.csv", "queue_trace.csv", "action_trace.csv", "episode_metrics.csv"):
                (trace_dir / name).write_text("episode_id,time,task_id\n1,0,1\n")
            (trace_dir / "mleo_candidate_latency_trace.csv").write_text(
                "episode_id,time,task_id,source_agent,raw_action_id,first_stage_decision,destination_type,destination_node_id,is_legal_candidate,is_selected,input_data_size,remaining_size,processing_density,required_cpu_cycles,arrival_time,absolute_deadline,timeout,private_wait_estimate,private_service_estimate,offloading_wait_estimate,transmission_estimate,public_wait_estimate,public_service_estimate,cloud_wait_estimate,cloud_service_estimate,total_estimated_latency,deadline_slack_estimate,estimated_deadline_violation,estimator_version,unavailable_fields_json,approximation_warnings_json\n"
                "1,0,1,0,0,local,local,,True,True,1,1,1,1,0,5,5,0,1,,,,,,,1,4,False,v1,[],[]\n"
            )
            report = build_validation_report(trace_dir)
            self.assertEqual(report["mleo_contract_status"], "paper_candidate_trace_ready")


if __name__ == "__main__":
    unittest.main()
