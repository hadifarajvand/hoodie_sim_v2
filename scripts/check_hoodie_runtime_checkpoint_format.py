from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


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


def run_format_check(args: argparse.Namespace) -> dict[str, Any]:
    from training.hoodie_runtime_checkpoint_loader import load_deepqnetwork_checkpoint, validate_hoodie_checkpoint_metadata

    checkpoint_dir = _resolve_path(args.checkpoint_dir)
    report: dict[str, Any] = {
        "phase": "6.8",
        "scope": "hoodie_runtime_checkpoint_format_unification",
        "format_check_run": True,
        "training_run": False,
        "validation_run": False,
        "simulation_rerun": False,
        "checkpoint_created": False,
        "main_py_called": False,
        "figure10_validation_called": False,
        "official_claim_allowed": False,
        "checkpoint_dir": str(checkpoint_dir),
        "agent_count": args.agent_count,
        "agent_reports": [],
        "all_agents_runtime_loadable": False,
        "accepted_formats_seen": [],
        "rejected_formats_seen": [],
        "blockers": [],
        "warnings": [],
    }
    if args.agent_count <= 0:
        report["blockers"].append("invalid_agent_count")
        return report
    if not checkpoint_dir.exists():
        report["blockers"].append("checkpoint_dir_missing")
        return report

    accepted: set[str] = set()
    rejected: set[str] = set()
    all_ok = True
    for agent_index in range(args.agent_count):
        checkpoint_path = checkpoint_dir / f"agent_{agent_index}.pth"
        metadata_path = checkpoint_path.with_name(checkpoint_path.name + ".meta.json")
        model, checkpoint_report = load_deepqnetwork_checkpoint(checkpoint_path, map_location="cpu")
        metadata_report = validate_hoodie_checkpoint_metadata(metadata_path)
        runtime_loadable = bool(checkpoint_report.get("loadable")) and not metadata_report.get("blockers")
        blockers = list(dict.fromkeys([*checkpoint_report.get("blockers", []), *metadata_report.get("blockers", [])]))
        if runtime_loadable and checkpoint_report.get("format"):
            accepted.add(str(checkpoint_report.get("format")))
        else:
            all_ok = False
            rejected.add(str(checkpoint_report.get("format") or "unknown"))
        report["agent_reports"].append(
            {
                "agent_index": agent_index,
                "checkpoint_path": str(checkpoint_path),
                "metadata_path": str(metadata_path),
                "runtime_loadable": runtime_loadable,
                "checkpoint_report": checkpoint_report,
                "metadata_report": metadata_report,
                "blockers": blockers,
            }
        )
        if blockers:
            report["blockers"].extend(blockers)

    report["accepted_formats_seen"] = sorted(accepted)
    report["rejected_formats_seen"] = sorted(rejected)
    report["all_agents_runtime_loadable"] = all_ok and not report["blockers"]
    report["blockers"] = list(dict.fromkeys(report["blockers"]))
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint-dir", required=True)
    parser.add_argument("--agent-count", type=int, required=True)
    parser.add_argument("--allow-format-check", action="store_true")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    if not args.allow_format_check:
        raise SystemExit("--allow-format-check is required")
    if args.agent_count <= 0:
        raise SystemExit("agent_count must be > 0")
    output = _resolve_path(args.output) if args.output else None
    if output is not None and _repo_relative(output):
        raise SystemExit("repo output refused")

    report = run_format_check(args)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not report["blockers"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
