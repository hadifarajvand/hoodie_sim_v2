from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import FEATURE_ID, READY_NEXT_FEATURE

ALLOWED_FINAL_VERDICTS = (
    "real_trainer_reduced_budget_campaign_validation_passed",
    "feature_059_prerequisite_blocked",
    "feature_058_prerequisite_blocked",
    "feature_057_prerequisite_blocked",
    "real_trainer_binding_blocked",
    "reduced_budget_execution_blocked",
    "training_metrics_blocked",
    "evaluation_metrics_blocked",
    "baseline_contract_blocked",
    "checkpoint_metadata_blocked",
    "artifact_manifest_blocked",
    "resource_control_blocked",
    "behavior_drift_detected",
)


def _ensure_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean")
    return value


def _required_keys(summary: dict[str, Any], field_name: str, keys: tuple[str, ...]) -> None:
    missing = [key for key in keys if key not in summary]
    if missing:
        raise ValueError(f"{field_name} is missing required keys: {missing}")


def _ensure_unique_names(entries: list[dict[str, Any]], field_name: str) -> None:
    names = [str(entry.get("name")) for entry in entries]
    if len(names) != len(set(names)):
        raise ValueError(f"{field_name} names must be unique")


@dataclass(frozen=True, slots=True)
class RealTrainerReducedBudgetCampaignExecutionValidationReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    feature_059_gate_verified: bool
    feature_058_harness_verified: bool
    feature_057_pilot_verified: bool
    real_trainer_binding_summary: dict[str, Any]
    reduced_budget_execution_summary: dict[str, Any]
    training_metrics_summary: dict[str, Any]
    evaluation_metrics_summary: dict[str, Any]
    baseline_contract_summary: dict[str, Any]
    checkpoint_metadata_summary: dict[str, Any]
    artifact_manifest_summary: dict[str, Any]
    resource_control_summary: dict[str, Any]
    safety_summary: dict[str, Any]
    remaining_blockers: list[str] = field(default_factory=list)
    recommended_next_feature: str = ""
    final_verdict: str = "feature_059_prerequisite_blocked"

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 060a-real-trainer-reduced-budget-campaign-execution-validation")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("invalid final_verdict")
        _ensure_unique_names(self.prerequisite_tags_verified, "prerequisite_tags_verified")
        for entry in self.prerequisite_tags_verified:
            _ensure_bool(entry.get("verified"), f"prerequisite_tags_verified.{entry.get('name')}.verified")
        feature_059_gate_verified = _ensure_bool(self.feature_059_gate_verified, "feature_059_gate_verified")
        feature_058_harness_verified = _ensure_bool(self.feature_058_harness_verified, "feature_058_harness_verified")
        feature_057_pilot_verified = _ensure_bool(self.feature_057_pilot_verified, "feature_057_pilot_verified")

        _required_keys(
            self.real_trainer_binding_summary,
            "real_trainer_binding_summary",
            (
                "torch_import_used",
                "real_trainer_import_used",
                "real_trainer_class",
                "real_trainer_instantiated",
                "trainer_method_called",
                "real_trainer_update_or_train_called",
            ),
        )
        _required_keys(
            self.reduced_budget_execution_summary,
            "reduced_budget_execution_summary",
            (
                "configured_full_campaign_budget",
                "actual_reduced_budget",
                "actual_budget_is_reduced_for_validation",
                "full_campaign_executed",
                "real_trainer_used",
                "trainer_method_called",
                "optimizer_steps_executed",
                "replay_populated",
                "loss_finite",
                "evaluation_metrics_generated",
                "baseline_contract_checked",
                "checkpoint_metadata_written",
                "run_manifest_written",
            ),
        )
        _required_keys(
            self.training_metrics_summary,
            "training_metrics_summary",
            ("optimizer_step_count", "replay_size", "loss_count", "loss_finite", "action_distribution"),
        )
        _required_keys(
            self.evaluation_metrics_summary,
            "evaluation_metrics_summary",
            ("evaluation_episode_count", "trace_bank_disjoint", "trace_bank_ids", "evaluation_on_training_traces"),
        )
        _required_keys(
            self.baseline_contract_summary,
            "baseline_contract_summary",
            ("feature_058_harness_verified", "baseline_harness_ready", "baseline_registry_ready", "metric_schema_complete"),
        )
        _required_keys(
            self.checkpoint_metadata_summary,
            "checkpoint_metadata_summary",
            ("metadata_artifact_exists", "checkpoint_schema_valid", "target_update_metadata", "replay_metadata", "seed_bundle"),
        )
        _required_keys(
            self.artifact_manifest_summary,
            "artifact_manifest_summary",
            (
                "real_campaign_json_report",
                "real_campaign_markdown_report",
                "training_metrics_json",
                "evaluation_metrics_json",
                "checkpoint_metadata_json",
                "run_manifest_json",
                "all_required_artifacts_exist",
            ),
        )
        _required_keys(
            self.resource_control_summary,
            "resource_control_summary",
            ("configured_full_campaign_budget", "actual_reduced_budget", "actual_budget_is_reduced_for_validation", "resource_control_complete"),
        )
        _required_keys(
            self.safety_summary,
            "safety_summary",
            (
                "no_full_campaign_execution",
                "no_paper_reproduction_claim",
                "no_performance_superiority_claim",
                "no_baseline_superiority_claim",
                "no_uncontrolled_campaign_loop",
                "no_policy_drift",
                "no_dependency_drift",
                "no_environment_contract_drift",
                "no_reward_timing_change",
                "no_prior_artifact_rewrite",
            ),
        )

        reduced_budget_ok = (
            int(self.reduced_budget_execution_summary.get("actual_reduced_budget", {}).get("training_episode_count", 0)) == 1
            and int(self.reduced_budget_execution_summary.get("actual_reduced_budget", {}).get("actual_episode_length", 0)) == 110
            and bool(self.reduced_budget_execution_summary.get("actual_budget_is_reduced_for_validation"))
            and self.reduced_budget_execution_summary.get("full_campaign_executed") is False
            and self.reduced_budget_execution_summary.get("real_trainer_used") is True
            and self.reduced_budget_execution_summary.get("optimizer_steps_executed") is True
            and self.reduced_budget_execution_summary.get("replay_populated") is True
            and self.reduced_budget_execution_summary.get("loss_finite") is True
            and self.reduced_budget_execution_summary.get("evaluation_metrics_generated") is True
            and self.reduced_budget_execution_summary.get("baseline_contract_checked") is True
            and self.reduced_budget_execution_summary.get("checkpoint_metadata_written") is True
            and self.reduced_budget_execution_summary.get("run_manifest_written") is True
        )
        training_ready = int(self.training_metrics_summary.get("optimizer_step_count", 0)) > 0 and int(self.training_metrics_summary.get("replay_size", 0)) > 0 and int(self.training_metrics_summary.get("loss_count", 0)) > 0 and self.training_metrics_summary.get("loss_finite") is True
        evaluation_ready = int(self.evaluation_metrics_summary.get("evaluation_episode_count", 0)) > 0 and self.evaluation_metrics_summary.get("trace_bank_disjoint") is True and self.evaluation_metrics_summary.get("evaluation_on_training_traces") is False
        baseline_ready = self.baseline_contract_summary.get("feature_058_harness_verified") is True and self.baseline_contract_summary.get("baseline_harness_ready") is True and self.baseline_contract_summary.get("baseline_registry_ready") is True and self.baseline_contract_summary.get("metric_schema_complete") is True
        checkpoint_ready = self.checkpoint_metadata_summary.get("metadata_artifact_exists") is True and self.checkpoint_metadata_summary.get("checkpoint_schema_valid") is True and bool(self.checkpoint_metadata_summary.get("target_update_metadata")) and bool(self.checkpoint_metadata_summary.get("replay_metadata")) and bool(self.checkpoint_metadata_summary.get("seed_bundle"))
        artifact_ready = self.artifact_manifest_summary.get("all_required_artifacts_exist") is True
        resource_ready = self.resource_control_summary.get("actual_budget_is_reduced_for_validation") is True and self.resource_control_summary.get("resource_control_complete") is True
        safety_ready = all(_ensure_bool(self.safety_summary.get(key), f"safety_summary.{key}") for key in self.safety_summary)
        prereq_ready = feature_059_gate_verified and feature_058_harness_verified and feature_057_pilot_verified and all(entry.get("verified") is True for entry in self.prerequisite_tags_verified)

        ready = prereq_ready and reduced_budget_ok and training_ready and evaluation_ready and baseline_ready and checkpoint_ready and artifact_ready and resource_ready and safety_ready and not self.remaining_blockers
        if ready:
            if self.final_verdict != "real_trainer_reduced_budget_campaign_validation_passed":
                raise ValueError("passing Feature 060A reports must use the passed verdict")
            if self.recommended_next_feature != READY_NEXT_FEATURE:
                raise ValueError("passing Feature 060A reports must route to Feature 060")
            return
        if self.final_verdict == "real_trainer_reduced_budget_campaign_validation_passed":
            raise ValueError("blocked Feature 060A reports cannot claim pass")
        if not self.remaining_blockers:
            raise ValueError("blocked Feature 060A reports must include blockers")
        if self.recommended_next_feature == READY_NEXT_FEATURE:
            raise ValueError("blocked Feature 060A reports must not route to Feature 060")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
