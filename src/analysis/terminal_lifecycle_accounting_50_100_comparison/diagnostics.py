from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import FEATURE_066_REPORT, FEATURE_ID
from .model import ClaimSafetyStatus, DiagnosticDecision

FEATURE_SCOPE_PREFIXES = (
    "artifacts/analysis/terminal-lifecycle-accounting-50-100-comparison/",
    "docs/architecture/euls_phase26_terminal_lifecycle_accounting_50_100_comparison.md",
    "specs/067-terminal-lifecycle-accounting-50-100-comparison/",
    "src/analysis/terminal_lifecycle_accounting_50_100_comparison/",
    "tests/unit/test_terminal_lifecycle_accounting_50_100_comparison",
    "tests/integration/test_terminal_lifecycle_accounting_50_100_comparison",
)

FORBIDDEN_PREFIXES = (
    "src/environment/",
    "src/dal/",
    "src/policies/",
    "src/environment/reward_timing.py",
    "src/environment/replay_hash.py",
    "src/analysis/staged_training_budget_learning_curve/",
    "src/analysis/final_review_release_gate_batch/",
    "src/analysis/evaluation_instrumentation_reward_state_diagnostic/",
    "src/analysis/reward_emission_evaluation_metric_aggregation_repair/",
    "requirements",
    "pyproject.toml",
    "poetry.lock",
    "uv.lock",
    "AGENTS.md",
    ".specify/feature.json",
)


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
    paths = [line[3:].strip() for line in output.splitlines() if line.strip()]
    return [path for path in paths if any(path.startswith(prefix) for prefix in FEATURE_SCOPE_PREFIXES)]


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


def load_feature_066_status() -> dict[str, Any]:
    status = {"path": str(FEATURE_066_REPORT), "exists": FEATURE_066_REPORT.exists(), "verified": False, "details": ""}
    if not status["exists"]:
        return status
    report = load_json(FEATURE_066_REPORT)
    status["verified"] = (
        report.get("final_verdict") == "reward_emission_aggregation_repair_ready"
        and report.get("remaining_blockers") == []
        and report.get("claim_safety_status", {}).get("claim_safety_passed") is True
    )
    status["details"] = "Feature 066 repair report validated as prerequisite"
    return status


def build_prerequisite_artifacts() -> dict[str, dict[str, Any]]:
    return {"feature_066_report": load_feature_066_status()}


def build_prerequisite_tags(
    working_tree_paths_approved: bool,
    staged_paths_approved: bool,
    base_branch_diff_approved: bool,
) -> list[dict[str, Any]]:
    branch = git_output("branch", "--show-current")
    return [
        {"name": "branch", "verified": branch == "067-terminal-lifecycle-accounting-50-100-comparison", "details": "current branch matches Feature 067"},
        {"name": "not_main", "verified": branch != "main", "details": "current branch is not main"},
        {"name": "feature_066_report_valid", "verified": load_feature_066_status()["verified"], "details": "Feature 066 report validated"},
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


def build_diagnostic_decision(
    *,
    terminal_reconciliation_failed: bool,
    reward_reconciliation_failed: bool,
    candidate_policy_vertical_collapse_in_evaluation: bool,
    candidate_policy_vertical_collapse_in_training_replay_window: bool,
    all_fixed_policies_zero_completion: bool,
    any_fixed_policy_completes: bool,
    terminal_event_coverage_ratio: float,
    policy_affects_reward: str,
    policy_affects_terminal_outcomes: str,
) -> dict[str, Any]:
    if terminal_reconciliation_failed and terminal_event_coverage_ratio > 1.05:
        decision = DiagnosticDecision(
            recommended_next_action="fix_environment_lifecycle_accounting_next",
            decision_reason="Terminal lifecycle accounting still over-counts raw events relative to canonical tasks.",
            evidence_notes=["terminal_event_coverage_ratio>1.05"],
        )
    elif terminal_reconciliation_failed:
        decision = DiagnosticDecision(
            recommended_next_action="blocked_due_to_unresolved_terminal_reconciliation",
            decision_reason="Terminal lifecycle reconciliation still fails, so the repaired comparison cannot be trusted.",
            evidence_notes=["terminal_reconciliation_failed=true"],
        )
    elif reward_reconciliation_failed:
        decision = DiagnosticDecision(
            recommended_next_action="fix_reward_function_next",
            decision_reason="Reward totals still do not reconcile after terminal repair.",
            evidence_notes=["reward_reconciliation_failed=true"],
        )
    elif candidate_policy_vertical_collapse_in_evaluation or candidate_policy_vertical_collapse_in_training_replay_window:
        if all_fixed_policies_zero_completion:
            decision = DiagnosticDecision(
                recommended_next_action="fix_completion_path_next",
                decision_reason="All examined policies still fail to complete tasks, so the completion path remains the next diagnostic target.",
                evidence_notes=["zero_completion_across_policies=true"],
            )
        elif any_fixed_policy_completes:
            decision = DiagnosticDecision(
                recommended_next_action="fix_state_representation_next",
                decision_reason="At least one fixed policy completes tasks, which points the next repair at state representation rather than the environment path.",
                evidence_notes=["some_fixed_policy_completes=true"],
            )
        elif policy_affects_reward == "false" and policy_affects_terminal_outcomes == "false":
            decision = DiagnosticDecision(
                recommended_next_action="fix_state_representation_next",
                decision_reason="Policy choice does not move reward or terminal outcomes, which points away from training and toward representation.",
                evidence_notes=["policy_effect_static=true"],
            )
        else:
            decision = DiagnosticDecision(
                recommended_next_action="fix_reward_function_next",
                decision_reason="The candidate still collapses vertically and the outcome signal is not separating cleanly.",
                evidence_notes=["vertical_collapse=true"],
            )
    else:
        decision = DiagnosticDecision(
            recommended_next_action="safe_to_proceed_to_state_representation_repair",
            decision_reason="Terminal and reward reconciliation pass, and the remaining diagnostic work can move to state-representation repair.",
            evidence_notes=["terminal_and_reward_reconciled=true"],
        )
    return decision.to_dict()
