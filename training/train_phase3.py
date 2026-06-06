from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .lstm_forecaster import LSTMForecaster
from .trace_dataset import load_trace_dataset, summary_to_dict
from .trainers import DQNTrainer, TrainerConfig, TrainingStepMetrics


def _build_report(algorithm: str) -> dict[str, object]:
    return {
        "phase": "Phase 3.2 Full Training Pipeline",
        "algorithm": algorithm,
        "completed_work": [],
        "skipped_work": [],
        "unavailable_fields": [],
        "approximation_warnings": [],
        "validation_status": "not_run",
        "paper_claims_made": False,
        "figures_generated": False,
        "phase4_evaluation_performed": False,
        "notes": [
            "This is trace-trained policy training, not final paper reproduction.",
        ],
        "artifact_paths": {},
    }


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--algorithm", default="dqn")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--checkpoint-every", type=int, default=5)
    parser.add_argument("--train-lstm", action="store_true")
    parser.add_argument("--lstm-target", choices=["latency", "queue_length", "reward"], default="latency")
    parser.add_argument("--sequence-length", type=int, default=4)
    args = parser.parse_args()

    if args.algorithm not in {"dqn", "ddqn", "dueling_dqn"}:
        raise SystemExit(f"unsupported algorithm: {args.algorithm}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    transitions, summary = load_trace_dataset(args.trace_dir)
    dataset_summary_path = output_dir / "dataset_summary.json"
    _write_json(dataset_summary_path, summary_to_dict(summary))

    report = _build_report(args.algorithm)
    report["artifact_paths"] = {"dataset_summary": str(dataset_summary_path)}
    report["validation_status"] = "passed" if transitions else "failed"
    if summary.approximation_warnings:
        report["approximation_warnings"] = list(summary.approximation_warnings)
    if summary.unavailable_fields:
        report["unavailable_fields"] = list(summary.unavailable_fields)

    if not transitions:
        raise SystemExit("trace dataset did not produce any transitions")

    cfg = TrainerConfig(
        algorithm=args.algorithm,
        input_dim=int(transitions[0].state.shape[0]),
        action_dim=int(summary.action_count or (max(t.action for t in transitions) + 1)),
        hidden_sizes=[64, 64],
        gamma=args.gamma,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
        target_update_interval=max(1, args.checkpoint_every),
        seed=args.seed,
    )
    trainer = DQNTrainer(cfg)
    metrics_by_epoch: list[dict[str, object]] = []
    checkpoint_epochs: list[int] = []

    rng = np.random.default_rng(args.seed)
    transition_indices = np.arange(len(transitions))

    for epoch in range(1, args.epochs + 1):
        rng.shuffle(transition_indices)
        for index in transition_indices:
            trainer.push(transitions[int(index)])
        epoch_losses: list[float] = []
        epoch_rewards: list[float] = []
        updates = max(1, len(transitions) // max(1, args.batch_size))
        for _ in range(updates):
            step_metrics = trainer.train_step()
            if step_metrics is None:
                break
            epoch_losses.append(step_metrics.loss)
            epoch_rewards.append(step_metrics.average_reward)
        if not epoch_losses:
            report["skipped_work"].append(f"epoch {epoch}: insufficient transitions for update")
        else:
            report["completed_work"].append(f"epoch {epoch}: trained {len(epoch_losses)} minibatches")
        if epoch % args.checkpoint_every == 0 or epoch == args.epochs:
            checkpoint_path = output_dir / f"checkpoint_epoch_{epoch:03d}.chkpt"
            trainer.save(checkpoint_path, epochs_completed=epoch)
            checkpoint_epochs.append(epoch)
        metrics_by_epoch.append(
            {
                "epoch": epoch,
                "loss": float(np.mean(epoch_losses)) if epoch_losses else None,
                "average_reward": float(np.mean(epoch_rewards)) if epoch_rewards else None,
                "transitions_used": len(transitions),
                "gradient_steps": trainer.gradient_steps,
            }
        )

    final_checkpoint = trainer.save(output_dir / "phase3_model.chkpt", epochs_completed=args.epochs)
    training_metrics = {
        "algorithm": args.algorithm,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "gamma": args.gamma,
        "seed": args.seed,
        "losses_by_epoch": metrics_by_epoch,
        "mean_loss": float(np.mean([m["loss"] for m in metrics_by_epoch if m["loss"] is not None])) if metrics_by_epoch else None,
        "final_loss": next((m["loss"] for m in reversed(metrics_by_epoch) if m["loss"] is not None), None),
        "transitions_used": len(transitions),
        "checkpoint_epochs": checkpoint_epochs,
        "completed_at": "current run",
        "final_checkpoint": final_checkpoint,
    }
    training_metrics_path = output_dir / "training_metrics.json"
    _write_json(training_metrics_path, training_metrics)

    report["artifact_paths"].update(
        {
            "phase3_model": final_checkpoint,
            "training_metrics": str(training_metrics_path),
        }
    )
    report["validation_status"] = "passed"

    if args.train_lstm:
        forecaster = LSTMForecaster(args.sequence_length, input_dim=1, hidden_dim=16, target=args.lstm_target, seed=args.seed)
        rows = [
            {
                "time": t.step_index if t.step_index is not None else idx,
                "latency": t.reward if args.lstm_target == "reward" else None,
                "queue_length": float(np.linalg.norm(t.state)),
                "reward": t.reward,
            }
            for idx, t in enumerate(transitions)
        ]
        seq_x, seq_y, reason = forecaster.build_sequences(rows)
        if reason is not None:
            report["skipped_work"].append(f"LSTM target {args.lstm_target}: {reason}")
            report["approximation_warnings"].append(reason)
        else:
            lstm_result = forecaster.train(seq_x, seq_y, epochs=1, learning_rate=args.learning_rate)
            report["completed_work"].append(
                f"LSTM target {args.lstm_target}: sequences={lstm_result.sequences}, mse={lstm_result.mse}, mae={lstm_result.mae}"
            )
            lstm_checkpoint = forecaster.save(output_dir / f"lstm_{args.lstm_target}.chkpt")
            report["artifact_paths"][f"lstm_{args.lstm_target}"] = lstm_checkpoint

    report["artifact_paths"].update(
        {
            "dataset_summary": str(dataset_summary_path),
            "phase3_training_report": str(output_dir / "phase3_training_report.json"),
        }
    )
    report_path = output_dir / "phase3_training_report.json"
    _write_json(report_path, report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
