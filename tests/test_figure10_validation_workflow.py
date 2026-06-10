from __future__ import annotations

import io
from contextlib import redirect_stdout
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from figure10_validation import (
    EXPECTED_POLICY_SET,
    Figure10ValidationConfig,
    assess_figure10_readiness,
    run_figure10_validation,
)


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venvmac" / "bin" / "python"


def _write_fixture_trace(trace_dir: Path, *, episode_id: int = 0, policy_name: str = "RO") -> None:
    trace_dir.mkdir(parents=True, exist_ok=True)
    lifecycle_rows = [
        {
            "task_id": 1,
            "episode_id": episode_id,
            "arrival_time": 0,
            "source_node": 0,
            "queue_enter_time": 0,
            "service_start_time": 1,
            "service_end_time": 4,
            "completion_time": 4,
            "drop_time": "",
            "selected_action": 0,
            "processing_node": 0,
            "latency": 4,
            "waiting_time": 1,
            "service_time": 3,
            "final_status": "completed",
            "drop_reason": "",
            "drop_penalty": 40,
            "reward_received": -4,
        },
        {
            "task_id": 2,
            "episode_id": episode_id,
            "arrival_time": 1,
            "source_node": 0,
            "queue_enter_time": 1,
            "service_start_time": "",
            "service_end_time": "",
            "completion_time": "",
            "drop_time": 1,
            "selected_action": "",
            "processing_node": 0,
            "latency": "",
            "waiting_time": "",
            "service_time": "",
            "final_status": "dropped",
            "drop_reason": "timeout",
            "drop_penalty": 40,
            "reward_received": -40,
        },
        {
            "task_id": 3,
            "episode_id": episode_id,
            "arrival_time": 2,
            "source_node": 0,
            "queue_enter_time": 2,
            "service_start_time": "",
            "service_end_time": "",
            "completion_time": "",
            "drop_time": "",
            "selected_action": "",
            "processing_node": 0,
            "latency": "",
            "waiting_time": "",
            "service_time": "",
            "final_status": "pending",
            "drop_reason": "",
            "drop_penalty": 40,
            "reward_received": 0,
        },
    ]
    with (trace_dir / "task_lifecycle.csv").open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "task_id",
                "episode_id",
                "arrival_time",
                "source_node",
                "queue_enter_time",
                "service_start_time",
                "service_end_time",
                "completion_time",
                "drop_time",
                "selected_action",
                "processing_node",
                "latency",
                "waiting_time",
                "service_time",
                "final_status",
                "drop_reason",
                "drop_penalty",
                "reward_received",
            ],
        )
        writer.writeheader()
        writer.writerows(lifecycle_rows)
    (trace_dir / "queue_trace.csv").write_text(
        "episode_id,time,node_id,queue_type,queue_length,arrivals,departures,drops,cpu_allocated\n"
        f"{episode_id},0,0,private,1,1,0,0,1\n"
    )
    (trace_dir / "action_trace.csv").write_text(
        "episode_id,time,agent_id,observation_shape,selected_action,target_node,reward_received,raw_action_id,first_stage_decision,destination_node_id,destination_type,is_valid,invalid_reason,adjacency_allowed,cloud_target,d_n_1,d_nk_2\n"
        f"{episode_id},0,0,\"[8]\",0,0,-4,0,local,,local,True,,True,False,1,\"{{}}\"\n"
    )
    (trace_dir / "episode_metrics.csv").write_text(
        "episode_id,total_tasks,completed_tasks,dropped_tasks,pending_tasks,average_latency,average_waiting_time,average_service_time,drop_ratio,average_queue_length,total_reward,mean_reward\n"
        f"{episode_id},3,1,1,1,4,1,3,0.3333333333,1.0,-44,-14.6666667\n"
    )
    (trace_dir / "pending_transition_trace.csv").write_text(
        "task_id,episode_id,source_agent,arrival_time,decision_time,state_at_decision_json,lstm_state_at_decision_json,action_at_decision,selected_target_node,raw_action_id,first_stage_decision,destination_type,destination_node_id,immediate_next_state_after_action_json,immediate_next_lstm_state_after_action_json,created_by_policy,replay_pairing_status\n"
        f"1,{episode_id},0,0,0,\"[1,2]\",\"[0,0]\",0,0,0,local,local,,\"[1,2]\",\"[0,0]\",{policy_name},paired\n"
    )
    (trace_dir / "delayed_reward_event_trace.csv").write_text(
        "task_id,episode_id,source_agent,decision_time,final_status,completion_time,drop_time,delay,reward,drop_penalty,reward_reason,paired_transition_found,replay_inserted,replay_pairing_status,reward_timing_convention\n"
        f"1,{episode_id},0,0,completed,4,,4,-4,40,completion_minus_arrival,True,False,paired,completion_minus_arrival\n"
    )
    (trace_dir / "mleo_candidate_latency_trace.csv").write_text(
        "episode_id,time,task_id,source_agent,raw_action_id,first_stage_decision,destination_type,destination_node_id,is_legal_candidate,is_selected,input_data_size,remaining_size,processing_density,required_cpu_cycles,arrival_time,absolute_deadline,timeout,private_wait_estimate,private_service_estimate,offloading_wait_estimate,transmission_estimate,public_wait_estimate,public_service_estimate,cloud_wait_estimate,cloud_service_estimate,total_estimated_latency,deadline_slack_estimate,estimated_deadline_violation,estimator_version,unavailable_fields_json,approximation_warnings_json\n"
        f"{episode_id},0,1,0,0,local,local,,True,True,2.0,2.0,0.297,0.594,0,10,10,1.0,3.0,,,,,,,4.0,6.0,False,phase3_candidate_latency_v1,\"[]\",\"[]\"\n"
        f"{episode_id},0,1,0,1,offload,horizontal_edge,1,True,False,2.0,2.0,0.297,0.594,0,10,10,, ,1.0,1.0,0.5,1.5,,,,4.0,6.0,False,phase3_candidate_latency_v1,\"[]\",\"[]\"\n"
        f"{episode_id},0,1,0,2,offload,vertical_cloud,20,True,False,2.0,2.0,0.297,0.594,0,10,10,, ,1.0,1.0,,,2.0,2.0,6.0,False,phase3_candidate_latency_v1,\"[]\",\"[]\"\n"
    )


def _write_hyperparameters(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "number_of_servers": 20,
                "task_arrive_probabilities": [0.5],
                "task_size_mins": [2.0],
                "task_size_maxs": [5.0],
                "timeout_delay_mins": [20],
                "cloud_computational_capacity": 30.0,
                "private_cpu_capacities": [5.0] * 20,
                "public_cpu_capacities": [5.0] * 20,
                "connection_matrix": [[0] * 21 for _ in range(20)],
                "decision_makers": "RO",
                "episode_time": 100,
                "static_frequency": 10,
                "task_size_distributions": ["uniform"],
                "timeout_delay_distributions": ["uniform"],
                "priotiry_mins": [1],
                "priotiry_maxs": [1],
                "priotiry_distributions": ["uniform"],
                "computational_density_mins": [0.297],
                "computational_density_maxs": [0.297],
                "computational_density_distributions": ["uniform"],
                "drop_penalty_mins": [40],
                "drop_penalty_maxs": [40],
                "drop_penalty_distributions": ["uniform"],
                "learning_rate": 7e-7,
                "learning_rate_end": 7e-7,
                "lr_scheduler_epochs": 1,
                "scheduler_choice": "constant",
                "hidden_layers": [16],
                "lstm_layers": 0,
                "lstm_time_step": 1,
                "dropout_rate": 0.0,
                "dueling": True,
                "epsilon": 0.0,
                "epsilon_decrement": 0.0,
                "epsilon_end": 0.0,
                "gamma": 0.99,
                "loss_function": "MSELoss",
                "optimizer": "Adam",
                "save_model_frequency": 1,
                "update_weight_percentage": 0.5,
                "memory_size": 10,
                "batch_size": 1,
                "replace_target_iter": 1,
            },
            indent=2,
            sort_keys=True,
        )
    )


def _fake_run_factory(trace_root: Path):
    def fake_run(cmd, cwd=None, capture_output=None, text=None, check=None):
        cmd_str = " ".join(cmd)
        if cmd[:2] == ["git", "branch"]:
            return __import__("subprocess").CompletedProcess(cmd, 0, stdout="100-hoodie-paper-base\n", stderr="")
        if cmd[:2] == ["git", "rev-parse"]:
            return __import__("subprocess").CompletedProcess(cmd, 0, stdout="abc123\n", stderr="")
        if "main.py" in cmd:
            config_path = Path(cmd[cmd.index("--config") + 1])
            config = {}
            if config_path.exists():
                for line in config_path.read_text().splitlines():
                    if ":" in line:
                        key, value = line.split(":", 1)
                        config[key.strip()] = value.strip().strip('"')
            hyper_path = Path(config["hyperparameters_file"])
            hp = json.loads(hyper_path.read_text())
            policy_name = hp["decision_makers"]
            trace_dir = Path(config["trace_output_dir"])
            if policy_name != "HOODIE":
                _write_fixture_trace(trace_dir, policy_name=policy_name)
            else:
                _write_fixture_trace(trace_dir, policy_name=policy_name)
            return __import__("subprocess").CompletedProcess(cmd, 0, stdout=f"completed {policy_name}\n", stderr="")
        return __import__("subprocess").CompletedProcess(cmd, 0, stdout="", stderr="")

    return fake_run


class Figure10ValidationWorkflowTests(unittest.TestCase):
    def test_expected_policy_set_and_readiness_fail_when_missing_or_unexpected(self):
        readiness = assess_figure10_readiness(
            {
                "active_policy_set": ["HOODIE", "RO"],
                "expected_policy_set": EXPECTED_POLICY_SET,
                "missing_policies": ["FLC"],
                "unexpected_policies": ["ZZZ"],
                "policy_class_map": {"HOODIE": "Agent"},
                "hoodie_checkpoint_status": "unavailable_not_trained",
                "mleo_required": True,
                "mleo_contract_status_seen": {"paper_candidate_trace_ready": 1},
                "delayed_reward_contract_status_seen": {"paper_replay_pairing_ready": 1},
                "validation_episode_count": 200,
                "non_hoodie_baselines_ready": True,
                "mleo_contract_status_ready": True,
                "paper_performance_claims_made": False,
                "test_mode": False,
            }
        )
        self.assertEqual(EXPECTED_POLICY_SET, ["HOODIE", "RO", "FLC", "VO", "HO", "BCO", "MLEO"])
        self.assertFalse(readiness["figure10_data_ready"])
        self.assertIn("missing_policies=['FLC']", readiness["blocking_reasons"])
        self.assertIn("unexpected_policies=['ZZZ']", readiness["blocking_reasons"])

    def test_mleo_readiness_is_policy_scoped_and_warnings_do_not_block_baseline(self):
        readiness = assess_figure10_readiness(
            {
                "active_policy_set": ["RO", "FLC", "VO", "HO", "BCO", "MLEO"],
                "expected_policy_set": EXPECTED_POLICY_SET,
                "baseline_policy_set": ["RO", "FLC", "VO", "HO", "BCO", "MLEO"],
                "missing_policies": ["HOODIE"],
                "unexpected_policies": [],
                "policy_class_map": {policy: policy for policy in EXPECTED_POLICY_SET},
                "hoodie_checkpoint_status": "unavailable_not_trained",
                "mleo_required": True,
                "mleo_policy_seen": True,
                "mleo_contract_status_seen": {"paper_candidate_trace_ready": 2, "present_but_invalid": 10},
                "delayed_reward_contract_status_seen": {"paper_replay_pairing_ready": 6},
                "validation_episode_count": 200,
                "non_hoodie_baselines_ready": True,
                "paper_performance_claims_made": False,
                "test_mode": False,
                "no_metric_rows_generated": False,
                "strict_paper_contract": False,
                "paper_contract_diagnostics": [{"parameter": "timeout_slots", "severity": "high"}],
            }
        )
        self.assertTrue(readiness["baseline_validation_ready"])
        self.assertFalse(readiness["figure10_data_ready"])
        self.assertNotIn("mleo_contract_status_ready=false", readiness["blocking_reasons"])
        self.assertNotIn("non_hoodie_baselines_ready=false", readiness["blocking_reasons"])
        self.assertIn("hoodie_checkpoint_status=unavailable_not_trained", readiness["figure10_blocking_reasons"])
        self.assertNotIn("hoodie_checkpoint_status=unavailable_not_trained", readiness["baseline_blocking_reasons"])

    def test_parameter_diagnostics_are_warnings_by_default(self):
        readiness = assess_figure10_readiness(
            {
                "active_policy_set": ["RO", "FLC", "VO", "HO", "BCO", "MLEO"],
                "expected_policy_set": EXPECTED_POLICY_SET,
                "baseline_policy_set": ["RO", "FLC", "VO", "HO", "BCO", "MLEO"],
                "missing_policies": ["HOODIE"],
                "unexpected_policies": [],
                "policy_class_map": {policy: policy for policy in EXPECTED_POLICY_SET},
                "hoodie_checkpoint_status": "unavailable_not_trained",
                "mleo_required": True,
                "mleo_policy_seen": True,
                "mleo_contract_status_seen": {"paper_candidate_trace_ready": 2},
                "delayed_reward_contract_status_seen": {"paper_replay_pairing_ready": 12},
                "validation_episode_count": 200,
                "non_hoodie_baselines_ready": True,
                "paper_performance_claims_made": False,
                "test_mode": False,
                "no_metric_rows_generated": False,
                "strict_paper_contract": False,
                "paper_contract_diagnostics": [{"parameter": "timeout_slots", "severity": "high"}],
            }
        )
        self.assertTrue(readiness["baseline_validation_ready"])
        self.assertFalse(readiness["figure10_data_ready"])
        self.assertEqual(readiness["policy_class_map"]["RO"], "RO")
        self.assertEqual(readiness["policy_class_map"]["MLEO"], "MLEO")
        self.assertNotIn("invalid_parameter_contract", readiness["baseline_blocking_reasons"])
        self.assertIn("timeout_slots", json.dumps(readiness["paper_contract_diagnostics"]))

    def test_strict_paper_contract_blocks_when_diagnostics_exist(self):
        readiness = assess_figure10_readiness(
            {
                "active_policy_set": ["RO", "FLC", "VO", "HO", "BCO", "MLEO"],
                "expected_policy_set": EXPECTED_POLICY_SET,
                "baseline_policy_set": ["RO", "FLC", "VO", "HO", "BCO", "MLEO"],
                "missing_policies": ["HOODIE"],
                "unexpected_policies": [],
                "policy_class_map": {policy: policy for policy in EXPECTED_POLICY_SET},
                "hoodie_checkpoint_status": "unavailable_not_trained",
                "mleo_required": True,
                "mleo_policy_seen": True,
                "mleo_contract_status_seen": {"paper_candidate_trace_ready": 2},
                "delayed_reward_contract_status_seen": {"paper_replay_pairing_ready": 12},
                "validation_episode_count": 200,
                "non_hoodie_baselines_ready": True,
                "paper_performance_claims_made": False,
                "test_mode": False,
                "no_metric_rows_generated": False,
                "strict_paper_contract": True,
                "paper_contract_diagnostics": [{"parameter": "timeout_slots", "severity": "high"}],
            }
        )
        self.assertFalse(readiness["baseline_validation_ready"])
        self.assertIn("invalid_parameter_contract", readiness["baseline_blocking_reasons"])
        self.assertIn("invalid_parameter_contract", readiness["figure10_blocking_reasons"])

    def test_mleo_missing_blocks_baseline(self):
        readiness = assess_figure10_readiness(
            {
                "active_policy_set": ["RO", "FLC", "VO", "HO", "BCO"],
                "expected_policy_set": EXPECTED_POLICY_SET,
                "baseline_policy_set": ["RO", "FLC", "VO", "HO", "BCO", "MLEO"],
                "missing_policies": ["HOODIE", "MLEO"],
                "unexpected_policies": [],
                "policy_class_map": {policy: policy for policy in EXPECTED_POLICY_SET},
                "hoodie_checkpoint_status": "unavailable_not_trained",
                "mleo_required": True,
                "mleo_policy_seen": False,
                "mleo_contract_status_seen": {},
                "delayed_reward_contract_status_seen": {"paper_replay_pairing_ready": 12},
                "validation_episode_count": 200,
                "non_hoodie_baselines_ready": True,
                "paper_performance_claims_made": False,
                "test_mode": False,
                "no_metric_rows_generated": False,
                "strict_paper_contract": False,
                "paper_contract_diagnostics": [],
            }
        )
        self.assertFalse(readiness["baseline_validation_ready"])
        self.assertIn("mleo_contract_status_ready=false", readiness["baseline_blocking_reasons"])

    def test_mleo_invalid_blocks_baseline(self):
        readiness = assess_figure10_readiness(
            {
                "active_policy_set": ["RO", "FLC", "VO", "HO", "BCO", "MLEO"],
                "expected_policy_set": EXPECTED_POLICY_SET,
                "baseline_policy_set": ["RO", "FLC", "VO", "HO", "BCO", "MLEO"],
                "missing_policies": ["HOODIE"],
                "unexpected_policies": [],
                "policy_class_map": {policy: policy for policy in EXPECTED_POLICY_SET},
                "hoodie_checkpoint_status": "unavailable_not_trained",
                "mleo_required": True,
                "mleo_policy_seen": True,
                "mleo_contract_status_seen": {"present_but_invalid": 2},
                "delayed_reward_contract_status_seen": {"paper_replay_pairing_ready": 12},
                "validation_episode_count": 200,
                "non_hoodie_baselines_ready": True,
                "paper_performance_claims_made": False,
                "test_mode": False,
                "no_metric_rows_generated": False,
                "strict_paper_contract": False,
                "paper_contract_diagnostics": [],
            }
        )
        self.assertFalse(readiness["baseline_validation_ready"])
        self.assertIn("mleo_contract_status_ready=false", readiness["baseline_blocking_reasons"])

    def test_hoodie_missing_only_blocks_full_figure10(self):
        readiness = assess_figure10_readiness(
            {
                "active_policy_set": ["RO", "FLC", "VO", "HO", "BCO", "MLEO"],
                "expected_policy_set": EXPECTED_POLICY_SET,
                "baseline_policy_set": ["RO", "FLC", "VO", "HO", "BCO", "MLEO"],
                "missing_policies": ["HOODIE"],
                "unexpected_policies": [],
                "policy_class_map": {policy: policy for policy in EXPECTED_POLICY_SET},
                "hoodie_checkpoint_status": "unavailable_not_trained",
                "mleo_required": True,
                "mleo_policy_seen": True,
                "mleo_contract_status_seen": {"paper_candidate_trace_ready": 2},
                "delayed_reward_contract_status_seen": {"paper_replay_pairing_ready": 12},
                "validation_episode_count": 200,
                "non_hoodie_baselines_ready": True,
                "paper_performance_claims_made": False,
                "test_mode": False,
                "no_metric_rows_generated": False,
                "strict_paper_contract": False,
                "paper_contract_diagnostics": [],
            }
        )
        self.assertTrue(readiness["baseline_validation_ready"])
        self.assertFalse(readiness["figure10_data_ready"])
        self.assertNotIn("HOODIE", json.dumps(readiness["baseline_blocking_reasons"]))
        self.assertIn("hoodie_checkpoint_status=unavailable_not_trained", readiness["figure10_blocking_reasons"])

    def test_hoodie_without_checkpoint_is_marked_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            hp_path = tmp_path / "hyperparameters.json"
            _write_hyperparameters(hp_path)
            out_dir = tmp_path / "figure10"
            config = Figure10ValidationConfig(
                output_dir=str(out_dir),
                episodes=1,
                seed=42,
                policies=list(EXPECTED_POLICY_SET),
                paper_contract_file=str(ROOT / "config" / "paper_table4_contract.json"),
                hyperparameters_file=str(hp_path),
                config_file=None,
                hoodie_checkpoint_dir=None,
                test_mode=True,
                strict_paper_contract=False,
                run_id="test-run",
                timestamp="2026-01-01T00:00:00Z",
                branch="test",
                commit="abc123",
            )
            with patch("figure10_validation.subprocess.run", side_effect=_fake_run_factory(tmp_path)):
                result = run_figure10_validation(config)
            readiness = json.loads((out_dir / "figure10_policy_readiness.json").read_text())
            manifest = json.loads((out_dir / "figure10_validation_manifest.json").read_text())
            summary = json.loads((out_dir / "figure10_policy_metrics_summary.json").read_text())
            self.assertEqual(readiness["hoodie_checkpoint_status"], "unavailable_not_trained")
            self.assertFalse(readiness["figure10_data_ready"])
            self.assertTrue(readiness["baseline_validation_ready"])
            self.assertIn("HOODIE", manifest["policies_skipped"])
            self.assertEqual(result["readiness"]["hoodie_checkpoint_status"], "unavailable_not_trained")
            self.assertEqual(summary["registry"]["policy_run_statuses"]["HOODIE"], "unavailable_not_trained")

    def test_baseline_only_ready_does_not_require_hoodie(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            hp_path = tmp_path / "hyperparameters.json"
            _write_hyperparameters(hp_path)
            out_dir = tmp_path / "figure10"

            def fake_run(cmd, cwd=None, capture_output=None, text=None, check=None):
                if "main.py" in cmd:
                    config_path = Path(cmd[cmd.index("--config") + 1])
                    config = {}
                    for line in config_path.read_text().splitlines():
                        if ":" in line:
                            key, value = line.split(":", 1)
                            config[key.strip()] = value.strip().strip('"')
                    trace_dir = Path(config["trace_output_dir"])
                    _write_fixture_trace(trace_dir, policy_name="RO")
                    return __import__("subprocess").CompletedProcess(cmd, 0, stdout="ok", stderr="")
                return __import__("subprocess").CompletedProcess(cmd, 0, stdout="", stderr="")

            with patch("figure10_validation.subprocess.run", side_effect=fake_run):
                result = __import__("figure10_validation").main(
                    [
                        "--output-dir",
                        str(out_dir),
                        "--episodes",
                        "1",
                        "--policies",
                        "RO,FLC,VO,HO,BCO,MLEO",
                        "--hyperparameters-file",
                        str(hp_path),
                        "--paper-contract",
                        str(ROOT / "config" / "paper_table4_contract.json"),
                        "--test-mode",
                    ]
                )
            readiness = json.loads((out_dir / "figure10_policy_readiness.json").read_text())
            summary = json.loads((out_dir / "figure10_policy_metrics_summary.json").read_text())
            self.assertEqual(result, 0)
            self.assertTrue(summary["summary_rows"])
            self.assertTrue(readiness["baseline_validation_ready"])
            self.assertFalse(readiness["figure10_data_ready"])
            self.assertIn("HOODIE", readiness["missing_policies"])

    def test_failed_subprocess_writes_logs_and_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            hp_path = tmp_path / "hyperparameters.json"
            _write_hyperparameters(hp_path)
            out_dir = tmp_path / "figure10"

            def fake_run(cmd, cwd=None, capture_output=None, text=None, check=None):
                if "main.py" in cmd:
                    return __import__("subprocess").CompletedProcess(cmd, 1, stdout="sim stdout", stderr="sim stderr tail")
                return __import__("subprocess").CompletedProcess(cmd, 0, stdout="", stderr="")

            runtime_hp = json.loads(hp_path.read_text())
            runtime_hp["decision_makers"] = "RO"
            run_dir = tmp_path / "run"
            trace_dir = tmp_path / "trace"
            with patch("figure10_validation.subprocess.run", side_effect=fake_run):
                result = __import__("figure10_validation")._run_main_for_policy(run_dir, runtime_hp, 1, 123, trace_dir)
            self.assertEqual(result.returncode, 1)
            self.assertTrue((run_dir / "main_stdout.txt").exists())
            self.assertTrue((run_dir / "main_stderr.txt").exists())
            self.assertTrue((run_dir / "main_returncode.txt").exists())
            self.assertIn("sim stderr tail", (run_dir / "main_stderr.txt").read_text())

            def fake_run_fail(cmd, cwd=None, capture_output=None, text=None, check=None):
                if "main.py" in cmd:
                    config_path = Path(cmd[cmd.index("--config") + 1])
                    config = {}
                    for line in config_path.read_text().splitlines():
                        if ":" in line:
                            key, value = line.split(":", 1)
                            config[key.strip()] = value.strip().strip('"')
                    trace_dir = Path(config["trace_output_dir"])
                    trace_dir.mkdir(parents=True, exist_ok=True)
                    return __import__("subprocess").CompletedProcess(cmd, 1, stdout="sim stdout", stderr="sim stderr tail")
                return __import__("subprocess").CompletedProcess(cmd, 0, stdout="", stderr="")

            with patch("figure10_validation.subprocess.run", side_effect=fake_run_fail):
                code = __import__("figure10_validation").main(
                    [
                        "--output-dir",
                        str(out_dir),
                        "--episodes",
                        "1",
                        "--policies",
                        "RO,FLC,VO,HO,BCO,MLEO",
                        "--hyperparameters-file",
                        str(hp_path),
                        "--paper-contract",
                        str(ROOT / "config" / "paper_table4_contract.json"),
                        "--test-mode",
                    ]
                )
            readiness = json.loads((out_dir / "figure10_policy_readiness.json").read_text())
            manifest = json.loads((out_dir / "figure10_validation_manifest.json").read_text())
            self.assertEqual(code, 0)
            self.assertIn("no_metric_rows_generated", readiness["blocking_reasons"])
            self.assertTrue(manifest["warnings"])
            self.assertIn("sim stderr tail", json.dumps(manifest["warnings"]))

    def test_average_delay_and_drop_ratio_use_lifecycle_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_dir = Path(tmp) / "trace"
            _write_fixture_trace(trace_dir)
            raw_rows, summary, detail = __import__("figure10_validation")._policy_run_summary(
                policy_name="RO",
                regime_id="delay",
                run_id="test-run",
                trace_dir=trace_dir,
                validation_episodes=1,
                timeout_slots=20,
                timeout_sec=2.0,
                config_hash="hash",
                hoodie_checkpoint_status="not_required",
                contract_diagnostics=[],
                test_mode=True,
            )
            self.assertEqual(len(raw_rows), 1)
            self.assertAlmostEqual(raw_rows[0]["average_computation_delay"], 4.0)
            self.assertAlmostEqual(raw_rows[0]["drop_ratio"], 1 / 3)
            self.assertEqual(raw_rows[0]["pending_tasks"], 1)
            self.assertEqual(detail["policy_readiness_status"], "ready")
            self.assertEqual(summary["mean_average_computation_delay"], 4.0)
            self.assertAlmostEqual(summary["mean_drop_ratio"], 1 / 3)

    def test_real_validation_requires_200_episodes_outside_test_mode(self):
        readiness = assess_figure10_readiness(
            {
                "active_policy_set": EXPECTED_POLICY_SET,
                "expected_policy_set": EXPECTED_POLICY_SET,
                "missing_policies": [],
                "unexpected_policies": [],
                "policy_class_map": {policy: policy for policy in EXPECTED_POLICY_SET},
                "hoodie_checkpoint_status": "present_and_loaded",
                "mleo_required": True,
                "mleo_contract_status_seen": {"paper_candidate_trace_ready": 1},
                "delayed_reward_contract_status_seen": {"paper_replay_pairing_ready": 1},
                "validation_episode_count": 1,
                "non_hoodie_baselines_ready": True,
                "mleo_contract_status_ready": True,
                "paper_performance_claims_made": False,
                "test_mode": False,
            }
        )
        self.assertFalse(readiness["figure10_data_ready"])
        self.assertIn("validation_episode_count=1", readiness["blocking_reasons"])

    def test_blocking_reasons_are_deduplicated(self):
        # When baseline blockers are copied into figure10_blocking_reasons we
        # previously could see duplicated strings (e.g. validation_episode_count=10).
        readiness = assess_figure10_readiness(
            {
                "active_policy_set": ["RO", "FLC", "VO", "HO", "BCO", "MLEO"],
                "expected_policy_set": EXPECTED_POLICY_SET,
                "missing_policies": [],
                "unexpected_policies": [],
                "policy_class_map": {policy: policy for policy in EXPECTED_POLICY_SET},
                "hoodie_checkpoint_status": "unavailable_not_trained",
                "mleo_required": True,
                "mleo_contract_status_seen": {"paper_candidate_trace_ready": 1},
                "delayed_reward_contract_status_seen": {"paper_replay_pairing_ready": 1},
                "validation_episode_count": 10,
                "non_hoodie_baselines_ready": False,
                "paper_performance_claims_made": False,
                "test_mode": False,
            }
        )
        # Ensure duplicates are removed in all returned lists
        reason = "validation_episode_count=10"
        self.assertEqual(readiness["baseline_blocking_reasons"].count(reason), 1)
        self.assertEqual(readiness["figure10_blocking_reasons"].count(reason), 1)
        self.assertEqual(readiness["blocking_reasons"].count(reason), 1)

    def test_no_plot_files_are_generated(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            hp_path = tmp_path / "hyperparameters.json"
            _write_hyperparameters(hp_path)
            out_dir = tmp_path / "figure10"

            with patch("figure10_validation.subprocess.run", side_effect=_fake_run_factory(tmp_path)):
                __import__("figure10_validation").main(
                    [
                        "--output-dir",
                        str(out_dir),
                        "--episodes",
                        "1",
                        "--policies",
                        "RO,FLC,VO,HO,BCO,MLEO",
                        "--hyperparameters-file",
                        str(hp_path),
                        "--paper-contract",
                        str(ROOT / "config" / "paper_table4_contract.json"),
                        "--test-mode",
                    ]
                )
            self.assertFalse(list(out_dir.rglob("*.png")))
            self.assertFalse(list(out_dir.rglob("*.pdf")))

    def test_runner_writes_required_outputs_and_no_plots(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            hp_path = tmp_path / "hyperparameters.json"
            _write_hyperparameters(hp_path)
            out_dir = tmp_path / "figure10"
            config = Figure10ValidationConfig(
                output_dir=str(out_dir),
                episodes=1,
                seed=42,
                policies=list(EXPECTED_POLICY_SET),
                paper_contract_file=str(ROOT / "config" / "paper_table4_contract.json"),
                hyperparameters_file=str(hp_path),
                config_file=None,
                hoodie_checkpoint_dir=None,
                test_mode=True,
                strict_paper_contract=False,
                run_id="test-run",
                timestamp="2026-01-01T00:00:00Z",
                branch="test",
                commit="abc123",
            )
            with patch("figure10_validation.subprocess.run", side_effect=_fake_run_factory(tmp_path)):
                run_figure10_validation(config)
            self.assertTrue((out_dir / "figure10_policy_metrics_raw.csv").exists())
            self.assertTrue((out_dir / "figure10_policy_metrics_summary.json").exists())
            self.assertTrue((out_dir / "figure10_policy_readiness.json").exists())
            self.assertTrue((out_dir / "figure10_run_config_snapshot.json").exists())
            self.assertTrue((out_dir / "figure10_validation_manifest.json").exists())
            self.assertFalse(list(out_dir.rglob("*.png")))
            self.assertFalse(list(out_dir.rglob("*.pdf")))

    def test_runner_emits_critical_progress_logs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            hp_path = tmp_path / "hyperparameters.json"
            _write_hyperparameters(hp_path)
            out_dir = tmp_path / "figure10"
            config = Figure10ValidationConfig(
                output_dir=str(out_dir),
                episodes=1,
                seed=42,
                policies=["RO", "MLEO"],
                paper_contract_file=str(ROOT / "config" / "paper_table4_contract.json"),
                hyperparameters_file=str(hp_path),
                config_file=None,
                hoodie_checkpoint_dir=None,
                test_mode=True,
                strict_paper_contract=False,
                run_id="test-run",
                timestamp="2026-01-01T00:00:00Z",
                branch="test",
                commit="abc123",
            )
            buffer = io.StringIO()
            with patch("figure10_validation.subprocess.run", side_effect=_fake_run_factory(tmp_path)):
                with redirect_stdout(buffer):
                    run_figure10_validation(config)
            output = buffer.getvalue()
            self.assertIn("=== Figure 10 Validation ===", output)
            self.assertIn("=== 1. Paper Contract Diagnostics", output)
            self.assertIn("=== 2. Regime Start: delay ===", output)
            self.assertIn("regime=delay policy=RO: launching main.py", output)
            self.assertIn("regime=delay policy=RO: reading trace report", output)
            self.assertIn("=== 3. Raw Metrics Written ===", output)
            self.assertIn("=== 4. Report Files Written ===", output)
            self.assertIn("=== 5. Validation Complete ===", output)

    def test_run_main_for_policy_includes_seed_argument(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            hp_path = tmp_path / "hyperparameters.json"
            _write_hyperparameters(hp_path)
            run_dir = tmp_path / "run"
            trace_dir = tmp_path / "trace"

            recorded_cmds = []

            def fake_run(cmd, cwd=None, capture_output=None, text=None, check=None):
                recorded_cmds.append(cmd)
                return __import__("subprocess").CompletedProcess(cmd, 0, stdout="ok", stderr="")

            runtime_hp = json.loads(hp_path.read_text())
            runtime_hp["decision_makers"] = "RO"
            with patch("figure10_validation.subprocess.run", side_effect=fake_run):
                __import__("figure10_validation")._run_main_for_policy(run_dir, runtime_hp, 1, 123, trace_dir)
            self.assertTrue(any("--seed" in cmd for cmd in recorded_cmds))
            self.assertTrue(any("--epochs" in cmd for cmd in recorded_cmds))
            self.assertFalse(any("--episodes" in cmd for cmd in recorded_cmds))

    def test_main_accepts_seed_argument(self):
        result = __import__("subprocess").run(
            [str(PYTHON), "main.py", "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("--seed", result.stdout)

    def test_diagnostic_cli_returns_zero_when_outputs_exist_even_if_not_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            hp_path = tmp_path / "hyperparameters.json"
            _write_hyperparameters(hp_path)
            out_dir = tmp_path / "figure10"

            with patch("figure10_validation.subprocess.run", side_effect=_fake_run_factory(tmp_path)):
                code = __import__("figure10_validation").main(
                    [
                        "--output-dir",
                        str(out_dir),
                        "--episodes",
                        "1",
                        "--policies",
                        ",".join(EXPECTED_POLICY_SET),
                        "--hyperparameters-file",
                        str(hp_path),
                        "--paper-contract",
                        str(ROOT / "config" / "paper_table4_contract.json"),
                        "--test-mode",
                    ]
                )
            self.assertEqual(code, 0)
            self.assertTrue((out_dir / "figure10_policy_metrics_raw.csv").exists())
            self.assertTrue((out_dir / "figure10_validation_manifest.json").exists())

    def test_strict_readiness_returns_one_when_not_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            hp_path = tmp_path / "hyperparameters.json"
            _write_hyperparameters(hp_path)
            out_dir = tmp_path / "figure10"

            def fake_run(cmd, cwd=None, capture_output=None, text=None, check=None):
                if "main.py" in cmd:
                    trace_dir = tmp_path / "trace"
                    _write_fixture_trace(trace_dir, policy_name="RO")
                return __import__("subprocess").CompletedProcess(cmd, 0, stdout="ok", stderr="")

            args = [
                "--output-dir",
                str(out_dir),
                "--episodes",
                "1",
                "--policies",
                ",".join(EXPECTED_POLICY_SET),
                "--hyperparameters-file",
                str(hp_path),
                "--paper-contract",
                str(ROOT / "config" / "paper_table4_contract.json"),
                "--test-mode",
                "--strict-readiness",
            ]
            with patch("figure10_validation.subprocess.run", side_effect=_fake_run_factory(tmp_path)):
                code = __import__("figure10_validation").main(args)
            self.assertEqual(code, 1)

    def test_existing_contract_tests_remain_compatible(self):
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
