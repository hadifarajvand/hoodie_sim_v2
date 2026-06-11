from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _resolve_path(path: str) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else (ROOT / candidate)


def _repo_relative(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except Exception:
        return False


def _expected_files(agent_count: int) -> tuple[list[str], list[str]]:
    return [f"agent_{i}.pth" for i in range(agent_count)], [f"agent_{i}.pth.meta.json" for i in range(agent_count)]


def _tiny_runtime_step(seed: int, state_dim: int, action_count: int, hidden_layers: list[int], lstm_layers: int):
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
    state = torch.zeros((1, state_dim), dtype=torch.float32)
    lstm_input = torch.zeros((1, 1, state_dim), dtype=torch.float32)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    q_values = model(state, lstm_input)
    loss = q_values.pow(2).mean()
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    return model, float(loss.item())


def run_smoke(args: argparse.Namespace) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    if args.agent_count <= 0:
        blockers.append("invalid_agent_count")
    if args.agent_count > 2:
        blockers.append("agent_count_too_large_for_tiny_smoke")
    if args.episodes > 2:
        blockers.append("episodes_too_large_for_tiny_smoke")
    if args.steps_per_episode > 5:
        blockers.append("steps_per_episode_too_large_for_tiny_smoke")

    output_dir = _resolve_path(args.output_dir)
    in_repo = _repo_relative(output_dir)
    if in_repo and not args.allow_repo_output:
        blockers.append("repo_output_refused")

    paper_contract = _load_json(_resolve_path(args.paper_contract))
    expected_checkpoint_files, expected_metadata_files = _expected_files(max(args.agent_count, 0))
    manifest = {
        "phase": "6.3",
        "run_type": "tiny_non_official_checkpoint_smoke",
        "official_claim_allowed": False,
        "paper_reproduction_claim": False,
        "simulation_rerun": False,
        "validation_run": False,
        "agent_count": args.agent_count,
        "seed": args.seed,
        "episodes": args.episodes,
        "steps_per_episode": args.steps_per_episode,
        "expected_checkpoint_files": expected_checkpoint_files,
        "expected_metadata_files": expected_metadata_files,
        "checkpoint_format": "pytorch_state_dict_file",
        "runtime_inspection_summary": {},
        "checkpoint_dir_assessment": {},
        "warnings": warnings,
        "blockers": blockers,
    }
    smoke_report = {
        "training_smoke_run": True,
        "official_training_run": False,
        "full_training_run": False,
        "validation_run": False,
        "checkpoint_created": False,
        "checkpoint_created_in_repo": False,
        "official_claim_allowed": False,
        "loss_values": [],
        "action_count": None,
        "state_dim": None,
        "output_dir": str(output_dir),
        "blockers": blockers,
        "warnings": warnings,
    }

    if blockers:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
        (output_dir / "smoke_report.json").write_text(json.dumps(smoke_report, indent=2, sort_keys=True))
        return {"manifest": manifest, "smoke_report": smoke_report}

    import torch

    from training.hoodie_checkpoint_interop import (
        assess_hoodie_checkpoint_dir,
        inspect_runtime_torch_checkpoint,
        write_checkpoint_metadata_sidecar,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    state_dim = 6
    action_count = 3
    hidden_layers = [8]
    lstm_layers = 1
    loss_values: list[float] = []
    for agent_index in range(args.agent_count):
        model, loss = _tiny_runtime_step(args.seed + agent_index, state_dim, action_count, hidden_layers, lstm_layers)
        loss_values.append(loss)
        checkpoint_path = output_dir / f"agent_{agent_index}.pth"
        payload = {
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
            "seed": args.seed + agent_index,
        }
        torch.save(payload, checkpoint_path)
        write_checkpoint_metadata_sidecar(
            checkpoint_path,
            {
                "policy_name": "HOODIE",
                "checkpoint_format": "pytorch_state_dict_file",
                "created_by": "run_hoodie_tiny_checkpoint_smoke.py",
                "seed": args.seed + agent_index,
                "state_dim": state_dim,
                "action_count": action_count,
                "agent_index": agent_index,
                "agent_count": args.agent_count,
                "episode_count": args.episodes,
                "paper_contract_ref": "config/paper_table4_contract.json",
                "paper_contract_hash": paper_contract.get("source"),
                "git_commit": None,
                "branch": None,
                "training_command": "tiny_non_official_checkpoint_smoke",
                "training_start_time_utc": None,
                "training_end_time_utc": None,
                "runtime_loader_target": "Phase 6.1 interop utilities",
                "official_claim_allowed": False,
                "validation_required_before_official_claim": True,
            },
        )
        inspection = inspect_runtime_torch_checkpoint(checkpoint_path)
        if not inspection.get("loadable"):
            blockers.append(f"checkpoint_inspection_failed: agent_{agent_index}")

    checkpoint_dir_assessment = assess_hoodie_checkpoint_dir(output_dir, expected_agent_count=args.agent_count)
    manifest["runtime_inspection_summary"] = {
        "checkpoint_dir_assessment": checkpoint_dir_assessment,
        "inspect_runtime_torch_checkpoint": inspect_runtime_torch_checkpoint(output_dir / "agent_0.pth"),
    }
    manifest["checkpoint_dir_assessment"] = checkpoint_dir_assessment
    smoke_report.update(
        {
            "checkpoint_created": True,
            "checkpoint_created_in_repo": in_repo,
            "loss_values": loss_values,
            "action_count": action_count,
            "state_dim": state_dim,
        }
    )
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    (output_dir / "smoke_report.json").write_text(json.dumps(smoke_report, indent=2, sort_keys=True))
    return {"manifest": manifest, "smoke_report": smoke_report}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper-contract", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--agent-count", type=int, required=True)
    parser.add_argument("--episodes", type=int, required=True)
    parser.add_argument("--steps-per-episode", type=int, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--allow-create-checkpoint", action="store_true")
    parser.add_argument("--allow-repo-output", action="store_true")
    args = parser.parse_args()

    if args.agent_count <= 0:
        raise SystemExit("invalid agent_count")
    if args.agent_count > 2:
        raise SystemExit("agent_count exceeds tiny smoke limit")
    if args.episodes > 2:
        raise SystemExit("episodes exceeds tiny smoke limit")
    if args.steps_per_episode > 5:
        raise SystemExit("steps_per_episode exceeds tiny smoke limit")
    if not args.allow_create_checkpoint:
        raise SystemExit("checkpoint creation requires --allow-create-checkpoint")
    if _repo_relative(_resolve_path(args.output_dir)) and not args.allow_repo_output:
        raise SystemExit("repo output refused without --allow-repo-output")

    run_smoke(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
