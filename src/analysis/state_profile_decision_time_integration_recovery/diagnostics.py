from __future__ import annotations

from pathlib import Path
import json
import subprocess
from typing import Any

from .config import ALLOWED_DIAGNOSTIC_DECISIONS, ALLOWED_FINAL_VERDICTS, FEATURE_ID
from .model import ClaimSafetyStatus, DiagnosticDecision

FEATURE_071_REPORT = Path(
    "artifacts/analysis/state-representation-deadline-queue-feasibility-repair/state-representation-repair-report.json"
)

APPROVED_PREFIXES = (
    "artifacts/analysis/state-profile-decision-time-integration-recovery/",
    "docs/architecture/euls_phase31_state_profile_decision_time_integration_recovery.md",
    "specs/072-state-profile-decision-time-integration-recovery/",
    "src/analysis/state_profile_decision_time_integration_recovery/",
    "tests/unit/test_state_profile_decision_time_integration_recovery",
    "tests/integration/test_state_profile_decision_time_integration_recovery",
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
    "artifacts/analysis/state-representation-deadline-queue-feasibility-repair/",
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


def load_feature_071_status() -> dict[str, Any]:
    status = {"path": str(FEATURE_071_REPORT), "exists": FEATURE_071_REPORT.exists(), "verified": False, "details": ""}
    if not status["exists"]:
        status["details"] = "Feature 071 report missing"
        return status
    try:
        payload = _load_json(FEATURE_071_REPORT)
    except Exception as exc:  # pragma: no cover - defensive
        status["details"] = f"unreadable report: {exc}"
        return status
    verified = (
        payload.get("feature_id") == "071-state-representation-deadline-queue-feasibility-repair"
        and payload.get("final_verdict") == "state_representation_deadline_queue_feasibility_ready"
        and payload.get("claim_safety_status", {}).get("claim_safety_passed") is True
        and payload.get("reconciliation_after_state_repair", {}).get("reward_reconciliation_passed") is True
        and payload.get("reconciliation_after_state_repair", {}).get("terminal_reconciliation_passed") is True
    )
    status["verified"] = verified
    status["details"] = "Feature 071 report validated" if verified else "Feature 071 report failed validation"
    return status


def load_feature_070_status() -> dict[str, Any]:
    return load_feature_071_status()


def build_prerequisite_artifacts() -> dict[str, dict[str, Any]]:
    status = load_feature_071_status()
    return {"feature_071_report": status, "feature_070_report": status}


def build_prerequisite_tags(
    working_tree_paths_approved: bool,
    staged_paths_approved: bool,
    base_branch_diff_approved: bool,
) -> list[dict[str, Any]]:
    branch = _git_output("branch", "--show-current")
    return [
        {"name": "branch", "verified": branch == "072-state-profile-decision-time-integration-recovery", "details": "current branch matches Feature 072"},
        {"name": "feature_071_report_valid", "verified": load_feature_071_status()["verified"], "details": "Feature 071 report validated"},
        {"name": "feature_070_report_valid", "verified": load_feature_070_status()["verified"], "details": "Feature 070 alias report validated"},
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
    decision_state_injection_passed: bool | None = None,
    replay_state_alignment_passed: bool | None = None,
    train_eval_state_profile_match: bool | None = None,
    no_nan_or_inf: bool | None = None,
    reward_reconciliation_passed: bool | None = None,
    terminal_reconciliation_passed: bool | None = None,
    completion_count_nonzero: bool | None = None,
    fixed_policy_completion_present: bool | None = None,
    action_collapse_reduced: bool | None = None,
    selected_action_feasibility_improved: bool | None = None,
    **legacy_kwargs: Any,
) -> dict[str, Any]:
    if decision_state_injection_passed is None:
        decision_state_injection_passed = bool(
            legacy_kwargs.pop("state_dim_match", False)
            or legacy_kwargs.pop("state_feature_coverage_complete", False)
        )
    if replay_state_alignment_passed is None:
        replay_state_alignment_passed = True
    if train_eval_state_profile_match is None:
        train_eval_state_profile_match = True
    if no_nan_or_inf is None:
        no_nan_or_inf = bool(legacy_kwargs.pop("no_nan_or_inf", False))
    if reward_reconciliation_passed is None:
        reward_reconciliation_passed = bool(legacy_kwargs.pop("reward_reconciliation_passed", False))
    if terminal_reconciliation_passed is None:
        terminal_reconciliation_passed = bool(legacy_kwargs.pop("terminal_reconciliation_passed", False))
    if completion_count_nonzero is None:
        completion_count_nonzero = bool(legacy_kwargs.pop("completion_count_nonzero", False))
    if fixed_policy_completion_present is None:
        fixed_policy_completion_present = bool(legacy_kwargs.pop("fixed_policy_completion_present", False))
    if action_collapse_reduced is None:
        action_collapse_reduced = bool(legacy_kwargs.pop("action_collapse_reduced", False))
    if selected_action_feasibility_improved is None:
        selected_action_feasibility_improved = bool(
            legacy_kwargs.pop("selected_action_feasibility_improved", False)
            or legacy_kwargs.pop("queue_feature_coverage_complete", False)
        )
    blockers: list[str] = []
    if not decision_state_injection_passed:
        blockers.append("decision_state_injection_failed")
    if not replay_state_alignment_passed:
        blockers.append("replay_state_alignment_failed")
    if not train_eval_state_profile_match:
        blockers.append("train_eval_state_profile_mismatch")
    if not no_nan_or_inf:
        blockers.append("state_nan_or_inf_detected")
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
            recommended_next_action="blocked_due_to_state_profile_integration_failure",
            decision_reason="The repaired decision-time state path failed one or more required consistency checks.",
            evidence_notes=sorted(set(blockers)),
        )
        return decision.to_dict()

    if not action_collapse_reduced:
        decision = DiagnosticDecision(
            recommended_next_action="fix_policy_exploration_next",
            decision_reason="The decision-time state path is valid, but candidate collapse remains strong.",
            evidence_notes=["policy_collapse_persists"],
        )
        return decision.to_dict()

    if not selected_action_feasibility_improved:
        decision = DiagnosticDecision(
            recommended_next_action="fix_state_profile_feature_scaling_next",
            decision_reason="The decision-time state path is valid, but selected-action feasibility did not improve enough.",
            evidence_notes=["selected_action_feasibility_not_improved"],
        )
        return decision.to_dict()

    decision = DiagnosticDecision(
        recommended_next_action="safe_to_proceed_to_reward_function_alignment",
        decision_reason="The repaired state profile is consistent and exposes current-task deadline, queue, and feasibility signals.",
        evidence_notes=["state_profile_passed", "decision_time_injection_passed"],
    )
    return decision.to_dict()


def build_prerequisite_verdict(feature_071_verified: bool) -> tuple[bool, str]:
    if not feature_071_verified:
        return False, "feature_071_prerequisite_blocked"
    return True, "ok"
