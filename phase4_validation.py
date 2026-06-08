from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import tempfile
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from training.trace_dataset import load_trace_dataset, summary_to_dict


ROOT = Path(__file__).resolve().parent
PYTHON = ROOT / ".venvmac" / "bin" / "python"
REQUIRED_TRACE_FILES = (
    "task_lifecycle.csv",
    "queue_trace.csv",
    "action_trace.csv",
    "paper_state_trace.csv",
    "episode_metrics.csv",
)


@dataclass(frozen=True)
class ValidationConfig:
    episodes: int
    output_dir: str
    seed: int
    mode: str
    raw_trace_dir: str | None
    keep_raw_traces: bool
    train_after_run: bool
    batch_size: int
    checkpoint_every: int
    sequence_length: int
    max_sample_rows: int
    fail_on_missing_paper_state: bool
    fail_on_invalid_actions: bool
    fail_on_non_lstm_forecast: bool
    timestamp: str
    branch: str | None
    commit: str | None


def _safe_int(value: Any) -> int | None:
    if value in (None, "", "None"):
        return None
    try:
        return int(float(value))
    except Exception:
        return None


def _safe_float(value: Any) -> float | None:
    if value in (None, "", "None"):
        return None
    try:
        return float(value)
    except Exception:
        return None


def _load_csv(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _json_value(value: Any) -> Any:
    if value in (None, "", "None"):
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return value
    return value


def _shape_from_json(value: Any) -> tuple[int, ...] | None:
    parsed = _json_value(value)
    if parsed is None:
        return None
    arr = np.asarray(parsed)
    return tuple(int(x) for x in arr.shape)


def _count_by_key(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        counter[str(row.get(key))] += 1
    return dict(counter)


def _array_len(value: Any) -> int | None:
    parsed = _json_value(value)
    if parsed is None:
        return None
    try:
        arr = np.asarray(parsed)
        return int(arr.reshape(-1).shape[0])
    except Exception:
        return None


def _read_trace_files(trace_dir: Path) -> dict[str, list[dict[str, Any]]]:
    return {name: _load_csv(trace_dir / name) for name in REQUIRED_TRACE_FILES}


def _build_episode_summary(episode_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "episode_id": row.get("episode_id"),
            "total_tasks": _safe_int(row.get("total_tasks")),
            "completed_tasks": _safe_int(row.get("completed_tasks")),
            "dropped_tasks": _safe_int(row.get("dropped_tasks")),
            "pending_tasks": _safe_int(row.get("pending_tasks")),
            "drop_ratio": _safe_float(row.get("drop_ratio")),
            "completion_ratio": (
                (_safe_int(row.get("completed_tasks")) or 0) / (_safe_int(row.get("total_tasks")) or 1)
                if _safe_int(row.get("total_tasks"))
                else None
            ),
            "average_latency": _safe_float(row.get("average_latency")),
            "average_waiting_time": _safe_float(row.get("average_waiting_time")),
            "average_service_time": _safe_float(row.get("average_service_time")),
            "average_queue_length": _safe_float(row.get("average_queue_length")),
            "total_reward": _safe_float(row.get("total_reward")),
            "mean_reward": _safe_float(row.get("mean_reward")),
        }
        for row in episode_rows
    ]


def _validate_trace_completeness(trace_rows: dict[str, list[dict[str, Any]]], expected_episodes: int) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    warnings: list[str] = []
    missing = [name for name in REQUIRED_TRACE_FILES if name not in trace_rows or not trace_rows[name]]
    if missing:
        blockers.append(f"missing required trace files: {missing}")
    episode_rows = trace_rows.get("episode_metrics.csv", [])
    if episode_rows and len(episode_rows) != expected_episodes:
        warnings.append(f"episode_metrics row count {len(episode_rows)} != requested episodes {expected_episodes}")
    return blockers, warnings


def _validate_actions(action_rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(action_rows)
    valid = 0
    invalid = 0
    local = horizontal = vertical = 0
    missing_selected = 0
    non_neighbor = 0
    self_offload = 0
    by_type = Counter()
    reasons = Counter()
    for row in action_rows:
        is_valid = str(row.get("is_valid")).lower() == "true"
        if is_valid:
            valid += 1
        else:
            invalid += 1
        destination_type = str(row.get("destination_type") or "unknown")
        by_type[destination_type] += 1
        if destination_type == "local":
            local += 1
        elif destination_type == "horizontal_edge":
            horizontal += 1
        elif destination_type == "vertical_cloud":
            vertical += 1
        if row.get("selected_action") in (None, ""):
            missing_selected += 1
        invalid_reason = str(row.get("invalid_reason") or "")
        reasons[invalid_reason] += 1
        if "adjac" in invalid_reason.lower() or "neighbor" in invalid_reason.lower():
            non_neighbor += 1
        if "self" in invalid_reason.lower():
            self_offload += 1
    return {
        "total_actions": total,
        "valid_actions": valid,
        "invalid_actions": invalid,
        "invalid_action_ratio": (invalid / total) if total else 0.0,
        "local_action_count": local,
        "horizontal_action_count": horizontal,
        "vertical_cloud_action_count": vertical,
        "action_distribution_by_type": dict(by_type),
        "missing_selected_action_count": missing_selected,
        "non_neighbor_offload_count": non_neighbor,
        "self_offload_violation_count": self_offload,
        "invalid_action_reasons": dict(reasons),
    }


def _validate_state_lstm(paper_state_rows: list[dict[str, Any]], transitions: list[Any]) -> dict[str, Any]:
    state_dims = [_safe_int(row.get("state_dim")) for row in paper_state_rows if _safe_int(row.get("state_dim")) is not None]
    l_shapes = [_shape_from_json(row.get("L_t_json")) for row in paper_state_rows]
    active_lengths = [_array_len(row.get("active_load_vector_json")) for row in paper_state_rows]
    predicted_lengths = [_array_len(row.get("predicted_next_load_json")) for row in paper_state_rows if row.get("predicted_next_load_json") not in (None, "", "None")]
    pred_methods = Counter(str(row.get("predicted_next_load_method") or "unknown") for row in paper_state_rows)
    forecast_true = sum(str(row.get("paper_lstm_forecast")).lower() == "true" for row in paper_state_rows)
    forecast_false = sum(str(row.get("paper_lstm_forecast")).lower() == "false" for row in paper_state_rows)
    unavailable_fields = Counter()
    approximation_warnings = Counter()
    for row in paper_state_rows:
        for field in _json_value(row.get("unavailable_fields_json")) or []:
            unavailable_fields[str(field)] += 1
        for field in _json_value(row.get("approximation_warnings_json")) or []:
            approximation_warnings[str(field)] += 1
    nonterminal_copy = 0
    terminal_copy = 0
    for transition in transitions:
        if getattr(transition, "done", False):
            terminal_copy += 1
        elif np.array_equal(getattr(transition, "state", np.array([])), getattr(transition, "next_state", np.array([]))):
            nonterminal_copy += 1
    return {
        "paper_state_rows": len(paper_state_rows),
        "state_dim_min": min(state_dims) if state_dims else None,
        "state_dim_max": max(state_dims) if state_dims else None,
        "state_dim_unique_values": sorted(set(state_dims)) if state_dims else [],
        "expected_state_dim": max(state_dims) if state_dims else None,
        "L_t_shape": list(next((shape for shape in l_shapes if shape is not None), ())),
        "active_load_vector_length": max(active_lengths) if active_lengths else None,
        "predicted_next_load_length": max(predicted_lengths) if predicted_lengths else None,
        "predicted_next_load_method_counts": dict(pred_methods),
        "paper_lstm_forecast_true_count": forecast_true,
        "paper_lstm_forecast_false_count": forecast_false,
        "unavailable_fields_counts": dict(unavailable_fields),
        "approximation_warning_counts": dict(approximation_warnings),
        "nonterminal_next_state_copy_count": nonterminal_copy,
        "terminal_next_state_copy_count": terminal_copy,
    }


def _dataset_summary_from_trace(trace_dir: Path) -> tuple[list[Any], dict[str, Any]]:
    transitions, summary = load_trace_dataset(trace_dir)
    return transitions, summary_to_dict(summary)


def assess_readiness(report: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    criteria: list[dict[str, Any]] = []

    def criterion(name: str, expected: str, observed: Any, ok: bool, warn: bool = False, evidence: str = "", next_action: str = "") -> None:
        status = "PASS" if ok else ("WARN" if warn else "FAIL")
        criteria.append(
            {
                "criterion": name,
                "expected": expected,
                "observed": observed,
                "status": status,
                "evidence": evidence,
                "next_action": next_action,
            }
        )
        if status == "FAIL":
            blockers.append(name)
        elif status == "WARN":
            warnings.append(name)

    episodes_completed = report.get("episodes_completed", 0)
    episode_metrics_count = report.get("episode_metrics_count", 0)
    paper_state_present = bool(report.get("paper_state_trace_present"))
    invalid_ratio = float(report.get("invalid_action_ratio") or 0.0)
    non_neighbor = int(report.get("non_neighbor_offload_count") or 0)
    self_offload = int(report.get("self_offload_violation_count") or 0)
    state_dim_min = report.get("state_dim_min")
    state_dim_max = report.get("state_dim_max")
    l_shape = report.get("L_t_shape") or []
    active_len = report.get("active_load_vector_length")
    predicted_len = report.get("predicted_next_load_length")
    pred_methods = report.get("predicted_next_load_method_counts", {})
    forecast_false = int(report.get("paper_lstm_forecast_false_count") or 0)
    transitions = int(report.get("transitions") or 0)
    state_source = report.get("state_source")
    next_state_source = report.get("next_state_source")
    nonterminal_copy = int(report.get("nonterminal_next_state_copy_count") or 0)
    paper_performance = bool(report.get("paper_performance_claims_made"))

    criterion("episodes_completed", "200", episodes_completed, episodes_completed >= 200, evidence=f"{episodes_completed}")
    criterion("episode_metrics_count", "200", episode_metrics_count, episode_metrics_count == 200, evidence=f"{episode_metrics_count}")
    criterion("paper_state_trace_present", "true", paper_state_present, paper_state_present, evidence=str(paper_state_present))
    criterion("invalid_action_ratio", "0", invalid_ratio, invalid_ratio == 0.0, evidence=str(invalid_ratio))
    criterion("non_neighbor_offload_count", "0", non_neighbor, non_neighbor == 0, evidence=str(non_neighbor))
    criterion("self_offload_violation_count", "0", self_offload, self_offload == 0, evidence=str(self_offload))
    criterion("state_dim_stable", ">2 and consistent", f"{state_dim_min}..{state_dim_max}", state_dim_min is not None and state_dim_max is not None and state_dim_min > 2 and state_dim_min == state_dim_max, evidence=str((state_dim_min, state_dim_max)))
    criterion("L_t_shape", "W x (N+1)", l_shape, len(l_shape) == 2 and all(int(x) > 0 for x in l_shape), evidence=str(l_shape))
    criterion("active_load_vector_length", "N+1", active_len, active_len is not None and int(active_len) > 0, evidence=str(active_len))
    criterion("predicted_next_load_length", "N+1", predicted_len, predicted_len is not None and int(predicted_len) > 0, evidence=str(predicted_len))
    criterion("predicted_next_load_method_reported", "reported", pred_methods, bool(pred_methods), evidence=str(pred_methods))
    criterion("paper_lstm_forecast_true_or_justified_false", "true or justified false", forecast_false, True if forecast_false == 0 else False, warn=forecast_false > 0, evidence=str(forecast_false), next_action="replace baseline forecast with trained LSTM" if forecast_false > 0 else "")
    criterion("transitions", ">0", transitions, transitions > 0, evidence=str(transitions))
    criterion("state_source", "runtime_paper_state_trace", state_source, state_source == "runtime_paper_state_trace", evidence=str(state_source))
    criterion("next_state_source", "runtime_paper_state_trace", next_state_source, next_state_source == "runtime_paper_state_trace", evidence=str(next_state_source))
    criterion("nonterminal_next_state_copy_count", "0", nonterminal_copy, nonterminal_copy == 0, evidence=str(nonterminal_copy))
    criterion("paper_performance_claims_made", "false", paper_performance, not paper_performance, evidence=str(paper_performance))

    ready = not blockers and report.get("episodes_completed", 0) >= 200 and episode_metrics_count == 200 and paper_state_present and invalid_ratio == 0.0 and non_neighbor == 0 and self_offload == 0 and state_dim_min is not None and state_dim_max is not None and state_dim_min == state_dim_max and state_dim_min > 2 and len(l_shape) == 2 and transitions > 0 and state_source == "runtime_paper_state_trace" and next_state_source == "runtime_paper_state_trace" and nonterminal_copy == 0 and not paper_performance
    return {
        "ready_for_phase5_figures": ready,
        "blockers": blockers,
        "warnings": warnings,
        "criteria": criteria,
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _build_report(trace_dir: Path, output_dir: Path, config: ValidationConfig) -> dict[str, Any]:
    trace_rows = _read_trace_files(trace_dir)
    blockers, warnings = _validate_trace_completeness(trace_rows, config.episodes)
    transitions, dataset_summary = _dataset_summary_from_trace(trace_dir) if (trace_dir / "paper_state_trace.csv").exists() else ([], {})

    action_summary = _validate_actions(trace_rows.get("action_trace.csv", []))
    state_summary = _validate_state_lstm(trace_rows.get("paper_state_trace.csv", []), transitions)
    episode_summary_rows = _build_episode_summary(trace_rows.get("episode_metrics.csv", []))

    report = {
        "branch": config.branch,
        "commit": config.commit,
        "mode": config.mode,
        "validation_status": "FAILED" if blockers else "PASSED",
        "ready_for_phase5_figures": False,
        "blockers": list(blockers),
        "warnings": list(warnings),
        "episodes_requested": config.episodes,
        "episodes_completed": len(trace_rows.get("episode_metrics.csv", [])),
        "total_tasks": sum(row.get("total_tasks") or 0 for row in episode_summary_rows),
        "completed_tasks": sum(row.get("completed_tasks") or 0 for row in episode_summary_rows),
        "dropped_tasks": sum(row.get("dropped_tasks") or 0 for row in episode_summary_rows),
        "pending_tasks": sum(row.get("pending_tasks") or 0 for row in episode_summary_rows),
        "drop_ratio": (sum(row.get("dropped_tasks") or 0 for row in episode_summary_rows) / max(1, sum(row.get("total_tasks") or 0 for row in episode_summary_rows))),
        "completion_ratio": (sum(row.get("completed_tasks") or 0 for row in episode_summary_rows) / max(1, sum(row.get("total_tasks") or 0 for row in episode_summary_rows))),
        "average_latency": float(np.mean([row["average_latency"] for row in episode_summary_rows if row["average_latency"] is not None])) if episode_summary_rows else None,
        "average_waiting_time": float(np.mean([row["average_waiting_time"] for row in episode_summary_rows if row["average_waiting_time"] is not None])) if episode_summary_rows else None,
        "average_service_time": float(np.mean([row["average_service_time"] for row in episode_summary_rows if row["average_service_time"] is not None])) if episode_summary_rows else None,
        "average_queue_length": float(np.mean([row["average_queue_length"] for row in episode_summary_rows if row["average_queue_length"] is not None])) if episode_summary_rows else None,
        "total_reward": float(np.sum([row["total_reward"] for row in episode_summary_rows if row["total_reward"] is not None])) if episode_summary_rows else None,
        "mean_reward": float(np.mean([row["mean_reward"] for row in episode_summary_rows if row["mean_reward"] is not None])) if episode_summary_rows else None,
        **action_summary,
        **state_summary,
        "paper_state_trace_present": (trace_dir / "paper_state_trace.csv").exists(),
        "state_source": dataset_summary.get("state_source"),
        "next_state_source": dataset_summary.get("next_state_source"),
        "waiting_time_source": dataset_summary.get("waiting_time_source"),
        "load_history_source": dataset_summary.get("load_history_source"),
        "predicted_next_load_method": dataset_summary.get("predicted_next_load_method"),
        "paper_lstm_forecast": dataset_summary.get("paper_lstm_forecast"),
        "state_dim": dataset_summary.get("state_dim"),
        "action_count": dataset_summary.get("action_count"),
        "transitions": dataset_summary.get("transitions", len(transitions)),
        "unavailable_fields": dataset_summary.get("unavailable_fields", []),
        "approximation_warnings": dataset_summary.get("approximation_warnings", []),
        "replay_dataset_summary": dataset_summary,
        "episode_metrics_count": len(trace_rows.get("episode_metrics.csv", [])),
        "state_lstm_summary": state_summary,
        "paper_performance_claims_made": False,
    }
    readiness = assess_readiness(report)
    report.update(readiness)
    report["validation_status"] = "FAILED" if report["blockers"] else ("PASSED_WITH_WARNINGS" if report["warnings"] else "PASSED")
    report["artifact_paths"] = {
        "validation_config": str(output_dir / "validation_config.json"),
        "phase4_validation_report": str(output_dir / "phase4_validation_report.json"),
        "phase4_validation_report_md": str(output_dir / "phase4_validation_report.md"),
        "episode_metrics_summary": str(output_dir / "episode_metrics_summary.csv"),
        "policy_action_summary": str(output_dir / "policy_action_summary.csv"),
        "state_lstm_summary": str(output_dir / "state_lstm_summary.json"),
        "readiness_matrix": str(output_dir / "readiness_matrix.csv"),
    }
    return report, episode_summary_rows


def _write_outputs(output_dir: Path, config: ValidationConfig, report: dict[str, Any], episode_summary_rows: list[dict[str, Any]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    config_path = output_dir / "validation_config.json"
    config_path.write_text(json.dumps(asdict(config), indent=2, sort_keys=True))
    (output_dir / "phase4_validation_report.json").write_text(json.dumps(report, indent=2, sort_keys=True))
    blockers_lines = [f"- {item}" for item in report.get("blockers", [])]
    warnings_lines = [f"- {item}" for item in report.get("warnings", [])]
    md = [
        "# Phase 4 200-Episode Validation",
        "",
        "## Scope",
        "Validation-only pipeline. No runtime behavior was modified.",
        "",
        "## Readiness",
        f"- ready_for_phase5_figures: {report['ready_for_phase5_figures']}",
        f"- validation_status: {report['validation_status']}",
        "",
        "## Blockers",
        *(blockers_lines if blockers_lines else ["- none"]),
        "",
        "## Warnings",
        *(warnings_lines if warnings_lines else ["- none"]),
        "",
        "## Next Step",
        report.get("next_required_phase", "Phase 5 figure generation only after readiness is true."),
    ]
    (output_dir / "phase4_validation_report.md").write_text("\n".join(md))
    _write_csv(output_dir / "episode_metrics_summary.csv", episode_summary_rows)
    action_summary_rows = [
        {"metric": key, "value": json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else value}
        for key, value in report.items()
        if key in {
            "total_actions",
            "valid_actions",
            "invalid_actions",
            "invalid_action_ratio",
            "local_action_count",
            "horizontal_action_count",
            "vertical_cloud_action_count",
            "missing_selected_action_count",
            "non_neighbor_offload_count",
            "self_offload_violation_count",
        }
    ]
    _write_csv(output_dir / "policy_action_summary.csv", action_summary_rows)
    (output_dir / "state_lstm_summary.json").write_text(json.dumps(report["state_lstm_summary"], indent=2, sort_keys=True))
    readiness_rows = []
    for item in report["criteria"]:
        readiness_rows.append(
            {
                "criterion": item["criterion"],
                "expected": item["expected"],
                "observed": item["observed"],
                "status": item["status"],
                "evidence": item["evidence"],
                "next_action": item["next_action"],
            }
        )
    _write_csv(output_dir / "readiness_matrix.csv", readiness_rows)


def run_validation(config: ValidationConfig) -> dict[str, Any]:
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    trace_dir = Path(config.raw_trace_dir) if config.raw_trace_dir else Path(tempfile.mkdtemp(prefix="phase4-validation-traces-"))
    trace_dir.mkdir(parents=True, exist_ok=True)

    main_cmd = [
        str(PYTHON),
        "main.py",
        "--epochs",
        str(config.episodes),
        "--log_folder",
        str(output_dir / "logs"),
        "--trace_output_dir",
        str(trace_dir),
        "--validate",
        "True",
    ]
    sim = subprocess.run(main_cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    if sim.returncode != 0:
        raise SystemExit(sim.stderr or sim.stdout or "simulation failed")

    if config.train_after_run:
        train_cmd = [
            str(PYTHON),
            "-m",
            "training.train_phase3",
            "--trace-dir",
            str(trace_dir),
            "--output-dir",
            str(output_dir),
            "--epochs",
            "1",
            "--batch-size",
            str(config.batch_size),
            "--checkpoint-every",
            str(config.checkpoint_every),
            "--sequence-length",
            str(config.sequence_length),
            "--seed",
            str(config.seed),
        ]
        train = subprocess.run(train_cmd, cwd=ROOT, capture_output=True, text=True, check=False)
        if train.returncode != 0:
            raise SystemExit(train.stderr or train.stdout or "training smoke failed")

    report, episode_summary_rows = _build_report(trace_dir, output_dir, config)

    if config.keep_raw_traces and config.raw_trace_dir:
        kept_dir = output_dir / "raw_traces"
        kept_dir.mkdir(parents=True, exist_ok=True)
        for path in trace_dir.iterdir():
            if path.is_file():
                shutil.copy2(path, kept_dir / path.name)

    _write_outputs(output_dir, config, report, episode_summary_rows)
    return report


def _detect_branch() -> str | None:
    try:
        result = subprocess.run(["git", "branch", "--show-current"], cwd=ROOT, capture_output=True, text=True, check=False)
        branch = result.stdout.strip()
        return branch or None
    except Exception:
        return None


def _detect_commit() -> str | None:
    try:
        result = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False)
        commit = result.stdout.strip()
        return commit or None
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=200)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--mode", choices=["smoke", "full"], default="full")
    parser.add_argument("--raw-trace-dir", default=None)
    parser.add_argument("--keep-raw-traces", action="store_true")
    parser.add_argument("--train-after-run", action="store_true")
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--checkpoint-every", type=int, default=1)
    parser.add_argument("--sequence-length", type=int, default=1)
    parser.add_argument("--max-sample-rows", type=int, default=25)
    parser.add_argument("--fail-on-missing-paper-state", action="store_true")
    parser.add_argument("--fail-on-invalid-actions", action="store_true")
    parser.add_argument("--fail-on-non-lstm-forecast", action="store_true")
    args = parser.parse_args()

    config = ValidationConfig(
        episodes=args.episodes,
        output_dir=args.output_dir,
        seed=args.seed,
        mode=args.mode,
        raw_trace_dir=args.raw_trace_dir,
        keep_raw_traces=bool(args.keep_raw_traces),
        train_after_run=bool(args.train_after_run or args.mode == "full"),
        batch_size=args.batch_size,
        checkpoint_every=args.checkpoint_every,
        sequence_length=args.sequence_length,
        max_sample_rows=args.max_sample_rows,
        fail_on_missing_paper_state=bool(args.fail_on_missing_paper_state),
        fail_on_invalid_actions=bool(args.fail_on_invalid_actions),
        fail_on_non_lstm_forecast=bool(args.fail_on_non_lstm_forecast),
        timestamp=datetime.now(timezone.utc).isoformat(),
        branch=_detect_branch(),
        commit=_detect_commit(),
    )
    report = run_validation(config)
    if report["validation_status"] == "FAILED":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
