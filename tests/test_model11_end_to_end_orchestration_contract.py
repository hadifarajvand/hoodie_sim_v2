from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

from training.orchestrate_model11 import (
    build_offline_evaluation_summary,
    orchestrate,
    preflight_runtime_trace,
    validate_training_artifacts,
)


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venvmac" / "bin" / "python"


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _trace_fixture(trace_dir: Path, with_lstm: bool = False) -> None:
    _write_csv(
        trace_dir / "task_lifecycle.csv",
        [
            {
                "task_id": 1,
                "episode_id": 1,
                "arrival_time": 0,
                "queue_enter_time": 0,
                "service_start_time": 0,
                "service_end_time": 1,
                "completion_time": 1,
                "drop_time": "",
                "selected_action": 1,
                "processing_node": 0,
                "latency": 1,
                "waiting_time": 0,
                "service_time": 1,
                "final_status": "completed",
                "drop_reason": "",
                "drop_penalty": 40.0,
                "source_node": 0,
                "input_data_size": 5,
            }
        ],
    )
    _write_csv(
        trace_dir / "queue_trace.csv",
        [
            {"episode_id": 1, "time": 0, "node_id": 0, "queue_type": "private", "queue_length": 1, "arrivals": 1, "departures": 0, "drops": 0, "cpu_allocated": 1},
            {"episode_id": 1, "time": 1, "node_id": 0, "queue_type": "private", "queue_length": 0, "arrivals": 0, "departures": 1, "drops": 0, "cpu_allocated": 1},
            {"episode_id": 1, "time": 0, "node_id": 0, "queue_type": "offloading", "queue_length": 1, "arrivals": 0, "departures": 0, "drops": 0, "cpu_allocated": 1},
            {"episode_id": 1, "time": 0, "node_id": 0, "queue_type": "public:0", "queue_length": 1, "arrivals": 1, "departures": 0, "drops": 0, "cpu_allocated": 1},
            {"episode_id": 1, "time": 0, "node_id": 1, "queue_type": "cloud_public:0", "queue_length": 1, "arrivals": 1, "departures": 0, "drops": 0, "cpu_allocated": 1},
        ],
    )
    _write_csv(
        trace_dir / "action_trace.csv",
        [
            {
                "episode_id": 1,
                "time": 0,
                "agent_id": 0,
                "x_n_t": 1,
                "observation_shape": json.dumps([4]),
                "selected_action": 1,
                "target_node": 1,
                "reward_received": -1.0,
                "raw_action_id": 5,
                "first_stage_decision": "offload",
                "destination_node_id": 1,
                "destination_type": "vertical_cloud",
                "is_valid": True,
                "invalid_reason": "",
                "adjacency_allowed": True,
                "cloud_target": True,
                "d_n_1": 0,
                "d_nk_2": json.dumps({"1": 1}),
                "paper_destination_nodes": json.dumps([1]),
                "paper_d_nk_2": json.dumps([0, 1]),
                "dm2_timing": "offloading_queue_exit",
                "requires_separate_dm2_at_offloading_queue_exit": False,
                "paper_u_n_t": 1,
                "dm2_pending": False,
            }
        ],
    )
    paper_rows = [
        {
            "episode_id": 1,
            "time": 0,
            "agent_id": 0,
            "x_n_t": 1,
            "task_id": 1,
            "eta_n": 5.0,
            "w_priv_n": 0.0,
            "w_off_n": 0.0,
            "l_pub_n_prev_json": json.dumps([0.0, 1.0]),
            "active_load_vector_json": json.dumps([1.0, 0.0]),
            "L_t_json": json.dumps([[0.0, 0.0], [1.0, 0.0]]),
            "predicted_next_load_json": json.dumps([1.0, 0.0]),
            "predicted_next_load_method": "persistence_baseline",
            "paper_lstm_forecast": False,
            "unavailable_fields_json": json.dumps([]),
            "approximation_warnings_json": json.dumps(["persistence_baseline"]),
            "state_vector_json": json.dumps([5.0, 0.0, 0.0, 1.0]),
            "state_dim": 4,
        },
        {
            "episode_id": 1,
            "time": 1,
            "agent_id": 0,
            "x_n_t": 0,
            "task_id": 1,
            "eta_n": 0.0,
            "w_priv_n": 0.0,
            "w_off_n": 0.0,
            "l_pub_n_prev_json": json.dumps([0.0, 1.0]),
            "active_load_vector_json": json.dumps([0.0, 1.0]),
            "L_t_json": json.dumps([[1.0, 0.0], [0.0, 1.0]]),
            "predicted_next_load_json": json.dumps([0.0, 1.0]),
            "predicted_next_load_method": "persistence_baseline",
            "paper_lstm_forecast": False,
            "unavailable_fields_json": json.dumps([]),
            "approximation_warnings_json": json.dumps(["persistence_baseline"]),
            "state_vector_json": json.dumps([0.0, 0.0, 0.0, 0.0]),
            "state_dim": 4,
        },
    ]
    if with_lstm:
        paper_rows.append(
            {
                "episode_id": 1,
                "time": 2,
                "agent_id": 0,
                "x_n_t": 0,
                "task_id": 1,
                "eta_n": 0.0,
                "w_priv_n": 0.0,
                "w_off_n": 0.0,
                "l_pub_n_prev_json": json.dumps([0.0, 1.0]),
                "active_load_vector_json": json.dumps([0.5, 0.5]),
                "L_t_json": json.dumps([[0.0, 1.0], [0.5, 0.5]]),
                "predicted_next_load_json": json.dumps([0.5, 0.5]),
                "predicted_next_load_method": "persistence_baseline",
                "paper_lstm_forecast": False,
                "unavailable_fields_json": json.dumps([]),
                "approximation_warnings_json": json.dumps(["persistence_baseline"]),
                "state_vector_json": json.dumps([0.0, 0.0, 0.0, 0.0]),
                "state_dim": 4,
            }
        )
    _write_csv(trace_dir / "paper_state_trace.csv", paper_rows)
    _write_csv(
        trace_dir / "delayed_reward_event_trace.csv",
        [
            {
                "task_id": 1,
                "episode_id": 1,
                "source_agent": 0,
                "decision_time": 0,
                "final_status": "completed",
                "completion_time": 1,
                "drop_time": "",
                "delay": 1,
                "reward": -1.0,
                "drop_penalty": 40.0,
                "reward_reason": "completed",
                "paired_transition_found": True,
                "replay_inserted": True,
                "replay_pairing_status": "paired",
                "reward_timing_convention": "completion_minus_arrival",
            }
        ],
    )
    _write_csv(
        trace_dir / "episode_metrics.csv",
        [
            {
                "episode_id": 1,
                "total_tasks": 1,
                "completed_tasks": 1,
                "dropped_tasks": 0,
                "pending_tasks": 0,
                "average_latency": 1.0,
                "average_waiting_time": 0.0,
                "average_service_time": 1.0,
                "drop_ratio": 0.0,
                "average_queue_length": 1.0,
                "total_reward": -1.0,
                "mean_reward": -1.0,
            }
        ],
    )


def test_preflight_fails_on_missing_required_trace_files(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    trace_dir.mkdir()
    _write_csv(trace_dir / "task_lifecycle.csv", [{"task_id": 1, "episode_id": 1, "final_status": "completed"}])
    _write_csv(trace_dir / "queue_trace.csv", [{"episode_id": 1, "time": 0, "node_id": 0, "queue_type": "private", "queue_length": 1, "arrivals": 1, "departures": 0, "drops": 0, "cpu_allocated": 1}])
    _write_csv(trace_dir / "action_trace.csv", [{"episode_id": 1, "time": 0, "agent_id": 0, "selected_action": 1, "reward_received": 0.0}])
    out_dir = tmp_path / "out"
    try:
        preflight_runtime_trace(trace_dir, out_dir)
        assert False, "expected failure"
    except ValueError as exc:
        assert "episode_metrics.csv" in str(exc)
    report = json.loads((out_dir / "preflight_runtime_trace_report.json").read_text())
    assert report["preflight_status"] == "failed"
    assert "episode_metrics.csv" in report["missing_required_files"]


def test_preflight_passes_with_full_trace_fixture(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _trace_fixture(trace_dir)
    out_dir = tmp_path / "out"
    report = preflight_runtime_trace(trace_dir, out_dir)
    assert report["preflight_status"] == "passed"
    assert report["paper_state_trace_present"] is True
    assert report["delayed_reward_event_trace_present"] is True
    assert report["simulation_executed"] is False
    assert report["paper_claims_made"] is False


def test_end_to_end_orchestration_succeeds_for_dqn(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _trace_fixture(trace_dir)
    out_dir = tmp_path / "out"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "training.orchestrate_model11",
            "--trace-dir",
            str(trace_dir),
            "--output-dir",
            str(out_dir),
            "--algorithm",
            "dqn",
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
    assert result.returncode == 0, result.stderr
    assert (out_dir / "preflight_runtime_trace_report.json").exists()
    assert (out_dir / "training" / "artifact_validation_report.json").exists()
    assert (out_dir / "training" / "offline_evaluation_summary.json").exists()
    assert (out_dir / "model11_orchestration_manifest.json").exists()
    assert (out_dir / "training" / "dataset_summary.json").exists()
    assert (out_dir / "training" / "training_metrics.json").exists()
    assert (out_dir / "training" / "phase3_training_report.json").exists()
    assert (out_dir / "training" / "phase3_model.chkpt").exists()
    manifest = json.loads((out_dir / "model11_orchestration_manifest.json").read_text())
    assert manifest["status"] == "passed"
    assert manifest["algorithm"] == "dqn"
    assert manifest["paper_claims_made"] is False
    assert manifest["simulation_executed"] is False
    assert manifest["full_pytest_executed"] is False


def test_orchestration_supports_ddqn_and_dueling_smoke(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _trace_fixture(trace_dir)
    for algorithm in ("ddqn", "dueling_dqn"):
        out_dir = tmp_path / algorithm
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "training.orchestrate_model11",
                "--trace-dir",
                str(trace_dir),
                "--output-dir",
                str(out_dir),
                "--algorithm",
                algorithm,
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
        assert result.returncode == 0, result.stderr
        report = json.loads((out_dir / "training" / "phase3_training_report.json").read_text())
        assert report["algorithm"] == algorithm
        assert report["q_model_type"] is not None
        assert report["model_architecture"] is not None


def test_lstm_requested_path(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _trace_fixture(trace_dir, with_lstm=True)
    out_dir = tmp_path / "out"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "training.orchestrate_model11",
            "--trace-dir",
            str(trace_dir),
            "--output-dir",
            str(out_dir),
            "--algorithm",
            "dqn",
            "--epochs",
            "1",
            "--batch-size",
            "1",
            "--checkpoint-every",
            "1",
            "--seed",
            "7",
            "--train-lstm",
            "--sequence-length",
            "2",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    manifest = json.loads((out_dir / "model11_orchestration_manifest.json").read_text())
    assert manifest["train_lstm_requested"] is True
    assert "lstm_active_load_vector.chkpt" in manifest["lstm_artifacts"]
    assert (out_dir / "training" / "lstm_active_load_vector.chkpt").exists()
    assert (out_dir / "training" / "paper_state_trace_lstm_forecast.csv").exists()
    report = json.loads((out_dir / "training" / "phase3_training_report.json").read_text())
    assert report["lstm_forecast_status"] == "trained"


def test_offline_evaluation_summary_is_diagnostic_only(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _trace_fixture(trace_dir)
    out_dir = tmp_path / "out"
    orchestrate(trace_dir, out_dir, algorithm="dqn", epochs=1, batch_size=1, checkpoint_every=1, seed=7)
    summary = json.loads((out_dir / "training" / "offline_evaluation_summary.json").read_text())
    assert summary["evaluation_type"] == "offline_trace_diagnostic_only"
    assert summary["paper_performance_claims_made"] is False
    assert summary["simulation_executed"] is False
    assert summary["phase4_evaluation_performed"] is False
    assert summary["runtime_episode_metrics"]["drop_ratio"] == 0.0
    assert "reward_source_counts" in summary
    assert summary["q_model_type"] is not None
    assert summary["model_architecture"] is not None


def test_artifact_validation_catches_missing_artifact(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _trace_fixture(trace_dir)
    out_dir = tmp_path / "out"
    orchestration = orchestrate(trace_dir, out_dir, algorithm="dqn", epochs=1, batch_size=1, checkpoint_every=1, seed=7)
    model_path = out_dir / "training" / "phase3_model.chkpt"
    model_path.unlink()
    try:
        validate_training_artifacts(out_dir / "training")
        assert False, "expected validation failure"
    except ValueError as exc:
        assert "phase3_model.chkpt" in str(exc)


def test_artifact_validation_catches_missing_dataset_summary_keys(tmp_path: Path) -> None:
    training_dir = tmp_path / "training"
    training_dir.mkdir()
    (training_dir / "dataset_summary.json").write_text(
        json.dumps(
            {
                "transitions": 1,
                "state_dim": 4,
                "action_count": 2,
                "state_source_counts": {},
                "next_state_source_counts": {},
            }
        )
    )
    (training_dir / "training_metrics.json").write_text(
        json.dumps(
            {
                "algorithm": "dqn",
                "epochs": 1,
                "batch_size": 1,
                "transitions_used": 1,
                "final_checkpoint": "phase3_model.chkpt",
            }
        )
    )
    (training_dir / "phase3_training_report.json").write_text(
        json.dumps(
            {
                "algorithm": "dqn",
                "q_model_type": "mlp",
                "model_architecture": "mlp",
                "paper_claims_made": False,
                "phase4_evaluation_performed": False,
            }
        )
    )
    (training_dir / "phase3_model.chkpt").write_text("chkpt")
    try:
        validate_training_artifacts(training_dir, expected_algorithm="dqn")
        assert False, "expected validation failure"
    except ValueError as exc:
        assert "dataset_summary.json" in str(exc)
    report = json.loads((training_dir / "artifact_validation_report.json").read_text())
    assert report["artifact_validation_status"] == "failed"
    assert report["dataset_summary_contract_passed"] is False
    assert any("dataset_summary.json" in item for item in report["invalid_artifacts"])


def test_artifact_validation_catches_missing_training_metrics_keys(tmp_path: Path) -> None:
    training_dir = tmp_path / "training"
    training_dir.mkdir()
    (training_dir / "dataset_summary.json").write_text(
        json.dumps(
            {
                "transitions": 1,
                "state_dim": 4,
                "action_count": 2,
                "reward_source_counts": {},
                "state_source_counts": {},
                "next_state_source_counts": {},
            }
        )
    )
    (training_dir / "training_metrics.json").write_text(
        json.dumps(
            {
                "algorithm": "dqn",
                "epochs": 1,
                "batch_size": 1,
                "transitions_used": 1,
            }
        )
    )
    (training_dir / "phase3_training_report.json").write_text(
        json.dumps(
            {
                "algorithm": "dqn",
                "q_model_type": "mlp",
                "model_architecture": "mlp",
                "paper_claims_made": False,
                "phase4_evaluation_performed": False,
            }
        )
    )
    (training_dir / "phase3_model.chkpt").write_text("chkpt")
    try:
        validate_training_artifacts(training_dir, expected_algorithm="dqn")
        assert False, "expected validation failure"
    except ValueError as exc:
        assert "training_metrics.json" in str(exc)
    report = json.loads((training_dir / "artifact_validation_report.json").read_text())
    assert report["artifact_validation_status"] == "failed"
    assert report["training_metrics_contract_passed"] is False
    assert any("training_metrics.json" in item for item in report["invalid_artifacts"])


def test_artifact_validation_catches_algorithm_mismatch(tmp_path: Path) -> None:
    training_dir = tmp_path / "training"
    training_dir.mkdir()
    (training_dir / "dataset_summary.json").write_text(
        json.dumps(
            {
                "transitions": 1,
                "state_dim": 4,
                "action_count": 2,
                "reward_source_counts": {},
                "state_source_counts": {},
                "next_state_source_counts": {},
            }
        )
    )
    (training_dir / "training_metrics.json").write_text(
        json.dumps(
            {
                "algorithm": "dqn",
                "epochs": 1,
                "batch_size": 1,
                "transitions_used": 1,
                "final_checkpoint": "phase3_model.chkpt",
            }
        )
    )
    (training_dir / "phase3_training_report.json").write_text(
        json.dumps(
            {
                "algorithm": "dqn",
                "q_model_type": "mlp",
                "model_architecture": "mlp",
                "paper_claims_made": False,
                "phase4_evaluation_performed": False,
            }
        )
    )
    (training_dir / "phase3_model.chkpt").write_text("chkpt")
    try:
        validate_training_artifacts(training_dir, expected_algorithm="ddqn")
        assert False, "expected validation failure"
    except ValueError as exc:
        assert "algorithm mismatch" in str(exc)
    report = json.loads((training_dir / "artifact_validation_report.json").read_text())
    assert report["artifact_validation_status"] == "failed"
    assert report["expected_algorithm"] == "ddqn"
    assert report["observed_algorithm_from_report"] == "dqn"
    assert report["observed_algorithm_from_metrics"] == "dqn"
