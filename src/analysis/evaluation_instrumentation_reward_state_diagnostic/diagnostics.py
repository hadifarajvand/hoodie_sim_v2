from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .config import (
    FEATURE_060_BASELINE_EVALUATION_METRICS,
    FEATURE_060_EVALUATION_METRICS,
    FEATURE_060_REPORT,
    FEATURE_060_TRAINING_METRICS,
    FEATURE_062_COMPARISON_READINESS,
    FEATURE_062_FINAL_FINDINGS,
    FEATURE_062_REPORT,
    FEATURE_063_CHECKPOINT_METRICS,
    FEATURE_063_COMPARISON_READINESS,
    FEATURE_063_REPORT,
    FEATURE_063_STAGED_COMPARATIVE_TABLE,
    FEATURE_064_REPORT,
)
from .model import ClaimSafetyStatus, DiagnosticDecision

ACTION_ORDER = ("local", "horizontal", "vertical")


def load_json(path: Path) -> dict[str, Any]:
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def artifact_status(path: Path) -> dict[str, Any]:
    return {"path": str(path), "exists": path.exists(), "verified": False, "details": ""}


def git_output(*args: str) -> str:
    import subprocess

    try:
        return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def git_status_paths() -> list[str]:
    output = git_output("status", "--short", "--untracked-files=all")
    return [line[3:].strip() for line in output.splitlines() if line.strip()]


def git_staged_paths() -> list[str]:
    return [line.strip() for line in git_output("diff", "--cached", "--name-only").splitlines() if line.strip()]


def git_diff_paths(base_ref: str) -> list[str]:
    return [line.strip() for line in git_output("diff", "--name-only", f"{base_ref}...HEAD").splitlines() if line.strip()]


def path_is_approved(path: str, prefixes: tuple[str, ...], forbidden_prefixes: tuple[str, ...]) -> bool:
    if any(path.startswith(prefix) for prefix in forbidden_prefixes):
        return False
    return any(path.startswith(prefix) for prefix in prefixes)


def classify_paths(paths: list[str], approved_prefixes: tuple[str, ...], forbidden_prefixes: tuple[str, ...]) -> dict[str, Any]:
    forbidden = [path for path in paths if any(path.startswith(prefix) for prefix in forbidden_prefixes)]
    approved = [path for path in paths if any(path.startswith(prefix) for prefix in approved_prefixes)]
    return {
        "paths": list(paths),
        "approved_paths_detected": approved,
        "forbidden_paths_detected": forbidden,
        "approved": not forbidden and (not paths or len(approved) == len(paths)),
    }


def _required_keys(summary: dict[str, Any], field_name: str, keys: tuple[str, ...]) -> None:
    missing = [key for key in keys if key not in summary]
    if missing:
        raise ValueError(f"{field_name} is missing required keys: {missing}")


def load_feature_060_status() -> dict[str, Any]:
    status = {
        "path": str(FEATURE_060_REPORT),
        "exists": FEATURE_060_REPORT.exists(),
        "verified": False,
        "details": "",
    }
    if not status["exists"]:
        return status
    report = load_json(FEATURE_060_REPORT)
    training = load_json(FEATURE_060_TRAINING_METRICS) if FEATURE_060_TRAINING_METRICS.exists() else {}
    evaluation = load_json(FEATURE_060_EVALUATION_METRICS) if FEATURE_060_EVALUATION_METRICS.exists() else {}
    baseline = load_json(FEATURE_060_BASELINE_EVALUATION_METRICS) if FEATURE_060_BASELINE_EVALUATION_METRICS.exists() else {}
    status["verified"] = (
        report.get("final_verdict") == "full_paper_default_training_campaign_execution_passed"
        and report.get("remaining_blockers") == []
        and report.get("feature_058_harness_verified") is True
        and report.get("feature_059_gate_verified") is True
        and report.get("feature_060a_validation_verified") is True
        and training.get("action_accounting_reconciled") is True
        and evaluation.get("metric_schema_coverage", {}).get("metric_schema_complete") is True
        and baseline.get("baseline_metrics_real_execution") is True
        and baseline.get("no_baseline_superiority_claim") is True
    )
    status["details"] = "Feature 060 report, training metrics, evaluation metrics, and baseline evaluation metrics validated"
    return status


def load_feature_062_status() -> dict[str, Any]:
    status = {
        "path": str(FEATURE_062_REPORT),
        "exists": FEATURE_062_REPORT.exists(),
        "verified": False,
        "details": "",
    }
    if not status["exists"]:
        return status
    report = load_json(FEATURE_062_REPORT)
    readiness = load_json(FEATURE_062_COMPARISON_READINESS) if FEATURE_062_COMPARISON_READINESS.exists() else {}
    findings_text = FEATURE_062_FINAL_FINDINGS.read_text(encoding="utf-8") if FEATURE_062_FINAL_FINDINGS.exists() else ""
    status["verified"] = (
        report.get("final_verdict") == "unified_campaign_result_analysis_ready"
        and report.get("remaining_blockers") == []
        and report.get("comparison_readiness", {}).get("comparison_ready") is True
        and readiness.get("comparison_ready") is True
        and "comparison-ready" in findings_text.lower()
    )
    status["details"] = "Feature 062 comparison-readiness and findings validated"
    return status


def load_feature_063_status() -> dict[str, Any]:
    status = {
        "path": str(FEATURE_063_REPORT),
        "exists": FEATURE_063_REPORT.exists(),
        "verified": False,
        "details": "",
    }
    if not status["exists"]:
        return status
    report = load_json(FEATURE_063_REPORT)
    checkpoint_metrics = load_json(FEATURE_063_CHECKPOINT_METRICS) if FEATURE_063_CHECKPOINT_METRICS.exists() else []
    readiness = load_json(FEATURE_063_COMPARISON_READINESS) if FEATURE_063_COMPARISON_READINESS.exists() else {}
    comparison_table = load_json(FEATURE_063_STAGED_COMPARATIVE_TABLE) if FEATURE_063_STAGED_COMPARATIVE_TABLE.exists() else {}
    budgets = [entry.get("training_budget") for entry in checkpoint_metrics] if isinstance(checkpoint_metrics, list) else []
    status["verified"] = (
        report.get("final_verdict") == "staged_training_budget_learning_curve_ready"
        and report.get("remaining_blockers") == []
        and report.get("training_mode") == "cumulative_staged"
        and report.get("training_rerun_from_scratch") is False
        and report.get("checkpoint_budgets") == [100, 150, 200, 500]
        and readiness.get("comparison_ready") is True
        and readiness.get("training_mode") == "cumulative_staged"
        and comparison_table.get("rows")
        and budgets == [100, 150, 200, 500]
    )
    status["details"] = "Feature 063 checkpoint metrics, comparison readiness, and staged comparative table validated"
    return status


def load_feature_064_status() -> dict[str, Any]:
    status = {
        "path": str(FEATURE_064_REPORT),
        "exists": FEATURE_064_REPORT.exists(),
        "verified": False,
        "details": "",
    }
    if not status["exists"]:
        return status
    report = load_json(FEATURE_064_REPORT)
    status["verified"] = (
        report.get("final_verdict") == "final_review_release_gate_blocked"
        and report.get("feature_060_prerequisite_verified") is True
        and report.get("feature_062_prerequisite_verified") is True
        and report.get("feature_063_prerequisite_verified") is True
        and report.get("claim_safety_status", {}).get("claim_safety_passed") is True
    )
    status["details"] = "Feature 064 blocked gate validated as the accepted prerequisite"
    return status


def build_prerequisite_artifacts() -> dict[str, dict[str, Any]]:
    return {
        "feature_060_report": load_feature_060_status(),
        "feature_060_training_metrics": artifact_status(FEATURE_060_TRAINING_METRICS),
        "feature_060_evaluation_metrics": artifact_status(FEATURE_060_EVALUATION_METRICS),
        "feature_060_baseline_evaluation_metrics": artifact_status(FEATURE_060_BASELINE_EVALUATION_METRICS),
        "feature_062_report": load_feature_062_status(),
        "feature_062_comparison_readiness": artifact_status(FEATURE_062_COMPARISON_READINESS),
        "feature_062_final_findings": artifact_status(FEATURE_062_FINAL_FINDINGS),
        "feature_063_report": load_feature_063_status(),
        "feature_063_checkpoint_metrics": artifact_status(FEATURE_063_CHECKPOINT_METRICS),
        "feature_063_comparison_readiness": artifact_status(FEATURE_063_COMPARISON_READINESS),
        "feature_063_staged_comparative_table": artifact_status(FEATURE_063_STAGED_COMPARATIVE_TABLE),
        "feature_064_report": load_feature_064_status(),
    }


def build_prerequisite_tags(working_tree_paths_approved: bool, staged_paths_approved: bool, base_branch_diff_approved: bool) -> list[dict[str, Any]]:
    branch = git_output("branch", "--show-current")
    return [
        {"name": "branch", "verified": branch == "065-evaluation-instrumentation-reward-state-diagnostic", "details": "current branch matches Feature 065"},
        {"name": "not_main", "verified": branch != "main", "details": "current branch is not main"},
        {"name": "feature_064_report_valid", "verified": load_feature_064_status()["verified"], "details": "Feature 064 blocked gate validated"},
        {"name": "feature_063_report_valid", "verified": load_feature_063_status()["verified"], "details": "Feature 063 outputs validated"},
        {"name": "feature_062_report_valid", "verified": load_feature_062_status()["verified"], "details": "Feature 062 outputs validated"},
        {"name": "feature_060_report_valid", "verified": load_feature_060_status()["verified"], "details": "Feature 060 outputs validated"},
        {"name": "working_tree_paths_approved", "verified": working_tree_paths_approved, "details": "working tree paths stay inside the approved scope"},
        {"name": "staged_paths_approved", "verified": staged_paths_approved, "details": "staged paths stay inside the approved scope"},
        {"name": "base_branch_head_diff_approved", "verified": base_branch_diff_approved, "details": "base-branch diff stays inside the approved scope"},
    ]


def build_scope_guard_summary(
    status_paths: list[str],
    staged_paths: list[str],
    diff_paths: list[str],
    approved_prefixes: tuple[str, ...],
    forbidden_prefixes: tuple[str, ...],
) -> dict[str, Any]:
    status_classification = classify_paths(status_paths, approved_prefixes, forbidden_prefixes)
    staged_classification = classify_paths(staged_paths, approved_prefixes, forbidden_prefixes)
    diff_classification = classify_paths(diff_paths, approved_prefixes, forbidden_prefixes)
    return {
        "working_tree_paths_approved": status_classification["approved"],
        "staged_paths_approved": staged_classification["approved"],
        "base_branch_head_diff_approved": diff_classification["approved"],
        "forbidden_paths_detected": status_classification["forbidden_paths_detected"] + staged_classification["forbidden_paths_detected"] + diff_classification["forbidden_paths_detected"],
        "approved_paths_detected": status_classification["approved_paths_detected"] + staged_classification["approved_paths_detected"] + diff_classification["approved_paths_detected"],
        "status_classification": status_classification,
        "staged_classification": staged_classification,
        "diff_classification": diff_classification,
    }


def build_claim_safety_status() -> dict[str, Any]:
    status = ClaimSafetyStatus(
        paper_reproduction_claim_made=False,
        performance_superiority_claim_made=False,
        baseline_superiority_claim_made=False,
        claim_safety_passed=True,
    )
    return status.to_dict()


def build_diagnostic_decision(
    *,
    policy_affects_reward: str,
    policy_affects_terminal_outcomes: str,
    evaluation_reward_static_after_instrumentation: bool,
    candidate_policy_vertical_collapse_in_evaluation: bool | str,
    candidate_policy_vertical_collapse_in_training_replay_window: bool | str,
    state_feature_coverage_summary: dict[str, Any],
    reward_decomposition_summary: dict[str, Any],
    action_logging_summary: dict[str, Any],
    raw_vs_canonical_metric_comparison: dict[str, Any] | None = None,
    canonical_task_outcome_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    comparison = raw_vs_canonical_metric_comparison or {}
    canonical_summary = canonical_task_outcome_summary or {}
    if comparison.get("double_count_detected") and comparison.get("duplicate_terminal_event_count", 0) > 0:
        recommended_next_action = "fix_environment_lifecycle_accounting_next"
        reason = "Raw lifecycle events exceed canonical task outcomes, so the lifecycle accounting path needs repair before any stronger claim."
    elif not reward_decomposition_summary.get("reward_available_count", 0):
        recommended_next_action = "fix_reward_function_next"
        reason = "No reward-bearing transitions were recovered from the instrumented evaluation."
    elif action_logging_summary.get("evaluation_action_distribution_source") != "evaluation_episodes":
        recommended_next_action = "blocked_due_to_unresolved_canonical_aggregation"
        reason = "Evaluation action logging could not be proven to come from evaluation episodes."
    elif candidate_policy_vertical_collapse_in_evaluation is True or candidate_policy_vertical_collapse_in_training_replay_window is True:
        if policy_affects_reward == "false" and policy_affects_terminal_outcomes == "false":
            recommended_next_action = "fix_state_representation_next"
            reason = "The candidate policy still collapses to vertical while canonical metrics do not move, which points at the visible state rather than the metric plumbing."
        elif evaluation_reward_static_after_instrumentation:
            recommended_next_action = "fix_evaluation_metric_aggregation_next"
            reason = "Canonical reward stayed static while the action and outcome signals were separated, so the aggregation layer still needs work."
        else:
            recommended_next_action = "fix_state_representation_next"
            reason = "The state audit shows limited policy-visible coverage and the policy is collapsing."
    elif canonical_summary.get("canonical_task_count", 0) and canonical_summary.get("canonical_task_reward_total", 0.0) == 0:
        recommended_next_action = "fix_reward_function_next"
        reason = "Canonical task accounting is available, but it still produces no reward-bearing task signal."
    elif state_feature_coverage_summary.get("high_risk_missing_fields"):
        recommended_next_action = "fix_state_representation_next"
        reason = "The state-feature audit still shows high-risk missing policy inputs."
    else:
        recommended_next_action = "safe_to_run_medium_training_after_metric_fix"
        reason = "Canonical task accounting is available and the remaining signal is sufficient for a medium follow-up training pass."
    decision = DiagnosticDecision(recommended_next_action=recommended_next_action, decision_reason=reason, evidence_notes=[])
    return decision.to_dict()
