from __future__ import annotations

from typing import Any

from .schema import CONFIDENCE_LEVELS, FINAL_STATUSES


def _assumption_rule(item: dict[str, Any]) -> str | None:
    proposed = item.get("proposed_assumption_rule") or item.get("proposed_value")
    if proposed:
        return str(proposed)
    return None


def classify_item(item: dict[str, Any], evidence: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    positive = evidence.get("positive", [])
    negative = evidence.get("negative", [])
    searched = evidence.get("searched", [])
    if item.get("item_id") == "Figure_7_adjacency":
        if item.get("manual_visual_recovery") and item["manual_visual_recovery"].get("edges"):
            return {
                **item,
                "status": "partially_recovered",
                "confidence": "medium",
                "positive_evidence": [],
                "negative_evidence": negative,
                "searched_sources": searched,
                "source_methods": ["visual_pdf_page_inspection"],
                "normalized_finding": item.get("title", ""),
                "runtime_approval_required": True,
                "evidence_exhaustion_rationale": "Partial per-edge manual recovery recorded; ambiguous edges remain unrecoverable.",
                "manual_visual_recovery": item.get("manual_visual_recovery"),
            }
        return {
            **item,
            "status": "unrecoverable_after_evidence_exhaustion",
            "confidence": "invalid",
            "positive_evidence": [],
            "negative_evidence": negative,
            "searched_sources": searched,
            "source_methods": [record["source_type"] for record in negative[:1]],
            "normalized_finding": item.get("title", ""),
            "runtime_approval_required": False,
            "evidence_exhaustion_rationale": "Figure 7 adjacency searched OCR, recovered registries, and prior topology reports, but no defensible per-edge manual extraction exists; ambiguous edges remain unrecoverable.",
            "manual_visual_recovery": item.get("manual_visual_recovery"),
        }

    if positive:
        confidence = positive[0].get("confidence", "medium")
        if confidence not in CONFIDENCE_LEVELS:
            confidence = "invalid"
        status = "recovered" if confidence == "high" else "partially_recovered"
        assumption_rule = _assumption_rule(item)
        if assumption_rule:
            status = "assumption_backed_requires_user_approval"
        return {
            **item,
            "status": status if status in FINAL_STATUSES else "partially_recovered",
            "confidence": confidence,
            "positive_evidence": positive,
            "negative_evidence": negative,
            "searched_sources": searched,
            "source_methods": [positive[0]["source_type"]],
            "normalized_finding": positive[0]["normalized_finding"],
            "runtime_approval_required": bool(assumption_rule),
            "evidence_exhaustion_rationale": (
                f"Proposed assumption rule requires approval: {assumption_rule}"
                if assumption_rule
                else ""
            ),
            "manual_visual_recovery": item.get("manual_visual_recovery"),
        }

    assumption_rule = _assumption_rule(item)
    if assumption_rule:
        return {
            **item,
            "status": "assumption_backed_requires_user_approval",
            "confidence": "low",
            "positive_evidence": [],
            "negative_evidence": negative,
            "searched_sources": searched,
            "source_methods": [record["source_type"] for record in negative[:1]],
            "normalized_finding": item.get("title", ""),
            "runtime_approval_required": True,
            "evidence_exhaustion_rationale": f"Proposed assumption rule requires approval: {assumption_rule}",
            "manual_visual_recovery": item.get("manual_visual_recovery"),
            "proposed_assumption_rule": assumption_rule,
        }

    return {
        **item,
        "status": "unrecoverable_after_evidence_exhaustion",
        "confidence": "invalid",
        "positive_evidence": [],
        "negative_evidence": negative,
        "searched_sources": searched,
        "source_methods": [record["source_type"] for record in negative[:1]],
        "normalized_finding": item.get("title", ""),
        "runtime_approval_required": False,
        "evidence_exhaustion_rationale": (
            f"Searched OCR, recovered registries, and prior analysis reports for {item.get('item_id')} but found no item-specific value; only negative evidence remains."
        ),
        "manual_visual_recovery": item.get("manual_visual_recovery"),
    }
