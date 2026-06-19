from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import FEATURE_ID, READY_NEXT_FEATURE, SAFETY_FIELDS

ALLOWED_FINAL_VERDICTS = (
    "full_paper_default_training_campaign_execution_passed",
    "feature_059_prerequisite_blocked",
    "campaign_execution_blocked",
    "training_metrics_blocked",
    "evaluation_metrics_blocked",
    "baseline_evaluation_blocked",
    "checkpoint_metadata_blocked",
    "artifact_manifest_blocked",
    "resource_control_blocked",
    "behavior_drift_detected",
)

REPAIR_ROUTING = {
    "feature_059_prerequisite_blocked": "Repair Feature 059 prerequisite evidence before Feature 060 can proceed",
    "campaign_execution_blocked": "Repair Feature 060 campaign execution",
    "training_metrics_blocked": "Repair Feature 060 training metrics",
    "evaluation_metrics_blocked": "Repair Feature 060 evaluation metrics",
    "baseline_evaluation_blocked": "Repair Feature 060 baseline evaluation metrics",
    "checkpoint_metadata_blocked": "Repair Feature 060 checkpoint metadata",
    "artifact_manifest_blocked": "Repair Feature 060 artifact manifest",
    "resource_control_blocked": "Repair Feature 060 resource controls",
    "behavior_drift_detected": "Repair Feature 060 behavior safety guard",
}


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
class FullPaperDefaultTrainingCampaignExecutionReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    feature_059_gate_verified: bool
    feature_060a_validation_verified: bool
    feature_058_harness_verified: bool
    campaign_execution_summary: dict[str, Any]
    training_metrics_summary: dict[str, Any]
    evaluation_metrics_summary: dict[str, Any]
    baseline_evaluation_summary: dict[str, Any]
    checkpoint_metadata_summary: dict[str, Any]
    artifact_manifest_summary: dict[str, Any]
    resource_control_summary: dict[str, Any]
    safety_summary: dict[str, Any]
    remaining_blockers: list[str] = field(default_factory=list)
    recommended_next_feature: str = ""
    final_verdict: str = "feature_059_prerequisite_blocked"

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 060-full-paper-default-training-campaign-execution")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("invalid final_verdict")

        _ensure_unique_names(self.prerequisite_tags_verified, "prerequisite_tags_verified")
        prerequisite_tags_ready = all(
            _ensure_bool(entry.get("verified"), f"prerequisite_tags_verified.{entry.get('name')}.verified")
            for entry in self.prerequisite_tags_verified
        )
        feature_059_gate_verified = _ensure_bool(self.feature_059_gate_verified, "feature_059_gate_verified")
        feature_060a_validation_verified = _ensure_bool(self.feature_060a_validation_verified, "feature_060a_validation_verified")
        feature_058_harness_verified = _ensure_bool(self.feature_058_harness_verified, "feature_058_harness_verified")

        _required_keys(
            self.campaign_execution_summary,
            "campaign_execution_summary",
            (
                "configured_budget",
                "actual_training_episode_count",
                "actual_evaluation_episode_count",
                "actual_baseline_evaluation_episode_count",
                "training_trace_bank_id",
                "evaluation_trace_bank_id",
                "baseline_harness_id",
                "seed_bundle",
                "execution_completed",
                "controlled_output_directory",
                "actual_budget_is_full_campaign",
                "real_trainer_used",
                "real_trainer_class",
                "trainer_method_called",
                "full_campaign_executed",
            ),
        )
        _required_keys(
            self.training_metrics_summary,
            "training_metrics_summary",
            (
                "optimizer_step_count",
                "replay_size",
                "loss_count",
                "loss_finite",
                "reward_summary",
                "target_update_summary",
                "action_distribution",
                "local_action_count",
                "horizontal_action_count",
                "vertical_action_count",
                "invalid_or_noop_action_count",
                "action_count_total",
                "action_accounting_reconciled",
            ),
        )
        _required_keys(
            self.evaluation_metrics_summary,
            "evaluation_metrics_summary",
            (
                "evaluation_trace_bank_id",
                "evaluation_episode_count",
                "metric_schema_coverage",
                "delay",
                "drop",
                "timeout",
                "reward",
                "action_distribution",
                "no_paper_reproduction_claim",
                "no_performance_superiority_claim",
            ),
        )
        _required_keys(
            self.baseline_evaluation_summary,
            "baseline_evaluation_summary",
            (
                "baseline_policy_names",
                "evaluated_policy_count",
                "actual_baseline_evaluation_episode_count",
                "per_policy_metrics",
                "baseline_metric_shells",
                "baseline_metrics_real_execution",
                "no_baseline_superiority_claim",
            ),
        )
        _required_keys(
            self.checkpoint_metadata_summary,
            "checkpoint_metadata_summary",
            (
                "metadata_artifact_exists",
                "target_update_metadata",
                "replay_metadata",
                "seed_bundle",
                "trace_bank_ids",
                "checkpoint_binary_policy",
            ),
        )
        _required_keys(
            self.artifact_manifest_summary,
            "artifact_manifest_summary",
            (
                "full_campaign_json_report",
                "full_campaign_markdown_report",
                "training_metrics_json",
                "evaluation_metrics_json",
                "baseline_evaluation_metrics_json",
                "checkpoint_metadata_json",
                "run_manifest_json",
                "all_required_artifacts_exist",
            ),
        )
        _required_keys(
            self.resource_control_summary,
            "resource_control_summary",
            (
                "configured_budget",
                "actual_executed_budget",
                "controlled_output_directory",
                "timeout_runtime_budget",
                "no_uncontrolled_campaign_loop",
                "resource_control_observed",
            ),
        )
        _required_keys(self.safety_summary, "safety_summary", SAFETY_FIELDS)

        configured_budget = dict(self.campaign_execution_summary.get("configured_budget", {}))
        expected_training_episode_count = int(configured_budget.get("training_episode_count", 0))
        expected_evaluation_episode_count = int(configured_budget.get("evaluation_episode_count", 0))
        expected_baseline_episode_count = int(configured_budget.get("baseline_evaluation_episode_count", 0))
        expected_episode_length = int(configured_budget.get("episode_length", 110))
        actual_training_episode_count = int(self.campaign_execution_summary.get("actual_training_episode_count", 0))
        actual_evaluation_episode_count = int(self.campaign_execution_summary.get("actual_evaluation_episode_count", 0))
        actual_baseline_episode_count = int(self.campaign_execution_summary.get("actual_baseline_evaluation_episode_count", 0))
        campaign_execution_ready = (
            expected_training_episode_count == 1000
            and expected_evaluation_episode_count == 100
            and expected_baseline_episode_count == 100
            and expected_episode_length == 110
            and actual_training_episode_count == expected_training_episode_count
            and actual_evaluation_episode_count == expected_evaluation_episode_count
            and actual_baseline_episode_count == expected_baseline_episode_count
            and bool(self.campaign_execution_summary.get("training_trace_bank_id"))
            and bool(self.campaign_execution_summary.get("evaluation_trace_bank_id"))
            and bool(self.campaign_execution_summary.get("baseline_harness_id"))
            and bool(self.campaign_execution_summary.get("seed_bundle"))
            and self.campaign_execution_summary.get("execution_completed") is True
            and bool(self.campaign_execution_summary.get("controlled_output_directory"))
            and self.campaign_execution_summary.get("actual_budget_is_full_campaign") is True
            and self.campaign_execution_summary.get("actual_budget_is_reduced_for_local_validation") is False
            and self.campaign_execution_summary.get("real_trainer_used") is True
            and bool(self.campaign_execution_summary.get("real_trainer_class"))
            and bool(self.campaign_execution_summary.get("trainer_method_called"))
            and self.campaign_execution_summary.get("full_campaign_executed") is True
        )
        replay_size = int(self.training_metrics_summary.get("replay_size", 0))
        training_action_distribution = dict(self.training_metrics_summary.get("action_distribution", {}))
        training_action_count_sum = sum(
            int(training_action_distribution.get(action, 0))
            for action in ("local", "horizontal", "vertical", "invalid_or_noop_action_count")
        )
        training_metrics_ready = (
            int(self.training_metrics_summary.get("optimizer_step_count", 0)) > 0
            and replay_size > 0
            and int(self.training_metrics_summary.get("loss_count", 0)) > 0
            and self.training_metrics_summary.get("loss_finite") is True
            and bool(self.training_metrics_summary.get("reward_summary"))
            and bool(self.training_metrics_summary.get("target_update_summary"))
            and bool(training_action_distribution)
            and training_action_count_sum == replay_size
            and int(self.training_metrics_summary.get("action_count_total", -1)) == replay_size
            and self.training_metrics_summary.get("action_accounting_reconciled") is True
        )
        evaluation_metrics_ready = (
            bool(self.evaluation_metrics_summary.get("evaluation_trace_bank_id"))
            and int(self.evaluation_metrics_summary.get("evaluation_episode_count", 0)) > 0
            and self.evaluation_metrics_summary.get("metric_schema_coverage", {}).get("metric_schema_complete") is True
            and self.evaluation_metrics_summary.get("no_paper_reproduction_claim") is True
            and self.evaluation_metrics_summary.get("no_performance_superiority_claim") is True
        )
        per_policy_metrics = dict(self.baseline_evaluation_summary.get("per_policy_metrics", {}))
        per_policy_episode_counts_ready = all(
            int(metrics.get("episode_count", 0)) == actual_baseline_episode_count
            for metrics in per_policy_metrics.values()
        )
        per_policy_real_metrics_ready = all(
            metrics.get("metric_shell_only") is False
            and metrics.get("performance_claim") is False
            and metrics.get("no_baseline_superiority_claim") is True
            for metrics in per_policy_metrics.values()
        )
        baseline_evaluation_ready = (
            len(self.baseline_evaluation_summary.get("baseline_policy_names", [])) > 0
            and int(self.baseline_evaluation_summary.get("evaluated_policy_count", 0)) == len(self.baseline_evaluation_summary.get("baseline_policy_names", []))
            and int(self.baseline_evaluation_summary.get("actual_baseline_evaluation_episode_count", 0)) == actual_baseline_episode_count == expected_baseline_episode_count
            and bool(per_policy_metrics)
            and per_policy_episode_counts_ready
            and per_policy_real_metrics_ready
            and self.baseline_evaluation_summary.get("baseline_metrics_real_execution") is True
            and bool(self.baseline_evaluation_summary.get("baseline_metric_shells"))
            and self.baseline_evaluation_summary.get("no_baseline_superiority_claim") is True
        )
        checkpoint_metadata_ready = (
            self.checkpoint_metadata_summary.get("metadata_artifact_exists") is True
            and bool(self.checkpoint_metadata_summary.get("target_update_metadata"))
            and bool(self.checkpoint_metadata_summary.get("replay_metadata"))
            and bool(self.checkpoint_metadata_summary.get("seed_bundle"))
            and bool(self.checkpoint_metadata_summary.get("trace_bank_ids"))
            and bool(self.checkpoint_metadata_summary.get("checkpoint_binary_policy"))
        )
        artifact_manifest_ready = self.artifact_manifest_summary.get("all_required_artifacts_exist") is True
        resource_control_ready = (
            bool(self.resource_control_summary.get("configured_budget"))
            and bool(self.resource_control_summary.get("actual_executed_budget"))
            and bool(self.resource_control_summary.get("controlled_output_directory"))
            and bool(self.resource_control_summary.get("timeout_runtime_budget"))
            and self.resource_control_summary.get("no_uncontrolled_campaign_loop") is True
            and self.resource_control_summary.get("resource_control_observed") is True
        )
        safety_ready = all(_ensure_bool(self.safety_summary.get(key), f"safety_summary.{key}") for key in SAFETY_FIELDS)

        ready = (
            prerequisite_tags_ready
            and feature_059_gate_verified
            and feature_060a_validation_verified
            and feature_058_harness_verified
            and campaign_execution_ready
            and training_metrics_ready
            and evaluation_metrics_ready
            and baseline_evaluation_ready
            and checkpoint_metadata_ready
            and artifact_manifest_ready
            and resource_control_ready
            and safety_ready
            and not self.remaining_blockers
        )

        if ready:
            if self.final_verdict != "full_paper_default_training_campaign_execution_passed":
                raise ValueError("passing Feature 060 reports must use the passed verdict")
            if self.recommended_next_feature != READY_NEXT_FEATURE:
                raise ValueError("passing Feature 060 reports must route to Feature 061")
            return

        if self.final_verdict == "full_paper_default_training_campaign_execution_passed":
            raise ValueError("blocked Feature 060 reports cannot claim pass")
        if not self.remaining_blockers:
            raise ValueError("blocked Feature 060 reports must include blockers")
        if self.recommended_next_feature == READY_NEXT_FEATURE:
            raise ValueError("blocked Feature 060 reports must not route to Feature 061")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
