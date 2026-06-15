from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from environment.paper_horizon import PAPER_ACTION_SLOTS, PAPER_DRAIN_SLOTS, PAPER_TOTAL_SLOTS
from .trace_dataset import load_trace_dataset, summary_to_dict


REQUIRED_TRACE_FILES = [
    "task_lifecycle.csv",
    "queue_trace.csv",
    "action_trace.csv",
    "episode_metrics.csv",
]
OPTIONAL_PAPER_TRACE_FILES = [
    "paper_state_trace.csv",
    "delayed_reward_event_trace.csv",
]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def preflight_runtime_trace(trace_dir: str | Path, output_dir: str | Path) -> dict[str, Any]:
    trace_dir = Path(trace_dir)
    output_dir = Path(output_dir)
    required_files_present = {name: (trace_dir / name).exists() for name in REQUIRED_TRACE_FILES}
    missing_required_files = [name for name, present in required_files_present.items() if not present]
    report = {
        "trace_dir": str(trace_dir),
        "required_files_present": required_files_present,
        "missing_required_files": missing_required_files,
        "paper_state_trace_present": (trace_dir / "paper_state_trace.csv").exists(),
        "delayed_reward_event_trace_present": (trace_dir / "delayed_reward_event_trace.csv").exists(),
        "task_lifecycle_present": (trace_dir / "task_lifecycle.csv").exists(),
        "queue_trace_present": (trace_dir / "queue_trace.csv").exists(),
        "action_trace_present": (trace_dir / "action_trace.csv").exists(),
        "episode_metrics_present": (trace_dir / "episode_metrics.csv").exists(),
        "run_horizon_report_present": (trace_dir / "run_horizon_report.json").exists(),
        "run_horizon_report_path": str(trace_dir / "run_horizon_report.json") if (trace_dir / "run_horizon_report.json").exists() else None,
        "preflight_status": "failed" if missing_required_files else "passed",
        "warnings": [],
        "paper_claims_made": False,
        "simulation_executed": False,
        "paper_action_slots": None,
        "paper_drain_slots": None,
        "paper_total_slots": None,
        "horizon_contract_passed": None,
    }
    if not report["paper_state_trace_present"]:
        report["warnings"].append("paper_state_trace.csv missing; state_source degraded")
    if not report["delayed_reward_event_trace_present"]:
        report["warnings"].append("delayed_reward_event_trace.csv missing; reward_source degraded")
    horizon_report_path = trace_dir / "run_horizon_report.json"
    if horizon_report_path.exists():
        try:
            horizon_report = json.loads(horizon_report_path.read_text())
        except Exception as exc:
            report["warnings"].append(f"run_horizon_report.json invalid: {exc}")
            raise ValueError("invalid run_horizon_report.json")
        report["paper_action_slots"] = horizon_report.get("paper_action_slots", PAPER_ACTION_SLOTS)
        report["paper_drain_slots"] = horizon_report.get("paper_drain_slots", PAPER_DRAIN_SLOTS)
        report["paper_total_slots"] = horizon_report.get("paper_total_slots", PAPER_TOTAL_SLOTS)
        report["horizon_contract_passed"] = horizon_report.get("horizon_contract_passed")
        if report["horizon_contract_passed"] is False:
            report["warnings"].append("run_horizon_report.json indicates horizon contract failed")
    else:
        report["warnings"].append("run_horizon_report.json missing; paper horizon not validated for this trace")
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "preflight_runtime_trace_report.json", report)
    if report["horizon_contract_passed"] is False:
        raise ValueError("paper horizon contract failed")
    if missing_required_files:
        raise ValueError(f"missing required trace files: {missing_required_files}")
    return report


def _run_train_phase3_subprocess(
    trace_dir: str | Path,
    output_dir: str | Path,
    algorithm: str,
    epochs: int,
    batch_size: int,
    checkpoint_every: int,
    seed: int,
    gamma: float,
    learning_rate: float,
    train_lstm: bool,
    sequence_length: int,
) -> subprocess.CompletedProcess[str]:
    cmd = [
        sys.executable,
        "-m",
        "training.train_phase3",
        "--trace-dir",
        str(trace_dir),
        "--output-dir",
        str(output_dir),
        "--algorithm",
        algorithm,
        "--epochs",
        str(epochs),
        "--batch-size",
        str(batch_size),
        "--checkpoint-every",
        str(checkpoint_every),
        "--seed",
        str(seed),
        "--gamma",
        str(gamma),
        "--learning-rate",
        str(learning_rate),
    ]
    if train_lstm:
        cmd.extend(["--train-lstm", "--sequence-length", str(sequence_length)])
    return subprocess.run(cmd, check=False, capture_output=True, text=True)


def _missing_keys(payload: dict[str, Any] | None, required_keys: list[str]) -> list[str]:
    if payload is None:
        return required_keys
    return [key for key in required_keys if key not in payload]


def validate_training_artifacts(
    training_dir: str | Path,
    expected_algorithm: str | None = None,
) -> dict[str, Any]:
    training_dir = Path(training_dir)
    checked = {
        "dataset_summary.json": training_dir / "dataset_summary.json",
        "training_metrics.json": training_dir / "training_metrics.json",
        "phase3_training_report.json": training_dir / "phase3_training_report.json",
        "phase3_model.chkpt": training_dir / "phase3_model.chkpt",
    }
    missing = [name for name, path in checked.items() if not path.exists()]
    invalid: list[str] = []
    dataset_summary = None
    training_metrics = None
    training_report = None
    if (training_dir / "dataset_summary.json").exists():
        try:
            dataset_summary = json.loads((training_dir / "dataset_summary.json").read_text())
        except Exception:
            invalid.append("dataset_summary.json")
    if (training_dir / "training_metrics.json").exists():
        try:
            training_metrics = json.loads((training_dir / "training_metrics.json").read_text())
        except Exception:
            invalid.append("training_metrics.json")
    if (training_dir / "phase3_training_report.json").exists():
        try:
            training_report = json.loads((training_dir / "phase3_training_report.json").read_text())
        except Exception:
            invalid.append("phase3_training_report.json")
    dataset_summary_required = [
        "transitions",
        "state_dim",
        "action_count",
        "reward_source_counts",
        "state_source_counts",
        "next_state_source_counts",
    ]
    training_metrics_required = [
        "algorithm",
        "epochs",
        "batch_size",
        "transitions_used",
        "final_checkpoint",
    ]
    training_report_required = [
        "algorithm",
        "q_model_type",
        "model_architecture",
        "paper_claims_made",
        "phase4_evaluation_performed",
    ]
    dataset_summary_missing = _missing_keys(dataset_summary, dataset_summary_required)
    training_metrics_missing = _missing_keys(training_metrics, training_metrics_required)
    training_report_missing = _missing_keys(training_report, training_report_required)
    if dataset_summary_missing:
        invalid.append(f"dataset_summary.json: missing keys {dataset_summary_missing}")
    if training_metrics_missing:
        invalid.append(f"training_metrics.json: missing keys {training_metrics_missing}")
    if training_report_missing:
        invalid.append(f"phase3_training_report.json: missing keys {training_report_missing}")
    if expected_algorithm is not None:
        if training_report and training_report.get("algorithm") != expected_algorithm:
            invalid.append(
                f"phase3_training_report.json: algorithm mismatch expected {expected_algorithm!r} observed {training_report.get('algorithm')!r}"
            )
        if training_metrics and training_metrics.get("algorithm") != expected_algorithm:
            invalid.append(
                f"training_metrics.json: algorithm mismatch expected {expected_algorithm!r} observed {training_metrics.get('algorithm')!r}"
            )
    dataset_summary_contract_passed = not dataset_summary_missing and dataset_summary is not None
    training_metrics_contract_passed = not training_metrics_missing and training_metrics is not None
    training_report_contract_passed = bool(
        training_report
        and not training_report_missing
        and training_report.get("paper_claims_made") is False
        and training_report.get("phase4_evaluation_performed") is False
        and training_report.get("algorithm") is not None
        and training_report.get("q_model_type") is not None
        and training_report.get("model_architecture") is not None
    )
    if expected_algorithm is not None and training_report is not None:
        training_report_contract_passed = training_report_contract_passed and training_report.get("algorithm") == expected_algorithm
    if expected_algorithm is not None and training_metrics is not None:
        training_metrics_contract_passed = training_metrics_contract_passed and training_metrics.get("algorithm") == expected_algorithm
    report_contract_passed = training_report_contract_passed
    artifact_validation_status = "passed" if not missing and not invalid and report_contract_passed else "failed"
    report = {
        "artifact_validation_status": artifact_validation_status,
        "checked_artifacts": list(checked.keys()),
        "missing_artifacts": missing,
        "invalid_artifacts": invalid,
        "dataset_summary_contract_passed": dataset_summary_contract_passed,
        "training_metrics_contract_passed": training_metrics_contract_passed,
        "training_report_contract_passed": training_report_contract_passed,
        "report_contract_passed": report_contract_passed,
        "expected_algorithm": expected_algorithm,
        "observed_algorithm_from_report": training_report.get("algorithm") if training_report else None,
        "observed_algorithm_from_metrics": training_metrics.get("algorithm") if training_metrics else None,
        "paper_claims_made": False,
    }
    _write_json(training_dir / "artifact_validation_report.json", report)
    if artifact_validation_status != "passed":
        raise ValueError(f"training artifact validation failed: missing={missing} invalid={invalid} report_contract_passed={report_contract_passed}")
    return {
        "report": report,
        "dataset_summary": dataset_summary,
        "training_metrics": training_metrics,
        "training_report": training_report,
    }


def _aggregate_episode_metrics(trace_dir: Path) -> dict[str, Any]:
    path = trace_dir / "episode_metrics.csv"
    if not path.exists():
        return {
            "total_tasks": 0,
            "completed_tasks": 0,
            "dropped_tasks": 0,
            "pending_tasks": 0,
            "drop_ratio": 0.0,
            "average_latency": None,
            "average_waiting_time": None,
            "average_service_time": None,
        }
    rows = list(csv.DictReader(path.open()))
    def _sum(key: str) -> int:
        return sum(int(float(row.get(key) or 0)) for row in rows)
    total_tasks = _sum("total_tasks")
    completed_tasks = _sum("completed_tasks")
    dropped_tasks = _sum("dropped_tasks")
    pending_tasks = _sum("pending_tasks")
    def _mean(key: str) -> float | None:
        vals = [float(row[key]) for row in rows if row.get(key) not in (None, "", "None")]
        if not vals:
            return None
        return float(sum(vals) / len(vals))
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "dropped_tasks": dropped_tasks,
        "pending_tasks": pending_tasks,
        "drop_ratio": float(dropped_tasks / total_tasks) if total_tasks else 0.0,
        "average_latency": _mean("average_latency"),
        "average_waiting_time": _mean("average_waiting_time"),
        "average_service_time": _mean("average_service_time"),
    }


def build_offline_evaluation_summary(
    trace_dir: str | Path,
    training_dir: str | Path,
    validation_result: dict[str, Any],
) -> dict[str, Any]:
    trace_dir = Path(trace_dir)
    training_dir = Path(training_dir)
    dataset_summary = validation_result["dataset_summary"]
    training_metrics = validation_result["training_metrics"]
    training_report = validation_result["training_report"]
    transitions_used = int(dataset_summary.get("transitions", 0))
    runtime_metrics = _aggregate_episode_metrics(trace_dir)
    summary = {
        "evaluation_type": "offline_trace_diagnostic_only",
        "paper_performance_claims_made": False,
        "simulation_executed": False,
        "phase4_evaluation_performed": False,
        "algorithm": training_report.get("algorithm"),
        "transitions_used": transitions_used,
        "state_dim": dataset_summary.get("state_dim"),
        "action_count": dataset_summary.get("action_count"),
        "reward_mean": dataset_summary.get("reward_mean"),
        "reward_min": dataset_summary.get("reward_min"),
        "reward_max": dataset_summary.get("reward_max"),
        "reward_source_counts": dataset_summary.get("reward_source_counts", {}),
        "state_source_counts": dataset_summary.get("state_source_counts", {}),
        "next_state_source_counts": dataset_summary.get("next_state_source_counts", {}),
        "terminal_copies": dataset_summary.get("terminal_copies", 0),
        "delayed_reward_matches": dataset_summary.get("delayed_reward_matches", 0),
        "delayed_reward_missing_matches": dataset_summary.get("delayed_reward_missing_matches", 0),
        "training_final_loss": training_metrics.get("final_loss"),
        "training_mean_loss": training_metrics.get("mean_loss"),
        "checkpoint_validated": True,
        "q_model_type": training_report.get("q_model_type"),
        "model_architecture": training_report.get("model_architecture"),
        "runtime_episode_metrics": runtime_metrics,
    }
    _write_json(training_dir / "offline_evaluation_summary.json", summary)
    return summary


def orchestrate(
    trace_dir: str | Path,
    output_dir: str | Path,
    algorithm: str,
    epochs: int,
    batch_size: int,
    checkpoint_every: int,
    seed: int,
    gamma: float = 0.99,
    learning_rate: float = 0.001,
    train_lstm: bool = False,
    sequence_length: int = 2,
) -> dict[str, Any]:
    trace_dir = Path(trace_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    preflight = preflight_runtime_trace(trace_dir, output_dir)
    training_dir = output_dir / "training"
    training_dir.mkdir(parents=True, exist_ok=True)
    result = _run_train_phase3_subprocess(
        trace_dir=trace_dir,
        output_dir=training_dir,
        algorithm=algorithm,
        epochs=epochs,
        batch_size=batch_size,
        checkpoint_every=checkpoint_every,
        seed=seed,
        gamma=gamma,
        learning_rate=learning_rate,
        train_lstm=train_lstm,
        sequence_length=sequence_length,
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or result.stdout.strip() or "training subprocess failed")
    validation_result = validate_training_artifacts(training_dir, expected_algorithm=algorithm)
    summary = build_offline_evaluation_summary(trace_dir, training_dir, validation_result)
    manifest = {
        "model": "Model 11 — End-to-End Runtime / Training / Evaluation Orchestration Contract",
        "status": "passed",
        "branch": "100-hoodie-paper-base",
        "accepted_models": [f"Model {idx}" for idx in range(1, 11)],
        "trace_dir": str(trace_dir),
        "output_dir": str(output_dir),
        "algorithm": algorithm,
        "train_lstm_requested": bool(train_lstm),
        "preflight_report_path": str(output_dir / "preflight_runtime_trace_report.json"),
        "training_output_dir": str(training_dir),
        "artifact_validation_report_path": str(training_dir / "artifact_validation_report.json"),
        "offline_evaluation_summary_path": str(training_dir / "offline_evaluation_summary.json"),
        "dataset_summary_path": str(training_dir / "dataset_summary.json"),
        "training_metrics_path": str(training_dir / "training_metrics.json"),
        "phase3_training_report_path": str(training_dir / "phase3_training_report.json"),
        "final_checkpoint_path": str(training_dir / "phase3_model.chkpt"),
        "run_horizon_report_path": preflight.get("run_horizon_report_path"),
        "paper_action_slots": preflight.get("paper_action_slots"),
        "paper_drain_slots": preflight.get("paper_drain_slots"),
        "paper_total_slots": preflight.get("paper_total_slots"),
        "horizon_contract_passed": preflight.get("horizon_contract_passed"),
        "lstm_artifacts": {},
        "paper_claims_made": False,
        "simulation_executed": False,
        "full_pytest_executed": False,
        "large_artifacts_created": False,
        "cleanup_performed": False,
        "git_add_dot_used": False,
    }
    if train_lstm:
        for name in ("lstm_active_load_vector.chkpt", "paper_state_trace_lstm_forecast.csv"):
            artifact_path = training_dir / name
            if artifact_path.exists():
                manifest["lstm_artifacts"][name] = str(artifact_path)
    _write_json(output_dir / "model11_orchestration_manifest.json", manifest)
    return {
        "preflight": preflight,
        "artifact_validation": validation_result["report"],
        "offline_evaluation_summary": summary,
        "manifest": manifest,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--algorithm", choices=["dqn", "ddqn", "dueling_dqn"], required=True)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--checkpoint-every", type=int, default=1)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--train-lstm", action="store_true")
    parser.add_argument("--sequence-length", type=int, default=2)
    args = parser.parse_args()
    orchestrate(
        trace_dir=args.trace_dir,
        output_dir=args.output_dir,
        algorithm=args.algorithm,
        epochs=args.epochs,
        batch_size=args.batch_size,
        checkpoint_every=args.checkpoint_every,
        seed=args.seed,
        gamma=args.gamma,
        learning_rate=args.learning_rate,
        train_lstm=args.train_lstm,
        sequence_length=args.sequence_length,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
