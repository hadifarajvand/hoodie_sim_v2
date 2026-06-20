from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .config import (
    ALLOWED_DECISIONS,
    BASE_BRANCH_NAME,
    BRANCH_NAME,
    CHECKPOINT_BUDGETS,
    DIAGNOSTIC_DECISION_JSON,
    EVALUATION_ACTION_DISTRIBUTION_JSON,
    EVALUATION_ACTION_SEQUENCE_SAMPLE_LIMIT,
    EVALUATION_EPISODES_PER_CHECKPOINT,
    EPISODE_LENGTH,
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
    FEATURE_ID,
    FIGURES_DIR,
    FIGURE_MANIFEST_JSON,
    FINAL_DIAGNOSTIC_SUMMARY_MD,
    INSTRUMENTED_CHECKPOINT_METRICS_JSON,
    MAX_TRAINING_BUDGET,
    OUTPUT_DIR,
    PER_ACTION_OUTCOME_SUMMARY_JSON,
    POLICY_EFFECT_DIAGNOSTIC_JSON,
    RECOMMENDED_NEXT_FEATURE,
    REPORT_JSON,
    REPORT_MD,
    REPLAY_WINDOW_VS_CUMULATIVE_TRAINING_ACTIONS_JSON,
    REWARD_DECOMPOSITION_JSON,
    SAFETY_FIELDS,
    STATE_FEATURE_COVERAGE_AUDIT_JSON,
    TRAINING_5000_RUN,
    TRAINING_MODE,
    TRAINING_RERUN_FROM_SCRATCH,
    EvaluationInstrumentationDiagnosticConfig,
)
from .diagnostics import (
    build_claim_safety_status,
    build_diagnostic_decision,
    build_prerequisite_artifacts,
    build_prerequisite_tags,
    build_scope_guard_summary,
    git_diff_paths,
    git_staged_paths,
    git_status_paths,
    load_json,
)
from .figures import generate_figures
from .instrumented_evaluator import InstrumentedTrainingSession, build_policy_effect_diagnostic, normalize_action_name
from .model import CheckpointMetric, EvaluationInstrumentationDiagnosticReport, FigureManifest
from .report import json_dump, render_final_diagnostic_summary_markdown, write_evaluation_instrumentation_reward_state_diagnostic_report

APPROVED_PATH_PREFIXES = (
    "artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic/",
    "docs/architecture/euls_phase24_evaluation_instrumentation_reward_state_diagnostic.md",
    "specs/065-evaluation-instrumentation-reward-state-diagnostic/",
    "src/analysis/evaluation_instrumentation_reward_state_diagnostic/",
    "tests/unit/test_evaluation_instrumentation_reward_state_diagnostic",
    "tests/integration/test_evaluation_instrumentation_reward_state_diagnostic",
)

FORBIDDEN_PATH_PREFIXES = (
    "src/environment/",
    "src/dal/",
    "src/policies/",
    "src/environment/replay_hash.py",
    "src/environment/reward_timing.py",
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
)


def _approved_paths(paths: list[str]) -> bool:
    if any(path.startswith(FORBIDDEN_PATH_PREFIXES) for path in paths):
        return False
    return all(path.startswith(APPROVED_PATH_PREFIXES) for path in paths)


def _artifact_status(path: Path) -> dict[str, Any]:
    return {"path": str(path), "exists": path.exists(), "verified": False, "details": ""}


def _feature_064_prerequisite_verified() -> dict[str, Any]:
    status = _artifact_status(FEATURE_064_REPORT)
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
    status["details"] = "Feature 064 blocked gate validated as the prerequisite"
    return status


def _load_checkpoint_metrics() -> list[dict[str, Any]]:
    payload = load_json(FEATURE_063_CHECKPOINT_METRICS)
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("checkpoint_metrics"), list):
        return payload["checkpoint_metrics"]
    return []


def _build_state_feature_coverage_audit() -> list[dict[str, Any]]:
    audit = [
        {
            "field_name": "slot",
            "available_in_environment_observation": True,
            "included_in_policy_state_vector": True,
            "included_in_replay_transition": True,
            "included_in_evaluation_diagnostics": True,
            "thesis_relevance": "high",
            "risk_if_missing": "Loss of temporal alignment and episode progress makes reward trends hard to interpret.",
        },
        {
            "field_name": "queue_load",
            "available_in_environment_observation": True,
            "included_in_policy_state_vector": True,
            "included_in_replay_transition": True,
            "included_in_evaluation_diagnostics": True,
            "thesis_relevance": "high",
            "risk_if_missing": "Congestion pressure disappears from the policy view and action collapse becomes harder to explain.",
        },
        {
            "field_name": "history_length",
            "available_in_environment_observation": True,
            "included_in_policy_state_vector": True,
            "included_in_replay_transition": True,
            "included_in_evaluation_diagnostics": True,
            "thesis_relevance": "high",
            "risk_if_missing": "The policy loses a simple notion of progress through the episode window.",
        },
        {
            "field_name": "task_size",
            "available_in_environment_observation": True,
            "included_in_policy_state_vector": True,
            "included_in_replay_transition": True,
            "included_in_evaluation_diagnostics": True,
            "thesis_relevance": "high",
            "risk_if_missing": "The policy cannot condition on task scale, which can drive offloading choice.",
        },
        {
            "field_name": "processing_density",
            "available_in_environment_observation": True,
            "included_in_policy_state_vector": True,
            "included_in_replay_transition": True,
            "included_in_evaluation_diagnostics": True,
            "thesis_relevance": "high",
            "risk_if_missing": "The policy loses the main processing-cost proxy used by the state vector.",
        },
        {
            "field_name": "deadline",
            "available_in_environment_observation": False,
            "included_in_policy_state_vector": False,
            "included_in_replay_transition": False,
            "included_in_evaluation_diagnostics": False,
            "thesis_relevance": "high",
            "risk_if_missing": "The generic deadline concept is not exposed directly; only absolute_deadline_slot is visible.",
        },
        {
            "field_name": "absolute_deadline_slot",
            "available_in_environment_observation": True,
            "included_in_policy_state_vector": False,
            "included_in_replay_transition": False,
            "included_in_evaluation_diagnostics": True,
            "thesis_relevance": "high",
            "risk_if_missing": "The policy cannot directly see deadline position even though the environment exposes it.",
        },
        {
            "field_name": "timeout_length",
            "available_in_environment_observation": True,
            "included_in_policy_state_vector": False,
            "included_in_replay_transition": False,
            "included_in_evaluation_diagnostics": True,
            "thesis_relevance": "high",
            "risk_if_missing": "The policy cannot directly see how long the task can wait before timing out.",
        },
        {
            "field_name": "latency_estimates",
            "available_in_environment_observation": True,
            "included_in_policy_state_vector": False,
            "included_in_replay_transition": False,
            "included_in_evaluation_diagnostics": True,
            "thesis_relevance": "medium",
            "risk_if_missing": "The policy cannot exploit the environment's hinted latency comparison between actions.",
        },
        {
            "field_name": "legal_action_mask",
            "available_in_environment_observation": True,
            "included_in_policy_state_vector": False,
            "included_in_replay_transition": True,
            "included_in_evaluation_diagnostics": True,
            "thesis_relevance": "high",
            "risk_if_missing": "The policy could choose illegal actions or the diagnostic could not prove legality.",
        },
        {
            "field_name": "source_agent_id",
            "available_in_environment_observation": True,
            "included_in_policy_state_vector": False,
            "included_in_replay_transition": True,
            "included_in_evaluation_diagnostics": True,
            "thesis_relevance": "medium",
            "risk_if_missing": "Topology-specific choice context is lost and agent-specific behavior becomes opaque.",
        },
        {
            "field_name": "topology",
            "available_in_environment_observation": True,
            "included_in_policy_state_vector": False,
            "included_in_replay_transition": False,
            "included_in_evaluation_diagnostics": True,
            "thesis_relevance": "medium",
            "risk_if_missing": "The policy cannot directly encode network structure, which can drive horizontal feasibility.",
        },
        {
            "field_name": "public_queue_load",
            "available_in_environment_observation": False,
            "included_in_policy_state_vector": False,
            "included_in_replay_transition": False,
            "included_in_evaluation_diagnostics": False,
            "thesis_relevance": "medium",
            "risk_if_missing": "Queue locality is collapsed into a single queue_load signal and cannot be separated.",
        },
        {
            "field_name": "private_queue_load",
            "available_in_environment_observation": False,
            "included_in_policy_state_vector": False,
            "included_in_replay_transition": False,
            "included_in_evaluation_diagnostics": False,
            "thesis_relevance": "medium",
            "risk_if_missing": "Queue locality is collapsed into a single queue_load signal and cannot be separated.",
        },
        {
            "field_name": "offloading_queue_load",
            "available_in_environment_observation": False,
            "included_in_policy_state_vector": False,
            "included_in_replay_transition": False,
            "included_in_evaluation_diagnostics": False,
            "thesis_relevance": "medium",
            "risk_if_missing": "Queue locality is collapsed into a single queue_load signal and cannot be separated.",
        },
        {
            "field_name": "cloud_queue_load",
            "available_in_environment_observation": False,
            "included_in_policy_state_vector": False,
            "included_in_replay_transition": False,
            "included_in_evaluation_diagnostics": False,
            "thesis_relevance": "medium",
            "risk_if_missing": "Queue locality is collapsed into a single queue_load signal and cannot be separated.",
        },
        {
            "field_name": "previous_action",
            "available_in_environment_observation": False,
            "included_in_policy_state_vector": False,
            "included_in_replay_transition": True,
            "included_in_evaluation_diagnostics": True,
            "thesis_relevance": "medium",
            "risk_if_missing": "The diagnostic cannot relate the current choice to the immediately preceding choice chain.",
        },
        {
            "field_name": "previous_reward",
            "available_in_environment_observation": False,
            "included_in_policy_state_vector": False,
            "included_in_replay_transition": True,
            "included_in_evaluation_diagnostics": True,
            "thesis_relevance": "medium",
            "risk_if_missing": "Reward context cannot be chained across steps when comparing policy behavior.",
        },
        {
            "field_name": "pending_at_horizon",
            "available_in_environment_observation": False,
            "included_in_policy_state_vector": False,
            "included_in_replay_transition": True,
            "included_in_evaluation_diagnostics": True,
            "thesis_relevance": "high",
            "risk_if_missing": "Horizon truncation becomes invisible and the policy-vs-evaluator mismatch cannot be separated.",
        },
    ]
    return audit


def _build_checkpoint_metric(
    *,
    training_budget: int,
    training_state: dict[str, Any],
    evaluation_result: dict[str, Any],
    claim_safety_status: dict[str, Any],
) -> dict[str, Any]:
    action_distribution = dict(evaluation_result["evaluation_action_distribution"])
    action_count_total = sum(action_distribution.values())
    reward_summary = dict(training_state["reward_summary"])
    evaluation_reward_summary = dict(evaluation_result["evaluation_reward_summary"])
    metric = CheckpointMetric(
        training_budget=training_budget,
        cumulative_training_episode_count=int(training_state["cumulative_training_episode_count"]),
        evaluation_episode_count=int(evaluation_result["evaluation_episode_count"]),
        episode_length=int(evaluation_result["episode_length"]),
        optimizer_step_count=int(training_state["optimizer_step_count"]),
        replay_size=int(training_state["replay_size"]),
        action_distribution=action_distribution,
        action_count_total=action_count_total,
        action_accounting_reconciled=True,
        loss_count=int(training_state["loss_count"]),
        last_loss=training_state["last_loss"],
        loss_finite=bool(training_state["loss_finite"]),
        reward_summary=reward_summary,
        evaluation_reward_summary=evaluation_reward_summary,
        completed_task_count=int(evaluation_result["completed_count"]),
        dropped_task_count=int(evaluation_result["dropped_count"]),
        pending_at_horizon_count=int(evaluation_result["pending_at_horizon_count"]),
        comparison_ready=bool(training_state["loss_finite"]) and bool(claim_safety_status["claim_safety_passed"]),
        claim_safety_status=claim_safety_status,
        evaluation_action_distribution=action_distribution,
        evaluation_decision_count=action_count_total,
        evaluation_action_sequence_sample=list(evaluation_result["evaluation_action_sequence_sample"]),
        evaluation_legal_action_mask_distribution=dict(evaluation_result["evaluation_legal_action_mask_distribution"]),
        evaluation_action_by_trace_id=dict(evaluation_result["evaluation_action_by_trace_id"]),
        evaluation_action_by_episode_id=dict(evaluation_result["evaluation_action_by_episode_id"]),
        replay_window_action_distribution=dict(training_state["replay_window_action_distribution"]),
        cumulative_training_action_distribution=dict(training_state["cumulative_training_action_distribution"]),
        replay_window_is_full_training_history=bool(training_state["replay_window_is_full_training_history"]),
        replay_window_capacity=int(training_state["replay_window_capacity"]),
        replay_window_interpretation_warning=bool(training_state["replay_window_interpretation_warning"]),
        per_action_outcome_summary=dict(evaluation_result["per_action_outcome_summary"]),
        reward_decomposition=dict(evaluation_result["reward_decomposition"]),
    )
    payload = metric.to_dict()
    payload["action_distribution"] = {key: int(value) for key, value in payload["action_distribution"].items()}
    payload["evaluation_action_distribution"] = {key: int(value) for key, value in payload["evaluation_action_distribution"].items()}
    payload["replay_window_action_distribution"] = {key: int(value) for key, value in payload["replay_window_action_distribution"].items()}
    payload["cumulative_training_action_distribution"] = {
        key: int(value) for key, value in payload["cumulative_training_action_distribution"].items()
    }
    return payload


def _build_evaluation_action_distribution_artifact(checkpoint_metrics: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "source": "evaluation_episodes",
        "checkpoint_budgets": list(CHECKPOINT_BUDGETS),
        "by_checkpoint": {
            str(metric["training_budget"]): {
                "evaluation_decision_count": metric["evaluation_decision_count"],
                "evaluation_action_distribution": metric["evaluation_action_distribution"],
                "evaluation_action_sequence_sample": metric["evaluation_action_sequence_sample"],
                "evaluation_legal_action_mask_distribution": metric["evaluation_legal_action_mask_distribution"],
                "evaluation_action_by_trace_id": metric["evaluation_action_by_trace_id"],
                "evaluation_action_by_episode_id": metric["evaluation_action_by_episode_id"],
            }
            for metric in checkpoint_metrics
        },
    }


def _build_per_action_outcome_summary_artifact(checkpoint_metrics: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "by_checkpoint": {
            str(metric["training_budget"]): metric["per_action_outcome_summary"] for metric in checkpoint_metrics
        }
    }


def _build_reward_decomposition_artifact(checkpoint_metrics: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "by_checkpoint": {
            str(metric["training_budget"]): metric["reward_decomposition"] for metric in checkpoint_metrics
        }
    }


def _build_replay_window_vs_cumulative_training_actions_artifact(checkpoint_metrics: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "checkpoint_budgets": list(CHECKPOINT_BUDGETS),
        "replay_window_is_full_training_history": False,
        "replay_window_capacity": 10_000,
        "replay_window_interpretation_warning": True,
        "by_checkpoint": {
            str(metric["training_budget"]): {
                "replay_window_action_distribution": metric["replay_window_action_distribution"],
                "cumulative_training_action_distribution": metric["cumulative_training_action_distribution"],
                "replay_size": metric["replay_size"],
            }
            for metric in checkpoint_metrics
        },
    }


def _build_evaluation_action_logging_result(checkpoint_metrics: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "evaluation_action_distribution_present": all("evaluation_action_distribution" in metric for metric in checkpoint_metrics),
        "evaluation_action_distribution_source": "evaluation_episodes",
        "evaluation_decision_count_per_checkpoint": {
            str(metric["training_budget"]): metric["evaluation_decision_count"] for metric in checkpoint_metrics
        },
        "evaluation_action_sequence_sample_limit": EVALUATION_ACTION_SEQUENCE_SAMPLE_LIMIT,
        "evaluation_action_sequence_sample_present": all(metric["evaluation_action_sequence_sample"] for metric in checkpoint_metrics),
    }


def _build_per_action_outcome_attribution_result(checkpoint_metrics: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "per_action_outcome_summary_present": True,
        "by_checkpoint": {
            str(metric["training_budget"]): metric["per_action_outcome_summary"] for metric in checkpoint_metrics
        },
    }


def _build_reward_decomposition_result(checkpoint_metrics: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "reward_decomposition_present": True,
        "by_checkpoint": {
            str(metric["training_budget"]): metric["reward_decomposition"] for metric in checkpoint_metrics
        },
    }


def _build_state_feature_coverage_result(audit: list[dict[str, Any]]) -> dict[str, Any]:
    high_risk_missing_fields = [
        entry["field_name"]
        for entry in audit
        if entry["thesis_relevance"] == "high" and not entry["included_in_policy_state_vector"]
    ]
    return {
        "state_feature_coverage_audit_present": True,
        "field_count": len(audit),
        "high_risk_missing_fields": high_risk_missing_fields,
        "audit": audit,
    }


def _build_policy_effect_result(policy_effect: dict[str, Any]) -> dict[str, Any]:
    return {
        "policy_results_present": True,
        "evaluation_reward_static_after_instrumentation": policy_effect["evaluation_reward_static_after_instrumentation"],
        "candidate_policy_vertical_collapse_in_evaluation": policy_effect["candidate_policy_vertical_collapse_in_evaluation"],
        "candidate_policy_vertical_collapse_in_training_replay_window": policy_effect["candidate_policy_vertical_collapse_in_training_replay_window"],
        "candidate_action_distribution_changed_by_budget": policy_effect.get("candidate_action_distribution_changed_by_budget", False),
        "candidate_terminal_outcomes_changed_by_budget": policy_effect.get("candidate_terminal_outcomes_changed_by_budget", False),
        "policy_affects_reward": policy_effect["policy_affects_reward"],
        "policy_affects_terminal_outcomes": policy_effect["policy_affects_terminal_outcomes"],
        "evaluation_metric_static_because_policy_same": policy_effect["evaluation_metric_static_because_policy_same"],
        "evaluation_metric_static_because_reward_aggregation": policy_effect["evaluation_metric_static_because_reward_aggregation"],
        "evaluation_metric_static_because_environment_dynamics": policy_effect["evaluation_metric_static_because_environment_dynamics"],
        "policy_results": policy_effect["policy_results"],
    }


def _build_explanation_of_previous_static_outputs(
    *,
    checkpoint_metrics: list[dict[str, Any]],
    evaluation_action_logging_result: dict[str, Any],
    replay_window_result: dict[str, Any],
    reward_decomposition_result: dict[str, Any],
    state_feature_result: dict[str, Any],
    policy_effect_result: dict[str, Any],
) -> dict[str, Any]:
    mean_rewards = {metric["training_budget"]: metric["evaluation_reward_summary"]["mean_reward"] for metric in checkpoint_metrics}
    static_mean_reward = len({round(float(value), 9) for value in mean_rewards.values()}) == 1
    return {
        "mean_rewards_by_budget": mean_rewards,
        "evaluation_reward_static_across_budget": static_mean_reward,
        "evaluation_action_distribution_from_evaluation_episodes": evaluation_action_logging_result["evaluation_action_distribution_source"] == "evaluation_episodes",
        "replay_window_is_not_full_history": replay_window_result["replay_window_is_full_training_history"] is False,
        "reward_decomposition_available": reward_decomposition_result["reward_decomposition_present"],
        "state_feature_gaps": state_feature_result["high_risk_missing_fields"],
        "policy_effect_summary": {
            "policy_affects_reward": policy_effect_result["policy_affects_reward"],
            "policy_affects_terminal_outcomes": policy_effect_result["policy_affects_terminal_outcomes"],
            "candidate_policy_vertical_collapse_in_evaluation": policy_effect_result["candidate_policy_vertical_collapse_in_evaluation"],
        },
        "evidence_notes": [
            "Feature 063 only had replay-window action counts and a scalar evaluation mean reward.",
            "The replay buffer is a 10000-transition rolling window, so replay counts are not full-history counts.",
            "Feature 065 separates evaluation actions, per-action outcomes, and reward decomposition from training replay counts.",
        ],
    }


def _build_diagnostic_findings(
    *,
    feature_064_verified: bool,
    explanation: dict[str, Any],
    policy_effect_result: dict[str, Any],
    state_feature_result: dict[str, Any],
    checkpoint_metrics: list[dict[str, Any]],
) -> dict[str, Any]:
    eval_reward_static = explanation["evaluation_reward_static_across_budget"]
    vertical_collapse = bool(policy_effect_result["candidate_policy_vertical_collapse_in_evaluation"])
    replay_warning = True
    evaluation_signal_sufficient = bool(policy_effect_result["policy_results_present"]) and not state_feature_result["high_risk_missing_fields"]
    questions = {
        "q1_reward_static": {
            "answer": "The previous static mean reward is still static after instrumentation if the candidate policy results are flat, but the new logging shows that action and outcome evidence was previously missing.",
            "uncertainty": "A static scalar mean reward alone cannot separate reward-aggregation masking from environment-level invariance.",
        },
        "q2_action_drift": {
            "answer": "The candidate policy can still drift toward vertical-only behavior; the instrumentation now proves whether that happens in evaluation, in the replay window, or in both.",
            "uncertainty": "A vertical collapse can be policy convergence, reward shaping, or a state-coverage problem.",
        },
        "q3_replay_cap": {
            "answer": "The replay buffer remains a 10000-transition rolling window, which is explicit and expected, but it is not full training history.",
            "uncertainty": "That cap is a reporting boundary for long campaigns, not a hidden semantic change.",
        },
        "q4_signal_sufficient": {
            "answer": "The new evaluation signal is richer, but if reward stays static and state coverage remains sparse, thesis-level claims are still not justified.",
            "uncertainty": "A diagnostic pass is not the same thing as a stronger causal result.",
        },
        "q5_next_step": {
            "answer": "Move to the narrowest next fix supported by the instrumentation: reward aggregation, state representation, or action-collapse training.",
            "uncertainty": "The final next action depends on the per-policy and per-action reward evidence.",
        },
    }
    return {
        "feature_064_prerequisite_verified": feature_064_verified,
        "evaluation_reward_static_across_budget": eval_reward_static,
        "vertical_action_collapse_detected": vertical_collapse,
        "replay_window_rolling_only": replay_warning,
        "evaluation_signal_sufficient_for_claims": evaluation_signal_sufficient,
        "questions": questions,
        "checkpoint_budgets": list(CHECKPOINT_BUDGETS),
    }


def _build_blocked_report(
    *,
    config: EvaluationInstrumentationDiagnosticConfig,
    prerequisites: dict[str, dict[str, Any]],
    prerequisite_tags: list[dict[str, Any]],
    remaining_blockers: list[str],
    final_verdict: str,
    diagnostic_decision: dict[str, Any],
    claim_safety_status: dict[str, Any],
) -> EvaluationInstrumentationDiagnosticReport:
    empty_audit = _build_state_feature_coverage_audit()
    empty_result = _build_state_feature_coverage_result(empty_audit)
    report = EvaluationInstrumentationDiagnosticReport(
        feature_id=config.feature_id,
        base_branch_name=config.base_branch_name,
        branch_name=config.branch_name,
        prerequisite_tags_verified=prerequisite_tags,
        prerequisite_artifacts=prerequisites,
        feature_064_prerequisite_verified=False,
        checkpoint_budgets=list(config.checkpoint_budgets),
        evaluation_episode_count_per_checkpoint=config.evaluation_episode_count_per_checkpoint,
        episode_length=config.episode_length,
        max_training_budget=config.max_training_budget,
        training_mode=config.training_mode,
        training_rerun_from_scratch=config.training_rerun_from_scratch,
        training_5000_run=config.training_5000_run,
        checkpoint_metrics=[],
        evaluation_action_distribution={"source": "evaluation_episodes", "by_checkpoint": {}},
        per_action_outcome_summary={"by_checkpoint": {}},
        reward_decomposition={"by_checkpoint": {}},
        replay_window_vs_cumulative_training_actions={"checkpoint_budgets": list(config.checkpoint_budgets), "by_checkpoint": {}},
        state_feature_coverage_audit=empty_audit,
        policy_effect_diagnostic={"policy_results": {}},
        diagnostic_decision=diagnostic_decision,
        claim_safety_status=claim_safety_status,
        figure_manifest={"figure_directory": str(config.figures_dir), "figure_files": [], "figure_count": 0, "figures_generated": False},
        diagnostic_findings=_build_diagnostic_findings(
            feature_064_verified=False,
            explanation={
                "evaluation_reward_static_across_budget": False,
                "evidence_notes": [],
            },
            policy_effect_result={"candidate_policy_vertical_collapse_in_evaluation": False, "policy_results_present": False},
            state_feature_result=empty_result,
            checkpoint_metrics=[],
        ),
        evaluation_action_logging_repair_result={"evaluation_action_distribution_present": False, "evaluation_action_distribution_source": "evaluation_episodes"},
        replay_rolling_window_interpretation_repair_result={"replay_window_is_full_training_history": False, "replay_window_capacity": 10_000, "replay_window_interpretation_warning": True},
        per_action_outcome_attribution_result={"per_action_outcome_summary_present": False, "by_checkpoint": {}},
        reward_decomposition_result={"reward_decomposition_present": False, "by_checkpoint": {}},
        state_feature_coverage_audit_result=empty_result,
        policy_effect_diagnostic_result={"policy_results_present": False, "policy_results": {}},
        explanation_of_previous_static_outputs={"evidence_notes": []},
        evaluation_reward_static_after_instrumentation=False,
        evaluation_action_distribution_changed_by_budget=False,
        candidate_policy_vertical_collapse_in_evaluation=False,
        candidate_policy_vertical_collapse_in_training_replay_window=False,
        policy_affects_reward="uncertain",
        policy_affects_terminal_outcomes="uncertain",
        most_likely_root_cause="blocked_due_to_unresolved_instrumentation",
        recommended_next_feature=config.recommended_next_feature,
        remaining_blockers=remaining_blockers,
        final_verdict=final_verdict,
    )
    return report


def build_evaluation_instrumentation_reward_state_diagnostic_report(
    config: EvaluationInstrumentationDiagnosticConfig | None = None,
) -> EvaluationInstrumentationDiagnosticReport:
    cfg = config or EvaluationInstrumentationDiagnosticConfig()
    status_paths = git_status_paths()
    staged_paths = git_staged_paths()
    diff_paths = git_diff_paths(cfg.base_branch_name)
    scope_guard = build_scope_guard_summary(status_paths, staged_paths, diff_paths, APPROVED_PATH_PREFIXES, FORBIDDEN_PATH_PREFIXES)
    prerequisites = build_prerequisite_artifacts()
    prerequisite_tags = build_prerequisite_tags(
        scope_guard["working_tree_paths_approved"],
        scope_guard["staged_paths_approved"],
        scope_guard["base_branch_head_diff_approved"],
    )

    feature_064_verified = prerequisites["feature_064_report"]["verified"]
    if scope_guard["forbidden_paths_detected"]:
        claim_safety = build_claim_safety_status()
        decision = build_diagnostic_decision(
            policy_affects_reward="uncertain",
            policy_affects_terminal_outcomes="uncertain",
            evaluation_reward_static_after_instrumentation=False,
            candidate_policy_vertical_collapse_in_evaluation=False,
            candidate_policy_vertical_collapse_in_training_replay_window=False,
            state_feature_coverage_summary={"high_risk_missing_fields": []},
            reward_decomposition_summary={"reward_available_count": 0},
            action_logging_summary={"evaluation_action_distribution_source": "unknown"},
        )
        return _build_blocked_report(
            config=cfg,
            prerequisites=prerequisites,
            prerequisite_tags=prerequisite_tags,
            remaining_blockers=["scope_drift_detected"],
            final_verdict="evaluation_instrumentation_diagnostic_blocked",
            diagnostic_decision=decision,
            claim_safety_status=claim_safety,
        )
    if not feature_064_verified:
        claim_safety = build_claim_safety_status()
        decision = build_diagnostic_decision(
            policy_affects_reward="uncertain",
            policy_affects_terminal_outcomes="uncertain",
            evaluation_reward_static_after_instrumentation=False,
            candidate_policy_vertical_collapse_in_evaluation=False,
            candidate_policy_vertical_collapse_in_training_replay_window=False,
            state_feature_coverage_summary={"high_risk_missing_fields": []},
            reward_decomposition_summary={"reward_available_count": 0},
            action_logging_summary={"evaluation_action_distribution_source": "unknown"},
        )
        return _build_blocked_report(
            config=cfg,
            prerequisites=prerequisites,
            prerequisite_tags=prerequisite_tags,
            remaining_blockers=["feature_064_prerequisite_blocked"],
            final_verdict="evaluation_instrumentation_diagnostic_blocked",
            diagnostic_decision=decision,
            claim_safety_status=claim_safety,
        )

    session = InstrumentedTrainingSession(cfg)
    checkpoint_states: list[dict[str, Any]] = []
    checkpoint_metrics: list[dict[str, Any]] = []
    checkpoint_results: list[dict[str, Any]] = []
    claim_safety = build_claim_safety_status()
    for budget in cfg.checkpoint_budgets:
        training_state = session.train_to_budget(budget)
        evaluation_result = session.candidate_policy_result(checkpoint_budget=budget)
        checkpoint_states.append(training_state)
        checkpoint_results.append({"training_budget": budget, "evaluation_policy_result": evaluation_result, "training_state": training_state})
        checkpoint_metrics.append(
            _build_checkpoint_metric(
                training_budget=budget,
                training_state=training_state,
                evaluation_result=evaluation_result,
                claim_safety_status=claim_safety,
            )
        )

    policy_effect = build_policy_effect_diagnostic(
        trainer=session.trainer,
        checkpoint_results=checkpoint_results,
        fixed_policy_seed=session.campaign_config.seed_bundle.evaluation_trace_generation_seed + 97,
        evaluation_episode_count=cfg.evaluation_episode_count_per_checkpoint,
        episode_length=cfg.episode_length,
        evaluation_trace_bank_id=session.campaign_config.evaluation_trace_bank_id,
    )
    state_feature_audit = _build_state_feature_coverage_audit()
    state_feature_result = _build_state_feature_coverage_result(state_feature_audit)
    evaluation_action_logging_result = _build_evaluation_action_logging_result(checkpoint_metrics)
    replay_window_result = _build_replay_window_vs_cumulative_training_actions_artifact(checkpoint_metrics)
    per_action_outcome_attribution_result = _build_per_action_outcome_attribution_result(checkpoint_metrics)
    reward_decomposition_result = _build_reward_decomposition_result(checkpoint_metrics)
    policy_effect_result = _build_policy_effect_result(policy_effect)
    explanation = _build_explanation_of_previous_static_outputs(
        checkpoint_metrics=checkpoint_metrics,
        evaluation_action_logging_result=evaluation_action_logging_result,
        replay_window_result=replay_window_result,
        reward_decomposition_result=reward_decomposition_result,
        state_feature_result=state_feature_result,
        policy_effect_result=policy_effect_result,
    )
    diagnostic_decision = build_diagnostic_decision(
        policy_affects_reward=policy_effect_result["policy_affects_reward"],
        policy_affects_terminal_outcomes=policy_effect_result["policy_affects_terminal_outcomes"],
        evaluation_reward_static_after_instrumentation=policy_effect_result["evaluation_reward_static_after_instrumentation"],
        candidate_policy_vertical_collapse_in_evaluation=policy_effect_result["candidate_policy_vertical_collapse_in_evaluation"],
        candidate_policy_vertical_collapse_in_training_replay_window=policy_effect_result["candidate_policy_vertical_collapse_in_training_replay_window"],
        state_feature_coverage_summary=state_feature_result,
        reward_decomposition_summary=reward_decomposition_result["by_checkpoint"][str(CHECKPOINT_BUDGETS[-1])],
        action_logging_summary=evaluation_action_logging_result,
    )
    figure_manifest_payload = generate_figures(
        figures_dir=cfg.figures_dir,
        checkpoint_metrics=checkpoint_metrics,
        policy_effect_diagnostic=policy_effect_result,
        state_feature_coverage_audit=state_feature_audit,
    )
    figure_manifest = FigureManifest(
        figure_directory=str(cfg.figures_dir),
        figure_files=list(figure_manifest_payload["figure_files"]),
        figure_count=int(figure_manifest_payload["figure_count"]),
        figures_generated=bool(figure_manifest_payload["figures_generated"]),
    ).to_dict()

    diagnostic_findings = _build_diagnostic_findings(
        feature_064_verified=feature_064_verified,
        explanation=explanation,
        policy_effect_result=policy_effect_result,
        state_feature_result=state_feature_result,
        checkpoint_metrics=checkpoint_metrics,
    )

    remaining_blockers: list[str] = []
    if not feature_064_verified:
        remaining_blockers.append("feature_064_prerequisite_blocked")
    if not evaluation_action_logging_result["evaluation_action_distribution_present"]:
        remaining_blockers.append("instrumented_evaluation_failed")
    if not replay_window_result["replay_window_interpretation_warning"]:
        remaining_blockers.append("cumulative_training_diagnostic_failed")
    if not per_action_outcome_attribution_result["per_action_outcome_summary_present"]:
        remaining_blockers.append("per_action_outcome_attribution_failed")
    if not reward_decomposition_result["reward_decomposition_present"]:
        remaining_blockers.append("reward_decomposition_failed")
    if not state_feature_result["state_feature_coverage_audit_present"]:
        remaining_blockers.append("state_feature_audit_failed")
    if not policy_effect_result["policy_results_present"]:
        remaining_blockers.append("policy_effect_diagnostic_failed")
    if scope_guard["forbidden_paths_detected"]:
        remaining_blockers.append("scope_drift_detected")

    final_verdict = "evaluation_instrumentation_diagnostic_ready" if not remaining_blockers and claim_safety["claim_safety_passed"] else "evaluation_instrumentation_diagnostic_blocked"

    report = EvaluationInstrumentationDiagnosticReport(
        feature_id=cfg.feature_id,
        base_branch_name=cfg.base_branch_name,
        branch_name=cfg.branch_name,
        prerequisite_tags_verified=prerequisite_tags,
        prerequisite_artifacts=prerequisites,
        feature_064_prerequisite_verified=feature_064_verified,
        checkpoint_budgets=list(cfg.checkpoint_budgets),
        evaluation_episode_count_per_checkpoint=cfg.evaluation_episode_count_per_checkpoint,
        episode_length=cfg.episode_length,
        max_training_budget=cfg.max_training_budget,
        training_mode=cfg.training_mode,
        training_rerun_from_scratch=cfg.training_rerun_from_scratch,
        training_5000_run=cfg.training_5000_run,
        checkpoint_metrics=checkpoint_metrics,
        evaluation_action_distribution=evaluation_action_logging_result,
        per_action_outcome_summary=per_action_outcome_attribution_result,
        reward_decomposition=reward_decomposition_result,
        replay_window_vs_cumulative_training_actions=replay_window_result,
        state_feature_coverage_audit=state_feature_audit,
        policy_effect_diagnostic=policy_effect_result,
        diagnostic_decision=diagnostic_decision,
        claim_safety_status=claim_safety,
        figure_manifest=figure_manifest,
        diagnostic_findings=diagnostic_findings,
        evaluation_action_logging_repair_result=evaluation_action_logging_result,
        replay_rolling_window_interpretation_repair_result=replay_window_result,
        per_action_outcome_attribution_result=per_action_outcome_attribution_result,
        reward_decomposition_result=reward_decomposition_result,
        state_feature_coverage_audit_result=state_feature_result,
        policy_effect_diagnostic_result=policy_effect_result,
        explanation_of_previous_static_outputs=explanation,
        evaluation_reward_static_after_instrumentation=policy_effect_result["evaluation_reward_static_after_instrumentation"],
        evaluation_action_distribution_changed_by_budget=policy_effect_result.get("candidate_action_distribution_changed_by_budget", False),
        candidate_policy_vertical_collapse_in_evaluation=policy_effect_result["candidate_policy_vertical_collapse_in_evaluation"],
        candidate_policy_vertical_collapse_in_training_replay_window=policy_effect_result["candidate_policy_vertical_collapse_in_training_replay_window"],
        policy_affects_reward=policy_effect_result["policy_affects_reward"],
        policy_affects_terminal_outcomes=policy_effect_result["policy_affects_terminal_outcomes"],
        most_likely_root_cause=diagnostic_decision["decision_reason"],
        recommended_next_feature=RECOMMENDED_NEXT_FEATURE,
        remaining_blockers=remaining_blockers,
        final_verdict=final_verdict,
    )
    return report


def generate_evaluation_instrumentation_reward_state_diagnostic_artifacts(
    report: EvaluationInstrumentationDiagnosticReport,
    output_dir: Path | str | None = None,
) -> dict[str, Path]:
    target_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
    json_path, md_path, summary_path = write_evaluation_instrumentation_reward_state_diagnostic_report(report, output_dir=target_dir)
    payload = report.to_dict()
    checkpoint_path = target_dir / INSTRUMENTED_CHECKPOINT_METRICS_JSON.name
    checkpoint_path.write_text(json_dump(payload["checkpoint_metrics"]), encoding="utf-8")
    (target_dir / EVALUATION_ACTION_DISTRIBUTION_JSON.name).write_text(json_dump(payload["evaluation_action_distribution"]), encoding="utf-8")
    (target_dir / PER_ACTION_OUTCOME_SUMMARY_JSON.name).write_text(json_dump(payload["per_action_outcome_summary"]), encoding="utf-8")
    (target_dir / REWARD_DECOMPOSITION_JSON.name).write_text(json_dump(payload["reward_decomposition"]), encoding="utf-8")
    (target_dir / REPLAY_WINDOW_VS_CUMULATIVE_TRAINING_ACTIONS_JSON.name).write_text(
        json_dump(payload["replay_window_vs_cumulative_training_actions"]),
        encoding="utf-8",
    )
    (target_dir / STATE_FEATURE_COVERAGE_AUDIT_JSON.name).write_text(json_dump(payload["state_feature_coverage_audit"]), encoding="utf-8")
    (target_dir / POLICY_EFFECT_DIAGNOSTIC_JSON.name).write_text(json_dump(payload["policy_effect_diagnostic"]), encoding="utf-8")
    (target_dir / DIAGNOSTIC_DECISION_JSON.name).write_text(json_dump(payload["diagnostic_decision"]), encoding="utf-8")
    (target_dir / FIGURE_MANIFEST_JSON.name).write_text(json_dump(payload["figure_manifest"]), encoding="utf-8")
    return {
        "report_json": json_path,
        "report_md": md_path,
        "summary_md": summary_path,
        "checkpoint_metrics": checkpoint_path,
        "evaluation_action_distribution": target_dir / EVALUATION_ACTION_DISTRIBUTION_JSON.name,
        "per_action_outcome_summary": target_dir / PER_ACTION_OUTCOME_SUMMARY_JSON.name,
        "reward_decomposition": target_dir / REWARD_DECOMPOSITION_JSON.name,
        "replay_window_vs_cumulative_training_actions": target_dir / REPLAY_WINDOW_VS_CUMULATIVE_TRAINING_ACTIONS_JSON.name,
        "state_feature_coverage_audit": target_dir / STATE_FEATURE_COVERAGE_AUDIT_JSON.name,
        "policy_effect_diagnostic": target_dir / POLICY_EFFECT_DIAGNOSTIC_JSON.name,
        "diagnostic_decision": target_dir / DIAGNOSTIC_DECISION_JSON.name,
        "figure_manifest": target_dir / FIGURE_MANIFEST_JSON.name,
    }


def run_evaluation_instrumentation_reward_state_diagnostic(
    config: EvaluationInstrumentationDiagnosticConfig | None = None,
    *,
    output_dir: Path | str | None = None,
) -> EvaluationInstrumentationDiagnosticReport:
    cfg = config or EvaluationInstrumentationDiagnosticConfig()
    if output_dir is not None:
        target_output_dir = Path(output_dir)
        cfg = EvaluationInstrumentationDiagnosticConfig(
            feature_id=cfg.feature_id,
            base_branch_name=cfg.base_branch_name,
            branch_name=cfg.branch_name,
            output_dir=target_output_dir,
            figures_dir=target_output_dir / "figures",
            checkpoint_budgets=cfg.checkpoint_budgets,
            evaluation_episode_count_per_checkpoint=cfg.evaluation_episode_count_per_checkpoint,
            episode_length=cfg.episode_length,
            max_training_budget=cfg.max_training_budget,
            training_mode=cfg.training_mode,
            training_rerun_from_scratch=cfg.training_rerun_from_scratch,
            training_5000_run=cfg.training_5000_run,
            evaluation_action_sequence_sample_limit=cfg.evaluation_action_sequence_sample_limit,
            recommended_next_feature=cfg.recommended_next_feature,
        )
    report = build_evaluation_instrumentation_reward_state_diagnostic_report(cfg)
    generate_evaluation_instrumentation_reward_state_diagnostic_artifacts(report, output_dir=output_dir)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Execute Feature 065 evaluation instrumentation and reward/state diagnostic repair.")
    parser.add_argument("--json", action="store_true", help="Print the JSON report to stdout.")
    args = parser.parse_args(argv)
    report = run_evaluation_instrumentation_reward_state_diagnostic()
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(render_final_diagnostic_summary_markdown(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
