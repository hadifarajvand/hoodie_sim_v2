from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from .action_diversity import build_action_path_diversity
from .comparison import build_before_after_consistency_comparison, build_consistent_50_100_comparison
from .config import (
    ALLOWED_DIAGNOSTIC_DECISIONS,
    ALLOWED_FINAL_VERDICTS,
    BASE_BRANCH_NAME,
    BRANCH_NAME,
    EVALUATION_EPISODE_COUNT,
    FEATURE_ID,
    FIGURES_DIR,
    FIGURE_MANIFEST_JSON,
    OUTPUT_DIR,
    REPORT_JSON,
    REPORT_MD,
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
    load_json,
    APPROVED_PREFIXES,
    FORBIDDEN_PREFIXES,
)
from .figures import generate_figures
from .policy_probe import build_consistent_policy_effect_comparison
from .reconciliation import build_policy_metric_consistency, build_reward_terminal_reconciliation_fix
from .report import json_dump, write_calibration_metric_consistency_report
from .universe import build_metric_universe_definitions, load_feature_069_compact_report, load_feature_069_raw_report


def _strip_repaired_records(policy_result: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in policy_result.items() if key != "repaired_task_records"}


def _build_policy_metric_consistency_checks(policy_effect: dict[str, Any]) -> dict[str, Any]:
    return {
        "metric_universes": build_metric_universe_definitions(),
        "by_policy": {name: dict(metrics) for name, metrics in policy_effect["policy_results"].items()},
        "all_reward_reconciled": all(metrics["reward_reconciled"] for metrics in policy_effect["policy_results"].values()),
        "all_terminal_reconciled": all(metrics["terminal_reconciled"] for metrics in policy_effect["policy_results"].values()),
        "max_raw_vs_canonical_reward_delta": max(abs(float(metrics["raw_vs_canonical_reward_delta"])) for metrics in policy_effect["policy_results"].values()),
        "any_fixed_policy_completes": bool(policy_effect["any_fixed_policy_completes"]),
    }


def build_calibration_metric_consistency_reconciliation_report(config: Any | None = None) -> dict[str, Any]:
    from .config import CalibrationMetricConsistencyConfig

    config = config or CalibrationMetricConsistencyConfig()
    scope_guard_summary = build_scope_guard_summary(
        git_status_paths(),
        git_staged_paths(),
        git_diff_paths("069-deadline-timeout-feasible-workload-calibration"),
        APPROVED_PREFIXES,
        FORBIDDEN_PREFIXES,
    )
    claim_safety_status = build_claim_safety_status()
    prerequisite_artifacts = build_prerequisite_artifacts()
    feature_069_verified = prerequisite_artifacts["feature_069_report"]["verified"]
    prerequisite_tags = build_prerequisite_tags(
        scope_guard_summary["working_tree_paths_approved"],
        scope_guard_summary["staged_paths_approved"],
        scope_guard_summary["base_branch_head_diff_approved"],
    )
    raw_payload = load_feature_069_raw_report(config=None)
    before_report = load_feature_069_compact_report(config.prior_report_path)
    candidate_100_internal = build_policy_metric_consistency(
        policy_name="candidate_policy_at_100",
        checkpoint_budget=100,
        policy_result=raw_payload["calibrated_policy_effect_comparison"]["policy_results"]["candidate_policy_at_100"],
        record_sample_limit=config.record_sample_limit,
    )
    policy_effect = build_consistent_policy_effect_comparison(raw_payload=raw_payload, record_sample_limit=config.record_sample_limit)
    candidate_100_task_records = candidate_100_internal["repaired_task_records"]
    action_path_diversity = build_action_path_diversity(candidate_100_task_records, checkpoint_budget=100)
    reward_terminal_reconciliation_fix = build_reward_terminal_reconciliation_fix(policy_effect["policy_results"])
    consistent_50_100_comparison = build_consistent_50_100_comparison(
        policy_effect,
        candidate_100_internal["task_feasibility_summary"],
    )
    before_after_consistency_comparison = build_before_after_consistency_comparison(
        before_report=before_report,
        after_policy_effect=policy_effect,
        after_action_diversity=action_path_diversity,
        after_reconciliation=reward_terminal_reconciliation_fix,
        after_policy_metrics=candidate_100_internal,
    )
    completion_count_nonzero = any(summary["completed_task_count"] > 0 for summary in policy_effect["policy_results"].values())
    diagnostic_decision = build_diagnostic_decision(
        reward_reconciliation_status=reward_terminal_reconciliation_fix["reward_reconciliation_status"],
        terminal_reconciled=reward_terminal_reconciliation_fix["terminal_reconciled"],
        actions_have_different_feasibility=action_path_diversity["actions_have_different_feasibility"],
        completion_count_nonzero=completion_count_nonzero,
        any_fixed_policy_completes=policy_effect["any_fixed_policy_completes"],
    )
    final_verdict = (
        "calibration_metric_consistency_reconciliation_ready"
        if diagnostic_decision["recommended_next_action"] == "safe_to_proceed_to_state_representation_repair"
        else "calibration_metric_consistency_reconciliation_blocked"
    )
    remaining_blockers = [] if final_verdict.endswith("ready") else ["metric_universe_mismatch_unresolved"]
    policy_metric_consistency_checks = _build_policy_metric_consistency_checks(policy_effect)
    report = {
        "feature_id": FEATURE_ID,
        "base_branch_name": BASE_BRANCH_NAME,
        "branch_name": BRANCH_NAME,
        "checkpoint_budgets": list(TRAINING_BUDGETS),
        "evaluation_episode_count": EVALUATION_EPISODE_COUNT,
        "episode_length": 110,
        "max_training_budget": 100,
        "training_mode": TRAINING_MODE,
        "training_rerun_from_scratch": TRAINING_RERUN_FROM_SCRATCH,
        "training_5000_run": TRAINING_5000_RUN,
        "calibration_profile_name": config.calibration_profile_name,
        "feature_069_prerequisite_verified": feature_069_verified,
        "prerequisite_artifacts": prerequisite_artifacts,
        "prerequisite_tags_verified": prerequisite_tags,
        "metric_universe_definitions": build_metric_universe_definitions(),
        "policy_metric_consistency_checks": policy_metric_consistency_checks,
        "reward_terminal_reconciliation_fix": reward_terminal_reconciliation_fix,
        "action_path_diversity_check": action_path_diversity,
        "consistent_policy_effect_comparison": {
            key: value
            for key, value in policy_effect.items()
            if key != "policy_results"
        }
        | {"policy_results": {name: _strip_repaired_records(result) for name, result in policy_effect["policy_results"].items()}},
        "consistent_50_100_comparison": consistent_50_100_comparison,
        "before_after_consistency_comparison": before_after_consistency_comparison,
        "diagnostic_decision": diagnostic_decision,
        "claim_safety_status": claim_safety_status,
        "figure_manifest": {},
        "final_verdict": final_verdict,
        "remaining_blockers": remaining_blockers,
        "recommended_next_feature": "State representation repair",
        "feature_069_analysis_code_modified": False,
        "modified_feature_069_files": [],
        "reason": "Consistency repair is derived from the raw 069 payload; no 069 analysis code was modified.",
        "paper_reproduction_claim_made": False,
        "performance_superiority_claim_made": False,
        "baseline_superiority_claim_made": False,
        "reward_function_modified": False,
        "policy_modified": False,
        "state_representation_modified": False,
        "dal_modified": False,
        "dependencies_modified": False,
    }
    figures = generate_figures(report, FIGURES_DIR)
    report["figure_manifest"] = {
        "figure_directory": str(FIGURES_DIR),
        "figure_files": [path.name for path in figures],
        "figure_count": len(figures),
        "figures_generated": len(figures) == 5,
    }
    report["policy_metric_consistency_checks"]["by_policy"] = {
        name: _strip_repaired_records(result) for name, result in policy_effect["policy_results"].items()
    }
    report["policy_metric_consistency_checks"]["metric_universes"] = build_metric_universe_definitions()
    report["consistent_policy_effect_comparison"]["policy_results"] = {
        name: _strip_repaired_records(result) for name, result in policy_effect["policy_results"].items()
    }
    report["consistent_policy_effect_comparison"]["policy_summaries"] = policy_effect["policy_summaries"]
    report["consistent_policy_effect_comparison"]["fixed_policy_summaries"] = policy_effect["fixed_policy_summaries"]
    report["consistent_policy_effect_comparison"]["candidate_policy_at_50"] = policy_effect["candidate_policy_at_50"]
    report["consistent_policy_effect_comparison"]["candidate_policy_at_100"] = policy_effect["candidate_policy_at_100"]
    report["consistent_policy_effect_comparison"]["any_fixed_policy_completes"] = policy_effect["any_fixed_policy_completes"]
    return report


def write_calibration_metric_consistency_reconciliation_report(report: dict[str, Any], output_dir: Path | str | None = None) -> tuple[Path, Path]:
    return write_calibration_metric_consistency_report(report, output_dir)


def run_calibration_metric_consistency_reconciliation_fix(config: Any | None = None) -> dict[str, Any]:
    report = build_calibration_metric_consistency_reconciliation_report(config)
    write_calibration_metric_consistency_report(report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = run_calibration_metric_consistency_reconciliation_fix()
    if args.json:
        print(json_dump(report))
    else:
        print(report["final_verdict"])
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
