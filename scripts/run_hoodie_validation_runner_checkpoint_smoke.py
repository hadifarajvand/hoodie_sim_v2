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


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _validate_metadata(metadata: dict[str, Any]) -> list[str]:
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


def _copy_sidecars(source_checkpoint_dir: Path, staged_log_dir: Path, agent_count: int) -> list[str]:
    copied: list[str] = []
    for agent_index in range(agent_count):
        src = source_checkpoint_dir / f"agent_{agent_index}.pth.meta.json"
        dst = staged_log_dir / src.name
        if src.exists():
            dst.write_text(src.read_text())
            copied.append(str(dst))
    return copied


def _stage_run_layout(output_dir: Path, run_id: str, checkpoint_dir: Path, agent_count: int) -> dict[str, Any]:
    from figure10_validation import EXPECTED_POLICY_SET, REGIME_IDS, _copy_hoodie_checkpoints
    from training.hoodie_checkpoint_interop import assess_hoodie_checkpoint_dir, inspect_runtime_torch_checkpoint

    blockers: list[str] = []
    warnings: list[str] = []
    staged_checkpoint_summaries: list[dict[str, Any]] = []
    smoke_root = output_dir / "runs" / run_id
    runner_copy_helper_exercised = False
    runner_copy_helper_copies_metadata_sidecars = False
    sidecars_copied_by_smoke_wrapper = False

    checkpoint_dir_assessment = assess_hoodie_checkpoint_dir(checkpoint_dir, expected_agent_count=agent_count)
    if checkpoint_dir_assessment.get("issues"):
        blockers.extend(checkpoint_dir_assessment.get("issues", []))

    for regime_id in REGIME_IDS:
        log_dir = smoke_root / regime_id / "HOODIE" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        ok, missing = _copy_hoodie_checkpoints(checkpoint_dir, log_dir, agent_count)
        runner_copy_helper_exercised = True
        if not ok:
            blockers.append(f"missing_checkpoint_after_copy:{missing}")
        copied_sidecars = _copy_sidecars(checkpoint_dir, log_dir, agent_count)
        sidecars_copied_by_smoke_wrapper = True
        if len(copied_sidecars) != agent_count:
            blockers.append("missing_metadata_sidecar_after_copy")
        if not list(log_dir.glob("agent_*.pth.meta.json")):
            blockers.append("metadata_sidecars_not_present_in_runner_layout")
        for agent_index in range(agent_count):
            source_checkpoint_path = checkpoint_dir / f"agent_{agent_index}.pth"
            staged_checkpoint_path = log_dir / f"agent_{agent_index}.pth"
            source_metadata_path = checkpoint_dir / f"agent_{agent_index}.pth.meta.json"
            staged_metadata_path = log_dir / f"agent_{agent_index}.pth.meta.json"
            source_torch_inspection = inspect_runtime_torch_checkpoint(source_checkpoint_path)
            staged_torch_inspection = inspect_runtime_torch_checkpoint(staged_checkpoint_path)
            metadata_validation: dict[str, Any] = {
                "policy_name": None,
                "checkpoint_format": None,
                "official_claim_allowed": None,
                "blockers": [],
            }
            if source_metadata_path.exists() and staged_metadata_path.exists():
                metadata = _load_json(staged_metadata_path)
                metadata_validation = {
                    "policy_name": metadata.get("policy_name"),
                    "checkpoint_format": metadata.get("checkpoint_format"),
                    "official_claim_allowed": metadata.get("official_claim_allowed", False),
                    "blockers": _validate_metadata(metadata),
                }
            summary_blockers: list[str] = []
            if not source_torch_inspection.get("loadable"):
                summary_blockers.append(f"checkpoint_not_loadable: agent_{agent_index}")
            summary_blockers.extend([b for b in metadata_validation["blockers"] if b not in summary_blockers])
            runner_layout_ready_for_smoke = (
                source_torch_inspection.get("loadable") is True
                and staged_torch_inspection.get("loadable") is True
                and not metadata_validation["blockers"]
            )
            if not runner_layout_ready_for_smoke:
                blockers.extend([b for b in summary_blockers if b not in blockers])
            staged_checkpoint_summaries.append(
                {
                    "regime_id": regime_id,
                    "policy_name": "HOODIE",
                    "agent_index": agent_index,
                    "source_checkpoint_path": str(source_checkpoint_path),
                    "staged_checkpoint_path": str(staged_checkpoint_path),
                    "source_metadata_path": str(source_metadata_path),
                    "staged_metadata_path": str(staged_metadata_path),
                    "source_torch_inspection": source_torch_inspection,
                    "staged_torch_inspection": staged_torch_inspection,
                    "metadata_validation": metadata_validation,
                    "runner_layout_ready_for_smoke": runner_layout_ready_for_smoke,
                    "blockers": summary_blockers,
                }
            )

    manifest = {
        "phase": "6.6",
        "run_type": "validation_runner_checkpoint_integration_smoke",
        "official_claim_allowed": False,
        "paper_reproduction_claim": False,
        "official_figure_claim": False,
        "figure10_claim": False,
        "validation_run": False,
        "simulation_rerun": False,
        "training_run": False,
        "checkpoint_created": False,
        "main_py_called": False,
        "run_figure10_validation_called": False,
        "figure10_official_outputs_created": False,
        "checkpoint_dir": str(checkpoint_dir),
        "output_dir": str(output_dir),
        "run_id": run_id,
        "agent_count": agent_count,
        "regimes": list(REGIME_IDS),
        "expected_policy_set_has_hoodie": "HOODIE" in EXPECTED_POLICY_SET,
        "runner_hoodie_checkpoint_dir_supported": True,
        "runner_copy_helper_exercised": runner_copy_helper_exercised,
        "runner_copy_helper_copies_metadata_sidecars": runner_copy_helper_copies_metadata_sidecars,
        "sidecars_copied_by_smoke_wrapper": sidecars_copied_by_smoke_wrapper,
        "staged_checkpoint_summaries": staged_checkpoint_summaries,
        "blockers": blockers,
        "warnings": warnings,
    }

    report = {
        "phase": "6.6",
        "validation_runner_checkpoint_smoke_run": True,
        "official_validation_run": False,
        "official_training_run": False,
        "full_training_run": False,
        "simulation_rerun": False,
        "validation_run": False,
        "checkpoint_created": False,
        "official_claim_allowed": False,
        "figure8_claim": False,
        "figure9_claim": False,
        "figure10_claim": False,
        "figure11_claim": False,
        "runner_layout_created": True,
        "staged_checkpoint_count": len([s for s in staged_checkpoint_summaries if s["staged_checkpoint_path"]]),
        "staged_sidecar_count": len([s for s in staged_checkpoint_summaries if s["staged_metadata_path"]]),
        "all_staged_checkpoints_loadable": all(s["staged_torch_inspection"].get("loadable") for s in staged_checkpoint_summaries),
        "blockers": blockers,
        "warnings": warnings,
    }
    return {"manifest": manifest, "report": report, "root": smoke_root}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--agent-count", type=int, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--run-id", default="phase6_6_runner_smoke")
    parser.add_argument("--allow-runner-checkpoint-smoke", action="store_true")
    parser.add_argument("--allow-tiny-checkpoint-dir", action="store_true")
    args = parser.parse_args()

    if not args.allow_runner_checkpoint_smoke:
        raise SystemExit("missing --allow-runner-checkpoint-smoke")
    if args.agent_count <= 0:
        raise SystemExit("invalid agent_count")
    if args.agent_count > 2:
        raise SystemExit("agent_count exceeds tiny smoke limit")

    checkpoint_dir = _resolve_path(args.checkpoint_dir)
    output_dir = _resolve_path(args.output_dir)
    if _repo_relative(output_dir):
        raise SystemExit("repo output refused")
    if not checkpoint_dir.exists():
        raise SystemExit("checkpoint dir missing")

    from training.hoodie_checkpoint_interop import inspect_runtime_torch_checkpoint

    for agent_index in range(args.agent_count):
        checkpoint_path = checkpoint_dir / f"agent_{agent_index}.pth"
        meta_path = checkpoint_dir / f"agent_{agent_index}.pth.meta.json"
        if not checkpoint_path.exists():
            raise SystemExit(f"missing checkpoint: agent_{agent_index}")
        if not meta_path.exists():
            raise SystemExit(f"missing metadata sidecar: agent_{agent_index}")
        torch_info = inspect_runtime_torch_checkpoint(checkpoint_path)
        if torch_info.get("loadable") is not True:
            raise SystemExit(f"checkpoint_not_loadable: agent_{agent_index}")
        metadata = _load_json(meta_path)
        blockers = _validate_metadata(metadata)
        if blockers:
            raise SystemExit(", ".join(blockers))

    result = _stage_run_layout(output_dir, args.run_id, checkpoint_dir, args.agent_count)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "validation_runner_checkpoint_smoke_manifest.json").write_text(json.dumps(result["manifest"], indent=2, sort_keys=True))
    (output_dir / "validation_runner_checkpoint_smoke_report.json").write_text(json.dumps(result["report"], indent=2, sort_keys=True))
    return 1 if result["report"]["blockers"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
