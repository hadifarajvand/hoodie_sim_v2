from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from training.replay_buffer import Transition
from training.trainers import DQNTrainer, TrainerConfig


def _cfg(algorithm: str = "dqn", hidden_sizes: list[int] | None = None) -> TrainerConfig:
    return TrainerConfig(
        algorithm=algorithm,
        input_dim=4,
        action_dim=3,
        hidden_sizes=hidden_sizes or [8, 4],
        gamma=0.99,
        learning_rate=0.01,
        batch_size=2,
        target_update_interval=2,
        seed=7,
    )


def _transition(state: list[float], action: int, reward: float, next_state: list[float], done: bool = False) -> Transition:
    return Transition(
        state=np.asarray(state, dtype=np.float32),
        action=action,
        reward=reward,
        next_state=np.asarray(next_state, dtype=np.float32),
        done=done,
    )


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _trace_fixture(trace_dir: Path) -> None:
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
                "input_data_size": 5,
                "source_node": 0,
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
    _write_csv(
        trace_dir / "paper_state_trace.csv",
        [
            {
                "episode_id": 1,
                "time": 0,
                "agent_id": 0,
                "x_n_t": 1,
                "task_id": 1,
                "eta_n": 5.0,
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
                "state_vector_json": json.dumps([5.0, 0.0, 0.0, 0.0]),
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
                "active_load_vector_json": json.dumps([0.0, 0.0]),
                "L_t_json": json.dumps([[0.0, 0.0], [0.0, 0.0]]),
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


def test_trainer_config_validation() -> None:
    _cfg("dqn").validate()
    _cfg("ddqn").validate()
    _cfg("dueling_dqn").validate()
    bad = _cfg()
    bad.algorithm = "bogus"
    with np.testing.assert_raises(ValueError):
        bad.validate()
    bad = _cfg()
    bad.hidden_sizes = []
    with np.testing.assert_raises(ValueError):
        bad.validate()
    bad = _cfg()
    bad.hidden_sizes = [8, 0]
    with np.testing.assert_raises(ValueError):
        bad.validate()
    bad = _cfg()
    bad.gamma = 1.5
    with np.testing.assert_raises(ValueError):
        bad.validate()
    bad = _cfg()
    bad.learning_rate = 0.0
    with np.testing.assert_raises(ValueError):
        bad.validate()


def test_hidden_sizes_are_used(tmp_path: Path) -> None:
    trainer = DQNTrainer(_cfg("dqn", [8, 4]))
    assert trainer.policy_net.hidden_sizes == [8, 4]
    assert trainer.policy_net.architecture == "mlp_q_network"
    assert trainer.policy_net.q_model_type == "mlp_q_network"
    ckpt = tmp_path / "model9_hidden_sizes.chkpt"
    trainer.save(ckpt, epochs_completed=1)
    payload = json.loads(ckpt.read_text())
    assert payload["hidden_sizes"] == [8, 4]
    assert payload["q_model_type"] == "mlp_q_network"


def test_dqn_and_ddqn_targets_differ() -> None:
    trainer_dqn = DQNTrainer(_cfg("dqn"))
    trainer_ddqn = DQNTrainer(_cfg("ddqn"))
    for trainer in (trainer_dqn, trainer_ddqn):
        trainer.policy_net.weights = [np.zeros_like(w) for w in trainer.policy_net.weights]
        trainer.policy_net.biases = [np.zeros_like(b) for b in trainer.policy_net.biases]
        trainer.target_net.weights = [np.zeros_like(w) for w in trainer.target_net.weights]
        trainer.target_net.biases = [np.zeros_like(b) for b in trainer.target_net.biases]
    trainer_dqn.target_net.biases[-1] = np.asarray([1.0, 5.0, 2.0], dtype=np.float32)
    trainer_ddqn.target_net.biases[-1] = np.asarray([1.0, 5.0, 2.0], dtype=np.float32)
    trainer_ddqn.policy_net.biases[-1] = np.asarray([9.0, 0.0, 1.0], dtype=np.float32)
    rewards = np.asarray([1.0], dtype=np.float32)
    next_states = np.asarray([[0.0, 0.0, 0.0, 0.0]], dtype=np.float32)
    dones = np.asarray([0.0], dtype=np.float32)
    dqn_target = trainer_dqn._compute_dqn_targets(rewards, next_states, dones)[0]
    ddqn_target = trainer_ddqn._compute_ddqn_targets(rewards, next_states, dones)[0]
    assert dqn_target != ddqn_target
    assert dqn_target > ddqn_target


def test_dueling_architecture_combines_value_and_advantage() -> None:
    trainer = DQNTrainer(_cfg("dueling_dqn"))
    model = trainer.policy_net
    model.shared_weights = [np.zeros_like(w) for w in model.shared_weights]
    model.shared_biases = [np.zeros_like(b) for b in model.shared_biases]
    model.value_weight = np.zeros_like(model.value_weight)
    model.value_weight[:, 0] = np.asarray([2.0, 2.0, 2.0, 2.0], dtype=np.float32)
    model.value_bias = np.asarray([1.0], dtype=np.float32)
    model.advantage_weight = np.zeros_like(model.advantage_weight)
    model.advantage_weight[:, 0] = np.asarray([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
    model.advantage_weight[:, 1] = np.asarray([3.0, 3.0, 3.0, 3.0], dtype=np.float32)
    model.advantage_weight[:, 2] = np.asarray([5.0, 5.0, 5.0, 5.0], dtype=np.float32)
    model.advantage_bias = np.asarray([1.0, -1.0, 0.0], dtype=np.float32)
    model.weights = model.shared_weights + [model.value_weight, model.advantage_weight]
    model.biases = model.shared_biases + [model.value_bias, model.advantage_bias]
    q_values = model.predict(np.asarray([[0.0, 0.0, 0.0, 0.0]], dtype=np.float32))
    expected = np.asarray([[2.0, 0.0, 1.0]], dtype=np.float32)
    np.testing.assert_allclose(q_values, expected)
    assert q_values.shape == (1, 3)


def test_train_step_consumes_valid_replay_transitions() -> None:
    for algorithm in ("dqn", "ddqn", "dueling_dqn"):
        trainer = DQNTrainer(_cfg(algorithm))
        trainer.push(_transition([1, 0, 0, 0], 0, -1.0, [0, 1, 0, 0], False))
        trainer.push(_transition([0, 1, 0, 0], 1, -2.0, [0, 0, 1, 0], True))
        before = trainer.gradient_steps
        metrics = trainer.train_step()
        assert metrics is not None
        assert np.isfinite(metrics.loss)
        assert metrics.transitions_consumed == 2
        assert trainer.gradient_steps == before + 1


def test_invalid_action_range_is_rejected_at_train_time() -> None:
    trainer = DQNTrainer(_cfg("dqn"))
    trainer.push(_transition([1, 0, 0, 0], 9, -1.0, [0, 1, 0, 0], False))
    trainer.push(_transition([0, 1, 0, 0], 1, -2.0, [0, 0, 1, 0], True))
    with np.testing.assert_raises(ValueError):
        trainer.train_step()


def test_checkpoint_roundtrip(tmp_path: Path) -> None:
    trainer = DQNTrainer(_cfg("dueling_dqn"))
    trainer.push(_transition([1, 0, 0, 0], 0, -1.0, [0, 1, 0, 0], False))
    trainer.push(_transition([0, 1, 0, 0], 1, -2.0, [0, 0, 1, 0], True))
    trainer.train_step()
    state = np.asarray([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    before = trainer.policy_net.predict(state.reshape(1, -1))
    ckpt = trainer.save(tmp_path / "model.chkpt", epochs_completed=1)
    restored = DQNTrainer(_cfg("dueling_dqn"))
    restored.load(ckpt)
    after = restored.policy_net.predict(state.reshape(1, -1))
    np.testing.assert_allclose(before, after)


def test_train_phase3_smoke_for_all_algorithms(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _trace_fixture(trace_dir)
    for algorithm in ("dqn", "ddqn", "dueling_dqn"):
        out_dir = tmp_path / f"out_{algorithm}"
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
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        assert (out_dir / "dataset_summary.json").exists()
        assert (out_dir / "training_metrics.json").exists()
        assert (out_dir / "phase3_training_report.json").exists()
        assert (out_dir / "phase3_model.chkpt").exists()
        report = json.loads((out_dir / "phase3_training_report.json").read_text())
        assert report["paper_claims_made"] is False
        assert report["phase4_evaluation_performed"] is False
        assert report["q_model_type"] in {"mlp_q_network", "dueling_mlp_q_network"}
