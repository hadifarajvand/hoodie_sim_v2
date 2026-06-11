from __future__ import annotations

import argparse
import json
import os
import pickle
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
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


def _make_scheduler_pickle(path: Path) -> None:
    from lr_schedulers import constant

    with path.open("wb") as f:
        pickle.dump(constant, f)


def _run_tiny_optimizer_step(
    *,
    seed: int,
    state_dim: int,
    action_count: int,
    hidden_layers: list[int],
    lstm_layers: int,
    checkpoint_format: str,
    synthetic_steps: int,
) -> tuple[Any, list[float]]:
    import torch

    from decision_makers.agent import DeepQNetwork

    torch.manual_seed(seed)
    model = DeepQNetwork(
        state_dimensions=state_dim,
        lstm_input_shape=state_dim,
        lstm_output_shape=state_dim,
        number_of_actions=action_count,
        hidden_layers=hidden_layers,
        lstm_layers=lstm_layers,
        dueling=True,
        dropout_rate=0.0,
    ).cpu()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_values: list[float] = []
    for _ in range(synthetic_steps):
        state = torch.randn((1, state_dim), dtype=torch.float32)
        lstm_input = torch.randn((1, 1, state_dim), dtype=torch.float32)
        target = torch.randn((1, action_count), dtype=torch.float32)
        prediction = model(state, lstm_input)
        loss = torch.nn.functional.mse_loss(prediction, target)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        loss_values.append(float(loss.item()))
    model.eval()
    if checkpoint_format == "pytorch_model_file":
        return model, loss_values
    return {
        "state_dict": model.state_dict(),
        "model_class": "DeepQNetwork",
        "state_dim": state_dim,
        "lstm_input_shape": state_dim,
        "lstm_output_shape": state_dim,
        "number_of_actions": action_count,
        "hidden_layers": hidden_layers,
        "lstm_layers": lstm_layers,
        "dueling": True,
        "dropout_rate": 0.0,
        "seed": seed,
        "synthetic_steps": 1,
    }, loss_values


def _build_controlled_trained_checkpoints(
    *,
    output_dir: Path,
    seed: int,
    checkpoint_format: str,
    agent_count: int,
    synthetic_steps: int,
    episodes: int,
) -> tuple[Path, list[dict[str, Any]], list[float], list[str]]:
    import torch
    from environment.environment import Environment
    from decision_makers.agent import DeepQNetwork
    from training.hoodie_checkpoint_interop import write_checkpoint_metadata_sidecar

    base_hyperparameters = _load_base_hyperparameters()
    checkpoint_dir = output_dir / "controlled_trained_checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    original_reset = Environment.reset

    def _noop_reset(self):  # pragma: no cover - defensive helper
        return None

    Environment.reset = _noop_reset
    warnings: list[str] = []
    losses: list[list[float]] = []
    summaries: list[dict[str, Any]] = []
    try:
        env = Environment(
            static_frequency=base_hyperparameters["static_frequency"],
            number_of_servers=agent_count,
            private_cpu_capacities=base_hyperparameters["private_cpu_capacities"],
            public_cpu_capacities=base_hyperparameters["public_cpu_capacities"],
            connection_matrix=base_hyperparameters["connection_matrix"],
            cloud_computational_capacity=base_hyperparameters["cloud_computational_capacity"],
            episode_time=base_hyperparameters["episode_time"],
            task_arrive_probabilities=base_hyperparameters["task_arrive_probabilities"],
            task_size_mins=base_hyperparameters["task_size_mins"],
            task_size_maxs=base_hyperparameters["task_size_maxs"],
            task_size_distributions=base_hyperparameters["task_size_distributions"],
            timeout_delay_mins=base_hyperparameters["timeout_delay_mins"],
            timeout_delay_maxs=base_hyperparameters["timeout_delay_maxs"],
            timeout_delay_distributions=base_hyperparameters["timeout_delay_distributions"],
            priotiry_mins=base_hyperparameters["priotiry_mins"],
            priotiry_maxs=base_hyperparameters["priotiry_maxs"],
            priotiry_distributions=base_hyperparameters["priotiry_distributions"],
            computational_density_mins=base_hyperparameters["computational_density_mins"],
            computational_density_maxs=base_hyperparameters["computational_density_maxs"],
            computational_density_distributions=base_hyperparameters["computational_density_distributions"],
            drop_penalty_mins=base_hyperparameters["drop_penalty_mins"],
            drop_penalty_maxs=base_hyperparameters["drop_penalty_maxs"],
            drop_penalty_distributions=base_hyperparameters["drop_penalty_distributions"],
        )
        env.tasks = [None for _ in range(agent_count)]
        for agent_index in range(agent_count):
            state_dim, lstm_shape, action_count = env.get_server_dimensions(agent_index)
            checkpoint_seed = seed + agent_index
            payload, loss_values = _run_tiny_optimizer_step(
                seed=checkpoint_seed,
                state_dim=state_dim,
                action_count=action_count,
                hidden_layers=list(base_hyperparameters["hidden_layers"]),
                lstm_layers=int(base_hyperparameters["lstm_layers"]),
                checkpoint_format=checkpoint_format,
                synthetic_steps=synthetic_steps,
            )
            losses.append(loss_values)
            checkpoint_path = checkpoint_dir / f"agent_{agent_index}.pth"
            if checkpoint_format == "pytorch_model_file":
                torch.save(payload, checkpoint_path)
            else:
                torch.save(payload, checkpoint_path)
            metadata = {
                "policy_name": "HOODIE",
                "checkpoint_format": checkpoint_format,
                "created_by": "run_hoodie_controlled_trained_checkpoint_loading_smoke.py",
                "phase": "6.9",
                "seed": checkpoint_seed,
                "agent_index": agent_index,
                "agent_count": agent_count,
                "state_dim": state_dim,
                "action_count": action_count,
                "synthetic_training_step_count": 1,
                "controlled_training_smoke": True,
                "trained_checkpoint": True,
                "trained_checkpoint_scope": "synthetic_controlled_smoke_only",
                "paper_training_run": False,
                "full_training_run": False,
                "official_claim_allowed": False,
                "paper_reproduction_claim": False,
                "validation_required_before_official_claim": True,
                "paper_contract_ref": "config/paper_table4_contract.json",
                "episode_count": episodes,
            }
            write_checkpoint_metadata_sidecar(checkpoint_path, metadata)
            summaries.append(
                {
                    "agent_index": agent_index,
                    "checkpoint_path": str(checkpoint_path),
                    "metadata_path": str(checkpoint_path.with_name(checkpoint_path.name + ".meta.json")),
                    "state_dim": state_dim,
                    "action_count": action_count,
                    "loss_values": loss_values,
                }
            )
    finally:
        Environment.reset = original_reset
    return checkpoint_dir, summaries, losses, warnings


def _verify_runtime_loadability(checkpoint_dir: Path, agent_count: int) -> tuple[bool, list[str], list[str], list[dict[str, Any]]]:
    from training.hoodie_runtime_checkpoint_loader import load_hoodie_checkpoint_with_metadata

    accepted: set[str] = set()
    rejected: set[str] = set()
    reports: list[dict[str, Any]] = []
    all_ok = True
    for agent_index in range(agent_count):
        checkpoint_path = checkpoint_dir / f"agent_{agent_index}.pth"
        _, report = load_hoodie_checkpoint_with_metadata(checkpoint_path, map_location="cpu")
        reports.append(report)
        if not report.get("runtime_loadable"):
            all_ok = False
        if report.get("checkpoint_report", {}).get("format"):
            accepted.add(str(report["checkpoint_report"]["format"]))
        if not report.get("runtime_loadable"):
            rejected.add(str(report.get("checkpoint_report", {}).get("format") or "unknown"))
    return all_ok, sorted(accepted), sorted(rejected), reports


def _make_agent_scheduler(path: Path) -> None:
    _make_scheduler_pickle(path)


def _verify_agent_load_model(checkpoint_path: Path, tmp_path: Path) -> tuple[bool, str]:
    import torch

    from decision_makers.agent import Agent

    scheduler = tmp_path / "scheduler.pth"
    _make_agent_scheduler(scheduler)
    agent = Agent(
        id=0,
        state_dimensions=6,
        lstm_shape=6,
        number_of_actions=3,
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
        scheduler_file=str(scheduler),
        loss_function=torch.nn.MSELoss,
        optimizer=torch.optim.Adam,
        checkpoint_folder=str(checkpoint_path),
        save_model_frequency=10,
        update_weight_percentage=1.0,
        memory_size=10,
        batch_size=2,
        replace_target_iter=5,
    )
    return isinstance(agent.Q_eval_network, torch.nn.Module) and bool(agent.last_checkpoint_load_report.get("runtime_loadable")), json.dumps(agent.last_checkpoint_load_report, sort_keys=True)


def _run_figure10_runner(
    *,
    output_dir: Path,
    checkpoint_dir: Path,
    episodes: int,
    seed: int,
    run_id: str,
    hyperparameters_file: Path,
) -> subprocess.CompletedProcess[str]:
    runner_output_dir = output_dir / "figure10_runner"
    cache_dir = output_dir / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"
    env["MPLCONFIGDIR"] = str(cache_dir / "mplconfig")
    env["XDG_CACHE_HOME"] = str(cache_dir / "xdg")
    cmd = [
        str(ROOT / ".venvmac" / "bin" / "python"),
        "figure10_validation.py",
        "--output-dir",
        str(runner_output_dir),
        "--episodes",
        str(episodes),
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


def run_smoke(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = _resolve_path(args.output_dir)
    if _repo_relative(output_dir):
        raise SystemExit("repo output refused")
    if not args.allow_controlled_trained_checkpoint_smoke:
        raise SystemExit("--allow-controlled-trained-checkpoint-smoke is required")
    if not args.allow_synthetic_training_step:
        raise SystemExit("--allow-synthetic-training-step is required")
    if args.episodes <= 0:
        raise SystemExit("episodes must be > 0")
    if args.episodes > 2:
        raise SystemExit("episodes must be <= 2 for smoke")
    if args.synthetic_steps <= 0:
        raise SystemExit("synthetic_steps must be > 0")
    if args.synthetic_steps > 2:
        raise SystemExit("synthetic_steps must be <= 2 for smoke")
    if args.checkpoint_format not in {"pytorch_state_dict_payload", "pytorch_model_file"}:
        raise SystemExit("unsupported checkpoint format")

    output_dir.mkdir(parents=True, exist_ok=True)
    base_hyperparameters = _load_base_hyperparameters()
    smoke_hyperparameters = json.loads(json.dumps(base_hyperparameters))
    smoke_hyperparameters["episode_time"] = min(int(smoke_hyperparameters.get("episode_time", 100)), 3)
    hyperparameters_file = output_dir / "inputs" / "hyperparameters_phase6_9_controlled_trained_checkpoint_smoke.json"
    _write_json(hyperparameters_file, smoke_hyperparameters)

    checkpoint_dir, fixture_summaries, losses, warnings = _build_controlled_trained_checkpoints(
        output_dir=output_dir,
        seed=args.seed,
        checkpoint_format=args.checkpoint_format,
        agent_count=int(base_hyperparameters["number_of_servers"]),
        synthetic_steps=args.synthetic_steps,
        episodes=args.episodes,
    )
    runtime_ok, accepted_formats, rejected_formats, loader_reports = _verify_runtime_loadability(
        checkpoint_dir, int(base_hyperparameters["number_of_servers"])
    )
    agent_load_model_ok, agent_load_report = _verify_agent_load_model(checkpoint_dir / "agent_0.pth", output_dir)

    runner_result = _run_figure10_runner(
        output_dir=output_dir,
        checkpoint_dir=checkpoint_dir,
        episodes=args.episodes,
        seed=args.seed,
        run_id=args.run_id,
        hyperparameters_file=hyperparameters_file,
    )

    runner_output_dir = output_dir / "figure10_runner"
    readiness_path = runner_output_dir / "figure10_policy_readiness.json"
    manifest_path = runner_output_dir / "figure10_validation_manifest.json"
    summary_path = runner_output_dir / "figure10_policy_metrics_summary.json"
    config_snapshot_path = runner_output_dir / "figure10_run_config_snapshot.json"
    raw_path = runner_output_dir / "figure10_policy_metrics_raw.csv"
    runner_outputs_present = all(
        path.exists() for path in [readiness_path, manifest_path, summary_path, config_snapshot_path, raw_path]
    )
    readiness = _load_json(readiness_path) if readiness_path.exists() else {}
    validation_manifest = _load_json(manifest_path) if manifest_path.exists() else {}
    main_returncodes = {"delay": None, "drop_ratio": None}
    main_returncode_files = {
        regime: runner_output_dir / "runs" / args.run_id / regime / "HOODIE" / "main_returncode.txt"
        for regime in ("delay", "drop_ratio")
    }
    main_py_subprocesses_seen = True
    main_py_all_returncodes_zero = True
    main_returncodes_seen = True
    runner_loaded_checkpoint_from_stdout = True
    runner_sidecars_present = True
    for regime, path in main_returncode_files.items():
        if not path.exists():
            main_py_subprocesses_seen = False
            main_py_all_returncodes_zero = False
            main_returncodes_seen = False
            runner_loaded_checkpoint_from_stdout = False
            runner_sidecars_present = False
            continue
        try:
            rc = int(path.read_text().strip())
        except Exception:
            rc = None
        main_returncodes[regime] = rc
        regime_dir = path.parent
        stdout_path = regime_dir / "main_stdout.txt"
        if not stdout_path.exists():
            runner_loaded_checkpoint_from_stdout = False
        else:
            stdout_text = stdout_path.read_text()
            if "model weights loaded" not in stdout_text:
                runner_loaded_checkpoint_from_stdout = False
        for agent_index in range(int(base_hyperparameters["number_of_servers"])):
            sidecar = regime_dir / "logs" / f"agent_{agent_index}.pth.meta.json"
            checkpoint = regime_dir / "logs" / f"agent_{agent_index}.pth"
            if not sidecar.exists() or not checkpoint.exists():
                runner_sidecars_present = False
        if rc is None:
            main_py_subprocesses_seen = False
            main_py_all_returncodes_zero = False
            main_returncodes_seen = False
        elif rc != 0:
            main_py_all_returncodes_zero = False
    figure10_data_ready = bool(readiness.get("figure10_data_ready", False))
    blockers: list[str] = []
    warnings.extend(
        [
            "trained_checkpoint_is_synthetic_controlled_smoke_only",
            "runner_outputs_are_non_official_smoke_outputs",
        ]
    )
    if args.synthetic_steps <= 0:
        blockers.append("synthetic_training_step_not_applied")
    if not runtime_ok:
        blockers.append("generated_checkpoint_not_runtime_loadable")
    if not agent_load_model_ok:
        blockers.append("agent_load_model_verification_failed")
    if runner_result.returncode != 0:
        blockers.append("figure10_runner_execution_failed")
    if not main_returncodes_seen:
        blockers.append("main_returncode_missing")
    if not main_py_all_returncodes_zero:
        blockers.append("main_py_failed")
    if not runner_sidecars_present:
        blockers.append("runner_checkpoint_sidecar_missing")
    if not runner_loaded_checkpoint_from_stdout:
        blockers.append("runner_checkpoint_load_not_observed")
    if figure10_data_ready:
        blockers.append("unexpected_official_readiness_true_in_smoke")
    if args.episodes != 1:
        blockers.append("unexpected_validation_episode_count")
    blockers = list(dict.fromkeys(blockers))

    manifest = {
        "phase": "6.9",
        "run_type": "controlled_trained_checkpoint_loading_smoke",
        "official_claim_allowed": False,
        "paper_reproduction_claim": False,
        "official_figure_claim": False,
        "official_validation_run": False,
        "official_200_episode_validation_run": False,
        "paper_training_run": False,
        "full_training_run": False,
        "controlled_synthetic_training_smoke_run": True,
        "synthetic_training_step_count": args.synthetic_steps,
        "trained_checkpoint_created": True,
        "trained_checkpoint_scope": "synthetic_controlled_smoke_only",
        "checkpoint_artifact_committed": False,
        "main_py_called": True,
        "main_py_called_only_through_validation_runner": True,
        "figure10_validation_entrypoint_called": True,
        "test_mode": True,
        "episodes": args.episodes,
        "policies": ["HOODIE"],
        "checkpoint_format": args.checkpoint_format,
        "output_dir": str(output_dir),
        "controlled_trained_checkpoint_dir": str(checkpoint_dir),
        "figure10_runner_output_dir": str(runner_output_dir),
        "all_agents_runtime_loadable": runtime_ok,
        "agent_load_model_verified": agent_load_model_ok,
        "runner_loaded_checkpoint_from_stdout": runner_loaded_checkpoint_from_stdout,
        "runner_sidecars_present": runner_sidecars_present,
        "figure10_data_ready": False,
        "non_official_runner_outputs_created": bool(runner_outputs_present),
        "official_figure10_outputs_created": False,
        "figure8_claim": False,
        "figure9_claim": False,
        "figure10_claim": False,
        "figure11_claim": False,
        "runner_returncode": runner_result.returncode,
        "main_returncodes": main_returncodes,
        "warnings": warnings,
        "blockers": blockers,
        "runtime_loader_accepted_formats": accepted_formats,
        "runtime_loader_rejected_formats": rejected_formats,
        "runtime_loader_reports": loader_reports,
        "checkpoint_generation_summaries": fixture_summaries,
        "loss_values": losses,
    }
    report = {
        "phase": "6.9",
        "controlled_trained_checkpoint_loading_smoke_run": True,
        "controlled_synthetic_training_smoke_run": True,
        "paper_training_run": False,
        "full_training_run": False,
        "official_validation_run": False,
        "official_200_episode_validation_run": False,
        "official_claim_allowed": False,
        "paper_reproduction_claim": False,
        "figure10_claim": False,
        "figure10_data_ready": False,
        "trained_checkpoint_created": True,
        "trained_checkpoint_scope": "synthetic_controlled_smoke_only",
        "runtime_loader_accepted_checkpoint": runtime_ok,
        "agent_load_model_verified": agent_load_model_ok,
        "runner_completed": runner_result.returncode == 0,
        "main_py_subprocesses_seen": main_py_subprocesses_seen,
        "main_py_all_returncodes_zero": main_py_all_returncodes_zero,
        "runner_loaded_checkpoint_from_stdout": runner_loaded_checkpoint_from_stdout,
        "runner_sidecars_present": runner_sidecars_present,
        "validation_episode_count": args.episodes,
        "blockers": blockers,
        "warnings": warnings,
        "manifest_path": str(output_dir / "controlled_trained_checkpoint_loading_smoke_manifest.json"),
        "report_path": str(output_dir / "controlled_trained_checkpoint_loading_smoke_report.json"),
        "checkpoint_dir": str(checkpoint_dir),
        "figure10_runner_output_dir": str(runner_output_dir),
        "loss_values": losses,
    }

    _write_json(output_dir / "controlled_trained_checkpoint_loading_smoke_manifest.json", manifest)
    _write_json(output_dir / "controlled_trained_checkpoint_loading_smoke_report.json", report)
    return {"manifest": manifest, "report": report}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--episodes", type=int, default=1)
    parser.add_argument("--synthetic-steps", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--run-id", default="phase6_9_controlled_trained_checkpoint_smoke")
    parser.add_argument("--checkpoint-format", default="pytorch_state_dict_payload")
    parser.add_argument("--allow-controlled-trained-checkpoint-smoke", action="store_true")
    parser.add_argument("--allow-synthetic-training-step", action="store_true")
    args = parser.parse_args()

    if not args.allow_controlled_trained_checkpoint_smoke:
        raise SystemExit("--allow-controlled-trained-checkpoint-smoke is required")
    if not args.allow_synthetic_training_step:
        raise SystemExit("--allow-synthetic-training-step is required")
    if args.episodes <= 0:
        raise SystemExit("episodes must be > 0")
    if args.episodes > 2:
        raise SystemExit("episodes must be <= 2 for smoke")
    if args.synthetic_steps <= 0:
        raise SystemExit("synthetic_steps must be > 0")
    if args.synthetic_steps > 2:
        raise SystemExit("synthetic_steps must be <= 2 for smoke")
    if args.checkpoint_format not in {"pytorch_state_dict_payload", "pytorch_model_file"}:
        raise SystemExit("unsupported checkpoint format")
    output_dir = _resolve_path(args.output_dir)
    if _repo_relative(output_dir):
        raise SystemExit("repo output refused")
    run_smoke(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
