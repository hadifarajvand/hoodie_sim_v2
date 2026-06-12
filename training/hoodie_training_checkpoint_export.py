from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from training.hoodie_checkpoint_interop import write_checkpoint_metadata_sidecar


ROOT = Path(__file__).resolve().parents[1]


def _repo_relative(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except Exception:
        return False


def build_training_checkpoint_metadata(
    *,
    agent_index: int,
    agent_count: int,
    checkpoint_format: str,
    seed: int,
    state_dim: int,
    action_count: int,
    episode_count: int,
    training_step_count: int,
    run_id: str,
    phase: str,
    created_by: str,
    paper_contract_ref: str = "config/paper_table4_contract.json",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = {
        "policy_name": "HOODIE",
        "checkpoint_format": checkpoint_format,
        "created_by": created_by,
        "phase": phase,
        "seed": seed,
        "agent_index": agent_index,
        "agent_count": agent_count,
        "state_dim": state_dim,
        "action_count": action_count,
        "episode_count": episode_count,
        "training_step_count": training_step_count,
        "run_id": run_id,
        "small_real_training_smoke_candidate": True,
        "trained_checkpoint": True,
        "trained_checkpoint_scope": "small_real_training_smoke_candidate_only",
        "paper_training_run": False,
        "full_training_run": False,
        "paper_grade_5000_episode_training_run": False,
        "official_claim_allowed": False,
        "paper_reproduction_claim": False,
        "validation_required_before_official_claim": True,
        "paper_contract_ref": paper_contract_ref,
    }
    if extra:
        metadata.update(extra)
    metadata["official_claim_allowed"] = False
    return metadata


def _extract_state_dict_payload(agent: Any) -> dict[str, Any] | None:
    network = getattr(agent, "Q_eval_network", None)
    if network is None:
        return None
    required = [
        "state_dimensions",
        "lstm_input_shape",
        "lstm_output_shape",
        "number_of_actions",
        "hidden_layers",
        "lstm_layers",
        "dueling",
        "dropout_rate",
    ]
    if not all(hasattr(network, name) for name in required):
        return None
    return {
        "state_dict": network.state_dict(),
        "model_class": "DeepQNetwork",
        "state_dim": int(getattr(network, "state_dimensions")),
        "lstm_input_shape": int(getattr(network, "lstm_input_shape")),
        "lstm_output_shape": int(getattr(network, "lstm_output_shape")),
        "number_of_actions": int(getattr(network, "number_of_actions")),
        "hidden_layers": list(getattr(network, "hidden_layers")),
        "lstm_layers": int(getattr(network, "lstm_layers")),
        "dueling": bool(getattr(network, "dueling")),
        "dropout_rate": float(getattr(network, "dropout_rate", 0.0)),
    }


def export_agent_runtime_checkpoint(
    agent: Any,
    checkpoint_path: Path,
    metadata: dict[str, Any],
    *,
    checkpoint_format: str = "pytorch_model_file",
) -> dict[str, Any]:
    import torch

    report = {
        "checkpoint_path": str(checkpoint_path),
        "metadata_path": str(checkpoint_path.with_name(checkpoint_path.name + ".meta.json")),
        "checkpoint_format": checkpoint_format,
        "checkpoint_written": False,
        "metadata_written": False,
        "official_claim_allowed": False,
        "blockers": [],
        "warnings": [],
    }
    if metadata.get("official_claim_allowed") is True:
        report["blockers"].append("official_claim_violation")
        return report
    if checkpoint_format not in {"pytorch_model_file", "pytorch_state_dict_payload"}:
        report["blockers"].append("unsupported_checkpoint_format")
        return report

    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if checkpoint_format == "pytorch_model_file":
            model = getattr(agent, "Q_eval_network", None)
            if model is None:
                report["blockers"].append("checkpoint_write_failed")
                return report
            torch.save(model, checkpoint_path)
        else:
            payload = _extract_state_dict_payload(agent)
            if payload is None:
                report["blockers"].append("state_dict_export_not_supported_for_training_path")
                return report
            torch.save(payload, checkpoint_path)
        report["checkpoint_written"] = True
    except Exception as exc:  # pragma: no cover - exercised in tests
        report["blockers"].append("checkpoint_write_failed")
        report["warnings"].append(str(exc))
        return report

    try:
        write_checkpoint_metadata_sidecar(checkpoint_path, metadata)
        report["metadata_written"] = True
    except Exception as exc:  # pragma: no cover - exercised in tests
        report["blockers"].append("metadata_write_failed")
        report["warnings"].append(str(exc))
    return report


def export_training_checkpoints(
    agents: list[Any],
    output_dir: Path,
    *,
    run_id: str,
    seed: int,
    episode_count: int,
    training_step_count: int,
    phase: str = "6.11",
    checkpoint_format: str = "pytorch_model_file",
) -> dict[str, Any]:
    output_dir = Path(output_dir)
    if _repo_relative(output_dir):
        return {
            "export_run": True,
            "checkpoint_created": False,
            "model_artifact_created": False,
            "checkpoint_artifact_committed": False,
            "agent_count": len(agents),
            "all_checkpoints_written": False,
            "all_metadata_written": False,
            "official_claim_allowed": False,
            "agent_reports": [],
            "blockers": ["repo_output_refused"],
            "warnings": [],
        }
    output_dir.mkdir(parents=True, exist_ok=True)
    agent_reports = []
    all_checkpoints_written = bool(agents)
    all_metadata_written = bool(agents)
    blockers: list[str] = []
    for agent_index, agent in enumerate(agents):
        checkpoint_path = output_dir / f"agent_{agent_index}.pth"
        metadata = build_training_checkpoint_metadata(
            agent_index=agent_index,
            agent_count=len(agents),
            checkpoint_format=checkpoint_format,
            seed=seed,
            state_dim=int(getattr(agent, "state_dimensions", 0)),
            action_count=int(getattr(agent, "number_of_actions", 0)),
            episode_count=episode_count,
            training_step_count=training_step_count,
            run_id=run_id,
            phase=phase,
            created_by="main.py",
        )
        report = export_agent_runtime_checkpoint(agent, checkpoint_path, metadata, checkpoint_format=checkpoint_format)
        agent_reports.append(report)
        for blocker in report.get("blockers", []):
            blockers.append(f"agent_{agent_index}:{blocker}")
        all_checkpoints_written = all_checkpoints_written and bool(report["checkpoint_written"])
        all_metadata_written = all_metadata_written and bool(report["metadata_written"])
    if not agents:
        blockers.append("no_agents_to_export")
    if not all_checkpoints_written:
        blockers.append("not_all_checkpoints_written")
    if not all_metadata_written:
        blockers.append("not_all_metadata_written")
    blockers = list(dict.fromkeys(blockers))
    return {
        "export_run": True,
        "checkpoint_created": all_checkpoints_written,
        "model_artifact_created": all_checkpoints_written,
        "checkpoint_artifact_committed": False,
        "agent_count": len(agents),
        "all_checkpoints_written": all_checkpoints_written,
        "all_metadata_written": all_metadata_written,
        "official_claim_allowed": False,
        "agent_reports": agent_reports,
        "blockers": blockers,
        "warnings": [],
    }
