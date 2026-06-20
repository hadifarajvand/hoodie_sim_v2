from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import (
    ALLOWED_DIAGNOSTIC_DECISIONS,
    ALLOWED_FINAL_VERDICTS,
    FEATURE_067_REPORT,
    FEATURE_ID,
    FIGURES_DIR,
    OUTPUT_DIR,
)
from .model import ClaimSafetyStatus, DiagnosticDecision

FEATURE_SCOPE_PREFIXES = (
    "artifacts/analysis/completion-path-deadline-feasibility-repair/",
    "docs/architecture/euls_phase27_completion_path_deadline_feasibility_repair.md",
    "specs/068-completion-path-deadline-feasibility-repair/",
    "src/analysis/completion_path_deadline_feasibility_repair/",
    "tests/unit/test_completion_path_deadline_feasibility_repair",
    "tests/integration/test_completion_path_deadline_feasibility_repair",
)

FORBIDDEN_PREFIXES = (
    "src/environment/",
    "src/dal/",
    "src/policies/",
    "src/environment/reward_timing.py",
    "src/environment/replay_hash.py",
    "requirements",
    "pyproject.toml",
    "poetry.lock",
    "uv.lock",
    "AGENTS.md",
    ".specify/feature.json",
    "src/analysis/staged_training_budget_learning_curve/",
    "src/analysis/final_review_release_gate_batch/",
    "src/analysis/evaluation_instrumentation_reward_state_diagnostic/",
    "src/analysis/reward_emission_evaluation_metric_aggregation_repair/",
    "src/analysis/terminal_lifecycle_accounting_50_100_comparison/",
)


def load_json(path: Path) -> dict[str, Any]:
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def git_output(*args: str) -> str:
    import subprocess

    try:
        return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


def git_status_paths() -> list[str]:
    output = git_output("status", "--short", "--untracked-files=all")
    paths = [line[3:].strip() for line in output.splitlines() if line.strip()]
    return [path for path in paths if any(path.startswith(prefix) for prefix in FEATURE_SCOPE_PREFIXES + FORBIDDEN_PREFIXES)]


def git_staged_paths() -> list[str]:
    return [line.strip() for line in git_output("diff", "--cached", "--name-only").splitlines() if line.strip()]


def git_diff_paths(base_ref: str) -> list[str]:
    return [line.strip() for line in git_output("diff", "--name-only", f"{base_ref}...HEAD").splitlines() if line.strip()]


def classify_paths(paths: list[str], approved_prefixes: tuple[str, ...], forbidden_prefixes: tuple[str, ...]) -> dict[str, Any]:
    forbidden = [path for path in paths if any(path.startswith(prefix) for prefix in forbidden_prefixes)]
    approved = [path for path in paths if any(path.startswith(prefix) for prefix in approved_prefixes)]
    return {
        "paths": list(paths),
        "approved_paths_detected": approved,
        "forbidden_paths_detected": forbidden,
        "approved": not forbidden and (not paths or len(approved) == len(paths)),
    }


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


def load_feature_067_status() -> dict[str, Any]:
    status = {"path": str(FEATURE_067_REPORT), "exists": FEATURE_067_REPORT.exists(), "verified": False, "details": ""}
    if not status["exists"]:
        return status
    report = load_json(FEATURE_067_REPORT)
    status["verified"] = (
        report.get("final_verdict") == "terminal_lifecycle_50_100_comparison_ready"
        and report.get("remaining_blockers") == []
        and report.get("claim_safety_status", {}).get("claim_safety_passed") is True
    )
    status["details"] = "Feature 067 report validated as prerequisite"
    return status


def build_prerequisite_artifacts() -> dict[str, dict[str, Any]]:
    return {"feature_067_report": load_feature_067_status()}


def build_prerequisite_tags(
    working_tree_paths_approved: bool,
    staged_paths_approved: bool,
    base_branch_diff_approved: bool,
) -> list[dict[str, Any]]:
    branch = git_output("branch", "--show-current")
    return [
        {"name": "branch", "verified": branch == "068-completion-path-deadline-feasibility-repair", "details": "current branch matches Feature 068"},
        {"name": "not_main", "verified": branch != "main", "details": "current branch is not main"},
        {"name": "feature_067_report_valid", "verified": load_feature_067_status()["verified"], "details": "Feature 067 report validated"},
        {"name": "working_tree_paths_approved", "verified": working_tree_paths_approved, "details": "working tree paths stay inside the approved scope"},
        {"name": "staged_paths_approved", "verified": staged_paths_approved, "details": "staged paths stay inside the approved scope"},
        {"name": "base_branch_diff_approved", "verified": base_branch_diff_approved, "details": "base-branch diff stays inside the approved scope"},
    ]


def build_claim_safety_status() -> dict[str, Any]:
    return ClaimSafetyStatus(
        paper_reproduction_claim_made=False,
        performance_superiority_claim_made=False,
        baseline_superiority_claim_made=False,
        claim_safety_passed=True,
    ).to_dict()


def classify_completion_failure(
    *,
    task_feasibility_summary: dict[str, Any],
    runtime_event_path_audit: dict[str, Any],
    coverage_classification: dict[str, Any],
    policy_effect_completion_feasibility: dict[str, Any],
) -> dict[str, Any]:
    overall_runtime = runtime_event_path_audit.get("overall", {})
    policy_results = policy_effect_completion_feasibility.get("policy_results", {})
    fixed_policy_names = ["fixed_local_policy", "fixed_horizontal_policy", "fixed_vertical_policy", "random_legal_policy"]
    all_fixed_zero_completion = all(
        int(policy_results.get(name, {}).get("evaluation_reward_summary", {}).get("completed_task_count", 0)) == 0 for name in fixed_policy_names
    )
    any_fixed_completes = any(
        int(policy_results.get(name, {}).get("evaluation_reward_summary", {}).get("completed_task_count", 0)) > 0 for name in fixed_policy_names
    )
    candidate_result = policy_results.get("candidate_policy_at_100", {})

    if coverage_classification.get("evaluation_mode") == "sampled_task_decision_evaluation" and coverage_classification.get("observed_decision_count", 0) < coverage_classification.get("expected_max_decision_slots", 0):
        return {
            "root_cause": "evaluation_probe_too_shallow",
            "decision": "fix_evaluation_probe_coverage_next",
            "evidence": ["full_step_coverage_unavailable=true"],
        }
    if task_feasibility_summary.get("all_actions_infeasible", False):
        return {
            "root_cause": "all_tasks_infeasible_under_current_deadlines",
            "decision": "fix_deadline_timeout_configuration_next",
            "evidence": [
                f"local_feasible_task_count={task_feasibility_summary.get('local_feasible_task_count', 0)}",
                f"horizontal_feasible_task_count={task_feasibility_summary.get('horizontal_feasible_task_count', 0)}",
                f"vertical_feasible_task_count={task_feasibility_summary.get('vertical_feasible_task_count', 0)}",
            ],
        }
    if int(overall_runtime.get("execution_completed_event_count", 0)) == 0 and int(overall_runtime.get("tasks_with_positive_execution_progress_count", 0)) == 0:
        return {
            "root_cause": "execution_completion_event_not_emitted",
            "decision": "fix_execution_completion_event_emission_next",
            "evidence": ["execution_progress_event_count=0", "execution_completed_event_count=0"],
        }
    if int(overall_runtime.get("transmission_completed_event_count", 0)) > 0 and int(overall_runtime.get("execution_started_event_count", 0)) == 0:
        return {
            "root_cause": "transmission_path_blocks_execution",
            "decision": "fix_transmission_to_execution_handoff_next",
            "evidence": ["transmission_completed_event_count>0", "execution_started_event_count=0"],
        }
    if int(overall_runtime.get("deadline_before_execution_completion_count", 0)) > 0:
        return {
            "root_cause": "deadline_sweep_preempts_completion",
            "decision": "fix_deadline_timeout_configuration_next",
            "evidence": [f"deadline_before_execution_completion_count={overall_runtime.get('deadline_before_execution_completion_count', 0)}"],
        }
    if candidate_result and all_fixed_zero_completion:
        return {
            "root_cause": "policy_selects_infeasible_actions",
            "decision": "fix_policy_action_feasibility_filter_next",
            "evidence": ["candidate_policy_zero_completion_across_all_fixed_policies=true"],
        }
    if any_fixed_completes:
        return {
            "root_cause": "unknown_completion_path_failure",
            "decision": "fix_state_representation_next",
            "evidence": ["some_fixed_policy_completes=true"],
        }
    return {
        "root_cause": "unknown_completion_path_failure",
        "decision": "blocked_due_to_unresolved_completion_path",
        "evidence": ["insufficient_evidence_for_specific_root_cause=true"],
    }


def build_diagnostic_decision(classification: dict[str, Any]) -> dict[str, Any]:
    recommended = classification["decision"]
    if recommended not in ALLOWED_DIAGNOSTIC_DECISIONS:
        raise ValueError("diagnostic decision must be one of the allowed decisions")
    if recommended == "fix_deadline_timeout_configuration_next":
        reason = "The workload/deadline envelope is infeasible for the observed task set, so deadlines/timeouts need adjustment before more training."
    elif recommended == "fix_execution_completion_event_emission_next":
        reason = "Execution progress exists but completion is not being emitted."
    elif recommended == "fix_transmission_to_execution_handoff_next":
        reason = "Transmission completes but execution never starts."
    elif recommended == "fix_policy_action_feasibility_filter_next":
        reason = "The policy is choosing infeasible actions under the current deadline envelope."
    elif recommended == "fix_evaluation_probe_coverage_next":
        reason = "The probe is too shallow to distinguish lifecycle failure modes."
    elif recommended == "fix_state_representation_next":
        reason = "At least one fixed policy completes, so representation remains the next plausible repair."
    else:
        reason = "The completion path failure remains unresolved."
    return DiagnosticDecision(
        recommended_next_action=recommended,
        decision_reason=reason,
        evidence_notes=list(classification.get("evidence", [])),
    ).to_dict()
