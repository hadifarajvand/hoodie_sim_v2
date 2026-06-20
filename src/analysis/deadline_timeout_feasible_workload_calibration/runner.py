from __future__ import annotations

import argparse
from contextlib import contextmanager
from pathlib import Path
import tempfile
from typing import Any

from src.analysis.completion_path_deadline_feasibility_repair.feasibility import (
    build_action_path_feasibility as build_base_action_path_feasibility,
    build_task_feasibility_summary as build_base_task_feasibility_summary,
)
from src.analysis.completion_path_deadline_feasibility_repair.report import json_dump as base_json_dump
from src.analysis.terminal_lifecycle_accounting_50_100_comparison.repaired_terminal_evaluator import TerminalLifecycleTrainingSession

from .calibration import build_calibration_change_log, build_calibration_profile, patched_calibrated_environment
from .comparison import build_checkpoint_50_100_calibrated_comparison
from .config import (
    ALLOWED_DIAGNOSTIC_DECISIONS,
    ALLOWED_FINAL_VERDICTS,
    BASE_BRANCH_NAME,
    BRANCH_NAME,
    CALIBRATED_ACTION_PATH_FEASIBILITY_JSON,
    CALIBRATED_POLICY_EFFECT_COMPARISON_JSON,
    CALIBRATED_TASK_FEASIBILITY_SUMMARY_JSON,
    CALIBRATION_CHANGE_LOG_JSON,
    CHECKPOINT_50_100_CALIBRATED_COMPARISON_JSON,
    DIAGNOSTIC_DECISION_JSON,
    EVALUATION_EPISODE_COUNT,
    FEATURE_ID,
    FIGURES_DIR,
    FIGURE_MANIFEST_JSON,
    OUTPUT_DIR,
    PAPER_ALIGNED_CALIBRATED_METRICS_JSON,
    REPORT_JSON,
    REPORT_MD,
    RUNTIME_EVENT_PATH_AFTER_CALIBRATION_JSON,
    TRAINING_BUDGETS,
    TRAINING_MODE,
    TRAINING_RERUN_FROM_SCRATCH,
    TRAINING_5000_RUN,
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
)
from .feasibility import (
    build_before_after_feasibility_comparison,
    build_calibrated_action_path_feasibility,
    build_calibrated_task_feasibility_summary,
    load_before_baseline_metrics,
)
from .figures import generate_figures
from .model import DeadlineTimeoutCalibrationReport, FigureManifest
from .policy_probe import build_calibrated_policy_effect_comparison
from .report import compact_deadline_timeout_calibration_payload, json_dump, write_deadline_timeout_calibration_report
from src.analysis.completion_path_deadline_feasibility_repair.config import REPORT_JSON as BASELINE_FEATURE_068_REPORT_JSON

APPROVED_PREFIXES = (
    "artifacts/analysis/deadline-timeout-feasible-workload-calibration/",
    "docs/architecture/euls_phase28_deadline_timeout_feasible_workload_calibration.md",
    "specs/069-deadline-timeout-feasible-workload-calibration/",
    "src/analysis/deadline_timeout_feasible_workload_calibration/",
    "tests/unit/test_deadline_timeout_feasible_workload_calibration",
    "tests/integration/test_deadline_timeout_feasible_workload_calibration",
)

FORBIDDEN_PREFIXES = (
    "src/environment/reward_timing.py",
    "src/environment/replay_hash.py",
    "src/dal/",
    "src/policies/",
    "requirements",
    "pyproject.toml",
    "poetry.lock",
    "uv.lock",
    "AGENTS.md",
    ".specify/feature.json",
    "artifacts/analysis/completion-path-deadline-feasibility-repair/",
    "artifacts/analysis/terminal-lifecycle-accounting-50-100-comparison/",
    "artifacts/analysis/reward-emission-evaluation-metric-aggregation-repair/",
)


def _run_feature(config) -> dict[str, Any]:
    scope_guard_summary = build_scope_guard_summary(
        git_status_paths(),
        git_staged_paths(),
        git_diff_paths("068-completion-path-deadline-feasibility-repair"),
        APPROVED_PREFIXES,
        FORBIDDEN_PREFIXES,
    )
    claim_safety_status = build_claim_safety_status()
    prerequisite_artifacts = build_prerequisite_artifacts()
    feature_068_verified = prerequisite_artifacts["feature_068_report"]["verified"]
    prerequisite_tags = build_prerequisite_tags(
        scope_guard_summary["working_tree_paths_approved"],
        scope_guard_summary["staged_paths_approved"],
        scope_guard_summary["base_branch_head_diff_approved"],
    )
    if not feature_068_verified or not scope_guard_summary["working_tree_paths_approved"] or not scope_guard_summary["staged_paths_approved"] or not scope_guard_summary["base_branch_head_diff_approved"]:
        blockers = []
        if not feature_068_verified:
            blockers.append("feature_068_prerequisite_blocked")
        if not scope_guard_summary["working_tree_paths_approved"] or not scope_guard_summary["staged_paths_approved"] or not scope_guard_summary["base_branch_head_diff_approved"]:
            blockers.append("scope_drift_detected")
        return {
            "feature_id": FEATURE_ID,
            "base_branch_name": BASE_BRANCH_NAME,
            "branch_name": BRANCH_NAME,
            "calibration_profile_name": config.calibration_profile_name,
            "checkpoint_budgets": list(TRAINING_BUDGETS),
            "evaluation_episode_count": EVALUATION_EPISODE_COUNT,
            "episode_length": config.episode_length,
            "max_training_budget": config.max_training_budget,
            "training_mode": TRAINING_MODE,
            "training_rerun_from_scratch": TRAINING_RERUN_FROM_SCRATCH,
            "training_5000_run": TRAINING_5000_RUN,
            "calibration_change_log": build_calibration_change_log(),
            "before_overall_feasible_task_ratio": 0.0,
            "after_overall_feasible_task_ratio": 0.0,
            "before_completion_count": 0,
            "after_completion_count": 0,
            "before_drop_ratio": 0.0,
            "after_drop_ratio": 0.0,
            "before_deadline_violation_ratio": 0.0,
            "after_deadline_violation_ratio": 0.0,
            "before_action_path_feasibility": {},
            "after_action_path_feasibility": {},
            "calibrated_task_feasibility_summary": {},
            "calibrated_policy_effect_comparison": {},
            "checkpoint_50_100_calibrated_comparison": {},
            "paper_aligned_calibrated_metrics": {},
            "runtime_event_path_after_calibration": {},
            "diagnostic_decision": {
                "recommended_next_action": "blocked_due_to_unresolved_feasibility",
                "decision_reason": "Prerequisite validation failed before the calibration probe could run.",
                "evidence_notes": blockers,
            },
            "claim_safety_status": claim_safety_status,
            "figure_manifest": FigureManifest(figure_directory=str(FIGURES_DIR), figure_files=[], figure_count=0, figures_generated=False).to_dict(),
            "final_verdict": "deadline_timeout_feasible_workload_calibration_blocked",
            "remaining_blockers": blockers,
            "recommended_next_feature": config.recommended_next_feature,
            "calibration_is_nontrivial": False,
            "actions_have_different_feasibility": False,
            "deadline_constraints_still_active": False,
            "completion_count_nonzero": False,
            "drop_count_nonzero": False,
            "paper_reproduction_claim_made": False,
            "performance_superiority_claim_made": False,
            "baseline_superiority_claim_made": False,
            "reward_function_modified": False,
            "policy_modified": False,
            "state_representation_modified": False,
            "dal_modified": False,
            "dependencies_modified": False,
            "environment_or_generator_files_modified": False,
            "modified_files": [],
            "environment_semantics_modified": False,
            "calibration_profile_explicit": True,
            "scope_guard_summary": scope_guard_summary,
        }

    before_report = load_before_baseline_metrics(BASELINE_FEATURE_068_REPORT_JSON)
    calibration_profile = build_calibration_profile(Path(tempfile.gettempdir()) / config.calibration_trace_root_name)

    with patched_calibrated_environment(calibration_profile):
        session = TerminalLifecycleTrainingSession(config)
        checkpoint_results: list[dict[str, Any]] = []
        for budget in config.training_budgets:
            training_state = session.train_to_budget(int(budget))
            evaluation_result = session.candidate_policy_result(checkpoint_budget=int(budget))
            checkpoint_results.append(
                {
                    "training_budget": int(budget),
                    "training_state": training_state,
                    "evaluation_policy_result": evaluation_result,
                    "candidate_policy_summary": {},
                }
            )

        calibrated_policy_effect = build_calibrated_policy_effect_comparison(
            trainer=session.trainer,
            checkpoint_results=checkpoint_results,
            fixed_policy_seed=session.campaign_config.seed_bundle.evaluation_trace_generation_seed,
            evaluation_episode_count=config.evaluation_episode_count,
            episode_length=config.episode_length,
            evaluation_trace_bank_id=session.campaign_config.evaluation_trace_bank_id,
            record_sample_limit=config.record_sample_limit,
        )
        checkpoint_results[-1]["candidate_policy_summary"] = calibrated_policy_effect["candidate_policy_at_100"]
        checkpoint_results[0]["candidate_policy_summary"] = calibrated_policy_effect["candidate_policy_at_50"]
        task_summary = build_calibrated_task_feasibility_summary(
            checkpoint_results[-1]["evaluation_policy_result"]["task_records"],
            record_sample_limit=config.record_sample_limit,
        )
        action_path = build_calibrated_action_path_feasibility(task_summary)
        before_after_comparison = build_before_after_feasibility_comparison(
            before_report,
            task_summary,
            action_path,
            checkpoint_results[-1],
        )
        checkpoint_comparison = build_checkpoint_50_100_calibrated_comparison(checkpoint_results, calibrated_policy_effect, task_summary)
        runtime_event_path = {
            "overall": checkpoint_results[-1]["candidate_policy_summary"].get("completion_path_audit", {}),
            "by_policy": {name: summary.get("completion_path_audit", {}) for name, summary in calibrated_policy_effect["policy_summaries"].items()},
            "by_checkpoint": [
                {"training_budget": int(checkpoint["training_budget"]), **checkpoint["candidate_policy_summary"].get("completion_path_audit", {})}
                for checkpoint in checkpoint_results
            ],
        }
        paper_metrics = {
            "calibration_is_nontrivial": (
                0.2 <= float(task_summary.get("overall_feasible_task_ratio", 0.0)) <= 0.8
                and any(summary.get("completed_count", 0) > 0 for summary in calibrated_policy_effect["fixed_policy_summaries"].values())
                and any(summary.get("dropped_count", 0) > 0 for summary in calibrated_policy_effect["fixed_policy_summaries"].values())
            ),
            "actions_have_different_feasibility": len({float(task_summary.get("local_feasible_ratio", 0.0)), float(task_summary.get("horizontal_feasible_ratio", 0.0)), float(task_summary.get("vertical_feasible_ratio", 0.0))}) > 1,
            "deadline_constraints_still_active": float(checkpoint_results[-1]["candidate_policy_summary"].get("drop_ratio", 0.0)) > 0.0,
            "completion_count_nonzero": any(summary.get("completed_count", 0) > 0 for summary in calibrated_policy_effect["fixed_policy_summaries"].values()),
            "drop_count_nonzero": any(summary.get("dropped_count", 0) > 0 for summary in calibrated_policy_effect["fixed_policy_summaries"].values()),
            "policy_metrics": calibrated_policy_effect["policy_summaries"],
        }
        diagnostic_decision = build_diagnostic_decision(
            calibration_is_nontrivial=paper_metrics["calibration_is_nontrivial"],
            completion_count_nonzero=paper_metrics["completion_count_nonzero"],
            any_fixed_policy_completes=calibrated_policy_effect["any_fixed_policy_completes"],
            actions_have_different_feasibility=paper_metrics["actions_have_different_feasibility"],
            deadline_constraints_still_active=paper_metrics["deadline_constraints_still_active"],
        )
        final_verdict = "deadline_timeout_feasible_workload_calibration_ready" if diagnostic_decision["recommended_next_action"] in {"safe_to_proceed_to_state_representation_repair", "safe_to_proceed_to_reward_function_alignment"} else "deadline_timeout_feasible_workload_calibration_blocked"
        remaining_blockers = [] if final_verdict.endswith("ready") else ["calibration_profile_failed"]
        figure_manifest = FigureManifest(
            figure_directory=str(FIGURES_DIR),
            figure_files=generate_figures(
                {
                    "before_after_feasibility_comparison": before_after_comparison,
                    "after_action_path_feasibility": action_path,
                    "calibrated_policy_effect_comparison": calibrated_policy_effect,
                    "checkpoint_50_100_calibrated_comparison": checkpoint_comparison,
                    "calibrated_task_feasibility_summary": task_summary,
                },
                FIGURES_DIR,
            ),
            figure_count=5,
            figures_generated=True,
        ).to_dict()
        report = {
            "feature_id": FEATURE_ID,
            "base_branch_name": BASE_BRANCH_NAME,
            "branch_name": BRANCH_NAME,
            "calibration_profile_name": calibration_profile.profile_name,
            "checkpoint_budgets": list(TRAINING_BUDGETS),
            "evaluation_episode_count": EVALUATION_EPISODE_COUNT,
            "episode_length": config.episode_length,
            "max_training_budget": config.max_training_budget,
            "training_mode": TRAINING_MODE,
            "training_rerun_from_scratch": TRAINING_RERUN_FROM_SCRATCH,
            "training_5000_run": TRAINING_5000_RUN,
            "calibration_change_log": build_calibration_change_log(),
            "before_overall_feasible_task_ratio": float(before_report["task_feasibility_summary"].get("feasible_task_ratio", 0.0)),
            "after_overall_feasible_task_ratio": float(task_summary.get("overall_feasible_task_ratio", 0.0)),
            "before_completion_count": int(before_report["checkpoint_metrics"][-1]["candidate_policy_summary"].get("completed_count", 0)),
            "after_completion_count": int(checkpoint_results[-1]["candidate_policy_summary"].get("completed_count", 0)),
            "before_drop_ratio": float(before_report["checkpoint_metrics"][-1]["candidate_policy_summary"].get("drop_ratio", 0.0)),
            "after_drop_ratio": float(checkpoint_results[-1]["candidate_policy_summary"].get("drop_ratio", 0.0)),
            "before_deadline_violation_ratio": float(before_report["checkpoint_metrics"][-1]["candidate_policy_summary"].get("deadline_violation_ratio", 0.0)),
            "after_deadline_violation_ratio": float(checkpoint_results[-1]["candidate_policy_summary"].get("deadline_violation_ratio", 0.0)),
            "before_action_path_feasibility": before_report["action_path_feasibility"],
            "after_action_path_feasibility": action_path,
            "before_after_feasibility_comparison": before_after_comparison,
            "calibrated_task_feasibility_summary": task_summary,
            "calibrated_policy_effect_comparison": calibrated_policy_effect,
            "checkpoint_50_100_calibrated_comparison": checkpoint_comparison,
            "paper_aligned_calibrated_metrics": paper_metrics,
            "runtime_event_path_after_calibration": runtime_event_path,
            "diagnostic_decision": diagnostic_decision,
            "claim_safety_status": claim_safety_status,
            "figure_manifest": figure_manifest,
            "final_verdict": final_verdict,
            "remaining_blockers": remaining_blockers,
            "recommended_next_feature": config.recommended_next_feature,
            "calibration_is_nontrivial": paper_metrics["calibration_is_nontrivial"],
            "actions_have_different_feasibility": paper_metrics["actions_have_different_feasibility"],
            "deadline_constraints_still_active": paper_metrics["deadline_constraints_still_active"],
            "completion_count_nonzero": paper_metrics["completion_count_nonzero"],
            "drop_count_nonzero": paper_metrics["drop_count_nonzero"],
            "paper_reproduction_claim_made": False,
            "performance_superiority_claim_made": False,
            "baseline_superiority_claim_made": False,
            "reward_function_modified": False,
            "policy_modified": False,
            "state_representation_modified": False,
            "dal_modified": False,
            "dependencies_modified": False,
            "environment_or_generator_files_modified": False,
            "modified_files": [],
            "environment_semantics_modified": False,
            "calibration_profile_explicit": True,
            "scope_guard_summary": scope_guard_summary,
            "environment_modification_reason": None,
        }
        report["feature_068_prerequisite_verified"] = feature_068_verified
        report["prerequisite_artifacts"] = prerequisite_artifacts
        report["prerequisite_tags_verified"] = prerequisite_tags
        return compact_deadline_timeout_calibration_payload(report)


def build_deadline_timeout_feasible_workload_calibration_report(config: Any | None = None) -> dict[str, Any]:
    from .config import DeadlineTimeoutCalibrationConfig

    return _run_feature(config or DeadlineTimeoutCalibrationConfig())


def write_deadline_timeout_feasible_workload_calibration_report(report: dict[str, Any], output_dir: Path | str | None = None) -> tuple[Path, Path]:
    return write_deadline_timeout_calibration_report(report, output_dir)


def generate_deadline_timeout_feasible_workload_calibration_artifacts(config: Any | None = None) -> tuple[dict[str, Any], Path, Path]:
    report = build_deadline_timeout_feasible_workload_calibration_report(config)
    json_path, md_path = write_deadline_timeout_feasible_workload_calibration_report(report)
    return report, json_path, md_path


def run_deadline_timeout_feasible_workload_calibration(config: Any | None = None) -> dict[str, Any]:
    report, _, _ = generate_deadline_timeout_feasible_workload_calibration_artifacts(config)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = run_deadline_timeout_feasible_workload_calibration()
    if args.json:
        print(base_json_dump(report))
    else:
        print(report["final_verdict"])
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
