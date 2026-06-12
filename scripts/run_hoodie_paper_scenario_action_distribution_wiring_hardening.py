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

from analysis.hoodie_action_distribution import write_action_distribution_outputs


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


def _run_metrics_hardening(
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
        "scripts/run_hoodie_smoke_checkpoint_evaluation_metrics_hardening.py",
        "--output-dir",
        str(output_dir / "metrics_hardening"),
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
        "--allow-smoke-checkpoint-evaluation-metrics-hardening",
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


def _load_raw_metrics_rows(raw_path: Path) -> list[dict[str, str]]:
    if not raw_path.exists():
        return []
    text = raw_path.read_text().strip()
    if not text:
        return []
    return list(csv.DictReader(text.splitlines()))


def _find_action_records_source(metrics_dir: Path) -> tuple[Path | None, str]:
    candidates = [
        metrics_dir / "wiring_smoke" / "action_records.json",
        metrics_dir / "wiring_smoke" / "evaluation_runner" / "action_records.json",
    ]
    candidates.extend(sorted(metrics_dir.glob("wiring_smoke/evaluation_runner/runs/**/action_records.json")))
    for candidate in candidates:
        if candidate.exists():
            return candidate, "real_phase6_14_action_records"
    return None, "synthetic_phase6_15_wiring_probe"


def _category_for_row(row: dict[str, str], index: int) -> str:
    regime = row.get("regime_id", "")
    if regime == "delay":
        return "local"
    if regime == "drop_ratio":
        return "horizontal" if index % 2 == 0 else "vertical"
    return "unknown"


def _build_action_records(rows: list[dict[str, str]], run_id: str, allow_unknown_actions_for_diagnostic: bool) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        category = _category_for_row(row, index)
        if category == "unknown" and not allow_unknown_actions_for_diagnostic:
            raise ValueError("action_record_numeric_only_unmapped")
        action_label = category if category != "unknown" else "unknown"
        records.append(
            {
                "run_id": run_id,
                "regime_id": row.get("regime_id", ""),
                "policy_name": "HOODIE",
                "agent_index": index,
                "evaluation_step": index,
                "action_type": action_label,
                "action_name": action_label,
                "action_category": action_label,
                "offload_type": action_label,
                "decision": action_label,
                "selected_action": action_label,
                "policy_action": action_label,
                "target_tier": action_label,
                "source": "phase6_15_action_distribution_wiring_probe",
                "diagnostic_only": True,
                "official_figure_claim": False,
                "paper_reproduction_claim": False,
            }
        )
    return records


def _validate_action_records(
    records: list[dict[str, Any]],
    *,
    allow_unknown_actions_for_diagnostic: bool,
) -> tuple[bool, list[str], dict[str, int]]:
    blockers: list[str] = []
    counts = Counter({"local": 0, "horizontal": 0, "vertical": 0, "unknown": 0})
    if not records:
        return False, ["action_records_empty"], dict(counts)
    for record in records:
        if not isinstance(record, dict):
            blockers.append("action_records_schema_missing_fields")
            continue
        if record.get("policy_name") != "HOODIE":
            blockers.append("action_record_policy_scope_invalid")
        if record.get("regime_id") not in {"delay", "drop_ratio"}:
            blockers.append("action_record_regime_scope_invalid")
        if not record.get("diagnostic_only", False):
            blockers.append("action_record_schema_missing_fields")
        if record.get("official_figure_claim") is True:
            blockers.append("action_record_official_claim_violation")
        if record.get("paper_reproduction_claim") is True:
            blockers.append("action_record_paper_reproduction_claim_violation")
        explicit_fields = [
            "action_type",
            "action_name",
            "action_category",
            "offload_type",
            "decision",
            "selected_action",
            "policy_action",
            "target_tier",
        ]
        explicit_values = [record.get(field) for field in explicit_fields if isinstance(record.get(field), str)]
        if not explicit_values:
            blockers.append("action_record_category_missing")
            continue
        normalized = next((v.lower() for v in explicit_values if v.lower() in {"local", "horizontal", "vertical", "unknown"}), None)
        if normalized is None:
            blockers.append("action_record_unknown_category")
            continue
        if normalized == "unknown" and not allow_unknown_actions_for_diagnostic:
            blockers.append("unknown_actions_present")
        counts[normalized] += 1
    if counts["unknown"] > 0 and not allow_unknown_actions_for_diagnostic:
        blockers.append("unknown_actions_present")
    if not allow_unknown_actions_for_diagnostic and counts["unknown"] > 0:
        blockers.append("action_distribution_unknown_count_not_allowed")
    return len(blockers) == 0, list(dict.fromkeys(blockers)), dict(counts)


def _validate_action_distribution_outputs(
    action_dir: Path,
    action_records: list[dict[str, Any]],
    *,
    allow_unknown_actions_for_diagnostic: bool,
) -> list[str]:
    blockers: list[str] = []
    records_path = action_dir / "action_records.json"
    csv_path = action_dir / "hoodie_action_distribution.csv"
    json_path = action_dir / "hoodie_action_distribution.json"
    metadata_path = action_dir / "hoodie_action_distribution_metadata.json"
    contract_summary_path = action_dir / "hoodie_action_distribution_contract_summary.json"
    paths = (records_path, csv_path, json_path, metadata_path, contract_summary_path)
    if not all(path.exists() for path in paths):
        blockers.append("action_distribution_file_missing")
        return list(dict.fromkeys(blockers))
    try:
        csv_rows = list(csv.DictReader(csv_path.read_text().splitlines()))
    except Exception:
        blockers.append("action_distribution_csv_invalid")
        csv_rows = []
    try:
        action_distribution = _load_json(json_path)
    except Exception:
        blockers.append("action_distribution_json_invalid")
        action_distribution = {}
    try:
        metadata = _load_json(metadata_path)
    except Exception:
        blockers.append("action_distribution_metadata_invalid")
        metadata = {}
    try:
        contract_summary = _load_json(contract_summary_path)
    except Exception:
        blockers.append("action_distribution_metadata_invalid")
        contract_summary = {}
    if csv_rows and any(row.get("policy_name") != "HOODIE" for row in csv_rows):
        blockers.append("action_distribution_csv_invalid")
    if csv_rows and set(row.get("category") for row in csv_rows) != {"local", "horizontal", "vertical", "unknown"}:
        blockers.append("action_distribution_csv_invalid")
    if action_distribution.get("policy_name") != "HOODIE":
        blockers.append("action_distribution_json_invalid")
    if action_distribution.get("total_actions") != len(action_records):
        blockers.append("action_distribution_count_mismatch")
    if action_distribution.get("unknown_count", 0) > 0 and not allow_unknown_actions_for_diagnostic:
        blockers.append("action_distribution_unknown_count_not_allowed")
    total_actions = action_distribution.get("total_actions", 0)
    if total_actions > 0:
        ratios = [
            action_distribution.get("local_ratio", 0.0),
            action_distribution.get("horizontal_ratio", 0.0),
            action_distribution.get("vertical_ratio", 0.0),
            action_distribution.get("unknown_ratio", 0.0),
        ]
        if any((not isinstance(r, (int, float))) or r < 0.0 or r > 1.0 for r in ratios):
            blockers.append("action_distribution_ratio_invalid")
        if abs(sum(ratios) - 1.0) > 1e-9:
            blockers.append("action_distribution_ratio_sum_invalid")
    if metadata.get("official_figure_claim") is True or metadata.get("official_claim_allowed") is True:
        blockers.append("action_distribution_official_claim_violation")
    if metadata.get("paper_reproduction_claim") is True:
        blockers.append("action_distribution_paper_reproduction_claim_violation")
    if metadata.get("source") not in {"checkpointed_evaluation_or_synthetic_test", "phase6_15_action_distribution_wiring_probe"}:
        blockers.append("action_distribution_metadata_invalid")
    if metadata.get("policy_name") != "HOODIE":
        blockers.append("action_distribution_metadata_invalid")
    if contract_summary.get("figure9_data_ready") is not False or contract_summary.get("figure10_data_ready") is not False:
        blockers.append("action_distribution_metadata_invalid")
    return list(dict.fromkeys(blockers))


def run_smoke(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = _resolve_path(args.output_dir)
    if _repo_relative(output_dir):
        raise SystemExit("repo output refused")
    required_flags = [
        args.allow_paper_scenario_action_distribution_wiring_hardening,
        args.allow_smoke_checkpoint_evaluation_metrics_hardening,
        args.allow_trained_checkpoint_evaluation_wiring_smoke,
        args.allow_bounded_training_smoke,
        args.allow_figure10_validation_test_mode,
        args.allow_main_py_training_execution,
        args.allow_training_checkpoint_export,
    ]
    if not all(required_flags):
        raise SystemExit("required allow flag missing")
    if args.training_epochs <= 0 or args.training_epochs > 1:
        raise SystemExit("training-epochs out of bounds")
    if args.training_episode_time <= 0 or args.training_episode_time > 3:
        raise SystemExit("training-episode-time out of bounds")
    if args.validation_episodes <= 0 or args.validation_episodes > 1:
        raise SystemExit("validation-episodes out of bounds")
    if args.expected_agent_count <= 0:
        raise SystemExit("expected-agent-count must be > 0")
    if args.policies != "HOODIE":
        raise SystemExit("only HOODIE is allowed")

    output_dir.mkdir(parents=True, exist_ok=True)
    metrics_result = _run_metrics_hardening(
        output_dir=output_dir,
        training_epochs=args.training_epochs,
        training_episode_time=args.training_episode_time,
        validation_episodes=args.validation_episodes,
        seed=args.seed,
        run_id=args.run_id,
        expected_agent_count=args.expected_agent_count,
        trace_level=args.trace_level,
    )

    metrics_dir = output_dir / "metrics_hardening"
    metrics_manifest_path = metrics_dir / "hoodie_smoke_checkpoint_evaluation_metrics_hardening_manifest.json"
    metrics_report_path = metrics_dir / "hoodie_smoke_checkpoint_evaluation_metrics_hardening_report.json"
    raw_metrics_path = metrics_dir / "wiring_smoke" / "evaluation_runner" / "figure10_policy_metrics_raw.csv"
    summary_path = metrics_dir / "wiring_smoke" / "evaluation_runner" / "figure10_policy_metrics_summary.json"
    readiness_path = metrics_dir / "wiring_smoke" / "evaluation_runner" / "figure10_policy_readiness.json"
    validation_manifest_path = metrics_dir / "wiring_smoke" / "evaluation_runner" / "figure10_validation_manifest.json"
    config_snapshot_path = metrics_dir / "wiring_smoke" / "evaluation_runner" / "figure10_run_config_snapshot.json"
    action_dir = output_dir / "action_distribution"
    records_path = action_dir / "action_records.json"
    csv_path = action_dir / "hoodie_action_distribution.csv"
    json_path = action_dir / "hoodie_action_distribution.json"
    metadata_path = action_dir / "hoodie_action_distribution_metadata.json"
    contract_summary_path = action_dir / "hoodie_action_distribution_contract_summary.json"

    blockers: list[str] = []
    warnings: list[str] = [
        "action_distribution_wiring_only_not_figure9_reproduction",
        "smoke_action_distribution_not_statistically_meaningful",
        "hoodie_only_policy_scope_not_official_figure9_or_figure10",
        "one_episode_validation_not_paper_scenario_validation",
        "figure9_remains_blocked_until_real_paper_scenario_action_distribution",
        "figure10_remains_blocked",
        "figure11_remains_blocked_until_lstm_ablation",
        "generated_action_distribution_outputs_must_not_be_committed",
    ]

    metrics_manifest = {}
    metrics_report = {}
    metrics_success = False
    if metrics_result.returncode != 0:
        blockers.append("metrics_hardening_failed")
    if metrics_manifest_path.exists():
        metrics_manifest = _load_json(metrics_manifest_path)
    else:
        blockers.append("metrics_hardening_manifest_missing")
    if metrics_report_path.exists():
        metrics_report = _load_json(metrics_report_path)
    else:
        blockers.append("metrics_hardening_report_missing")

    if metrics_manifest.get("readiness_figure10_data_ready") is True or metrics_report.get("figure10_data_ready") is True:
        blockers.append("metrics_hardening_figure10_data_ready_true")
    metrics_success = (
        metrics_result.returncode == 0
        and metrics_manifest.get("metrics_consistency_valid") is True
        and metrics_manifest.get("raw_metrics_policy_scope_valid") is True
        and metrics_manifest.get("raw_metrics_regime_scope_valid") is True
        and metrics_manifest.get("raw_metrics_numeric_contract_valid") is True
        and metrics_manifest.get("raw_metrics_notes_json_valid") is True
        and metrics_manifest.get("summary_metrics_schema_valid") is True
        and metrics_manifest.get("readiness_schema_valid") is True
        and metrics_manifest.get("manifest_schema_valid") is True
        and metrics_manifest.get("official_claim_allowed") is False
        and metrics_manifest.get("paper_reproduction_claim") is False
        and metrics_manifest.get("readiness_figure10_data_ready") is False
    )
    if not metrics_success:
        blockers.append("metrics_hardening_failed")
        if metrics_manifest.get("metrics_consistency_valid") is not True:
            blockers.append("metrics_hardening_consistency_invalid")
        if metrics_manifest.get("raw_metrics_policy_scope_valid") is not True:
            blockers.append("metrics_hardening_raw_policy_scope_invalid")
        if metrics_manifest.get("raw_metrics_regime_scope_valid") is not True:
            blockers.append("metrics_hardening_raw_regime_scope_invalid")
        if metrics_manifest.get("raw_metrics_numeric_contract_valid") is not True:
            blockers.append("metrics_hardening_numeric_contract_invalid")
        if metrics_manifest.get("raw_metrics_notes_json_valid") is not True:
            blockers.append("metrics_hardening_notes_json_invalid")
        if metrics_manifest.get("summary_metrics_schema_valid") is not True:
            blockers.append("metrics_hardening_summary_schema_invalid")
        if metrics_manifest.get("readiness_schema_valid") is not True:
            blockers.append("metrics_hardening_readiness_schema_invalid")
        if metrics_manifest.get("manifest_schema_valid") is not True:
            blockers.append("metrics_hardening_manifest_schema_invalid")
        if metrics_manifest.get("official_claim_allowed") is True:
            blockers.append("metrics_hardening_official_claim_violation")
        if metrics_manifest.get("paper_reproduction_claim") is True:
            blockers.append("metrics_hardening_paper_reproduction_claim_violation")

    rows = _load_raw_metrics_rows(raw_metrics_path)
    if not rows:
        blockers.append("action_records_missing")
    source_path, source_kind = _find_action_records_source(metrics_dir)
    records: list[dict[str, Any]] = []
    action_records_source = source_kind
    synthetic_action_records_used = source_kind == "synthetic_phase6_15_wiring_probe"
    real_action_records_used = source_kind == "real_phase6_14_action_records"
    if source_path is not None:
        try:
            loaded = _load_json(source_path)
        except Exception:
            blockers.append("action_records_schema_missing_fields")
            loaded = None
        if isinstance(loaded, list):
            records = loaded
        elif loaded is not None:
            blockers.append("action_records_schema_missing_fields")
    elif rows:
        try:
            records = _build_action_records(rows, args.run_id, args.allow_unknown_actions_for_diagnostic)
        except ValueError as exc:
            blockers.append(str(exc))
        synthetic_action_records_used = True
        real_action_records_used = False

    records_valid = False
    counts = {"local": 0, "horizontal": 0, "vertical": 0, "unknown": 0}
    if records:
        records_valid, record_blockers, counts = _validate_action_records(records, allow_unknown_actions_for_diagnostic=args.allow_unknown_actions_for_diagnostic)
        blockers.extend(record_blockers)
    elif source_path is not None:
        blockers.append("action_records_empty")

    action_files_present = False
    if metrics_success and records_valid:
        _write_json(records_path, records)
        outputs = write_action_distribution_outputs(records, action_dir, label=args.run_id, policy_name="HOODIE")
        contract_summary = {
            "phase": "6.15",
            "scope": "hoodie_paper_scenario_action_distribution_wiring_hardening",
            "metrics_hardening_manifest": str(metrics_manifest_path),
            "metrics_hardening_report": str(metrics_report_path),
            "action_records_path": str(records_path),
            "action_distribution_csv_path": str(csv_path),
            "action_distribution_json_path": str(json_path),
            "action_distribution_metadata_path": str(metadata_path),
            "allowed_unknown_actions_for_diagnostic": args.allow_unknown_actions_for_diagnostic,
            "policy_name": "HOODIE",
            "action_records_source": action_records_source,
            "action_records_source_path": str(source_path) if source_path else None,
            "synthetic_action_records_used": synthetic_action_records_used,
            "real_action_records_used": real_action_records_used,
            "figure9_data_ready": False,
            "figure10_data_ready": False,
            "official_claim_allowed": False,
            "paper_reproduction_claim": False,
            "warnings": warnings,
        }
        _write_json(contract_summary_path, contract_summary)
        action_files_present = all(path.exists() for path in (records_path, csv_path, json_path, metadata_path, contract_summary_path))
    else:
        blockers.append("action_distribution_file_missing")

    if action_files_present:
        action_records = _load_json(records_path)
        blockers.extend(
            _validate_action_distribution_outputs(
                action_dir,
                action_records,
                allow_unknown_actions_for_diagnostic=args.allow_unknown_actions_for_diagnostic,
            )
        )
        action_distribution = _load_json(json_path)
        metadata = _load_json(metadata_path)
        action_files_present = all(path.exists() for path in (records_path, csv_path, json_path, metadata_path, contract_summary_path)) and not blockers

    manifest = {
        "phase": "6.15",
        "scope": "hoodie_paper_scenario_action_distribution_wiring_hardening",
        "action_distribution_wiring_hardening_run": True,
        "metrics_hardening_run": True,
        "metrics_hardening_scope": "phase6_14_smoke_checkpoint_evaluation_metrics_hardening",
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
        "simulation_rerun_scope": "bounded_training_plus_test_mode_action_distribution_wiring_hardening_only",
        "official_simulation_rerun": False,
        "action_records_present": bool(records),
        "action_records_schema_valid": records_valid,
        "action_records_explicit_category_valid": records_valid,
        "action_records_policy_scope_valid": all(r.get("policy_name") == "HOODIE" for r in records) if records else False,
        "action_records_regime_scope_valid": all(r.get("regime_id") in {"delay", "drop_ratio"} for r in records) if records else False,
        "action_records_source": action_records_source,
        "action_records_source_path": str(source_path) if source_path else None,
        "synthetic_action_records_used": synthetic_action_records_used,
        "real_action_records_used": real_action_records_used,
        "action_distribution_files_present": action_files_present,
        "action_distribution_csv_valid": action_files_present,
        "action_distribution_json_valid": action_files_present,
        "action_distribution_metadata_valid": action_files_present,
        "action_distribution_counts_valid": action_files_present,
        "action_distribution_ratios_valid": action_files_present,
        "unknown_actions_present": counts.get("unknown", 0) > 0,
        "unknown_actions_allowed": False,
        "paper_scenario_action_distribution_ready": False,
        "action_distribution_wiring_ready": action_files_present and not blockers,
        "total_action_records": len(records),
        "local_count": counts.get("local", 0),
        "horizontal_count": counts.get("horizontal", 0),
        "vertical_count": counts.get("vertical", 0),
        "unknown_count": counts.get("unknown", 0),
        "local_ratio": 0.0 if len(records) == 0 else counts.get("local", 0) / len(records),
        "horizontal_ratio": 0.0 if len(records) == 0 else counts.get("horizontal", 0) / len(records),
        "vertical_ratio": 0.0 if len(records) == 0 else counts.get("vertical", 0) / len(records),
        "unknown_ratio": 0.0 if len(records) == 0 else counts.get("unknown", 0) / len(records),
        "figure9_data_ready": False,
        "figure10_data_ready": False,
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
        "figure9_artifact_committed": False,
        "figure10_artifact_committed": False,
        "metrics_artifact_committed": False,
        "action_distribution_artifact_committed": False,
        "figure8_claim": False,
        "figure9_claim": False,
        "figure10_claim": False,
        "figure11_claim": False,
        "metrics_hardening_manifest_path": str(metrics_manifest_path),
        "metrics_hardening_report_path": str(metrics_report_path),
        "action_records_path": str(records_path),
        "action_distribution_csv_path": str(csv_path),
        "action_distribution_json_path": str(json_path),
        "action_distribution_metadata_path": str(metadata_path),
        "action_distribution_contract_summary_path": str(contract_summary_path),
        "blockers": list(dict.fromkeys(blockers)),
        "warnings": warnings,
    }

    report = {
        "phase": "6.15",
        "scope": "hoodie_paper_scenario_action_distribution_wiring_hardening",
        "action_distribution_wiring_hardening_run": True,
        "metrics_hardening_completed": metrics_success,
        "action_records_present": bool(records),
        "action_distribution_files_present": action_files_present,
        "action_distribution_counts_valid": action_files_present,
        "action_distribution_ratios_valid": action_files_present,
        "unknown_actions_present": counts.get("unknown", 0) > 0,
        "figure9_data_ready": False,
        "figure10_data_ready": False,
        "official_claim_allowed": False,
        "paper_reproduction_claim": False,
        "blockers": manifest["blockers"],
        "warnings": warnings,
    }

    _write_json(output_dir / "hoodie_paper_scenario_action_distribution_wiring_hardening_manifest.json", manifest)
    _write_json(output_dir / "hoodie_paper_scenario_action_distribution_wiring_hardening_report.json", report)
    return {"manifest": manifest, "report": report}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--training-epochs", type=int, default=1)
    parser.add_argument("--training-episode-time", type=int, default=3)
    parser.add_argument("--validation-episodes", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--run-id", default="phase6_15_paper_scenario_action_distribution_wiring_hardening")
    parser.add_argument("--expected-agent-count", type=int, default=20)
    parser.add_argument("--trace-level", default="summary")
    parser.add_argument("--allow-paper-scenario-action-distribution-wiring-hardening", action="store_true")
    parser.add_argument("--allow-smoke-checkpoint-evaluation-metrics-hardening", action="store_true")
    parser.add_argument("--allow-trained-checkpoint-evaluation-wiring-smoke", action="store_true")
    parser.add_argument("--allow-bounded-training-smoke", action="store_true")
    parser.add_argument("--allow-figure10-validation-test-mode", action="store_true")
    parser.add_argument("--allow-main-py-training-execution", action="store_true")
    parser.add_argument("--allow-training-checkpoint-export", action="store_true")
    parser.add_argument("--allow-unknown-actions-for-diagnostic", action="store_true")
    parser.add_argument("--policies", default="HOODIE")
    args = parser.parse_args(argv)

    output_dir = _resolve_path(args.output_dir)
    if _repo_relative(output_dir):
        raise SystemExit("repo output refused")
    if not args.allow_paper_scenario_action_distribution_wiring_hardening:
        raise SystemExit("--allow-paper-scenario-action-distribution-wiring-hardening is required")
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
        raise SystemExit("training-epochs out of bounds")
    if args.training_episode_time <= 0 or args.training_episode_time > 3:
        raise SystemExit("training-episode-time out of bounds")
    if args.validation_episodes <= 0 or args.validation_episodes > 1:
        raise SystemExit("validation-episodes out of bounds")
    if args.expected_agent_count <= 0:
        raise SystemExit("expected-agent-count must be > 0")
    if args.policies != "HOODIE":
        raise SystemExit("only HOODIE is allowed")
    result = run_smoke(args)
    return 0 if not result["manifest"]["blockers"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
