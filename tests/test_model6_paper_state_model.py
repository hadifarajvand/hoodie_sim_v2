from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

import numpy as np

from environment.environment import Environment
from environment.task import Task
from phase1_tracing import TraceRecorder
from training.trace_dataset import load_trace_dataset


class Model6PaperStateModelTests(unittest.TestCase):
    def _build_env(self, trace_recorder=None) -> Environment:
        env = Environment(
            static_frequency=0,
            number_of_servers=2,
            private_cpu_capacities=[1, 1],
            public_cpu_capacities=[1, 1],
            connection_matrix=np.array([[0, 1], [1, 0]]),
            cloud_computational_capacity=3,
            episode_time=1,
            task_arrive_probabilities=[0.0, 0.0],
            task_size_mins=[1.0, 1.0],
            task_size_maxs=[1.0, 1.0],
            task_size_distributions=["constant", "constant"],
            timeout_delay_mins=[10, 10],
            timeout_delay_maxs=[10, 10],
            timeout_delay_distributions=["constant", "constant"],
            priotiry_mins=[1, 1],
            priotiry_maxs=[1, 1],
            priotiry_distributions=["constant", "constant"],
            computational_density_mins=[0.297, 0.297],
            computational_density_maxs=[0.297, 0.297],
            computational_density_distributions=["constant", "constant"],
            drop_penalty_mins=[40, 40],
            drop_penalty_maxs=[40, 40],
            drop_penalty_distributions=["constant", "constant"],
            vertical_offloading_rate=7.0,
            trace_recorder=trace_recorder,
        )
        env.reset()
        return env

    def test_source_specific_public_queue_vector(self):
        env = self._build_env()
        cloud_task = Task(size=1.0, arrival_time=0, timeout_delay=10, computational_density=0.297, drop_penalty=40, origin_server_id=0, target_server_id=2, task_id=11)
        edge_task = Task(size=1.0, arrival_time=0, timeout_delay=10, computational_density=0.297, drop_penalty=40, origin_server_id=1, target_server_id=0, task_id=12)
        env.cloud.public_queue_manager.add_tasks([cloud_task], current_time=0)
        env.servers[0].public_queue_manager.add_tasks([edge_task], current_time=0)
        env._refresh_paper_state_history()

        state0 = env.get_paper_state(0)
        state1 = env.get_paper_state(1)

        self.assertEqual(state0["l_pub_n_prev"].shape, (3,))
        self.assertEqual(state1["l_pub_n_prev"].shape, (3,))
        self.assertEqual(state0["l_pub_n_prev"][0], 0.0)
        self.assertEqual(state0["l_pub_n_prev"][2], 1.0)
        self.assertEqual(state1["l_pub_n_prev"][2], 0.0)
        self.assertEqual(state1["l_pub_n_prev"][0], 1.0)
        self.assertFalse(np.isnan(state0["l_pub_n_prev"]).any())
        self.assertFalse(np.isnan(state1["l_pub_n_prev"]).any())

    def test_l_t_shape_and_no_nan(self):
        env = self._build_env()
        state = env.get_paper_state(0)
        self.assertEqual(state["L_t"].shape, (env.paper_state_window, env.number_of_servers + 1))
        self.assertEqual(state["active_load_vector"].shape, (env.number_of_servers + 1,))
        self.assertEqual(state["predicted_next_load"].shape, (env.number_of_servers + 1,))
        self.assertFalse(np.isnan(state["l_pub_n_prev"]).any())
        self.assertFalse(np.isnan(state["L_t"]).any())
        self.assertFalse(np.isnan(state["active_load_vector"]).any())
        self.assertFalse(np.isnan(state["predicted_next_load"]).any())
        self.assertEqual(state["predicted_next_load_method"], "persistence_baseline")
        self.assertFalse(state["paper_lstm_forecast"])
        self.assertTrue(any("persistence_baseline" in warning for warning in state["approximation_warnings"]))

    def test_paper_state_trace_export(self):
        recorder = TraceRecorder(trace_level="full")
        recorder.start_episode(0)
        env = self._build_env(trace_recorder=recorder)
        env._record_paper_state_traces()
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp)
            recorder.export(trace_dir)
            path = trace_dir / "paper_state_trace.csv"
            self.assertTrue(path.exists())
            with path.open(newline="") as f:
                rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), env.number_of_servers)
        self.assertIn("l_pub_n_prev_json", rows[0])
        self.assertIn("L_t_json", rows[0])
        self.assertIn("predicted_next_load_json", rows[0])
        self.assertIn("predicted_next_load_method", rows[0])
        self.assertIn("paper_lstm_forecast", rows[0])
        self.assertIn("state_vector_json", rows[0])
        self.assertIn("state_dim", rows[0])

    def test_trace_dataset_prefers_paper_state_trace(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp)
            (trace_dir / "task_lifecycle.csv").write_text(
                "episode_id,time,task_id,source_node,arrival_time,queue_enter_time,final_status,input_data_size,timeout_delay,computational_density,drop_penalty,selected_action\n"
                "0,1,1,0,1,1,completed,1,10,0.297,40,0\n"
            )
            (trace_dir / "queue_trace.csv").write_text(
                "episode_id,time,node_id,queue_type,queue_length\n"
                "0,1,0,public:0,1\n"
            )
            (trace_dir / "action_trace.csv").write_text(
                "episode_id,time,agent_id,selected_action,reward_received,policy_name\n"
                "0,1,0,0,0,HOODIE\n"
            )
            (trace_dir / "episode_metrics.csv").write_text("episode_id,reward\n0,0\n")
            (trace_dir / "paper_state_trace.csv").write_text(
                "episode_id,time,agent_id,x_n_t,task_id,eta_n,w_priv_n,w_off_n,l_pub_n_prev_json,active_load_vector_json,L_t_json,predicted_next_load_json,predicted_next_load_method,paper_lstm_forecast,unavailable_fields_json,approximation_warnings_json,state_vector_json,state_dim\n"
                "0,1,0,1,1,1,0,0,\"[0,1,2]\",\"[0,0,0]\",\"[[0,0,0],[0,0,0],[0,0,0],[0,0,0]]\",\"[0,0,0]\",persistence_baseline,False,\"[]\",\"[]\",\"[1,0,0,0,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0]\",19\n"
            )
            transitions, summary = load_trace_dataset(trace_dir)
        self.assertTrue(summary.paper_state_trace_present)
        self.assertEqual(summary.state_source, "runtime_paper_state_trace")
        self.assertTrue(transitions)
        self.assertEqual(transitions[0].state.shape[0], 19)

    def test_trace_dataset_supports_cloud_public_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp)
            (trace_dir / "task_lifecycle.csv").write_text(
                "episode_id,time,task_id,source_node,arrival_time,queue_enter_time,final_status,input_data_size,timeout_delay,computational_density,drop_penalty,selected_action\n"
                "0,1,1,0,1,1,completed,1,10,0.297,40,0\n"
                "0,1,2,1,1,1,completed,1,10,0.297,40,0\n"
            )
            (trace_dir / "queue_trace.csv").write_text(
                "episode_id,time,node_id,queue_type,queue_length\n"
                "0,0,1,public:0,4\n"
                "0,0,0,public:1,5\n"
                "0,0,2,cloud_public:0,7\n"
                "0,0,2,cloud_public:1,9\n"
            )
            (trace_dir / "action_trace.csv").write_text(
                "episode_id,time,agent_id,selected_action,reward_received,policy_name\n"
                "0,1,0,0,0,HOODIE\n"
                "0,1,1,0,0,HOODIE\n"
            )
            (trace_dir / "episode_metrics.csv").write_text("episode_id,reward\n0,0\n")
            transitions, summary = load_trace_dataset(trace_dir)
        self.assertTrue(transitions)
        self.assertEqual(summary.state_dim, len(transitions[0].state))
        self.assertEqual(transitions[0].l_pub_n_prev.shape, (3,))
        self.assertFalse(np.isnan(transitions[0].l_pub_n_prev).any())
        self.assertEqual(transitions[0].l_pub_n_prev[2], 7.0)
        self.assertEqual(transitions[1].l_pub_n_prev[0], 5.0)
        self.assertEqual(transitions[1].l_pub_n_prev[2], 9.0)


if __name__ == "__main__":
    unittest.main()
