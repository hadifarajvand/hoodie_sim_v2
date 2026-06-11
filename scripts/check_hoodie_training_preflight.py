from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _git_output(args: list[str]) -> str | None:
    try:
        import subprocess

        result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False)
        return result.stdout.strip() or None
    except Exception:
        return None


def _resolve_paper_contract_path(path: str) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else (ROOT / candidate)


def _check_gitignore(text: str) -> dict[str, Any]:
    markers = [
        "*.pth",
        "*.pt",
        "*.pkl",
        "*.pickle",
        "paper_state_trace.csv",
        "queue_trace.csv",
        "mleo_candidate_latency_trace.csv",
    ]
    return {marker: (marker in text) for marker in markers}


def _expected_checkpoint_names(agent_count: int) -> list[str]:
    return [f"agent_{index}.pth" for index in range(agent_count)]


def _expected_metadata_names(agent_count: int) -> list[str]:
    return [f"agent_{index}.pth.meta.json" for index in range(agent_count)]


def build_report(paper_contract: Path, agent_count: int) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    try:
        contract = _load_json(paper_contract)
    except Exception as exc:
        return {
            "training_run": False,
            "simulation_rerun": False,
            "checkpoint_created": False,
            "model_artifact_created": False,
            "paper_contract_loaded": False,
            "expected_agent_count": agent_count,
            "expected_checkpoint_files": _expected_checkpoint_names(agent_count),
            "expected_metadata_files": _expected_metadata_names(agent_count),
            "gitignore_protection_status": {},
            "blockers": [f"paper_contract_load_failed: {exc}"],
            "warnings": [],
            "ready_for_tiny_smoke": False,
        }

    gitignore_text = (ROOT / ".gitignore").read_text()
    gitignore_status = _check_gitignore(gitignore_text)
    if not all(gitignore_status.values()):
        blockers.append("gitignore_missing_checkpoint_or_trace_protection")

    protocol_doc = ROOT / "artifacts/paper-contract-audit/phase6_2/hoodie_runtime_checkpoint_training_protocol.md"
    if not protocol_doc.exists():
        blockers.append("protocol_document_missing")

    if contract.get("number_of_eas") != agent_count:
        warnings.append(f"agent_count_mismatch: contract={contract.get('number_of_eas')} requested={agent_count}")

    git_commit = _git_output(["rev-parse", "HEAD"])
    branch = _git_output(["rev-parse", "--abbrev-ref", "HEAD"])

    return {
        "training_run": False,
        "simulation_rerun": False,
        "checkpoint_created": False,
        "model_artifact_created": False,
        "paper_contract_loaded": True,
        "expected_agent_count": agent_count,
        "expected_checkpoint_files": _expected_checkpoint_names(agent_count),
        "expected_metadata_files": _expected_metadata_names(agent_count),
        "gitignore_protection_status": gitignore_status,
        "git_commit": git_commit,
        "branch": branch,
        "blockers": blockers,
        "warnings": warnings,
        "ready_for_tiny_smoke": len(blockers) == 0,
        "paper_contract_summary": {
            "delta_sec": contract.get("delta_sec"),
            "action_slots": contract.get("action_slots"),
            "drain_slots": contract.get("drain_slots"),
            "validation_episodes": contract.get("validation_episodes"),
            "task_arrival_probability": contract.get("task_arrival_probability"),
            "task_sizes_mbits": contract.get("task_sizes_mbits"),
            "processing_density_gcycles_per_mbit": contract.get("processing_density_gcycles_per_mbit"),
            "private_cpu_ghz": contract.get("private_cpu_ghz"),
            "public_cpu_ghz": contract.get("public_cpu_ghz"),
            "cloud_cpu_ghz": contract.get("cloud_cpu_ghz"),
            "horizontal_rate_mbps": contract.get("horizontal_rate_mbps"),
            "vertical_rate_mbps": contract.get("vertical_rate_mbps"),
            "number_of_eas": contract.get("number_of_eas"),
            "timeout_slots": contract.get("timeout_slots"),
            "timeout_sec": contract.get("timeout_sec"),
            "learning_rate": contract.get("learning_rate"),
            "discount_factor": contract.get("discount_factor"),
            "replay_memory_size": contract.get("replay_memory_size"),
            "batch_size": contract.get("batch_size"),
            "drop_penalty": contract.get("drop_penalty"),
            "lstm_lookback_window": contract.get("lstm_lookback_window"),
            "training_episodes": contract.get("training_episodes"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper-contract", required=True)
    parser.add_argument("--agent-count", type=int, required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    report = build_report(_resolve_paper_contract_path(args.paper_contract), args.agent_count)
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2, sort_keys=True))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
