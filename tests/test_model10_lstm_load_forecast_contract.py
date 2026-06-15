from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from training.lstm_forecaster import LSTMForecaster


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venvmac" / "bin" / "python"


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _paper_trace_fixture(trace_dir: Path, rows: list[dict[str, object]]) -> None:
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
    _write_csv(trace_dir / "paper_state_trace.csv", rows)
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
                "total_tasks": len(rows),
                "completed_tasks": len(rows),
                "dropped_tasks": 0,
                "pending_tasks": 0,
                "average_latency": 1.0,
                "average_waiting_time": 0.0,
                "average_service_time": 1.0,
                "drop_ratio": 0.0,
                "average_queue_length": 1.0,
                "total_reward": -float(len(rows)),
                "mean_reward": -1.0,
            }
        ],
    )


def test_lstm_forecaster_config_validation() -> None:
    LSTMForecaster(sequence_length=2, input_dim=2, hidden_dim=4, target="active_load_vector", seed=1, output_dim=2)
    with np.testing.assert_raises(ValueError):
        LSTMForecaster(sequence_length=0, input_dim=2, hidden_dim=4, target="active_load_vector", seed=1, output_dim=2)
    with np.testing.assert_raises(ValueError):
        LSTMForecaster(sequence_length=2, input_dim=0, hidden_dim=4, target="active_load_vector", seed=1, output_dim=2)
    with np.testing.assert_raises(ValueError):
        LSTMForecaster(sequence_length=2, input_dim=2, hidden_dim=0, target="active_load_vector", seed=1, output_dim=2)
    with np.testing.assert_raises(ValueError):
        LSTMForecaster(sequence_length=2, input_dim=2, hidden_dim=4, target="latency", seed=1, output_dim=2)
    with np.testing.assert_raises(ValueError):
        LSTMForecaster(sequence_length=2, input_dim=2, hidden_dim=4, target="active_load_vector", seed=1, output_dim=0)


def test_sequence_builder_respects_episode_agent_time_order() -> None:
    forecaster = LSTMForecaster(sequence_length=2, input_dim=2, hidden_dim=4, target="active_load_vector", seed=1, output_dim=2)
    rows = [
        {"episode_id": 1, "agent_id": 0, "time": 0, "active_load_vector": [1.0, 0.0]},
        {"episode_id": 1, "agent_id": 0, "time": 1, "active_load_vector": [0.0, 1.0]},
        {"episode_id": 1, "agent_id": 0, "time": 2, "active_load_vector": [0.5, 0.5]},
        {"episode_id": 1, "agent_id": 1, "time": 0, "active_load_vector": [2.0, 0.0]},
        {"episode_id": 1, "agent_id": 1, "time": 1, "active_load_vector": [0.0, 2.0]},
        {"episode_id": 1, "agent_id": 1, "time": 2, "active_load_vector": [1.5, 0.5]},
        {"episode_id": 2, "agent_id": 0, "time": 0, "active_load_vector": [9.0, 9.0]},
        {"episode_id": 2, "agent_id": 0, "time": 1, "active_load_vector": [8.0, 8.0]},
        {"episode_id": 2, "agent_id": 0, "time": 2, "active_load_vector": [7.0, 7.0]},
    ]
    sequences, targets, reason = forecaster.build_sequences(rows)
    assert reason is None
    assert sequences.shape == (3, 2, 2)
    assert targets.shape == (3, 2)
    np.testing.assert_allclose(sequences[0], np.asarray([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32))
    np.testing.assert_allclose(targets[0], np.asarray([0.5, 0.5], dtype=np.float32))
    np.testing.assert_allclose(sequences[1], np.asarray([[2.0, 0.0], [0.0, 2.0]], dtype=np.float32))
    np.testing.assert_allclose(targets[1], np.asarray([1.5, 0.5], dtype=np.float32))
    np.testing.assert_allclose(sequences[2], np.asarray([[9.0, 9.0], [8.0, 8.0]], dtype=np.float32))
    np.testing.assert_allclose(targets[2], np.asarray([7.0, 7.0], dtype=np.float32))


def test_insufficient_sequence_handling() -> None:
    forecaster = LSTMForecaster(sequence_length=3, input_dim=2, hidden_dim=4, target="active_load_vector", seed=1, output_dim=2)
    sequences, targets, reason = forecaster.build_sequences(
        [
            {"episode_id": 1, "agent_id": 0, "time": 0, "active_load_vector": [1.0, 0.0]},
            {"episode_id": 1, "agent_id": 0, "time": 1, "active_load_vector": [0.0, 1.0]},
        ]
    )
    assert sequences.shape == (0, 3, 2)
    assert targets.shape == (0, 2)
    assert reason is not None
    assert "not enough" in reason.lower()


def test_predict_and_checkpoint_roundtrip(tmp_path: Path) -> None:
    forecaster = LSTMForecaster(sequence_length=2, input_dim=2, hidden_dim=4, target="active_load_vector", seed=7, output_dim=2)
    sequences = np.asarray(
        [
            [[1.0, 0.0], [0.0, 1.0]],
            [[0.0, 1.0], [1.0, 0.0]],
            [[1.0, 1.0], [0.5, 0.5]],
        ],
        dtype=np.float32,
    )
    targets = np.asarray([[0.0, 1.0], [1.0, 0.0], [0.25, 0.75]], dtype=np.float32)
    result = forecaster.train(sequences, targets, epochs=1, learning_rate=1e-2)
    assert result.paper_lstm_forecast is True
    load_history = np.asarray([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    before = forecaster.predict(load_history)
    ckpt = forecaster.save(tmp_path / "lstm.chkpt")
    restored = LSTMForecaster(sequence_length=2, input_dim=2, hidden_dim=4, target="active_load_vector", seed=7, output_dim=2)
    restored.load(ckpt)
    after = restored.predict(load_history)
    np.testing.assert_allclose(before, after)


def test_train_phase3_does_not_train_lstm_by_default(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    rows = [
        {
            "episode_id": 1,
            "time": 0,
            "agent_id": 0,
            "x_n_t": 1,
            "task_id": 1,
            "eta_n": 4.0,
            "w_priv_n": 0.0,
            "w_off_n": 0.0,
            "l_pub_n_prev_json": json.dumps([0.0, 0.0]),
            "active_load_vector_json": json.dumps([1.0, 0.0]),
            "L_t_json": json.dumps([[0.0, 0.0], [1.0, 0.0]]),
            "predicted_next_load_json": json.dumps([1.0, 0.0]),
            "predicted_next_load_method": "persistence_baseline",
            "paper_lstm_forecast": False,
            "unavailable_fields_json": json.dumps([]),
            "approximation_warnings_json": json.dumps(["persistence_baseline"]),
            "state_vector_json": json.dumps([4.0, 0.0, 0.0, 0.0]),
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
            "l_pub_n_prev_json": json.dumps([0.0, 0.0]),
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
    _paper_trace_fixture(trace_dir, rows)
    out_dir = tmp_path / "out"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "training.train_phase3",
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
    assert not (out_dir / "lstm_active_load_vector.chkpt").exists()
    report = json.loads((out_dir / "phase3_training_report.json").read_text())
    assert report["lstm_forecast_requested"] is False
    assert report["lstm_forecast_status"] == "skipped"
    assert report["predicted_next_load_method"] == "persistence_baseline"
    assert report["paper_lstm_forecast"] is False
    assert report["paper_claims_made"] is False


def test_train_phase3_trains_lstm_when_requested(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    rows = [
        {
            "episode_id": 1,
            "time": 0,
            "agent_id": 0,
            "x_n_t": 1,
            "task_id": 1,
            "eta_n": 4.0,
            "w_priv_n": 0.0,
            "w_off_n": 0.0,
            "l_pub_n_prev_json": json.dumps([0.0, 0.0]),
            "active_load_vector_json": json.dumps([1.0, 0.0]),
            "L_t_json": json.dumps([[0.0, 0.0], [1.0, 0.0]]),
            "predicted_next_load_json": json.dumps([1.0, 0.0]),
            "predicted_next_load_method": "persistence_baseline",
            "paper_lstm_forecast": False,
            "unavailable_fields_json": json.dumps([]),
            "approximation_warnings_json": json.dumps(["persistence_baseline"]),
            "state_vector_json": json.dumps([4.0, 0.0, 0.0, 0.0]),
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
            "l_pub_n_prev_json": json.dumps([0.0, 0.0]),
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
        {
            "episode_id": 1,
            "time": 2,
            "agent_id": 0,
            "x_n_t": 0,
            "task_id": 1,
            "eta_n": 0.0,
            "w_priv_n": 0.0,
            "w_off_n": 0.0,
            "l_pub_n_prev_json": json.dumps([0.0, 0.0]),
            "active_load_vector_json": json.dumps([0.5, 0.5]),
            "L_t_json": json.dumps([[0.0, 1.0], [0.5, 0.5]]),
            "predicted_next_load_json": json.dumps([0.5, 0.5]),
            "predicted_next_load_method": "persistence_baseline",
            "paper_lstm_forecast": False,
            "unavailable_fields_json": json.dumps([]),
            "approximation_warnings_json": json.dumps(["persistence_baseline"]),
            "state_vector_json": json.dumps([0.0, 0.0, 0.0, 0.0]),
            "state_dim": 4,
        },
    ]
    _paper_trace_fixture(trace_dir, rows)
    out_dir = tmp_path / "out"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "training.train_phase3",
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
    assert (out_dir / "lstm_active_load_vector.chkpt").exists()
    assert (out_dir / "paper_state_trace_lstm_forecast.csv").exists()
    report = json.loads((out_dir / "phase3_training_report.json").read_text())
    assert report["lstm_forecast_requested"] is True
    assert report["lstm_forecast_status"] == "trained"
    assert report["lstm_target"] == "active_load_vector"
    assert report["predicted_next_load_method"] == "trained_lstm"
    assert report["paper_lstm_forecast"] is True
    assert report["paper_claims_made"] is False
    forecast_rows = list(csv.DictReader((out_dir / "paper_state_trace_lstm_forecast.csv").open()))
    assert forecast_rows
    assert all(row["predicted_next_load_method"] == "trained_lstm" for row in forecast_rows)
    assert all(row["paper_lstm_forecast"].lower() == "true" for row in forecast_rows)


def test_original_runtime_paper_state_is_not_mislabeled(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    rows = [
        {
            "episode_id": 1,
            "time": 0,
            "agent_id": 0,
            "x_n_t": 1,
            "task_id": 1,
            "eta_n": 4.0,
            "w_priv_n": 0.0,
            "w_off_n": 0.0,
            "l_pub_n_prev_json": json.dumps([0.0, 0.0]),
            "active_load_vector_json": json.dumps([1.0, 0.0]),
            "L_t_json": json.dumps([[0.0, 0.0], [1.0, 0.0]]),
            "predicted_next_load_json": json.dumps([1.0, 0.0]),
            "predicted_next_load_method": "persistence_baseline",
            "paper_lstm_forecast": False,
            "unavailable_fields_json": json.dumps([]),
            "approximation_warnings_json": json.dumps(["persistence_baseline"]),
            "state_vector_json": json.dumps([4.0, 0.0, 0.0, 0.0]),
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
            "l_pub_n_prev_json": json.dumps([0.0, 0.0]),
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
        {
            "episode_id": 1,
            "time": 2,
            "agent_id": 0,
            "x_n_t": 0,
            "task_id": 1,
            "eta_n": 0.0,
            "w_priv_n": 0.0,
            "w_off_n": 0.0,
            "l_pub_n_prev_json": json.dumps([0.0, 0.0]),
            "active_load_vector_json": json.dumps([0.5, 0.5]),
            "L_t_json": json.dumps([[0.0, 1.0], [0.5, 0.5]]),
            "predicted_next_load_json": json.dumps([0.5, 0.5]),
            "predicted_next_load_method": "persistence_baseline",
            "paper_lstm_forecast": False,
            "unavailable_fields_json": json.dumps([]),
            "approximation_warnings_json": json.dumps(["persistence_baseline"]),
            "state_vector_json": json.dumps([0.0, 0.0, 0.0, 0.0]),
            "state_dim": 4,
        },
    ]
    _paper_trace_fixture(trace_dir, rows)
    out_dir = tmp_path / "out"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "training.train_phase3",
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
    runtime_rows = list(csv.DictReader((out_dir / "paper_state_trace.csv").open()))
    assert runtime_rows
    assert all(row["predicted_next_load_method"] == "persistence_baseline" for row in runtime_rows)
    assert all(row["paper_lstm_forecast"].lower() == "false" for row in runtime_rows)
    forecast_rows = list(csv.DictReader((out_dir / "paper_state_trace_lstm_forecast.csv").open()))
    assert forecast_rows
    assert all(row["predicted_next_load_method"] == "trained_lstm" for row in forecast_rows)
    assert all(row["paper_lstm_forecast"].lower() == "true" for row in forecast_rows)
