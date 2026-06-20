from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import OUTPUT_DIR, REPORT_JSON, REPORT_MD, FINAL_COMPLETION_PATH_SUMMARY_MD
from .model import CompletionPathFeasibilityReport


def json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _compact_policy_result(policy_result: dict[str, Any]) -> dict[str, Any]:
    allowed_keys = {
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
        "policy_feasibility_summary",
        "sample_task_records",
        "candidate_policy_vertical_share",
        "raw_reward_event_count",
        "raw_reward_total",
        "raw_terminal_event_count",
    }
    return {key: value for key, value in policy_result.items() if key in allowed_keys}


def compact_completion_path_payload(payload: dict[str, Any]) -> dict[str, Any]:
    compact = json.loads(json.dumps(payload))
    task_summary = compact.get("task_feasibility_summary", {})
    if isinstance(task_summary, dict):
        task_summary.pop("records_by_task_key", None)
    policy_effect = compact.get("policy_effect_completion_feasibility", {})
    if isinstance(policy_effect, dict):
        policy_results = policy_effect.get("policy_results")
        if isinstance(policy_results, dict):
            policy_effect["policy_results"] = {name: _compact_policy_result(result) for name, result in policy_results.items()}
        policy_feasibility_summary = policy_effect.get("policy_feasibility_summary")
        if isinstance(policy_feasibility_summary, dict):
            for summary in policy_feasibility_summary.values():
                if isinstance(summary, dict):
                    summary.pop("runtime_event_audit", None)
                    summary.pop("sample_task_records", None)
    for checkpoint in compact.get("checkpoint_metrics", []):
        if isinstance(checkpoint, dict):
            checkpoint.pop("evaluation_policy_result", None)
            checkpoint.pop("training_state", None)
            policy_summary = checkpoint.get("policy_feasibility_summary")
            if isinstance(policy_summary, dict):
                policy_results = policy_summary.get("policy_results")
                if isinstance(policy_results, dict):
                    policy_summary["policy_results"] = {name: _compact_policy_result(result) for name, result in policy_results.items()}
    return compact


def _checkpoint_episode_count(checkpoint: dict[str, Any]) -> int:
    training_state = checkpoint.get("training_state", checkpoint)
    return int(checkpoint.get("cumulative_training_episode_count", training_state.get("cumulative_training_episode_count", 0)))


def _render_markdown(payload: dict[str, Any]) -> str:
    checkpoint_rows = [
        "| budget | cumulative episodes | decisions | completion | drop | pending | feasibility | terminal cov. | reward delta |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for checkpoint in payload["checkpoint_metrics"]:
        feasibility = checkpoint["task_feasibility_summary"]
        candidate_summary = checkpoint.get("candidate_policy_summary", {})
        checkpoint_rows.append(
                "| {training_budget} | {episodes} | {decisions} | {completed} | {dropped} | {pending} | {feasible_ratio:.3f} | {terminal_coverage:.3f} | {reward_delta:.1f} |".format(
                    training_budget=checkpoint["training_budget"],
                    episodes=_checkpoint_episode_count(checkpoint),
                decisions=checkpoint["action_count_total"],
                completed=candidate_summary.get("completed_count", 0),
                dropped=candidate_summary.get("dropped_count", 0),
                pending=candidate_summary.get("pending_count", 0),
                feasible_ratio=float(feasibility.get("feasible_task_ratio", 0.0)),
                terminal_coverage=float(candidate_summary.get("terminal_event_coverage_ratio", 0.0)),
                reward_delta=float(checkpoint.get("reward_reconciliation_after_terminal_repair", {}).get("raw_vs_canonical_reward_delta", 0.0)),
            )
        )
    sections = [
        "# Completion Path and Deadline Feasibility Repair",
        "",
        f"- feature_id: `{payload['feature_id']}`",
        f"- final_verdict: `{payload['final_verdict']}`",
        f"- diagnostic_decision: `{payload['diagnostic_decision']['recommended_next_action']}`",
        f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
        "",
        "## 1. Feature 067 Prerequisite Verification",
        json_dump(
            {
                "feature_067_prerequisite_verified": payload["feature_067_prerequisite_verified"],
                "prerequisite_tags": payload["prerequisite_tags_verified"],
                "prerequisite_artifacts": payload["prerequisite_artifacts"],
            }
        ).strip(),
        "",
        "## 2. Evaluation Coverage Classification",
        json_dump(payload["evaluation_coverage_classification"]).strip(),
        "",
        "## 3. Task Feasibility and Action-Path Feasibility",
        json_dump(
            {
                "task_feasibility_summary": payload["task_feasibility_summary"],
                "action_path_feasibility": payload["action_path_feasibility"],
            }
        ).strip(),
        "",
        "## 4. Runtime Event Path Audit",
        json_dump(payload["runtime_event_path_audit"]).strip(),
        "",
        "## 5. Completion Failure Classification",
        json_dump(payload["completion_failure_classification"]).strip(),
        "",
        "## 6. Policy-Effect Completion Feasibility",
        json_dump(payload["policy_effect_completion_feasibility"]).strip(),
        "",
        "## 7. 50 vs 100 Comparison",
        json_dump(payload["checkpoint_50_100_feasibility_comparison"]).strip(),
        "",
        "## 8. Why Completion Remains Zero",
        payload["explanation_of_completion_blocker"],
        "",
        "## 9. Whether Completion Is Genuinely Blocked",
        json_dump(
            {
                "all_tasks_infeasible_under_current_deadlines": payload["completion_failure_classification"]["root_cause"] == "all_tasks_infeasible_under_current_deadlines",
                "completion_path_changed": payload["checkpoint_50_100_feasibility_comparison"]["comparison_classification"] == "completion_path_changed",
            }
        ).strip(),
        "",
        "## 10. Candidate and Fixed Policy Feasibility",
        json_dump(payload["policy_effect_completion_feasibility"]["policy_feasibility_summary"]).strip(),
        "",
        "## 11. Whether Larger Training Is Still Blocked",
        json_dump({"remaining_blockers": payload["remaining_blockers"]}).strip(),
        "",
        "## 12. Recommended Next Repair",
        payload["recommended_next_feature"],
        "",
        "## 13. Final Verdict",
        payload["final_verdict"],
        "",
        "## Claim Safety",
        json_dump(payload["claim_safety_status"]).strip(),
        "",
        "## Figure Manifest",
        json_dump(payload["figure_manifest"]).strip(),
        "",
        "## Checkpoint Summary",
        "\n".join(checkpoint_rows),
    ]
    return "\n".join(sections) + "\n"


def render_final_completion_path_summary_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Final Completion Path Summary",
            "",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- diagnostic_decision: `{payload['diagnostic_decision']['recommended_next_action']}`",
            f"- root_cause: `{payload['completion_failure_classification']['root_cause']}`",
            f"- remaining_blockers: `{payload['remaining_blockers']}`",
            "",
            payload["explanation_of_completion_blocker"],
        ]
    ) + "\n"


def write_completion_path_feasibility_report(
    report: CompletionPathFeasibilityReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = compact_completion_path_payload(report.to_dict())
    json_path = target_dir / REPORT_JSON.name
    md_path = target_dir / REPORT_MD.name
    summary_path = target_dir / FINAL_COMPLETION_PATH_SUMMARY_MD.name
    json_path.write_text(json_dump(payload), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    summary_path.write_text(render_final_completion_path_summary_markdown(payload), encoding="utf-8")
    return json_path, md_path, summary_path
