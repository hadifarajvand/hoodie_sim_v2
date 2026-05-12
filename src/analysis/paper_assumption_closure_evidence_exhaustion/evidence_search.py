from __future__ import annotations

from typing import Any
import json


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

NEGATIVE_SOURCE_HINTS = (
    "/recovered/topology-g.json",
    "/recovered/paper-parameter-registry.json",
    "topology-recovery-report.json",
    "unit-validation-report.json",
    "reward-contract-report.json",
    "paper-mechanism-registry.json",
)

OCR_SOURCE_HINTS = ("/ocr/", "HOODIE_paper.pdf")


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


def _is_negative_source(source_path: Any) -> bool:
    path = str(source_path)
    return any(hint in path for hint in NEGATIVE_SOURCE_HINTS) and not any(hint in path for hint in OCR_SOURCE_HINTS)


def _negative_evidence_snippets(item_id: str, source_path: Any, payload: Any) -> list[dict[str, Any]]:
    if not _is_negative_source(source_path):
        return []

    path = str(source_path)
    snippets: list[dict[str, Any]] = []

    def add_record(raw: Any, normalized: str | None = None) -> None:
        if raw is None:
            return
        if isinstance(raw, str):
            raw_text = raw.strip()
        else:
            raw_text = json.dumps(raw, sort_keys=True, default=str, separators=(",", ":"))
        if len(raw_text) > 380:
            raw_text = raw_text[:377] + "..."
        if not raw_text:
            return
        snippets.append(
            {
                "source_reference": path,
                "raw_evidence": raw_text,
                "normalized_finding": normalized or item_id,
                "confidence": "invalid",
                "source_type": "prior_registry_or_report_statement",
            }
        )

    if path.endswith("topology-g.json") and isinstance(payload, dict):
        if item_id == "Figure_7_adjacency":
            add_record(
                {
                    "adjacency_matrix_status": payload.get("adjacency_matrix_status"),
                    "edge_cloud_connectivity_status": (payload.get("edge_cloud_connectivity") or {}).get("recovery_status"),
                    "edge_cloud_connectivity_value": (payload.get("edge_cloud_connectivity") or {}).get("value"),
                    "unrecoverable_items": payload.get("unrecoverable_items"),
                }
            )
        elif item_id == "legal_horizontal_destinations":
            add_record(
                {
                    "legal_horizontal_destinations": payload.get("legal_horizontal_destinations"),
                    "adjacency_matrix_status": payload.get("adjacency_matrix_status"),
                    "unrecoverable_items": payload.get("unrecoverable_items"),
                }
            )
        return snippets

    if path.endswith("paper-parameter-registry.json") and isinstance(payload, dict):
        if item_id in {"EA_private_cpu_capacity", "EA_public_cpu_capacity", "cloud_cpu_capacity"}:
            cpu_key = {
                "EA_private_cpu_capacity": "EA_private",
                "EA_public_cpu_capacity": "EA_public",
                "cloud_cpu_capacity": "cloud",
            }[item_id]
            add_record(
                {
                    "cpu_capacity_status": (payload.get("cpu_capacities", {}).get(cpu_key) or {}).get("recovery_status"),
                    "cpu_capacity_value": (payload.get("cpu_capacities", {}).get(cpu_key) or {}).get("value"),
                    "unrecoverable_items": payload.get("unrecoverable_items"),
                }
            )
        elif item_id == "cloud_data_rate":
            add_record(
                {
                    "cloud_data_rate_status": (payload.get("cloud_data_rate") or {}).get("recovery_status"),
                    "cloud_data_rate_value": (payload.get("cloud_data_rate") or {}).get("value"),
                    "unrecoverable_items": payload.get("unrecoverable_items"),
                }
            )
        elif item_id == "timeout_value":
            add_record(
                {
                    "timeout_value_status": (payload.get("timeout_values") or {}).get("recovery_status"),
                    "timeout_value_value": (payload.get("timeout_values") or {}).get("value"),
                    "unrecoverable_items": payload.get("unrecoverable_items"),
                }
            )
        return snippets

    if path.endswith("topology-recovery-report.json") and isinstance(payload, dict):
        add_record(
            {
                "topology_summary_status": (payload.get("topology_summary") or {}).get("recovery_status"),
                "topology_summary_unrecoverable_items": (payload.get("topology_summary") or {}).get("unrecoverable_items"),
                "unrecoverable_items": payload.get("unrecoverable_items"),
            }
        )
        return snippets

    if path.endswith("unit-validation-report.json") and isinstance(payload, dict):
        if item_id in {"EA_private_cpu_capacity", "EA_public_cpu_capacity", "cloud_cpu_capacity"}:
            add_record(
                {
                    "cpu_capacity_contract_status": (payload.get("cpu_capacity_contract") or {}).get("runtime"),
                    "cpu_capacity_contract_values": {
                        key: (payload.get("cpu_capacity_contract") or {}).get(key)
                        for key in ("EA_private", "EA_public", "cloud")
                    },
                    "unrecoverable_items": payload.get("unrecoverable_items"),
                }
            )
        elif item_id == "timeout_value":
            add_record(
                {
                    "runtime_timeout_slots": (payload.get("runtime_unit_contract") or {}).get("runtime_timeout_slots"),
                    "runtime_timeout_source": (payload.get("runtime_unit_contract") or {}).get("runtime_timeout_source"),
                    "unrecoverable_items": payload.get("unrecoverable_items"),
                }
            )
        return snippets

    if path.endswith("reward-contract-report.json") and isinstance(payload, dict):
        if item_id == "multi_agent_aggregation_reduction_order":
            add_record(
                {
                    "aggregation_contract_exact_reduction_order": (payload.get("aggregation_contract") or {}).get("exact_reduction_order"),
                    "aggregation_contract_average_across": (payload.get("aggregation_contract") or {}).get("average_across_distributed_agents"),
                    "unrecoverable_items": payload.get("unrecoverable_items"),
                    "assumption_backed_items": payload.get("assumption_backed_items"),
                }
            )
        return snippets

    if path.endswith("paper-mechanism-registry.json") and isinstance(payload, dict):
        add_record(
            {
                "blocking_gap_count": len(payload.get("blocking_gaps", [])),
                "implementation_gap_summary_missing": (payload.get("implementation_gap_summary") or {}).get("missing"),
                "high_risk_assumption_count": len(payload.get("high_risk_assumptions", [])),
            }
        )
        return snippets

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
        negative.extend(_negative_evidence_snippets(item_id, source_path, loaded.payload))
    return {"positive": positive, "negative": negative, "searched": searched}
