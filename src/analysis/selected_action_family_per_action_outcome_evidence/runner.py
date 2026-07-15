from __future__ import annotations

from pathlib import Path
import json
import subprocess
from typing import Any

from .config import FEATURE_ID, PRIOR_ARTIFACTS, SelectedActionOutcomeEvidenceConfig
from .model import (
    BehaviorEquivalenceSummary,
    ExposureMatrixInternalConsistencySummary,
    Feature049UnblockAssessment,
    LegalButUnselectedConsistencySummary,
    PerActionOutcomeJoinSummary,
    PerActionOutcomeMatrix,
    SelectedActionFamilyEvidenceSummary,
    SelectedActionOutcomeEvidenceReport,
    SelectedActionToTaskJoinSummary,
)
from .report import write_selected_action_outcome_evidence_report


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_output(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _current_branch() -> str:
    return _git_output("branch", "--show-current")


def _prerequisite_tags_verified() -> list[dict[str, Any]]:
    return [
        {"name": "branch", "verified": _current_branch() == FEATURE_ID, "details": f"current branch is {FEATURE_ID}"},
        {"name": "not_main", "verified": _current_branch() != "main", "details": "branch is not main"},
        {"name": "main_equals_origin_main", "verified": _git_output("rev-parse", "main") == _git_output("rev-parse", "origin/main"), "details": "main matches origin/main"},
        {"name": "main_equals_049", "verified": _git_output("rev-parse", "main") == _git_output("rev-parse", "049-exposure-matrix-paper-mechanism-alignment-complete^{}"), "details": "main matches 049-exposure-matrix-paper-mechanism-alignment-complete^{}"},
        {"name": "prerequisite_diff_empty", "verified": _git_output("diff", "--name-only", "049-exposure-matrix-paper-mechanism-alignment-complete^{}", "main") == "", "details": "diff between 049-exposure-matrix-paper-mechanism-alignment-complete^{} and main is empty"},
        {"name": "pointer_correct", "verified": "specs/050-selected-action-family-per-action-outcome-evidence" in Path(".specify/feature.json").read_text(encoding="utf-8"), "details": ".specify/feature.json points at Feature 050"},
        {"name": "pointer_not_staged", "verified": _git_output("diff", "--cached", "--name-only", "--", ".specify/feature.json") == "", "details": ".specify/feature.json is not staged"},
        {"name": "pointer_not_in_main_head", "verified": ".specify/feature.json" not in _git_output("diff", "--name-only", "origin/main...HEAD").splitlines(), "details": ".specify/feature.json is not in origin/main...HEAD diff"},
        {"name": "agents_clean_before_report", "verified": _git_output("status", "--short").find("AGENTS.md") == -1, "details": "AGENTS.md clean before report generation"},
    ]


def _prior_feature_gates_verified() -> list[dict[str, Any]]:
    return [{"name": name, "verified": path.exists(), "details": str(path)} for name, path in PRIOR_ARTIFACTS.items()]


def _behavior_equivalence_summary(feature_044: dict[str, Any]) -> BehaviorEquivalenceSummary:
    checks = feature_044.get("behavior_equivalence_checks", [])
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for check in checks:
        name = check.get("name")
        if name in seen:
            continue
        seen.add(name)
        deduped.append({"name": name, "verified": bool(check.get("verified")), "details": check.get("details", "")})
    return BehaviorEquivalenceSummary(checks=deduped, passed=all(item["verified"] for item in deduped))


def build_selected_action_outcome_evidence_report(config: SelectedActionOutcomeEvidenceConfig | None = None) -> SelectedActionOutcomeEvidenceReport:
    config = config or SelectedActionOutcomeEvidenceConfig()
    feature_044 = _load_json(PRIOR_ARTIFACTS["passive_runtime_lifecycle_trace_instrumentation"])
    feature_048 = _load_json(PRIOR_ARTIFACTS["exposure_matrix_paper_mechanism_alignment"])
    behavior = _behavior_equivalence_summary(feature_044)
    selected_action_family_evidence_status = feature_048.get("selected_action_family_evidence_status", "unavailable")
    selected_action_to_task_join_status = "unavailable"
    per_action_outcome_evidence_status = feature_048.get("per_action_outcome_evidence_status", "unavailable")
    exposure_matrix_internal_consistency_verified = bool(feature_048.get("exposure_matrix_internal_consistency_verified", False))
    feature_049_can_be_rerun = (
        selected_action_family_evidence_status == "available"
        and selected_action_to_task_join_status == "available"
        and per_action_outcome_evidence_status == "available"
        and exposure_matrix_internal_consistency_verified
        and behavior.passed
        and bool(feature_048.get("no_action_selection_drift", False))
        and bool(feature_048.get("no_action_legality_drift", False))
    )
    blockers = [
        reason
        for condition, reason in [
            (selected_action_family_evidence_status != "available", "selected_action_family_evidence_incomplete"),
            (selected_action_to_task_join_status != "available", "selected_action_to_task_join_incomplete"),
            (per_action_outcome_evidence_status != "available", "per_action_outcome_join_incomplete"),
            (not exposure_matrix_internal_consistency_verified, "exposure_matrix_internal_consistency_failed"),
            (not behavior.passed, "behavior_equivalence_failed"),
        ]
        if condition
    ]
    if feature_048.get("selected_action_family_evidence_status") == "unavailable" and "selected_action_family_evidence_incomplete" not in blockers:
        blockers.append("selected_action_family_evidence_incomplete")
    feature_049_unblock_assessment = Feature049UnblockAssessment(
        feature_049_can_be_rerun=feature_049_can_be_rerun,
        feature_049_remaining_blockers=blockers if not feature_049_can_be_rerun else [],
        selected_action_family_evidence_status=selected_action_family_evidence_status,
        selected_action_to_task_join_status=selected_action_to_task_join_status,
        per_action_outcome_evidence_status=per_action_outcome_evidence_status,
        exposure_matrix_internal_consistency_verified=exposure_matrix_internal_consistency_verified,
        behavior_equivalence_passed=behavior.passed,
        recommended_next_feature="Feature 051 — Exposure Matrix Paper Mechanism Rerun with Outcome Evidence" if feature_049_can_be_rerun else "selected-action family trace repair before training",
    )
    final_verdict = "selected_action_outcome_evidence_ready_for_feature_049_rerun" if feature_049_can_be_rerun else "selected_action_family_evidence_incomplete"
    if selected_action_family_evidence_status != "available":
        final_verdict = "selected_action_family_evidence_incomplete"
    elif selected_action_to_task_join_status != "available":
        final_verdict = "per_action_outcome_join_incomplete"
    elif per_action_outcome_evidence_status != "available":
        final_verdict = "per_action_outcome_join_incomplete"
    if not exposure_matrix_internal_consistency_verified:
        final_verdict = "exposure_matrix_internal_consistency_failed"
    if not behavior.passed:
        final_verdict = "behavior_drift_detected"
    selected_family_summary = SelectedActionFamilyEvidenceSummary(
        evidence_status=selected_action_family_evidence_status,
        selected_local_count=feature_048.get("selected_local_count"),
        selected_horizontal_count=feature_048.get("selected_horizontal_count"),
        selected_vertical_count=feature_048.get("selected_vertical_count"),
        selected_action_count=feature_048.get("selected_action_count"),
        selected_action_count_consistency_verified=bool(feature_048.get("selected_action_count_consistency_verified", False)),
    )
    selected_to_task_summary = SelectedActionToTaskJoinSummary(
        selected_action_to_task_join_count=None,
        selected_action_to_task_join_ratio=None,
        missing_selected_action_task_join_count=None,
        selected_action_to_task_join_status=selected_action_to_task_join_status,
    )
    per_action_summary = PerActionOutcomeJoinSummary(
        per_action_completion_count={"local": None, "horizontal": None, "vertical": None},
        per_action_drop_count={"local": None, "horizontal": None, "vertical": None},
        per_action_pending_count={"local": None, "horizontal": None, "vertical": None},
        per_action_completion_rate={"local": None, "horizontal": None, "vertical": None},
        per_action_drop_rate={"local": None, "horizontal": None, "vertical": None},
        per_action_pending_rate={"local": None, "horizontal": None, "vertical": None},
        per_action_outcome_evidence_status=per_action_outcome_evidence_status,
    )
    report = SelectedActionOutcomeEvidenceReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=_prerequisite_tags_verified(),
        prior_feature_gates_verified=_prior_feature_gates_verified(),
        selected_action_family_evidence_status=selected_action_family_evidence_status,
        selected_action_to_task_join_status=selected_action_to_task_join_status,
        per_action_outcome_evidence_status=per_action_outcome_evidence_status,
        behavior_equivalence_passed=behavior.passed,
        selected_action_family_evidence_summary=selected_family_summary,
        per_strategy_seed_selected_action_family_matrix=[],
        selected_action_to_task_join_summary=selected_to_task_summary,
        per_action_outcome_join_summary=per_action_summary,
        per_action_outcome_matrix=PerActionOutcomeMatrix(per_strategy_seed_selected_action_family_matrix=[], per_action_outcome_join_summary=per_action_summary),
        legal_but_unselected_consistency_summary=LegalButUnselectedConsistencySummary(None, None, None, False),
        exposure_matrix_internal_consistency_summary=ExposureMatrixInternalConsistencySummary(
            selected_action_count_consistency_verified=bool(feature_048.get("selected_action_count_consistency_verified", False)),
            selected_illegal_action_count=feature_048.get("selected_illegal_action_count"),
            selected_action_to_task_join_status=selected_action_to_task_join_status,
            per_action_outcome_evidence_status=per_action_outcome_evidence_status,
            legal_but_unselected_consistency_verified=bool(feature_048.get("legal_but_unselected_consistency_verified", False)),
            exposure_matrix_internal_consistency_verified=exposure_matrix_internal_consistency_verified,
        ),
        exposure_matrix_internal_consistency_verified=exposure_matrix_internal_consistency_verified,
        feature_049_can_be_rerun=feature_049_can_be_rerun,
        feature_049_remaining_blockers=[] if feature_049_can_be_rerun else blockers,
        feature_049_unblock_assessment=feature_049_unblock_assessment,
        behavior_equivalence_summary=behavior,
        evidence_population_summary={
            "selected_action_family_evidence_source": PRIOR_ARTIFACTS["exposure_matrix_paper_mechanism_alignment"].as_posix(),
            "selected_action_to_task_join_source": None,
            "per_action_outcome_source": PRIOR_ARTIFACTS["exposure_matrix_paper_mechanism_alignment"].as_posix(),
        },
        final_verdict=final_verdict,
        recommended_next_feature=feature_049_unblock_assessment.recommended_next_feature,
    )
    return report


def run_selected_action_outcome_evidence(output_dir: Path | str | None = None) -> SelectedActionOutcomeEvidenceReport:
    report = build_selected_action_outcome_evidence_report()
    write_selected_action_outcome_evidence_report(report, output_dir)
    return report
