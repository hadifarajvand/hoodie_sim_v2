from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import FEATURE_ID, METRIC_COLLECTION_FIELDS, READY_NEXT_FEATURE, SAFETY_FIELDS

ALLOWED_FINAL_VERDICTS = (
    "full_paper_default_training_campaign_gate_ready",
    "feature_058_prerequisite_blocked",
    "campaign_scope_blocked",
    "training_execution_gate_blocked",
    "evaluation_harness_gate_blocked",
    "artifact_output_contract_blocked",
    "resource_control_blocked",
    "checkpoint_contract_blocked",
    "metric_collection_contract_blocked",
    "behavior_drift_detected",
)

REPAIR_ROUTING = {
    "feature_058_prerequisite_blocked": "Repair Feature 058 prerequisite evidence before Feature 059 can proceed",
    "campaign_scope_blocked": "Repair Feature 059 campaign scope gate",
    "training_execution_gate_blocked": "Repair Feature 059 training execution gate",
    "evaluation_harness_gate_blocked": "Repair Feature 059 evaluation harness gate",
    "artifact_output_contract_blocked": "Repair Feature 059 artifact output contract",
    "resource_control_blocked": "Repair Feature 059 resource control contract",
    "checkpoint_contract_blocked": "Repair Feature 059 checkpoint contract",
    "metric_collection_contract_blocked": "Repair Feature 059 metric collection contract",
    "behavior_drift_detected": "Repair Feature 059 behavior safety guard",
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
class FullPaperDefaultTrainingCampaignGateReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    feature_058_harness_verified: bool
    campaign_scope_summary: dict[str, Any]
    training_execution_gate_summary: dict[str, Any]
    evaluation_harness_gate_summary: dict[str, Any]
    artifact_output_contract_summary: dict[str, Any]
    resource_control_summary: dict[str, Any]
    checkpoint_contract_summary: dict[str, Any]
    metric_collection_contract_summary: dict[str, Any]
    safety_summary: dict[str, Any]
    remaining_blockers: list[str] = field(default_factory=list)
    recommended_next_feature: str = ""
    final_verdict: str = "feature_058_prerequisite_blocked"

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 059-full-paper-default-training-campaign-gate")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("invalid final_verdict")

        _ensure_unique_names(self.prerequisite_tags_verified, "prerequisite_tags_verified")
        prerequisite_tags_ready = all(
            _ensure_bool(entry.get("verified"), f"prerequisite_tags_verified.{entry.get('name')}.verified")
            for entry in self.prerequisite_tags_verified
        )
        feature_058_harness_verified = _ensure_bool(self.feature_058_harness_verified, "feature_058_harness_verified")

        _required_keys(
            self.campaign_scope_summary,
            "campaign_scope_summary",
            (
                "full_campaign_allowed_next_feature",
                "full_campaign_executed_this_feature",
                "paper_default_training_campaign",
                "training_trace_bank_id",
                "evaluation_trace_bank_id",
                "baseline_harness_id",
                "seed_bundle",
                "run_count_or_episode_budget",
                "campaign_scale_is_explicit",
            ),
        )
        _required_keys(
            self.training_execution_gate_summary,
            "training_execution_gate_summary",
            (
                "training_execution_allowed_next_feature",
                "training_executed_this_feature",
                "optimizer_executed_this_feature",
                "replay_mutated_this_feature",
                "checkpoint_binary_written_this_feature",
            ),
        )
        _required_keys(
            self.evaluation_harness_gate_summary,
            "evaluation_harness_gate_summary",
            (
                "evaluation_trace_bank_ready",
                "train_eval_trace_banks_disjoint",
                "baseline_policy_registry_ready",
                "baseline_harness_ready",
                "metric_schema_complete",
                "determinism_ready",
            ),
        )
        _required_keys(
            self.artifact_output_contract_summary,
            "artifact_output_contract_summary",
            (
                "full_campaign_json_report",
                "full_campaign_markdown_report",
                "training_metrics_artifact",
                "evaluation_metrics_artifact",
                "checkpoint_metadata_artifact",
                "run_manifest_artifact",
                "artifact_output_contract_complete",
            ),
        )
        _required_keys(
            self.resource_control_summary,
            "resource_control_summary",
            (
                "deterministic_seeds",
                "max_episode_or_run_budget",
                "timeout_runtime_budget",
                "controlled_output_directory",
                "no_uncontrolled_loop",
                "resource_control_complete",
            ),
        )
        _required_keys(
            self.checkpoint_contract_summary,
            "checkpoint_contract_summary",
            (
                "metadata_required",
                "checkpoint_binary_policy",
                "target_update_metadata_required",
                "replay_metadata_required",
                "seed_bundle_required",
                "trace_bank_ids_required",
                "checkpoint_contract_complete",
            ),
        )
        _required_keys(
            self.metric_collection_contract_summary,
            "metric_collection_contract_summary",
            ("required_metric_fields", "present_metric_fields", "missing_metric_fields", "metric_collection_contract_complete"),
        )
        _required_keys(self.safety_summary, "safety_summary", SAFETY_FIELDS)

        campaign_scope_ready = (
            self.campaign_scope_summary.get("full_campaign_allowed_next_feature") is True
            and self.campaign_scope_summary.get("full_campaign_executed_this_feature") is False
            and self.campaign_scope_summary.get("paper_default_training_campaign") is True
            and bool(self.campaign_scope_summary.get("training_trace_bank_id"))
            and bool(self.campaign_scope_summary.get("evaluation_trace_bank_id"))
            and bool(self.campaign_scope_summary.get("baseline_harness_id"))
            and bool(self.campaign_scope_summary.get("seed_bundle"))
            and bool(self.campaign_scope_summary.get("run_count_or_episode_budget"))
            and self.campaign_scope_summary.get("campaign_scale_is_explicit") is True
        )
        training_execution_gate_ready = (
            self.training_execution_gate_summary.get("training_execution_allowed_next_feature") is True
            and self.training_execution_gate_summary.get("training_executed_this_feature") is False
            and self.training_execution_gate_summary.get("optimizer_executed_this_feature") is False
            and self.training_execution_gate_summary.get("replay_mutated_this_feature") is False
            and self.training_execution_gate_summary.get("checkpoint_binary_written_this_feature") is False
        )
        evaluation_harness_ready = all(
            _ensure_bool(self.evaluation_harness_gate_summary.get(key), f"evaluation_harness_gate_summary.{key}")
            for key in (
                "evaluation_trace_bank_ready",
                "train_eval_trace_banks_disjoint",
                "baseline_policy_registry_ready",
                "baseline_harness_ready",
                "metric_schema_complete",
                "determinism_ready",
            )
        )
        artifact_contract_ready = _ensure_bool(
            self.artifact_output_contract_summary.get("artifact_output_contract_complete"),
            "artifact_output_contract_summary.artifact_output_contract_complete",
        ) and all(bool(self.artifact_output_contract_summary.get(key)) for key in (
            "full_campaign_json_report",
            "full_campaign_markdown_report",
            "training_metrics_artifact",
            "evaluation_metrics_artifact",
            "checkpoint_metadata_artifact",
            "run_manifest_artifact",
        ))
        resource_control_ready = (
            bool(self.resource_control_summary.get("deterministic_seeds"))
            and bool(self.resource_control_summary.get("max_episode_or_run_budget"))
            and bool(self.resource_control_summary.get("timeout_runtime_budget"))
            and bool(self.resource_control_summary.get("controlled_output_directory"))
            and self.resource_control_summary.get("no_uncontrolled_loop") is True
            and self.resource_control_summary.get("resource_control_complete") is True
        )
        checkpoint_contract_ready = (
            self.checkpoint_contract_summary.get("metadata_required") is True
            and bool(self.checkpoint_contract_summary.get("checkpoint_binary_policy"))
            and self.checkpoint_contract_summary.get("target_update_metadata_required") is True
            and self.checkpoint_contract_summary.get("replay_metadata_required") is True
            and self.checkpoint_contract_summary.get("seed_bundle_required") is True
            and self.checkpoint_contract_summary.get("trace_bank_ids_required") is True
            and self.checkpoint_contract_summary.get("checkpoint_contract_complete") is True
        )
        missing_metric_fields = list(self.metric_collection_contract_summary.get("missing_metric_fields", []))
        metric_collection_ready = (
            tuple(self.metric_collection_contract_summary.get("required_metric_fields", [])) == METRIC_COLLECTION_FIELDS
            and set(self.metric_collection_contract_summary.get("present_metric_fields", [])) >= set(METRIC_COLLECTION_FIELDS)
            and missing_metric_fields == []
            and self.metric_collection_contract_summary.get("metric_collection_contract_complete") is True
        )
        safety_ready = all(_ensure_bool(self.safety_summary.get(key), f"safety_summary.{key}") for key in SAFETY_FIELDS)

        ready = (
            prerequisite_tags_ready
            and feature_058_harness_verified
            and campaign_scope_ready
            and training_execution_gate_ready
            and evaluation_harness_ready
            and artifact_contract_ready
            and resource_control_ready
            and checkpoint_contract_ready
            and metric_collection_ready
            and safety_ready
            and not self.remaining_blockers
        )

        if ready:
            if self.final_verdict != "full_paper_default_training_campaign_gate_ready":
                raise ValueError("passing Feature 059 reports must use the ready verdict")
            if self.recommended_next_feature != READY_NEXT_FEATURE:
                raise ValueError("passing Feature 059 reports must route to Feature 060")
            return

        if self.final_verdict == "full_paper_default_training_campaign_gate_ready":
            raise ValueError("blocked Feature 059 reports cannot claim ready")
        if not self.remaining_blockers:
            raise ValueError("blocked Feature 059 reports must include blockers")
        if self.recommended_next_feature == READY_NEXT_FEATURE:
            raise ValueError("blocked Feature 059 reports must not route to Feature 060")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
