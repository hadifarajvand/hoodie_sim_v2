from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def _resolve_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (ROOT / path).resolve()


def _repo_relative(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except Exception:
        return False


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _inspect_main_py() -> dict[str, Any]:
    path = ROOT / "main.py"
    source = path.read_text()
    tree = ast.parse(source)
    text = source
    cli_flags = {
        flag: (flag in text)
        for flag in [
            "--config",
            "--log_folder",
            "--hyperparameters_file",
            "--epochs",
            "--validate",
            "--trace_output_dir",
            "--seed",
            "--trace_level",
        ]
    }
    training_path_detected = "if not args.validate" in text and "decision_maker.learn()" in text and "reset_lstm_history()" in text
    checkpoint_export_detected = "store_model(" in text or "torch.save(" in text and "checkpoint_folder" in text
    return {
        "path": str(path),
        "cli_flags": cli_flags,
        "training_path_detected": training_path_detected,
        "checkpoint_export_detected": checkpoint_export_detected,
        "exports_checkpoint_after_training": "store_model(" in text or "torch.save(" in text,
        "tree": tree,
    }


def _inspect_agent_py() -> dict[str, Any]:
    path = ROOT / "decision_makers" / "agent.py"
    source = path.read_text()
    return {
        "path": str(path),
        "store_model_detected": "def store_model" in source,
        "learn_detected": "def learn" in source,
        "last_checkpoint_load_report_detected": "last_checkpoint_load_report" in source,
        "unified_loader_detected": "load_hoodie_checkpoint_with_metadata" in source,
    }


def _inspect_loader_py() -> dict[str, Any]:
    path = ROOT / "training" / "hoodie_runtime_checkpoint_loader.py"
    source = path.read_text()
    return {
        "path": str(path),
        "full_model_supported": "pytorch_model_file" in source,
        "state_dict_payload_supported": "pytorch_state_dict_payload" in source,
        "trainer_json_rejected": "trainer_json_checkpoint_not_runtime_loadable" in source,
    }


def compute_small_real_training_readiness(
    *,
    main_info: dict[str, Any],
    agent_info: dict[str, Any],
    loader_info: dict[str, Any],
) -> dict[str, Any]:
    cli_flags = main_info["cli_flags"]
    main_py_cli_detected = all(cli_flags.values())
    main_py_training_path_detected = bool(main_info["training_path_detected"])
    main_py_checkpoint_export_detected = bool(main_info["checkpoint_export_detected"])
    agent_store_model_detected = bool(agent_info["store_model_detected"])
    agent_unified_loader_detected = bool(agent_info["unified_loader_detected"])

    runtime_loader_ready = all(
        [
            loader_info["full_model_supported"],
            loader_info["state_dict_payload_supported"],
            loader_info["trainer_json_rejected"],
            agent_unified_loader_detected,
        ]
    )
    safe_output_routing_ready = all(
        [
            cli_flags["--log_folder"],
            cli_flags["--hyperparameters_file"],
            cli_flags["--trace_output_dir"],
        ]
    )
    bounded_training_config_ready = all(
        [
            cli_flags["--epochs"],
            cli_flags["--seed"],
            cli_flags["--trace_level"],
            main_py_training_path_detected,
        ]
    )
    checkpoint_export_ready = bool(main_py_checkpoint_export_detected)
    metadata_sidecar_ready = False
    small_real_training_execution_ready = all(
        [
            runtime_loader_ready,
            safe_output_routing_ready,
            bounded_training_config_ready,
            checkpoint_export_ready,
            metadata_sidecar_ready,
        ]
    )

    blockers = [
        "small_real_training_execution_not_run",
        "training_checkpoint_export_missing" if not checkpoint_export_ready else None,
        "training_checkpoint_metadata_sidecar_missing" if not metadata_sidecar_ready else None,
        "paper_grade_training_not_run",
        "official_200_episode_validation_not_run",
        "official_figure_reproduction_not_run",
    ]
    if not main_py_training_path_detected:
        blockers.append("main_py_training_path_missing")
    if not safe_output_routing_ready:
        blockers.append("safe_output_routing_missing")
    if not runtime_loader_ready:
        blockers.append("runtime_loader_missing")
    if not agent_store_model_detected:
        blockers.append("agent_store_model_missing")
    if not bounded_training_config_ready:
        blockers.append("bounded_training_guard_missing")
    blockers = [b for b in dict.fromkeys(blockers) if b is not None]

    return {
        "preflight_defined": True,
        "training_execution_run": False,
        "main_py_called": False,
        "figure10_validation_called": False,
        "run_figure10_validation_called": False,
        "checkpoint_created": False,
        "model_artifact_created": False,
        "official_training_run": False,
        "full_training_run": False,
        "paper_training_run": False,
        "paper_grade_5000_episode_training_run": False,
        "official_200_episode_validation_run": False,
        "official_figure_claims_made": False,
        "official_claim_allowed": False,
        "requested_episodes": 1,
        "requested_episode_time": 3,
        "expected_agent_count": 20,
        "seed": 42,
        "main_py_cli_detected": main_py_cli_detected,
        "main_py_training_path_detected": main_py_training_path_detected,
        "main_py_checkpoint_export_detected": main_py_checkpoint_export_detected,
        "agent_store_model_detected": agent_store_model_detected,
        "agent_unified_loader_detected": agent_unified_loader_detected,
        "runtime_loader_ready": runtime_loader_ready,
        "safe_output_routing_ready": safe_output_routing_ready,
        "bounded_training_config_ready": bounded_training_config_ready,
        "checkpoint_export_ready": checkpoint_export_ready,
        "metadata_sidecar_ready": metadata_sidecar_ready,
        "small_real_training_execution_ready": small_real_training_execution_ready,
        "proposed_next_phase_command_preview": [
            "./.venvmac/bin/python",
            "scripts/run_hoodie_small_real_training_smoke.py",
            "--output-dir",
            "/tmp/hoodie_phase6_11_small_real_training_smoke",
            "--episodes",
            "1",
            "--episode-time",
            "3",
            "--seed",
            "42",
            "--allow-small-real-training-smoke",
        ],
        "required_next_phase_changes": [
            "add_training_smoke_script_with_tmp_only_outputs",
            "write_runtime_checkpoint_and_metadata_sidecar_after_training",
            "ensure_trained_checkpoint_uses_runtime_loader_compatible_format",
        ],
        "blockers": blockers,
        "warnings": [
            "preflight_only_no_training_executed",
            "future_phase_must_add_checkpoint_export_if_missing",
            "future_phase_must_write_metadata_sidecars_if_missing",
            "small_training_smoke_is_not_paper_training",
            "figure10_remains_blocked",
        ],
    }


def run_preflight(args: argparse.Namespace) -> dict[str, Any]:
    main_info = _inspect_main_py()
    agent_info = _inspect_agent_py()
    loader_info = _inspect_loader_py()
    report = {
        "phase": "6.10",
        "scope": "hoodie_small_real_training_smoke_preflight",
        "preflight_run": True,
        "training_execution_run": False,
        "simulation_rerun": False,
        "main_py_called": False,
        "figure10_validation_called": False,
        "run_figure10_validation_called": False,
        "checkpoint_created": False,
        "model_artifact_created": False,
        "official_training_run": False,
        "full_training_run": False,
        "paper_training_run": False,
        "paper_grade_5000_episode_training_run": False,
        "official_200_episode_validation_run": False,
        "official_figure_claims_made": False,
        "official_claim_allowed": False,
        "requested_episodes": args.episodes,
        "requested_episode_time": args.episode_time,
        "expected_agent_count": args.expected_agent_count,
        "seed": args.seed,
        **{k: v for k, v in compute_small_real_training_readiness(main_info=main_info, agent_info=agent_info, loader_info=loader_info).items()},
        "main_py_cli_detected": main_info["cli_flags"] and all(main_info["cli_flags"].values()),
        "main_py_training_path_detected": main_info["training_path_detected"],
        "main_py_checkpoint_export_detected": main_info["checkpoint_export_detected"],
        "agent_store_model_detected": agent_info["store_model_detected"],
        "agent_unified_loader_detected": agent_info["unified_loader_detected"],
        "runtime_loader_ready": all(
            [
                loader_info["full_model_supported"],
                loader_info["state_dict_payload_supported"],
                loader_info["trainer_json_rejected"],
                agent_info["unified_loader_detected"],
            ]
        ),
        "safe_output_routing_ready": all(
            [
                main_info["cli_flags"]["--log_folder"],
                main_info["cli_flags"]["--hyperparameters_file"],
                main_info["cli_flags"]["--trace_output_dir"],
            ]
        ),
        "bounded_training_config_ready": all(
            [
                main_info["cli_flags"]["--epochs"],
                main_info["cli_flags"]["--seed"],
                main_info["cli_flags"]["--trace_level"],
                main_info["training_path_detected"],
            ]
        ),
        "checkpoint_export_ready": bool(main_info["checkpoint_export_detected"]),
        "metadata_sidecar_ready": False,
        "small_real_training_execution_ready": False,
        "proposed_next_phase_command_preview": [
            "./.venvmac/bin/python",
            "scripts/run_hoodie_small_real_training_smoke.py",
            "--output-dir",
            "/tmp/hoodie_phase6_11_small_real_training_smoke",
            "--episodes",
            "1",
            "--episode-time",
            "3",
            "--seed",
            "42",
            "--allow-small-real-training-smoke",
        ],
        "required_next_phase_changes": [
            "add_training_smoke_script_with_tmp_only_outputs",
            "write_runtime_checkpoint_and_metadata_sidecar_after_training",
            "ensure_trained_checkpoint_uses_runtime_loader_compatible_format",
        ],
        "blockers": [
            "small_real_training_execution_not_run",
            "training_checkpoint_export_missing",
            "training_checkpoint_metadata_sidecar_missing",
            "paper_grade_training_not_run",
            "official_200_episode_validation_not_run",
            "official_figure_reproduction_not_run",
        ],
        "warnings": [
            "preflight_only_no_training_executed",
            "future_phase_must_add_checkpoint_export_if_missing",
            "future_phase_must_write_metadata_sidecars_if_missing",
            "small_training_smoke_is_not_paper_training",
            "figure10_remains_blocked",
        ],
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--episodes", type=int, default=1)
    parser.add_argument("--episode-time", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--expected-agent-count", type=int, default=20)
    parser.add_argument("--allow-small-real-training-preflight", action="store_true")
    args = parser.parse_args()

    if not args.allow_small_real_training_preflight:
        raise SystemExit("--allow-small-real-training-preflight is required")
    if args.episodes <= 0:
        raise SystemExit("episodes must be > 0")
    if args.episodes > 2:
        raise SystemExit("episodes must be <= 2 for preflight")
    if args.episode_time <= 0:
        raise SystemExit("episode_time must be > 0")
    if args.episode_time > 5:
        raise SystemExit("episode_time must be <= 5 for preflight")
    if args.expected_agent_count <= 0:
        raise SystemExit("expected-agent-count must be > 0")
    if args.output is not None:
        output = _resolve_path(args.output)
        if _repo_relative(output):
            raise SystemExit("repo output refused")
    report = run_preflight(args)
    if args.output is not None:
        output = _resolve_path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
