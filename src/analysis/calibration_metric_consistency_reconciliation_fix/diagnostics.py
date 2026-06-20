from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import BASE_BRANCH_NAME, FEATURE_ID, REPORT_JSON
from .model import ClaimSafetyStatus, DiagnosticDecision

APPROVED_PREFIXES = (
    "artifacts/analysis/calibration-metric-consistency-reconciliation-fix/",
    "docs/architecture/euls_phase29_calibration_metric_consistency_reconciliation_fix.md",
    "specs/070-calibration-metric-consistency-reconciliation-fix/",
    "src/analysis/calibration_metric_consistency_reconciliation_fix/",
    "tests/unit/test_calibration_metric_consistency_reconciliation_fix",
    "tests/integration/test_calibration_metric_consistency_reconciliation_fix",
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
    "artifacts/analysis/deadline-timeout-feasible-workload-calibration/",
    "src/analysis/deadline_timeout_feasible_workload_calibration/",
    "artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic/",
    "artifacts/analysis/reward-emission-evaluation-metric-aggregation-repair/",
    "artifacts/analysis/terminal-lifecycle-accounting-50-100-comparison/",
    "artifacts/analysis/completion-path-deadline-feasibility-repair/",
)


def load_json(path: Path) -> dict[str, Any]:
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def git_output(*args: str) -> str:
    import subprocess

    try:
        return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()
    except Exception:
        return ""


def git_status_paths() -> list[str]:
    output = git_output("status", "--short", "--untracked-files=all")
    return [line[3:].strip() for line in output.splitlines() if line.strip()]


def git_staged_paths() -> list[str]:
    return [line.strip() for line in git_output("diff", "--cached", "--name-only").splitlines() if line.strip()]


def git_diff_paths(base_ref: str) -> list[str]:
    return [line.strip() for line in git_output("diff", "--name-only", f"{base_ref}...HEAD").splitlines() if line.strip()]


def classify_paths(paths: list[str], approved_prefixes: tuple[str, ...], forbidden_prefixes: tuple[str, ...]) -> dict[str, Any]:
    relevant_paths = [
        path
        for path in paths
        if any(path.startswith(prefix) for prefix in approved_prefixes) or any(path.startswith(prefix) for prefix in forbidden_prefixes)
    ]
    forbidden = [path for path in relevant_paths if any(path.startswith(prefix) for prefix in forbidden_prefixes)]
    approved = [path for path in relevant_paths if any(path.startswith(prefix) for prefix in approved_prefixes)]
    return {"paths": list(relevant_paths), "approved_paths_detected": approved, "forbidden_paths_detected": forbidden, "approved": not forbidden}


def build_scope_guard_summary(status_paths: list[str], staged_paths: list[str], diff_paths: list[str], approved_prefixes: tuple[str, ...], forbidden_prefixes: tuple[str, ...]) -> dict[str, Any]:
    status = classify_paths(status_paths, approved_prefixes, forbidden_prefixes)
    staged = classify_paths(staged_paths, approved_prefixes, forbidden_prefixes)
    diff = classify_paths(diff_paths, approved_prefixes, forbidden_prefixes)
    return {
        "working_tree_paths_approved": status["approved"],
        "staged_paths_approved": staged["approved"],
        "base_branch_head_diff_approved": diff["approved"],
        "forbidden_paths_detected": status["forbidden_paths_detected"] + staged["forbidden_paths_detected"] + diff["forbidden_paths_detected"],
        "approved_paths_detected": status["approved_paths_detected"] + staged["approved_paths_detected"] + diff["approved_paths_detected"],
    }


def build_claim_safety_status() -> dict[str, Any]:
    return ClaimSafetyStatus(
        paper_reproduction_claim_made=False,
        performance_superiority_claim_made=False,
        baseline_superiority_claim_made=False,
        claim_safety_passed=True,
    ).to_dict()


def build_prerequisite_artifacts() -> dict[str, Any]:
    status = {"path": str(Path("artifacts/analysis/deadline-timeout-feasible-workload-calibration/deadline-timeout-calibration-report.json")), "exists": False, "verified": False, "details": ""}
    if Path(status["path"]).exists():
        status["exists"] = True
        report = load_json(Path(status["path"]))
        status["verified"] = report.get("final_verdict") == "deadline_timeout_feasible_workload_calibration_ready"
        status["details"] = "Feature 069 calibration report validated"
    return {"feature_069_report": status}


def build_prerequisite_tags(working_tree_paths_approved: bool, staged_paths_approved: bool, base_branch_diff_approved: bool) -> list[dict[str, Any]]:
    branch = git_output("branch", "--show-current")
    return [
        {"name": "branch", "verified": branch == FEATURE_ID, "details": "current branch matches Feature 070"},
        {"name": "base_branch", "verified": BASE_BRANCH_NAME == "069-deadline-timeout-feasible-workload-calibration", "details": "base branch matches Feature 069"},
        {"name": "feature_069_report_valid", "verified": build_prerequisite_artifacts()["feature_069_report"]["verified"], "details": "Feature 069 report validated"},
        {"name": "working_tree_paths_approved", "verified": working_tree_paths_approved, "details": "working tree paths stay inside the approved scope"},
        {"name": "staged_paths_approved", "verified": staged_paths_approved, "details": "staged paths stay inside the approved scope"},
        {"name": "base_branch_head_diff_approved", "verified": base_branch_diff_approved, "details": "base-branch diff stays inside the approved scope"},
    ]


def build_diagnostic_decision(
    *,
    reward_reconciliation_status: str,
    terminal_reconciled: bool,
    actions_have_different_feasibility: bool,
    completion_count_nonzero: bool,
    any_fixed_policy_completes: bool,
) -> dict[str, Any]:
    if reward_reconciliation_status != "passed" or not terminal_reconciled:
        decision = DiagnosticDecision(
            recommended_next_action="fix_reward_terminal_reconciliation_next",
            decision_reason="Reward or terminal reconciliation still fails after the consistency repair.",
            evidence_notes=["reward_terminal_reconciliation_failed"],
        )
    elif not actions_have_different_feasibility:
        decision = DiagnosticDecision(
            recommended_next_action="fix_calibration_action_path_diversity_next",
            decision_reason="Action feasibility still collapses to a single path, so the calibration needs another pass.",
            evidence_notes=["actions_have_different_feasibility=false"],
        )
    elif not completion_count_nonzero:
        decision = DiagnosticDecision(
            recommended_next_action="blocked_due_to_unresolved_consistency",
            decision_reason="Completion disappeared after consistency repair, so the metric universe is still unstable.",
            evidence_notes=["completion_count_nonzero=false"],
        )
    elif any_fixed_policy_completes:
        decision = DiagnosticDecision(
            recommended_next_action="safe_to_proceed_to_state_representation_repair",
            decision_reason="Metrics are consistent, action feasibility is diversified, and fixed policies still complete tasks.",
            evidence_notes=["consistency_passed=true"],
        )
    else:
        decision = DiagnosticDecision(
            recommended_next_action="blocked_due_to_unresolved_consistency",
            decision_reason="Fixed-policy completion disappeared after repair.",
            evidence_notes=["any_fixed_policy_completes=false"],
        )
    return decision.to_dict()
