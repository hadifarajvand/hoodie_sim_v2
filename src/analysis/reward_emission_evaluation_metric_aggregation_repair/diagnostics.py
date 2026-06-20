from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import FEATURE_065_REPORT
from .model import ClaimSafetyStatus, DiagnosticDecision

FEATURE_SCOPE_PREFIXES = (
    "artifacts/analysis/reward-emission-evaluation-metric-aggregation-repair/",
    "docs/architecture/euls_phase25_reward_emission_evaluation_metric_aggregation_repair.md",
    "specs/066-reward-emission-evaluation-metric-aggregation-repair/",
    "src/analysis/reward_emission_evaluation_metric_aggregation_repair/",
    "tests/unit/test_reward_emission_evaluation_metric_aggregation_repair",
    "tests/integration/test_reward_emission_evaluation_metric_aggregation_repair",
    "src/environment/",
    "src/dal/",
    "src/policies/",
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


def load_feature_065_status() -> dict[str, Any]:
    status = {"path": str(FEATURE_065_REPORT), "exists": FEATURE_065_REPORT.exists(), "verified": False, "details": ""}
    if not status["exists"]:
        return status
    report = load_json(FEATURE_065_REPORT)
    status["verified"] = (
        report.get("final_verdict") == "evaluation_instrumentation_diagnostic_ready"
        and report.get("remaining_blockers") == []
        and report.get("claim_safety_status", {}).get("claim_safety_passed") is True
    )
    status["details"] = "Feature 065 diagnostic report validated as prerequisite"
    return status


def build_prerequisite_artifacts() -> dict[str, dict[str, Any]]:
    return {
        "feature_065_report": load_feature_065_status(),
    }


def build_prerequisite_tags(
    working_tree_paths_approved: bool,
    staged_paths_approved: bool,
    base_branch_diff_approved: bool,
) -> list[dict[str, Any]]:
    branch = git_output("branch", "--show-current")
    return [
        {"name": "branch", "verified": branch == "066-reward-emission-evaluation-metric-aggregation-repair", "details": "current branch matches Feature 066"},
        {"name": "not_main", "verified": branch != "main", "details": "current branch is not main"},
        {"name": "feature_065_report_valid", "verified": load_feature_065_status()["verified"], "details": "Feature 065 report validated"},
        {"name": "working_tree_paths_approved", "verified": working_tree_paths_approved, "details": "working tree paths stay inside the approved scope"},
        {"name": "staged_paths_approved", "verified": staged_paths_approved, "details": "staged paths stay inside the approved scope"},
        {"name": "base_branch_head_diff_approved", "verified": base_branch_diff_approved, "details": "base-branch diff stays inside the approved scope"},
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
    raw_reward_event_recovery_blocked: bool,
    terminal_event_recovery_blocked: bool,
    reward_reconciled: bool,
    candidate_policy_vertical_collapse_in_evaluation: bool,
    candidate_policy_vertical_collapse_in_training_replay_window: bool,
    policy_affects_reward: str,
    policy_affects_terminal_outcomes: str,
) -> dict[str, Any]:
    if raw_reward_event_recovery_blocked:
        decision = DiagnosticDecision(
            recommended_next_action="blocked_due_to_unresolved_reward_event_recovery",
            decision_reason="Raw reward events are still not recovered from evaluation stepping evidence, so the pipeline remains blocked.",
            evidence_notes=["raw_reward_event_recovery_blocked=true"],
        )
    elif not reward_reconciled:
        decision = DiagnosticDecision(
            recommended_next_action="fix_environment_lifecycle_accounting_next",
            decision_reason="Raw and canonical reward totals do not reconcile, so lifecycle accounting still needs repair.",
            evidence_notes=["raw_vs_canonical_reward_delta!=0"],
        )
    elif candidate_policy_vertical_collapse_in_evaluation or candidate_policy_vertical_collapse_in_training_replay_window:
        if policy_affects_reward == "false" and policy_affects_terminal_outcomes == "false":
            decision = DiagnosticDecision(
                recommended_next_action="fix_state_representation_next",
                decision_reason="The candidate policy still collapses toward vertical while policy choice does not move reward or terminal outcomes.",
                evidence_notes=["vertical_collapse=true"],
            )
        else:
            decision = DiagnosticDecision(
                recommended_next_action="fix_reward_function_next",
                decision_reason="The policy collapses and the reward signal still does not separate outcomes cleanly enough for the thesis pipeline.",
                evidence_notes=["vertical_collapse=true", "policy_affects_reward!=false"],
            )
    elif terminal_event_recovery_blocked:
        decision = DiagnosticDecision(
            recommended_next_action="blocked_due_to_unresolved_reward_event_recovery",
            decision_reason="Terminal lifecycle events are still not fully recovered alongside reward emission evidence.",
            evidence_notes=["terminal_event_recovery_blocked=true"],
        )
    else:
        decision = DiagnosticDecision(
            recommended_next_action="safe_to_proceed_to_state_reward_alignment",
            decision_reason="Raw reward events and canonical task metrics reconcile, and the remaining diagnostic path can move to state/reward alignment.",
            evidence_notes=["reward_reconciled=true"],
        )
    return decision.to_dict()
