from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


def _serialize(value: Any) -> Any:
    return value.to_dict() if hasattr(value, "to_dict") else value


def _validate_nonempty_unique(entries: list[MechanismContractResult]) -> None:
    names = [entry.name for entry in entries]
    if len(names) != len(set(names)):
        raise ValueError("mechanism_contracts names must be unique")


@dataclass(frozen=True, slots=True)
class MechanismBlocker:
    category: str
    severity: str
    description: str
    evidence_source: str
    next_action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class QueuePressureEvidence:
    queue_id: str
    queue_type: str
    length_before: int
    length_after: int
    waiting_time_estimate: float | None
    service_effect: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CoordinationGraphContract:
    source_agent_id: str
    neighbor_ids: tuple[str, ...]
    cloud_reachable: bool
    evidence_source: str
    assumption_status: str
    blockers: tuple[MechanismBlocker, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_agent_id": self.source_agent_id,
            "neighbor_ids": list(self.neighbor_ids),
            "cloud_reachable": self.cloud_reachable,
            "evidence_source": self.evidence_source,
            "assumption_status": self.assumption_status,
            "blockers": [blocker.to_dict() for blocker in self.blockers],
        }


@dataclass(frozen=True, slots=True)
class SynchronizationContract:
    slot_index: int
    decision_phase: str
    action_application_phase: str
    queue_update_phase: str
    terminal_accounting_phase: str
    reward_emission_phase: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DelayedRewardContract:
    task_id: str
    selected_action: str
    terminal_outcome: str
    reward_emitted_at: str
    reward_equation_status: str
    blockers: tuple[MechanismBlocker, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "selected_action": self.selected_action,
            "terminal_outcome": self.terminal_outcome,
            "reward_emitted_at": self.reward_emitted_at,
            "reward_equation_status": self.reward_equation_status,
            "blockers": [blocker.to_dict() for blocker in self.blockers],
        }


@dataclass(frozen=True, slots=True)
class CongestionControlContract:
    private_queue_pressure: QueuePressureEvidence | None
    public_queue_pressure: QueuePressureEvidence | None
    cloud_queue_pressure: QueuePressureEvidence | None
    placement_action: str
    observed_delay_effect: str
    compatibility_fallback: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "private_queue_pressure": _serialize(self.private_queue_pressure),
            "public_queue_pressure": _serialize(self.public_queue_pressure),
            "cloud_queue_pressure": _serialize(self.cloud_queue_pressure),
            "placement_action": self.placement_action,
            "observed_delay_effect": self.observed_delay_effect,
            "compatibility_fallback": self.compatibility_fallback,
        }


@dataclass(frozen=True, slots=True)
class TimeoutDropEvidence:
    task_id: str
    deadline_or_timeout: str
    completion_time: str | None
    drop_status: str
    accounting_phase: str
    blocker_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RewardPipelineEvidence:
    task_id: str
    decision_slot: int
    terminal_slot: int
    reward_slot: int
    reward_value: float | None
    equation_source: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Feature068RRegressionEvidence:
    registry_coverage_passed: bool
    legal_mask_authority_passed: bool
    family_fallback_passed: bool
    seeded_ro_passed: bool
    bco_balance_hint_passed: bool
    mleo_candidate_metadata_passed: bool
    validation_commands: tuple[str, ...] = ()

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
            "passed": self.passed,
        }


@dataclass(frozen=True, slots=True)
class MechanismContractResult:
    name: str
    category: str
    status: str
    verified_behavior: str
    compatibility_fallback: str
    assumption_backed_behavior: str
    blockers: tuple[str, ...]
    evidence_files: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "status": self.status,
            "verified_behavior": self.verified_behavior,
            "compatibility_fallback": self.compatibility_fallback,
            "assumption_backed_behavior": self.assumption_backed_behavior,
            "blockers": list(self.blockers),
            "evidence_files": list(self.evidence_files),
        }


@dataclass(frozen=True, slots=True)
class MechanismFidelityReport:
    feature_name: str
    status: str
    passed: bool
    changed_files: tuple[str, ...]
    mechanism_contracts: tuple[MechanismContractResult, ...]
    blockers: tuple[MechanismBlocker, ...]
    validation_commands: tuple[str, ...]
    feature_068r_regression_status: Feature068RRegressionEvidence
    paper_claim_boundary: str
    recommended_next_feature: str
    coordination_graph_contract: CoordinationGraphContract
    synchronization_contract: SynchronizationContract
    delayed_reward_contract: DelayedRewardContract
    congestion_control_contract: CongestionControlContract
    timeout_drop_evidence: TimeoutDropEvidence
    reward_pipeline_evidence: RewardPipelineEvidence

    def __post_init__(self) -> None:
        if self.feature_name != "Feature 069 - Full HOODIE Mechanism Fidelity Batch":
            raise ValueError("feature_name must match the Feature 069 contract")
        _validate_nonempty_unique(list(self.mechanism_contracts))
        if not self.validation_commands:
            raise ValueError("validation_commands must not be empty")
        if self.passed and not self.feature_068r_regression_status.passed:
            raise ValueError("passed reports require a green Feature 068R regression gate")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_name": self.feature_name,
            "status": self.status,
            "passed": self.passed,
            "changed_files": list(self.changed_files),
            "mechanism_contracts": [contract.to_dict() for contract in self.mechanism_contracts],
            "blockers": [blocker.to_dict() for blocker in self.blockers],
            "validation_commands": list(self.validation_commands),
            "feature_068r_regression_status": self.feature_068r_regression_status.to_dict(),
            "paper_claim_boundary": self.paper_claim_boundary,
            "recommended_next_feature": self.recommended_next_feature,
            "coordination_graph_contract": self.coordination_graph_contract.to_dict(),
            "synchronization_contract": self.synchronization_contract.to_dict(),
            "delayed_reward_contract": self.delayed_reward_contract.to_dict(),
            "congestion_control_contract": self.congestion_control_contract.to_dict(),
            "timeout_drop_evidence": self.timeout_drop_evidence.to_dict(),
            "reward_pipeline_evidence": self.reward_pipeline_evidence.to_dict(),
        }
