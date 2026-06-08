from __future__ import annotations

import argparse
import csv
import hashlib
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

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

from decision_makers import Agent, AllHorizontal, AllLocal, AllVertical, BalancedCyclicOffloader, MinimumLatencyEstimationOffloader, Random
from decision_makers.baselines import official_policy_map
from paper_contract import build_paper_table4_contract, validate_hyperparameters_against_contract
from phase2_mechanisms import build_validation_report, load_trace_csv


ROOT = Path(__file__).resolve().parent
PYTHON = ROOT / ".venvmac" / "bin" / "python"
OFFICIAL_POLICY_CLASSES = {
    "HOODIE": Agent,
    "RO": Random,
    "FLC": AllLocal,
    "VO": AllVertical,
    "HO": AllHorizontal,
    "BCO": BalancedCyclicOffloader,
    "MLEO": MinimumLatencyEstimationOffloader,
}
EXPECTED_POLICY_SET = ["HOODIE", "RO", "FLC", "VO", "HO", "BCO", "MLEO"]
REGIME_IDS = ("delay", "drop_ratio")


@dataclass(frozen=True)
class Figure10ValidationConfig:
    output_dir: str
    episodes: int
    seed: int
    policies: list[str]
    paper_contract_file: str
    hyperparameters_file: str
    config_file: str | None
    hoodie_checkpoint_dir: str | None
    test_mode: bool
    run_id: str
    timestamp: str
    branch: str | None
    commit: str | None


def _safe_float(value: Any) -> float | None:
    if value in (None, "", "None"):
        return None
    try:
        return float(value)
    except Exception:
        return None


def _safe_int(value: Any) -> int | None:
    if value in (None, "", "None"):
        return None
    try:
        return int(float(value))
    except Exception:
        return None


def _load_yaml_config(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"config file not found: {path}")
    if yaml is not None:
        data = yaml.safe_load(config_path.read_text()) or {}
        if not isinstance(data, dict):
            raise ValueError("config file must contain a mapping")
        return data
    data: dict[str, Any] = {}
    for raw_line in config_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError("config file must use key: value entries")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def _write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if yaml is not None:
        path.write_text(yaml.safe_dump(data, sort_keys=False))
        return
    lines: list[str] = []
    for key, value in data.items():
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        elif isinstance(value, (int, float)):
            rendered = str(value)
        elif isinstance(value, (list, dict)):
            rendered = json.dumps(value)
        else:
            rendered = str(value)
        lines.append(f"{key}: {rendered}")
    path.write_text("\n".join(lines) + "\n")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _log(message: str) -> None:
    print(message, flush=True)


def _detect_branch() -> str | None:
    try:
        result = subprocess.run(["git", "branch", "--show-current"], cwd=ROOT, capture_output=True, text=True, check=False)
        return result.stdout.strip() or None
    except Exception:
        return None


def _detect_commit() -> str | None:
    try:
        result = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False)
        return result.stdout.strip() or None
    except Exception:
        return None


def _load_contract(path: str | Path) -> dict[str, Any]:
    contract_path = Path(path)
    if not contract_path.exists():
        raise FileNotFoundError(f"paper contract not found: {path}")
    return json.loads(contract_path.read_text())


def _normalize_policy_list(policies: list[str] | None) -> list[str]:
    if policies:
        return list(policies)
    return list(EXPECTED_POLICY_SET)


def _policy_class_name(policy_name: str) -> str:
    cls = OFFICIAL_POLICY_CLASSES[policy_name]
    return cls.__name__ if cls is not None else "Unavailable"


def _validate_parameter_contract(runtime_hyperparameters: dict[str, Any], contract: dict[str, Any]) -> list[dict[str, Any]]:
    diagnostics: list[dict[str, Any]] = []
    if runtime_hyperparameters.get("number_of_servers") != contract.get("number_of_eas"):
        diagnostics.append(
            {
                "parameter": "number_of_eas",
                "paper_value": contract.get("number_of_eas"),
                "runtime_value": runtime_hyperparameters.get("number_of_servers"),
                "unit": "count",
                "conversion_formula": "direct",
                "severity": "high",
            }
        )
    if runtime_hyperparameters.get("task_arrive_probabilities", [None])[0] != contract.get("task_arrival_probability"):
        diagnostics.append(
            {
                "parameter": "task_arrival_probability",
                "paper_value": contract.get("task_arrival_probability"),
                "runtime_value": runtime_hyperparameters.get("task_arrive_probabilities", [None])[0],
                "unit": "probability",
                "conversion_formula": "direct",
                "severity": "medium",
            }
        )
    if runtime_hyperparameters.get("task_size_mins", [None])[0] != contract.get("task_sizes_mbits", [None])[0]:
        diagnostics.append(
            {
                "parameter": "task_size_min",
                "paper_value": contract.get("task_sizes_mbits", [None])[0],
                "runtime_value": runtime_hyperparameters.get("task_size_mins", [None])[0],
                "unit": "Mbits",
                "conversion_formula": "direct",
                "severity": "medium",
            }
        )
    if runtime_hyperparameters.get("task_size_maxs", [None])[0] != contract.get("task_sizes_mbits", [None])[-1]:
        diagnostics.append(
            {
                "parameter": "task_size_max",
                "paper_value": contract.get("task_sizes_mbits", [None])[-1],
                "runtime_value": runtime_hyperparameters.get("task_size_maxs", [None])[0],
                "unit": "Mbits",
                "conversion_formula": "direct",
                "severity": "medium",
            }
        )
    if runtime_hyperparameters.get("timeout_delay_mins", [None])[0] != contract.get("timeout_slots"):
        diagnostics.append(
            {
                "parameter": "timeout_slots",
                "paper_value": contract.get("timeout_slots"),
                "runtime_value": runtime_hyperparameters.get("timeout_delay_mins", [None])[0],
                "unit": "slots",
                "conversion_formula": "timeout_sec / delta_sec",
                "severity": "high",
            }
        )
    if runtime_hyperparameters.get("cloud_computational_capacity") != contract.get("cloud_cpu_ghz"):
        diagnostics.append(
            {
                "parameter": "cloud_cpu_ghz",
                "paper_value": contract.get("cloud_cpu_ghz"),
                "runtime_value": runtime_hyperparameters.get("cloud_computational_capacity"),
                "unit": "GHz",
                "conversion_formula": "direct",
                "severity": "high",
            }
        )
    return diagnostics


def _episode_metrics_from_lifecycle(lifecycle_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in lifecycle_rows:
        grouped[str(row.get("episode_id"))].append(row)
    episode_rows: list[dict[str, Any]] = []
    for episode_id, rows in sorted(grouped.items(), key=lambda item: int(float(item[0])) if item[0] not in (None, "", "None") else -1):
        total = len(rows)
        completed = [row for row in rows if str(row.get("final_status")).lower() == "completed"]
        dropped = [row for row in rows if str(row.get("final_status")).lower() in {"dropped", "timeout", "timed_out"}]
        pending = [row for row in rows if str(row.get("final_status")).lower() == "pending"]
        delays = []
        waiting_times = []
        service_times = []
        for row in completed:
            delay = _safe_float(row.get("latency"))
            if delay is None:
                arrival = _safe_int(row.get("arrival_time"))
                completion = _safe_int(row.get("completion_time"))
                if arrival is not None and completion is not None:
                    delay = float(completion - arrival)
            if delay is not None:
                delays.append(delay)
            waiting = _safe_float(row.get("waiting_time"))
            if waiting is not None:
                waiting_times.append(waiting)
            service = _safe_float(row.get("service_time"))
            if service is not None:
                service_times.append(service)
        total_reward = sum(_safe_float(row.get("reward_received")) or 0.0 for row in rows)
        episode_rows.append(
            {
                "episode_id": int(float(episode_id)) if episode_id not in (None, "", "None") else None,
                "total_tasks": total,
                "completed_tasks": len(completed),
                "dropped_tasks": len(dropped),
                "pending_tasks": len(pending),
                "average_computation_delay": float(np.mean(delays)) if delays else None,
                "drop_ratio": (len(dropped) / total) if total else 0.0,
                "mean_reward": (total_reward / total) if total else 0.0,
                "total_reward": total_reward,
                "average_waiting_time": float(np.mean(waiting_times)) if waiting_times else None,
                "average_service_time": float(np.mean(service_times)) if service_times else None,
            }
        )
    return episode_rows


def _build_notes_json(
    *,
    regime_id: str,
    regime_source: str,
    timeout_slots: int | None,
    timeout_sec: float | None,
    pending_tasks: int,
    contract_diagnostics: list[dict[str, Any]],
    mleo_contract_status: str | None,
    delayed_reward_contract_status: str | None,
    policy_readiness_status: str,
) -> str:
    return json.dumps(
        {
            "regime_id": regime_id,
            "regime_source": regime_source,
            "average_computation_delay_denominator": "completed_tasks only",
            "drop_ratio_denominator": "dropped_tasks / total_tasks",
            "pending_tasks_visible": pending_tasks > 0,
            "timeout_slots": timeout_slots,
            "timeout_sec": timeout_sec,
            "contract_diagnostics": contract_diagnostics,
            "mleo_contract_status": mleo_contract_status,
            "delayed_reward_contract_status": delayed_reward_contract_status,
            "policy_readiness_status": policy_readiness_status,
        },
        sort_keys=True,
    )


def _prepare_runtime_hyperparameters(base_hyperparameters: dict[str, Any], policy_name: str, *, regime_id: str, contract: dict[str, Any], validation_episodes: int, test_mode: bool) -> dict[str, Any]:
    runtime = json.loads(json.dumps(base_hyperparameters))
    runtime["decision_makers"] = policy_name
    runtime["episodes"] = validation_episodes
    runtime["validate"] = True
    runtime["validation_regime_id"] = regime_id
    runtime["paper_contract_source"] = contract.get("source")
    if test_mode:
        runtime["validation_test_mode"] = True
    return runtime


def _run_main_for_policy(run_dir: Path, runtime_hyperparameters: dict[str, Any], episodes: int, seed: int, trace_dir: Path) -> subprocess.CompletedProcess[str]:
    run_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = run_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    runtime_hyperparameters_path = run_dir / "hyperparameters.json"
    runtime_hyperparameters_path.write_text(json.dumps(runtime_hyperparameters, indent=2, sort_keys=True))
    config_path = run_dir / "config.yml"
    _write_yaml(
        config_path,
        {
            "hyperparameters_file": str(runtime_hyperparameters_path),
            "log_folder": str(logs_dir),
            "trace_output_dir": str(trace_dir),
            "epochs": episodes,
            "validate": True,
            "episode_log_interval": 10,
        },
    )
    cmd = [str(PYTHON), "main.py", "--config", str(config_path), "--epochs", str(episodes), "--seed", str(seed)]
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    (run_dir / "main_stdout.txt").write_text(result.stdout or "")
    (run_dir / "main_stderr.txt").write_text(result.stderr or "")
    (run_dir / "main_returncode.txt").write_text(str(result.returncode))
    return result


def _copy_hoodie_checkpoints(hoodie_checkpoint_dir: Path, log_dir: Path, number_of_servers: int) -> tuple[bool, list[str]]:
    missing: list[str] = []
    for idx in range(number_of_servers):
        src = hoodie_checkpoint_dir / f"agent_{idx}.pth"
        dst = log_dir / f"agent_{idx}.pth"
        if not src.exists():
            missing.append(str(src))
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return (len(missing) == 0, missing)


def _policy_run_summary(
    *,
    policy_name: str,
    regime_id: str,
    run_id: str,
    trace_dir: Path | None,
    trace_report: dict[str, Any] | None = None,
    lifecycle_rows: list[dict[str, Any]] | None = None,
    trace_episode_rows: list[dict[str, Any]] | None = None,
    validation_episodes: int,
    timeout_slots: int | None,
    timeout_sec: float | None,
    config_hash: str,
    hoodie_checkpoint_status: str,
    contract_diagnostics: list[dict[str, Any]],
    test_mode: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    if trace_dir is None or not trace_dir.exists():
        summary = {
            "episodes_requested": validation_episodes,
            "episodes_completed": 0,
            "total_tasks": 0,
            "completed_tasks": 0,
            "dropped_tasks": 0,
            "pending_tasks": 0,
            "mean_average_computation_delay": None,
            "std_average_computation_delay": None,
            "mean_drop_ratio": None,
            "std_drop_ratio": None,
            "policy_readiness_status": "unavailable_not_trained" if policy_name == "HOODIE" else "run_failed",
            "warnings": ["trace directory missing"],
        }
        return [], summary, {
            "policy_name": policy_name,
            "policy_class": _policy_class_name(policy_name),
            "policy_readiness_status": summary["policy_readiness_status"],
            "mleo_contract_status": "missing",
            "delayed_reward_contract_status": "missing",
            "hoodie_checkpoint_status": hoodie_checkpoint_status,
            "notes_json": _build_notes_json(
                regime_id=regime_id,
                regime_source="paper_contract_or_unverified_runtime_override",
                timeout_slots=timeout_slots,
                timeout_sec=timeout_sec,
                pending_tasks=0,
                contract_diagnostics=contract_diagnostics,
                mleo_contract_status="missing",
                delayed_reward_contract_status="missing",
                policy_readiness_status=summary["policy_readiness_status"],
            ),
        }

    trace_report = trace_report or build_validation_report(trace_dir)
    lifecycle_rows = lifecycle_rows if lifecycle_rows is not None else load_trace_csv(trace_dir / "task_lifecycle.csv")
    episode_metrics_rows = _episode_metrics_from_lifecycle(lifecycle_rows)
    trace_episode_rows = trace_episode_rows if trace_episode_rows is not None else load_trace_csv(trace_dir / "episode_metrics.csv")
    raw_rows: list[dict[str, Any]] = []
    policy_readiness_status = "ready"
    if policy_name == "HOODIE" and hoodie_checkpoint_status == "unavailable_not_trained":
        policy_readiness_status = "unavailable_not_trained"
    elif trace_report.get("mleo_contract_status") != "paper_candidate_trace_ready" and policy_name == "MLEO":
        policy_readiness_status = "invalid_mleo_trace"
    elif trace_report.get("delayed_reward_contract_status") != "paper_replay_pairing_ready":
        policy_readiness_status = "invalid_delayed_reward_trace"
    elif contract_diagnostics:
        policy_readiness_status = "invalid_parameter_contract"
    elif not trace_episode_rows:
        policy_readiness_status = "run_failed"

    for episode_row in episode_metrics_rows:
        notes_json = _build_notes_json(
            regime_id=regime_id,
            regime_source="paper_contract_or_unverified_runtime_override",
            timeout_slots=timeout_slots,
            timeout_sec=timeout_sec,
            pending_tasks=int(episode_row.get("pending_tasks") or 0),
            contract_diagnostics=contract_diagnostics,
            mleo_contract_status=trace_report.get("mleo_contract_status"),
            delayed_reward_contract_status=trace_report.get("delayed_reward_contract_status"),
            policy_readiness_status=policy_readiness_status,
        )
        raw_rows.append(
            {
                "run_id": run_id,
                "regime_id": regime_id,
                "policy_name": policy_name,
                "policy_class": _policy_class_name(policy_name),
                "episode_id": episode_row.get("episode_id"),
                "validation_episode_count": validation_episodes,
                "task_count": episode_row.get("total_tasks"),
                "completed_tasks": episode_row.get("completed_tasks"),
                "dropped_tasks": episode_row.get("dropped_tasks"),
                "pending_tasks": episode_row.get("pending_tasks"),
                "average_computation_delay": episode_row.get("average_computation_delay"),
                "drop_ratio": episode_row.get("drop_ratio"),
                "mean_reward": episode_row.get("mean_reward"),
                "total_reward": episode_row.get("total_reward"),
                "mleo_contract_status": trace_report.get("mleo_contract_status"),
                "delayed_reward_contract_status": trace_report.get("delayed_reward_contract_status"),
                "policy_readiness_status": policy_readiness_status,
                "hoodie_checkpoint_status": hoodie_checkpoint_status,
                "config_hash": config_hash,
                "trace_dir": str(trace_dir),
                "notes_json": notes_json,
            }
        )

    avg_delays = [row["average_computation_delay"] for row in episode_metrics_rows if row["average_computation_delay"] is not None]
    drop_ratios = [row["drop_ratio"] for row in episode_metrics_rows if row["drop_ratio"] is not None]
    summary = {
        "episodes_requested": validation_episodes,
        "episodes_completed": len(trace_episode_rows),
        "total_tasks": sum(row["total_tasks"] for row in episode_metrics_rows),
        "completed_tasks": sum(row["completed_tasks"] for row in episode_metrics_rows),
        "dropped_tasks": sum(row["dropped_tasks"] for row in episode_metrics_rows),
        "pending_tasks": sum(row["pending_tasks"] for row in episode_metrics_rows),
        "mean_average_computation_delay": float(np.mean(avg_delays)) if avg_delays else None,
        "std_average_computation_delay": float(np.std(avg_delays)) if len(avg_delays) > 1 else 0.0 if avg_delays else None,
        "mean_drop_ratio": float(np.mean(drop_ratios)) if drop_ratios else None,
        "std_drop_ratio": float(np.std(drop_ratios)) if len(drop_ratios) > 1 else 0.0 if drop_ratios else None,
        "policy_readiness_status": policy_readiness_status,
        "warnings": [
            *([f"contract diagnostics: {contract_diagnostics}"] if contract_diagnostics else []),
            *([f"mleo_contract_status={trace_report.get('mleo_contract_status')}"] if policy_name == "MLEO" else []),
            *([f"delayed_reward_contract_status={trace_report.get('delayed_reward_contract_status')}"] if trace_report.get("delayed_reward_contract_status") else []),
        ],
        "mleo_contract_status": trace_report.get("mleo_contract_status"),
        "delayed_reward_contract_status": trace_report.get("delayed_reward_contract_status"),
        "hoodie_checkpoint_status": hoodie_checkpoint_status,
        "regime_source": "paper_contract_or_unverified_runtime_override",
        "trace_report": trace_report,
    }
    if policy_name == "HOODIE" and hoodie_checkpoint_status == "unavailable_not_trained":
        summary["warnings"].append("HOODIE checkpoint unavailable; policy skipped")
    return raw_rows, summary, {
        "policy_name": policy_name,
        "policy_class": _policy_class_name(policy_name),
        "policy_readiness_status": policy_readiness_status,
        "mleo_contract_status": trace_report.get("mleo_contract_status"),
        "delayed_reward_contract_status": trace_report.get("delayed_reward_contract_status"),
        "hoodie_checkpoint_status": hoodie_checkpoint_status,
        "trace_dir": str(trace_dir),
        "notes_json": raw_rows[0]["notes_json"] if raw_rows else _build_notes_json(
            regime_id=regime_id,
            regime_source="paper_contract_or_unverified_runtime_override",
            timeout_slots=None,
            timeout_sec=None,
            pending_tasks=0,
            contract_diagnostics=contract_diagnostics,
            mleo_contract_status=trace_report.get("mleo_contract_status"),
            delayed_reward_contract_status=trace_report.get("delayed_reward_contract_status"),
            policy_readiness_status=policy_readiness_status,
        ),
    }


def assess_figure10_readiness(summary: dict[str, Any]) -> dict[str, Any]:
    active_policy_set = summary.get("active_policy_set", [])
    expected_policy_set = summary.get("expected_policy_set", EXPECTED_POLICY_SET)
    baseline_policy_set = summary.get("baseline_policy_set", [policy for policy in EXPECTED_POLICY_SET if policy != "HOODIE"])
    missing_policies = summary.get("missing_policies", [])
    unexpected_policies = summary.get("unexpected_policies", [])
    baseline_missing_policies = [policy for policy in baseline_policy_set if policy not in active_policy_set]
    baseline_unexpected_policies = [
        policy for policy in active_policy_set if policy not in baseline_policy_set and policy != "HOODIE"
    ]
    policy_class_map = summary.get("policy_class_map", {})
    hoodie_checkpoint_status = summary.get("hoodie_checkpoint_status", "unavailable_not_trained")
    mleo_contract_status_seen = summary.get("mleo_contract_status_seen", {})
    delayed_reward_contract_status_seen = summary.get("delayed_reward_contract_status_seen", {})
    validation_episode_count = summary.get("validation_episode_count")
    mleo_contract_status_ready = bool(mleo_contract_status_seen) and all(
        status == "paper_candidate_trace_ready" for status in mleo_contract_status_seen
    )
    delayed_reward_contract_status_ready = bool(delayed_reward_contract_status_seen) and all(
        status == "paper_replay_pairing_ready" for status in delayed_reward_contract_status_seen
    )
    baseline_validation_ready = (
        not baseline_missing_policies
        and not baseline_unexpected_policies
        and summary.get("non_hoodie_baselines_ready", False)
        and mleo_contract_status_ready
        and delayed_reward_contract_status_ready
        and (summary.get("validation_episode_count") == 200 or summary.get("test_mode", False))
        and summary.get("paper_performance_claims_made", False) is False
        and not summary.get("no_metric_rows_generated", False)
    )
    figure10_data_ready = (
        baseline_validation_ready
        and hoodie_checkpoint_status == "present_and_loaded"
        and not missing_policies
        and not unexpected_policies
        and summary.get("validation_episode_count") == 200
        and summary.get("paper_performance_claims_made", False) is False
    )
    blocking_reasons = []
    if missing_policies:
        blocking_reasons.append(f"missing_policies={missing_policies}")
    if unexpected_policies:
        blocking_reasons.append(f"unexpected_policies={unexpected_policies}")
    if baseline_missing_policies:
        blocking_reasons.append(f"baseline_missing_policies={baseline_missing_policies}")
    if baseline_unexpected_policies:
        blocking_reasons.append(f"baseline_unexpected_policies={baseline_unexpected_policies}")
    if not summary.get("non_hoodie_baselines_ready", False):
        blocking_reasons.append("non_hoodie_baselines_ready=false")
    if not mleo_contract_status_ready:
        blocking_reasons.append("mleo_contract_status_ready=false")
    if not delayed_reward_contract_status_ready:
        blocking_reasons.append("delayed_reward_contract_status_ready=false")
    if summary.get("no_metric_rows_generated", False):
        blocking_reasons.append("no_metric_rows_generated")
    if hoodie_checkpoint_status != "present_and_loaded":
        blocking_reasons.append(f"hoodie_checkpoint_status={hoodie_checkpoint_status}")
    if summary.get("validation_episode_count") != 200 and not summary.get("test_mode", False):
        blocking_reasons.append(f"validation_episode_count={summary.get('validation_episode_count')}")
    if summary.get("paper_performance_claims_made", False):
        blocking_reasons.append("paper_performance_claims_made=true")
    return {
        "active_policy_set": active_policy_set,
        "expected_policy_set": expected_policy_set,
        "baseline_policy_set": baseline_policy_set,
        "missing_policies": missing_policies,
        "unexpected_policies": unexpected_policies,
        "baseline_missing_policies": baseline_missing_policies,
        "baseline_unexpected_policies": baseline_unexpected_policies,
        "policy_class_map": policy_class_map,
        "hoodie_checkpoint_status": hoodie_checkpoint_status,
        "mleo_required": True,
        "mleo_contract_status_seen": mleo_contract_status_seen,
        "delayed_reward_contract_status_seen": delayed_reward_contract_status_seen,
        "validation_episode_count": validation_episode_count,
        "figure10_data_ready": figure10_data_ready,
        "baseline_validation_ready": baseline_validation_ready,
        "blocking_reasons": blocking_reasons,
    }


def run_figure10_validation(config: Figure10ValidationConfig) -> dict[str, Any]:
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    contract = _load_contract(config.paper_contract_file)
    runtime_hyperparameters = json.loads(Path(config.hyperparameters_file).read_text())
    runtime_diagnostics = _validate_parameter_contract(runtime_hyperparameters, contract)
    _log("=== Figure 10 Validation ===")
    _log(f"  - run_id: {config.run_id}")
    _log(f"  - output_dir: {output_dir}")
    _log(f"  - episodes: {config.episodes}")
    _log(f"  - seed: {config.seed}")
    _log(f"  - policies: {config.policies}")
    _log(f"  - test_mode: {config.test_mode}")
    if runtime_diagnostics and not config.test_mode:
        _log("=== 1. Paper Contract Diagnostics ===")
        for diag in runtime_diagnostics:
            _log(f"  - {diag['parameter']}: paper={diag['paper_value']} runtime={diag['runtime_value']} severity={diag['severity']}")
    elif runtime_diagnostics and config.test_mode:
        _log("=== 1. Paper Contract Diagnostics (test mode) ===")
        for diag in runtime_diagnostics:
            _log(f"  - {diag['parameter']}: paper={diag['paper_value']} runtime={diag['runtime_value']} severity={diag['severity']}")
    else:
        _log("=== 1. Paper Contract Diagnostics ===")
        _log("  - no parameter mismatches detected")

    run_id = config.run_id
    run_root = output_dir / "runs" / run_id
    run_root.mkdir(parents=True, exist_ok=True)

    raw_rows: list[dict[str, Any]] = []
    policy_summaries: dict[str, dict[str, Any]] = {}
    policy_details: dict[str, dict[str, Any]] = {}
    policy_class_map = {policy: _policy_class_name(policy) for policy in config.policies}
    active_policy_set = list(config.policies)
    expected_policy_set = list(EXPECTED_POLICY_SET)
    missing_policies = [policy for policy in EXPECTED_POLICY_SET if policy not in config.policies]
    unexpected_policies = [policy for policy in config.policies if policy not in EXPECTED_POLICY_SET]
    policy_run_statuses: dict[str, str] = {}
    hoodie_checkpoint_status = "unavailable_not_trained"
    hoodie_loaded = False
    mleo_contract_status_seen: Counter[str] = Counter()
    delayed_reward_contract_status_seen: Counter[str] = Counter()

    for regime_id in REGIME_IDS:
        _log(f"=== 2. Regime Start: {regime_id} ===")
        for policy_name in config.policies:
            policy_class = OFFICIAL_POLICY_CLASSES.get(policy_name)
            if policy_class is None:
                policy_run_statuses[policy_name] = "invalid_policy_mapping"
                _log(f"  - policy={policy_name}: invalid mapping, skipping")
                continue
            if policy_name == "HOODIE":
                checkpoint_dir = Path(config.hoodie_checkpoint_dir) if config.hoodie_checkpoint_dir else None
                if checkpoint_dir is None or not checkpoint_dir.exists():
                    policy_run_statuses[policy_name] = "unavailable_not_trained"
                    hoodie_checkpoint_status = "unavailable_not_trained"
                    _log(f"  - regime={regime_id} policy={policy_name}: checkpoint unavailable, skipping")
                    policy_details[policy_name] = {
                        "policy_name": policy_name,
                        "policy_class": _policy_class_name(policy_name),
                        "policy_readiness_status": "unavailable_not_trained",
                        "mleo_contract_status": "missing",
                        "delayed_reward_contract_status": "missing",
                        "hoodie_checkpoint_status": "unavailable_not_trained",
                        "trace_dir": None,
                        "notes_json": _build_notes_json(
                            regime_id=regime_id,
                            regime_source="paper_contract_or_unverified_runtime_override",
                            timeout_slots=contract.get("timeout_slots"),
                            timeout_sec=contract.get("timeout_sec"),
                            pending_tasks=0,
                            contract_diagnostics=runtime_diagnostics,
                            mleo_contract_status="missing",
                            delayed_reward_contract_status="missing",
                            policy_readiness_status="unavailable_not_trained",
                        ),
                    }
                    continue
                hoodie_loaded = True
                _log(f"  - regime={regime_id} policy={policy_name}: checkpoint found, preparing run")

            regime_run_dir = run_root / regime_id / policy_name
            trace_dir = regime_run_dir / "traces"
            regime_run_dir.mkdir(parents=True, exist_ok=True)
            _log(f"  - regime={regime_id} policy={policy_name}: writing runtime config to {regime_run_dir}")

            runtime_hp = _prepare_runtime_hyperparameters(
                runtime_hyperparameters,
                policy_name,
                regime_id=regime_id,
                contract=contract,
                validation_episodes=config.episodes,
                test_mode=config.test_mode,
            )
            runtime_hp["decision_makers"] = policy_name
            runtime_hp_path = regime_run_dir / "hyperparameters.json"
            runtime_hp_path.write_text(json.dumps(runtime_hp, indent=2, sort_keys=True))
            config_path = regime_run_dir / "config.yml"
            _write_yaml(
                config_path,
                {
                    "hyperparameters_file": str(runtime_hp_path),
                    "log_folder": str(regime_run_dir / "logs"),
                    "trace_output_dir": str(trace_dir),
                    "epochs": config.episodes,
                    "validate": True,
                    "episode_log_interval": 10,
                    "step_log_interval": 10,
                },
            )
            _log(f"  - regime={regime_id} policy={policy_name}: launching main.py for {config.episodes} episodes")

            if policy_name == "HOODIE" and config.hoodie_checkpoint_dir:
                log_dir = regime_run_dir / "logs"
                log_dir.mkdir(parents=True, exist_ok=True)
                checkpoint_ok, missing_checkpoints = _copy_hoodie_checkpoints(Path(config.hoodie_checkpoint_dir), log_dir, int(contract.get("number_of_eas", runtime_hyperparameters.get("number_of_servers", 0))))
                if not checkpoint_ok:
                    policy_run_statuses[policy_name] = "unavailable_not_trained"
                    hoodie_checkpoint_status = "unavailable_not_trained"
                    _log(f"  - regime={regime_id} policy={policy_name}: missing checkpoints {missing_checkpoints}, skipping")
                    policy_details[policy_name] = {
                        "policy_name": policy_name,
                        "policy_class": _policy_class_name(policy_name),
                        "policy_readiness_status": "unavailable_not_trained",
                        "mleo_contract_status": "missing",
                        "delayed_reward_contract_status": "missing",
                        "hoodie_checkpoint_status": "unavailable_not_trained",
                        "trace_dir": None,
                        "notes_json": _build_notes_json(
                            regime_id=regime_id,
                            regime_source="paper_contract_or_unverified_runtime_override",
                            timeout_slots=contract.get("timeout_slots"),
                            timeout_sec=contract.get("timeout_sec"),
                            pending_tasks=0,
                            contract_diagnostics=runtime_diagnostics,
                            mleo_contract_status="missing",
                            delayed_reward_contract_status="missing",
                            policy_readiness_status="unavailable_not_trained",
                        ),
                    }
                    continue
                hoodie_checkpoint_status = "present_and_loaded"

            result = _run_main_for_policy(regime_run_dir, runtime_hp, config.episodes, config.seed, trace_dir)
            _log(f"  - regime={regime_id} policy={policy_name}: main.py return code {result.returncode}")
            if result.returncode != 0:
                policy_run_statuses[policy_name] = "run_failed"
                stderr_tail = (result.stderr or "").strip().splitlines()[-20:]
                warning = f"{policy_name}/{regime_id} subprocess failed rc={result.returncode}"
                if stderr_tail:
                    warning = f"{warning}; stderr_tail={stderr_tail}"
                _log(f"  - regime={regime_id} policy={policy_name}: failed; stderr tail captured")
                policy_details[policy_name] = {
                    "policy_name": policy_name,
                    "policy_class": _policy_class_name(policy_name),
                    "policy_readiness_status": "run_failed",
                    "mleo_contract_status": "missing",
                    "delayed_reward_contract_status": "missing",
                    "hoodie_checkpoint_status": hoodie_checkpoint_status if policy_name == "HOODIE" else "not_required",
                    "trace_dir": str(trace_dir),
                    "warnings": [warning],
                    "notes_json": _build_notes_json(
                        regime_id=regime_id,
                        regime_source="paper_contract_or_unverified_runtime_override",
                        timeout_slots=contract.get("timeout_slots"),
                        timeout_sec=contract.get("timeout_sec"),
                        pending_tasks=0,
                        contract_diagnostics=runtime_diagnostics,
                        mleo_contract_status="missing",
                        delayed_reward_contract_status="missing",
                        policy_readiness_status="run_failed",
                    ),
                }
                (regime_run_dir / "warnings.json").write_text(json.dumps([warning], indent=2))
                continue

            _log(f"  - regime={regime_id} policy={policy_name}: reading trace report")
            report = build_validation_report(trace_dir)
            policy_run_status = "ready"
            if runtime_diagnostics:
                policy_run_status = "invalid_parameter_contract"
            if policy_name == "MLEO" and report.get("mleo_contract_status") != "paper_candidate_trace_ready":
                policy_run_status = "invalid_mleo_trace"
            if report.get("delayed_reward_contract_status") != "paper_replay_pairing_ready":
                policy_run_status = "invalid_delayed_reward_trace"
            if policy_name == "HOODIE" and hoodie_checkpoint_status != "present_and_loaded":
                policy_run_status = "unavailable_not_trained"
            policy_run_statuses[policy_name] = policy_run_status
            mleo_contract_status_seen[str(report.get("mleo_contract_status"))] += 1
            delayed_reward_contract_status_seen[str(report.get("delayed_reward_contract_status"))] += 1
            lifecycle_rows = load_trace_csv(trace_dir / "task_lifecycle.csv")
            episode_rows = _episode_metrics_from_lifecycle(lifecycle_rows)
            _log(
                f"  - regime={regime_id} policy={policy_name}: lifecycle_rows={len(lifecycle_rows)} "
                f"episodes={len(episode_rows)} mleo_status={report.get('mleo_contract_status')} "
                f"delayed_reward_status={report.get('delayed_reward_contract_status')} readiness={policy_run_status}"
            )
            if not episode_rows:
                policy_run_status = "run_failed"
                policy_run_statuses[policy_name] = policy_run_status
                _log(f"  - regime={regime_id} policy={policy_name}: no episode rows generated, marking failed")
            policy_summary_rows, policy_summary, detail_row = _policy_run_summary(
                policy_name=policy_name,
                regime_id=regime_id,
                run_id=run_id,
                trace_dir=trace_dir,
                trace_report=report,
                lifecycle_rows=lifecycle_rows,
                trace_episode_rows=load_trace_csv(trace_dir / "episode_metrics.csv"),
                validation_episodes=config.episodes,
                timeout_slots=_safe_int(runtime_hp.get("timeout_delay_mins", [None])[0]),
                timeout_sec=contract.get("timeout_sec"),
                config_hash=hashlib.sha256(json.dumps({"policy": policy_name, "regime": regime_id, "runtime": runtime_hp}, sort_keys=True).encode()).hexdigest(),
                hoodie_checkpoint_status=hoodie_checkpoint_status if policy_name == "HOODIE" else "not_required",
                contract_diagnostics=runtime_diagnostics,
                test_mode=config.test_mode,
            )
            _log(
                f"  - regime={regime_id} policy={policy_name}: summary rows={len(policy_summary_rows)} "
                f"episodes_completed={policy_summary.get('episodes_completed')} "
                f"mean_delay={policy_summary.get('mean_average_computation_delay')} "
                f"mean_drop_ratio={policy_summary.get('mean_drop_ratio')}"
            )
            for row in policy_summary_rows:
                row["policy_readiness_status"] = policy_run_status
                row["hoodie_checkpoint_status"] = hoodie_checkpoint_status if policy_name == "HOODIE" else "not_required"
                row["mleo_contract_status"] = report.get("mleo_contract_status")
                row["delayed_reward_contract_status"] = report.get("delayed_reward_contract_status")
                raw_rows.append(row)
            policy_summaries.setdefault(regime_id, {})[policy_name] = policy_summary
            policy_details[policy_name] = detail_row
        _log(f"=== 2. Regime Complete: {regime_id} ===")

    policy_summary_json: dict[str, Any] = {"regimes": policy_summaries}
    if raw_rows:
        _write_csv(output_dir / "figure10_policy_metrics_raw.csv", raw_rows)
        _log(f"=== 3. Raw Metrics Written ===")
        _log(f"  - rows: {len(raw_rows)}")
    else:
        (output_dir / "figure10_policy_metrics_raw.csv").write_text("")
        _log("=== 3. Raw Metrics Written ===")
        _log("  - rows: 0")

    summary_rows: list[dict[str, Any]] = []
    for regime_id, policies in policy_summaries.items():
        for policy_name, policy_summary in policies.items():
            summary_rows.append(
                {
                    "regime_id": regime_id,
                    "policy_name": policy_name,
                    "episodes_requested": policy_summary["episodes_requested"],
                    "episodes_completed": policy_summary["episodes_completed"],
                    "total_tasks": policy_summary["total_tasks"],
                    "completed_tasks": policy_summary["completed_tasks"],
                    "dropped_tasks": policy_summary["dropped_tasks"],
                    "pending_tasks": policy_summary["pending_tasks"],
                    "mean_average_computation_delay": policy_summary["mean_average_computation_delay"],
                    "std_average_computation_delay": policy_summary["std_average_computation_delay"],
                    "mean_drop_ratio": policy_summary["mean_drop_ratio"],
                    "std_drop_ratio": policy_summary["std_drop_ratio"],
                    "policy_readiness_status": policy_summary["policy_readiness_status"],
                    "warnings": policy_summary["warnings"],
                }
            )
    policy_summary_json["summary_rows"] = summary_rows
    policy_summary_json["policy_details"] = policy_details
    policy_summary_json["runtime_parameter_diagnostics"] = runtime_diagnostics
    policy_summary_json["paper_contract_source"] = contract.get("source")
    policy_summary_json["expected_policy_set"] = EXPECTED_POLICY_SET
    policy_summary_json["active_policy_set"] = active_policy_set
    policy_summary_json["validation_episode_count"] = config.episodes

    readiness_input = {
        "active_policy_set": active_policy_set,
        "expected_policy_set": EXPECTED_POLICY_SET,
        "baseline_policy_set": [policy for policy in EXPECTED_POLICY_SET if policy != "HOODIE"],
        "missing_policies": missing_policies,
        "unexpected_policies": unexpected_policies,
        "policy_class_map": policy_class_map,
        "hoodie_checkpoint_status": hoodie_checkpoint_status,
        "mleo_required": True,
        "mleo_contract_status_seen": dict(mleo_contract_status_seen),
        "delayed_reward_contract_status_seen": dict(delayed_reward_contract_status_seen),
        "validation_episode_count": config.episodes,
        "non_hoodie_baselines_ready": all(
            policy_run_statuses.get(policy) == "ready" for policy in EXPECTED_POLICY_SET if policy != "HOODIE"
        ),
        "paper_performance_claims_made": False,
        "test_mode": config.test_mode,
        "no_metric_rows_generated": not raw_rows,
    }
    readiness = assess_figure10_readiness(readiness_input)

    figure10_policy_metrics_summary = {
        "regimes": policy_summaries,
        "summary_rows": summary_rows,
        "runtime_parameter_diagnostics": runtime_diagnostics,
        "policy_class_map": policy_class_map,
        "validation_episode_count": config.episodes,
        "paper_contract_source": contract.get("source"),
        "paper_performance_claims_made": False,
        "registry": {
            "active_policy_set": active_policy_set,
            "expected_policy_set": EXPECTED_POLICY_SET,
            "policy_run_statuses": policy_run_statuses,
        },
    }

    config_snapshot = {
        "run_id": run_id,
        "timestamp": config.timestamp,
        "branch": config.branch,
        "commit": config.commit,
        "output_dir": str(output_dir),
        "episodes": config.episodes,
        "seed": config.seed,
        "policies": config.policies,
        "paper_contract_file": config.paper_contract_file,
        "hyperparameters_file": config.hyperparameters_file,
        "config_file": config.config_file,
        "hoodie_checkpoint_dir": config.hoodie_checkpoint_dir,
        "test_mode": config.test_mode,
        "runtime_parameter_diagnostics": runtime_diagnostics,
        "expected_policy_set": EXPECTED_POLICY_SET,
        "active_policy_set": active_policy_set,
        "figure10_data_ready": readiness["figure10_data_ready"],
        "baseline_validation_ready": readiness["baseline_validation_ready"],
        "blocking_reasons": readiness["blocking_reasons"],
        "no_metric_rows_generated": not raw_rows,
    }

    manifest = {
        "run_id": run_id,
        "output_dir": str(output_dir),
        "diagnostic_only": True,
        "paper_performance_claims_made": False,
        "input_artifacts": {
            "paper_contract": config.paper_contract_file,
            "hyperparameters": config.hyperparameters_file,
        },
        "outputs": {
            "raw_csv": str(output_dir / "figure10_policy_metrics_raw.csv"),
            "summary_json": str(output_dir / "figure10_policy_metrics_summary.json"),
            "readiness_json": str(output_dir / "figure10_policy_readiness.json"),
            "config_snapshot": str(output_dir / "figure10_run_config_snapshot.json"),
            "manifest_json": str(output_dir / "figure10_validation_manifest.json"),
        },
        "policies_evaluated": [p for p in config.policies if policy_run_statuses.get(p) != "unavailable_not_trained"],
        "policies_skipped": [p for p, s in policy_run_statuses.items() if s == "unavailable_not_trained"],
        "figure10_data_ready": readiness["figure10_data_ready"],
        "baseline_validation_ready": readiness["baseline_validation_ready"],
        "blocking_reasons": readiness["blocking_reasons"],
        "no_metric_rows_generated": not raw_rows,
        "warnings": [
            *[w for policies in policy_summaries.values() for policy in policies.values() for w in policy.get("warnings", [])],
            *[w for detail in policy_details.values() for w in detail.get("warnings", [])],
        ],
    }

    (output_dir / "figure10_policy_metrics_summary.json").write_text(json.dumps(figure10_policy_metrics_summary, indent=2, sort_keys=True))
    (output_dir / "figure10_policy_readiness.json").write_text(json.dumps(readiness, indent=2, sort_keys=True))
    (output_dir / "figure10_run_config_snapshot.json").write_text(json.dumps(config_snapshot, indent=2, sort_keys=True))
    (output_dir / "figure10_validation_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    _log("=== 4. Report Files Written ===")
    _log(f"  - summary_json: {output_dir / 'figure10_policy_metrics_summary.json'}")
    _log(f"  - readiness_json: {output_dir / 'figure10_policy_readiness.json'}")
    _log(f"  - config_snapshot: {output_dir / 'figure10_run_config_snapshot.json'}")
    _log(f"  - manifest_json: {output_dir / 'figure10_validation_manifest.json'}")

    _log("=== 5. Validation Complete ===")
    _log(f"run_id: {run_id}")
    _log(f"output_dir: {output_dir}")
    _log(f"policies evaluated: {[p for p in config.policies if policy_run_statuses.get(p) != 'unavailable_not_trained']}")
    _log(f"policies skipped: {[p for p, s in policy_run_statuses.items() if s == 'unavailable_not_trained']}")
    _log(f"readiness status: {'ready' if readiness['figure10_data_ready'] else 'blocked'}")
    _log(f"blocking reasons: {readiness['blocking_reasons']}")
    return {
        "raw_rows": raw_rows,
        "summary": figure10_policy_metrics_summary,
        "readiness": readiness,
        "manifest": manifest,
        "config_snapshot": config_snapshot,
        "runtime_parameter_diagnostics": runtime_diagnostics,
    }


def _validation_outputs_present(output_dir: Path) -> bool:
    required = [
        output_dir / "figure10_policy_metrics_raw.csv",
        output_dir / "figure10_policy_metrics_summary.json",
        output_dir / "figure10_policy_readiness.json",
        output_dir / "figure10_run_config_snapshot.json",
        output_dir / "figure10_validation_manifest.json",
    ]
    return all(path.exists() for path in required)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=None)
    parser.add_argument("--hyperparameters-file", default="hyperparameters/hyperparameters.json")
    parser.add_argument("--paper-contract", default="config/paper_table4_contract.json")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--episodes", type=int, default=200)
    parser.add_argument("--policies", default="HOODIE,RO,FLC,VO,HO,BCO,MLEO")
    parser.add_argument("--hoodie-checkpoint-dir", default=None)
    parser.add_argument("--test-mode", action="store_true")
    parser.add_argument("--strict-readiness", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args(argv)

    config_overrides = _load_yaml_config(args.config)
    policies = [p.strip() for p in str(config_overrides.get("policies", args.policies)).split(",") if p.strip()]
    run_id = args.run_id or str(config_overrides.get("run_id") or f"figure10-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-seed{args.seed}")
    config = Figure10ValidationConfig(
        output_dir=str(config_overrides.get("output_dir", args.output_dir)),
        episodes=int(config_overrides.get("episodes", args.episodes)),
        seed=int(config_overrides.get("seed", args.seed)),
        policies=_normalize_policy_list(policies),
        paper_contract_file=str(config_overrides.get("paper_contract", args.paper_contract)),
        hyperparameters_file=str(config_overrides.get("hyperparameters_file", args.hyperparameters_file)),
        config_file=args.config,
        hoodie_checkpoint_dir=str(config_overrides.get("hoodie_checkpoint_dir", args.hoodie_checkpoint_dir)) if config_overrides.get("hoodie_checkpoint_dir", args.hoodie_checkpoint_dir) else None,
        test_mode=bool(config_overrides.get("test_mode", args.test_mode)),
        run_id=run_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        branch=_detect_branch(),
        commit=_detect_commit(),
    )
    result = run_figure10_validation(config)
    if not _validation_outputs_present(Path(config.output_dir)):
        return 1
    if not args.strict_readiness:
        return 0
    return 0 if result["readiness"]["figure10_data_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
