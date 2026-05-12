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
        "assumption_status": "approved",
        "proposed_value": {
            "node_count": 20,
            "node_order": "1_to_20",
            "graph_type": "undirected_unweighted",
            "edge_count": 30,
            "degree_regular": 3,
            "symmetric_required": True,
            "zero_diagonal_required": True,
            "source": "user_supplied_manual_extraction",
            "paper_recovery_claim": False,
            "edge_list": [
                [1, 6], [2, 7], [3, 8], [4, 9], [5, 10],
                [1, 11], [2, 12], [3, 13], [4, 14], [5, 15],
                [6, 16], [7, 17], [8, 18], [9, 19], [10, 20],
                [11, 16], [12, 17], [13, 18], [14, 19], [15, 20],
                [1, 16], [2, 17], [3, 18], [4, 19], [5, 20],
                [6, 11], [7, 12], [8, 13], [9, 14], [10, 15],
            ],
            "adjacency_matrix": [
                [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            ],
        },
        "value_type": "adjacency_matrix",
        "runtime_use_allowed": True,
        "approval_required": False,
        "approval_source": "user_supplied_manual_extraction",
        "rationale": "User supplied a manually extracted undirected, unweighted Figure 7 adjacency matrix. It is approved for runtime assumption use but remains non-paper-recovered.",
        "scientific_risk": "Manual extraction may differ from the original paper figure; using it as paper evidence would be invalid. Downstream work must label it as a user-approved assumption.",
        "affected_runtime_components": ["topology legality", "action mask generation", "horizontal offloading", "offloading policy"],
        "validation_plan": "Validate matrix shape 20x20, zero diagonal, symmetry, degree 3 for every node, 30 undirected edges, and edge-list/matrix consistency before any runtime consumer uses this assumption.",
    },
    {
        "item_id": "legal_horizontal_destinations",
        "domain": "topology",
        "paper_status_required": "unrecoverable_after_evidence_exhaustion",
        "assumption_status": "approved",
        "proposed_value": {
            "rule": "neighbor_only_horizontal_legality",
            "source_item_id": "Figure_7_adjacency",
            "source_assumption_status_required": "approved",
            "node_order": "1_to_20",
            "no_self_offload": True,
            "non_neighbor_horizontal_offload_allowed": False,
            "vertical_cloud_offload_separate": True,
            "destinations": {
                "1": [6, 11, 16],
                "2": [7, 12, 17],
                "3": [8, 13, 18],
                "4": [9, 14, 19],
                "5": [10, 15, 20],
                "6": [1, 11, 16],
                "7": [2, 12, 17],
                "8": [3, 13, 18],
                "9": [4, 14, 19],
                "10": [5, 15, 20],
                "11": [1, 6, 16],
                "12": [2, 7, 17],
                "13": [3, 8, 18],
                "14": [4, 9, 19],
                "15": [5, 10, 20],
                "16": [1, 6, 11],
                "17": [2, 7, 12],
                "18": [3, 8, 13],
                "19": [4, 9, 14],
                "20": [5, 10, 15],
            },
            "paper_recovery_claim": False,
        },
        "value_type": "horizontal_destination_rule",
        "runtime_use_allowed": True,
        "approval_required": False,
        "approval_source": "derived_from_user_approved_adjacency_neighbor_rule",
        "rationale": "Legal horizontal destinations are approved as the neighbor set of the user-approved Figure 7 adjacency assumption. This enables horizontal legality without claiming paper recovery.",
        "scientific_risk": "If the manually supplied adjacency differs from the original paper figure, this legality map will inherit that error. Downstream results must label horizontal legality as user-approved assumption-backed.",
        "affected_runtime_components": ["topology legality", "destination filtering", "action mask generation", "horizontal offloading", "offloading policy"],
        "validation_plan": "Validate that every destination is an adjacent node in the approved Figure_7_adjacency matrix, no node includes itself, no non-neighbor appears, each node has exactly 3 legal horizontal destinations, and vertical/cloud actions remain separate.",
    },
    {
        "item_id": "EA_private_cpu_capacity",
        "domain": "compute capacity",
        "paper_status_required": "unrecoverable_after_evidence_exhaustion",
        "assumption_status": "approved",
        "proposed_value": {
            "source": "user_supplied_table4_ocr_extraction",
            "symbol": "f_n^{EA,priv}",
            "frequency_ghz": 5.0,
            "slot_duration_seconds": 0.1,
            "derived_capacity_gcycles_per_slot": 0.5,
            "conversion_formula": "derived_capacity_gcycles_per_slot = frequency_ghz * slot_duration_seconds",
            "previous_runtime_default_gcycles_per_slot": 32.0,
            "previous_runtime_default_ratio_to_approved": 64.0,
            "runtime_patch_applied": False,
            "paper_recovery_claim": False,
        },
        "value_type": "numeric_derived_capacity",
        "runtime_use_allowed": True,
        "approval_required": False,
        "approval_source": "user_supplied_table4_ocr_extraction",
        "rationale": "User supplied Table 4 OCR extraction for private EA CPU frequency f_n^{EA,priv}=5 GHz. With Δ=0.1 sec, the approved assumption derives EA private capacity as 0.5 gigacycles/slot. This replaces the earlier proposed runtime default 32.0 for assumption-governance purposes only; no runtime config is changed in this feature.",
        "scientific_risk": "Using the old 32.0 gcycles/slot runtime default would understate local/private computation delay by a factor of 64 relative to the user-supplied Table 4-derived capacity. This approved value must still be treated as an assumption-registry value until a later paper-registry/runtime-config correction feature applies it.",
        "affected_runtime_components": ["agent compute delay", "local/private execution timing", "slot completion logic", "capacity normalization", "future runtime config patch"],
        "validation_plan": "Validate that frequency_ghz=5.0, slot_duration_seconds=0.1, derived_capacity_gcycles_per_slot=0.5, previous_runtime_default_gcycles_per_slot=32.0, and previous_runtime_default_ratio_to_approved=64.0. Confirm no runtime config is changed and no paper-recovery claim is introduced.",
    },
    {
        "item_id": "EA_public_cpu_capacity",
        "domain": "compute capacity",
        "paper_status_required": "unrecoverable_after_evidence_exhaustion",
        "assumption_status": "approved",
        "proposed_value": {
            "source": "user_supplied_table4_ocr_extraction",
            "symbol": "f_n^{EA,pub}",
            "frequency_ghz": 5.0,
            "slot_duration_seconds": 0.1,
            "derived_capacity_gcycles_per_slot": 0.5,
            "conversion_formula": "derived_capacity_gcycles_per_slot = frequency_ghz * slot_duration_seconds",
            "previous_runtime_default_gcycles_per_slot": 64.0,
            "previous_runtime_default_ratio_to_approved": 128.0,
            "runtime_patch_applied": False,
            "paper_recovery_claim": False,
        },
        "value_type": "numeric_derived_capacity",
        "runtime_use_allowed": True,
        "approval_required": False,
        "approval_source": "user_supplied_table4_ocr_extraction",
        "rationale": "User supplied Table 4 OCR extraction for public EA CPU frequency f_n^{EA,pub}=5 GHz. With Δ=0.1 sec, the approved assumption derives EA public capacity as 0.5 gigacycles/slot. This replaces the earlier proposed runtime default 64.0 for assumption-governance purposes only; no runtime config is changed in this feature.",
        "scientific_risk": "Using the old 64.0 gcycles/slot runtime default would understate public/edge computation delay by a factor of 128 relative to the user-supplied Table 4-derived capacity. This approved value must still be treated as an assumption-registry value until a later paper-registry/runtime-config correction feature applies it.",
        "affected_runtime_components": ["edge compute delay", "public queue execution timing", "horizontal offload completion timing", "slot completion logic", "capacity normalization", "future runtime config patch"],
        "validation_plan": "Validate that frequency_ghz=5.0, slot_duration_seconds=0.1, derived_capacity_gcycles_per_slot=0.5, previous_runtime_default_gcycles_per_slot=64.0, and previous_runtime_default_ratio_to_approved=128.0. Confirm no runtime config is changed and no paper-recovery claim is introduced.",
    },
    {
        "item_id": "cloud_cpu_capacity",
        "domain": "compute capacity",
        "paper_status_required": "unrecoverable_after_evidence_exhaustion",
        "assumption_status": "approved",
        "proposed_value": {
            "source": "user_supplied_table4_ocr_extraction",
            "symbol": "f^{Cloud}",
            "frequency_ghz": 30.0,
            "slot_duration_seconds": 0.1,
            "derived_capacity_gcycles_per_slot": 3.0,
            "conversion_formula": "derived_capacity_gcycles_per_slot = frequency_ghz * slot_duration_seconds",
            "previous_runtime_default_gcycles_per_slot": 128.0,
            "previous_runtime_default_ratio_to_approved": 42.6666666667,
            "runtime_patch_applied": False,
            "paper_recovery_claim": False,
        },
        "value_type": "numeric_derived_capacity",
        "runtime_use_allowed": True,
        "approval_required": False,
        "approval_source": "user_supplied_table4_ocr_extraction",
        "rationale": "User supplied Table 4 OCR extraction for cloud CPU frequency f^{Cloud}=30 GHz. With Δ=0.1 sec, the approved assumption derives cloud capacity as 3.0 gigacycles/slot. This replaces the earlier proposed runtime default 128.0 for assumption-governance purposes only; no runtime config is changed in this feature.",
        "scientific_risk": "Using the old 128.0 gcycles/slot runtime default would understate cloud computation delay by approximately 42.67x relative to the user-supplied Table 4-derived capacity. This approved value must still be treated as an assumption-registry value until a later paper-registry/runtime-config correction feature applies it.",
        "affected_runtime_components": ["cloud compute delay", "vertical offload completion timing", "slot completion logic", "capacity normalization", "future runtime config patch"],
        "validation_plan": "Validate that frequency_ghz=30.0, slot_duration_seconds=0.1, derived_capacity_gcycles_per_slot=3.0, previous_runtime_default_gcycles_per_slot=128.0, and previous_runtime_default_ratio_to_approved is approximately 42.6666666667. Confirm no runtime config is changed and no paper-recovery claim is introduced.",
        "no_paper_recovery_claim": True,
    },
    {
        "item_id": "cloud_data_rate",
        "domain": "link/data rate",
        "paper_status_required": "unrecoverable_after_evidence_exhaustion",
        "assumption_status": "approved",
        "proposed_value": {
            "source": "user_supplied_table4_ocr_extraction",
            "symbol": "R_V",
            "rate_mbps": 10.0,
            "rate_bps": 10000000.0,
            "interpretation": "cloud-facing vertical offload data rate",
            "separate_cloud_specific_rate_claim": False,
            "runtime_patch_applied": False,
            "paper_recovery_claim": False,
        },
        "value_type": "numeric_data_rate",
        "runtime_use_allowed": True,
        "approval_required": False,
        "approval_source": "user_supplied_table4_ocr_extraction",
        "rationale": "User supplied Table 4 OCR extraction for vertical data rate R_V=10 Mbps. Because cloud offloading is vertical offloading in the HOODIE model, the approved assumption uses R_V as the cloud-facing transmission rate. This does not introduce a separate cloud-specific data-rate constant and does not change runtime config in this feature.",
        "scientific_risk": "If cloud offload is assigned a rate different from R_V without evidence, vertical transmission delay and offload selection behavior would be distorted. This approved value must remain labeled as user-approved assumption-registry data until a later paper-registry/runtime-config correction feature applies it.",
        "affected_runtime_components": ["vertical transmission delay", "cloud offload latency", "network latency model", "offloading policy", "future runtime config patch"],
        "validation_plan": "Validate that rate_mbps=10.0, rate_bps=10000000.0, interpretation is cloud-facing vertical offload data rate, separate_cloud_specific_rate_claim=false, runtime_patch_applied=false, and no paper-recovery claim is introduced. Confirm link-rate runtime config is not changed.",
        "no_paper_recovery_claim": True,
    },
    {
        "item_id": "timeout_value",
        "domain": "timeout/deadline",
        "paper_status_required": "unrecoverable_after_evidence_exhaustion",
        "assumption_status": "approved",
        "proposed_value": {
            "source": "user_supplied_table4_ocr_extraction",
            "symbol": "φ_n",
            "timeout_slots": 20,
            "slot_duration_seconds": 0.1,
            "timeout_seconds": 2.0,
            "conversion_formula": "timeout_seconds = timeout_slots * slot_duration_seconds",
            "interpretation": "task timeout/drop deadline threshold",
            "runtime_patch_applied": False,
            "paper_recovery_claim": False,
        },
        "value_type": "rule",
        "runtime_use_allowed": True,
        "approval_required": False,
        "approval_source": "user_supplied_table4_ocr_extraction",
        "rationale": "User supplied Table 4 OCR extraction for task timeout φ_n=20 time slots. With Δ=0.1 sec, the approved assumption derives timeout_seconds=2.0. This resolves the previous blocked timeout assumption for assumption-governance purposes only; no runtime timeout logic or config is changed in this feature.",
        "scientific_risk": "Timeout directly controls drop behavior, reward timing, and deadline enforcement. A wrong timeout would change the task drop rate and learned objective. This value must remain labeled as user-approved assumption-registry data until a later paper-registry/runtime-config correction feature applies or verifies it.",
        "affected_runtime_components": ["deadline enforcement", "timeout/drop logic", "reward timing", "task lifecycle", "future runtime config patch"],
        "validation_plan": "Validate that timeout_slots=20, slot_duration_seconds=0.1, timeout_seconds=2.0, conversion_formula is correct, runtime_patch_applied=false, and no paper-recovery claim is introduced. Confirm timeout/drop runtime code and traffic/runtime config are not changed.",
        "no_paper_recovery_claim": True,
    },
    {
        "item_id": "multi_agent_aggregation_reduction_order",
        "domain": "reward aggregation",
        "paper_status_required": "unrecoverable_after_evidence_exhaustion",
        "assumption_status": "approved",
        "proposed_value": {
            "source": "user_approved_safe_reporting_rule",
            "rule": "per_agent_episode_sum_then_arithmetic_mean_across_agents",
            "agent_level_reduction": "sum terminal task rewards per agent per episode",
            "cross_agent_reduction": "arithmetic_mean",
            "no_task_slots": "excluded_or_omitted_not_zero",
            "nan_policy": "exclude_from_numeric_aggregation",
            "slot_level_direct_average": False,
            "seed_or_run_level_aggregation_in_scope": False,
            "runtime_patch_applied": False,
            "paper_recovery_claim": False,
        },
        "value_type": "aggregation_rule",
        "runtime_use_allowed": True,
        "approval_required": False,
        "approval_source": "user_approved_safe_reporting_rule",
        "rationale": "The paper states rewards are collected cumulatively over episodes and averaged across distributed HOODIE agents, but Feature 030 did not recover the exact reduction order. The approved assumption uses a transparent rule: sum terminal task rewards per agent per episode, then take the arithmetic mean across agents, while excluding no-task/NaN/omitted slots from numeric aggregation.",
        "scientific_risk": "A different reduction order could change reported reward curves and cross-agent comparability. Treating no-task slots as zero would bias rewards. This approved rule must remain labeled as user-approved assumption-registry data until a later evaluation/campaign reporting feature consumes it explicitly.",
        "affected_runtime_components": ["reward aggregation", "episode reporting", "multi-agent evaluation", "validation reporting", "future campaign reporting"],
        "validation_plan": "Validate that the rule performs per-agent episode summation before cross-agent arithmetic mean, excludes no-task/NaN/omitted slots, does not perform direct slot-level averaging, does not apply seed/run aggregation in this registry, and introduces no runtime reward-emission change.",
        "no_paper_recovery_claim": True,
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
    proposed_value: Any
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
        proposed_value=candidate.get("proposed_value", ""),
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
