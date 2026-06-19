from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import FEATURE_ID, READY_NEXT_STEP, REQUIRED_FIGURES

ALLOWED_FINAL_VERDICTS = (
    "unified_campaign_result_analysis_ready",
    "feature_060_prerequisite_blocked",
    "result_integrity_blocked",
    "comparison_readiness_blocked",
    "baseline_consistency_blocked",
    "metric_schema_blocked",
    "figure_generation_blocked",
    "findings_report_blocked",
    "claim_safety_blocked",
    "scope_drift_detected",
)


@dataclass(frozen=True, slots=True)
class UnifiedCampaignAnalysisReport:
    feature_id: str
    feature_060_prerequisite_verification: dict[str, Any]
    integrity_audit_result: dict[str, Any]
    training_metrics_summary: dict[str, Any]
    evaluation_metrics_summary: dict[str, Any]
    baseline_evaluation_summary: dict[str, Any]
    comparison_readiness: dict[str, Any]
    result_tables_summary: dict[str, Any]
    figure_manifest: dict[str, Any]
    claim_safety_review: dict[str, Any]
    remaining_blockers: list[str] = field(default_factory=list)
    recommended_next_step: str = ""
    final_verdict: str = "feature_060_prerequisite_blocked"

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError(f"feature_id must equal {FEATURE_ID}")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("invalid final_verdict")
        if self.final_verdict == "unified_campaign_result_analysis_ready":
            if self.remaining_blockers:
                raise ValueError("ready verdict cannot include blockers")
            if self.recommended_next_step != READY_NEXT_STEP:
                raise ValueError("ready verdict must use the configured next step")
            if not self.feature_060_prerequisite_verification.get("verified"):
                raise ValueError("ready verdict requires Feature 060 prerequisite verification")
            if not self.integrity_audit_result.get("passed"):
                raise ValueError("ready verdict requires passing integrity audit")
            if not self.comparison_readiness.get("comparison_ready"):
                raise ValueError("ready verdict requires comparison readiness")
            if not self.claim_safety_review.get("claim_safety_passed"):
                raise ValueError("ready verdict requires claim safety")
            missing = set(REQUIRED_FIGURES) - set(self.figure_manifest.get("figure_files", []))
            if missing:
                raise ValueError(f"ready verdict requires all figures: {sorted(missing)}")
        if self.claim_safety_review.get("paper_reproduction_claim_made"):
            raise ValueError("paper reproduction claim is forbidden")
        if self.claim_safety_review.get("performance_superiority_claim_made"):
            raise ValueError("performance superiority claim is forbidden")
        if self.claim_safety_review.get("baseline_superiority_claim_made"):
            raise ValueError("baseline superiority claim is forbidden")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
