from __future__ import annotations

import argparse
import csv
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


def _load_paper_state_rows(trace_dir: Path) -> list[dict[str, object]]:
    paper_state_path = trace_dir / "paper_state_trace.csv"
    if not paper_state_path.exists():
        return []
    with paper_state_path.open(newline="") as f:
        return list(csv.DictReader(f))


def _vector_from_json_row(row: dict[str, object], key: str) -> np.ndarray | None:
    raw = row.get(key)
    if raw in (None, "", "None"):
        return None
    try:
        value = json.loads(str(raw))
    except Exception:
        return None
    array = np.asarray(value, dtype=np.float32)
    if array.ndim != 1 or not np.all(np.isfinite(array)):
        return None
    return array


def _rebuild_state_vector(transition) -> np.ndarray:
    parts = [
        np.asarray(
            [
                np.nan if transition.eta_n is None else transition.eta_n,
                np.nan if transition.w_priv_n is None else transition.w_priv_n,
                np.nan if transition.w_off_n is None else transition.w_off_n,
            ],
            dtype=np.float32,
        )
    ]
    if transition.l_pub_n_prev is not None and transition.l_pub_n_prev.size:
        parts.append(np.asarray(transition.l_pub_n_prev, dtype=np.float32).reshape(-1))
    if transition.load_history is not None and transition.load_history.size:
        parts.append(np.asarray(transition.load_history, dtype=np.float32).reshape(-1))
    if transition.predicted_next_load is not None and transition.predicted_next_load.size:
        parts.append(np.asarray(transition.predicted_next_load, dtype=np.float32).reshape(-1))
    return np.concatenate(parts).astype(np.float32)


def _write_runtime_state_artifacts(
    output_dir: Path,
    trace_dir: Path,
    summary: object,
    sample_rows: list[dict[str, object]] | None = None,
    paper_state_rows: list[dict[str, object]] | None = None,
) -> None:
    summary_dict = summary_to_dict(summary)
    report = {
        "branch": "100-hoodie-paper-base",
        "phase": "Phase 3.2",
        "previous_gaps": [
            "next_state_not_copy",
            "waiting_time_not_queue_length_proxy",
            "active_load_matrix_not_queue_length_history",
        ],
        "repair_status": {
            "next_state_not_copy": "CLOSED" if summary_dict.get("paper_state_trace_present") else "OPEN",
            "waiting_time_not_queue_length_proxy": "PARTIAL" if summary_dict.get("paper_state_trace_present") else "OPEN",
            "active_load_matrix_not_queue_length_history": "PARTIAL" if summary_dict.get("paper_state_trace_present") else "OPEN",
        },
        "evidence": [
            "paper_state_trace.csv exported at runtime",
            f"state_source={summary_dict.get('state_source')}",
            f"next_state_source={summary_dict.get('next_state_source')}",
            f"predicted_next_load_method={summary_dict.get('predicted_next_load_method')}",
        ],
        "remaining_limitations": [
            "predicted_next_load uses a persistence baseline, not a trained LSTM",
            "waiting-time fields are runtime estimates, not a paper-verified analytical derivation",
        ],
        "next_required_step": "phase3.3 paper-faithful LSTM and reward timing repair",
        "runtime_behavior_changed": False,
        "paper_performance_claims_made": False,
        "artifact_paths": {},
    }
    (output_dir / "phase3_runtime_state_report.json").write_text(json.dumps(report, indent=2, sort_keys=True))
    lines = [
        "# Phase 3.2 Runtime Paper State Repair",
        "",
        f"state_source: {summary_dict.get('state_source')}",
        f"next_state_source: {summary_dict.get('next_state_source')}",
        f"waiting_time_source: {summary_dict.get('waiting_time_source')}",
        f"load_history_source: {summary_dict.get('load_history_source')}",
        f"predicted_next_load_method: {summary_dict.get('predicted_next_load_method')}",
        f"paper_lstm_forecast: {summary_dict.get('paper_lstm_forecast')}",
    ]
    (output_dir / "phase3_runtime_state_report.md").write_text("\n".join(lines))
    contract = {
        "next_state_not_copy": "closed" if summary_dict.get("paper_state_trace_present") else "open",
        "waiting_time_not_queue_length_proxy": "partial" if summary_dict.get("paper_state_trace_present") else "open",
        "active_load_matrix_not_queue_length_history": "partial" if summary_dict.get("paper_state_trace_present") else "open",
    }
    (output_dir / "state_source_contract.json").write_text(json.dumps(contract, indent=2, sort_keys=True))
    gap_rows = [
        ["previous_gap", "repair_status", "evidence", "remaining_limitation", "next_required_step"],
        ["next_state_not_copy", contract["next_state_not_copy"].upper(), "next_state is paired from the next runtime paper state row", "terminal rows still copy state when no t+1 exists", "carry terminal bootstrap/episode-end handling"],
        ["waiting_time_not_queue_length_proxy", contract["waiting_time_not_queue_length_proxy"].upper(), "waiting time is read from runtime queue waiting counters", "some queues still expose approximate counters only", "instrument exact queue timing if needed"],
        ["active_load_matrix_not_queue_length_history", contract["active_load_matrix_not_queue_length_history"].upper(), "L_t is exported as active-load history", "persistence baseline forecast is still not an LSTM", "replace persistence with trained LSTM"],
    ]
    with (output_dir / "gap_closure_matrix.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(gap_rows)
    if paper_state_rows is not None and paper_state_rows:
        with (output_dir / "paper_state_trace.csv").open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(paper_state_rows[0].keys()))
            writer.writeheader()
            writer.writerows(paper_state_rows)
    else:
        paper_state_path = trace_dir / "paper_state_trace.csv"
        if paper_state_path.exists():
            (output_dir / "paper_state_trace.csv").write_text(paper_state_path.read_text())
    if sample_rows is not None:
        with (output_dir / "sample_paper_state_trace.csv").open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(sample_rows[0].keys()))
            writer.writeheader()
            writer.writerows(sample_rows)
    else:
        paper_state_path = output_dir / "paper_state_trace.csv"
        if paper_state_path.exists():
            sample_lines = paper_state_path.read_text().splitlines()[:5]
            (output_dir / "sample_paper_state_trace.csv").write_text("\n".join(sample_lines) + "\n")
    report["artifact_paths"] = {
        "dataset_summary": str(output_dir / "dataset_summary.json"),
        "phase3_runtime_state_report": str(output_dir / "phase3_runtime_state_report.json"),
        "state_source_contract": str(output_dir / "state_source_contract.json"),
        "gap_closure_matrix": str(output_dir / "gap_closure_matrix.csv"),
    }
    (output_dir / "phase3_runtime_state_report.json").write_text(json.dumps(report, indent=2, sort_keys=True))


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
    parser.add_argument("--lstm-target", choices=["active_load_vector"], default="active_load_vector")
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
    report["lstm_forecast_requested"] = bool(args.train_lstm)
    report["lstm_forecast_status"] = "skipped"
    report["predicted_next_load_method"] = "persistence_baseline"
    report["paper_lstm_forecast"] = False
    report["lstm_target"] = "active_load_vector"
    report["paper_claims_made"] = False
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
    report["algorithm"] = cfg.algorithm
    report["q_model_type"] = trainer.policy_net.q_model_type
    report["model_architecture"] = trainer.policy_net.architecture
    report["paper_claims_made"] = False
    report["phase4_evaluation_performed"] = False
    metrics_by_epoch: list[dict[str, object]] = []
    checkpoint_epochs: list[int] = []

    rng = np.random.default_rng(args.seed)
    transition_indices = np.arange(len(transitions))

    for epoch in range(1, args.epochs + 1):
        rng.shuffle(transition_indices)
        for index in transition_indices:
            transition = transitions[int(index)]
            try:
                transition.validate()
            except Exception as exc:
                raise SystemExit(f"invalid training transition at index {int(index)}: {exc}") from exc
            trainer.push(transition)
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

    sample_rows: list[dict[str, object]] | None = None
    paper_state_rows: list[dict[str, object]] | None = None
    forecast_artifact_rows: list[dict[str, object]] | None = None
    paper_state_rows_raw = _load_paper_state_rows(Path(args.trace_dir))
    if args.train_lstm:
        if not summary.paper_state_trace_present or not paper_state_rows_raw:
            report["lstm_forecast_status"] = "skipped_insufficient_data"
            report["lstm_reason"] = "paper_state_trace unavailable"
            report["skipped_work"].append("LSTM forecast skipped: paper_state_trace unavailable")
        else:
            active_rows = []
            for row in paper_state_rows_raw:
                vector = _vector_from_json_row(row, "active_load_vector_json")
                if vector is None:
                    continue
                normalized_row = dict(row)
                normalized_row["active_load_vector"] = vector
                active_rows.append(normalized_row)
            lstm_input_dim = int(active_rows[0]["active_load_vector"].shape[0]) if active_rows else 1
            forecaster = LSTMForecaster(args.sequence_length, input_dim=lstm_input_dim, hidden_dim=16, target=args.lstm_target, seed=args.seed, output_dim=lstm_input_dim)
            seq_x, seq_y, reason = forecaster.build_sequences(active_rows)
            if reason is not None or len(seq_x) == 0:
                report["lstm_forecast_status"] = "skipped_insufficient_data"
                report["lstm_reason"] = reason or "not enough active_load_vector samples"
                report["skipped_work"].append(f"LSTM forecast skipped: {report['lstm_reason']}")
                report["approximation_warnings"].append("persistence_baseline retained because LSTM training had insufficient data")
            else:
                lstm_result = forecaster.train(seq_x, seq_y, epochs=1, learning_rate=args.learning_rate)
                report["lstm_forecast_status"] = "trained"
                report["lstm_sequences"] = lstm_result.sequences
                report["lstm_mse"] = lstm_result.mse
                report["lstm_mae"] = lstm_result.mae
                report["lstm_target"] = lstm_result.target
                report["predicted_next_load_method"] = lstm_result.forecast_method or "trained_lstm"
                report["paper_lstm_forecast"] = bool(lstm_result.paper_lstm_forecast)
                report["completed_work"].append(
                    f"LSTM target active_load_vector: sequences={lstm_result.sequences}, mse={lstm_result.mse}, mae={lstm_result.mae}"
                )
                lstm_checkpoint = forecaster.save(output_dir / "lstm_active_load_vector.chkpt")
                report["artifact_paths"]["lstm_active_load_vector"] = lstm_checkpoint
                report["approximation_warnings"].append("trained_lstm_forecast_artifact is non-official and reproduction-oriented only")
                forecast_artifact_rows = []
                for row in active_rows:
                    enriched = dict(row)
                    history = _vector_from_json_row(row, "L_t_json")
                    if history is None:
                        history = np.asarray([row["active_load_vector"]], dtype=np.float32)
                    predicted = forecaster.predict(history)
                    enriched["predicted_next_load_json"] = json.dumps(predicted.tolist())
                    enriched["predicted_next_load_method"] = "trained_lstm"
                    enriched["paper_lstm_forecast"] = True
                    warnings = list(json.loads(row.get("approximation_warnings_json") or "[]"))
                    warnings.append("trained_lstm_forecast_artifact")
                    enriched["approximation_warnings_json"] = json.dumps(warnings)
                    forecast_artifact_rows.append(enriched)
                forecast_path = output_dir / "paper_state_trace_lstm_forecast.csv"
                if forecast_artifact_rows:
                    with forecast_path.open("w", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=list(forecast_artifact_rows[0].keys()))
                        writer.writeheader()
                        writer.writerows(forecast_artifact_rows)
                report["artifact_paths"]["paper_state_trace_lstm_forecast"] = str(forecast_path)
                sample_rows = forecast_artifact_rows[:10]
    else:
        report["lstm_forecast_status"] = "skipped"
        report["lstm_reason"] = "explicitly disabled by CLI"
        report["skipped_work"].append("LSTM forecast skipped intentionally because --train-lstm was not passed")
        report["approximation_warnings"].append("persistence_baseline retained because --train-lstm was not passed")

    if summary.paper_state_trace_present:
        _write_runtime_state_artifacts(output_dir, Path(args.trace_dir), summary, sample_rows=sample_rows, paper_state_rows=paper_state_rows)

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
