from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class CollapseAssessment:
    status: str
    outcome_signatures: list[str]
    policy_diversity: int
    notes: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "outcome_signatures": list(self.outcome_signatures),
            "policy_diversity": self.policy_diversity,
            "notes": list(self.notes),
        }


def _signature(result: dict[str, Any]) -> str:
    metrics = result.get("final_metrics", {})
    return f"completed={metrics.get('completed_tasks', 0)}::dropped={metrics.get('dropped_tasks', 0)}::throughput={metrics.get('throughput', 0)}::delay={metrics.get('average_delay', 0)}"


def classify_collapse(results: list[dict[str, Any]]) -> CollapseAssessment:
    if not results:
        return CollapseAssessment("inconclusive", [], 0, ["no results available"])

    signatures = [_signature(result) for result in results]
    distinct = sorted(set(signatures))
    completed_counts = [int(result.get("final_metrics", {}).get("completed_tasks", 0)) for result in results]
    dropped_counts = [int(result.get("final_metrics", {}).get("dropped_tasks", 0)) for result in results]

    if all(count == 0 for count in completed_counts) and any(count > 0 for count in dropped_counts):
        return CollapseAssessment("collapse_worsened", distinct, len(distinct), ["all baselines dropped every task"])
    if len(distinct) == 1:
        return CollapseAssessment("collapse_unchanged", distinct, 1, ["baseline signatures remained identical"])
    if len(distinct) > 1:
        return CollapseAssessment("collapse_reduced", distinct, len(distinct), ["baseline signatures differentiated"])
    return CollapseAssessment("inconclusive", distinct, len(distinct), ["insufficient signal"])


def classify_policy_differentiation(results: list[dict[str, Any]]) -> dict[str, Any]:
    assessment = classify_collapse(results)
    return assessment.to_dict()
