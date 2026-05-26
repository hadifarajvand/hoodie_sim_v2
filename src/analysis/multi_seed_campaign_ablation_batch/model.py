from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import FEATURE_ID, READY_NEXT_FEATURE, REQUIRED_TOP_LEVEL_FIELDS

ALLOWED_FINAL_VERDICTS = (
    "multi_seed_campaign_ablation_batch_passed",
    "feature_061_prerequisite_blocked",
    "multi_seed_gate_blocked",
    "multi_seed_campaign_blocked",
    "multi_seed_aggregation_blocked",
    "ablation_gate_blocked",
    "ablation_execution_blocked",
    "artifact_manifest_blocked",
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
class MultiSeedCampaignAblationBatchReport:
    feature_id: str
    batch_items_covered: list[str]
    prerequisite_tags_verified: list[dict[str, Any]]
    feature_061_verified: bool
    multi_seed_gate_summary: dict[str, Any]
    multi_seed_campaign_summary: dict[str, Any]
    multi_seed_aggregation_summary: dict[str, Any]
    ablation_gate_summary: dict[str, Any]
    ablation_execution_summary: dict[str, Any]
    artifact_manifest_summary: dict[str, Any]
    safety_summary: dict[str, Any]
    remaining_blockers: list[str] = field(default_factory=list)
    recommended_next_feature: str = ""
    final_verdict: str = "feature_061_prerequisite_blocked"

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 062-multi-seed-campaign-ablation-batch")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("invalid final_verdict")
        if list(self.batch_items_covered) != [
            "Multi-Seed Campaign Gate",
            "Multi-Seed Campaign Execution",
            "Multi-Seed Result Aggregation",
            "Mechanism Ablation Gate",
            "Mechanism Ablation Execution",
        ]:
            raise ValueError("batch_items_covered must preserve the approved batch order")
        _unique_names(self.prerequisite_tags_verified)
        if not REQUIRED_TOP_LEVEL_FIELDS:
            raise ValueError("required fields unavailable")
        _required_keys(self.multi_seed_gate_summary, "multi_seed_gate_summary", ("seed_set", "seed_count", "bounded_execution_budget_per_seed", "evaluation_trace_bank_id", "training_trace_bank_id", "baseline_policy_list", "trained_policy_reference", "metric_schema", "real_trainer_binding_evidence", "controlled_output_directory"))
        _required_keys(self.multi_seed_campaign_summary, "multi_seed_campaign_summary", ("seed_level_results", "configured_budget_per_seed", "actual_executed_budget_per_seed", "same_metric_schema_across_seeds", "same_evaluation_trace_bank_across_seeds", "no_training_evaluation_leakage", "controlled_experiment_data"))
        _required_keys(self.multi_seed_aggregation_summary, "multi_seed_aggregation_summary", ("sample_count", "metrics", "single_run_limitation_removed"))
        _required_keys(self.ablation_gate_summary, "ablation_gate_summary", ("variants", "same_seed_set", "same_trace_bank_constraints", "same_metric_schema"))
        _required_keys(self.ablation_execution_summary, "ablation_execution_summary", ("variant_results", "controlled_experiment_data", "no_superiority_claim"))
        _required_keys(self.artifact_manifest_summary, "artifact_manifest_summary", ("artifact_exists", "all_required_artifacts_exist"))
        _required_keys(self.safety_summary, "safety_summary", ("no_dependency_drift", "no_policy_drift", "no_environment_contract_drift", "no_reward_timing_change", "no_prior_feature_artifact_rewrite", "no_paper_reproduction_claim", "no_unsupported_superiority_claim", "no_uncontrolled_campaign_loop", "no_checkpoint_binary_created"))
        if self.final_verdict == "multi_seed_campaign_ablation_batch_passed":
            if self.remaining_blockers:
                raise ValueError("passing report cannot include blockers")
            if self.recommended_next_feature != READY_NEXT_FEATURE:
                raise ValueError("passing report must route to Feature 063")
        else:
            if not self.remaining_blockers:
                raise ValueError("blocked report must include blockers")
            if self.recommended_next_feature == READY_NEXT_FEATURE:
                raise ValueError("blocked report must not route to Feature 063")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
