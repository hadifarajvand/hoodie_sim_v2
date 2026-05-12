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

NEGATIVE_EVIDENCE_HINTS = {
    "Figure_7_adjacency": ("Figure 7 adjacency edges", "Figure 7", "adjacency", "unrecoverable"),
    "legal_horizontal_destinations": ("Figure 7 legal horizontal destinations", "legal horizontal destinations", "unrecoverable"),
    "EA_private_cpu_capacity": ("EA private/public/cloud CPU capacities", "CPU capacities", "unrecoverable"),
    "EA_public_cpu_capacity": ("EA private/public/cloud CPU capacities", "CPU capacities", "unrecoverable"),
    "cloud_cpu_capacity": ("EA private/public/cloud CPU capacities", "CPU capacities", "unrecoverable"),
    "cloud_data_rate": ("cloud data rate", "vertical rate", "unrecoverable"),
    "timeout_value": ("timeout", "deadline", "unrecoverable"),
    "multi_agent_aggregation_reduction_order": ("aggregation reduction order", "assumption", "multi-agent", "reward"),
    "Phi_n_pub_exact_formatting": ("Phi_n^pub", "Phi_n pub", "equation", "normalized_formula"),
}


def _snippet(text: str, term: str, window: int = 180) -> str:
    lower = text.lower()
    idx = lower.find(term.lower())
    if idx < 0:
        return text[: min(len(text), window)]
    start = max(0, idx - window // 2)
    end = min(len(text), idx + len(term) + window // 2)
    return text[start:end].replace("\n", " ").strip()


def _searched_source(source_path: Any, search_terms: tuple[str, ...], match_count: int, relevant_match_count: int) -> dict[str, Any]:
    return {
        "source_reference": str(source_path),
        "search_terms": list(search_terms),
        "search_method": "item_specific_term_match",
        "match_count": match_count,
        "relevant_match_count": relevant_match_count,
    }


def _negative_evidence_snippets(item_id: str, source_path: Any, text: str) -> list[dict[str, Any]]:
    snippets: list[dict[str, Any]] = []
    hints = NEGATIVE_EVIDENCE_HINTS.get(item_id, ())
    lowered = text.lower()
    for hint in hints:
        if hint.lower() in lowered:
            snippet = _snippet(text, hint)
            if snippet:
                snippets.append(
                    {
                        "source_reference": str(source_path),
                        "raw_evidence": snippet,
                        "normalized_finding": item_id,
                        "confidence": "invalid",
                        "source_type": "prior_registry_or_report_statement",
                    }
                )
            break
    return snippets


def search_evidence(item: dict[str, Any], sources: dict[Any, Any]) -> dict[str, list[dict[str, Any]]]:
    item_id = str(item.get("item_id", ""))
    matched_terms = ITEM_SEARCH_TERMS.get(item_id, ())
    positive: list[dict[str, Any]] = []
    negative: list[dict[str, Any]] = []
    searched: list[dict[str, Any]] = []
    for source_path, loaded in sources.items():
        text = loaded.payload if isinstance(loaded.payload, str) else str(loaded.payload)
        text_lower = text.lower()
        match_count = sum(1 for term in matched_terms if term.lower() in text_lower)
        relevant_match_count = 0
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
                    relevant_match_count += 1
        searched.append(_searched_source(source_path, matched_terms, match_count, relevant_match_count))
        negative.extend(_negative_evidence_snippets(item_id, source_path, text))
    return {"positive": positive, "negative": negative, "searched": searched}
