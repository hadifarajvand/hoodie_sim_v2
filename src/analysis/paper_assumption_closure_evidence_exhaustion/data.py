from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class EvidenceRecord:
    source_type: str
    source_reference: str
    raw_evidence: str
    normalized_finding: str
    confidence: str
    contradiction_notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class EvidenceItem:
    item_id: str
    domain: str
    title: str
    description: str
    status: str
    confidence: str
    runtime_approval_required: bool
    positive_evidence: list[EvidenceRecord] = field(default_factory=list)
    negative_evidence: list[EvidenceRecord] = field(default_factory=list)
    searched_sources: list[dict[str, Any]] = field(default_factory=list)
    normalized_finding: str = ""
    evidence_exhaustion_rationale: str = ""
    manual_visual_recovery: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["positive_evidence"] = [record.to_dict() for record in self.positive_evidence]
        data["negative_evidence"] = [record.to_dict() for record in self.negative_evidence]
        return data


@dataclass(slots=True)
class ReportSummary:
    total_items: int
    by_status: dict[str, int]
    by_confidence: dict[str, int]
    manual_review_count: int
    approval_required_count: int
    unrecoverable_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ReportArtifact:
    feature_id: str
    schema_version: str
    source_gates: list[dict[str, str]]
    inventory_summary: ReportSummary
    items: list[EvidenceItem]
    recovered_items: list[dict[str, Any]]
    partially_recovered_items: list[dict[str, Any]]
    contradicted_items: list[dict[str, Any]]
    assumption_backed_items: list[dict[str, Any]]
    unrecoverable_after_evidence_exhaustion_items: list[dict[str, Any]]
    out_of_scope_items: list[dict[str, Any]]
    manual_review_required_items: list[dict[str, Any]]
    runtime_dependency_decisions: dict[str, Any]
    no_training_or_policy_drift: bool
    no_dependency_drift: bool
    final_verdict: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "schema_version": self.schema_version,
            "source_gates": list(self.source_gates),
            "inventory_summary": self.inventory_summary.to_dict(),
            "items": [item.to_dict() for item in self.items],
            "recovered_items": list(self.recovered_items),
            "partially_recovered_items": list(self.partially_recovered_items),
            "contradicted_items": list(self.contradicted_items),
            "assumption_backed_items": list(self.assumption_backed_items),
            "unrecoverable_after_evidence_exhaustion_items": list(self.unrecoverable_after_evidence_exhaustion_items),
            "out_of_scope_items": list(self.out_of_scope_items),
            "manual_review_required_items": list(self.manual_review_required_items),
            "runtime_dependency_decisions": dict(self.runtime_dependency_decisions),
            "no_training_or_policy_drift": self.no_training_or_policy_drift,
            "no_dependency_drift": self.no_dependency_drift,
            "final_verdict": self.final_verdict,
        }
