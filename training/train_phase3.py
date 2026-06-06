from __future__ import annotations

import argparse
import json
from pathlib import Path

from .lstm_forecaster import LSTMForecaster
from .trace_dataset import load_trace_dataset, summary_to_dict
from .trainers import DQNTrainer, TrainerConfig


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--algorithm", choices=["dqn", "ddqn", "dueling_dqn"], default="dqn")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--target-update-interval", type=int, default=10)
    parser.add_argument("--checkpoint-interval", type=int, default=1)
    parser.add_argument("--train-lstm", action="store_true")
    parser.add_argument("--lstm-target", choices=["latency", "queue_length", "reward"], default="latency")
    parser.add_argument("--sequence-length", type=int, default=4)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    transitions, summary = load_trace_dataset(args.trace_dir)
    (output_dir / "dataset_summary.json").write_text(json.dumps(summary_to_dict(summary), indent=2, sort_keys=True))

    report: dict[str, object] = {
        "algorithm": args.algorithm,
        "completed_work": [],
        "skipped_work": [],
        "unavailable_fields": [],
        "approximation_warnings": [],
        "artifact_paths": {"dataset_summary": str(output_dir / "dataset_summary.json")},
    }

    if transitions:
        input_dim = transitions[0].state.shape[0]
        action_dim = len({t.action for t in transitions}) or 1
        trainer_cfg = TrainerConfig(
            algorithm=args.algorithm,
            input_dim=input_dim,
            action_dim=action_dim,
            hidden_sizes=[64, 64],
            gamma=args.gamma,
            learning_rate=args.learning_rate,
            batch_size=args.batch_size,
            target_update_interval=args.target_update_interval,
            seed=args.seed,
        )
        trainer = DQNTrainer(trainer_cfg)
        checkpoint_path = trainer.save(output_dir / "phase3_model.chkpt")
        report["artifact_paths"]["checkpoint"] = checkpoint_path
        for transition in transitions[: max(1, min(len(transitions), args.batch_size))]:
            trainer.push(transition)
        metrics = trainer.train_step()
        if metrics is not None:
            report["completed_work"].append("ran one trainer step against trace-derived transitions")
            report["artifact_paths"]["training_metrics"] = str(output_dir / "training_metrics.json")
            (output_dir / "training_metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True))
        else:
            report["skipped_work"].append("insufficient transitions for a trainer step")
    else:
        report["skipped_work"].append("no transitions available")
        report["artifact_paths"]["checkpoint"] = str(output_dir / "phase3_model.chkpt")
        (output_dir / "phase3_model.chkpt").write_text(
            json.dumps(
                {
                    "cfg": {
                        "algorithm": args.algorithm,
                        "seed": args.seed,
                        "note": "checkpoint emitted even though no transitions were available",
                    },
                    "backend_present": False,
                    "buffer_size": 0,
                    "gradient_steps": 0,
                },
                indent=2,
                sort_keys=True,
            )
        )

    if args.train_lstm:
        forecaster = LSTMForecaster(args.sequence_length, input_dim=1, hidden_dim=16, target=args.lstm_target, seed=args.seed)
        report["skipped_work"].append("LSTM training is not wired to a suitable sequence source yet")

    (output_dir / "phase3_training_report.json").write_text(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
