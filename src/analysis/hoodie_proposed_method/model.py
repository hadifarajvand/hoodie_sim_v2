from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .config import (
    ALLOWED_COMPONENT_STATUSES,
    ALLOWED_READINESS_LEVELS,
    BLOCKED_STATUS,
    FEATURE_ID,
    READY_STATUS,
    REQUIRED_COMPONENT_IDS,
    TARGET_METHOD_ID,
)


def _is_non_empty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


@dataclass(frozen=True, slots=True)
class ComponentCoverageEntry:
    component_id: str
    component_name: str
    paper_requirement: str
    current_implementation: str
    implementation_reference: str
    status: str
    gap: str
    required_repair: str

    def __post_init__(self) -> None:
        if self.component_id not in REQUIRED_COMPONENT_IDS:
            raise ValueError("component_id must be one of the required components")
        if not _is_non_empty_text(self.component_name):
            raise ValueError("component_name must be non-empty")
        if not _is_non_empty_text(self.paper_requirement):
            raise ValueError("paper_requirement must be non-empty")
        if not _is_non_empty_text(self.current_implementation):
            raise ValueError("current_implementation must be non-empty")
        if not _is_non_empty_text(self.implementation_reference):
            raise ValueError("implementation_reference must be non-empty")
        if self.status not in ALLOWED_COMPONENT_STATUSES:
            raise ValueError("status must be explicit and recognized")
        if not _is_non_empty_text(self.gap):
            raise ValueError("gap must be non-empty")
        if not _is_non_empty_text(self.required_repair):
            raise ValueError("required_repair must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class HoodieProposedMethodReport:
    feature_id: str
    status: str
    passed: bool
    component_count: int
    implemented_count: int
    partial_count: int
    missing_count: int
    formula_registry: tuple[Any, ...]
    component_coverage: tuple[ComponentCoverageEntry, ...]
    remaining_gaps: tuple[str, ...]
    readiness_level: str
    validation_summary: tuple[str, ...]
    claim_boundary: tuple[str, ...]
    scope_evidence: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must match the Feature 080 contract")
        if self.status not in {READY_STATUS, BLOCKED_STATUS}:
            raise ValueError("status must be explicit and recognized")
        if self.readiness_level not in ALLOWED_READINESS_LEVELS:
            raise ValueError("readiness_level must be explicit and recognized")
        if self.component_count != len(self.component_coverage):
            raise ValueError("component_count must match component_coverage")
        if not self.component_coverage:
            raise ValueError("component_coverage must be non-empty")
        if self.implemented_count != sum(1 for component in self.component_coverage if component.status == "implemented"):
            raise ValueError("implemented_count must match component_coverage")
        if self.partial_count != sum(1 for component in self.component_coverage if component.status == "partial"):
            raise ValueError("partial_count must match component_coverage")
        if self.missing_count != sum(1 for component in self.component_coverage if component.status == "missing"):
            raise ValueError("missing_count must match component_coverage")
        if self.component_count != self.implemented_count + self.partial_count + self.missing_count:
            raise ValueError("component counts must sum to component_count")
        if len({component.component_id for component in self.component_coverage}) != len(self.component_coverage):
            raise ValueError("component_coverage must not contain duplicate component IDs")
        if not self.formula_registry:
            raise ValueError("formula_registry must be non-empty")
        if not self.remaining_gaps:
            raise ValueError("remaining_gaps must be non-empty")
        if not self.validation_summary:
            raise ValueError("validation_summary must be non-empty")
        if not self.claim_boundary:
            raise ValueError("claim_boundary must be non-empty")
        if not self.scope_evidence:
            raise ValueError("scope_evidence must be non-empty")
        if any(not _is_non_empty_text(item) for item in self.remaining_gaps):
            raise ValueError("remaining_gaps must contain explicit text")
        if any(not _is_non_empty_text(item) for item in self.validation_summary):
            raise ValueError("validation_summary must contain explicit text")
        if any(not _is_non_empty_text(item) for item in self.claim_boundary):
            raise ValueError("claim_boundary must contain explicit text")
        if any(not _is_non_empty_text(item) for item in self.scope_evidence):
            raise ValueError("scope_evidence must contain explicit text")
        if self.missing_count > 0 and self.readiness_level == "fully_implemented":
            raise ValueError("fully_implemented requires zero missing components")
        if self.partial_count > 0 and self.readiness_level == "fully_implemented":
            raise ValueError("fully_implemented requires zero partial components")
        if self.passed and self.status != READY_STATUS:
            raise ValueError("passed reports must use the ready status")
        if self.passed and self.readiness_level == "blocked":
            raise ValueError("passed reports cannot be blocked")
        if self.passed and TARGET_METHOD_ID != "HOODIE_PROPOSED":
            raise ValueError("target method identity must remain base-paper HOODIE_PROPOSED")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "status": self.status,
            "passed": self.passed,
            "component_count": self.component_count,
            "implemented_count": self.implemented_count,
            "partial_count": self.partial_count,
            "missing_count": self.missing_count,
            "formula_registry": [entry.to_dict() if hasattr(entry, "to_dict") else dict(entry) for entry in self.formula_registry],
            "component_coverage": [component.to_dict() for component in self.component_coverage],
            "remaining_gaps": list(self.remaining_gaps),
            "readiness_level": self.readiness_level,
            "validation_summary": list(self.validation_summary),
            "claim_boundary": list(self.claim_boundary),
            "scope_evidence": list(self.scope_evidence),
        }
