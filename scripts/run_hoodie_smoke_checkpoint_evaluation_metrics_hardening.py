from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "hoodie_mplconfig"))
os.environ.setdefault("XDG_CACHE_HOME", str(Path(tempfile.gettempdir()) / "hoodie_xdg_cache"))
os.environ.setdefault("TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD", "1")


def _resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else (ROOT / candidate)


def _repo_relative(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except Exception:
        return False


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def _run_wiring_smoke(
    *,
    output_dir: Path,
    training_epochs: int,
    training_episode_time: int,
    validation_episodes: int,
    seed: int,
    run_id: str,
    expected_agent_count: int,
    trace_level: str,
) -> subprocess.CompletedProcess[str]:
    cmd = [
        sys.executable,
        "scripts/run_hoodie_trained_checkpoint_evaluation_wiring_smoke.py",
        "--output-dir",
        str(output_dir / "wiring_smoke"),
        "--training-epochs",
        str(training_epochs),
        "--training-episode-time",
        str(training_episode_time),
        "--validation-episodes",
        str(validation_episodes),
        "--seed",
        str(seed),
        "--run-id",
        run_id,
        "--expected-agent-count",
        str(expected_agent_count),
        "--trace-level",
        trace_level,
        "--allow-trained-checkpoint-evaluation-wiring-smoke",
        "--allow-bounded-training-smoke",
        "--allow-figure10-validation-test-mode",
        "--allow-main-py-training-execution",
        "--allow-training-checkpoint-export",
    ]
    env = dict(os.environ)
    env["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"
    env["MPLCONFIGDIR"] = str(output_dir / "cache" / "mplconfig")
    env["XDG_CACHE_HOME"] = str(output_dir / "cache" / "xdg")
    return subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, check=False)


def _validate_raw_metrics(raw_path: Path, output_dir: Path) -> tuple[bool, dict[str, Any], list[str]]:
    blockers: list[str] = []
    if not raw_path.exists():
        return False, {}, ["raw_metrics_missing"]
    text = raw_path.read_text()
    if not text.strip():
        return False, {}, ["raw_metrics_empty"]
    rows = list(csv.DictReader(text.splitlines()))
    if not rows:
        return False, {}, ["raw_metrics_empty"]
    required_columns = {
        "run_id",
        "regime_id",
        "policy_name",
        "policy_class",
        "episode_id",
        "validation_episode_count",
        "task_count",
        "completed_tasks",
        "dropped_tasks",
        "pending_tasks",
        "average_computation_delay",
        "drop_ratio",
        "mean_reward",
        "total_reward",
        "mleo_contract_status",
        "delayed_reward_contract_status",
        "policy_readiness_status",
        "hoodie_checkpoint_status",
        "config_hash",
        "trace_dir",
        "notes_json",
    }
    if not required_columns.issubset(rows[0].keys()):
        blockers.append("raw_metrics_schema_missing_columns")
        return False, {"rows": rows}, blockers
    policy_set = sorted({row["policy_name"] for row in rows})
    regime_set = sorted({row["regime_id"] for row in rows})
    if policy_set != ["HOODIE"]:
        blockers.append("raw_metrics_unexpected_policy_set")
    if regime_set != ["delay", "drop_ratio"]:
        blockers.append("raw_metrics_unexpected_regime_set")
    if any(int(row["validation_episode_count"]) != 1 for row in rows):
        blockers.append("raw_metrics_unexpected_validation_episode_count")
    if any(int(row["episode_id"]) < 0 for row in rows):
        blockers.append("raw_metrics_invalid_episode_id")
    if any(int(row["task_count"]) < 0 for row in rows):
        blockers.append("raw_metrics_invalid_task_count")
    for row in rows:
        task_count = int(row["task_count"])
        completed = int(row["completed_tasks"])
        dropped = int(row["dropped_tasks"])
        pending = int(row["pending_tasks"])
        if completed + dropped + pending != task_count:
            blockers.append("raw_metrics_task_count_inconsistent")
            break
        drop_ratio = float(row["drop_ratio"])
        if drop_ratio < 0.0 or drop_ratio > 1.0:
            blockers.append("raw_metrics_invalid_drop_ratio")
        if row["average_computation_delay"] not in ("", "None", None):
            if float(row["average_computation_delay"]) < 0:
                blockers.append("raw_metrics_invalid_delay")
        if row["mean_reward"] not in ("", "None", None):
            float(row["mean_reward"])
        if row["total_reward"] not in ("", "None", None):
            float(row["total_reward"])
        trace_dir = Path(row["trace_dir"])
        if not trace_dir.exists():
            blockers.append("raw_metrics_trace_dir_missing")
        try:
            trace_dir.resolve().relative_to(output_dir.resolve())
        except Exception:
            blockers.append("raw_metrics_trace_dir_outside_output_dir")
        notes = json.loads(row["notes_json"])
        required_notes = {"regime_id", "regime_source", "average_computation_delay_denominator", "drop_ratio_denominator", "policy_readiness_status", "pending_tasks_visible"}
        if not required_notes.issubset(notes.keys()):
            blockers.append("raw_metrics_notes_json_missing_required_fields")
        if "contract_diagnostics" in notes and not isinstance(notes["contract_diagnostics"], list):
            blockers.append("raw_metrics_notes_json_invalid")
    metrics = {
        "rows": rows,
        "row_count": len(rows),
        "policy_set": policy_set,
        "regime_set": regime_set,
    }
    return len(blockers) == 0, metrics, blockers


def _validate_summary(summary_path: Path) -> tuple[bool, dict[str, Any], list[str]]:
    if not summary_path.exists():
        return False, {}, ["summary_metrics_missing"]
    summary = _load_json(summary_path)
    if not isinstance(summary, dict):
        return False, {}, ["summary_metrics_schema_invalid"]
    policy_map = summary.get("registry", {})
    active_set = policy_map.get("active_policy_set", [])
    if active_set != ["HOODIE"]:
        return False, summary, ["summary_metrics_unexpected_policy_scope"]
    if summary.get("validation_episode_count") != 1:
        return False, summary, ["summary_metrics_unexpected_validation_episode_count"]
    if summary.get("paper_performance_claims_made") is True:
        return False, summary, ["official_claim_violation"]
    if summary.get("no_metric_rows_generated") is True:
        return False, summary, ["metrics_consistency_failed"]
    return True, summary, []


def _validate_readiness(readiness_path: Path) -> tuple[bool, dict[str, Any], list[str]]:
    if not readiness_path.exists():
        return False, {}, ["readiness_missing"]
    readiness = _load_json(readiness_path)
    blockers: list[str] = []
    if readiness.get("validation_episode_count") != 1:
        blockers.append("readiness_schema_invalid")
    if readiness.get("active_policy_set") not in (["HOODIE"], None):
        blockers.append("official_policy_set_used")
    if readiness.get("figure10_data_ready") is True:
        blockers.append("unexpected_figure10_data_ready_true")
    return len(blockers) == 0, readiness, blockers


def _validate_manifest(manifest_path: Path) -> tuple[bool, dict[str, Any], list[str]]:
    if not manifest_path.exists():
        return False, {}, ["validation_manifest_missing"]
    manifest = _load_json(manifest_path)
    blockers: list[str] = []
    if manifest.get("diagnostic_only") is not True:
        blockers.append("validation_manifest_schema_invalid")
    if manifest.get("figure10_data_ready") is True:
        blockers.append("unexpected_figure10_data_ready_true")
    if manifest.get("paper_performance_claims_made") is True:
        blockers.append("official_claim_violation")
    return len(blockers) == 0, manifest, blockers


def _build_contract_summary(raw_metrics: dict[str, Any], summary: dict[str, Any], readiness: dict[str, Any], manifest: dict[str, Any], metrics_ok: bool, summary_ok: bool, readiness_ok: bool, manifest_ok: bool) -> dict[str, Any]:
    rows = raw_metrics.get("rows", [])
    return {
        "policy_set": raw_metrics.get("policy_set", []),
        "regime_set": raw_metrics.get("regime_set", []),
        "row_count": raw_metrics.get("row_count", 0),
        "figure10_data_ready": bool(readiness.get("figure10_data_ready", False)),
        "baseline_validation_ready": readiness.get("baseline_validation_ready", False),
        "policy_readiness_status": summary.get("registry", {}).get("policy_run_statuses", {}).get("HOODIE"),
        "summary_policy_set": summary.get("registry", {}).get("active_policy_set", []),
        "validation_manifest": manifest,
        "metrics_ok": metrics_ok,
        "summary_ok": summary_ok,
        "readiness_ok": readiness_ok,
        "manifest_ok": manifest_ok,
        "rows": rows,
    }


def run_smoke(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = _resolve_path(args.output_dir)
    if _repo_relative(output_dir):
        raise SystemExit("repo output refused")
    if not args.allow_smoke_checkpoint_evaluation_metrics_hardening:
        raise SystemExit("--allow-smoke-checkpoint-evaluation-metrics-hardening is required")
    if not args.allow_trained_checkpoint_evaluation_wiring_smoke:
        raise SystemExit("--allow-trained-checkpoint-evaluation-wiring-smoke is required")
    if not args.allow_bounded_training_smoke:
        raise SystemExit("--allow-bounded-training-smoke is required")
    if not args.allow_figure10_validation_test_mode:
        raise SystemExit("--allow-figure10-validation-test-mode is required")
    if not args.allow_main_py_training_execution:
        raise SystemExit("--allow-main-py-training-execution is required")
    if not args.allow_training_checkpoint_export:
        raise SystemExit("--allow-training-checkpoint-export is required")
    if args.training_epochs <= 0:
        raise SystemExit("training-epochs must be > 0")
    if args.training_epochs > 1:
        raise SystemExit("training-epochs must be <= 1")
    if args.training_episode_time <= 0:
        raise SystemExit("training-episode-time must be > 0")
    if args.training_episode_time > 3:
        raise SystemExit("training-episode-time must be <= 3")
    if args.validation_episodes <= 0:
        raise SystemExit("validation-episodes must be > 0")
    if args.validation_episodes > 1:
        raise SystemExit("validation-episodes must be <= 1")
    if args.expected_agent_count <= 0:
        raise SystemExit("expected-agent-count must be > 0")
    if args.policies != "HOODIE":
        raise SystemExit("only HOODIE is allowed in this phase")

    output_dir.mkdir(parents=True, exist_ok=True)
    wiring_smoke_result = _run_wiring_smoke(
        output_dir=output_dir,
        training_epochs=args.training_epochs,
        training_episode_time=args.training_episode_time,
        validation_episodes=args.validation_episodes,
        seed=args.seed,
        run_id=args.run_id,
        expected_agent_count=args.expected_agent_count,
        trace_level=args.trace_level,
    )

    wiring_manifest_path = output_dir / "wiring_smoke" / "hoodie_trained_checkpoint_evaluation_wiring_smoke_manifest.json"
    wiring_report_path = output_dir / "wiring_smoke" / "hoodie_trained_checkpoint_evaluation_wiring_smoke_report.json"
    raw_metrics_path = output_dir / "wiring_smoke" / "evaluation_runner" / "figure10_policy_metrics_raw.csv"
    summary_path = output_dir / "wiring_smoke" / "evaluation_runner" / "figure10_policy_metrics_summary.json"
    readiness_path = output_dir / "wiring_smoke" / "evaluation_runner" / "figure10_policy_readiness.json"
    config_snapshot_path = output_dir / "wiring_smoke" / "evaluation_runner" / "figure10_run_config_snapshot.json"
    validation_manifest_path = output_dir / "wiring_smoke" / "evaluation_runner" / "figure10_validation_manifest.json"
    metrics_contract_summary_path = output_dir / "metrics_hardening" / "hoodie_smoke_checkpoint_metrics_contract_summary.json"

    blockers: list[str] = []
    warnings: list[str] = [
        "smoke_metrics_only_not_paper_performance_validation",
        "one_episode_validation_not_statistically_meaningful",
        "hoodie_only_policy_scope_not_official_figure10",
        "baseline_missing_policies_expected_in_smoke",
        "figure10_remains_blocked",
        "figure9_remains_blocked_until_real_paper_scenario_action_distribution",
        "figure11_remains_blocked_until_lstm_ablation",
    ]
    if wiring_smoke_result.returncode != 0:
        blockers.append("wiring_smoke_failed")
    if not wiring_manifest_path.exists():
        blockers.append("wiring_smoke_manifest_missing")
    if not wiring_report_path.exists():
        blockers.append("wiring_smoke_report_missing")

    metrics_ok, raw_metrics, raw_blockers = _validate_raw_metrics(raw_metrics_path, output_dir / "wiring_smoke" / "evaluation_runner")
    summary_ok, summary, summary_blockers = _validate_summary(summary_path)
    readiness_ok, readiness, readiness_blockers = _validate_readiness(readiness_path)
    manifest_ok, validation_manifest, manifest_blockers = _validate_manifest(validation_manifest_path)
    blockers.extend(raw_blockers)
    blockers.extend(summary_blockers)
    blockers.extend(readiness_blockers)
    blockers.extend(manifest_blockers)
    if raw_metrics_path.exists() is False or summary_path.exists() is False or readiness_path.exists() is False or validation_manifest_path.exists() is False:
        blockers.append("metric_file_missing")
    if readiness.get("figure10_data_ready") is True:
        blockers.append("unexpected_figure10_data_ready_true")
    if validation_manifest.get("paper_performance_claims_made") is True:
        blockers.append("paper_reproduction_claim_violation")
    if validation_manifest.get("official_claim_allowed") is True:
        blockers.append("official_claim_violation")
    if validation_manifest.get("strict_readiness", False) is True:
        blockers.append("strict_readiness_used")
    if not raw_metrics:
        blockers.append("raw_metrics_missing")
    if not raw_metrics_path.exists() or not raw_metrics_path.read_text().strip():
        blockers.append("raw_metrics_empty")

    metrics_contract_summary = _build_contract_summary(raw_metrics, summary, readiness, validation_manifest, metrics_ok, summary_ok, readiness_ok, manifest_ok)
    _write_json(metrics_contract_summary_path, metrics_contract_summary)

    manifest = {
        "phase": "6.14",
        "scope": "hoodie_smoke_checkpoint_evaluation_metrics_hardening",
        "metrics_hardening_run": True,
        "wiring_smoke_run": True,
        "wiring_smoke_scope": "phase6_13_trained_checkpoint_evaluation_wiring_smoke",
        "training_epochs": args.training_epochs,
        "training_episode_time": args.training_episode_time,
        "validation_episodes": args.validation_episodes,
        "validation_policies": ["HOODIE"],
        "strict_readiness_used": False,
        "main_py_called": True,
        "main_py_training_called_by_guarded_runner": True,
        "main_py_validation_called_by_figure10_runner": True,
        "figure10_validation_called": True,
        "figure10_validation_test_mode": True,
        "simulation_rerun": True,
        "simulation_rerun_scope": "bounded_training_plus_test_mode_metrics_hardening_smoke_only",
        "official_simulation_rerun": False,
        "metrics_files_present": raw_metrics_path.exists() and summary_path.exists() and readiness_path.exists() and validation_manifest_path.exists(),
        "raw_metrics_schema_valid": metrics_ok,
        "raw_metrics_rows_present": bool(raw_metrics.get("row_count", 0)),
        "raw_metrics_policy_scope_valid": raw_metrics.get("policy_set") == ["HOODIE"],
        "raw_metrics_regime_scope_valid": raw_metrics.get("regime_set") == ["delay", "drop_ratio"],
        "raw_metrics_numeric_contract_valid": metrics_ok,
        "raw_metrics_notes_json_valid": metrics_ok,
        "summary_metrics_schema_valid": summary_ok,
        "readiness_schema_valid": readiness_ok,
        "manifest_schema_valid": manifest_ok,
        "metrics_consistency_valid": metrics_ok and summary_ok and readiness_ok and manifest_ok,
        "non_official_guard_valid": True,
        "raw_row_count": raw_metrics.get("row_count", 0),
        "raw_policy_set": raw_metrics.get("policy_set", []),
        "raw_regime_set": raw_metrics.get("regime_set", []),
        "readiness_figure10_data_ready": bool(readiness.get("figure10_data_ready", False)),
        "summary_figure10_data_ready": summary.get("figure10_data_ready"),
        "validation_manifest_figure10_data_ready": validation_manifest.get("figure10_data_ready"),
        "official_training_run": False,
        "full_training_run": False,
        "paper_training_run": False,
        "paper_grade_5000_episode_training_run": False,
        "official_validation_run": False,
        "official_200_episode_validation_run": False,
        "official_figure_claims_made": False,
        "official_claim_allowed": False,
        "paper_reproduction_claim": False,
        "checkpoint_artifact_committed": False,
        "model_artifact_committed": False,
        "trace_artifact_committed": False,
        "figure10_artifact_committed": False,
        "metrics_artifact_committed": False,
        "figure8_claim": False,
        "figure9_claim": False,
        "figure10_claim": False,
        "figure11_claim": False,
        "wiring_smoke_manifest_path": str(wiring_manifest_path),
        "wiring_smoke_report_path": str(wiring_report_path),
        "raw_metrics_path": str(raw_metrics_path),
        "summary_metrics_path": str(summary_path),
        "readiness_path": str(readiness_path),
        "validation_manifest_path": str(validation_manifest_path),
        "config_snapshot_path": str(config_snapshot_path),
        "metrics_contract_summary_path": str(metrics_contract_summary_path),
        "blockers": list(dict.fromkeys(blockers)),
        "warnings": warnings,
    }

    report = {
        "phase": "6.14",
        "scope": "hoodie_smoke_checkpoint_evaluation_metrics_hardening",
        "metrics_hardening_run": True,
        "wiring_smoke_completed": wiring_smoke_result.returncode == 0,
        "metrics_files_present": manifest["metrics_files_present"],
        "raw_metrics_schema_valid": metrics_ok,
        "raw_metrics_numeric_contract_valid": metrics_ok,
        "raw_metrics_notes_json_valid": metrics_ok,
        "metrics_consistency_valid": manifest["metrics_consistency_valid"],
        "figure10_data_ready": False,
        "official_claim_allowed": False,
        "paper_reproduction_claim": False,
        "blockers": manifest["blockers"],
        "warnings": warnings,
    }

    _write_json(output_dir / "hoodie_smoke_checkpoint_evaluation_metrics_hardening_manifest.json", manifest)
    _write_json(output_dir / "hoodie_smoke_checkpoint_evaluation_metrics_hardening_report.json", report)
    return {"manifest": manifest, "report": report}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--training-epochs", type=int, default=1)
    parser.add_argument("--training-episode-time", type=int, default=3)
    parser.add_argument("--validation-episodes", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--run-id", default="phase6_14_smoke_checkpoint_evaluation_metrics_hardening")
    parser.add_argument("--expected-agent-count", type=int, default=20)
    parser.add_argument("--trace-level", default="summary")
    parser.add_argument("--allow-smoke-checkpoint-evaluation-metrics-hardening", action="store_true")
    parser.add_argument("--allow-trained-checkpoint-evaluation-wiring-smoke", action="store_true")
    parser.add_argument("--allow-bounded-training-smoke", action="store_true")
    parser.add_argument("--allow-figure10-validation-test-mode", action="store_true")
    parser.add_argument("--allow-main-py-training-execution", action="store_true")
    parser.add_argument("--allow-training-checkpoint-export", action="store_true")
    parser.add_argument("--policies", default="HOODIE")
    args = parser.parse_args(argv)

    output_dir = _resolve_path(args.output_dir)
    if _repo_relative(output_dir):
        raise SystemExit("repo output refused")
    if not args.allow_smoke_checkpoint_evaluation_metrics_hardening:
        raise SystemExit("--allow-smoke-checkpoint-evaluation-metrics-hardening is required")
    if not args.allow_trained_checkpoint_evaluation_wiring_smoke:
        raise SystemExit("--allow-trained-checkpoint-evaluation-wiring-smoke is required")
    if not args.allow_bounded_training_smoke:
        raise SystemExit("--allow-bounded-training-smoke is required")
    if not args.allow_figure10_validation_test_mode:
        raise SystemExit("--allow-figure10-validation-test-mode is required")
    if not args.allow_main_py_training_execution:
        raise SystemExit("--allow-main-py-training-execution is required")
    if not args.allow_training_checkpoint_export:
        raise SystemExit("--allow-training-checkpoint-export is required")
    if args.training_epochs <= 0 or args.training_epochs > 1:
        raise SystemExit("training-epochs must be 1 for this smoke")
    if args.training_episode_time <= 0 or args.training_episode_time > 3:
        raise SystemExit("training-episode-time must be between 1 and 3 for this smoke")
    if args.validation_episodes <= 0 or args.validation_episodes > 1:
        raise SystemExit("validation-episodes must be 1 for this smoke")
    if args.expected_agent_count <= 0:
        raise SystemExit("expected-agent-count must be > 0")

    result = run_smoke(args)
    blockers = result["manifest"].get("blockers", []) or result["report"].get("blockers", [])
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
