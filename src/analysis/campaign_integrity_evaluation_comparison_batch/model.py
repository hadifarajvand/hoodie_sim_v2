from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import FEATURE_ID, READY_NEXT_FEATURE, REQUIRED_TOP_LEVEL_FIELDS

ALLOWED_FINAL_VERDICTS = (
    "campaign_integrity_evaluation_comparison_batch_passed",
    "feature_060_prerequisite_blocked",
    "campaign_integrity_blocked",
    "baseline_evaluation_blocked",
    "trained_policy_evaluation_blocked",
    "comparison_readiness_blocked",
    "comparison_report_blocked",
    "artifact_manifest_blocked",
    "behavior_drift_detected",
)

REPAIR_ROUTING = {
    "feature_060_prerequisite_blocked": "Repair Feature 060 and 060B prerequisites before Feature 061 can proceed",
    "campaign_integrity_blocked": "Repair campaign artifact integrity",
    "baseline_evaluation_blocked": "Repair baseline evaluation execution",
    "trained_policy_evaluation_blocked": "Repair trained-policy evaluation execution",
    "comparison_readiness_blocked": "Repair comparison readiness audit",
    "comparison_report_blocked": "Repair comparison report generation",
    "artifact_manifest_blocked": "Repair Feature 061 artifact manifest",
    "behavior_drift_detected": "Repair Feature 061 behavior guard",
}


def _required_keys(summary: dict[str, Any], field_name: str, keys: tuple[str, ...]) -> None:
    missing = [key for key in keys if key not in summary]
    if missing:
        raise ValueError(f"{field_name} missing keys: {missing}")


def _unique_names(entries: list[dict[str, Any]]) -> None:
    names = [str(entry.get("name")) for entry in entries]
    if len(names) != len(set(names)):
        raise ValueError("prerequisite tag names must be unique")


@dataclass(frozen=True, slots=True)
class CampaignIntegrityEvaluationComparisonBatchReport:
    feature_id: str
    batch_items_covered: list[str]
    prerequisite_tags_verified: list[dict[str, Any]]
    feature_060_verified: bool
    campaign_integrity_summary: dict[str, Any]
    baseline_evaluation_summary: dict[str, Any]
    trained_policy_evaluation_summary: dict[str, Any]
    comparison_readiness_summary: dict[str, Any]
    comparison_report_summary: dict[str, Any]
    artifact_manifest_summary: dict[str, Any]
    safety_summary: dict[str, Any]
    remaining_blockers: list[str] = field(default_factory=list)
    recommended_next_feature: str = ""
    final_verdict: str = "feature_060_prerequisite_blocked"

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 061-campaign-integrity-evaluation-comparison-batch")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("invalid final_verdict")
        if list(self.batch_items_covered) != [
            "Campaign Result Integrity and Comparison Readiness Audit",
            "Baseline Evaluation Execution",
            "Trained Policy Evaluation Execution",
            "Baseline vs Trained Policy Comparison Readiness Audit",
            "Baseline vs Trained Policy Comparison Report",
        ]:
            raise ValueError("batch_items_covered must preserve the approved batch order")
        _unique_names(self.prerequisite_tags_verified)
        if not REQUIRED_TOP_LEVEL_FIELDS:
            raise ValueError("required fields unavailable")
        _required_keys(self.campaign_integrity_summary, "campaign_integrity_summary", ("feature_060_report_exists", "feature_060_training_metrics_exist", "feature_060_evaluation_metrics_exist", "feature_060_checkpoint_metadata_exist", "feature_060_run_manifest_exist", "artifact_manifest_paths_agree", "trace_bank_ids_consistent", "seed_bundle_consistent", "real_trainer_binding_evidence_exists", "scalar_fallback_drives_campaign_claim"))
        _required_keys(self.baseline_evaluation_summary, "baseline_evaluation_summary", ("evaluation_trace_bank_id", "trace_ids", "policies", "metric_schema", "baseline_policy_metrics", "controlled_experiment_data"))
        _required_keys(self.trained_policy_evaluation_summary, "trained_policy_evaluation_summary", ("evaluation_trace_bank_id", "trace_ids", "metric_schema", "trained_policy_metrics", "controlled_experiment_data"))
        _required_keys(self.comparison_readiness_summary, "comparison_readiness_summary", ("same_evaluation_trace_bank", "identical_metric_schema", "identical_action_contract", "trace_ids_comparable", "no_training_traces_leak_into_evaluation", "no_paper_reproduction_claim", "no_unsupported_superiority_claim"))
        _required_keys(self.comparison_report_summary, "comparison_report_summary", ("delay", "drop", "timeout", "reward", "action_distribution", "local_action_count", "horizontal_action_count", "vertical_action_count", "per_episode_summary", "train_eval_separation", "baseline_policy_metrics", "trained_policy_metrics", "controlled_experiment_data", "paper_reproduction_claim", "superiority_claim", "single_run_limitation"))
        _required_keys(self.artifact_manifest_summary, "artifact_manifest_summary", ("artifact_exists", "all_required_artifacts_exist"))
        _required_keys(self.safety_summary, "safety_summary", ("no_dependency_drift", "no_policy_drift", "no_environment_contract_drift", "no_reward_timing_change", "no_prior_feature_artifact_rewrite", "no_paper_reproduction_claim", "no_unsupported_superiority_claim", "no_uncontrolled_campaign_loop"))
        if self.final_verdict == "campaign_integrity_evaluation_comparison_batch_passed":
            if self.remaining_blockers:
                raise ValueError("passing report cannot include blockers")
            if self.recommended_next_feature != READY_NEXT_FEATURE:
                raise ValueError("passing report must route to Feature 062")
        else:
            if not self.remaining_blockers:
                raise ValueError("blocked report must include blockers")
            if self.recommended_next_feature == READY_NEXT_FEATURE:
                raise ValueError("blocked report must not route to Feature 062")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
