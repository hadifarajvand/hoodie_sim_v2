from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .config import FEATURE_ID, READY_NEXT_FEATURE

ALLOWED_FINAL_VERDICTS = (
    "training_readiness_contract_ready_for_smoke_run",
    "evidence_chain_prerequisite_blocked",
    "paper_default_config_contract_blocked",
    "observation_contract_blocked",
    "action_or_legality_contract_blocked",
    "reward_timeout_capacity_contract_blocked",
    "metric_or_artifact_contract_blocked",
    "behavior_drift_detected",
)

LOCK_FIELD_NAMES = (
    "paper_default_config_locked",
    "observation_contract_locked",
    "action_contract_locked",
    "legality_contract_locked",
    "reward_contract_locked",
    "timeout_contract_locked",
    "capacity_contract_locked",
    "transmission_contract_locked",
    "queue_contract_locked",
    "metric_contract_locked",
    "seed_contract_locked",
    "artifact_contract_locked",
)

NO_Drift_FIELD_NAMES = (
    "no_training_started",
    "no_optimizer_step",
    "no_replay_training",
    "no_target_update_execution",
    "no_checkpoint_written",
    "no_campaign_run",
    "no_policy_drift",
    "no_runtime_semantic_changes",
    "no_dependency_drift",
    "no_prior_artifact_rewrite",
    "no_paper_reproduction_claim",
)


def _normalize_behavior_summary(summary: Any) -> tuple[bool, list[str]]:
    if hasattr(summary, "passed"):
        checks = list(getattr(summary, "checks", []))
        passed = bool(getattr(summary, "passed"))
    elif isinstance(summary, dict):
        checks = list(summary.get("checks", []))
        passed = bool(summary.get("passed"))
    else:
        raise ValueError("behavior_equivalence_summary must be a summary object or mapping")

    names = [str(check.get("name")) for check in checks]
    if len(names) != len(set(names)):
        raise ValueError("behavior-equivalence check names must be unique")
    if passed != all(bool(check.get("verified")) for check in checks):
        raise ValueError("behavior_equivalence_summary.passed must match the verification results")
    return passed, names


def _ensure_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean")
    return value


@dataclass(frozen=True, slots=True)
class BehaviorEquivalenceSummary:
    checks: list[dict[str, Any]]
    passed: bool

    def __post_init__(self) -> None:
        _normalize_behavior_summary(self)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class TrainingReadinessContractReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    prior_feature_gates_verified: list[dict[str, Any]]
    feature_053_readiness_verified: bool
    evidence_chain_ready_for_training_contract: bool
    paper_default_config_locked: bool
    observation_contract_locked: bool
    action_contract_locked: bool
    legality_contract_locked: bool
    reward_contract_locked: bool
    timeout_contract_locked: bool
    capacity_contract_locked: bool
    transmission_contract_locked: bool
    queue_contract_locked: bool
    metric_contract_locked: bool
    seed_contract_locked: bool
    artifact_contract_locked: bool
    behavior_equivalence_summary: BehaviorEquivalenceSummary | dict[str, Any]
    behavior_equivalence_passed: bool
    training_execution_allowed_next: bool
    remaining_blockers: list[str]
    recommended_next_feature: str
    no_training_started: bool = True
    no_optimizer_step: bool = True
    no_replay_training: bool = True
    no_target_update_execution: bool = True
    no_checkpoint_written: bool = True
    no_campaign_run: bool = True
    no_policy_drift: bool = True
    no_runtime_semantic_changes: bool = True
    no_dependency_drift: bool = True
    no_prior_artifact_rewrite: bool = True
    no_paper_reproduction_claim: bool = True
    final_verdict: str = "evidence_chain_prerequisite_blocked"

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 054-training-readiness-contract")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("invalid final_verdict")

        for field_name in (
            "feature_053_readiness_verified",
            "evidence_chain_ready_for_training_contract",
            *LOCK_FIELD_NAMES,
            "behavior_equivalence_passed",
            "training_execution_allowed_next",
            *NO_Drift_FIELD_NAMES,
        ):
            _ensure_bool(getattr(self, field_name), field_name)

        summary_passed, _check_names = _normalize_behavior_summary(self.behavior_equivalence_summary)
        if self.behavior_equivalence_passed != summary_passed:
            raise ValueError("behavior_equivalence_passed must match behavior_equivalence_summary.passed")

        prior_gate_verifications = [bool(entry.get("verified")) for entry in self.prior_feature_gates_verified]
        prerequisite_tag_verifications = [bool(entry.get("verified")) for entry in self.prerequisite_tags_verified]
        evidence_chain_expected = self.feature_053_readiness_verified and all(prior_gate_verifications) and all(prerequisite_tag_verifications)
        if self.evidence_chain_ready_for_training_contract != evidence_chain_expected:
            raise ValueError("evidence_chain_ready_for_training_contract must match the committed prior gates")

        all_locks = all(getattr(self, field_name) is True for field_name in LOCK_FIELD_NAMES)
        all_no_drift_flags = all(getattr(self, field_name) is True for field_name in NO_Drift_FIELD_NAMES)
        ready_to_run = (
            self.feature_053_readiness_verified
            and self.evidence_chain_ready_for_training_contract
            and all_locks
            and self.behavior_equivalence_passed
            and all_no_drift_flags
        )
        if self.training_execution_allowed_next != ready_to_run:
            raise ValueError("training_execution_allowed_next must match the readiness gate bundle")

        if not prerequisite_tag_verifications or not all(prerequisite_tag_verifications):
            expected_final_verdict = "evidence_chain_prerequisite_blocked"
        elif not self.feature_053_readiness_verified or not self.evidence_chain_ready_for_training_contract:
            expected_final_verdict = "evidence_chain_prerequisite_blocked"
        elif not self.paper_default_config_locked:
            expected_final_verdict = "paper_default_config_contract_blocked"
        elif not self.observation_contract_locked:
            expected_final_verdict = "observation_contract_blocked"
        elif not self.action_contract_locked or not self.legality_contract_locked:
            expected_final_verdict = "action_or_legality_contract_blocked"
        elif not self.reward_contract_locked or not self.timeout_contract_locked or not self.capacity_contract_locked or not self.transmission_contract_locked or not self.queue_contract_locked:
            expected_final_verdict = "reward_timeout_capacity_contract_blocked"
        elif not self.metric_contract_locked or not self.seed_contract_locked or not self.artifact_contract_locked:
            expected_final_verdict = "metric_or_artifact_contract_blocked"
        elif not self.behavior_equivalence_passed or not all_no_drift_flags:
            expected_final_verdict = "behavior_drift_detected"
        else:
            expected_final_verdict = "training_readiness_contract_ready_for_smoke_run"

        if self.final_verdict != expected_final_verdict:
            raise ValueError("final_verdict must match the first failing gate or the ready path")

        if self.training_execution_allowed_next:
            if self.final_verdict != "training_readiness_contract_ready_for_smoke_run":
                raise ValueError("ready reports must use the smoke-run readiness verdict")
            if self.remaining_blockers:
                raise ValueError("ready reports must not report blockers")
            if self.recommended_next_feature != READY_NEXT_FEATURE:
                raise ValueError("ready reports must route to Feature 055")
        else:
            if not self.remaining_blockers:
                raise ValueError("blocked reports must report at least one blocker")
            if self.recommended_next_feature == READY_NEXT_FEATURE:
                raise ValueError("blocked reports must not route to Feature 055")
            if self.final_verdict == "training_readiness_contract_ready_for_smoke_run":
                raise ValueError("blocked reports cannot claim smoke-run readiness")

    def to_dict(self) -> dict[str, Any]:
        def serialize(value: Any) -> Any:
            return value.to_dict() if hasattr(value, "to_dict") else value

        return {
            "feature_id": self.feature_id,
            "prerequisite_tags_verified": list(self.prerequisite_tags_verified),
            "prior_feature_gates_verified": list(self.prior_feature_gates_verified),
            "feature_053_readiness_verified": self.feature_053_readiness_verified,
            "evidence_chain_ready_for_training_contract": self.evidence_chain_ready_for_training_contract,
            "paper_default_config_locked": self.paper_default_config_locked,
            "observation_contract_locked": self.observation_contract_locked,
            "action_contract_locked": self.action_contract_locked,
            "legality_contract_locked": self.legality_contract_locked,
            "reward_contract_locked": self.reward_contract_locked,
            "timeout_contract_locked": self.timeout_contract_locked,
            "capacity_contract_locked": self.capacity_contract_locked,
            "transmission_contract_locked": self.transmission_contract_locked,
            "queue_contract_locked": self.queue_contract_locked,
            "metric_contract_locked": self.metric_contract_locked,
            "seed_contract_locked": self.seed_contract_locked,
            "artifact_contract_locked": self.artifact_contract_locked,
            "behavior_equivalence_summary": serialize(self.behavior_equivalence_summary),
            "behavior_equivalence_passed": self.behavior_equivalence_passed,
            "training_execution_allowed_next": self.training_execution_allowed_next,
            "remaining_blockers": list(self.remaining_blockers),
            "recommended_next_feature": self.recommended_next_feature,
            "no_training_started": self.no_training_started,
            "no_optimizer_step": self.no_optimizer_step,
            "no_replay_training": self.no_replay_training,
            "no_target_update_execution": self.no_target_update_execution,
            "no_checkpoint_written": self.no_checkpoint_written,
            "no_campaign_run": self.no_campaign_run,
            "no_policy_drift": self.no_policy_drift,
            "no_runtime_semantic_changes": self.no_runtime_semantic_changes,
            "no_dependency_drift": self.no_dependency_drift,
            "no_prior_artifact_rewrite": self.no_prior_artifact_rewrite,
            "no_paper_reproduction_claim": self.no_paper_reproduction_claim,
            "final_verdict": self.final_verdict,
        }
