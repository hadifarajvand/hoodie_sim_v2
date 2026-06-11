from __future__ import annotations

import argparse
import json
import re
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


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _static_figure10_contract() -> dict[str, bool]:
    source = (ROOT / "figure10_validation.py").read_text()
    return {
        "expected_policy_set_has_hoodie": "EXPECTED_POLICY_SET" in source and '"HOODIE"' in source,
        "official_policy_classes_has_hoodie": "OFFICIAL_POLICY_CLASSES" in source and '"HOODIE": Agent' in source,
        "config_has_hoodie_checkpoint_dir": "hoodie_checkpoint_dir" in source and "Figure10ValidationConfig" in source,
        "runner_checkpoint_cli_or_config_path_detected": (
            "--hoodie-checkpoint-dir" in source or "hoodie_checkpoint_dir" in source
        ),
    }


def _validate_checkpoint_metadata(metadata: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if metadata.get("policy_name") != "HOODIE":
        blockers.append("metadata_policy_name_invalid")
    if metadata.get("official_claim_allowed") is True:
        blockers.append("metadata_official_claim_allowed_true")
    if metadata.get("checkpoint_format") not in {"pytorch_state_dict_file", "pytorch_model_file"}:
        blockers.append("metadata_checkpoint_format_invalid")
    if metadata.get("checkpoint_format") == "trainer_json_checkpoint":
        blockers.append("trainer_json_checkpoint_not_accepted")
    return blockers


def run_preflight(args: argparse.Namespace) -> dict[str, Any]:
    from training.hoodie_checkpoint_interop import assess_hoodie_checkpoint_dir, inspect_runtime_torch_checkpoint

    blockers: list[str] = []
    warnings: list[str] = []

    if not args.allow_preflight:
        blockers.append("missing_allow_preflight")
    if args.agent_count <= 0:
        blockers.append("invalid_agent_count")

    paper_contract_path = _resolve_path(args.paper_contract)
    checkpoint_dir = _resolve_path(args.checkpoint_dir)
    output_path = _resolve_path(args.output) if args.output else None
    if output_path is not None and _repo_relative(output_path):
        blockers.append("repo_output_refused")
    if args.output:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    figure10_static_contract = _static_figure10_contract()
    contract = _load_json(paper_contract_path)
    paper_contract_summary = {
        "validation_episodes": contract.get("validation_episodes"),
        "number_of_eas": contract.get("number_of_eas"),
        "training_episodes": contract.get("training_episodes"),
        "timeout_slots": contract.get("timeout_slots"),
        "timeout_sec": contract.get("timeout_sec"),
        "action_slots": contract.get("action_slots"),
        "drain_slots": contract.get("drain_slots"),
    }

    checkpoint_dir_assessment = assess_hoodie_checkpoint_dir(checkpoint_dir, expected_agent_count=args.agent_count)
    checkpoint_agent_summaries: list[dict[str, Any]] = []

    expected_agents = max(args.agent_count, 0)
    for agent_index in range(expected_agents):
        checkpoint_path = checkpoint_dir / f"agent_{agent_index}.pth"
        metadata_path = checkpoint_dir / f"agent_{agent_index}.pth.meta.json"
        agent_blockers: list[str] = []
        summary: dict[str, Any] = {
            "agent_index": agent_index,
            "checkpoint_path": str(checkpoint_path),
            "metadata_path": str(metadata_path),
            "torch_inspection": {},
            "metadata_validation": {},
            "runtime_compatible_for_preflight": False,
            "blockers": agent_blockers,
        }
        if not checkpoint_path.exists():
            agent_blockers.append(f"missing_checkpoint: agent_{agent_index}")
        if not metadata_path.exists():
            agent_blockers.append(f"missing_metadata_sidecar: agent_{agent_index}")
        if checkpoint_path.exists():
            torch_inspection = inspect_runtime_torch_checkpoint(checkpoint_path)
        else:
            torch_inspection = {"loadable": False, "error": "missing", "warnings": []}
        summary["torch_inspection"] = torch_inspection
        if torch_inspection.get("loadable"):
            payload = None
            try:
                import torch

                payload = torch.load(str(checkpoint_path), map_location="cpu")
            except Exception as exc:
                agent_blockers.append(f"checkpoint_load_failed: {exc}")
            if not isinstance(payload, dict):
                agent_blockers.append("checkpoint_payload_not_mapping")
            else:
                if payload.get("state_dict") is None:
                    agent_blockers.append("missing_state_dict")
                if payload.get("model_class") != "DeepQNetwork":
                    agent_blockers.append("invalid_model_class")
        if metadata_path.exists():
            metadata = _load_json(metadata_path)
            metadata_validation = {
                "policy_name": metadata.get("policy_name"),
                "checkpoint_format": metadata.get("checkpoint_format"),
                "official_claim_allowed": metadata.get("official_claim_allowed", False),
                "blockers": _validate_checkpoint_metadata(metadata),
            }
            summary["metadata_validation"] = metadata_validation
            agent_blockers.extend(
                b for b in metadata_validation["blockers"] if b not in agent_blockers
            )
        if agent_blockers:
            blockers.extend(b for b in agent_blockers if b not in blockers)
        if not agent_blockers and checkpoint_path.exists() and metadata_path.exists():
            summary["runtime_compatible_for_preflight"] = True
        checkpoint_agent_summaries.append(summary)

    official_validation_ready = False
    if args.agent_count < int(contract.get("number_of_eas", 0)) and not args.allow_tiny_checkpoint_dir:
        blockers.append("tiny_checkpoint_dir_requires_allow_flag")
    if checkpoint_dir_assessment.get("issues"):
        blockers.extend(checkpoint_dir_assessment.get("issues", []))

    if len(checkpoint_agent_summaries) < args.agent_count:
        blockers.append("missing_agent_summaries")

    required_runner_changes = [
        "wire_hoodie_checkpoint_dir_into_agent_construction",
        "load_runtime_checkpoint_per_agent_before_validation",
        "emit_checkpointed_hoodie_action_records",
        "connect_action_distribution_outputs_to_figure9_or_separate_artifact",
        "guard_official_claims_until_200_episode_validation_passes",
    ]

    report: dict[str, Any] = {
        "phase": "6.5",
        "scope": "hoodie_validation_runner_checkpoint_integration_preflight",
        "preflight_run": True,
        "validation_run": False,
        "simulation_rerun": False,
        "training_run": False,
        "checkpoint_created": False,
        "official_figure_claims_made": False,
        "official_claim_allowed": False,
        "figure10_static_contract": figure10_static_contract,
        "paper_contract_summary": paper_contract_summary,
        "checkpoint_dir_assessment": checkpoint_dir_assessment,
        "checkpoint_agent_summaries": checkpoint_agent_summaries,
        "integration_preflight_passed": len(blockers) == 0 and all(item.get("runtime_compatible_for_preflight") for item in checkpoint_agent_summaries),
        "official_validation_ready": False,
        "runner_integration_required_before_official_validation": True,
        "required_runner_changes": required_runner_changes,
        "blockers": blockers,
        "warnings": warnings,
    }
    report["official_validation_ready"] = False
    if output_path is not None:
        output_path.write_text(json.dumps(report, indent=2, sort_keys=True))
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper-contract", required=True)
    parser.add_argument("--checkpoint-dir", required=True)
    parser.add_argument("--agent-count", type=int, required=True)
    parser.add_argument("--output")
    parser.add_argument("--allow-tiny-checkpoint-dir", action="store_true")
    parser.add_argument("--allow-preflight", action="store_true")
    args = parser.parse_args()

    if not args.allow_preflight:
        raise SystemExit("missing --allow-preflight")
    if args.agent_count <= 0:
        raise SystemExit("invalid agent_count")
    report = run_preflight(args)
    return 1 if report.get("blockers") else 0


if __name__ == "__main__":
    raise SystemExit(main())
