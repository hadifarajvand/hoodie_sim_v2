from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Feature071RegressionEvidence:
    name: str
    passed: bool
    summary: str
    validation_commands: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "summary": self.summary,
            "validation_commands": list(self.validation_commands),
        }


@dataclass(frozen=True, slots=True)
class DeadlineEvidence:
    arrival_slot: int
    phi: int
    absolute_deadline_slot: int
    paper_mode_before_deadline_passed: bool
    paper_mode_at_deadline_failed: bool
    paper_mode_after_deadline_failed: bool
    compatibility_mode_at_deadline_passed: bool
    paper_mode_default: bool
    compatibility_mode_explicit: bool
    runtime_compatibility_note: str

    @property
    def passed(self) -> bool:
        return all(
            (
                self.paper_mode_default,
                self.paper_mode_before_deadline_passed,
                self.paper_mode_at_deadline_failed,
                self.paper_mode_after_deadline_failed,
                self.compatibility_mode_at_deadline_passed,
                self.compatibility_mode_explicit,
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class TerminalStateEvidence:
    completed_private_without_drop_reason: bool
    completed_public_without_drop_reason: bool
    completed_cloud_without_drop_reason: bool
    dropped_timeout_requires_terminal_slot_and_drop_reason: bool
    dropped_unavailable_requires_terminal_slot_and_drop_reason: bool
    pending_cannot_emit_reward: bool
    terminal_evidence_explicit_before_reward: bool

    @property
    def passed(self) -> bool:
        return all(
            (
                self.completed_private_without_drop_reason,
                self.completed_public_without_drop_reason,
                self.completed_cloud_without_drop_reason,
                self.dropped_timeout_requires_terminal_slot_and_drop_reason,
                self.dropped_unavailable_requires_terminal_slot_and_drop_reason,
                self.pending_cannot_emit_reward,
                self.terminal_evidence_explicit_before_reward,
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RewardRuntimeEvidence:
    equation_20_inactive_sentinel_is_explicit: bool
    equation_20_success_reward_is_negative_phi: bool
    equation_20_drop_reward_is_negative_c: bool
    equation_21_private_selection_is_explicit: bool
    equation_21_public_selection_is_explicit: bool
    equation_22_private_example_phi: int
    equation_22_private_example_passed: bool
    reward_for_terminal_task_default_completion_reward: float
    reward_for_terminal_task_compatibility_completion_reward: float
    reward_for_terminal_task_default_uses_plus_one: bool
    reward_for_terminal_task_compatibility_preserves_old_approximation: bool
    equation_23_public_example_phi: int
    equation_23_public_example_passed: bool
    inactive_reward_behavior: str
    reward_emission_after_terminal_evidence: bool
    reward_slot_convention: str

    @property
    def passed(self) -> bool:
        return all(
            (
                self.equation_20_inactive_sentinel_is_explicit,
                self.equation_20_success_reward_is_negative_phi,
                self.equation_20_drop_reward_is_negative_c,
                self.equation_21_private_selection_is_explicit,
                self.equation_21_public_selection_is_explicit,
                self.equation_22_private_example_passed,
                self.reward_for_terminal_task_default_uses_plus_one,
                self.reward_for_terminal_task_compatibility_preserves_old_approximation,
                self.equation_23_public_example_passed,
                self.reward_emission_after_terminal_evidence,
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RuntimeCompatibilityEvidence:
    legacy_behavior_name: str
    paper_behavior_name: str
    divergence_description: str
    compatibility_mode_available: bool
    paper_mode_default_in_feature_071: bool
    build_timeout_contract_default_is_paper: bool
    build_timeout_contract_compatibility_is_explicit: bool
    deadline_rules_default_is_paper: bool
    deadline_rules_compatibility_is_explicit: bool
    reward_for_terminal_task_default_is_paper: bool
    reward_for_terminal_task_compatibility_is_explicit: bool
    no_call_stack_compatibility_bypass: bool

    @property
    def passed(self) -> bool:
        return all(
            (
                self.compatibility_mode_available,
                self.paper_mode_default_in_feature_071,
                self.build_timeout_contract_default_is_paper,
                self.build_timeout_contract_compatibility_is_explicit,
                self.deadline_rules_default_is_paper,
                self.deadline_rules_compatibility_is_explicit,
                self.reward_for_terminal_task_default_is_paper,
                self.reward_for_terminal_task_compatibility_is_explicit,
                self.no_call_stack_compatibility_bypass,
                bool(self.divergence_description),
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Feature071Report:
    feature_name: str
    status: str
    passed: bool
    changed_files: tuple[str, ...]
    deadline_evidence: DeadlineEvidence
    terminal_state_evidence: TerminalStateEvidence
    reward_runtime_evidence: RewardRuntimeEvidence
    compatibility_evidence: RuntimeCompatibilityEvidence
    feature_068r_regression_status: Feature071RegressionEvidence
    feature_069_regression_status: Feature071RegressionEvidence
    feature_070_regression_status: Feature071RegressionEvidence
    paper_claim_boundary: str
    recommended_next_feature: str

    def __post_init__(self) -> None:
        if self.feature_name != "Feature 071 - Runtime Paper-Faithful Semantics Alignment":
            raise ValueError("feature_name must match the Feature 071 contract")
        if self.passed and self.status != "runtime_paper_faithful_semantics_alignment_ready":
            raise ValueError("passed reports must use the ready status")
        if self.passed and not all(
            (
                self.deadline_evidence.passed,
                self.terminal_state_evidence.passed,
                self.reward_runtime_evidence.passed,
                self.compatibility_evidence.passed,
                self.feature_068r_regression_status.passed,
                self.feature_069_regression_status.passed,
                self.feature_070_regression_status.passed,
            )
        ):
            raise ValueError("passed reports require all evidence and regression gates to pass")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_name": self.feature_name,
            "status": self.status,
            "passed": self.passed,
            "changed_files": list(self.changed_files),
            "deadline_evidence": self.deadline_evidence.to_dict(),
            "terminal_state_evidence": self.terminal_state_evidence.to_dict(),
            "reward_runtime_evidence": self.reward_runtime_evidence.to_dict(),
            "compatibility_evidence": self.compatibility_evidence.to_dict(),
            "feature_068r_regression_status": self.feature_068r_regression_status.to_dict(),
            "feature_069_regression_status": self.feature_069_regression_status.to_dict(),
            "feature_070_regression_status": self.feature_070_regression_status.to_dict(),
            "paper_claim_boundary": self.paper_claim_boundary,
            "recommended_next_feature": self.recommended_next_feature,
        }
