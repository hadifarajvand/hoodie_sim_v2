from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from phase4_validation import ValidationConfig, assess_readiness, run_validation


ROOT = Path(__file__).resolve().parents[1]


def _write_minimal_trace(trace_dir: Path, *, invalid_action_ratio: float = 0.0, state_dim: int = 8, nonterminal_copy: int = 0, paper_state: bool = True) -> None:
    trace_dir.mkdir(parents=True, exist_ok=True)
    (trace_dir / "task_lifecycle.csv").write_text(
        "task_id,episode_id,arrival_time,source_node,queue_enter_time,service_start_time,service_end_time,completion_time,drop_time,selected_action,processing_node,latency,waiting_time,service_time,final_status,drop_reason\n"
        "1,0,0,0,0,1,2,2,,0,2,1,1,1,completed,\n"
    )
    (trace_dir / "queue_trace.csv").write_text(
        "episode_id,time,node_id,queue_type,queue_length,arrivals,departures,drops,cpu_allocated\n"
        "0,0,0,private,1,1,0,0,1\n"
    )
    is_valid = "False" if invalid_action_ratio > 0 else "True"
    invalid_reason = "adjacency violation" if invalid_action_ratio > 0 else ""
    (trace_dir / "action_trace.csv").write_text(
        "episode_id,time,agent_id,observation_shape,selected_action,target_node,reward_received,raw_action_id,first_stage_decision,destination_node_id,destination_type,is_valid,invalid_reason,adjacency_allowed,cloud_target,d_n_1,d_nk_2\n"
        f"0,0,0,\"[8]\",1,1,-4,1,offload,1,horizontal_edge,{is_valid},{invalid_reason},True,False,1,\"{{\\\"1\\\": 1}}\"\n"
    )
    forecast = "True" if paper_state else "False"
    pred_method = "lstm_forecast" if paper_state else "persistence_baseline"
    (trace_dir / "paper_state_trace.csv").write_text(
        "episode_id,time,agent_id,task_id,eta_n,w_priv_n,w_off_n,l_pub_n_prev_json,active_load_vector_json,L_t_json,predicted_next_load_json,predicted_next_load_method,paper_lstm_forecast,unavailable_fields_json,approximation_warnings_json,state_vector_json,state_dim\n"
        f"0,0,0,1,5,2,1,\"[0,0]\",\"[1,0,0]\",\"[[1,0,0],[0,1,0],[0,0,1],[1,1,1]]\",\"[1,0,0]\",{pred_method},{forecast},\"[]\",\"[]\",\"[5,2,1,0,0,1,0,0]\",{state_dim}\n"
    )
    (trace_dir / "episode_metrics.csv").write_text(
        "episode_id,total_tasks,completed_tasks,dropped_tasks,pending_tasks,average_latency,average_waiting_time,average_service_time,drop_ratio,average_queue_length,total_reward,mean_reward\n"
        "0,1,1,0,0,2,1,1,0,1,-4,-4\n"
    )


class Phase4ValidationTests(unittest.TestCase):
    def test_readiness_rules_fail_when_required_signals_are_missing(self):
        report = {
            "episodes_completed": 200,
            "episode_metrics_count": 200,
            "paper_state_trace_present": False,
            "invalid_action_ratio": 0.0,
            "non_neighbor_offload_count": 0,
            "self_offload_violation_count": 0,
            "state_dim_min": 8,
            "state_dim_max": 8,
            "L_t_shape": [4, 21],
            "active_load_vector_length": 21,
            "predicted_next_load_length": 21,
            "predicted_next_load_method_counts": {"lstm_forecast": 1},
            "paper_lstm_forecast_false_count": 0,
            "transitions": 1,
            "state_source": "runtime_paper_state_trace",
            "next_state_source": "runtime_paper_state_trace",
            "nonterminal_next_state_copy_count": 0,
            "paper_performance_claims_made": False,
        }
        readiness = assess_readiness(report)
        self.assertFalse(readiness["ready_for_phase5_figures"])
        self.assertIn("paper_state_trace_present", readiness["blockers"])

    def test_readiness_rules_fail_on_invalid_actions(self):
        report = {
            "episodes_completed": 200,
            "episode_metrics_count": 200,
            "paper_state_trace_present": True,
            "invalid_action_ratio": 0.5,
            "non_neighbor_offload_count": 0,
            "self_offload_violation_count": 0,
            "state_dim_min": 8,
            "state_dim_max": 8,
            "L_t_shape": [4, 21],
            "active_load_vector_length": 21,
            "predicted_next_load_length": 21,
            "predicted_next_load_method_counts": {"lstm_forecast": 1},
            "paper_lstm_forecast_false_count": 0,
            "transitions": 1,
            "state_source": "runtime_paper_state_trace",
            "next_state_source": "runtime_paper_state_trace",
            "nonterminal_next_state_copy_count": 0,
            "paper_performance_claims_made": False,
        }
        readiness = assess_readiness(report)
        self.assertFalse(readiness["ready_for_phase5_figures"])
        self.assertIn("invalid_action_ratio", readiness["blockers"])

    def test_readiness_rules_fail_when_state_dim_is_obsolete(self):
        report = {
            "episodes_completed": 200,
            "episode_metrics_count": 200,
            "paper_state_trace_present": True,
            "invalid_action_ratio": 0.0,
            "non_neighbor_offload_count": 0,
            "self_offload_violation_count": 0,
            "state_dim_min": 2,
            "state_dim_max": 2,
            "L_t_shape": [4, 21],
            "active_load_vector_length": 21,
            "predicted_next_load_length": 21,
            "predicted_next_load_method_counts": {"lstm_forecast": 1},
            "paper_lstm_forecast_false_count": 0,
            "transitions": 1,
            "state_source": "runtime_paper_state_trace",
            "next_state_source": "runtime_paper_state_trace",
            "nonterminal_next_state_copy_count": 0,
            "paper_performance_claims_made": False,
        }
        readiness = assess_readiness(report)
        self.assertFalse(readiness["ready_for_phase5_figures"])
        self.assertIn("state_dim_stable", readiness["blockers"])

    def test_readiness_rules_fail_when_nonterminal_next_state_is_copied(self):
        report = {
            "episodes_completed": 200,
            "episode_metrics_count": 200,
            "paper_state_trace_present": True,
            "invalid_action_ratio": 0.0,
            "non_neighbor_offload_count": 0,
            "self_offload_violation_count": 0,
            "state_dim_min": 8,
            "state_dim_max": 8,
            "L_t_shape": [4, 21],
            "active_load_vector_length": 21,
            "predicted_next_load_length": 21,
            "predicted_next_load_method_counts": {"lstm_forecast": 1},
            "paper_lstm_forecast_false_count": 0,
            "transitions": 1,
            "state_source": "runtime_paper_state_trace",
            "next_state_source": "runtime_paper_state_trace",
            "nonterminal_next_state_copy_count": 1,
            "paper_performance_claims_made": False,
        }
        readiness = assess_readiness(report)
        self.assertFalse(readiness["ready_for_phase5_figures"])
        self.assertIn("nonterminal_next_state_copy_count", readiness["blockers"])

    def test_synthetic_valid_summary_can_pass_with_warning(self):
        report = {
            "episodes_completed": 200,
            "episode_metrics_count": 200,
            "paper_state_trace_present": True,
            "invalid_action_ratio": 0.0,
            "non_neighbor_offload_count": 0,
            "self_offload_violation_count": 0,
            "state_dim_min": 8,
            "state_dim_max": 8,
            "L_t_shape": [4, 21],
            "active_load_vector_length": 21,
            "predicted_next_load_length": 21,
            "predicted_next_load_method_counts": {"persistence_baseline": 1},
            "paper_lstm_forecast_false_count": 1,
            "transitions": 1,
            "state_source": "runtime_paper_state_trace",
            "next_state_source": "runtime_paper_state_trace",
            "nonterminal_next_state_copy_count": 0,
            "paper_performance_claims_made": False,
        }
        readiness = assess_readiness(report)
        self.assertTrue(readiness["ready_for_phase5_figures"])
        self.assertIn("paper_lstm_forecast_true_or_justified_false", readiness["warnings"])

    def test_report_marks_no_paper_performance_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            out_dir.mkdir(parents=True, exist_ok=True)
            report_path = out_dir / "phase4_validation_report.json"
            report_path.write_text(json.dumps({"paper_performance_claims_made": False}))
            parsed = json.loads(report_path.read_text())
            self.assertFalse(parsed["paper_performance_claims_made"])

    def test_smoke_mode_writes_required_reports_and_does_not_copy_raw_traces_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "trace"
            out_dir = Path(tmp) / "out"

            def fake_run(cmd, cwd=None, capture_output=None, text=None, check=None):
                if "main.py" in cmd:
                    _write_minimal_trace(trace_dir)
                elif "training.train_phase3" in cmd:
                    (out_dir / "phase3_model.chkpt").write_text(json.dumps({"state_dim": 8}))
                    (out_dir / "training_metrics.json").write_text(json.dumps({"epochs": 1}))
                    (out_dir / "phase3_training_report.json").write_text(json.dumps({"paper_claims_made": False}))
                return __import__("subprocess").CompletedProcess(cmd, 0, stdout="", stderr="")

            config = ValidationConfig(
                episodes=1,
                output_dir=str(out_dir),
                seed=42,
                mode="smoke",
                raw_trace_dir=str(trace_dir),
                keep_raw_traces=False,
                train_after_run=True,
                batch_size=1,
                checkpoint_every=1,
                sequence_length=1,
                max_sample_rows=5,
                fail_on_missing_paper_state=True,
                fail_on_invalid_actions=True,
                fail_on_non_lstm_forecast=True,
                timestamp="2026-01-01T00:00:00Z",
                branch="test",
                commit="abc123",
            )
            with patch("phase4_validation.subprocess.run", side_effect=fake_run):
                report = run_validation(config)
            self.assertIn("phase4_validation_report.json", {p.name for p in out_dir.iterdir()})
            self.assertIn("episode_metrics_summary.csv", {p.name for p in out_dir.iterdir()})
            self.assertIn("policy_action_summary.csv", {p.name for p in out_dir.iterdir()})
            self.assertIn("state_lstm_summary.json", {p.name for p in out_dir.iterdir()})
            self.assertIn("readiness_matrix.csv", {p.name for p in out_dir.iterdir()})
            self.assertFalse((out_dir / "raw_traces").exists())
            self.assertIn("paper_performance_claims_made", report)
            self.assertFalse(report["paper_performance_claims_made"])


if __name__ == "__main__":
    unittest.main()
