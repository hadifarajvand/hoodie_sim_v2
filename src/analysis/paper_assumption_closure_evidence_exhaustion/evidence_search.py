from __future__ import annotations

from typing import Any


SEARCH_TERMS = {
    "topology": ("figure 7", "adjacency", "legal destination", "edge-cloud", "connectivity"),
    "compute capacity": ("cpu", "capacity", "gigacycles", "cycles"),
    "link/data rate": ("data rate", "Mbps", "cloud data rate", "vertical rate"),
    "timeout/deadline": ("timeout", "deadline", "slot", "thrown", "dropped"),
    "reward aggregation": ("reward", "cumulative", "average", "episodes", "agent"),
    "equation formatting": ("phi_n^pub", "phi_n(t)", "equation", "ocr"),
}


def search_evidence(item: dict[str, Any], sources: dict[Any, Any]) -> list[dict[str, Any]]:
    title = str(item.get("title", "")).lower()
    description = str(item.get("description", "")).lower()
    haystack = f"{title} {description}"
    matches: list[dict[str, Any]] = []
    for source_path, loaded in sources.items():
        text = loaded.payload if isinstance(loaded.payload, str) else str(loaded.payload)
        text_lower = text.lower()
        if any(term in text_lower for terms in SEARCH_TERMS.values() for term in terms if term in haystack):
            matches.append(
                {
                    "source_reference": str(source_path),
                    "raw_evidence": text[:500],
                    "normalized_finding": item.get("title", ""),
                    "confidence": "medium",
                    "source_type": "cross_artifact_consistency_check",
                }
            )
    return matches
