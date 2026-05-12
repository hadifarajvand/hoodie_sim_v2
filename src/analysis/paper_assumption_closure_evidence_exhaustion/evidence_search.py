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

ITEM_SEARCH_TERMS = {
    "Figure_7_adjacency": ("figure 7", "adjacency", "edge", "topology"),
    "legal_horizontal_destinations": ("horizontal destinations", "legal horizontal", "destination"),
    "EA_private_cpu_capacity": ("private cpu", "ea private", "cpu capacity"),
    "EA_public_cpu_capacity": ("public cpu", "ea public", "cpu capacity"),
    "cloud_cpu_capacity": ("cloud cpu", "cpu capacity"),
    "cloud_data_rate": ("cloud data rate", "vertical rate", "data rate"),
    "timeout_value": ("timeout", "deadline", "slot"),
    "multi_agent_aggregation_reduction_order": ("cumulative reward", "averaged across", "distributed ho", "multi-agent"),
    "Phi_n_pub_exact_formatting": ("phi_n^pub", "phi_n,pub", "phi_n pub", "equation"),
}


def _snippet(text: str, term: str, window: int = 180) -> str:
    lower = text.lower()
    idx = lower.find(term.lower())
    if idx < 0:
        return text[: min(len(text), window)]
    start = max(0, idx - window // 2)
    end = min(len(text), idx + len(term) + window // 2)
    return text[start:end].replace("\n", " ").strip()


def search_evidence(item: dict[str, Any], sources: dict[Any, Any]) -> dict[str, list[dict[str, Any]]]:
    item_id = str(item.get("item_id", ""))
    matched_terms = ITEM_SEARCH_TERMS.get(item_id, ())
    positive: list[dict[str, Any]] = []
    negative: list[dict[str, Any]] = []
    searched: list[dict[str, Any]] = []
    for source_path, loaded in sources.items():
        text = loaded.payload if isinstance(loaded.payload, str) else str(loaded.payload)
        text_lower = text.lower()
        searched.append(
            {
                "source_reference": str(source_path),
                "search_terms": list(matched_terms),
                "search_method": "item_specific_term_match",
            }
        )
        for term in matched_terms:
            if term in text_lower and item_id == "Phi_n_pub_exact_formatting":
                snippet = _snippet(text, term)
                if snippet:
                    positive.append(
                        {
                            "source_reference": str(source_path),
                            "raw_evidence": snippet,
                            "normalized_finding": item.get("title", ""),
                            "confidence": "medium",
                            "source_type": "cross_artifact_consistency_check",
                        }
                    )
            else:
                negative.append(
                    {
                        "source_reference": str(source_path),
                        "raw_evidence": f"Searched for {term}; item-specific value not recovered.",
                        "normalized_finding": item.get("title", ""),
                        "confidence": "invalid",
                        "source_type": "cross_artifact_consistency_check",
                    }
                )
    return {"positive": positive, "negative": negative, "searched": searched}
