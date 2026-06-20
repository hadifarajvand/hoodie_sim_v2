from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import (
    BEFORE_AFTER_FEASIBILITY_COMPARISON_JSON,
    CALIBRATED_ACTION_PATH_FEASIBILITY_JSON,
    CALIBRATED_POLICY_EFFECT_COMPARISON_JSON,
    CALIBRATED_TASK_FEASIBILITY_SUMMARY_JSON,
    CALIBRATION_CHANGE_LOG_JSON,
    CHECKPOINT_50_100_CALIBRATED_COMPARISON_JSON,
    DIAGNOSTIC_DECISION_JSON,
    FINAL_CALIBRATION_SUMMARY_MD,
    FIGURE_MANIFEST_JSON,
    OUTPUT_DIR,
    PAPER_ALIGNED_CALIBRATED_METRICS_JSON,
    REPORT_JSON,
    REPORT_MD,
    RUNTIME_EVENT_PATH_AFTER_CALIBRATION_JSON,
)


def json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _compact_policy_result(policy_result: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "policy_name",
        "policy_kind",
        "checkpoint_budget",
        "evaluation_episode_count",
        "episode_length",
        "evaluation_trace_bank_id",
        "same_evaluation_trace_bank",
        "evaluation_action_distribution_source",
        "evaluation_action_distribution",
        "evaluation_decision_count",
        "decision_records_summary",
        "terminal_event_records",
        "reward_event_records",
        "evaluation_reward_summary",
        "raw_vs_canonical_terminal_reconciliation",
        "reward_reconciliation_after_terminal_repair",
        "completion_path_audit",
        "paper_aligned_diagnostic_metrics",
        "policy_summaries",
    }
    return {key: value for key, value in policy_result.items() if key in allowed}


def _before_after_comparison(payload: dict[str, Any]) -> dict[str, Any]:
    if "before_after_feasibility_comparison" in payload:
        return payload["before_after_feasibility_comparison"]
    return {
        "before_overall_feasible_task_ratio": payload.get("before_overall_feasible_task_ratio", 0.0),
        "after_overall_feasible_task_ratio": payload.get("after_overall_feasible_task_ratio", 0.0),
        "before_completion_count": payload.get("before_completion_count", 0),
        "after_completion_count": payload.get("after_completion_count", 0),
        "before_drop_ratio": payload.get("before_drop_ratio", 0.0),
        "after_drop_ratio": payload.get("after_drop_ratio", 0.0),
        "before_deadline_violation_ratio": payload.get("before_deadline_violation_ratio", 0.0),
        "after_deadline_violation_ratio": payload.get("after_deadline_violation_ratio", 0.0),
        "before_action_path_feasibility": payload.get("before_action_path_feasibility", {}),
        "after_action_path_feasibility": payload.get("after_action_path_feasibility", {}),
    }


def _figure_manifest(payload: dict[str, Any], target_dir: Path) -> dict[str, Any]:
    figure_manifest = payload.get("figure_manifest")
    if isinstance(figure_manifest, dict) and figure_manifest.get("figure_files"):
        return figure_manifest
    figure_dir = target_dir / "figures"
    figure_files = sorted(path.name for path in figure_dir.glob("*.png"))
    return {
        "figure_directory": str(figure_dir),
        "figure_files": figure_files,
        "figure_count": len(figure_files),
        "figures_generated": len(figure_files) == 5,
    }


def compact_deadline_timeout_calibration_payload(payload: dict[str, Any]) -> dict[str, Any]:
    compact = json.loads(json.dumps(payload))
    if "calibrated_task_feasibility_summary" in compact:
        compact["calibrated_task_feasibility_summary"].pop("records_by_task_key", None)
    if "calibrated_policy_effect_comparison" in compact:
        policy_effect = compact["calibrated_policy_effect_comparison"]
        if isinstance(policy_effect, dict):
            if "policy_results" in policy_effect and isinstance(policy_effect["policy_results"], dict):
                policy_effect["policy_results"] = {name: _compact_policy_result(result) for name, result in policy_effect["policy_results"].items()}
            if "policy_summaries" in policy_effect and isinstance(policy_effect["policy_summaries"], dict):
                for summary in policy_effect["policy_summaries"].values():
                    if isinstance(summary, dict):
                        summary.pop("task_records", None)
            if "fixed_policy_summaries" in policy_effect and isinstance(policy_effect["fixed_policy_summaries"], dict):
                for summary in policy_effect["fixed_policy_summaries"].values():
                    if isinstance(summary, dict):
                        summary.pop("task_records", None)
    if "before_after_feasibility_comparison" not in compact:
        compact["before_after_feasibility_comparison"] = _before_after_comparison(compact)
    if not isinstance(compact.get("figure_manifest"), dict) or not compact["figure_manifest"].get("figure_files"):
        compact["figure_manifest"] = _figure_manifest(compact, OUTPUT_DIR)
    return compact


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Deadline / Timeout Feasible Workload Calibration",
        "",
        f"- feature_id: `{payload['feature_id']}`",
        f"- final_verdict: `{payload['final_verdict']}`",
        f"- diagnostic_decision: `{payload['diagnostic_decision']['recommended_next_action']}`",
        f"- calibration_profile_name: `{payload['calibration_profile_name']}`",
        "",
        "## Calibration Summary",
        json_dump(
            {
                "before_overall_feasible_task_ratio": payload["before_overall_feasible_task_ratio"],
                "after_overall_feasible_task_ratio": payload["after_overall_feasible_task_ratio"],
                "before_completion_count": payload["before_completion_count"],
                "after_completion_count": payload["after_completion_count"],
                "before_drop_ratio": payload["before_drop_ratio"],
                "after_drop_ratio": payload["after_drop_ratio"],
                "before_deadline_violation_ratio": payload["before_deadline_violation_ratio"],
                "after_deadline_violation_ratio": payload["after_deadline_violation_ratio"],
            }
        ).strip(),
        "",
        "## Calibration Change Log",
        json_dump(payload["calibration_change_log"]).strip(),
        "",
        "## Before / After Comparison",
        json_dump(_before_after_comparison(payload)).strip(),
        "",
        "## Calibrated Policy Effect Comparison",
        json_dump(payload["calibrated_policy_effect_comparison"]).strip(),
        "",
        "## Paper-Aligned Metrics",
        json_dump(payload["paper_aligned_calibrated_metrics"]).strip(),
        "",
        "## Claim Safety",
        json_dump(payload["claim_safety_status"]).strip(),
        "",
        "## Figure Manifest",
        json_dump(payload["figure_manifest"]).strip(),
    ]
    return "\n".join(lines) + "\n"


def write_deadline_timeout_calibration_report(report: dict[str, Any], output_dir: Path | str | None = None) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = compact_deadline_timeout_calibration_payload(report)
    json_path = target_dir / REPORT_JSON.name
    md_path = target_dir / REPORT_MD.name
    json_path.write_text(json_dump(payload), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    (target_dir / CALIBRATION_CHANGE_LOG_JSON.name).write_text(json_dump(payload["calibration_change_log"]), encoding="utf-8")
    (target_dir / BEFORE_AFTER_FEASIBILITY_COMPARISON_JSON.name).write_text(json_dump(_before_after_comparison(payload)), encoding="utf-8")
    (target_dir / CALIBRATED_TASK_FEASIBILITY_SUMMARY_JSON.name).write_text(json_dump(payload["calibrated_task_feasibility_summary"]), encoding="utf-8")
    (target_dir / CALIBRATED_ACTION_PATH_FEASIBILITY_JSON.name).write_text(json_dump(payload["after_action_path_feasibility"]), encoding="utf-8")
    (target_dir / CALIBRATED_POLICY_EFFECT_COMPARISON_JSON.name).write_text(json_dump(payload["calibrated_policy_effect_comparison"]), encoding="utf-8")
    (target_dir / CHECKPOINT_50_100_CALIBRATED_COMPARISON_JSON.name).write_text(json_dump(payload["checkpoint_50_100_calibrated_comparison"]), encoding="utf-8")
    (target_dir / PAPER_ALIGNED_CALIBRATED_METRICS_JSON.name).write_text(json_dump(payload["paper_aligned_calibrated_metrics"]), encoding="utf-8")
    (target_dir / RUNTIME_EVENT_PATH_AFTER_CALIBRATION_JSON.name).write_text(json_dump(payload["runtime_event_path_after_calibration"]), encoding="utf-8")
    (target_dir / DIAGNOSTIC_DECISION_JSON.name).write_text(json_dump(payload["diagnostic_decision"]), encoding="utf-8")
    (target_dir / FINAL_CALIBRATION_SUMMARY_MD.name).write_text(
        "\n".join([
            "# Final Calibration Summary",
            "",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- diagnostic_decision: `{payload['diagnostic_decision']['recommended_next_action']}`",
            f"- calibration_profile_name: `{payload['calibration_profile_name']}`",
            f"- calibration_is_nontrivial: `{payload['calibration_is_nontrivial']}`",
            f"- completion_count_nonzero: `{payload['completion_count_nonzero']}`",
        ]) + "\n",
        encoding="utf-8",
    )
    (target_dir / FIGURE_MANIFEST_JSON.name).write_text(json_dump(_figure_manifest(payload, target_dir)), encoding="utf-8")
    return json_path, md_path
