from __future__ import annotations

from typing import Any

from .schema import CONFIDENCE_LEVELS, FINAL_STATUSES


def classify_item(item: dict[str, Any], evidence: list[dict[str, Any]]) -> dict[str, Any]:
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
        "source_evidence": [],
        "source_methods": [],
        "normalized_finding": item.get("title", ""),
        "runtime_approval_required": bool(item.get("runtime_approval_required", False)),
        "evidence_exhaustion_rationale": f"No evidence found after exhausting approved sources for {item.get('item_id')}.",
        "manual_visual_recovery": item.get("manual_visual_recovery"),
    }
