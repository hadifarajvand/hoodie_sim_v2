from __future__ import annotations

from typing import Any

from .schema import CONFIDENCE_LEVELS, FINAL_STATUSES


def classify_item(item: dict[str, Any], evidence: list[dict[str, Any]]) -> dict[str, Any]:
    if item.get("item_id") == "Figure_7_adjacency":
        if item.get("manual_visual_recovery") and item["manual_visual_recovery"].get("edges"):
            return {
                **item,
                "status": "partially_recovered",
                "confidence": "medium",
                "source_evidence": [],
                "source_methods": ["visual_pdf_page_inspection"],
                "normalized_finding": item.get("title", ""),
                "runtime_approval_required": True,
                "evidence_exhaustion_rationale": "",
                "manual_visual_recovery": item.get("manual_visual_recovery"),
            }
        return {
            **item,
            "status": "unrecoverable_after_evidence_exhaustion",
            "confidence": "low",
            "source_evidence": evidence[:1],
            "source_methods": [record["source_type"] for record in evidence[:1]],
            "normalized_finding": item.get("title", ""),
            "runtime_approval_required": True,
            "evidence_exhaustion_rationale": "Figure 7 adjacency has no defensible per-edge manual extraction and must remain unrecoverable.",
            "manual_visual_recovery": item.get("manual_visual_recovery"),
        }

    if evidence:
        confidence = evidence[0].get("confidence", "medium")
        if confidence not in CONFIDENCE_LEVELS:
            confidence = "invalid"
        status = "recovered" if confidence == "high" else "partially_recovered"
        if str(item.get("runtime_approval_required", False)).lower() == "true":
            status = "assumption_backed_requires_user_approval"
        return {
            **item,
            "status": status if status in FINAL_STATUSES else "partially_recovered",
            "confidence": confidence,
            "source_evidence": evidence,
            "source_methods": [evidence[0]["source_type"]],
            "normalized_finding": evidence[0]["normalized_finding"],
            "runtime_approval_required": bool(item.get("runtime_approval_required", False)),
            "evidence_exhaustion_rationale": "",
            "manual_visual_recovery": item.get("manual_visual_recovery"),
        }

    return {
        **item,
        "status": "unrecoverable_after_evidence_exhaustion",
        "confidence": "low",
        "source_evidence": evidence[:1],
        "source_methods": [],
        "normalized_finding": item.get("title", ""),
        "runtime_approval_required": bool(item.get("runtime_approval_required", False)),
        "evidence_exhaustion_rationale": f"No item-specific evidence found after exhausting approved sources for {item.get('item_id')}.",
        "manual_visual_recovery": item.get("manual_visual_recovery"),
    }
