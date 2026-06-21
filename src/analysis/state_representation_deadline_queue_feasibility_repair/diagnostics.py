from __future__ import annotations

from pathlib import Path
import json
import subprocess
from typing import Any

from .config import ALLOWED_DIAGNOSTIC_DECISIONS, ALLOWED_FINAL_VERDICTS, FEATURE_ID
from .model import ClaimSafetyStatus, DiagnosticDecision

FEATURE_070_REPORT = Path(
    "artifacts/analysis/calibration-metric-consistency-reconciliation-fix/calibration-metric-consistency-report.json"
)

APPROVED_PREFIXES = (
    "artifacts/analysis/state-representation-deadline-queue-feasibility-repair/",
    "docs/architecture/euls_phase30_state_representation_deadline_queue_feasibility_repair.md",
    "specs/071-state-representation-deadline-queue-feasibility-repair/",
    "src/analysis/state_representation_deadline_queue_feasibility_repair/",
    "tests/unit/test_state_representation_deadline_queue_feasibility_repair",
    "tests/integration/test_state_representation_deadline_queue_feasibility_repair",
    "src/analysis/full_training_reproduction_campaign/replay.py",
    "src/analysis/full_training_reproduction_campaign/trainer.py",
    "src/analysis/full_training_reproduction_campaign/config.py",
)

FORBIDDEN_PREFIXES = (
    "src/environment/reward_timing.py",
    "src/dal/",
    "src/policies/",
    "src/environment/replay_hash.py",
    "requirements",
    "pyproject.toml",
    "poetry.lock",
    "uv.lock",
    "AGENTS.md",
    ".specify/feature.json",
    "artifacts/analysis/full-paper-default-training-campaign-execution/",
    "artifacts/analysis/unified-campaign-result-analysis-figures-findings/",
    "artifacts/analysis/staged-training-budget-learning-curve/",
    "artifacts/analysis/final-review-release-gate-batch/",
    "artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic/",
    "artifacts/analysis/reward-emission-evaluation-metric-aggregation-repair/",
    "artifacts/analysis/terminal-lifecycle-accounting-50-100-comparison/",
    "artifacts/analysis/completion-path-deadline-feasibility-repair/",
    "artifacts/analysis/deadline-timeout-feasible-workload-calibration/",
    "artifacts/analysis/calibration-metric-consistency-reconciliation-fix/",
)


def _git_output(*args: str) -> str:
    result = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    return result.stdout.rstrip("\n")


def git_status_paths() -> list[str]:
    return [line[3:].strip() for line in _git_output("status", "--short", "--untracked-files=no").splitlines() if line.strip()]


def git_staged_paths() -> list[str]:
    return [line.strip() for line in _git_output("diff", "--cached", "--name-only").splitlines() if line.strip()]


def git_diff_paths(base_ref: str) -> list[str]:
    return [line.strip() for line in _git_output("diff", "--name-only", f"{base_ref}...HEAD").splitlines() if line.strip()]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_feature_070_status() -> dict[str, Any]:
    status = {"path": str(FEATURE_070_REPORT), "exists": FEATURE_070_REPORT.exists(), "verified": False, "details": ""}
    if not status["exists"]:
        status["details"] = "Feature 070 report missing"
        return status
    try:
        payload = _load_json(FEATURE_070_REPORT)
    except Exception as exc:  # pragma: no cover - defensive
        status["details"] = f"unreadable report: {exc}"
        return status
    verified = (
        payload.get("feature_id") == "070-calibration-metric-consistency-reconciliation-fix"
        and payload.get("final_verdict") == "calibration_metric_consistency_reconciliation_ready"
        and payload.get("claim_safety_status", {}).get("claim_safety_passed") is True
        and payload.get("before_after_consistency_comparison", {}).get("after", {}).get("reward_reconciled") is True
        and payload.get("before_after_consistency_comparison", {}).get("after", {}).get("terminal_reconciled") is True
    )
    status["verified"] = verified
    status["details"] = "Feature 070 report validated" if verified else "Feature 070 report failed validation"
    return status


def build_prerequisite_artifacts() -> dict[str, dict[str, Any]]:
    return {"feature_070_report": load_feature_070_status()}


def build_prerequisite_tags(
    working_tree_paths_approved: bool,
    staged_paths_approved: bool,
    base_branch_diff_approved: bool,
) -> list[dict[str, Any]]:
    branch = _git_output("branch", "--show-current")
    return [
        {"name": "branch", "verified": branch == "071-state-representation-deadline-queue-feasibility-repair", "details": "current branch matches Feature 071"},
        {"name": "feature_070_report_valid", "verified": load_feature_070_status()["verified"], "details": "Feature 070 report validated"},
        {"name": "working_tree_paths_approved", "verified": working_tree_paths_approved, "details": "working tree stays within the approved scope"},
        {"name": "staged_paths_approved", "verified": staged_paths_approved, "details": "staged paths stay within the approved scope"},
        {"name": "base_branch_diff_approved", "verified": base_branch_diff_approved, "details": "branch diff stays within the approved scope"},
    ]


def build_scope_guard_summary(
    working_tree_paths: list[str],
    staged_paths: list[str],
    diff_paths: list[str],
) -> dict[str, Any]:
    def _is_allowed(path: str) -> bool:
        return any(path.startswith(prefix) for prefix in APPROVED_PREFIXES)

    def _is_forbidden(path: str) -> bool:
        return any(path.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)

    return {
        "working_tree_paths_approved": all(_is_allowed(path) and not _is_forbidden(path) for path in working_tree_paths),
        "staged_paths_approved": all(_is_allowed(path) and not _is_forbidden(path) for path in staged_paths),
        "base_branch_head_diff_approved": all(_is_allowed(path) and not _is_forbidden(path) for path in diff_paths),
        "working_tree_paths": list(working_tree_paths),
        "staged_paths": list(staged_paths),
        "diff_paths": list(diff_paths),
        "approved_prefixes": list(APPROVED_PREFIXES),
        "forbidden_prefixes": list(FORBIDDEN_PREFIXES),
    }


def build_claim_safety_status() -> dict[str, Any]:
    return ClaimSafetyStatus(
        paper_reproduction_claim_made=False,
        performance_superiority_claim_made=False,
        baseline_superiority_claim_made=False,
        claim_safety_passed=True,
    ).to_dict()


def build_diagnostic_decision(
    *,
    state_dim_match: bool,
    no_nan_or_inf: bool,
    state_feature_coverage_complete: bool,
    reward_reconciliation_passed: bool,
    terminal_reconciliation_passed: bool,
    completion_count_nonzero: bool,
    fixed_policy_completion_present: bool,
    action_collapse_reduced: bool,
    selected_action_feasibility_improved: bool,
    queue_feature_coverage_complete: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    if not state_dim_match:
        blockers.append("state_dim_mismatch")
    if not no_nan_or_inf:
        blockers.append("state_nan_or_inf_detected")
    if not state_feature_coverage_complete:
        blockers.append("state_feature_coverage_incomplete")
    if not queue_feature_coverage_complete:
        blockers.append("state_feature_coverage_incomplete")
    if not reward_reconciliation_passed:
        blockers.append("reward_reconciliation_failed")
    if not terminal_reconciliation_passed:
        blockers.append("terminal_reconciliation_failed")
    if not completion_count_nonzero:
        blockers.append("completion_count_zero")
    if not fixed_policy_completion_present:
        blockers.append("completion_count_zero")
    if blockers:
        decision = DiagnosticDecision(
            recommended_next_action="blocked_due_to_state_profile_failure",
            decision_reason="The repaired state profile failed one or more required consistency checks.",
            evidence_notes=sorted(set(blockers)),
        )
        return decision.to_dict()

    if not state_feature_coverage_complete:
        decision = DiagnosticDecision(
            recommended_next_action="fix_state_feature_coverage_next",
            decision_reason="The state vector is valid, but required feature coverage is still incomplete.",
            evidence_notes=["state_feature_coverage_incomplete"],
        )
        return decision.to_dict()

    if not queue_feature_coverage_complete:
        decision = DiagnosticDecision(
            recommended_next_action="fix_queue_feature_coverage_next",
            decision_reason="The state vector is valid, but queue/path pressure coverage remains incomplete.",
            evidence_notes=["queue_feature_coverage_incomplete"],
        )
        return decision.to_dict()

    if not selected_action_feasibility_improved:
        decision = DiagnosticDecision(
            recommended_next_action="fix_action_feasibility_feature_next",
            decision_reason="The new profile is valid, but selected-action feasibility did not improve.",
            evidence_notes=["selected_action_feasibility_not_improved"],
        )
        return decision.to_dict()

    if not action_collapse_reduced:
        decision = DiagnosticDecision(
            recommended_next_action="fix_policy_exploration_next",
            decision_reason="The new profile is valid, but candidate action collapse remains strong.",
            evidence_notes=["policy_collapse_persists"],
        )
        return decision.to_dict()

    decision = DiagnosticDecision(
        recommended_next_action="safe_to_proceed_to_reward_function_alignment",
        decision_reason="The repaired state profile is consistent and exposes deadline, queue, and feasibility signals.",
        evidence_notes=["state_profile_passed", "state_coverage_complete"],
    )
    return decision.to_dict()


def build_prerequisite_verdict(feature_070_verified: bool) -> tuple[bool, str]:
    if not feature_070_verified:
        return False, "feature_070_prerequisite_blocked"
    return True, "ok"
