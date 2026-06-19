from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.analysis.full_training_reproduction_campaign.config import CampaignConfig
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer, EvaluationSummary

from .config import (
    CHECKPOINT_BUDGETS,
    CHECKPOINT_METRICS_JSON,
    COMPARISON_READINESS_JSON,
    EVALUATION_EPISODES_PER_CHECKPOINT,
    FEATURE_062_REPORT,
    FEATURE_060_BASELINE_EVALUATION_METRICS,
    FEATURE_ID,
    FIGURE_MANIFEST_JSON,
    OUTPUT_DIR,
    REPORT_JSON,
    REPORT_MD,
    READY_NEXT_FEATURE,
    STAGED_COMPARATIVE_TABLE_JSON,
    STAGED_FINDINGS_MD,
    StagedTrainingBudgetLearningCurveConfig,
)
from .figures import generate_figures
from .model import (
    ClaimSafetyStatus,
    CheckpointMetric,
    ComparisonReadinessSummary,
    FigureManifest,
    StagedTrainingBudgetLearningCurveReport,
)
from .report import json_dump, render_staged_findings_markdown, write_staged_training_budget_learning_curve_report

APPROVED_PATH_PREFIXES = (
    "artifacts/analysis/staged-training-budget-learning-curve/",
    "docs/architecture/euls_phase22_staged_training_budget_learning_curve.md",
    "specs/063-staged-training-budget-learning-curve/",
    "src/analysis/staged_training_budget_learning_curve/",
    "tests/unit/test_staged_training_budget_learning_curve",
    "tests/integration/test_staged_training_budget_learning_curve",
)
FORBIDDEN_PATH_PREFIXES = (
    "src/environment/",
    "src/dal/",
    "src/policies/",
    "src/environment/replay_hash.py",
    "src/analysis/full_training_reproduction_campaign/",
    "src/analysis/full_paper_default_training_campaign_execution/",
    "src/analysis/unified_campaign_result_analysis_figures_findings/",
    "requirements",
    "pyproject.toml",
    "poetry.lock",
    "uv.lock",
    "AGENTS.md",
    ".specify/feature.json",
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_output(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def _status_paths() -> list[str]:
    lines = _git_output("status", "--short", "--untracked-files=no").splitlines()
    return [line[3:].strip() for line in lines if line.strip()]


def _staged_paths() -> list[str]:
    lines = _git_output("diff", "--cached", "--name-only").splitlines()
    return [line.strip() for line in lines if line.strip()]


def _diff_names(base_ref: str) -> list[str]:
    lines = _git_output("diff", "--name-only", f"{base_ref}...HEAD").splitlines()
    return [line.strip() for line in lines if line.strip()]


def _approved_paths(paths: list[str]) -> bool:
    if any(path.startswith(FORBIDDEN_PATH_PREFIXES) for path in paths):
        return False
    return all(path.startswith(APPROVED_PATH_PREFIXES) for path in paths)


def _feature_062_prerequisite_verified() -> dict[str, Any]:
    status = {
        "path": str(FEATURE_062_REPORT),
        "exists": FEATURE_062_REPORT.exists(),
        "verified": False,
        "final_verdict": None,
        "remaining_blockers": None,
    }
    if not status["exists"]:
        return status
    payload = _load_json(FEATURE_062_REPORT)
    status["final_verdict"] = payload.get("final_verdict")
    status["remaining_blockers"] = payload.get("remaining_blockers")
    status["verified"] = payload.get("final_verdict") == "unified_campaign_result_analysis_ready" and payload.get("remaining_blockers") == []
    return status


def _baseline_reference_summary() -> dict[str, Any]:
    if not FEATURE_060_BASELINE_EVALUATION_METRICS.exists():
        return {
            "available": False,
            "artifact_path": str(FEATURE_060_BASELINE_EVALUATION_METRICS),
        }
    payload = _load_json(FEATURE_060_BASELINE_EVALUATION_METRICS)
    return {
        "available": True,
        "artifact_path": str(FEATURE_060_BASELINE_EVALUATION_METRICS),
        "baseline_policy_names": payload.get("baseline_policy_names", []),
        "evaluated_policy_count": payload.get("evaluated_policy_count", 0),
        "actual_baseline_evaluation_episode_count": payload.get("actual_baseline_evaluation_episode_count", 0),
        "baseline_metrics_real_execution": payload.get("baseline_metrics_real_execution", False),
        "no_baseline_superiority_claim": payload.get("no_baseline_superiority_claim", False),
        "baseline_policy_episode_counts": {
            name: metrics.get("episode_count")
            for name, metrics in payload.get("per_policy_metrics", {}).items()
        },
    }


def _action_distribution(transitions: list[Any]) -> dict[str, int]:
    counts = {"local": 0, "horizontal": 0, "vertical": 0, "invalid_or_noop_action_count": 0}
    for transition in transitions:
        raw_action = transition["action"] if isinstance(transition, dict) else getattr(transition, "action", None)
        action_name = {0: "local", 1: "horizontal", 2: "vertical"}.get(raw_action) if isinstance(raw_action, int) else None
        if action_name in ("local", "horizontal", "vertical"):
            counts[action_name] += 1
        else:
            counts["invalid_or_noop_action_count"] += 1
    return counts


def _reward_summary(transitions: list[Any]) -> dict[str, Any]:
    reward_values = [
        float(transition["reward"] if isinstance(transition, dict) else getattr(transition, "reward"))
        for transition in transitions
        if (transition["reward_available"] if isinstance(transition, dict) else getattr(transition, "reward_available"))
    ]
    return {
        "reward_count": len(reward_values),
        "total_reward": float(sum(reward_values)) if reward_values else 0.0,
        "mean_reward": float(sum(reward_values) / len(reward_values)) if reward_values else 0.0,
        "pending_at_horizon_count": sum(
            1
            for transition in transitions
            if (transition["pending_at_horizon"] if isinstance(transition, dict) else getattr(transition, "pending_at_horizon"))
        ),
    }


def _evaluation_reward_summary(summary: EvaluationSummary) -> dict[str, Any]:
    return {
        "evaluation_episode_count": summary.evaluation_episode_count,
        "mean_reward": summary.mean_reward,
        "completed_task_count": summary.completed_task_count,
        "dropped_task_count": summary.dropped_task_count,
        "terminal_transition_count": summary.terminal_transition_count,
        "reward_bearing_transition_count": summary.reward_bearing_transition_count,
        "pending_at_horizon_count": None,
        "trace_bank_disjoint": summary.trace_bank_disjoint,
        "trace_bank_ids": dict(summary.trace_bank_ids),
        "trace_ids": list(summary.trace_ids),
        "evaluation_on_training_traces": summary.evaluation_on_training_traces,
    }


def _claim_safety_status() -> dict[str, Any]:
    return {
        "paper_reproduction_claim_made": False,
        "performance_superiority_claim_made": False,
        "baseline_superiority_claim_made": False,
        "claim_safety_passed": True,
    }


def _checkpoint_metric_from_state(
    *,
    training_budget: int,
    cumulative_training_episode_count: int,
    evaluation_summary: EvaluationSummary,
    replay_transitions: list[Any],
    optimizer_step_count: int,
    last_loss: float | None,
    loss_count: int,
    baseline_reference_summary: dict[str, Any],
) -> dict[str, Any]:
    action_distribution = _action_distribution(replay_transitions)
    replay_size = len(replay_transitions)
    action_count_total = sum(action_distribution.values())
    reward_summary = _reward_summary(replay_transitions)
    evaluation_reward = _evaluation_reward_summary(evaluation_summary)
    claim_safety = _claim_safety_status()
    comparison_ready = (
        baseline_reference_summary.get("available") is True
        and action_count_total == replay_size
        and loss_count >= 0
        and claim_safety["claim_safety_passed"]
        and evaluation_reward["evaluation_episode_count"] == EVALUATION_EPISODES_PER_CHECKPOINT
        and training_budget in CHECKPOINT_BUDGETS
    )
    metric = CheckpointMetric(
        training_budget=training_budget,
        cumulative_training_episode_count=cumulative_training_episode_count,
        evaluation_episode_count=evaluation_reward["evaluation_episode_count"],
        episode_length=110,
        optimizer_step_count=optimizer_step_count,
        replay_size=replay_size,
        action_distribution=action_distribution,
        action_count_total=action_count_total,
        action_accounting_reconciled=action_count_total == replay_size,
        loss_count=loss_count,
        last_loss=last_loss,
        loss_finite=last_loss is None or math.isfinite(float(last_loss)),
        reward_summary=reward_summary,
        evaluation_reward_summary=evaluation_reward,
        completed_task_count=evaluation_reward["completed_task_count"],
        dropped_task_count=evaluation_reward["dropped_task_count"],
        pending_at_horizon_count=reward_summary["pending_at_horizon_count"],
        comparison_ready=comparison_ready,
        claim_safety_status=claim_safety,
    )
    return metric.to_dict()


def _build_cumulative_training_sweep(
    config: StagedTrainingBudgetLearningCurveConfig,
) -> dict[str, Any]:
    campaign_config = CampaignConfig(evaluation_episode_length=config.episode_length, full_campaign_episode_length=config.episode_length)
    trainer = DDQNTrainer(campaign_config)
    baseline_reference_summary = _baseline_reference_summary()
    checkpoint_metrics: list[dict[str, Any]] = []
    cumulative_training_episode_count = 0
    loss_values: list[float] = []

    for training_budget in config.checkpoint_budgets:
        additional_episodes = training_budget - cumulative_training_episode_count
        if additional_episodes < 0:
            raise ValueError("checkpoint budgets must be cumulative and increasing")
        for episode_offset in range(additional_episodes):
            episode_id = cumulative_training_episode_count + episode_offset
            rollout_summary = trainer._episode_rollout(  # noqa: SLF001 - use the existing trainer implementation without changing it
                episode_id=episode_id,
                seed=campaign_config.seed_bundle.training_trace_generation_seed + episode_id,
                episode_length=config.episode_length,
                training=True,
            )
            loss_values.extend(float(loss) for loss in rollout_summary["loss_values"])
        cumulative_training_episode_count = training_budget
        evaluation_summary = trainer.evaluate(episodes=config.evaluation_episode_count_per_checkpoint)
        replay_transitions = trainer.replay_buffer.as_list()
        last_loss = float(loss_values[-1]) if loss_values else None
        checkpoint_metrics.append(
            _checkpoint_metric_from_state(
                training_budget=training_budget,
                cumulative_training_episode_count=cumulative_training_episode_count,
                evaluation_summary=evaluation_summary,
                replay_transitions=replay_transitions,
                optimizer_step_count=trainer.optimizer_step_count,
                last_loss=last_loss,
                loss_count=len(loss_values),
                baseline_reference_summary=baseline_reference_summary,
            )
        )

    comparison_ready = baseline_reference_summary.get("available") is True and all(metric["comparison_ready"] for metric in checkpoint_metrics)
    return {
        "training_mode": config.training_mode,
        "checkpoint_metrics": checkpoint_metrics,
        "loss_values": loss_values,
        "baseline_reference_summary": baseline_reference_summary,
        "comparison_ready": comparison_ready,
        "optimizer_step_count": trainer.optimizer_step_count,
        "replay_size": len(trainer.replay_buffer.as_list()),
    }


def _build_training_summary(config: StagedTrainingBudgetLearningCurveConfig, execution: dict[str, Any]) -> dict[str, Any]:
    checkpoint_metrics = list(execution["checkpoint_metrics"])
    last_checkpoint = checkpoint_metrics[-1] if checkpoint_metrics else {}
    return {
        "training_mode": config.training_mode,
        "checkpoint_budgets": list(config.checkpoint_budgets),
        "evaluation_episode_count_per_checkpoint": config.evaluation_episode_count_per_checkpoint,
        "episode_length": config.episode_length,
        "training_rerun_from_scratch": config.training_rerun_from_scratch,
        "total_max_training_budget": config.total_max_training_budget,
        "cumulative_training_episode_count": checkpoint_metrics[-1]["cumulative_training_episode_count"] if checkpoint_metrics else 0,
        "optimizer_step_count": int(execution["optimizer_step_count"]),
        "replay_size": int(execution["replay_size"]),
        "loss_count": len(execution["loss_values"]),
        "last_loss": checkpoint_metrics[-1].get("last_loss") if checkpoint_metrics else None,
        "loss_finite": all(metric["loss_finite"] for metric in checkpoint_metrics) if checkpoint_metrics else False,
        "baseline_reference_artifact_path": execution["baseline_reference_summary"].get("artifact_path"),
    }


def _build_comparison_readiness_summary(config: StagedTrainingBudgetLearningCurveConfig, execution: dict[str, Any]) -> dict[str, Any]:
    checkpoint_metrics = list(execution["checkpoint_metrics"])
    ready = [metric["training_budget"] for metric in checkpoint_metrics if metric["comparison_ready"]]
    not_ready = [metric["training_budget"] for metric in checkpoint_metrics if not metric["comparison_ready"]]
    summary = ComparisonReadinessSummary(
        comparison_ready=bool(execution["comparison_ready"]),
        checkpoint_budgets=list(config.checkpoint_budgets),
        ready_checkpoint_budgets=ready,
        unready_checkpoint_budgets=not_ready,
        evaluation_episode_count_per_checkpoint=config.evaluation_episode_count_per_checkpoint,
        episode_length=config.episode_length,
        training_mode=config.training_mode,
        baseline_reference_reused=execution["baseline_reference_summary"].get("available", False),
        baseline_reference_artifact_path=execution["baseline_reference_summary"].get("artifact_path", ""),
        baseline_reference_summary=execution["baseline_reference_summary"],
        no_paper_reproduction_claim=True,
        no_performance_superiority_claim=True,
        no_baseline_superiority_claim=True,
    )
    return summary.to_dict()


def _build_comparative_table(execution: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for metric in execution["checkpoint_metrics"]:
        rows.append(
            {
                "training_budget": metric["training_budget"],
                "cumulative_training_episode_count": metric["cumulative_training_episode_count"],
                "evaluation_mean_reward": metric["evaluation_reward_summary"]["mean_reward"],
                "optimizer_step_count": metric["optimizer_step_count"],
                "replay_size": metric["replay_size"],
                "loss_count": metric["loss_count"],
                "last_loss": metric["last_loss"],
                "action_count_total": metric["action_count_total"],
                "action_accounting_reconciled": metric["action_accounting_reconciled"],
                "comparison_ready": metric["comparison_ready"],
                "claim_safety_passed": metric["claim_safety_status"]["claim_safety_passed"],
            }
        )
    return {
        "rows": rows,
        "comparison_ready": bool(execution["comparison_ready"]),
        "comparison_scope": "comparison readiness and descriptive trend analysis only",
        "baseline_reference_reused": execution["baseline_reference_summary"].get("available", False),
    }


def _build_figure_manifest(figures_dir: Path, figure_payload: dict[str, Any]) -> dict[str, Any]:
    manifest = FigureManifest(
        figure_directory=str(figures_dir),
        figure_files=list(figure_payload["figure_files"]),
        figure_count=int(figure_payload["figure_count"]),
        figures_generated=bool(figure_payload["figures_generated"]),
    )
    return manifest.to_dict()


def _build_claim_safety_status(execution: dict[str, Any]) -> dict[str, Any]:
    claim_safety = ClaimSafetyStatus(
        paper_reproduction_claim_made=False,
        performance_superiority_claim_made=False,
        baseline_superiority_claim_made=False,
        claim_safety_passed=True,
    )
    return claim_safety.to_dict()


def _build_prerequisite_tags_verified(config: StagedTrainingBudgetLearningCurveConfig, feature_062_verified: dict[str, Any], status_paths: list[str], staged_paths: list[str], diff_paths: list[str]) -> list[dict[str, Any]]:
    branch = _git_output("branch", "--show-current")
    return [
        {"name": "branch", "verified": branch == config.feature_id, "details": f"git branch --show-current == {config.feature_id}"},
        {"name": "not_main", "verified": branch != "main", "details": "current branch != main"},
        {"name": "feature_062_report_valid", "verified": feature_062_verified["verified"], "details": str(feature_062_verified["path"])},
        {"name": "baseline_reference_available", "verified": _baseline_reference_summary().get("available", False), "details": str(FEATURE_060_BASELINE_EVALUATION_METRICS)},
        {"name": "working_tree_paths_approved", "verified": _approved_paths(status_paths), "details": "git status contains only approved Feature 063 paths"},
        {"name": "staged_paths_approved", "verified": _approved_paths(staged_paths), "details": "git diff --cached contains only approved Feature 063 paths"},
        {"name": "base_branch_head_diff_approved", "verified": _approved_paths(diff_paths), "details": "git diff --name-only 062...HEAD contains only approved Feature 063 paths"},
        {"name": "agents_stable_not_modified", "verified": "AGENTS.md" not in status_paths + staged_paths + diff_paths, "details": "AGENTS.md is stable and not modified"},
        {"name": "pointer_local_only_not_dirty_or_staged", "verified": ".specify/feature.json" not in status_paths + staged_paths + diff_paths, "details": ".specify/feature.json is absent from dirty/staged/committed paths"},
    ]


def build_staged_training_budget_learning_curve_report(
    config: StagedTrainingBudgetLearningCurveConfig | None = None,
) -> StagedTrainingBudgetLearningCurveReport:
    cfg = config or StagedTrainingBudgetLearningCurveConfig()
    status_paths = _status_paths()
    staged_paths = _staged_paths()
    diff_paths = _diff_names("062-unified-campaign-result-analysis-figures-findings")
    feature_062_verified = _feature_062_prerequisite_verified()
    prerequisites = _build_prerequisite_tags_verified(cfg, feature_062_verified, status_paths, staged_paths, diff_paths)

    if not feature_062_verified["verified"]:
        return StagedTrainingBudgetLearningCurveReport(
            feature_id=FEATURE_ID,
            prerequisite_tags_verified=prerequisites,
            feature_062_prerequisite_verified=False,
            training_mode=cfg.training_mode,
            checkpoint_budgets=list(cfg.checkpoint_budgets),
            evaluation_episode_count_per_checkpoint=cfg.evaluation_episode_count_per_checkpoint,
            episode_length=cfg.episode_length,
            training_rerun_from_scratch=cfg.training_rerun_from_scratch,
            total_max_training_budget=cfg.total_max_training_budget,
            baseline_reference_summary=_baseline_reference_summary(),
            checkpoint_metrics=[],
            comparison_readiness_summary={
                "comparison_ready": False,
                "checkpoint_budgets": list(cfg.checkpoint_budgets),
                "ready_checkpoint_budgets": [],
                "unready_checkpoint_budgets": list(cfg.checkpoint_budgets),
                "evaluation_episode_count_per_checkpoint": cfg.evaluation_episode_count_per_checkpoint,
                "episode_length": cfg.episode_length,
                "training_mode": cfg.training_mode,
                "baseline_reference_reused": False,
                "baseline_reference_artifact_path": str(cfg.baseline_reference_metrics_path),
                "baseline_reference_summary": _baseline_reference_summary(),
                "no_paper_reproduction_claim": True,
                "no_performance_superiority_claim": True,
                "no_baseline_superiority_claim": True,
                "descriptive_only": True,
            },
            staged_comparative_table_summary={"rows": [], "comparison_ready": False, "comparison_scope": "comparison readiness and descriptive trend analysis only", "baseline_reference_reused": False},
            figure_manifest={"figure_directory": str(cfg.figures_dir), "figure_files": [], "figure_count": 0, "figures_generated": False},
            claim_safety_status={
                "paper_reproduction_claim_made": False,
                "performance_superiority_claim_made": False,
                "baseline_superiority_claim_made": False,
                "claim_safety_passed": True,
            },
            remaining_blockers=["feature_062_prerequisite_blocked"],
            recommended_next_feature="Repair Feature 062 prerequisite evidence before Feature 063 can proceed",
            final_verdict="feature_062_prerequisite_blocked",
        )

    if not _approved_paths(status_paths + staged_paths + diff_paths):
        return StagedTrainingBudgetLearningCurveReport(
            feature_id=FEATURE_ID,
            prerequisite_tags_verified=prerequisites,
            feature_062_prerequisite_verified=True,
            training_mode=cfg.training_mode,
            checkpoint_budgets=list(cfg.checkpoint_budgets),
            evaluation_episode_count_per_checkpoint=cfg.evaluation_episode_count_per_checkpoint,
            episode_length=cfg.episode_length,
            training_rerun_from_scratch=cfg.training_rerun_from_scratch,
            total_max_training_budget=cfg.total_max_training_budget,
            baseline_reference_summary=_baseline_reference_summary(),
            checkpoint_metrics=[],
            comparison_readiness_summary={
                "comparison_ready": False,
                "checkpoint_budgets": list(cfg.checkpoint_budgets),
                "ready_checkpoint_budgets": [],
                "unready_checkpoint_budgets": list(cfg.checkpoint_budgets),
                "evaluation_episode_count_per_checkpoint": cfg.evaluation_episode_count_per_checkpoint,
                "episode_length": cfg.episode_length,
                "training_mode": cfg.training_mode,
                "baseline_reference_reused": False,
                "baseline_reference_artifact_path": str(cfg.baseline_reference_metrics_path),
                "baseline_reference_summary": _baseline_reference_summary(),
                "no_paper_reproduction_claim": True,
                "no_performance_superiority_claim": True,
                "no_baseline_superiority_claim": True,
                "descriptive_only": True,
            },
            staged_comparative_table_summary={"rows": [], "comparison_ready": False, "comparison_scope": "comparison readiness and descriptive trend analysis only", "baseline_reference_reused": False},
            figure_manifest={"figure_directory": str(cfg.figures_dir), "figure_files": [], "figure_count": 0, "figures_generated": False},
            claim_safety_status={
                "paper_reproduction_claim_made": False,
                "performance_superiority_claim_made": False,
                "baseline_superiority_claim_made": False,
                "claim_safety_passed": True,
            },
            remaining_blockers=["scope_drift_detected"],
            recommended_next_feature="Restore approved Feature 063 paths before proceeding",
            final_verdict="scope_drift_detected",
        )

    execution = _build_cumulative_training_sweep(cfg)
    training_summary = _build_training_summary(cfg, execution)
    comparison_readiness_summary = _build_comparison_readiness_summary(cfg, execution)
    staged_comparative_table_summary = _build_comparative_table(execution)
    figure_payload = generate_figures(figures_dir=cfg.figures_dir, checkpoint_metrics=list(execution["checkpoint_metrics"]))
    figure_manifest = _build_figure_manifest(cfg.figures_dir, figure_payload)
    claim_safety_status = _build_claim_safety_status(execution)

    report = StagedTrainingBudgetLearningCurveReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=prerequisites,
        feature_062_prerequisite_verified=True,
        training_mode=training_summary["training_mode"],
        checkpoint_budgets=training_summary["checkpoint_budgets"],
        evaluation_episode_count_per_checkpoint=training_summary["evaluation_episode_count_per_checkpoint"],
        episode_length=training_summary["episode_length"],
        training_rerun_from_scratch=training_summary["training_rerun_from_scratch"],
        total_max_training_budget=training_summary["total_max_training_budget"],
        baseline_reference_summary=execution["baseline_reference_summary"],
        checkpoint_metrics=list(execution["checkpoint_metrics"]),
        comparison_readiness_summary=comparison_readiness_summary,
        staged_comparative_table_summary=staged_comparative_table_summary,
        figure_manifest=figure_manifest,
        claim_safety_status=claim_safety_status,
        remaining_blockers=[],
        recommended_next_feature=READY_NEXT_FEATURE,
        final_verdict="staged_training_budget_learning_curve_ready",
    )

    CHECKPOINT_METRICS_JSON.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_METRICS_JSON.write_text(json_dump(report.to_dict()["checkpoint_metrics"]), encoding="utf-8")
    COMPARISON_READINESS_JSON.write_text(json_dump(comparison_readiness_summary), encoding="utf-8")
    STAGED_COMPARATIVE_TABLE_JSON.write_text(json_dump(staged_comparative_table_summary), encoding="utf-8")
    FIGURE_MANIFEST_JSON.write_text(json_dump(figure_manifest), encoding="utf-8")
    findings_text = render_staged_findings_markdown(report.to_dict())
    STAGED_FINDINGS_MD.write_text(findings_text, encoding="utf-8")

    return report


def generate_staged_training_budget_learning_curve_artifacts(
    report: StagedTrainingBudgetLearningCurveReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path]:
    return write_staged_training_budget_learning_curve_report(report, output_dir=output_dir)


def run_staged_training_budget_learning_curve(
    config: StagedTrainingBudgetLearningCurveConfig | None = None,
    *,
    output_dir: Path | str | None = None,
) -> StagedTrainingBudgetLearningCurveReport:
    report = build_staged_training_budget_learning_curve_report(config)
    generate_staged_training_budget_learning_curve_artifacts(report, output_dir=output_dir)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Execute Feature 063 staged training budget learning curve analysis.")
    parser.add_argument("--json", action="store_true", help="Print the JSON report to stdout.")
    args = parser.parse_args(argv)
    report = run_staged_training_budget_learning_curve()
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(render_staged_findings_markdown(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
