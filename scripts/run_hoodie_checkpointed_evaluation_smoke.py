from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _resolve_path(path: str) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else (ROOT / candidate)


def _repo_relative(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except Exception:
        return False


def map_smoke_action_id(action_id: int) -> str:
    return {0: "local", 1: "horizontal", 2: "vertical"}.get(action_id, "unknown")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _build_synthetic_eval_input(state_dim: int, lstm_input_shape: int):
    import torch

    state = torch.zeros((1, state_dim), dtype=torch.float32)
    lstm_input = torch.zeros((1, 1, lstm_input_shape), dtype=torch.float32)
    return state, lstm_input


def _load_deepqnetwork_from_payload(payload: dict[str, Any], checkpoint_path: Path):
    import torch

    from decision_makers.agent import DeepQNetwork

    model_class = payload.get("model_class")
    if model_class != "DeepQNetwork":
        raise ValueError(f"unsupported_model_class: {model_class}")
    required = [
        "state_dict",
        "state_dim",
        "lstm_input_shape",
        "lstm_output_shape",
        "number_of_actions",
        "hidden_layers",
        "lstm_layers",
        "dueling",
        "dropout_rate",
    ]
    missing = [key for key in required if key not in payload]
    if missing:
        raise ValueError(f"missing_payload_fields: {missing}")
    model = DeepQNetwork(
        state_dimensions=int(payload["state_dim"]),
        lstm_input_shape=int(payload["lstm_input_shape"]),
        lstm_output_shape=int(payload["lstm_output_shape"]),
        number_of_actions=int(payload["number_of_actions"]),
        hidden_layers=list(payload["hidden_layers"]),
        lstm_layers=int(payload["lstm_layers"]),
        dueling=bool(payload["dueling"]),
        dropout_rate=float(payload["dropout_rate"]),
    ).cpu()
    state_dict = payload["state_dict"]
    if not isinstance(state_dict, dict):
        raise ValueError("state_dict_payload_not_a_mapping")
    model.load_state_dict(state_dict)
    model.eval()
    inspection = {
        "checkpoint_path": str(checkpoint_path),
        "model_class": model_class,
        "state_dim": int(payload["state_dim"]),
        "lstm_input_shape": int(payload["lstm_input_shape"]),
        "lstm_output_shape": int(payload["lstm_output_shape"]),
        "number_of_actions": int(payload["number_of_actions"]),
    }
    return model, inspection


def _validate_checkpoint_metadata(metadata: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if metadata.get("policy_name") != "HOODIE":
        blockers.append("metadata_policy_name_invalid")
    if metadata.get("official_claim_allowed") is True:
        blockers.append("metadata_official_claim_allowed_true")
    if metadata.get("checkpoint_format") != "pytorch_state_dict_file":
        blockers.append("metadata_checkpoint_format_invalid")
    return blockers


def _action_records_for_agent(
    model,
    *,
    agent_index: int,
    evaluation_steps: int,
    seed: int,
    state_dim: int,
    lstm_input_shape: int,
) -> list[dict[str, Any]]:
    import torch

    records: list[dict[str, Any]] = []
    for step in range(evaluation_steps):
        torch.manual_seed(seed + agent_index * 1000 + step)
        state, lstm_input = _build_synthetic_eval_input(state_dim, lstm_input_shape)
        with torch.no_grad():
            q_values = model(state, lstm_input)
            action_id = int(torch.argmax(q_values, dim=1).item())
        records.append(
            {
                "policy_name": "HOODIE",
                "agent_index": agent_index,
                "evaluation_step": step,
                "action_id": action_id,
                "selected_action": map_smoke_action_id(action_id),
                "source": "checkpointed_evaluation_smoke",
                "official_figure_claim": False,
            }
        )
    return records


def run_smoke(args: argparse.Namespace) -> dict[str, Any]:
    from training.hoodie_checkpoint_interop import assess_hoodie_checkpoint_dir, inspect_runtime_torch_checkpoint
    from analysis.hoodie_action_distribution import write_action_distribution_outputs

    blockers: list[str] = []
    warnings: list[str] = []

    if args.agent_count <= 0:
        blockers.append("invalid_agent_count")
    if args.agent_count > 2:
        blockers.append("agent_count_too_large_for_checkpointed_evaluation_smoke")
    if args.evaluation_steps <= 0:
        blockers.append("invalid_evaluation_steps")
    if args.evaluation_steps > 5:
        blockers.append("evaluation_steps_too_large_for_checkpointed_evaluation_smoke")

    checkpoint_dir = _resolve_path(args.checkpoint_dir)
    output_dir = _resolve_path(args.output_dir)
    in_repo = _repo_relative(output_dir)
    if in_repo and not args.allow_repo_output:
        blockers.append("repo_output_refused")
    if not args.allow_evaluation_smoke:
        blockers.append("missing_allow_evaluation_smoke")
    if not checkpoint_dir.exists() or not checkpoint_dir.is_dir():
        blockers.append("checkpoint_dir_missing")

    expected_checkpoint_files = [f"agent_{i}.pth" for i in range(max(args.agent_count, 0))]
    expected_metadata_files = [f"agent_{i}.pth.meta.json" for i in range(max(args.agent_count, 0))]
    checkpoint_dir_assessment = assess_hoodie_checkpoint_dir(checkpoint_dir, expected_agent_count=args.agent_count)

    manifest: dict[str, Any] = {
        "phase": "6.4",
        "run_type": "checkpointed_evaluation_wiring_smoke",
        "official_claim_allowed": False,
        "paper_reproduction_claim": False,
        "official_figure_claim": False,
        "simulation_rerun": False,
        "validation_run": False,
        "full_training_run": False,
        "checkpoint_created": False,
        "checkpoint_dir": str(checkpoint_dir),
        "output_dir": str(output_dir),
        "agent_count": args.agent_count,
        "evaluation_steps": args.evaluation_steps,
        "seed": args.seed,
        "expected_checkpoint_files": expected_checkpoint_files,
        "expected_metadata_files": expected_metadata_files,
        "checkpoint_dir_assessment": checkpoint_dir_assessment,
        "runtime_inspection_summary": {},
        "action_distribution_outputs": {},
        "warnings": warnings,
        "blockers": blockers,
    }
    report: dict[str, Any] = {
        "checkpointed_evaluation_smoke_run": True,
        "official_evaluation_run": False,
        "official_training_run": False,
        "full_training_run": False,
        "simulation_rerun": False,
        "validation_run": False,
        "checkpoint_created": False,
        "official_claim_allowed": False,
        "paper_reproduction_claim": False,
        "figure8_claim": False,
        "figure9_claim": False,
        "figure10_claim": False,
        "figure11_claim": False,
        "total_action_records": 0,
        "unknown_action_count": 0,
        "action_distribution_path": None,
        "blockers": blockers,
        "warnings": warnings,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    if blockers:
        (output_dir / "checkpointed_evaluation_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
        (output_dir / "checkpointed_evaluation_report.json").write_text(json.dumps(report, indent=2, sort_keys=True))
        return {"manifest": manifest, "report": report}

    import torch

    action_records: list[dict[str, Any]] = []
    runtime_inspection_summary: dict[str, Any] = {
        "checkpoint_dir_assessment": checkpoint_dir_assessment,
        "agents": [],
    }

    for agent_index in range(args.agent_count):
        checkpoint_path = checkpoint_dir / f"agent_{agent_index}.pth"
        meta_path = checkpoint_dir / f"agent_{agent_index}.pth.meta.json"
        if not checkpoint_path.exists():
            blockers.append(f"missing_checkpoint: agent_{agent_index}")
            continue
        if not meta_path.exists():
            blockers.append(f"missing_metadata_sidecar: agent_{agent_index}")
            continue
        payload_info = inspect_runtime_torch_checkpoint(checkpoint_path)
        runtime_inspection_summary["agents"].append(payload_info)
        if not payload_info.get("loadable"):
            blockers.append(f"checkpoint_not_loadable: agent_{agent_index}")
            continue
        payload = torch.load(str(checkpoint_path), map_location="cpu")
        if not isinstance(payload, dict):
            blockers.append(f"checkpoint_payload_not_mapping: agent_{agent_index}")
            continue
        if payload.get("state_dict") is None:
            blockers.append(f"missing_state_dict: agent_{agent_index}")
            continue
        if payload.get("model_class") != "DeepQNetwork":
            blockers.append(f"invalid_model_class: agent_{agent_index}")
            continue
        metadata = _load_json(meta_path)
        blockers.extend(_validate_checkpoint_metadata(metadata))
        if blockers:
            continue
        model, inspection = _load_deepqnetwork_from_payload(payload, checkpoint_path)
        runtime_inspection_summary["agents"].append(inspection)
        state_dim = int(payload["state_dim"])
        lstm_input_shape = int(payload["lstm_input_shape"])
        action_records.extend(
            _action_records_for_agent(
                model,
                agent_index=agent_index,
                evaluation_steps=args.evaluation_steps,
                seed=args.seed,
                state_dim=state_dim,
                lstm_input_shape=lstm_input_shape,
            )
        )

    if blockers:
        manifest["runtime_inspection_summary"] = runtime_inspection_summary
        report["blockers"] = blockers
        report["warnings"] = warnings
        (output_dir / "checkpointed_evaluation_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
        (output_dir / "checkpointed_evaluation_report.json").write_text(json.dumps(report, indent=2, sort_keys=True))
        return {"manifest": manifest, "report": report}

    action_records_path = output_dir / "action_records.json"
    action_records_path.write_text(json.dumps(action_records, indent=2, sort_keys=True))
    action_distribution_outputs = write_action_distribution_outputs(
        action_records,
        output_dir,
        label="checkpointed_evaluation_smoke",
        policy_name="HOODIE",
    )
    report.update(
        {
            "total_action_records": len(action_records),
            "unknown_action_count": sum(1 for record in action_records if record["selected_action"] == "unknown"),
            "action_distribution_path": action_distribution_outputs["json"],
        }
    )
    manifest["runtime_inspection_summary"] = runtime_inspection_summary
    manifest["action_distribution_outputs"] = action_distribution_outputs
    manifest["blockers"] = blockers
    report["blockers"] = blockers
    report["warnings"] = warnings
    (output_dir / "checkpointed_evaluation_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    (output_dir / "checkpointed_evaluation_report.json").write_text(json.dumps(report, indent=2, sort_keys=True))
    return {"manifest": manifest, "report": report}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint-dir", required=True)
    parser.add_argument("--paper-contract", default="config/paper_table4_contract.json")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--agent-count", type=int, required=True)
    parser.add_argument("--evaluation-steps", type=int, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--allow-evaluation-smoke", action="store_true")
    parser.add_argument("--allow-repo-output", action="store_true")
    args = parser.parse_args()

    if not args.allow_evaluation_smoke:
        raise SystemExit("missing --allow-evaluation-smoke")
    if args.agent_count <= 0:
        raise SystemExit("invalid agent_count")
    if args.agent_count > 2:
        raise SystemExit("agent_count exceeds tiny smoke limit")
    if args.evaluation_steps <= 0:
        raise SystemExit("invalid evaluation_steps")
    if args.evaluation_steps > 5:
        raise SystemExit("evaluation_steps exceeds tiny smoke limit")
    if _repo_relative(_resolve_path(args.output_dir)) and not args.allow_repo_output:
        raise SystemExit("repo output refused without --allow-repo-output")

    result = run_smoke(args)
    blockers = result.get("report", {}).get("blockers", [])
    return 1 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
