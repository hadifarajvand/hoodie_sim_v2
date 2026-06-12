from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
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


def _training_smoke_args(
    *,
    output_dir: Path,
    training_epochs: int,
    training_episode_time: int,
    seed: int,
    run_id: str,
    expected_agent_count: int,
    trace_level: str,
) -> SimpleNamespace:
    return SimpleNamespace(
        output_dir=str(output_dir),
        epochs=int(training_epochs),
        episode_time=int(training_episode_time),
        seed=int(seed),
        run_id=run_id,
        expected_agent_count=int(expected_agent_count),
        trace_level=trace_level,
        checkpoint_format="pytorch_model_file",
        allow_bounded_small_real_training_smoke=True,
        allow_main_py_training_execution=True,
        allow_training_checkpoint_export=True,
    )


def _run_training_smoke(
    *,
    output_dir: Path,
    training_epochs: int,
    training_episode_time: int,
    seed: int,
    run_id: str,
    expected_agent_count: int,
    trace_level: str,
) -> dict[str, Any]:
    import scripts.run_hoodie_bounded_small_real_training_smoke as bounded_smoke

    args = _training_smoke_args(
        output_dir=output_dir,
        training_epochs=training_epochs,
        training_episode_time=training_episode_time,
        seed=seed,
        run_id=run_id,
        expected_agent_count=expected_agent_count,
        trace_level=trace_level,
    )
    result = bounded_smoke.run_smoke(args)
    training_manifest_path = output_dir / "hoodie_bounded_small_real_training_smoke_manifest.json"
    training_report_path = output_dir / "hoodie_bounded_small_real_training_smoke_report.json"
    export_manifest_path = output_dir / "hoodie_small_real_training_export_manifest.json"
    return {
        "result": result,
        "manifest": result.get("manifest", {}),
        "report": result.get("report", {}),
        "manifest_path": training_manifest_path,
        "report_path": training_report_path,
        "export_manifest_path": export_manifest_path,
        "checkpoint_dir": output_dir / "trained_checkpoints",
    }


def _prepare_evaluation_hyperparameters(
    *,
    output_dir: Path,
    training_episode_time: int,
) -> tuple[Path, list[dict[str, Any]]]:
    base_hyperparameters = _load_json(ROOT / "hyperparameters" / "hyperparameters.json")
    hyperparameters = json.loads(json.dumps(base_hyperparameters))
    overrides: list[dict[str, Any]] = []

    def _apply(key: str, value: Any) -> None:
        hyperparameters[key] = value
        overrides.append({"key": key, "value": value})

    if hyperparameters.get("decision_makers") != "HOODIE":
        _apply("decision_makers", "HOODIE")
    desired_episode_time = min(int(training_episode_time), 3)
    if int(hyperparameters.get("episode_time", desired_episode_time)) != desired_episode_time:
        _apply("episode_time", desired_episode_time)
    if isinstance(hyperparameters.get("task_arrive_probabilities"), list):
        _apply("task_arrive_probabilities", [1.0 for _ in hyperparameters["task_arrive_probabilities"]])

    inputs_dir = output_dir / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)
    hyperparameters_path = inputs_dir / "hyperparameters_phase6_13_evaluation.json"
    _write_json(hyperparameters_path, hyperparameters)
    return hyperparameters_path, overrides


def _run_figure10_validation_runner(
    *,
    output_dir: Path,
    validation_episodes: int,
    seed: int,
    run_id: str,
    hyperparameters_file: Path,
    checkpoint_dir: Path,
) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"
    env["MPLCONFIGDIR"] = str(output_dir / "cache" / "mplconfig")
    env["XDG_CACHE_HOME"] = str(output_dir / "cache" / "xdg")
    cmd = [
        sys.executable,
        "figure10_validation.py",
        "--output-dir",
        str(output_dir / "evaluation_runner"),
        "--episodes",
        str(validation_episodes),
        "--policies",
        "HOODIE",
        "--hoodie-checkpoint-dir",
        str(checkpoint_dir),
        "--test-mode",
        "--trace-level",
        "summary",
        "--seed",
        str(seed),
        "--run-id",
        run_id,
        "--hyperparameters-file",
        str(hyperparameters_file),
        "--paper-contract",
        str(ROOT / "config" / "paper_table4_contract.json"),
    ]
    return subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, check=False)


def _verify_training_smoke(result: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    manifest = result.get("manifest", {})
    report = result.get("report", {})
    blockers: list[str] = []
    warnings: list[str] = []
    manifest_path = Path(result["manifest_path"])
    report_path = Path(result["report_path"])
    checkpoint_dir = Path(result["checkpoint_dir"])

    if not manifest_path.exists():
        blockers.append("training_smoke_manifest_missing")
    if not report_path.exists():
        blockers.append("training_smoke_report_missing")
    if report.get("main_returncode") != 0:
        blockers.append("training_smoke_failed")
    if not checkpoint_dir.exists():
        blockers.append("training_checkpoint_dir_missing")
    if manifest.get("blockers"):
        blockers.extend(str(item) for item in manifest.get("blockers", []))
    if report.get("blockers"):
        blockers.extend(str(item) for item in report.get("blockers", []))
    if not report.get("runtime_loader_verified"):
        blockers.append("training_checkpoint_not_runtime_loadable")
    if not report.get("agent_load_model_verified"):
        blockers.append("training_agent_load_model_not_verified")
    for agent_index in range(int(report.get("actual_agent_count", manifest.get("actual_agent_count", 0)) or 0)):
        checkpoint = checkpoint_dir / f"agent_{agent_index}.pth"
        sidecar = checkpoint_dir / f"agent_{agent_index}.pth.meta.json"
        if not checkpoint.exists():
            blockers.append(f"training_checkpoint_missing: agent_{agent_index}")
        if not sidecar.exists():
            blockers.append(f"training_metadata_sidecar_missing: agent_{agent_index}")
    if report.get("official_claim_allowed") is True or manifest.get("official_claim_allowed") is True:
        blockers.append("official_claim_violation")
    warnings.extend(
        [
            "bounded_smoke_checkpoint_only_not_paper_training",
            "test_mode_evaluation_only_not_official_figure10",
            "one_episode_validation_not_performance_validation",
            "figure10_remains_blocked",
            "figure9_remains_blocked_until_real_paper_scenario_action_distribution",
            "figure11_remains_blocked_until_lstm_ablation",
        ]
    )
    blockers = list(dict.fromkeys(blockers))
    return len(blockers) == 0, blockers, warnings


def _collect_evaluation_wiring_report(
    *,
    output_dir: Path,
    run_id: str,
    expected_agent_count: int,
) -> tuple[bool, list[dict[str, Any]], list[str], list[str], dict[str, Any], dict[str, Any], bool]:
    from training.hoodie_runtime_checkpoint_loader import load_hoodie_checkpoint_with_metadata

    runner_output_dir = output_dir / "evaluation_runner"
    readiness_path = runner_output_dir / "figure10_policy_readiness.json"
    manifest_path = runner_output_dir / "figure10_validation_manifest.json"
    summary_path = runner_output_dir / "figure10_policy_metrics_summary.json"
    config_snapshot_path = runner_output_dir / "figure10_run_config_snapshot.json"
    raw_path = runner_output_dir / "figure10_policy_metrics_raw.csv"

    evaluation_outputs_present = all(
        path.exists() for path in [readiness_path, manifest_path, summary_path, config_snapshot_path, raw_path]
    )
    readiness = _load_json(readiness_path) if readiness_path.exists() else {}
    validation_manifest = _load_json(manifest_path) if manifest_path.exists() else {}

    blockers: list[str] = []
    warnings: list[str] = []
    staged_checkpoint_summaries: list[dict[str, Any]] = []
    main_py_subprocesses_seen = True
    main_py_all_returncodes_zero = True
    runner_checkpoint_staging_verified = True
    runner_sidecars_present = True
    runner_loaded_checkpoint_from_stdout = True
    evaluation_checkpoints_runtime_loadable = True
    main_returncodes: dict[str, int | None] = {"delay": None, "drop_ratio": None}

    for regime in ("delay", "drop_ratio"):
        regime_dir = runner_output_dir / "runs" / run_id / regime / "HOODIE"
        main_returncode_path = regime_dir / "main_returncode.txt"
        stdout_path = regime_dir / "main_stdout.txt"
        if not main_returncode_path.exists():
            blockers.append("evaluation_main_returncode_missing")
            main_py_subprocesses_seen = False
            main_py_all_returncodes_zero = False
            main_returncodes[regime] = None
            runner_loaded_checkpoint_from_stdout = False
            runner_checkpoint_staging_verified = False
            runner_sidecars_present = False
            evaluation_checkpoints_runtime_loadable = False
            continue
        try:
            rc = int(main_returncode_path.read_text().strip())
        except Exception:
            rc = None
        main_returncodes[regime] = rc
        if rc is None:
            blockers.append("evaluation_main_returncode_missing")
            main_py_subprocesses_seen = False
            main_py_all_returncodes_zero = False
        elif rc != 0:
            blockers.append("evaluation_main_failed")
            main_py_all_returncodes_zero = False
        if not stdout_path.exists():
            runner_loaded_checkpoint_from_stdout = False
        else:
            stdout_text = stdout_path.read_text()
            if "model weights loaded" not in stdout_text:
                runner_loaded_checkpoint_from_stdout = False
                blockers.append("runner_checkpoint_load_not_observed")
        for agent_index in range(expected_agent_count):
            checkpoint_path = regime_dir / "logs" / f"agent_{agent_index}.pth"
            metadata_path = regime_dir / "logs" / f"agent_{agent_index}.pth.meta.json"
            staged_ok = checkpoint_path.exists() and metadata_path.exists()
            if not checkpoint_path.exists():
                blockers.append("runner_checkpoint_staging_missing")
                runner_checkpoint_staging_verified = False
            if not metadata_path.exists():
                blockers.append("runner_metadata_sidecar_missing")
                runner_sidecars_present = False
            staged_report: dict[str, Any] = {
                "regime_id": regime,
                "policy_name": "HOODIE",
                "agent_index": agent_index,
                "source_checkpoint_path": str(Path(output_dir / "training_smoke" / "trained_checkpoints" / f"agent_{agent_index}.pth")),
                "staged_checkpoint_path": str(checkpoint_path),
                "source_metadata_path": str(Path(output_dir / "training_smoke" / "trained_checkpoints" / f"agent_{agent_index}.pth.meta.json")),
                "staged_metadata_path": str(metadata_path),
                "source_torch_inspection": {},
                "staged_torch_inspection": {},
                "metadata_validation": {},
                "runner_layout_ready_for_smoke": False,
                "blockers": [],
            }
            if checkpoint_path.exists() and metadata_path.exists():
                _, source_report = load_hoodie_checkpoint_with_metadata(Path(staged_report["source_checkpoint_path"]), map_location="cpu")
                staged_model, staged_report_details = load_hoodie_checkpoint_with_metadata(checkpoint_path, map_location="cpu")
                staged_report["source_torch_inspection"] = source_report.get("checkpoint_report", {})
                staged_report["staged_torch_inspection"] = staged_report_details.get("checkpoint_report", {})
                staged_report["metadata_validation"] = staged_report_details.get("metadata_report", {})
                staged_report["blockers"] = list(staged_report_details.get("blockers", []))
                if not staged_report_details.get("runtime_loadable"):
                    evaluation_checkpoints_runtime_loadable = False
                    blockers.append("evaluation_checkpoint_not_runtime_loadable")
                if staged_model is None:
                    evaluation_checkpoints_runtime_loadable = False
                    blockers.append("evaluation_checkpoint_not_runtime_loadable")
                if staged_report_details.get("metadata_report", {}).get("official_claim_allowed") is True:
                    blockers.append("official_claim_violation")
                if staged_report_details.get("blockers"):
                    blockers.extend(str(item) for item in staged_report_details.get("blockers", []))
                if staged_report["staged_torch_inspection"].get("loadable") is not True:
                    evaluation_checkpoints_runtime_loadable = False
                staged_report["runner_layout_ready_for_smoke"] = (
                    staged_report["staged_torch_inspection"].get("loadable") is True
                    and not staged_report["metadata_validation"].get("blockers")
                    and staged_model is not None
                )
            else:
                evaluation_checkpoints_runtime_loadable = False
            staged_checkpoint_summaries.append(staged_report)
        if rc == 0 and not runner_loaded_checkpoint_from_stdout:
            blockers.append("runner_checkpoint_load_not_observed")

    if not evaluation_outputs_present:
        blockers.append("figure10_runner_output_missing")
    if not readiness:
        blockers.append("figure10_readiness_missing")
    if readiness and readiness.get("figure10_data_ready") is True:
        blockers.append("unexpected_figure10_data_ready_true")

    if validation_manifest and any(
        validation_manifest.get(field) is True for field in ("official_claim_allowed", "paper_reproduction_claim", "official_figure_claim")
    ):
        blockers.append("official_claim_violation")
    if validation_manifest.get("figure10_data_ready") is True or readiness.get("figure10_data_ready") is True:
        blockers.append("unexpected_figure10_data_ready_true")

    warnings.extend(
        [
            "bounded_smoke_checkpoint_only_not_paper_training",
            "test_mode_evaluation_only_not_official_figure10",
            "one_episode_validation_not_performance_validation",
            "figure10_remains_blocked",
            "figure9_remains_blocked_until_real_paper_scenario_action_distribution",
            "figure11_remains_blocked_until_lstm_ablation",
        ]
    )
    blockers = list(dict.fromkeys(blockers))
    all_runtime_loadable = evaluation_checkpoints_runtime_loadable and not blockers
    return all_runtime_loadable, staged_checkpoint_summaries, blockers, warnings, readiness, validation_manifest, runner_loaded_checkpoint_from_stdout


def run_smoke(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = _resolve_path(args.output_dir)
    if _repo_relative(output_dir):
        raise SystemExit("repo output refused")
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
        raise SystemExit("training-epochs must be <= 1 for this smoke")
    if args.training_episode_time <= 0:
        raise SystemExit("training-episode-time must be > 0")
    if args.training_episode_time > 3:
        raise SystemExit("training-episode-time must be <= 3 for this smoke")
    if args.validation_episodes <= 0:
        raise SystemExit("validation-episodes must be > 0")
    if args.validation_episodes > 1:
        raise SystemExit("validation-episodes must be <= 1 for this smoke")
    if args.expected_agent_count <= 0:
        raise SystemExit("expected-agent-count must be > 0")
    if args.policies != "HOODIE":
        raise SystemExit("only HOODIE is allowed in this phase")
    output_dir.mkdir(parents=True, exist_ok=True)

    blockers: list[str] = []
    warnings: list[str] = [
        "bounded_smoke_checkpoint_only_not_paper_training",
        "test_mode_evaluation_only_not_official_figure10",
        "one_episode_validation_not_performance_validation",
        "figure10_remains_blocked",
        "figure9_remains_blocked_until_real_paper_scenario_action_distribution",
        "figure11_remains_blocked_until_lstm_ablation",
    ]

    training_dir = output_dir / "training_smoke"
    training_dir.mkdir(parents=True, exist_ok=True)
    training_run_id = f"{args.run_id}_training"
    try:
        training_smoke_result = _run_training_smoke(
            output_dir=training_dir,
            training_epochs=args.training_epochs,
            training_episode_time=args.training_episode_time,
            seed=args.seed,
            run_id=training_run_id,
            expected_agent_count=args.expected_agent_count,
            trace_level=args.trace_level,
        )
    except Exception as exc:
        training_smoke_result = {
            "manifest": {},
            "report": {"blockers": [f"training_smoke_exception:{exc}"], "main_returncode": 1},
            "manifest_path": training_dir / "hoodie_bounded_small_real_training_smoke_manifest.json",
            "report_path": training_dir / "hoodie_bounded_small_real_training_smoke_report.json",
            "export_manifest_path": training_dir / "hoodie_small_real_training_export_manifest.json",
            "checkpoint_dir": training_dir / "trained_checkpoints",
        }
    training_ok, training_blockers, training_warnings = _verify_training_smoke(training_smoke_result)
    warnings.extend(training_warnings)
    blockers.extend(training_blockers)

    training_manifest = training_smoke_result.get("manifest", {})
    training_report = training_smoke_result.get("report", {})
    training_checkpoint_dir = Path(training_smoke_result["checkpoint_dir"])

    if not training_ok:
        if not Path(training_smoke_result["manifest_path"]).exists():
            blockers.append("training_smoke_manifest_missing")
        if not Path(training_smoke_result["report_path"]).exists():
            blockers.append("training_smoke_report_missing")
        blockers = list(dict.fromkeys(blockers))
        manifest = {
            "phase": "6.13",
            "scope": "hoodie_trained_checkpoint_evaluation_wiring_smoke",
            "trained_checkpoint_evaluation_wiring_smoke_run": True,
            "training_smoke_run": True,
            "training_smoke_scope": "bounded_small_real_training_smoke_only",
            "training_epochs": args.training_epochs,
            "training_episode_time": args.training_episode_time,
            "training_returncode": training_report.get("main_returncode"),
            "training_checkpoint_dir": str(training_checkpoint_dir),
            "training_runtime_loader_verified": bool(training_report.get("runtime_loader_verified")),
            "training_agent_load_model_verified": bool(training_report.get("agent_load_model_verified")),
            "evaluation_runner_called": False,
            "evaluation_runner_called_by": "run_hoodie_trained_checkpoint_evaluation_wiring_smoke.py",
            "figure10_validation_called": False,
            "figure10_validation_test_mode": True,
            "strict_readiness_used": False,
            "validation_episodes": args.validation_episodes,
            "validation_policies": ["HOODIE"],
            "evaluation_returncode": None,
            "evaluation_output_dir": str(output_dir / "evaluation_runner"),
            "main_py_called": True,
            "main_py_training_called_by_guarded_runner": True,
            "main_py_validation_called_by_figure10_runner": False,
            "simulation_rerun": True,
            "simulation_rerun_scope": "bounded_training_plus_test_mode_evaluation_wiring_smoke_only",
            "official_simulation_rerun": False,
            "checkpoint_source": "phase6_12_bounded_training_smoke_tmp_output",
            "runner_checkpoint_staging_verified": False,
            "runner_sidecars_present": False,
            "runner_loaded_checkpoint_from_stdout": False,
            "evaluation_checkpoints_runtime_loadable": False,
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
            "figure10_artifact_committed": False,
            "figure8_claim": False,
            "figure9_claim": False,
            "figure10_claim": False,
            "figure11_claim": False,
            "training_smoke_manifest_path": str(training_smoke_result["manifest_path"]),
            "training_smoke_report_path": str(training_smoke_result["report_path"]),
            "figure10_readiness_path": str(output_dir / "evaluation_runner" / "figure10_policy_readiness.json"),
            "figure10_manifest_path": str(output_dir / "evaluation_runner" / "figure10_validation_manifest.json"),
            "evaluation_hyperparameter_overrides": [],
            "loader_reports": [],
            "blockers": blockers,
            "warnings": warnings,
        }
        report = {
            "phase": "6.13",
            "scope": "hoodie_trained_checkpoint_evaluation_wiring_smoke",
            "trained_checkpoint_evaluation_wiring_smoke_run": True,
            "training_smoke_completed": False,
            "evaluation_runner_completed": False,
            "checkpoint_source": "phase6_12_bounded_training_smoke_tmp_output",
            "runner_checkpoint_staging_verified": False,
            "runner_sidecars_present": False,
            "runner_loaded_checkpoint_from_stdout": False,
            "evaluation_checkpoints_runtime_loadable": False,
            "figure10_data_ready": False,
            "official_claim_allowed": False,
            "paper_reproduction_claim": False,
            "blockers": blockers,
            "warnings": warnings,
        }
        _write_json(output_dir / "hoodie_trained_checkpoint_evaluation_wiring_smoke_manifest.json", manifest)
        _write_json(output_dir / "hoodie_trained_checkpoint_evaluation_wiring_smoke_report.json", report)
        return {"manifest": manifest, "report": report}

    hyperparameters_file, overrides = _prepare_evaluation_hyperparameters(
        output_dir=output_dir,
        training_episode_time=args.training_episode_time,
    )
    try:
        evaluation_result = _run_figure10_validation_runner(
            output_dir=output_dir,
            validation_episodes=args.validation_episodes,
            seed=args.seed,
            run_id=f"{args.run_id}_evaluation",
            hyperparameters_file=hyperparameters_file,
            checkpoint_dir=training_checkpoint_dir,
        )
    except Exception as exc:
        evaluation_result = subprocess.CompletedProcess(args=["figure10_validation.py"], returncode=1, stdout="", stderr=str(exc))

    eval_ok, staged_summaries, evaluation_blockers, evaluation_warnings, readiness, validation_manifest, runner_loaded_checkpoint_from_stdout = _collect_evaluation_wiring_report(
        output_dir=output_dir,
        run_id=f"{args.run_id}_evaluation",
        expected_agent_count=args.expected_agent_count,
    )
    warnings.extend(evaluation_warnings)
    blockers.extend(evaluation_blockers)

    if evaluation_result.returncode != 0:
        blockers.append("evaluation_runner_failed")
    if readiness and readiness.get("figure10_data_ready") is True:
        blockers.append("unexpected_figure10_data_ready_true")
    if not readiness:
        blockers.append("figure10_readiness_missing")
    if validation_manifest and any(
        validation_manifest.get(field) is True for field in ("official_claim_allowed", "paper_reproduction_claim", "official_figure_claim")
    ):
        blockers.append("official_claim_violation")
    if evaluation_result.returncode == 0 and not eval_ok:
        blockers.append("evaluation_checkpoint_not_runtime_loadable")
    blockers = list(dict.fromkeys(blockers))

    manifest = {
        "phase": "6.13",
        "scope": "hoodie_trained_checkpoint_evaluation_wiring_smoke",
        "trained_checkpoint_evaluation_wiring_smoke_run": True,
        "training_smoke_run": True,
        "training_smoke_scope": "bounded_small_real_training_smoke_only",
        "training_epochs": args.training_epochs,
        "training_episode_time": args.training_episode_time,
        "training_returncode": training_report.get("main_returncode"),
        "training_checkpoint_dir": str(training_checkpoint_dir),
        "training_runtime_loader_verified": bool(training_report.get("runtime_loader_verified")),
        "training_agent_load_model_verified": bool(training_report.get("agent_load_model_verified")),
        "evaluation_runner_called": True,
        "evaluation_runner_called_by": "run_hoodie_trained_checkpoint_evaluation_wiring_smoke.py",
        "figure10_validation_called": True,
        "figure10_validation_test_mode": True,
        "strict_readiness_used": False,
        "validation_episodes": args.validation_episodes,
        "validation_policies": ["HOODIE"],
        "evaluation_returncode": evaluation_result.returncode,
        "evaluation_output_dir": str(output_dir / "evaluation_runner"),
        "main_py_called": True,
        "main_py_training_called_by_guarded_runner": True,
        "main_py_validation_called_by_figure10_runner": True,
        "simulation_rerun": True,
        "simulation_rerun_scope": "bounded_training_plus_test_mode_evaluation_wiring_smoke_only",
        "official_simulation_rerun": False,
        "checkpoint_source": "phase6_12_bounded_training_smoke_tmp_output",
        "runner_checkpoint_staging_verified": bool(staged_summaries) and all(s.get("runner_layout_ready_for_smoke") for s in staged_summaries),
        "runner_sidecars_present": all(Path(s["staged_metadata_path"]).exists() for s in staged_summaries) if staged_summaries else False,
        "runner_loaded_checkpoint_from_stdout": runner_loaded_checkpoint_from_stdout,
        "evaluation_checkpoints_runtime_loadable": eval_ok,
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
        "figure10_artifact_committed": False,
        "figure8_claim": False,
        "figure9_claim": False,
        "figure10_claim": False,
        "figure11_claim": False,
        "training_smoke_manifest_path": str(training_smoke_result["manifest_path"]),
        "training_smoke_report_path": str(training_smoke_result["report_path"]),
        "figure10_readiness_path": str(output_dir / "evaluation_runner" / "figure10_policy_readiness.json"),
        "figure10_manifest_path": str(output_dir / "evaluation_runner" / "figure10_validation_manifest.json"),
        "evaluation_hyperparameter_overrides": overrides,
        "loader_reports": [s.get("staged_torch_inspection", {}) for s in staged_summaries],
        "staged_checkpoint_summaries": staged_summaries,
        "blockers": blockers,
        "warnings": warnings,
    }
    report = {
        "phase": "6.13",
        "scope": "hoodie_trained_checkpoint_evaluation_wiring_smoke",
        "trained_checkpoint_evaluation_wiring_smoke_run": True,
        "training_smoke_completed": True,
        "evaluation_runner_completed": evaluation_result.returncode == 0,
        "checkpoint_source": "phase6_12_bounded_training_smoke_tmp_output",
        "runner_checkpoint_staging_verified": bool(staged_summaries) and all(s.get("runner_layout_ready_for_smoke") for s in staged_summaries),
        "runner_sidecars_present": all(Path(s["staged_metadata_path"]).exists() for s in staged_summaries) if staged_summaries else False,
        "runner_loaded_checkpoint_from_stdout": runner_loaded_checkpoint_from_stdout,
        "evaluation_checkpoints_runtime_loadable": eval_ok,
        "figure10_data_ready": False,
        "official_claim_allowed": False,
        "paper_reproduction_claim": False,
        "blockers": blockers,
        "warnings": warnings,
    }
    _write_json(output_dir / "hoodie_trained_checkpoint_evaluation_wiring_smoke_manifest.json", manifest)
    _write_json(output_dir / "hoodie_trained_checkpoint_evaluation_wiring_smoke_report.json", report)
    return {"manifest": manifest, "report": report}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--training-epochs", type=int, default=1)
    parser.add_argument("--training-episode-time", type=int, default=3)
    parser.add_argument("--validation-episodes", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--run-id", default="phase6_13_trained_checkpoint_evaluation_wiring_smoke")
    parser.add_argument("--expected-agent-count", type=int, default=20)
    parser.add_argument("--trace-level", default="summary")
    parser.add_argument("--policies", default="HOODIE")
    parser.add_argument("--allow-trained-checkpoint-evaluation-wiring-smoke", action="store_true")
    parser.add_argument("--allow-bounded-training-smoke", action="store_true")
    parser.add_argument("--allow-figure10-validation-test-mode", action="store_true")
    parser.add_argument("--allow-main-py-training-execution", action="store_true")
    parser.add_argument("--allow-training-checkpoint-export", action="store_true")
    args = parser.parse_args(argv)

    output_dir = _resolve_path(args.output_dir)
    if _repo_relative(output_dir):
        raise SystemExit("repo output refused")
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
