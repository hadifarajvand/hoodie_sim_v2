from __future__ import annotations

from pathlib import Path
import json
import subprocess
from typing import Any

from .config import (
    COMMITTED_INPUT_REPORTS,
    FEATURE_ID,
    READY_NEXT_FEATURE,
    ExposureMatrixPaperMechanismRerunConfig,
)
from .model import BehaviorEquivalenceSummary, ExposureMatrixPaperMechanismRerunReport
from .report import write_exposure_matrix_paper_mechanism_rerun_report


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_output(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _validate_feature_id(payload: dict[str, Any], expected: str, path: Path) -> None:
    if payload.get("feature_id") != expected:
        raise ValueError(f"{path} must contain feature_id={expected}")


def _load_committed_inputs(config: ExposureMatrixPaperMechanismRerunConfig) -> dict[str, dict[str, Any]]:
    payloads = {
        "048": _load_json(config.feature_048_report),
        "049": _load_json(config.feature_049_report),
        "050": _load_json(config.feature_050_report),
        "051": _load_json(config.feature_051_report),
        "052": _load_json(config.feature_052_report),
    }
    _validate_feature_id(payloads["048"], "048-legality-evidence-expansion", config.feature_048_report)
    _validate_feature_id(payloads["049"], "049-exposure-matrix-paper-mechanism-alignment", config.feature_049_report)
    _validate_feature_id(payloads["050"], "050-selected-action-family-per-action-outcome-evidence", config.feature_050_report)
    _validate_feature_id(payloads["051"], "051-passive-selected-action-trace-repair", config.feature_051_report)
    _validate_feature_id(payloads["052"], "052-selected-action-outcome-evidence-rerun", config.feature_052_report)
    return payloads


def _prerequisite_tags_verified() -> list[dict[str, Any]]:
    main_commit = _git_output("rev-parse", "main")
    feature_052_commit = _git_output("rev-parse", "052-selected-action-outcome-evidence-rerun-complete^{}")
    return [
        {"name": "branch", "verified": _git_output("branch", "--show-current") == FEATURE_ID, "details": f"current branch is {FEATURE_ID}"},
        {"name": "not_main", "verified": _git_output("branch", "--show-current") != "main", "details": "branch is not main"},
        {"name": "main_equals_feature_052", "verified": main_commit == feature_052_commit, "details": "main matches 052-selected-action-outcome-evidence-rerun-complete^{}"},
        {"name": "main_is_branch_base", "verified": _git_output("merge-base", "main", "HEAD") == main_commit, "details": "main is an ancestor of HEAD"},
    ]


def _prior_feature_gates_verified(payloads: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"feature": feature, "verified": path.exists(), "details": str(path)}
        for feature, path in COMMITTED_INPUT_REPORTS.items()
    ]


def _behavior_equivalence_summary(feature_051: dict[str, Any]) -> BehaviorEquivalenceSummary:
    summary = feature_051.get("behavior_equivalence_summary", {})
    checks = summary.get("checks", [])
    normalized_checks = [
        {
            "name": str(check.get("name")),
            "verified": bool(check.get("verified")),
            "details": check.get("details", ""),
        }
        for check in checks
    ]
    return BehaviorEquivalenceSummary(checks=normalized_checks, passed=bool(summary.get("passed")))


def _derived_exposure_matrix_internal_consistency(
    feature_048: dict[str, Any],
    feature_049: dict[str, Any],
    feature_051: dict[str, Any],
    feature_052: dict[str, Any],
) -> bool:
    observation_passed = bool(feature_049.get("observation_vector_audit", {}).get("passed"))
    formula_passed = bool(feature_049.get("paper_formula_unit_audit", {}).get("passed"))
    behavior_passed = bool(feature_051.get("behavior_equivalence_summary", {}).get("passed"))
    selected_action_statuses_available = (
        feature_052.get("selected_action_family_evidence_status") == "available"
        and feature_052.get("selected_action_to_task_join_status") == "available"
        and feature_052.get("per_action_outcome_evidence_status") == "available"
    )
    feature_052_gate_inputs_ready = (
        feature_052.get("feature_049_can_be_rerun") is True
        and feature_052.get("feature_049_remaining_blockers") == []
        and feature_052.get("final_verdict") == "selected_action_outcome_evidence_ready_for_feature_049_rerun"
    )
    return (
        feature_048.get("final_verdict") == "legality_evidence_ready_for_exposure_matrix_rerun"
        and bool(feature_048.get("exposure_matrix_unblocked"))
        and observation_passed
        and formula_passed
        and behavior_passed
        and selected_action_statuses_available
        and feature_052_gate_inputs_ready
    )


def _feature_052_readiness_verified(
    feature_048: dict[str, Any],
    feature_049: dict[str, Any],
    feature_051: dict[str, Any],
    feature_052: dict[str, Any],
) -> tuple[bool, bool]:
    exposure_matrix_internal_consistency_verified = _derived_exposure_matrix_internal_consistency(feature_048, feature_049, feature_051, feature_052)
    feature_052_trace_readiness_verified = (
        feature_052.get("feature_049_can_be_rerun") is True
        and feature_052.get("feature_049_remaining_blockers") == []
        and feature_052.get("per_action_outcome_evidence_status") == "available"
        and feature_052.get("final_verdict") == "selected_action_outcome_evidence_ready_for_feature_049_rerun"
        and exposure_matrix_internal_consistency_verified
    )
    return feature_052_trace_readiness_verified, exposure_matrix_internal_consistency_verified


def _alignment_statuses(
    feature_048: dict[str, Any],
    feature_049: dict[str, Any],
    feature_050: dict[str, Any],
    feature_051: dict[str, Any],
    feature_052: dict[str, Any],
    feature_052_readiness_verified: bool,
    exposure_matrix_internal_consistency_verified: bool,
) -> tuple[str, str, str, str, str]:
    observation_vector_alignment_status = "available" if bool(feature_049.get("observation_vector_audit", {}).get("passed")) else ("partial" if feature_049.get("observation_vector_audit") else "unavailable")
    formula_unit_alignment_status = "available" if bool(feature_049.get("paper_formula_unit_audit", {}).get("passed")) else ("partial" if feature_049.get("paper_formula_unit_audit") else "unavailable")
    selected_action_outcome_alignment_status = "available" if feature_052.get("per_action_outcome_evidence_status") == "available" and feature_052.get("feature_049_can_be_rerun") is True else ("partial" if feature_052.get("per_action_outcome_evidence_status") in {"partial", "available"} else "unavailable")
    exposure_matrix_alignment_status = "available" if exposure_matrix_internal_consistency_verified else ("partial" if feature_052_readiness_verified else "unavailable")
    training_readiness_contract_status = "available" if (
        feature_052_readiness_verified
        and observation_vector_alignment_status == "available"
        and formula_unit_alignment_status == "available"
        and exposure_matrix_alignment_status == "available"
        and selected_action_outcome_alignment_status == "available"
        and bool(feature_051.get("behavior_equivalence_summary", {}).get("passed"))
    ) else "partial" if feature_052_readiness_verified else "unavailable"
    return (
        observation_vector_alignment_status,
        formula_unit_alignment_status,
        exposure_matrix_alignment_status,
        selected_action_outcome_alignment_status,
        training_readiness_contract_status,
    )


def _remaining_blockers(
    feature_052_readiness_verified: bool,
    observation_vector_alignment_status: str,
    formula_unit_alignment_status: str,
    exposure_matrix_alignment_status: str,
    selected_action_outcome_alignment_status: str,
    training_readiness_contract_status: str,
    behavior_equivalence_passed: bool,
) -> list[str]:
    blockers: list[str] = []
    if not feature_052_readiness_verified:
        blockers.append("feature_052_readiness_failed")
    if observation_vector_alignment_status != "available":
        blockers.append("observation_vector_alignment_blocked")
    if formula_unit_alignment_status != "available":
        blockers.append("formula_unit_alignment_blocked")
    if exposure_matrix_alignment_status != "available":
        blockers.append("exposure_matrix_alignment_blocked")
    if selected_action_outcome_alignment_status != "available":
        blockers.append("selected_action_outcome_alignment_blocked")
    if training_readiness_contract_status != "available":
        blockers.append("training_readiness_contract_blocked")
    if not behavior_equivalence_passed:
        blockers.append("behavior_drift_detected")
    return blockers


def _final_decision(
    feature_052_readiness_verified: bool,
    observation_vector_alignment_status: str,
    formula_unit_alignment_status: str,
    exposure_matrix_alignment_status: str,
    selected_action_outcome_alignment_status: str,
    training_readiness_contract_status: str,
    behavior_equivalence_passed: bool,
) -> tuple[bool, str, str, list[str]]:
    blockers = _remaining_blockers(
        feature_052_readiness_verified,
        observation_vector_alignment_status,
        formula_unit_alignment_status,
        exposure_matrix_alignment_status,
        selected_action_outcome_alignment_status,
        training_readiness_contract_status,
        behavior_equivalence_passed,
    )
    if not feature_052_readiness_verified:
        return False, "prerequisite_blocked", "Feature 052 — Selected-Action Outcome Evidence Rerun", blockers
    if observation_vector_alignment_status != "available":
        return False, "observation_vector_alignment_blocked", "observation vector alignment repair before training", blockers
    if formula_unit_alignment_status != "available":
        return False, "formula_unit_alignment_blocked", "formula/unit alignment repair before training", blockers
    if exposure_matrix_alignment_status != "available":
        return False, "exposure_matrix_alignment_blocked", "exposure matrix alignment repair before training", blockers
    if selected_action_outcome_alignment_status != "available":
        return False, "selected_action_outcome_alignment_blocked", "selected-action outcome evidence repair before training", blockers
    if not behavior_equivalence_passed:
        return False, "behavior_drift_detected", "behavior drift repair before training", blockers
    if training_readiness_contract_status != "available":
        return False, "prerequisite_blocked", "training readiness contract repair before Feature 054", blockers
    return True, "paper_mechanism_alignment_ready_for_training_contract", READY_NEXT_FEATURE, []


def build_exposure_matrix_paper_mechanism_rerun_report(
    config: ExposureMatrixPaperMechanismRerunConfig | None = None,
) -> ExposureMatrixPaperMechanismRerunReport:
    config = config or ExposureMatrixPaperMechanismRerunConfig()
    payloads = _load_committed_inputs(config)
    feature_048 = payloads["048"]
    feature_049 = payloads["049"]
    feature_050 = payloads["050"]
    feature_051 = payloads["051"]
    feature_052 = payloads["052"]
    behavior_equivalence_summary = _behavior_equivalence_summary(feature_051)
    feature_052_trace_readiness_verified, exposure_matrix_internal_consistency_verified = _feature_052_readiness_verified(
        feature_048,
        feature_049,
        feature_051,
        feature_052,
    )
    observation_vector_alignment_status, formula_unit_alignment_status, exposure_matrix_alignment_status, selected_action_outcome_alignment_status, training_readiness_contract_status = _alignment_statuses(
        feature_048,
        feature_049,
        feature_050,
        feature_051,
        feature_052,
        feature_052_trace_readiness_verified,
        exposure_matrix_internal_consistency_verified,
    )
    paper_mechanism_alignment_ready, final_verdict, recommended_next_feature, blockers = _final_decision(
        feature_052_trace_readiness_verified,
        observation_vector_alignment_status,
        formula_unit_alignment_status,
        exposure_matrix_alignment_status,
        selected_action_outcome_alignment_status,
        training_readiness_contract_status,
        behavior_equivalence_summary.passed,
    )
    if paper_mechanism_alignment_ready:
        blockers = []
    report = ExposureMatrixPaperMechanismRerunReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=_prerequisite_tags_verified(),
        prior_feature_gates_verified=_prior_feature_gates_verified(payloads),
        feature_052_trace_readiness_verified=feature_052_trace_readiness_verified,
        feature_052_readiness_verified=feature_052_trace_readiness_verified,
        observation_vector_alignment_status=observation_vector_alignment_status,
        formula_unit_alignment_status=formula_unit_alignment_status,
        exposure_matrix_alignment_status=exposure_matrix_alignment_status,
        selected_action_outcome_alignment_status=selected_action_outcome_alignment_status,
        training_readiness_contract_status=training_readiness_contract_status,
        paper_mechanism_alignment_ready=paper_mechanism_alignment_ready,
        remaining_blockers=blockers,
        recommended_next_feature=recommended_next_feature,
        behavior_equivalence_summary=behavior_equivalence_summary,
        behavior_equivalence_passed=behavior_equivalence_summary.passed,
        final_verdict=final_verdict,
    )
    return report


def run_exposure_matrix_paper_mechanism_rerun(output_dir: Path | str | None = None) -> ExposureMatrixPaperMechanismRerunReport:
    report = build_exposure_matrix_paper_mechanism_rerun_report()
    write_exposure_matrix_paper_mechanism_rerun_report(report, output_dir)
    return report


def main() -> int:
    run_exposure_matrix_paper_mechanism_rerun()
    return 0
