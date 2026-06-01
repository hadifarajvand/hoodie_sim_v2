from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .config import FEATURE_ID, FEATURE_NAME, READY_STATUS, REQUIRED_COMPONENT_IDS


ALLOWED_COMPONENT_STATUSES: tuple[str, ...] = ("implemented", "partial", "missing", "not_applicable")


def _is_non_empty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


@dataclass(frozen=True, slots=True)
class HoodieProposedComponent:
    component_id: str
    component_name: str
    paper_definition: str
    paper_source: str
    current_implementation: str
    implementation_reference: str
    status: str
    gap: str
    required_repair: str

    def __post_init__(self) -> None:
        if self.component_id not in REQUIRED_COMPONENT_IDS:
            raise ValueError("component_id must be one of the required HOODIE paper components")
        if not _is_non_empty_text(self.component_name):
            raise ValueError("component_name must be non-empty")
        if not _is_non_empty_text(self.paper_definition):
            raise ValueError("paper_definition must be non-empty")
        if not _is_non_empty_text(self.paper_source):
            raise ValueError("paper_source must be non-empty")
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
class HoodieProposedRepairPlanEntry:
    component_id: str
    gap_type: str
    repair_action: str
    target_files: tuple[str, ...]
    tests_needed: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.component_id not in REQUIRED_COMPONENT_IDS:
            raise ValueError("component_id must be one of the required HOODIE paper components")
        if not _is_non_empty_text(self.gap_type):
            raise ValueError("gap_type must be non-empty")
        if not _is_non_empty_text(self.repair_action):
            raise ValueError("repair_action must be non-empty")
        if not self.target_files:
            raise ValueError("target_files must be non-empty")
        if not self.tests_needed:
            raise ValueError("tests_needed must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "component_id": self.component_id,
            "gap_type": self.gap_type,
            "repair_action": self.repair_action,
            "target_files": list(self.target_files),
            "tests_needed": list(self.tests_needed),
        }


def _claim_boundary_is_explicit(claim_boundary: tuple[str, ...]) -> bool:
    combined = " ".join(claim_boundary).lower()
    required_phrases = (
        "no evaluation claim",
        "no non-paper extension claim",
        "no overclaim is made",
        "hoodie_proposed is the base-paper target",
    )
    return all(phrase in combined for phrase in required_phrases)


@dataclass(frozen=True, slots=True)
class HoodieProposedFidelityReport:
    feature_id: str
    status: str
    passed: bool
    source_pdf: str
    source_ocr: str
    component_count: int
    implemented_count: int
    partial_count: int
    missing_count: int
    not_applicable_count: int
    components: tuple[HoodieProposedComponent, ...]
    gap_summary: tuple[str, ...]
    repair_plan: tuple[HoodieProposedRepairPlanEntry, ...]
    validation_summary: tuple[str, ...]
    claim_boundary: tuple[str, ...]
    scope_evidence: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must match the Feature 081 contract")
        if self.status not in {READY_STATUS, "hoodie_proposed_fidelity_blocked"}:
            raise ValueError("status must be explicit and recognized")
        if not _is_non_empty_text(self.source_pdf):
            raise ValueError("source_pdf must be non-empty")
        if not _is_non_empty_text(self.source_ocr):
            raise ValueError("source_ocr must be non-empty")
        if self.component_count != len(self.components):
            raise ValueError("component_count must match the number of components")
        if not self.components:
            raise ValueError("components must be non-empty")
        if len(self.components) != len(REQUIRED_COMPONENT_IDS):
            raise ValueError("components must cover all required paper components")
        component_ids = [component.component_id for component in self.components]
        if len(component_ids) != len(set(component_ids)):
            raise ValueError("components must not contain duplicate component IDs")
        if set(component_ids) != set(REQUIRED_COMPONENT_IDS):
            raise ValueError("components must cover the complete required component set")
        if self.implemented_count != sum(1 for component in self.components if component.status == "implemented"):
            raise ValueError("implemented_count must match the components")
        if self.partial_count != sum(1 for component in self.components if component.status == "partial"):
            raise ValueError("partial_count must match the components")
        if self.missing_count != sum(1 for component in self.components if component.status == "missing"):
            raise ValueError("missing_count must match the components")
        if self.not_applicable_count != sum(1 for component in self.components if component.status == "not_applicable"):
            raise ValueError("not_applicable_count must match the components")
        if self.component_count != self.implemented_count + self.partial_count + self.missing_count + self.not_applicable_count:
            raise ValueError("component counts must sum to the total")
        if not self.gap_summary:
            raise ValueError("gap_summary must be non-empty")
        if not self.repair_plan:
            raise ValueError("repair_plan must be non-empty")
        if not self.validation_summary:
            raise ValueError("validation_summary must be non-empty")
        if not self.claim_boundary:
            raise ValueError("claim_boundary must be non-empty")
        if not self.scope_evidence:
            raise ValueError("scope_evidence must be non-empty")
        repair_component_ids = [entry.component_id for entry in self.repair_plan]
        expected_repair_component_ids = {
            component.component_id
            for component in self.components
            if component.status in {"partial", "missing"}
        }
        if set(repair_component_ids) != expected_repair_component_ids:
            raise ValueError("repair_plan must cover every partial or missing component exactly once")
        if len(repair_component_ids) != len(set(repair_component_ids)):
            raise ValueError("repair_plan must not contain duplicate component IDs")
        if not _claim_boundary_is_explicit(self.claim_boundary):
            raise ValueError("claim_boundary must be explicit")
        if self.passed and self.status != READY_STATUS:
            raise ValueError("passed reports must use the ready status")
        if self.passed and any("PROPOSED_DCQ" in entry for entry in self.validation_summary + self.gap_summary + self.claim_boundary):
            raise ValueError("passed reports must not expose thesis/DCQ markers")
        if self.passed and any("proposed_deadline_queueing" in entry.lower() for entry in self.validation_summary + self.gap_summary + self.claim_boundary):
            raise ValueError("passed reports must use the base-paper-safe proposed-method identity")
        if not any(component.status == "implemented" for component in self.components):
            raise ValueError("at least one component must be implemented")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "status": self.status,
            "passed": self.passed,
            "source_pdf": self.source_pdf,
            "source_ocr": self.source_ocr,
            "component_count": self.component_count,
            "implemented_count": self.implemented_count,
            "partial_count": self.partial_count,
            "missing_count": self.missing_count,
            "not_applicable_count": self.not_applicable_count,
            "components": [component.to_dict() for component in self.components],
            "gap_summary": list(self.gap_summary),
            "repair_plan": [entry.to_dict() for entry in self.repair_plan],
            "validation_summary": list(self.validation_summary),
            "claim_boundary": list(self.claim_boundary),
            "scope_evidence": list(self.scope_evidence),
        }
