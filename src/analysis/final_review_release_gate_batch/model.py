from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import FEATURE_ID, READY_NEXT_FEATURE, REQUIRED_TOP_LEVEL_FIELDS

ALLOWED_FINAL_VERDICTS = (
    "final_review_release_gate_batch_passed",
    "feature_063_prerequisite_blocked",
    "repository_state_audit_blocked",
    "artifact_completeness_blocked",
    "claim_boundary_review_blocked",
    "release_tag_readiness_blocked",
    "handoff_blocked",
    "behavior_drift_detected",
)


def _required_keys(summary: dict[str, Any], field_name: str, keys: tuple[str, ...]) -> None:
    missing = [key for key in keys if key not in summary]
    if missing:
        raise ValueError(f"{field_name} missing keys: {missing}")


def _unique_names(entries: list[dict[str, Any]]) -> None:
    names = [str(entry.get("name")) for entry in entries]
    if len(names) != len(set(names)):
        raise ValueError("prerequisite tag names must be unique")


@dataclass(frozen=True, slots=True)
class FinalReviewReleaseGateBatchReport:
    feature_id: str
    batch_items_covered: list[str]
    prerequisite_tags_verified: list[dict[str, Any]]
    feature_063_verified: bool
    repository_state_audit_summary: dict[str, Any]
    artifact_completeness_summary: dict[str, Any]
    claim_boundary_review_summary: dict[str, Any]
    release_tag_readiness_summary: dict[str, Any]
    handoff_summary: dict[str, Any]
    safety_summary: dict[str, Any]
    remaining_blockers: list[str] = field(default_factory=list)
    recommended_next_feature: str = ""
    final_verdict: str = "feature_063_prerequisite_blocked"

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 064-final-review-release-gate-batch")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("invalid final_verdict")
        if list(self.batch_items_covered) != [
            "Final Repository State Audit",
            "Final Artifact Completeness Gate",
            "Final Claim Boundary Review",
            "Release Tag Readiness Package",
            "Final Handoff and Next-Work Recommendation",
        ]:
            raise ValueError("batch_items_covered must preserve the approved batch order")
        _unique_names(self.prerequisite_tags_verified)
        if not REQUIRED_TOP_LEVEL_FIELDS:
            raise ValueError("required fields unavailable")
        _required_keys(self.repository_state_audit_summary, "repository_state_audit_summary", ("source_backed_evidence", "committed_inputs_only", "no_uncommitted_local_state_dependency"))
        _required_keys(self.artifact_completeness_summary, "artifact_completeness_summary", ("feature_063_final_exports_exist", "source_artifacts_exist", "feature_064_outputs_exist_after_generation"))
        _required_keys(self.claim_boundary_review_summary, "claim_boundary_review_summary", ("supported_claims_mapped", "unsupported_claims_explicit", "no_paper_reproduction_claim", "no_unsupported_superiority_claim"))
        _required_keys(self.release_tag_readiness_summary, "release_tag_readiness_summary", ("recommended_release_tag", "post_merge_tag_commands", "tag_not_created_by_this_feature", "prerequisites", "rollback_or_repair_note"))
        _required_keys(self.handoff_summary, "handoff_summary", ("supported_results", "unsupported_claims", "known_limitations", "repository_artifact_readiness", "next_work_recommendation"))
        _required_keys(self.safety_summary, "safety_summary", ("no_training_rerun", "no_new_experiment_output", "no_dependency_drift", "no_policy_drift", "no_environment_contract_drift", "no_reward_timing_change", "no_prior_feature_artifact_rewrite", "no_paper_reproduction_claim", "no_unsupported_superiority_claim", "no_release_tag_created"))
        if self.repository_state_audit_summary.get("source_backed_evidence") is not True:
            raise ValueError("repository state audit must be source-backed")
        if self.artifact_completeness_summary.get("feature_063_final_exports_exist") is not True:
            raise ValueError("artifact completeness must verify Feature 063 exports")
        if self.claim_boundary_review_summary.get("no_paper_reproduction_claim") is not True or self.claim_boundary_review_summary.get("no_unsupported_superiority_claim") is not True:
            raise ValueError("claim boundary review must reject unsupported claims")
        if self.safety_summary.get("no_release_tag_created") is not True:
            raise ValueError("Feature 064 must not create a tag")
        if self.final_verdict == "final_review_release_gate_batch_passed":
            if self.remaining_blockers:
                raise ValueError("passing report cannot include blockers")
            if self.recommended_next_feature != READY_NEXT_FEATURE:
                raise ValueError("passing report must route to release or writing workflow")
        else:
            if not self.remaining_blockers:
                raise ValueError("blocked report must include blockers")
            if self.recommended_next_feature == READY_NEXT_FEATURE:
                raise ValueError("blocked report must not route to release or writing workflow")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
