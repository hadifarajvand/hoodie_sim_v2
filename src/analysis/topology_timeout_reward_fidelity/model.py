from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Feature070Blocker:
    category: str
    severity: str
    description: str
    evidence_source: str
    next_action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class TopologyEvidenceReport:
    source_agent_id: str
    edge_agent_ids: tuple[str, ...]
    cloud_id: str
    adjacency_matrix_source: str
    neighbor_map: dict[str, tuple[str, ...]]
    cloud_reachability: bool
    evidence_status: str
    provenance: str = ""
    blockers: tuple[Feature070Blocker, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_agent_id": self.source_agent_id,
            "edge_agent_ids": list(self.edge_agent_ids),
            "cloud_id": self.cloud_id,
            "adjacency_matrix_source": self.adjacency_matrix_source,
            "neighbor_map": {key: list(value) for key, value in self.neighbor_map.items()},
            "cloud_reachability": self.cloud_reachability,
            "evidence_status": self.evidence_status,
            "provenance": self.provenance,
            "blockers": [blocker.to_dict() for blocker in self.blockers],
        }


@dataclass(frozen=True, slots=True)
class NeighborLegalityEvidence:
    source_agent_id: str
    destination_agent_id: str
    is_neighbor: bool
    is_self_destination: bool
    legal_under_topology: bool
    legal_under_action_mask: bool
    final_legal: bool
    blockers: tuple[Feature070Blocker, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_agent_id": self.source_agent_id,
            "destination_agent_id": self.destination_agent_id,
            "is_neighbor": self.is_neighbor,
            "is_self_destination": self.is_self_destination,
            "legal_under_topology": self.legal_under_topology,
            "legal_under_action_mask": self.legal_under_action_mask,
            "final_legal": self.final_legal,
            "blockers": [blocker.to_dict() for blocker in self.blockers],
        }


@dataclass(frozen=True, slots=True)
class TimeoutDropAccountingEvidence:
    task_id: str
    arrival_slot: int
    timeout_length: int
    absolute_deadline_slot: int
    completion_slot: int | None
    terminal_slot: int | None
    terminal_status: str
    drop_reason: str | None
    paper_semantics_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RewardEquationEvidence:
    equation_id: str
    equation_text: str
    source_reference: str
    terms: tuple[str, ...]
    recovered_status: str
    assumption_status: str
    blockers: tuple[Feature070Blocker, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "equation_id": self.equation_id,
            "equation_text": self.equation_text,
            "source_reference": self.source_reference,
            "terms": list(self.terms),
            "recovered_status": self.recovered_status,
            "assumption_status": self.assumption_status,
            "blockers": [blocker.to_dict() for blocker in self.blockers],
        }


@dataclass(frozen=True, slots=True)
class TerminalRewardEvidence:
    task_id: str
    selected_action: str
    terminal_status: str
    terminal_slot: int
    reward_slot: int
    reward_value: float | None
    reward_equation_id: str | None
    timing_valid: bool
    blockers: tuple[Feature070Blocker, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "selected_action": self.selected_action,
            "terminal_status": self.terminal_status,
            "terminal_slot": self.terminal_slot,
            "reward_slot": self.reward_slot,
            "reward_value": self.reward_value,
            "reward_equation_id": self.reward_equation_id,
            "timing_valid": self.timing_valid,
            "blockers": [blocker.to_dict() for blocker in self.blockers],
        }


@dataclass(frozen=True, slots=True)
class Feature068RRegressionEvidence:
    registry_coverage_passed: bool
    legal_mask_authority_passed: bool
    family_fallback_passed: bool
    seeded_ro_passed: bool
    bco_balance_hint_passed: bool
    mleo_candidate_metadata_passed: bool
    validation_commands: tuple[str, ...]
    summary: str

    @property
    def passed(self) -> bool:
        return all(
            (
                self.registry_coverage_passed,
                self.legal_mask_authority_passed,
                self.family_fallback_passed,
                self.seeded_ro_passed,
                self.bco_balance_hint_passed,
                self.mleo_candidate_metadata_passed,
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "registry_coverage_passed": self.registry_coverage_passed,
            "legal_mask_authority_passed": self.legal_mask_authority_passed,
            "family_fallback_passed": self.family_fallback_passed,
            "seeded_ro_passed": self.seeded_ro_passed,
            "bco_balance_hint_passed": self.bco_balance_hint_passed,
            "mleo_candidate_metadata_passed": self.mleo_candidate_metadata_passed,
            "validation_commands": list(self.validation_commands),
            "summary": self.summary,
            "passed": self.passed,
        }


@dataclass(frozen=True, slots=True)
class Feature069RegressionEvidence:
    mechanism_report_generated_passed: bool
    blocker_separation_passed: bool
    claim_boundary_passed: bool
    scope_guard_passed: bool
    read_only_evidence_passed: bool
    validation_commands: tuple[str, ...]
    summary: str

    @property
    def passed(self) -> bool:
        return all(
            (
                self.mechanism_report_generated_passed,
                self.blocker_separation_passed,
                self.claim_boundary_passed,
                self.scope_guard_passed,
                self.read_only_evidence_passed,
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "mechanism_report_generated_passed": self.mechanism_report_generated_passed,
            "blocker_separation_passed": self.blocker_separation_passed,
            "claim_boundary_passed": self.claim_boundary_passed,
            "scope_guard_passed": self.scope_guard_passed,
            "read_only_evidence_passed": self.read_only_evidence_passed,
            "validation_commands": list(self.validation_commands),
            "summary": self.summary,
            "passed": self.passed,
        }


@dataclass(frozen=True, slots=True)
class Feature070FidelityReport:
    feature_name: str
    status: str
    passed: bool
    changed_files: tuple[str, ...]
    topology_evidence: TopologyEvidenceReport
    neighbor_legality_evidence: NeighborLegalityEvidence
    timeout_drop_accounting_evidence: TimeoutDropAccountingEvidence
    reward_equation_evidence: RewardEquationEvidence
    terminal_reward_evidence: TerminalRewardEvidence
    blockers: tuple[Feature070Blocker, ...]
    feature_068r_regression_status: Feature068RRegressionEvidence
    feature_069_regression_status: Feature069RegressionEvidence
    paper_claim_boundary: str
    recommended_next_feature: str

    def __post_init__(self) -> None:
        if self.feature_name != "Feature 070 - Topology, Timeout/Drop, and Reward Fidelity":
            raise ValueError("feature_name must match the Feature 070 contract")
        blocker_categories = [blocker.category for blocker in self.blockers]
        if len(blocker_categories) != len(set(blocker_categories)):
            raise ValueError("blockers categories must be unique")
        if self.passed and not (self.feature_068r_regression_status.passed and self.feature_069_regression_status.passed):
            raise ValueError("passed reports require green Feature 068R and Feature 069 regression gates")
        if self.passed and self.blockers:
            raise ValueError("passed reports must not carry blockers")
        if self.passed and not self.terminal_reward_evidence.timing_valid:
            raise ValueError("passed reports require valid terminal reward timing")
        if self.passed and self.terminal_reward_evidence.reward_slot < self.terminal_reward_evidence.terminal_slot:
            raise ValueError("passed reports require reward_slot to be at or after terminal_slot")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_name": self.feature_name,
            "status": self.status,
            "passed": self.passed,
            "changed_files": list(self.changed_files),
            "topology_evidence": self.topology_evidence.to_dict(),
            "neighbor_legality_evidence": self.neighbor_legality_evidence.to_dict(),
            "timeout_drop_accounting_evidence": self.timeout_drop_accounting_evidence.to_dict(),
            "reward_equation_evidence": self.reward_equation_evidence.to_dict(),
            "terminal_reward_evidence": self.terminal_reward_evidence.to_dict(),
            "blockers": [blocker.to_dict() for blocker in self.blockers],
            "feature_068r_regression_status": self.feature_068r_regression_status.to_dict(),
            "feature_069_regression_status": self.feature_069_regression_status.to_dict(),
            "paper_claim_boundary": self.paper_claim_boundary,
            "recommended_next_feature": self.recommended_next_feature,
        }
