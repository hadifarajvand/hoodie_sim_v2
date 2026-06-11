from __future__ import annotations

import argparse
import json
import os
import shutil
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


def _load_base_hyperparameters() -> dict[str, Any]:
    return _load_json(ROOT / "hyperparameters" / "hyperparameters.json")


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def _build_runtime_fixture_checkpoints(output_dir: Path, seed: int) -> tuple[Path, list[dict[str, Any]]]:
    import torch

    from decision_makers.agent import DeepQNetwork
    from environment.environment import Environment

    base_hyperparameters = _load_base_hyperparameters()
    agent_count = int(base_hyperparameters["number_of_servers"])
    fixture_dir = output_dir / "runtime_fixture_checkpoints"
    fixture_dir.mkdir(parents=True, exist_ok=True)

    original_reset = Environment.reset

    def _noop_reset(self):  # pragma: no cover - simple monkeypatch helper
        return None

    Environment.reset = _noop_reset
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
        summaries: list[dict[str, Any]] = []
        for agent_index in range(agent_count):
            state_dim, lstm_shape, action_count = env.get_server_dimensions(agent_index)
            model = DeepQNetwork(
                state_dimensions=state_dim,
                lstm_input_shape=lstm_shape,
                lstm_output_shape=lstm_shape,
                number_of_actions=action_count,
                hidden_layers=list(base_hyperparameters["hidden_layers"]),
                lstm_layers=int(base_hyperparameters["lstm_layers"]),
                dueling=bool(base_hyperparameters["dueling"]),
                dropout_rate=float(base_hyperparameters["dropout_rate"]),
            )
            checkpoint_path = fixture_dir / f"agent_{agent_index}.pth"
            torch.save(model, checkpoint_path)
            metadata = {
                "policy_name": "HOODIE",
                "checkpoint_format": "pytorch_model_file",
                "created_by": "run_hoodie_validation_runner_execution_smoke.py",
                "runtime_fixture_checkpoint": True,
                "trained_checkpoint": False,
                "official_claim_allowed": False,
                "paper_reproduction_claim": False,
                "phase": "6.7",
                "seed": seed,
                "agent_index": agent_index,
                "agent_count": agent_count,
                "state_dim": state_dim,
                "action_count": action_count,
                "validation_required_before_official_claim": True,
            }
            (fixture_dir / f"agent_{agent_index}.pth.meta.json").write_text(json.dumps(metadata, indent=2, sort_keys=True))
            summaries.append(
                {
                    "agent_index": agent_index,
                    "checkpoint_path": str(checkpoint_path),
                    "metadata_path": str(fixture_dir / f"agent_{agent_index}.pth.meta.json"),
                    "state_dim": state_dim,
                    "action_count": action_count,
                }
            )
        return fixture_dir, summaries
    finally:
        Environment.reset = original_reset


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
    if not args.allow_controlled_runner_execution_smoke:
        raise SystemExit("--allow-controlled-runner-execution-smoke is required")
    if args.episodes <= 0:
        raise SystemExit("episodes must be > 0")
    if args.episodes > 2:
        raise SystemExit("episodes must be <= 2 for smoke")
    if args.policies != "HOODIE":
        raise SystemExit("only HOODIE is allowed in this phase")
    if not args.allow_runtime_fixture_checkpoints:
        raise SystemExit("--allow-runtime-fixture-checkpoints is required")

    output_dir.mkdir(parents=True, exist_ok=True)
    base_hyperparameters = _load_base_hyperparameters()
    smoke_hyperparameters = json.loads(json.dumps(base_hyperparameters))
    smoke_hyperparameters["episode_time"] = min(int(smoke_hyperparameters.get("episode_time", 100)), 3)
    hyperparameters_file = output_dir / "inputs" / "hyperparameters_phase6_7_execution_smoke.json"
    _write_json(hyperparameters_file, smoke_hyperparameters)

    runtime_fixture_checkpoint_dir, fixture_summaries = _build_runtime_fixture_checkpoints(output_dir, args.seed)
    runner_result = _run_figure10_runner(
        output_dir=output_dir,
        checkpoint_dir=runtime_fixture_checkpoint_dir,
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
    policy_summary = _load_json(summary_path) if summary_path.exists() else {}

    main_returncodes: dict[str, int | None] = {"delay": None, "drop_ratio": None}
    main_returncode_files = {
        regime: runner_output_dir / "runs" / args.run_id / regime / "HOODIE" / "main_returncode.txt"
        for regime in ("delay", "drop_ratio")
    }
    main_returncodes_seen = True
    main_py_subprocesses_seen = True
    main_py_all_returncodes_zero = True
    for regime, path in main_returncode_files.items():
        if not path.exists():
            main_py_subprocesses_seen = False
            main_py_all_returncodes_zero = False
            main_returncodes_seen = False
            continue
        try:
            rc = int(path.read_text().strip())
        except Exception:
            rc = None
        main_returncodes[regime] = rc
        if rc is None:
            main_py_subprocesses_seen = False
            main_py_all_returncodes_zero = False
            main_returncodes_seen = False
        elif rc != 0:
            main_py_all_returncodes_zero = False

    figure10_data_ready = bool(readiness.get("figure10_data_ready", False))
    blockers: list[str] = []
    warnings: list[str] = []
    if runner_result.returncode != 0:
        blockers.append("figure10_runner_execution_failed")
    if not main_returncodes_seen:
        blockers.append("main_returncode_missing")
    if not main_py_all_returncodes_zero:
        blockers.append("main_py_failed")
    if not runner_outputs_present:
        blockers.append("figure10_runner_outputs_missing")
    if figure10_data_ready:
        blockers.append("unexpected_official_readiness_true_in_smoke")
    if args.episodes != 1:
        blockers.append("unexpected_validation_episode_count")
    if not readiness or readiness.get("figure10_data_ready") is not False:
        warnings.append("figure10_data_ready remained false or unavailable as expected for smoke")
    if not validation_manifest:
        warnings.append("validation manifest missing or unreadable")

    official_claim_false = not any(
        validation_manifest.get(field) is True
        for field in ("official_claim_allowed", "paper_reproduction_claim", "official_figure_claim")
    )
    if not official_claim_false:
        blockers.append("official_claim_violation")

    manifest = {
        "phase": "6.7",
        "run_type": "controlled_validation_runner_execution_smoke",
        "official_claim_allowed": False,
        "paper_reproduction_claim": False,
        "official_figure_claim": False,
        "official_validation_run": False,
        "official_200_episode_validation_run": False,
        "controlled_runner_execution_smoke_run": True,
        "training_run": False,
        "full_training_run": False,
        "simulation_rerun": False,
        "checkpoint_training_run": False,
        "runtime_fixture_checkpoints_created": True,
        "runtime_fixture_checkpoints_trained": False,
        "main_py_called": True,
        "main_py_called_only_through_validation_runner": True,
        "figure10_validation_entrypoint_called": True,
        "run_figure10_validation_called": True,
        "test_mode": True,
        "episodes": args.episodes,
        "policies": [args.policies],
        "trace_level": "summary",
        "output_dir": str(output_dir),
        "figure10_runner_output_dir": str(runner_output_dir),
        "runtime_fixture_checkpoint_dir": str(runtime_fixture_checkpoint_dir),
        "non_official_runner_outputs_created": runner_outputs_present,
        "official_figure10_outputs_created": False,
        "figure8_claim": False,
        "figure9_claim": False,
        "figure10_claim": False,
        "figure11_claim": False,
        "runner_returncode": runner_result.returncode,
        "main_returncodes": main_returncodes,
        "figure10_readiness": readiness,
        "blocking_reasons": readiness.get("blocking_reasons", []) if isinstance(readiness, dict) else [],
        "blockers": blockers,
        "warnings": warnings,
        "runtime_fixture_checkpoint_summaries": fixture_summaries,
        "runner_output_manifest": validation_manifest,
        "runner_output_summary": policy_summary,
        "runner_stdout": runner_result.stdout,
        "runner_stderr": runner_result.stderr,
        "runner_returncode_zero": runner_result.returncode == 0,
    }

    report = {
        "phase": "6.7",
        "controlled_validation_runner_execution_smoke_run": True,
        "runner_completed": runner_result.returncode == 0,
        "main_py_subprocesses_seen": main_py_subprocesses_seen,
        "main_py_all_returncodes_zero": main_py_all_returncodes_zero,
        "official_validation_run": False,
        "official_200_episode_validation_run": False,
        "training_run": False,
        "checkpoint_training_run": False,
        "runtime_fixture_checkpoints_created": True,
        "runtime_fixture_checkpoints_trained": False,
        "official_claim_allowed": False,
        "paper_reproduction_claim": False,
        "figure10_claim": False,
        "figure10_data_ready": figure10_data_ready,
        "baseline_validation_ready": bool(readiness.get("baseline_validation_ready", False)) if isinstance(readiness, dict) else False,
        "validation_episode_count": args.episodes,
        "policies_evaluated": ["HOODIE"],
        "policies_skipped": [],
        "runner_outputs_present": runner_outputs_present,
        "blockers": blockers,
        "warnings": warnings,
    }

    _write_json(output_dir / "validation_runner_execution_smoke_manifest.json", manifest)
    _write_json(output_dir / "validation_runner_execution_smoke_report.json", report)
    return {"manifest": manifest, "report": report}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--allow-controlled-runner-execution-smoke", action="store_true")
    parser.add_argument("--episodes", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--run-id", default="phase6_7_runner_execution_smoke")
    parser.add_argument("--allow-runtime-fixture-checkpoints", action="store_true")
    parser.add_argument("--policies", default="HOODIE")
    args = parser.parse_args()

    result = run_smoke(args)
    return 0 if not result["manifest"]["blockers"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
