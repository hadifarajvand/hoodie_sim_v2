from __future__ import annotations

from dataclasses import dataclass, asdict
import json
import subprocess
from pathlib import Path
from typing import Any, Iterable


SOURCE_GATE_TAG = "030-paper-assumption-closure-evidence-exhaustion-pipeline-complete"
FEATURE_ID = "031-user-approved-assumption-patch-registry"
SCHEMA_VERSION = "1.0.0"
SOURCE_REPORT_PATH = Path("artifacts/analysis/paper-assumption-closure-evidence-exhaustion/assumption-closure-report.json")
OUTPUT_PATH = Path("resources/papers/hoodie/recovered/user-approved-assumption-registry.json")

_CANDIDATES: tuple[dict[str, Any], ...] = (
    {
        "item_id": "Figure_7_adjacency",
        "domain": "topology",
        "paper_status_required": "unrecoverable_after_evidence_exhaustion",
        "assumption_status": "blocked_no_assumption",
        "proposed_value": "",
        "value_type": "structural",
        "runtime_use_allowed": False,
        "approval_required": True,
        "approval_source": "manual_user_value_required",
        "rationale": "Topology cannot be generated automatically; user-supplied adjacency is required before runtime use.",
        "scientific_risk": "Fabricated adjacency would invalidate legal action constraints and offloading legality.",
        "affected_runtime_components": ["topology legality", "action mask generation", "offloading policy"],
        "validation_plan": "Confirm user-provided edges match the paper or approved assumptions before any runtime consumer reads them.",
    },
    {
        "item_id": "legal_horizontal_destinations",
        "domain": "topology",
        "paper_status_required": "unrecoverable_after_evidence_exhaustion",
        "assumption_status": "blocked_no_assumption",
        "proposed_value": "",
        "value_type": "structural",
        "runtime_use_allowed": False,
        "approval_required": True,
        "approval_source": "explicit_topology_required",
        "rationale": "Legal horizontal destinations depend on explicit topology and cannot be inferred safely.",
        "scientific_risk": "Guessing destinations would produce invalid routing legality and corrupt offloading decisions.",
        "affected_runtime_components": ["topology legality", "destination filtering", "policy action masks"],
        "validation_plan": "Validate destinations against a manually approved topology file before enabling runtime use.",
    },
    {
        "item_id": "EA_private_cpu_capacity",
        "domain": "compute capacity",
        "paper_status_required": "unrecoverable_after_evidence_exhaustion",
        "assumption_status": "proposed",
        "proposed_value": "cpu_capacity_per_slot_agent = 32.0",
        "value_type": "numeric",
        "runtime_use_allowed": False,
        "approval_required": True,
        "approval_source": "current_runtime_default",
        "rationale": "Current runtime defaults can be surfaced as an explicit assumption, but the paper did not recover the capacity value.",
        "scientific_risk": "A wrong private capacity would distort computation-delay estimates and scheduling feasibility.",
        "affected_runtime_components": ["agent compute delay", "slot completion logic", "capacity normalization"],
        "validation_plan": "Compare simulated delay behavior against any future approved capacity source before enabling runtime use.",
    },
    {
        "item_id": "EA_public_cpu_capacity",
        "domain": "compute capacity",
        "paper_status_required": "unrecoverable_after_evidence_exhaustion",
        "assumption_status": "proposed",
        "proposed_value": "cpu_capacity_per_slot_edge = 64.0",
        "value_type": "numeric",
        "runtime_use_allowed": False,
        "approval_required": True,
        "approval_source": "current_runtime_default",
        "rationale": "The public/edge capacity is a runtime default only; it is not paper-recovered evidence.",
        "scientific_risk": "An incorrect edge capacity would change completion timing and resource contention behavior.",
        "affected_runtime_components": ["edge compute delay", "slot completion logic", "capacity normalization"],
        "validation_plan": "Verify downstream use only after an explicit approval review and a regression comparison against reference traces.",
    },
    {
        "item_id": "cloud_cpu_capacity",
        "domain": "compute capacity",
        "paper_status_required": "unrecoverable_after_evidence_exhaustion",
        "assumption_status": "proposed",
        "proposed_value": "cpu_capacity_per_slot_cloud = 128.0",
        "value_type": "numeric",
        "runtime_use_allowed": False,
        "approval_required": True,
        "approval_source": "current_runtime_default",
        "rationale": "Cloud capacity is surfaced as a proposed runtime assumption because the paper did not recover a numeric value.",
        "scientific_risk": "Overstating cloud capacity would suppress delay and hide contention in offloaded execution paths.",
        "affected_runtime_components": ["cloud compute delay", "offload completion timing", "capacity normalization"],
        "validation_plan": "Require explicit user approval and trace-based regression checks before any runtime config consumes the value.",
    },
    {
        "item_id": "cloud_data_rate",
        "domain": "link/data rate",
        "paper_status_required": "unrecoverable_after_evidence_exhaustion",
        "assumption_status": "proposed",
        "proposed_value": "vertical data-rate assumption = 10 Mbps",
        "value_type": "numeric",
        "runtime_use_allowed": False,
        "approval_required": True,
        "approval_source": "vertical_data_rate_assumption",
        "rationale": "The cloud-facing rate may reuse the vertical data-rate assumption as an explicit proposal, but it is not paper-backed.",
        "scientific_risk": "A wrong transfer rate would distort transmission delay and offload selection behavior.",
        "affected_runtime_components": ["transmission delay", "network latency model", "offloading policy"],
        "validation_plan": "Compare offload latency traces against the approved rate before runtime use is enabled.",
    },
    {
        "item_id": "timeout_value",
        "domain": "timeout/deadline",
        "paper_status_required": "unrecoverable_after_evidence_exhaustion",
        "assumption_status": "blocked_no_assumption",
        "proposed_value": "",
        "value_type": "rule",
        "runtime_use_allowed": False,
        "approval_required": True,
        "approval_source": "manual_timeout_value_required",
        "rationale": "Timeout must be explicitly supplied; inventing a deadline would fabricate a key control parameter.",
        "scientific_risk": "An invented timeout would change drop behavior, reward timing, and deadline enforcement.",
        "affected_runtime_components": ["deadline enforcement", "drop logic", "reward timing"],
        "validation_plan": "Validate a manually supplied timeout against paper notes or approved assumptions before runtime use.",
    },
    {
        "item_id": "multi_agent_aggregation_reduction_order",
        "domain": "reward aggregation",
        "paper_status_required": "unrecoverable_after_evidence_exhaustion",
        "assumption_status": "proposed",
        "proposed_value": "sum rewards per agent per episode, then arithmetic mean across agents",
        "value_type": "rule",
        "runtime_use_allowed": False,
        "approval_required": True,
        "approval_source": "safe_runtime_reporting_rule",
        "rationale": "A transparent reduction rule can be proposed for approval without claiming paper recovery.",
        "scientific_risk": "A wrong aggregation order would alter reported rewards and cross-agent comparability.",
        "affected_runtime_components": ["reward aggregation", "episode reporting", "multi-agent evaluation"],
        "validation_plan": "Confirm the reduction order against downstream reporting artifacts before runtime use is enabled.",
    },
)


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@dataclass(frozen=True, slots=True)
class RegistryEntry:
    item_id: str
    paper_status: str
    paper_confidence: str
    assumption_status: str
    proposed_value: str
    value_type: str
    runtime_use_allowed: bool
    approval_required: bool
    approval_source: str
    rationale: str
    scientific_risk: str
    affected_runtime_components: list[str]
    validation_plan: str
    no_paper_recovery_claim: bool = True

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["affected_runtime_components"] = list(self.affected_runtime_components)
        return data


def validate_source_gate(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path.cwd()
    report_path = root / SOURCE_REPORT_PATH
    if not report_path.exists():
        raise FileNotFoundError(f"Missing source report: {report_path}")

    tag_result = subprocess.run(
        ["git", "tag", "--list", SOURCE_GATE_TAG],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    tag_present = SOURCE_GATE_TAG in {line.strip() for line in tag_result.stdout.splitlines()}
    if not tag_present:
        raise RuntimeError(f"Required source gate tag missing: {SOURCE_GATE_TAG}")
    return {
        "source_report": str(report_path),
        "source_gate_tag": SOURCE_GATE_TAG,
        "tag_present": True,
    }


def load_feature_030_closure_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path.cwd()
    path = root / SOURCE_REPORT_PATH
    if not path.exists():
        raise FileNotFoundError(f"Missing Feature 030 closure report: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _closure_index(closure_report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for item in closure_report.get("items", []):
        if isinstance(item, dict) and item.get("item_id"):
            index[str(item["item_id"])] = item
    return index


def _candidate_entry(candidate: dict[str, Any], closure_item: dict[str, Any]) -> RegistryEntry:
    return RegistryEntry(
        item_id=str(candidate["item_id"]),
        paper_status=str(closure_item.get("status", "")),
        paper_confidence=str(closure_item.get("confidence", "")),
        assumption_status=str(candidate["assumption_status"]),
        proposed_value=str(candidate.get("proposed_value", "")),
        value_type=str(candidate["value_type"]),
        runtime_use_allowed=bool(candidate["runtime_use_allowed"]),
        approval_required=bool(candidate["approval_required"]),
        approval_source=str(candidate["approval_source"]),
        rationale=str(candidate["rationale"]),
        scientific_risk=str(candidate["scientific_risk"]),
        affected_runtime_components=list(candidate["affected_runtime_components"]),
        validation_plan=str(candidate["validation_plan"]),
    )


def build_registry_entries(repo_root: Path | None = None) -> list[RegistryEntry]:
    closure_report = load_feature_030_closure_report(repo_root)
    index = _closure_index(closure_report)
    entries: list[RegistryEntry] = []
    missing: list[str] = []
    for candidate in _CANDIDATES:
        item = index.get(candidate["item_id"])
        if item is None:
            missing.append(candidate["item_id"])
            continue
        entries.append(_candidate_entry(candidate, item))
    if missing:
        raise KeyError(f"Missing Feature 030 candidate(s): {', '.join(missing)}")
    return entries


def _source_gates(repo_root: Path | None = None) -> list[dict[str, Any]]:
    root = repo_root or Path.cwd()
    return [
        {
            "source": "feature_030_closure_report",
            "path": str(root / SOURCE_REPORT_PATH),
            "required": True,
        },
        {
            "source": "feature_030_complete_tag",
            "tag": SOURCE_GATE_TAG,
            "required": True,
        },
    ]


def build_user_approved_assumption_registry(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path.cwd()
    validate_source_gate(root)
    entries = build_registry_entries(root)
    return {
        "feature_id": FEATURE_ID,
        "schema_version": SCHEMA_VERSION,
        "source_gates": _source_gates(root),
        "item_count": len(entries),
        "entries": [entry.to_dict() for entry in entries],
    }


def write_user_approved_assumption_registry(repo_root: Path | None = None) -> Path:
    root = repo_root or Path.cwd()
    payload = build_user_approved_assumption_registry(root)
    output = root / OUTPUT_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(_json_dump(payload), encoding="utf-8")
    return output

