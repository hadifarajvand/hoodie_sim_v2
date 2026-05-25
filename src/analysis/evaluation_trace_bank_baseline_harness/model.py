from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import BEHAVIOR_SAFETY_FIELDS, FEATURE_ID, METRIC_SCHEMA_FIELDS, READY_NEXT_FEATURE

ALLOWED_FINAL_VERDICTS = (
    "evaluation_trace_bank_baseline_harness_ready",
    "feature_057_prerequisite_blocked",
    "evaluation_trace_bank_blocked",
    "train_eval_separation_blocked",
    "baseline_registry_blocked",
    "baseline_harness_blocked",
    "metric_schema_blocked",
    "determinism_blocked",
    "behavior_drift_detected",
)

REPAIR_ROUTING = {
    "feature_057_prerequisite_blocked": "Repair Feature 057 prerequisite evidence before Feature 058 can proceed",
    "evaluation_trace_bank_blocked": "Repair Feature 058 evaluation trace-bank construction",
    "train_eval_separation_blocked": "Repair Feature 058 train/eval trace-bank separation",
    "baseline_registry_blocked": "Repair Feature 058 baseline policy registry",
    "baseline_harness_blocked": "Repair Feature 058 baseline evaluation harness",
    "metric_schema_blocked": "Repair Feature 058 metric schema coverage",
    "determinism_blocked": "Repair Feature 058 determinism evidence",
    "behavior_drift_detected": "Repair Feature 058 behavior safety guard",
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
class EvaluationTraceBankBaselineHarnessReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    feature_057_pilot_verified: bool
    evaluation_trace_bank_summary: dict[str, Any]
    train_eval_separation_summary: dict[str, Any]
    baseline_policy_registry_summary: dict[str, Any]
    baseline_evaluation_harness_summary: dict[str, Any]
    metric_schema_summary: dict[str, Any]
    determinism_summary: dict[str, Any]
    behavior_safety_summary: dict[str, Any]
    remaining_blockers: list[str] = field(default_factory=list)
    recommended_next_feature: str = ""
    final_verdict: str = "feature_057_prerequisite_blocked"

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 058-evaluation-trace-bank-baseline-harness")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("invalid final_verdict")

        _ensure_unique_names(self.prerequisite_tags_verified, "prerequisite_tags_verified")
        feature_057_pilot_verified = _ensure_bool(self.feature_057_pilot_verified, "feature_057_pilot_verified")

        _required_keys(
            self.evaluation_trace_bank_summary,
            "evaluation_trace_bank_summary",
            (
                "evaluation_trace_bank_id",
                "evaluation_trace_count",
                "seed_bundle",
                "trace_identities",
                "trace_hashes",
                "trace_bank_signature",
                "repeatability_evidence",
                "bank_generation_repeatable",
            ),
        )
        _required_keys(
            self.train_eval_separation_summary,
            "train_eval_separation_summary",
            (
                "training_trace_bank_id",
                "evaluation_trace_bank_id",
                "training_trace_bank_exists",
                "evaluation_trace_bank_exists",
                "training_trace_ids",
                "evaluation_trace_ids",
                "overlap_trace_ids",
                "train_eval_trace_banks_disjoint",
                "evaluation_on_training_traces",
            ),
        )
        _required_keys(
            self.baseline_policy_registry_summary,
            "baseline_policy_registry_summary",
            (
                "registered_policy_names",
                "baseline_policy_count",
                "policies",
                "action_contract_compatible",
                "no_learned_policy_checkpoint_dependency",
            ),
        )
        _required_keys(
            self.baseline_evaluation_harness_summary,
            "baseline_evaluation_harness_summary",
            (
                "registered_policy_count",
                "evaluated_policy_count",
                "evaluation_trace_count",
                "per_policy_metric_shells",
                "no_optimizer_steps",
                "no_replay_mutation",
                "no_checkpoint_binary",
                "no_training_execution",
            ),
        )
        _required_keys(self.metric_schema_summary, "metric_schema_summary", ("required_metric_fields", "present_metric_fields", "missing_metric_fields", "metric_schema_complete"))
        _required_keys(self.determinism_summary, "determinism_summary", ("trace_bank_repeatable", "harness_outputs_repeatable", "first_run_signature", "second_run_signature", "repeatability_proven"))
        _required_keys(self.behavior_safety_summary, "behavior_safety_summary", BEHAVIOR_SAFETY_FIELDS)

        trace_count = int(self.evaluation_trace_bank_summary.get("evaluation_trace_count", 0))
        trace_identities = list(self.evaluation_trace_bank_summary.get("trace_identities", []))
        trace_hashes = list(self.evaluation_trace_bank_summary.get("trace_hashes", []))
        evaluation_trace_bank_ready = (
            bool(self.evaluation_trace_bank_summary.get("evaluation_trace_bank_id"))
            and trace_count > 0
            and len(trace_identities) == trace_count
            and len(trace_hashes) == trace_count
            and len(trace_identities) == len(set(trace_identities))
            and len(trace_hashes) == len(set(trace_hashes))
            and _ensure_bool(self.evaluation_trace_bank_summary.get("bank_generation_repeatable"), "evaluation_trace_bank_summary.bank_generation_repeatable")
        )

        train_eval_separation_ready = (
            bool(self.train_eval_separation_summary.get("training_trace_bank_id"))
            and bool(self.train_eval_separation_summary.get("evaluation_trace_bank_id"))
            and _ensure_bool(self.train_eval_separation_summary.get("training_trace_bank_exists"), "train_eval_separation_summary.training_trace_bank_exists")
            and _ensure_bool(self.train_eval_separation_summary.get("evaluation_trace_bank_exists"), "train_eval_separation_summary.evaluation_trace_bank_exists")
            and _ensure_bool(self.train_eval_separation_summary.get("train_eval_trace_banks_disjoint"), "train_eval_separation_summary.train_eval_trace_banks_disjoint")
            and self.train_eval_separation_summary.get("evaluation_on_training_traces") is False
            and self.train_eval_separation_summary.get("overlap_trace_ids") == []
        )

        baseline_policy_count = int(self.baseline_policy_registry_summary.get("baseline_policy_count", 0))
        policy_names = list(self.baseline_policy_registry_summary.get("registered_policy_names", []))
        baseline_registry_ready = (
            baseline_policy_count > 0
            and baseline_policy_count == len(policy_names)
            and len(policy_names) == len(set(policy_names))
            and _ensure_bool(self.baseline_policy_registry_summary.get("action_contract_compatible"), "baseline_policy_registry_summary.action_contract_compatible")
            and _ensure_bool(self.baseline_policy_registry_summary.get("no_learned_policy_checkpoint_dependency"), "baseline_policy_registry_summary.no_learned_policy_checkpoint_dependency")
        )

        per_policy_metric_shells = self.baseline_evaluation_harness_summary.get("per_policy_metric_shells", {})
        baseline_harness_ready = (
            int(self.baseline_evaluation_harness_summary.get("registered_policy_count", 0)) == baseline_policy_count
            and int(self.baseline_evaluation_harness_summary.get("evaluated_policy_count", 0)) == baseline_policy_count
            and int(self.baseline_evaluation_harness_summary.get("evaluation_trace_count", 0)) > 0
            and isinstance(per_policy_metric_shells, dict)
            and set(per_policy_metric_shells) == set(policy_names)
            and _ensure_bool(self.baseline_evaluation_harness_summary.get("no_optimizer_steps"), "baseline_evaluation_harness_summary.no_optimizer_steps")
            and _ensure_bool(self.baseline_evaluation_harness_summary.get("no_replay_mutation"), "baseline_evaluation_harness_summary.no_replay_mutation")
            and _ensure_bool(self.baseline_evaluation_harness_summary.get("no_checkpoint_binary"), "baseline_evaluation_harness_summary.no_checkpoint_binary")
            and _ensure_bool(self.baseline_evaluation_harness_summary.get("no_training_execution"), "baseline_evaluation_harness_summary.no_training_execution")
        )

        missing_metric_fields = list(self.metric_schema_summary.get("missing_metric_fields", []))
        metric_schema_ready = (
            tuple(self.metric_schema_summary.get("required_metric_fields", [])) == METRIC_SCHEMA_FIELDS
            and set(self.metric_schema_summary.get("present_metric_fields", [])) >= set(METRIC_SCHEMA_FIELDS)
            and missing_metric_fields == []
            and _ensure_bool(self.metric_schema_summary.get("metric_schema_complete"), "metric_schema_summary.metric_schema_complete")
        )

        determinism_ready = (
            _ensure_bool(self.determinism_summary.get("trace_bank_repeatable"), "determinism_summary.trace_bank_repeatable")
            and _ensure_bool(self.determinism_summary.get("harness_outputs_repeatable"), "determinism_summary.harness_outputs_repeatable")
            and self.determinism_summary.get("first_run_signature") == self.determinism_summary.get("second_run_signature")
            and _ensure_bool(self.determinism_summary.get("repeatability_proven"), "determinism_summary.repeatability_proven")
        )
        behavior_safe = all(_ensure_bool(self.behavior_safety_summary.get(key), f"behavior_safety_summary.{key}") for key in BEHAVIOR_SAFETY_FIELDS)

        ready = (
            feature_057_pilot_verified
            and evaluation_trace_bank_ready
            and train_eval_separation_ready
            and baseline_registry_ready
            and baseline_harness_ready
            and metric_schema_ready
            and determinism_ready
            and behavior_safe
            and not self.remaining_blockers
        )

        if ready:
            if self.final_verdict != "evaluation_trace_bank_baseline_harness_ready":
                raise ValueError("passing Feature 058 reports must use the ready verdict")
            if self.recommended_next_feature != READY_NEXT_FEATURE:
                raise ValueError("passing Feature 058 reports must route to Feature 059")
            return

        if self.final_verdict == "evaluation_trace_bank_baseline_harness_ready":
            raise ValueError("blocked Feature 058 reports cannot claim ready")
        if not self.remaining_blockers:
            raise ValueError("blocked Feature 058 reports must include blockers")
        if self.recommended_next_feature == READY_NEXT_FEATURE:
            raise ValueError("blocked Feature 058 reports must not route to Feature 059")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
