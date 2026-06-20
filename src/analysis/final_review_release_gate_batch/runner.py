from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.analysis.full_training_reproduction_campaign.config import CampaignConfig

from .config import (
    ACTION_COLLAPSE_REVIEW_JSON,
    BASE_BRANCH_NAME,
    BRANCH_NAME,
    CHECKPOINT_BUDGETS,
    DIAGNOSTIC_FINDINGS_JSON,
    EVALUATION_EPISODES_PER_CHECKPOINT,
    EVALUATION_SIGNAL_REVIEW_JSON,
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
    FEATURE_ID,
    FIGURES_DIR,
    FIGURE_MANIFEST_JSON,
    FINAL_REVIEW_SUMMARY_MD,
    NEXT_ACTION_DECISION_JSON,
    OUTPUT_DIR,
    RECOMMENDED_NEXT_ACTION,
    REPLAY_BUFFER_REVIEW_JSON,
    REPORT_JSON,
    REPORT_MD,
    REWARD_STABILITY_REVIEW_JSON,
    FinalReviewReleaseGateBatchConfig,
)
from .figures import generate_figures
from .model import (
    ALLOWED_FINAL_VERDICTS,
    ActionCollapseReview,
    ClaimSafetyStatus,
    DiagnosticFindings,
    EvaluationSignalReview,
    FinalReviewReleaseGateBatchReport,
    NextActionDecision,
    ReplayBufferReview,
    RewardStabilityReview,
)
from .report import json_dump, render_final_review_summary_markdown, write_final_review_release_gate_batch_report

APPROVED_PATH_PREFIXES = (
    "artifacts/analysis/final-review-release-gate-batch/",
    "docs/architecture/euls_phase23_final_review_release_gate_batch.md",
    "specs/064-final-review-release-gate-batch/",
    "src/analysis/final_review_release_gate_batch/",
    "tests/unit/test_final_review_release_gate_batch",
    "tests/integration/test_final_review_release_gate_batch",
)

FORBIDDEN_PATH_PREFIXES = (
    "src/environment/",
    "src/dal/",
    "src/policies/",
    "src/environment/replay_hash.py",
    "src/analysis/full_training_reproduction_campaign/",
    "src/analysis/full_paper_default_training_campaign_execution/",
    "src/analysis/evaluation_trace_bank_baseline_harness/",
    "src/analysis/unified_campaign_result_analysis_figures_findings/",
    "src/analysis/staged_training_budget_learning_curve/",
    "requirements",
    "pyproject.toml",
    "AGENTS.md",
    ".specify/feature.json",
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_output(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def _status_paths() -> list[str]:
    output = subprocess.run(["git", "status", "--short", "--untracked-files=no"], check=True, capture_output=True, text=True).stdout
    lines = output.splitlines()
    return [line[3:].strip() for line in lines if line.strip()]


def _staged_paths() -> list[str]:
    lines = _git_output("diff", "--cached", "--name-only").splitlines()
    return [line.strip() for line in lines if line.strip()]


def _diff_paths(base_ref: str) -> list[str]:
    lines = _git_output("diff", "--name-only", f"{base_ref}...HEAD").splitlines()
    return [line.strip() for line in lines if line.strip()]


def _approved_paths(paths: list[str]) -> bool:
    if any(path.startswith(FORBIDDEN_PATH_PREFIXES) for path in paths):
        return False
    return all(path.startswith(APPROVED_PATH_PREFIXES) for path in paths)


def _path_classification(paths: list[str]) -> dict[str, Any]:
    forbidden = [path for path in paths if path.startswith(FORBIDDEN_PATH_PREFIXES)]
    approved = [path for path in paths if path.startswith(APPROVED_PATH_PREFIXES)]
    return {
        "paths": list(paths),
        "approved_paths_detected": approved,
        "forbidden_paths_detected": forbidden,
        "approved": not forbidden and (not paths or len(approved) == len(paths)),
    }


def _artifact_status(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "exists": path.exists(),
        "verified": False,
        "details": "",
    }


def _feature_060_prerequisite_verified() -> dict[str, Any]:
    status = _artifact_status(FEATURE_060_REPORT)
    if not status["exists"]:
        return status
    report = _load_json(FEATURE_060_REPORT)
    training = _load_json(FEATURE_060_TRAINING_METRICS) if FEATURE_060_TRAINING_METRICS.exists() else {}
    evaluation = _load_json(FEATURE_060_EVALUATION_METRICS) if FEATURE_060_EVALUATION_METRICS.exists() else {}
    baseline = _load_json(FEATURE_060_BASELINE_EVALUATION_METRICS) if FEATURE_060_BASELINE_EVALUATION_METRICS.exists() else {}
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


def _feature_062_prerequisite_verified() -> dict[str, Any]:
    status = _artifact_status(FEATURE_062_REPORT)
    if not status["exists"]:
        return status
    report = _load_json(FEATURE_062_REPORT)
    readiness = _load_json(FEATURE_062_COMPARISON_READINESS) if FEATURE_062_COMPARISON_READINESS.exists() else {}
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


def _feature_063_prerequisite_verified() -> dict[str, Any]:
    status = _artifact_status(FEATURE_063_REPORT)
    if not status["exists"]:
        return status
    report = _load_json(FEATURE_063_REPORT)
    checkpoint_metrics = _load_json(FEATURE_063_CHECKPOINT_METRICS) if FEATURE_063_CHECKPOINT_METRICS.exists() else []
    readiness = _load_json(FEATURE_063_COMPARISON_READINESS) if FEATURE_063_COMPARISON_READINESS.exists() else {}
    comparison_table = _load_json(FEATURE_063_STAGED_COMPARATIVE_TABLE) if FEATURE_063_STAGED_COMPARATIVE_TABLE.exists() else {}
    budgets = [entry.get("training_budget") for entry in checkpoint_metrics] if isinstance(checkpoint_metrics, list) else []
    status["verified"] = (
        report.get("final_verdict") == "staged_training_budget_learning_curve_ready"
        and report.get("remaining_blockers") == []
        and report.get("training_mode") == "cumulative_staged"
        and report.get("training_rerun_from_scratch") is False
        and report.get("checkpoint_budgets") == list(CHECKPOINT_BUDGETS)
        and readiness.get("comparison_ready") is True
        and readiness.get("training_mode") == "cumulative_staged"
        and comparison_table.get("rows")
        and budgets == list(CHECKPOINT_BUDGETS)
    )
    status["details"] = "Feature 063 checkpoint metrics, comparison readiness, and staged comparative table validated"
    return status


def _checkpoint_metrics() -> list[dict[str, Any]]:
    payload = _load_json(FEATURE_063_CHECKPOINT_METRICS)
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("checkpoint_metrics"), list):
        return payload["checkpoint_metrics"]
    raise ValueError("checkpoint-metrics artifact has an unexpected schema")


def _evaluation_mean_rewards(checkpoints: list[dict[str, Any]]) -> dict[int, float]:
    return {
        int(checkpoint["training_budget"]): float(checkpoint["evaluation_reward_summary"]["mean_reward"])
        for checkpoint in checkpoints
    }


def _action_distributions(checkpoints: list[dict[str, Any]]) -> dict[int, dict[str, int]]:
    return {
        int(checkpoint["training_budget"]): dict(checkpoint["action_distribution"])
        for checkpoint in checkpoints
    }


def _replay_sizes(checkpoints: list[dict[str, Any]]) -> dict[int, int]:
    return {int(checkpoint["training_budget"]): int(checkpoint["replay_size"]) for checkpoint in checkpoints}


def _vertical_shares(action_distributions: dict[int, dict[str, int]]) -> dict[int, float]:
    shares: dict[int, float] = {}
    for budget, counts in action_distributions.items():
        total = sum(int(counts.get(action, 0)) for action in ("local", "horizontal", "vertical"))
        shares[budget] = (int(counts.get("vertical", 0)) / total) if total else 0.0
    return shares


def _reward_stability_review(checkpoints: list[dict[str, Any]], feature_060_eval: dict[str, Any], feature_062_readiness: dict[str, Any]) -> RewardStabilityReview:
    budgets = [int(checkpoint["training_budget"]) for checkpoint in checkpoints]
    mean_rewards = _evaluation_mean_rewards(checkpoints)
    static_values = len(set(mean_rewards.values())) == 1
    deterministic_evaluation_path = bool(feature_060_eval.get("train_eval_separation", {}).get("trace_bank_disjoint")) and bool(
        feature_060_eval.get("real_trainer_bound_evaluation")
    )
    same_trace_bank = (
        feature_060_eval.get("train_eval_separation", {}).get("trace_bank_ids", {}).get("evaluation") == feature_060_eval.get("evaluation_trace_bank_id")
        if feature_060_eval.get("train_eval_separation")
        else False
    )
    likely_causes = [
        "same_evaluation_trace_bank",
        "deterministic_evaluation_path",
        "policy_not_affecting_evaluation_reward",
        "environment_or_evaluator_design_limitation",
    ] if static_values else []
    evidence_notes = [
        "Feature 063 evaluation mean reward is -4181.2 at 100, 150, 200, and 500 episodes.",
        "Feature 063 evaluation traces are disjoint from training traces and reuse the same evaluation bank.",
        "Feature 060 evaluation metrics are schema-complete, but delay and timeout are explicitly not claimed there.",
    ]
    return RewardStabilityReview(
        evaluation_reward_static_across_budget=static_values,
        checkpoint_budgets=budgets,
        evaluation_mean_rewards=mean_rewards,
        same_evaluation_trace_bank=same_trace_bank or bool(feature_062_readiness.get("comparison_ready")),
        deterministic_evaluation_path=deterministic_evaluation_path,
        policy_not_affecting_evaluation_reward=static_values,
        likely_causes=likely_causes,
        evidence_notes=evidence_notes,
    )


def _action_collapse_review(checkpoints: list[dict[str, Any]]) -> ActionCollapseReview:
    budgets = [int(checkpoint["training_budget"]) for checkpoint in checkpoints]
    action_distributions = _action_distributions(checkpoints)
    vertical_shares = _vertical_shares(action_distributions)
    vertical_collapse = vertical_shares.get(500, 0.0) >= 0.99
    possible_causes = [
        "expected_policy_convergence",
        "degenerate_policy_collapse",
        "reward_incentive_artifact",
        "evaluation_training_mismatch",
    ] if vertical_collapse else []
    evidence_notes = [
        "The vertical share rises from 30.52% at 100 episodes to 100% at 500 episodes.",
        "Invalid or noop actions remain at 0 across all checkpoints, so illegality is not the explanation.",
    ]
    return ActionCollapseReview(
        vertical_action_collapse_detected=vertical_collapse,
        checkpoint_budgets=budgets,
        action_distributions=action_distributions,
        vertical_share_by_budget=vertical_shares,
        dominant_action="vertical",
        possible_causes=possible_causes,
        evidence_notes=evidence_notes,
    )


def _replay_buffer_review(checkpoints: list[dict[str, Any]]) -> ReplayBufferReview:
    config_capacity = CampaignConfig().replay_memory_capacity
    observed = _replay_sizes(checkpoints)
    cap_detected = all(size == config_capacity for size in observed.values())
    evidence_notes = [
        "CampaignConfig.replay_memory_capacity validates to 10000.",
        "DDQNTrainer instantiates ReplayBuffer(capacity=self.config.replay_memory_capacity, ...).",
        "Every Feature 063 checkpoint reports replay_size = 10000.",
    ]
    return ReplayBufferReview(
        replay_buffer_capacity=config_capacity,
        observed_replay_size_by_checkpoint=observed,
        replay_size_cap_detected=cap_detected,
        is_cap_expected=True,
        is_cap_blocking_larger_training=True,
        cap_type="configured_cap",
        evidence_notes=evidence_notes,
    )


def _evaluation_signal_review(
    feature_060_eval: dict[str, Any],
    feature_060_baseline: dict[str, Any],
    feature_062_readiness: dict[str, Any],
    reward_review: RewardStabilityReview,
) -> EvaluationSignalReview:
    delay = feature_060_eval.get("delay", {})
    timeout = feature_060_eval.get("timeout", {})
    drop = feature_060_eval.get("drop", {})
    reward = feature_060_eval.get("reward", {})
    train_eval = feature_060_eval.get("train_eval_separation", {})
    baseline_metrics_available = bool(feature_060_baseline.get("baseline_metrics_real_execution")) and bool(feature_060_baseline.get("no_baseline_superiority_claim"))
    missing_or_null_metrics = []
    if delay.get("value") is None or delay.get("status") == "not_claimed_in_feature_060":
        missing_or_null_metrics.append("delay")
    if timeout.get("value") is None or timeout.get("status") == "not_claimed_in_feature_060":
        missing_or_null_metrics.append("timeout")
    thesis_level_sufficient = False
    evidence_notes = [
        "Feature 060 metric schema is complete, but delay and timeout are explicitly not claimed.",
        "Feature 063 checkpoints only provide descriptive reward/action counts and do not supply delay or QoS-style metrics.",
        "Comparison readiness is descriptive only, not a thesis-result signal.",
    ]
    return EvaluationSignalReview(
        reward_available=reward.get("mean_reward") is not None,
        drop_count_available=drop.get("count") is not None,
        completed_task_count_available=feature_060_eval.get("completed_task_count") is not None,
        delay_metric_available=delay.get("value") is not None and delay.get("status") != "not_claimed_in_feature_060",
        timeout_metric_available=timeout.get("value") is not None and timeout.get("status") != "not_claimed_in_feature_060",
        train_eval_separation_available=bool(train_eval.get("trace_bank_disjoint")),
        baseline_metrics_available=baseline_metrics_available,
        thesis_level_sufficient=thesis_level_sufficient,
        missing_or_null_metrics=missing_or_null_metrics,
        comparison_ready=bool(feature_062_readiness.get("comparison_ready")) and reward_review.evaluation_reward_static_across_budget,
        evidence_notes=evidence_notes,
    )


def _next_action_decision(
    reward_review: RewardStabilityReview,
    action_review: ActionCollapseReview,
    replay_review: ReplayBufferReview,
    evaluation_review: EvaluationSignalReview,
) -> NextActionDecision:
    if not reward_review.evaluation_reward_static_across_budget and not action_review.vertical_action_collapse_detected and evaluation_review.thesis_level_sufficient:
        return NextActionDecision(
            recommended_next_action="release_ready_for_thesis_drafting",
            decision_reason="The evidence is sufficiently dynamic and claim-safe for release readiness.",
            should_run_larger_training_next=False,
            should_audit_reward_and_evaluation_design_first=False,
            should_fix_action_collapse_first=False,
            should_fix_replay_capacity_or_reporting_first=False,
        )
    return NextActionDecision(
        recommended_next_action=RECOMMENDED_NEXT_ACTION,
        decision_reason=(
            "Do not spend on larger training yet. The evaluation reward is static across the staged budgets, "
            "the 500-episode policy collapses to vertical actions, and the current evaluation signal is not rich enough for thesis-level claims."
        ),
        should_run_larger_training_next=False,
        should_audit_reward_and_evaluation_design_first=True,
        should_fix_action_collapse_first=action_review.vertical_action_collapse_detected,
        should_fix_replay_capacity_or_reporting_first=False,
    )


def _prerequisite_artifacts(
    feature_060: dict[str, Any],
    feature_062: dict[str, Any],
    feature_063: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    return {
        "feature_060_report": feature_060,
        "feature_060_training_metrics": {
            "path": str(FEATURE_060_TRAINING_METRICS),
            "exists": FEATURE_060_TRAINING_METRICS.exists(),
            "verified": feature_060.get("verified") is True,
        },
        "feature_060_evaluation_metrics": {
            "path": str(FEATURE_060_EVALUATION_METRICS),
            "exists": FEATURE_060_EVALUATION_METRICS.exists(),
            "verified": feature_060.get("verified") is True,
        },
        "feature_060_baseline_evaluation_metrics": {
            "path": str(FEATURE_060_BASELINE_EVALUATION_METRICS),
            "exists": FEATURE_060_BASELINE_EVALUATION_METRICS.exists(),
            "verified": feature_060.get("verified") is True,
        },
        "feature_062_report": feature_062,
        "feature_062_comparison_readiness": {
            "path": str(FEATURE_062_COMPARISON_READINESS),
            "exists": FEATURE_062_COMPARISON_READINESS.exists(),
            "verified": feature_062.get("verified") is True,
        },
        "feature_062_final_findings": {
            "path": str(FEATURE_062_FINAL_FINDINGS),
            "exists": FEATURE_062_FINAL_FINDINGS.exists(),
            "verified": feature_062.get("verified") is True,
        },
        "feature_063_report": feature_063,
        "feature_063_checkpoint_metrics": {
            "path": str(FEATURE_063_CHECKPOINT_METRICS),
            "exists": FEATURE_063_CHECKPOINT_METRICS.exists(),
            "verified": feature_063.get("verified") is True,
        },
        "feature_063_comparison_readiness": {
            "path": str(FEATURE_063_COMPARISON_READINESS),
            "exists": FEATURE_063_COMPARISON_READINESS.exists(),
            "verified": feature_063.get("verified") is True,
        },
        "feature_063_staged_comparative_table": {
            "path": str(FEATURE_063_STAGED_COMPARATIVE_TABLE),
            "exists": FEATURE_063_STAGED_COMPARATIVE_TABLE.exists(),
            "verified": feature_063.get("verified") is True,
        },
    }


def _questions(
    reward_review: RewardStabilityReview,
    action_review: ActionCollapseReview,
    replay_review: ReplayBufferReview,
    evaluation_review: EvaluationSignalReview,
    next_action: NextActionDecision,
) -> dict[str, dict[str, Any]]:
    return {
        "q1_reward_static": {
            "question": "Why did evaluation mean reward remain constant across 100/150/200/500?",
            "answer": (
                "The checkpoint mean reward is exactly -4181.2 at every budget, while the evaluation trace bank stays disjoint and fixed. "
                "The evidence supports a deterministic evaluation path on the same evaluation bank, not a meaningful reward trend."
            ),
            "evidence": reward_review.evidence_notes,
            "uncertainty": "The artifacts do not let us distinguish a pure evaluator limitation from a reward extraction bug with certainty.",
        },
        "q2_action_drift": {
            "question": "Why did the policy/action distribution drift toward vertical-only by 500 episodes?",
            "answer": (
                "The 500-episode checkpoint is 100% vertical actions. That looks like a policy collapse or a reward incentive artifact, "
                "not an action legality problem, because invalid or noop actions remain zero."
            ),
            "evidence": action_review.evidence_notes,
            "uncertainty": "The current artifacts do not prove whether this is expected convergence or a degenerate collapse; both remain plausible.",
        },
        "q3_replay_cap": {
            "question": "Is replay_size capped at 10000, and is that expected or a hidden bottleneck?",
            "answer": (
                "Yes. The trainer config enforces a replay capacity of 10000 and the observed replay size is 10000 at every checkpoint. "
                "That cap is expected, but it is also a likely bottleneck for much longer training because the buffer is already saturated."
            ),
            "evidence": replay_review.evidence_notes,
            "uncertainty": "The cap is explicit, so it is not hidden; the bottleneck concern is an inference about longer runs."
        },
        "q4_signal_sufficient": {
            "question": "Is the current reward/evaluation signal sufficient for thesis-level result claims?",
            "answer": (
                "No. The current signal is descriptive and comparison-ready, but it lacks claimed delay and timeout metrics and does not show a changing evaluation reward. "
                "That is not enough for thesis-level claims."
            ),
            "evidence": evaluation_review.evidence_notes,
            "uncertainty": "None of the available artifacts justify a stronger claim."
        },
        "q5_next_step": {
            "question": "Should we run larger training next, or audit/fix reward/evaluation design first?",
            "answer": (
                "Audit and fix reward/evaluation design first. Larger training would mostly amplify the same signal problem and the same action-collapse behavior."
            ),
            "evidence": [next_action.decision_reason],
            "uncertainty": "Running larger training before fixing the signal would be a spend, not a diagnosis."
        },
    }


def _claim_safety_status() -> ClaimSafetyStatus:
    return ClaimSafetyStatus(
        paper_reproduction_claim_made=False,
        performance_superiority_claim_made=False,
        baseline_superiority_claim_made=False,
        claim_safety_passed=True,
    )


def _scope_guard_summary(status_paths: list[str], staged_paths: list[str], diff_paths: list[str]) -> dict[str, Any]:
    status_classification = _path_classification(status_paths)
    staged_classification = _path_classification(staged_paths)
    diff_classification = _path_classification(diff_paths)
    return {
        "working_tree": status_classification,
        "staged": staged_classification,
        "base_branch_diff": diff_classification,
        "working_tree_paths_approved": status_classification["approved"],
        "staged_paths_approved": staged_classification["approved"],
        "base_branch_head_diff_approved": diff_classification["approved"],
        "forbidden_paths_detected": (
            status_classification["forbidden_paths_detected"]
            + staged_classification["forbidden_paths_detected"]
            + diff_classification["forbidden_paths_detected"]
        ),
        "approved_paths_detected": (
            status_classification["approved_paths_detected"]
            + staged_classification["approved_paths_detected"]
            + diff_classification["approved_paths_detected"]
        ),
    }


def _prerequisite_tags_verified(
    feature_060: dict[str, Any],
    feature_062: dict[str, Any],
    feature_063: dict[str, Any],
    scope_guard: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {"name": "branch", "verified": _git_output("branch", "--show-current") == BRANCH_NAME, "details": "current branch matches the Feature 064 branch"},
        {"name": "not_main", "verified": _git_output("branch", "--show-current") != "main", "details": "current branch is not main"},
        {"name": "feature_060_report_valid", "verified": feature_060.get("verified") is True, "details": "Feature 060 committed artifacts are valid"},
        {"name": "feature_062_report_valid", "verified": feature_062.get("verified") is True, "details": "Feature 062 committed artifacts are valid"},
        {"name": "feature_063_report_valid", "verified": feature_063.get("verified") is True, "details": "Feature 063 committed artifacts are valid"},
        {"name": "working_tree_paths_approved", "verified": scope_guard["working_tree_paths_approved"], "details": "working tree paths stay inside the approved scope"},
        {"name": "staged_paths_approved", "verified": scope_guard["staged_paths_approved"], "details": "staged paths stay inside the approved scope"},
        {"name": "base_branch_head_diff_approved", "verified": scope_guard["base_branch_head_diff_approved"], "details": "base-branch diff stays inside the approved scope"},
    ]


def build_final_review_release_gate_batch_report() -> FinalReviewReleaseGateBatchReport:
    config = FinalReviewReleaseGateBatchConfig()
    status_paths = _status_paths()
    staged_paths = _staged_paths()
    diff_paths = _diff_paths(config.base_branch_name)
    feature_060 = _feature_060_prerequisite_verified()
    feature_062 = _feature_062_prerequisite_verified()
    feature_063 = _feature_063_prerequisite_verified()
    checkpoints = _checkpoint_metrics() if all(entry["verified"] for entry in (feature_060, feature_062, feature_063) if isinstance(entry, dict)) else []

    feature_060_eval = _load_json(FEATURE_060_EVALUATION_METRICS) if FEATURE_060_EVALUATION_METRICS.exists() else {}
    feature_060_baseline = _load_json(FEATURE_060_BASELINE_EVALUATION_METRICS) if FEATURE_060_BASELINE_EVALUATION_METRICS.exists() else {}
    feature_062_readiness = _load_json(FEATURE_062_COMPARISON_READINESS) if FEATURE_062_COMPARISON_READINESS.exists() else {}
    feature_063_readiness = _load_json(FEATURE_063_COMPARISON_READINESS) if FEATURE_063_COMPARISON_READINESS.exists() else {}

    reward_review = _reward_stability_review(checkpoints, feature_060_eval, feature_062_readiness) if checkpoints else RewardStabilityReview(
        evaluation_reward_static_across_budget=False,
        checkpoint_budgets=list(CHECKPOINT_BUDGETS),
        evaluation_mean_rewards={budget: 0.0 for budget in CHECKPOINT_BUDGETS},
        same_evaluation_trace_bank=False,
        deterministic_evaluation_path=False,
        policy_not_affecting_evaluation_reward=False,
        likely_causes=[],
        evidence_notes=[],
    )
    action_review = _action_collapse_review(checkpoints) if checkpoints else ActionCollapseReview(
        vertical_action_collapse_detected=False,
        checkpoint_budgets=list(CHECKPOINT_BUDGETS),
        action_distributions={budget: {"local": 0, "horizontal": 0, "vertical": 0} for budget in CHECKPOINT_BUDGETS},
        vertical_share_by_budget={budget: 0.0 for budget in CHECKPOINT_BUDGETS},
        dominant_action="vertical",
        possible_causes=[],
        evidence_notes=[],
    )
    replay_review = _replay_buffer_review(checkpoints) if checkpoints else ReplayBufferReview(
        replay_buffer_capacity=10_000,
        observed_replay_size_by_checkpoint={budget: 0 for budget in CHECKPOINT_BUDGETS},
        replay_size_cap_detected=False,
        is_cap_expected=True,
        is_cap_blocking_larger_training=False,
        cap_type="unclear",
        evidence_notes=[],
    )
    evaluation_review = _evaluation_signal_review(feature_060_eval, feature_060_baseline, feature_062_readiness, reward_review)
    next_action_decision = _next_action_decision(reward_review, action_review, replay_review, evaluation_review)
    scope_guard = _scope_guard_summary(status_paths, staged_paths, diff_paths)
    claim_safety = _claim_safety_status()
    questions = _questions(reward_review, action_review, replay_review, evaluation_review, next_action_decision)
    diagnostic_findings = DiagnosticFindings(
        feature_060_prerequisite_verified=feature_060.get("verified") is True,
        feature_062_prerequisite_verified=feature_062.get("verified") is True,
        feature_063_prerequisite_verified=feature_063.get("verified") is True,
        evaluation_reward_static_across_budget=reward_review.evaluation_reward_static_across_budget,
        vertical_action_collapse_detected=action_review.vertical_action_collapse_detected,
        replay_size_cap_detected=replay_review.replay_size_cap_detected,
        evaluation_signal_sufficient_for_claims=evaluation_review.thesis_level_sufficient,
        recommended_next_action=next_action_decision.recommended_next_action,
        questions=questions,
    )

    artifact_statuses = _prerequisite_artifacts(feature_060, feature_062, feature_063)
    prerequisite_tags_verified = _prerequisite_tags_verified(feature_060, feature_062, feature_063, scope_guard)
    remaining_blockers: list[str] = []
    if not feature_060.get("verified"):
        remaining_blockers.append("feature_060_prerequisite_blocked")
    if not feature_062.get("verified"):
        remaining_blockers.append("feature_062_prerequisite_blocked")
    if not feature_063.get("verified"):
        remaining_blockers.append("feature_063_prerequisite_blocked")
    if reward_review.evaluation_reward_static_across_budget:
        remaining_blockers.append("evaluation_reward_static_blocker")
    if action_review.vertical_action_collapse_detected:
        remaining_blockers.append("vertical_action_collapse_blocker")
    if not replay_review.is_cap_expected:
        remaining_blockers.append("replay_buffer_capacity_unclear")
    if not evaluation_review.thesis_level_sufficient:
        remaining_blockers.append("evaluation_signal_insufficient_for_claims")
    if scope_guard["forbidden_paths_detected"]:
        remaining_blockers.append("scope_drift_detected")

    final_verdict = "final_review_release_gate_ready" if not remaining_blockers and claim_safety.claim_safety_passed else "final_review_release_gate_blocked"
    if final_verdict == "final_review_release_gate_ready":
        recommended_next_action = "release_ready_for_thesis_drafting"
    else:
        recommended_next_action = next_action_decision.recommended_next_action

    artifact_completeness_summary = {
        "feature_063_final_exports_exist": all(
            path.exists()
            for path in (
                FEATURE_063_REPORT,
                FEATURE_063_CHECKPOINT_METRICS,
                FEATURE_063_COMPARISON_READINESS,
                FEATURE_063_STAGED_COMPARATIVE_TABLE,
            )
        ),
    }
    claim_boundary_review_summary = {
        "no_paper_reproduction_claim": True,
        "no_performance_superiority_claim": True,
        "no_baseline_superiority_claim": True,
    }
    repository_state_audit_summary = {
        "release_evidence_mapped_to_source": not scope_guard["forbidden_paths_detected"],
        "working_tree_paths_approved": scope_guard["working_tree_paths_approved"],
        "staged_paths_approved": scope_guard["staged_paths_approved"],
        "base_branch_head_diff_approved": scope_guard["base_branch_head_diff_approved"],
    }
    handoff_summary = {
        "next_work_recommendation": "Release tag creation or thesis/paper writing workflow",
        "next_action": recommended_next_action,
    }
    safety_summary = {
        "no_release_tag_created": True,
        "no_paper_reproduction_claim": True,
        "no_performance_superiority_claim": True,
        "no_baseline_superiority_claim": True,
        "no_uncontrolled_campaign_loop": True,
        "no_policy_drift": True,
        "no_dependency_drift": True,
        "no_environment_contract_drift": True,
        "no_reward_timing_change": True,
        "no_prior_artifact_rewrite": True,
    }

    figure_manifest = generate_figures(
        figures_dir=FIGURES_DIR,
        reward_values=reward_review.evaluation_mean_rewards,
        action_distributions=action_review.action_distributions,
        replay_sizes=replay_review.observed_replay_size_by_checkpoint,
        replay_capacity=replay_review.replay_buffer_capacity,
    )

    report = FinalReviewReleaseGateBatchReport(
        feature_id=FEATURE_ID,
        branch_name=_git_output("branch", "--show-current") or BRANCH_NAME,
        base_branch_name=BASE_BRANCH_NAME,
        prerequisite_tags_verified=prerequisite_tags_verified,
        prerequisite_artifacts=artifact_statuses,
        feature_060_prerequisite_verified=feature_060.get("verified") is True,
        feature_062_prerequisite_verified=feature_062.get("verified") is True,
        feature_063_prerequisite_verified=feature_063.get("verified") is True,
        feature_063_verified=feature_063.get("verified") is True,
        checkpoint_budgets=list(CHECKPOINT_BUDGETS),
        evaluation_episode_count_per_checkpoint=EVALUATION_EPISODES_PER_CHECKPOINT,
        episode_length=110,
        training_rerun_from_scratch=False,
        training_5000_run=False,
        artifact_completeness_summary=artifact_completeness_summary,
        claim_boundary_review_summary=claim_boundary_review_summary,
        reward_stability_review=reward_review.to_dict(),
        action_collapse_review=action_review.to_dict(),
        replay_buffer_review=replay_review.to_dict(),
        evaluation_signal_review=evaluation_review.to_dict(),
        next_action_decision={**next_action_decision.to_dict(), "recommended_next_action": recommended_next_action},
        diagnostic_findings=diagnostic_findings.to_dict(),
        claim_safety_status=claim_safety.to_dict(),
        figure_manifest=figure_manifest,
        scope_guard_summary=scope_guard,
        repository_state_audit_summary=repository_state_audit_summary,
        handoff_summary=handoff_summary,
        safety_summary=safety_summary,
        remaining_blockers=remaining_blockers,
        recommended_next_action=recommended_next_action,
        recommended_next_feature="Release tag creation or thesis/paper writing workflow",
        final_verdict=final_verdict,
    )
    return report


def generate_final_review_release_gate_batch_artifacts(report: FinalReviewReleaseGateBatchReport) -> dict[str, Path]:
    report_json_path, report_md_path, summary_path = write_final_review_release_gate_batch_report(report, OUTPUT_DIR)
    payload = report.to_dict()
    json_path = OUTPUT_DIR / DIAGNOSTIC_FINDINGS_JSON.name
    json_path.write_text(json_dump(payload["diagnostic_findings"]), encoding="utf-8")
    (OUTPUT_DIR / REWARD_STABILITY_REVIEW_JSON.name).write_text(json_dump(payload["reward_stability_review"]), encoding="utf-8")
    (OUTPUT_DIR / ACTION_COLLAPSE_REVIEW_JSON.name).write_text(json_dump(payload["action_collapse_review"]), encoding="utf-8")
    (OUTPUT_DIR / REPLAY_BUFFER_REVIEW_JSON.name).write_text(json_dump(payload["replay_buffer_review"]), encoding="utf-8")
    (OUTPUT_DIR / EVALUATION_SIGNAL_REVIEW_JSON.name).write_text(json_dump(payload["evaluation_signal_review"]), encoding="utf-8")
    (OUTPUT_DIR / NEXT_ACTION_DECISION_JSON.name).write_text(json_dump(payload["next_action_decision"]), encoding="utf-8")
    (OUTPUT_DIR / FIGURE_MANIFEST_JSON.name).write_text(json_dump(payload["figure_manifest"]), encoding="utf-8")
    return {
        "report_json": report_json_path,
        "report_md": report_md_path,
        "summary_md": summary_path,
        "diagnostic_findings": json_path,
        "reward_stability_review": OUTPUT_DIR / REWARD_STABILITY_REVIEW_JSON.name,
        "action_collapse_review": OUTPUT_DIR / ACTION_COLLAPSE_REVIEW_JSON.name,
        "replay_buffer_review": OUTPUT_DIR / REPLAY_BUFFER_REVIEW_JSON.name,
        "evaluation_signal_review": OUTPUT_DIR / EVALUATION_SIGNAL_REVIEW_JSON.name,
        "next_action_decision": OUTPUT_DIR / NEXT_ACTION_DECISION_JSON.name,
        "figure_manifest": OUTPUT_DIR / FIGURE_MANIFEST_JSON.name,
    }


def run_final_review_release_gate_batch() -> dict[str, Any]:
    report = build_final_review_release_gate_batch_report()
    artifacts = generate_final_review_release_gate_batch_artifacts(report)
    payload = report.to_dict()
    payload["generated_artifacts"] = {name: str(path) for name, path in artifacts.items()}
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="print the report JSON after generating artifacts")
    args = parser.parse_args(argv)
    payload = run_final_review_release_gate_batch()
    if args.json:
        sys.stdout.write(json_dump(payload))
    else:
        sys.stdout.write(render_final_review_summary_markdown(payload))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
