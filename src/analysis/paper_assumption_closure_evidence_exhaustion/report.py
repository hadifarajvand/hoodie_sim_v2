from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .classifier import classify_item
from .data import EvidenceItem, EvidenceRecord, ReportArtifact, ReportSummary
from .evidence_search import search_evidence
from .inventory import deduplicate_items, normalize_inventory_item
from .schema import CONFIDENCE_LEVELS, FINAL_STATUSES
from .source_loader import SOURCE_GATE_PATHS, load_sources

DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/paper-assumption-closure-evidence-exhaustion")
JSON_FILENAME = "assumption-closure-report.json"
MARKDOWN_FILENAME = "assumption-closure-report.md"
FEATURE_ID = "030-paper-assumption-closure-evidence-exhaustion-pipeline"
SCHEMA_VERSION = "1.0.0"


def build_inventory() -> list[dict[str, Any]]:
    sources = load_sources(SOURCE_GATE_PATHS)
    items = [
        {"item_id": "Figure_7_adjacency", "domain": "topology", "title": "Figure 7 adjacency", "description": "Paper topology adjacency graph", "runtime_approval_required": True},
        {"item_id": "legal_horizontal_destinations", "domain": "topology", "title": "Legal horizontal destinations", "description": "Allowed horizontal destinations", "runtime_approval_required": True},
        {"item_id": "EA_private_cpu_capacity", "domain": "compute capacity", "title": "EA private CPU capacity", "description": "Edge agent private CPU capacity", "runtime_approval_required": True},
        {"item_id": "EA_public_cpu_capacity", "domain": "compute capacity", "title": "EA public CPU capacity", "description": "Edge agent public CPU capacity", "runtime_approval_required": True},
        {"item_id": "cloud_cpu_capacity", "domain": "compute capacity", "title": "Cloud CPU capacity", "description": "Cloud CPU capacity", "runtime_approval_required": True},
        {"item_id": "cloud_data_rate", "domain": "link/data rate", "title": "Cloud data rate", "description": "Cloud data rate constant beyond vertical rate", "runtime_approval_required": True},
        {"item_id": "timeout_value", "domain": "timeout/deadline", "title": "Timeout value", "description": "Numeric timeout or deadline value", "runtime_approval_required": True},
        {"item_id": "multi_agent_aggregation_reduction_order", "domain": "reward aggregation", "title": "Multi-agent aggregation reduction order", "description": "Exact multi-agent reward reduction order", "runtime_approval_required": True},
        {"item_id": "Phi_n_pub_exact_formatting", "domain": "equation formatting", "title": "Phi_n^pub exact formatting", "description": "Noisy Phi_n^pub equation formatting", "runtime_approval_required": False},
    ]
    for path, loaded in sources.items():
        if path.suffix != ".json":
            continue
        if isinstance(loaded.payload, dict):
            for key in ("unrecoverable_items", "assumption_backed_items", "partially_recovered_items"):
                value = loaded.payload.get(key, [])
                if isinstance(value, list):
                    for index, entry in enumerate(value):
                        if isinstance(entry, dict):
                            enriched = dict(entry)
                            enriched.setdefault("source_reference", f"{path}#{key}[{index}]")
                            items.append(enriched)
    return [normalize_inventory_item(item) for item in deduplicate_items(items)]


def build_assumption_closure_report() -> ReportArtifact:
    sources = load_sources(SOURCE_GATE_PATHS)
    inventory = build_inventory()
    classified: list[dict[str, Any]] = []
    for item in inventory:
        evidence = search_evidence(item, sources)
        classified.append(classify_item(item, evidence))

    items = [EvidenceItem(
        item_id=item["item_id"],
        domain=item["domain"],
        title=item["title"],
        description=item["description"],
        status=item["status"],
        confidence=item["confidence"],
        runtime_approval_required=bool(item.get("runtime_approval_required", False)),
        source_methods=item.get("source_methods", []),
        source_evidence=[
            EvidenceRecord(
                source_type=record.get("source_type", "manual_review"),
                source_reference=record.get("source_reference", ""),
                raw_evidence=record.get("raw_evidence", ""),
                normalized_finding=record.get("normalized_finding", ""),
                confidence=record.get("confidence", "low"),
                contradiction_notes=record.get("contradiction_notes"),
            )
            for record in item.get("source_evidence", [])
        ],
        normalized_finding=item.get("normalized_finding", ""),
        evidence_exhaustion_rationale=item.get("evidence_exhaustion_rationale", ""),
        manual_visual_recovery=item.get("manual_visual_recovery"),
    ) for item in classified]

    by_status = {status: 0 for status in FINAL_STATUSES}
    by_confidence = {level: 0 for level in CONFIDENCE_LEVELS}
    manual_review_count = 0
    approval_required_count = 0
    unrecoverable_count = 0
    for item in classified:
        by_status[item["status"]] = by_status.get(item["status"], 0) + 1
        by_confidence[item["confidence"]] = by_confidence.get(item["confidence"], 0) + 1
        if item.get("manual_visual_recovery"):
            manual_review_count += 1
        if item.get("runtime_approval_required"):
            approval_required_count += 1
        if item["status"] == "unrecoverable_after_evidence_exhaustion":
            unrecoverable_count += 1

    summary = ReportSummary(
        total_items=len(classified),
        by_status=by_status,
        by_confidence=by_confidence,
        manual_review_count=manual_review_count,
        approval_required_count=approval_required_count,
        unrecoverable_count=unrecoverable_count,
    )

    def select(status: str) -> list[dict[str, Any]]:
        return [item for item in classified if item["status"] == status]

    return ReportArtifact(
        feature_id=FEATURE_ID,
        schema_version=SCHEMA_VERSION,
        source_gates=[{"path": str(path)} for path in SOURCE_GATE_PATHS],
        inventory_summary=summary,
        items=items,
        recovered_items=select("recovered"),
        partially_recovered_items=select("partially_recovered"),
        contradicted_items=select("contradicted"),
        assumption_backed_items=select("assumption_backed_requires_user_approval"),
        unrecoverable_after_evidence_exhaustion_items=select("unrecoverable_after_evidence_exhaustion"),
        out_of_scope_items=select("out_of_scope"),
        manual_review_required_items=[item for item in classified if item.get("manual_visual_recovery")],
        runtime_dependency_decisions={
            "runtime_behavior_changes": "out_of_scope",
            "low_confidence_runtime_use": "blocked_until_approval",
            "invalid_guess_policy": "rejected",
            "manual_figure_7_policy": "ambiguous_edges_unrecoverable",
        },
        no_training_or_policy_drift=True,
        no_dependency_drift=True,
        final_verdict="all_items_closed_without_runtime_changes"
        if not select("unrecoverable_after_evidence_exhaustion")
        else "blocked_by_unrecoverable_core_evidence",
    )


def write_assumption_closure_report(report: ReportArtifact | None = None, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    closure_report = report or build_assumption_closure_report()
    destination = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    destination.mkdir(parents=True, exist_ok=True)
    json_path = destination / JSON_FILENAME
    md_path = destination / MARKDOWN_FILENAME
    json_path.write_text(json.dumps(closure_report.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_lines = [
        f"# Assumption Closure Report ({closure_report.feature_id})",
        "",
        f"- schema_version: `{closure_report.schema_version}`",
        f"- final_verdict: `{closure_report.final_verdict}`",
        f"- total_items: `{closure_report.inventory_summary.total_items}`",
        f"- unrecoverable_count: `{closure_report.inventory_summary.unrecoverable_count}`",
        "",
        "## Items",
    ]
    for item in closure_report.items:
        md_lines.extend([
            f"- `{item.item_id}` | `{item.domain}` | `{item.status}` | `{item.confidence}` | approval_required={item.runtime_approval_required}",
        ])
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    return json_path, md_path
