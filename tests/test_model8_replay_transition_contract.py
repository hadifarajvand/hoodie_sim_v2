from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from training.replay_buffer import Transition
from training.trace_dataset import load_trace_dataset


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _base_trace_dir(trace_dir: Path) -> None:
    _write_csv(
        trace_dir / "task_lifecycle.csv",
        [
            {
                "task_id": 1,
                "episode_id": 1,
                "arrival_time": 1,
                "queue_enter_time": 1,
                "final_status": "completed",
                "completion_time": 2,
                "service_start_time": 1,
                "service_end_time": 2,
                "source_node": 0,
                "selected_action": 1,
                "drop_penalty": 40.0,
            }
        ],
    )
    _write_csv(
        trace_dir / "queue_trace.csv",
        [
            {
                "episode_id": 1,
                "time": 1,
                "node_id": 0,
                "queue_type": "private",
                "queue_length": 1.0,
                "arrivals": 1,
                "departures": 0,
                "drops": 0,
                "cpu_allocated": 1.0,
            }
        ],
    )
    _write_csv(
        trace_dir / "action_trace.csv",
        [
            {
                "episode_id": 1,
                "time": 1,
                "agent_id": 0,
                "x_n_t": 1,
                "observation_shape": json.dumps([12]),
                "selected_action": 1,
                "target_node": 0,
                "reward_received": 0.0,
                "raw_action_id": 11,
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


def test_transition_validation_rejects_bad_tuples() -> None:
    valid = Transition(
        state=np.asarray([1.0, 2.0], dtype=np.float32),
        action=1,
        reward=0.0,
        next_state=np.asarray([1.5, 2.5], dtype=np.float32),
        done=False,
    )
    valid.validate()

    with np.testing.assert_raises(ValueError):
        Transition(
            state=np.asarray([1.0, 2.0], dtype=np.float32),
            action=1,
            reward=0.0,
            next_state=np.asarray([1.0, 2.0, 3.0], dtype=np.float32),
            done=False,
        ).validate()

    with np.testing.assert_raises(ValueError):
        Transition(
            state=np.asarray([1.0, np.nan], dtype=np.float32),
            action=1,
            reward=0.0,
            next_state=np.asarray([1.0, 2.0], dtype=np.float32),
            done=False,
        ).validate()

    with np.testing.assert_raises(ValueError):
        Transition(
            state=np.asarray([1.0, 2.0], dtype=np.float32),
            action=1,
            reward=0.0,
            next_state=np.asarray([1.0, np.nan], dtype=np.float32),
            done=False,
        ).validate()

    with np.testing.assert_raises((TypeError, ValueError)):
        Transition(
            state=np.asarray([1.0, 2.0], dtype=np.float32),
            action=1.5,  # type: ignore[arg-type]
            reward=0.0,
            next_state=np.asarray([1.0, 2.0], dtype=np.float32),
            done=False,
        ).validate()

    with np.testing.assert_raises(ValueError):
        Transition(
            state=np.asarray([1.0, 2.0], dtype=np.float32),
            action=1,
            reward=float("inf"),
            next_state=np.asarray([1.0, 2.0], dtype=np.float32),
            done=False,
        ).validate()


def test_paper_state_trace_builds_non_terminal_next_state(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _base_trace_dir(trace_dir)
    _write_csv(
        trace_dir / "paper_state_trace.csv",
        [
            {
                "episode_id": 1,
                "time": 1,
                "agent_id": 0,
                "x_n_t": 1,
                "task_id": 1,
                "eta_n": 3.0,
                "w_priv_n": 1.0,
                "w_off_n": 0.0,
                "l_pub_n_prev_json": json.dumps([0.0, 2.0]),
                "active_load_vector_json": json.dumps([1.0, 0.0]),
                "L_t_json": json.dumps([[0.0, 0.0], [1.0, 0.0]]),
                "predicted_next_load_json": json.dumps([1.0, 1.0]),
                "predicted_next_load_method": "persistence_baseline",
                "paper_lstm_forecast": False,
                "unavailable_fields_json": json.dumps([]),
                "approximation_warnings_json": json.dumps(["persistence_baseline"]),
                "state_vector_json": json.dumps([3.0, 1.0, 0.0, 0.0]),
                "state_dim": 4,
            },
            {
                "episode_id": 1,
                "time": 2,
                "agent_id": 0,
                "x_n_t": 0,
                "task_id": 2,
                "eta_n": 0.0,
                "w_priv_n": 0.0,
                "w_off_n": 0.0,
                "l_pub_n_prev_json": json.dumps([0.0, 1.0]),
                "active_load_vector_json": json.dumps([0.0, 0.0]),
                "L_t_json": json.dumps([[0.0, 0.0], [1.0, 0.0]]),
                "predicted_next_load_json": json.dumps([0.0, 0.0]),
                "predicted_next_load_method": "persistence_baseline",
                "paper_lstm_forecast": False,
                "unavailable_fields_json": json.dumps([]),
                "approximation_warnings_json": json.dumps(["persistence_baseline"]),
                "state_vector_json": json.dumps([0.0, 0.0, 0.0, 0.0]),
                "state_dim": 4,
            },
        ],
    )
    _write_csv(
        trace_dir / "delayed_reward_event_trace.csv",
        [
            {
                "task_id": 1,
                "episode_id": 1,
                "source_agent": 0,
                "decision_time": 1,
                "final_status": "completed",
                "completion_time": 2,
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

    transitions, summary = load_trace_dataset(trace_dir)
    transition = next(t for t in transitions if t.episode_id == 1 and t.step_index == 1)
    np.testing.assert_allclose(transition.state, np.asarray([3.0, 1.0, 0.0, 0.0], dtype=np.float32))
    np.testing.assert_allclose(transition.next_state, np.asarray([0.0, 0.0, 0.0, 0.0], dtype=np.float32))
    assert transition.done is False
    assert transition.reward == -1.0
    assert transition.reward_source == "delayed_reward_event_trace"
    assert transition.state_source == "runtime_paper_state_trace"
    assert transition.next_state_source == "runtime_paper_state_trace"
    assert "used delayed_reward_event_trace for reward reconstruction" in summary.notes


def test_terminal_paper_state_row_uses_terminal_copy(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _base_trace_dir(trace_dir)
    _write_csv(
        trace_dir / "paper_state_trace.csv",
        [
            {
                "episode_id": 1,
                "time": 1,
                "agent_id": 0,
                "x_n_t": 1,
                "task_id": 1,
                "eta_n": 3.0,
                "w_priv_n": 1.0,
                "w_off_n": 0.0,
                "l_pub_n_prev_json": json.dumps([0.0, 2.0]),
                "active_load_vector_json": json.dumps([1.0, 0.0]),
                "L_t_json": json.dumps([[0.0, 0.0], [1.0, 0.0]]),
                "predicted_next_load_json": json.dumps([1.0, 1.0]),
                "predicted_next_load_method": "persistence_baseline",
                "paper_lstm_forecast": False,
                "unavailable_fields_json": json.dumps([]),
                "approximation_warnings_json": json.dumps(["persistence_baseline"]),
                "state_vector_json": json.dumps([3.0, 1.0, 0.0, 0.0]),
                "state_dim": 4,
            }
        ],
    )
    _write_csv(
        trace_dir / "delayed_reward_event_trace.csv",
        [
            {
                "task_id": 1,
                "episode_id": 1,
                "source_agent": 0,
                "decision_time": 1,
                "final_status": "completed",
                "completion_time": 1,
                "drop_time": "",
                "delay": 0,
                "reward": -0.0,
                "drop_penalty": 40.0,
                "reward_reason": "completed",
                "paired_transition_found": True,
                "replay_inserted": True,
                "replay_pairing_status": "paired",
                "reward_timing_convention": "completion_minus_arrival",
            }
        ],
    )

    transitions, summary = load_trace_dataset(trace_dir)
    assert len(transitions) == 1
    transition = transitions[0]
    assert transition.done is True
    np.testing.assert_allclose(transition.next_state, transition.state)
    assert transition.next_state_source == "terminal_copy"
    assert summary.terminal_copies >= 1


def test_action_metadata_is_preserved(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _base_trace_dir(trace_dir)
    _write_csv(
        trace_dir / "paper_state_trace.csv",
        [
            {
                "episode_id": 1,
                "time": 1,
                "agent_id": 0,
                "x_n_t": 1,
                "task_id": 1,
                "eta_n": 3.0,
                "w_priv_n": 1.0,
                "w_off_n": 0.0,
                "l_pub_n_prev_json": json.dumps([0.0, 2.0]),
                "active_load_vector_json": json.dumps([1.0, 0.0]),
                "L_t_json": json.dumps([[0.0, 0.0], [1.0, 0.0]]),
                "predicted_next_load_json": json.dumps([1.0, 1.0]),
                "predicted_next_load_method": "persistence_baseline",
                "paper_lstm_forecast": False,
                "unavailable_fields_json": json.dumps([]),
                "approximation_warnings_json": json.dumps(["persistence_baseline"]),
                "state_vector_json": json.dumps([3.0, 1.0, 0.0, 0.0]),
                "state_dim": 4,
            }
        ],
    )
    transitions, _ = load_trace_dataset(trace_dir)
    transition = transitions[0]
    assert transition.raw_action_id == 11
    assert transition.first_stage_decision == "offload"
    assert transition.destination_node_id == 1
    assert transition.destination_type == "vertical_cloud"
    assert transition.is_valid is True
    assert transition.adjacency_allowed is True
    assert transition.cloud_target is True
    assert transition.d_n_1 == 0
    assert transition.d_nk_2 == {"1": 1} or transition.d_nk_2 == {1: 1}


def test_lifecycle_fallback_uses_copied_next_state_with_warning(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _write_csv(
        trace_dir / "task_lifecycle.csv",
        [
            {
                "task_id": 1,
                "episode_id": 1,
                "arrival_time": 1,
                "queue_enter_time": 1,
                "final_status": "completed",
                "completion_time": 4,
                "service_start_time": 2,
                "service_end_time": 4,
                "source_node": 0,
                "selected_action": 1,
                "drop_penalty": 40.0,
            }
        ],
    )
    _write_csv(
        trace_dir / "queue_trace.csv",
        [
            {
                "episode_id": 1,
                "time": 1,
                "node_id": 0,
                "queue_type": "private",
                "queue_length": 1.0,
                "arrivals": 1,
                "departures": 0,
                "drops": 0,
                "cpu_allocated": 1.0,
            }
        ],
    )
    _write_csv(
        trace_dir / "action_trace.csv",
        [
            {
                "episode_id": 1,
                "time": 1,
                "agent_id": 0,
                "x_n_t": 1,
                "observation_shape": json.dumps([12]),
                "selected_action": 1,
                "target_node": 0,
                "reward_received": -3.0,
                "raw_action_id": 11,
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
    _write_csv(
        trace_dir / "episode_metrics.csv",
        [
            {
                "episode_id": 1,
                "total_tasks": 1,
                "completed_tasks": 1,
                "dropped_tasks": 0,
                "pending_tasks": 0,
                "average_latency": 3.0,
                "average_waiting_time": 1.0,
                "average_service_time": 2.0,
                "drop_ratio": 0.0,
                "average_queue_length": 1.0,
                "total_reward": -3.0,
                "mean_reward": -3.0,
            }
        ],
    )

    transitions, summary = load_trace_dataset(trace_dir)
    transition = transitions[0]
    np.testing.assert_allclose(transition.next_state, transition.state)
    assert summary.next_state_source == "legacy_state_copy"
    assert any("copied" in warning.lower() or "missing runtime paper_state_trace" in warning.lower() for warning in summary.approximation_warnings)


def test_train_phase3_validates_transitions_before_training(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _base_trace_dir(trace_dir)
    _write_csv(
        trace_dir / "paper_state_trace.csv",
        [
            {
                "episode_id": 1,
                "time": 1,
                "agent_id": 0,
                "x_n_t": 1,
                "task_id": 1,
                "eta_n": 3.0,
                "w_priv_n": 1.0,
                "w_off_n": 0.0,
                "l_pub_n_prev_json": json.dumps([0.0, 2.0]),
                "active_load_vector_json": json.dumps([1.0, 0.0]),
                "L_t_json": json.dumps([[0.0, 0.0], [1.0, 0.0]]),
                "predicted_next_load_json": json.dumps([1.0, 1.0]),
                "predicted_next_load_method": "persistence_baseline",
                "paper_lstm_forecast": False,
                "unavailable_fields_json": json.dumps([]),
                "approximation_warnings_json": json.dumps(["persistence_baseline"]),
                "state_vector_json": json.dumps([3.0, 1.0, 0.0, 0.0]),
                "state_dim": 4,
            },
            {
                "episode_id": 1,
                "time": 2,
                "agent_id": 0,
                "x_n_t": 0,
                "task_id": 2,
                "eta_n": 0.0,
                "w_priv_n": 0.0,
                "w_off_n": 0.0,
                "l_pub_n_prev_json": json.dumps([0.0, 1.0]),
                "active_load_vector_json": json.dumps([0.0, 0.0]),
                "L_t_json": json.dumps([[0.0, 0.0], [1.0, 0.0]]),
                "predicted_next_load_json": json.dumps([0.0, 0.0]),
                "predicted_next_load_method": "persistence_baseline",
                "paper_lstm_forecast": False,
                "unavailable_fields_json": json.dumps([]),
                "approximation_warnings_json": json.dumps(["persistence_baseline"]),
                "state_vector_json": json.dumps([0.0, 0.0, 0.0, 0.0]),
                "state_dim": 4,
            },
        ],
    )
    _write_csv(
        trace_dir / "delayed_reward_event_trace.csv",
        [
            {
                "task_id": 1,
                "episode_id": 1,
                "source_agent": 0,
                "decision_time": 1,
                "final_status": "completed",
                "completion_time": 2,
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

    output_dir = tmp_path / "out"
    cmd = [
        sys.executable,
        "-m",
        "training.train_phase3",
        "--trace-dir",
        str(trace_dir),
        "--output-dir",
        str(output_dir),
        "--epochs",
        "1",
        "--batch-size",
        "1",
        "--checkpoint-every",
        "1",
        "--seed",
        "7",
    ]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert (output_dir / "dataset_summary.json").exists()
    assert (output_dir / "training_metrics.json").exists()
    summary = json.loads((output_dir / "dataset_summary.json").read_text())
    assert summary["transitions_validated"] >= 1
    assert summary["reward_source_counts"]["delayed_reward_event_trace"] >= 1
