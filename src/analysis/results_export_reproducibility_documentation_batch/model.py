from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import FEATURE_ID, READY_NEXT_FEATURE, REQUIRED_TOP_LEVEL_FIELDS

ALLOWED_FINAL_VERDICTS = (
    "results_export_reproducibility_documentation_batch_passed",
    "feature_062_prerequisite_blocked",
    "final_integrity_audit_blocked",
    "results_export_blocked",
    "reproducibility_package_blocked",
    "mechanism_documentation_blocked",
    "artifact_index_blocked",
    "claim_boundary_blocked",
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
class ResultsExportReproducibilityDocumentationBatchReport:
    feature_id: str
    batch_items_covered: list[str]
    prerequisite_tags_verified: list[dict[str, Any]]
    feature_062_verified: bool
    final_integrity_audit_summary: dict[str, Any]
    results_export_summary: dict[str, Any]
    reproducibility_package_summary: dict[str, Any]
    mechanism_documentation_summary: dict[str, Any]
    artifact_index_summary: dict[str, Any]
    claim_boundary_summary: dict[str, Any]
    safety_summary: dict[str, Any]
    remaining_blockers: list[str] = field(default_factory=list)
    recommended_next_feature: str = ""
    final_verdict: str = "feature_062_prerequisite_blocked"

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 063-results-export-reproducibility-documentation-batch")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("invalid final_verdict")
        if list(self.batch_items_covered) != [
            "Final Experiment Integrity Audit",
            "Paper/Thesis Results Table Export",
            "Reproducibility Package",
            "Final Mechanism Documentation",
            "Final Artifact Index and Handoff Report",
        ]:
            raise ValueError("batch_items_covered must preserve the approved batch order")
        _unique_names(self.prerequisite_tags_verified)
        if not REQUIRED_TOP_LEVEL_FIELDS:
            raise ValueError("required fields unavailable")
        _required_keys(self.final_integrity_audit_summary, "final_integrity_audit_summary", ("claim_mappings", "unsupported_claims", "source_mapping_complete", "no_paper_reproduction_claim", "no_unsupported_superiority_claim", "no_training_rerun"))
        _required_keys(self.results_export_summary, "results_export_summary", ("csv_export", "markdown_export", "figure_data_export", "controlled_experiment_data_only"))
        _required_keys(self.reproducibility_package_summary, "reproducibility_package_summary", ("commands", "branch_tag_assumptions", "source_artifacts", "final_artifacts", "seed_set", "trace_bank_ids", "runtime_environment_assumptions", "known_limitations", "non_claim_boundaries"))
        _required_keys(self.mechanism_documentation_summary, "mechanism_documentation_summary", ("faithful_components", "implemented_simplifications", "deviation_notes", "real_torch_trainer_binding", "selected_action_outcome_evidence", "multi_seed_and_ablation_limits", "non_claims"))
        _required_keys(self.artifact_index_summary, "artifact_index_summary", ("artifact_entries", "all_required_artifacts_exist"))
        _required_keys(self.claim_boundary_summary, "claim_boundary_summary", ("controlled_experiment_data", "paper_reproduction_claim", "unsupported_superiority_claim", "production_performance_claim", "unsupported_claims_marked", "source_mapping_complete"))
        _required_keys(self.safety_summary, "safety_summary", ("no_training_rerun", "no_dependency_drift", "no_policy_drift", "no_environment_contract_drift", "no_reward_timing_change", "no_prior_feature_artifact_rewrite", "no_paper_reproduction_claim", "no_unsupported_superiority_claim", "no_uncontrolled_outputs"))
        if self.final_integrity_audit_summary.get("no_paper_reproduction_claim") is not True or self.final_integrity_audit_summary.get("no_unsupported_superiority_claim") is not True:
            raise ValueError("integrity audit must reject reproduction or superiority claims")
        if self.results_export_summary.get("controlled_experiment_data_only") is not True:
            raise ValueError("results export must remain controlled experiment data")
        if self.claim_boundary_summary.get("paper_reproduction_claim") is not False or self.claim_boundary_summary.get("unsupported_superiority_claim") is not False:
            raise ValueError("claim boundary must reject reproduction and superiority claims")
        if self.final_verdict == "results_export_reproducibility_documentation_batch_passed":
            if self.remaining_blockers:
                raise ValueError("passing report cannot include blockers")
            if self.recommended_next_feature != READY_NEXT_FEATURE:
                raise ValueError("passing report must route to Feature 064")
        else:
            if not self.remaining_blockers:
                raise ValueError("blocked report must include blockers")
            if self.recommended_next_feature == READY_NEXT_FEATURE:
                raise ValueError("blocked report must not route to Feature 064")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
