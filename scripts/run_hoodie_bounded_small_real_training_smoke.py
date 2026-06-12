from __future__ import annotations

import argparse
import json
import os
import pickle
import subprocess
import sys
import tempfile
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


def _load_base_hyperparameters() -> dict[str, Any]:
    return _load_json(ROOT / "hyperparameters" / "hyperparameters.json")


def _write_empty_config(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# intentionally empty\n")


def _prepare_smoke_hyperparameters(base_hyperparameters: dict[str, Any], episode_time: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    hyperparameters = json.loads(json.dumps(base_hyperparameters))
    overrides: list[dict[str, Any]] = []

    def _apply(key: str, value: Any) -> None:
        if key in hyperparameters:
            hyperparameters[key] = value
            overrides.append({"key": key, "value": value})

    _apply("decision_makers", "HOODIE")
    _apply("episode_time", int(episode_time))
    if "batch_size" in hyperparameters:
        _apply("batch_size", 1)
    if "memory_size" in hyperparameters:
        _apply("memory_size", max(20, int(hyperparameters["memory_size"])))
    if isinstance(hyperparameters.get("task_arrive_probabilities"), list):
        _apply("task_arrive_probabilities", [1.0 for _ in hyperparameters["task_arrive_probabilities"]])
    return hyperparameters, overrides


def _environment_dimensions(hyperparameters: dict[str, Any]) -> tuple[int, int]:
    from environment import Environment

    env = Environment(
        number_of_servers=hyperparameters["number_of_servers"],
        private_cpu_capacities=hyperparameters["private_cpu_capacities"],
        public_cpu_capacities=hyperparameters["public_cpu_capacities"],
        connection_matrix=hyperparameters["connection_matrix"],
        cloud_computational_capacity=hyperparameters["cloud_computational_capacity"],
        episode_time=hyperparameters["episode_time"],
        static_frequency=hyperparameters["static_frequency"],
        task_arrive_probabilities=hyperparameters["task_arrive_probabilities"],
        task_size_mins=hyperparameters["task_size_mins"],
        task_size_maxs=hyperparameters["task_size_maxs"],
        task_size_distributions=hyperparameters["task_size_distributions"],
        timeout_delay_mins=hyperparameters["timeout_delay_mins"],
        timeout_delay_maxs=hyperparameters["timeout_delay_maxs"],
        timeout_delay_distributions=hyperparameters["timeout_delay_distributions"],
        priotiry_mins=hyperparameters["priotiry_mins"],
        priotiry_maxs=hyperparameters["priotiry_maxs"],
        priotiry_distributions=hyperparameters["priotiry_distributions"],
        computational_density_mins=hyperparameters["computational_density_mins"],
        computational_density_maxs=hyperparameters["computational_density_maxs"],
        computational_density_distributions=hyperparameters["computational_density_distributions"],
        drop_penalty_mins=hyperparameters["drop_penalty_mins"],
        drop_penalty_maxs=hyperparameters["drop_penalty_maxs"],
        drop_penalty_distributions=hyperparameters["drop_penalty_distributions"],
    )
    state_dim, _, action_count = env.get_server_dimensions(0)
    return int(state_dim), int(action_count)


def _run_main_training(*, output_dir: Path, seed: int, epochs: int, trace_level: str, hyperparameters_file: Path, config_file: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"
    env["MPLCONFIGDIR"] = str(output_dir / "cache" / "mplconfig")
    env["XDG_CACHE_HOME"] = str(output_dir / "cache" / "xdg")
    env["PYTHONUNBUFFERED"] = "1"
    cmd = [
        sys.executable,
        "main.py",
        "--config",
        str(config_file),
        "--log_folder",
        str(output_dir / "main_logs"),
        "--hyperparameters_file",
        str(hyperparameters_file),
        "--epochs",
        str(epochs),
        "--trace_output_dir",
        str(output_dir / "traces"),
        "--seed",
        str(seed),
        "--trace_level",
        trace_level,
        "--export_trained_checkpoints",
        "--checkpoint_export_dir",
        str(output_dir / "trained_checkpoints"),
        "--checkpoint_export_format",
        "pytorch_model_file",
        "--allow_training_checkpoint_export",
        "--checkpoint_export_manifest",
        str(output_dir / "hoodie_small_real_training_export_manifest.json"),
    ]
    return subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, check=False)


def _build_agent_for_load_check(*, checkpoint_path: Path, scheduler_file: Path, state_dim: int, action_count: int):
    import torch

    from decision_makers.agent import Agent

    return Agent(
        id=0,
        state_dimensions=state_dim,
        lstm_shape=state_dim,
        number_of_actions=action_count,
        hidden_layers=[8],
        lstm_layers=1,
        lstm_time_step=1,
        dropout_rate=0.0,
        device="cpu",
        epsilon=0.0,
        epsilon_decrement=0.0,
        epsilon_end=0.0,
        gamma=0.99,
        learning_rate=1e-6,
        scheduler_file=str(scheduler_file),
        loss_function=torch.nn.MSELoss,
        optimizer=torch.optim.Adam,
        checkpoint_folder=str(checkpoint_path),
        save_model_frequency=10,
        update_weight_percentage=1.0,
        memory_size=10,
        batch_size=2,
        replace_target_iter=5,
    )


def _verify_trained_checkpoints(checkpoint_dir: Path, agent_count: int) -> tuple[bool, list[dict[str, Any]], list[str], list[str]]:
    from training.hoodie_runtime_checkpoint_loader import load_hoodie_checkpoint_with_metadata

    reports: list[dict[str, Any]] = []
    accepted_formats: set[str] = set()
    rejected_formats: set[str] = set()
    blockers: list[str] = []
    all_ok = True

    for agent_index in range(agent_count):
        checkpoint_path = checkpoint_dir / f"agent_{agent_index}.pth"
        model, report = load_hoodie_checkpoint_with_metadata(checkpoint_path, map_location="cpu")
        reports.append(report)
        accepted_formats.add(str(report.get("checkpoint_report", {}).get("format") or "unknown"))
        if not report.get("runtime_loadable"):
            all_ok = False
            blockers.append(f"generated_checkpoint_not_runtime_loadable: agent_{agent_index}")
            rejected_formats.add(str(report.get("checkpoint_report", {}).get("format") or "unknown"))
        if model is None:
            blockers.append(f"generated_checkpoint_missing_model: agent_{agent_index}")
    return all_ok, reports, sorted(accepted_formats), sorted(rejected_formats)


def _verify_agent_load_model(checkpoint_path: Path, scheduler_file: Path, state_dim: int, action_count: int) -> tuple[bool, dict[str, Any]]:
    import torch

    agent = _build_agent_for_load_check(
        checkpoint_path=checkpoint_path,
        scheduler_file=scheduler_file,
        state_dim=state_dim,
        action_count=action_count,
    )
    return bool(agent.last_checkpoint_load_report.get("runtime_loadable")) and isinstance(agent.Q_eval_network, torch.nn.Module), agent.last_checkpoint_load_report


def run_smoke(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = _resolve_path(args.output_dir)
    if _repo_relative(output_dir):
        raise SystemExit("repo output refused")
    if not args.allow_bounded_small_real_training_smoke:
        raise SystemExit("--allow-bounded-small-real-training-smoke is required")
    if not args.allow_main_py_training_execution:
        raise SystemExit("--allow-main-py-training-execution is required")
    if not args.allow_training_checkpoint_export:
        raise SystemExit("--allow-training-checkpoint-export is required")
    if args.epochs <= 0:
        raise SystemExit("epochs must be > 0")
    if args.epochs > 1:
        raise SystemExit("epochs must be <= 1 for this smoke")
    if args.episode_time <= 0:
        raise SystemExit("episode_time must be > 0")
    if args.episode_time > 3:
        raise SystemExit("episode_time must be <= 3 for this smoke")
    if args.expected_agent_count <= 0:
        raise SystemExit("expected-agent-count must be > 0")
    if args.checkpoint_format != "pytorch_model_file":
        raise SystemExit("unsupported checkpoint format")

    output_dir.mkdir(parents=True, exist_ok=True)
    base_hyperparameters = _load_base_hyperparameters()
    smoke_hyperparameters, smoke_overrides = _prepare_smoke_hyperparameters(base_hyperparameters, args.episode_time)
    config_file = output_dir / "inputs" / "config_phase6_12_empty.yml"
    hyperparameters_file = output_dir / "inputs" / "hyperparameters_phase6_12_bounded_small_real_training_smoke.json"
    _write_empty_config(config_file)
    _write_json(hyperparameters_file, smoke_hyperparameters)

    main_result = _run_main_training(
        output_dir=output_dir,
        seed=args.seed,
        epochs=args.epochs,
        trace_level=args.trace_level,
        hyperparameters_file=hyperparameters_file,
        config_file=config_file,
    )
    (output_dir / "main_stdout.txt").write_text(main_result.stdout)
    (output_dir / "main_stderr.txt").write_text(main_result.stderr)
    (output_dir / "main_returncode.txt").write_text(str(main_result.returncode))

    export_manifest_path = output_dir / "hoodie_small_real_training_export_manifest.json"
    trained_checkpoint_dir = output_dir / "trained_checkpoints"
    main_logs_dir = output_dir / "main_logs"
    traces_dir = output_dir / "traces"
    runtime_loader_verified = False
    agent_load_model_verified = False
    trained_checkpoint_load_reports: list[dict[str, Any]] = []
    load_model_report: dict[str, Any] = {}
    expected_agent_count = int(args.expected_agent_count)
    export_manifest = _load_json(export_manifest_path) if export_manifest_path.exists() else {}

    all_runtime_loadable = False
    if main_result.returncode == 0 and trained_checkpoint_dir.exists():
        all_runtime_loadable, trained_checkpoint_load_reports, accepted_formats, rejected_formats = _verify_trained_checkpoints(
            trained_checkpoint_dir, expected_agent_count
        )
        try:
            scheduler_file = main_logs_dir / "scheduler.pth"
            first_checkpoint = trained_checkpoint_dir / "agent_0.pth"
            if scheduler_file.exists() and first_checkpoint.exists():
                state_dim, action_count = _environment_dimensions(smoke_hyperparameters)
                agent_load_model_verified, load_model_report = _verify_agent_load_model(
                    first_checkpoint,
                    scheduler_file,
                    state_dim=state_dim,
                    action_count=action_count,
                )
        except Exception as exc:  # pragma: no cover - defensive
            agent_load_model_verified = False
            load_model_report = {"blockers": [str(exc)]}

    figure10_runner_outputs_present = False
    for name in [
        "figure10_policy_metrics_raw.csv",
        "figure10_policy_metrics_summary.json",
        "figure10_policy_readiness.json",
        "figure10_run_config_snapshot.json",
        "figure10_validation_manifest.json",
    ]:
        if (output_dir / "figure10_runner" / name).exists():
            figure10_runner_outputs_present = True
    blockers: list[str] = []
    warnings = [
        "bounded_small_real_training_smoke_only",
        "generated_checkpoints_are_tmp_only",
    ]
    if main_result.returncode != 0:
        blockers.append("main_py_failed")
    if not export_manifest_path.exists():
        blockers.append("training_checkpoint_export_manifest_missing")
    if not trained_checkpoint_dir.exists():
        blockers.append("trained_checkpoint_dir_missing")
    if not all_runtime_loadable:
        blockers.append("generated_checkpoint_not_runtime_loadable")
    if not agent_load_model_verified:
        blockers.append("agent_load_model_verification_failed")
    if figure10_runner_outputs_present:
        blockers.append("unexpected_figure10_outputs_present")
    if export_manifest and export_manifest.get("blockers"):
        blockers.extend(f"export_manifest:{item}" for item in export_manifest.get("blockers", []))
    blockers = list(dict.fromkeys(blockers))

    manifest = {
        "phase": "6.12",
        "scope": "hoodie_bounded_small_real_training_smoke_execution",
        "bounded_small_real_training_smoke_run": True,
        "main_py_called": True,
        "main_py_called_by": "run_hoodie_bounded_small_real_training_smoke.py",
        "main_py_training_execution_run": True,
        "training_execution_run": True,
        "simulation_rerun": False,
        "official_training_run": False,
        "full_training_run": False,
        "paper_training_run": False,
        "paper_grade_5000_episode_training_run": False,
        "official_validation_run": False,
        "official_200_episode_validation_run": False,
        "official_figure_claims_made": False,
        "official_claim_allowed": False,
        "checkpoint_export_requested": True,
        "checkpoint_export_performed": bool(export_manifest),
        "checkpoint_export_dir": str(trained_checkpoint_dir),
        "checkpoint_export_format": args.checkpoint_format,
        "main_logs_dir": str(main_logs_dir),
        "traces_dir": str(traces_dir),
        "export_manifest_path": str(export_manifest_path),
        "main_stdout_path": str(output_dir / "main_stdout.txt"),
        "main_stderr_path": str(output_dir / "main_stderr.txt"),
        "main_returncode_path": str(output_dir / "main_returncode.txt"),
        "episodes": args.epochs,
        "episode_time": args.episode_time,
        "seed": args.seed,
        "run_id": args.run_id,
        "expected_agent_count": expected_agent_count,
        "actual_agent_count": expected_agent_count,
        "smoke_hyperparameter_overrides": smoke_overrides,
        "trained_checkpoint_load_reports": trained_checkpoint_load_reports,
        "runtime_loader_accepted_formats": accepted_formats if main_result.returncode == 0 and trained_checkpoint_dir.exists() else [],
        "runtime_loader_rejected_formats": rejected_formats if main_result.returncode == 0 and trained_checkpoint_dir.exists() else [],
        "runtime_loader_verified": all_runtime_loadable,
        "agent_load_model_verified": agent_load_model_verified,
        "agent_load_model_report": load_model_report,
        "checkpoint_artifact_committed": False,
        "model_artifact_committed": False,
        "figure10_validation_called": False,
        "figure10_data_ready": False,
        "figure10_runner_outputs_present": figure10_runner_outputs_present,
        "figure8_claim": False,
        "figure9_claim": False,
        "figure10_claim": False,
        "figure11_claim": False,
        "main_returncode": main_result.returncode,
        "blockers": blockers,
        "warnings": warnings,
    }
    report = {
        "phase": "6.12",
        "scope": "hoodie_bounded_small_real_training_smoke_execution",
        "bounded_small_real_training_smoke_run": True,
        "main_py_called": True,
        "main_py_called_by": "run_hoodie_bounded_small_real_training_smoke.py",
        "main_py_training_execution_run": True,
        "training_execution_run": True,
        "simulation_rerun": False,
        "official_training_run": False,
        "full_training_run": False,
        "paper_training_run": False,
        "paper_grade_5000_episode_training_run": False,
        "official_validation_run": False,
        "official_200_episode_validation_run": False,
        "official_figure_claims_made": False,
        "official_claim_allowed": False,
        "checkpoint_export_requested": True,
        "checkpoint_export_performed": bool(export_manifest),
        "checkpoint_export_dir": str(trained_checkpoint_dir),
        "checkpoint_export_format": args.checkpoint_format,
        "main_logs_dir": str(main_logs_dir),
        "traces_dir": str(traces_dir),
        "export_manifest_path": str(export_manifest_path),
        "main_stdout_path": str(output_dir / "main_stdout.txt"),
        "main_stderr_path": str(output_dir / "main_stderr.txt"),
        "main_returncode_path": str(output_dir / "main_returncode.txt"),
        "validation_execution_run": False,
        "episodes": args.epochs,
        "episode_time": args.episode_time,
        "seed": args.seed,
        "run_id": args.run_id,
        "expected_agent_count": expected_agent_count,
        "actual_agent_count": expected_agent_count,
        "smoke_hyperparameter_overrides": smoke_overrides,
        "runtime_loader_accepted_formats": accepted_formats if main_result.returncode == 0 and trained_checkpoint_dir.exists() else [],
        "runtime_loader_rejected_formats": rejected_formats if main_result.returncode == 0 and trained_checkpoint_dir.exists() else [],
        "runtime_loader_verified": all_runtime_loadable,
        "agent_load_model_verified": agent_load_model_verified,
        "main_returncode": main_result.returncode,
        "main_stdout_contains_model_weights_loaded": "model weights loaded" in (output_dir / "main_stdout.txt").read_text() if (output_dir / "main_stdout.txt").exists() else False,
        "generated_checkpoints": [str(p) for p in sorted(trained_checkpoint_dir.glob("agent_*.pth"))],
        "figure10_runner_outputs_present": figure10_runner_outputs_present,
        "figure10_data_ready": False,
        "figure8_claim": False,
        "figure9_claim": False,
        "figure10_claim": False,
        "figure11_claim": False,
        "blockers": blockers,
        "warnings": warnings,
    }

    _write_json(output_dir / "hoodie_bounded_small_real_training_smoke_manifest.json", manifest)
    _write_json(output_dir / "hoodie_bounded_small_real_training_smoke_report.json", report)
    return {"manifest": manifest, "report": report}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--episode-time", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--run-id", default="phase6_12_bounded_small_real_training_smoke")
    parser.add_argument("--expected-agent-count", type=int, default=20)
    parser.add_argument("--trace-level", default="summary")
    parser.add_argument("--checkpoint-format", default="pytorch_model_file")
    parser.add_argument("--allow-bounded-small-real-training-smoke", action="store_true")
    parser.add_argument("--allow-main-py-training-execution", action="store_true")
    parser.add_argument("--allow-training-checkpoint-export", action="store_true")
    args = parser.parse_args()

    output_dir = _resolve_path(args.output_dir)
    if _repo_relative(output_dir):
        raise SystemExit("repo output refused")
    if not args.allow_bounded_small_real_training_smoke:
        raise SystemExit("--allow-bounded-small-real-training-smoke is required")
    if not args.allow_main_py_training_execution:
        raise SystemExit("--allow-main-py-training-execution is required")
    if not args.allow_training_checkpoint_export:
        raise SystemExit("--allow-training-checkpoint-export is required")
    if args.epochs <= 0:
        raise SystemExit("epochs must be > 0")
    if args.epochs > 1:
        raise SystemExit("epochs must be <= 1 for this smoke")
    if args.episode_time <= 0:
        raise SystemExit("episode_time must be > 0")
    if args.episode_time > 3:
        raise SystemExit("episode_time must be <= 3 for this smoke")
    if args.expected_agent_count <= 0:
        raise SystemExit("expected-agent-count must be > 0")
    if args.checkpoint_format != "pytorch_model_file":
        raise SystemExit("unsupported checkpoint format")

    result = run_smoke(args)
    blockers = result["manifest"].get("blockers", []) or result["report"].get("blockers", [])
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
