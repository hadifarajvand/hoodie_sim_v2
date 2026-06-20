from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import FINAL_TERMINAL_LIFECYCLE_SUMMARY_MD, OUTPUT_DIR, REPORT_JSON, REPORT_MD
from .model import TerminalLifecycleComparisonReport


def json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _checkpoint_episode_count(checkpoint: dict[str, Any]) -> int:
    training_state = checkpoint.get("training_state", checkpoint)
    return int(
        checkpoint.get(
            "cumulative_training_episode_count",
            training_state.get("cumulative_training_episode_count", 0),
        )
    )


def _render_markdown(payload: dict[str, Any]) -> str:
    checkpoint_rows = [
        "| budget | cumulative episodes | decisions | terminal tasks | completed | dropped | raw terminal | canonical terminal | terminal coverage | raw reward delta |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for checkpoint in payload["checkpoint_metrics"]:
        eval_summary = checkpoint["evaluation_reward_summary"]
        recon = checkpoint["raw_vs_canonical_terminal_reconciliation"]
        checkpoint_rows.append(
            "| {training_budget} | {cumulative_training_episode_count} | {evaluation_decision_count} | {terminal_transition_count} | {completed_task_count} | {dropped_task_count} | {raw_terminal_event_count} | {canonical_terminal_task_count} | {terminal_event_coverage_ratio:.3f} | {raw_vs_canonical_reward_delta:.3f} |".format(
                training_budget=checkpoint["training_budget"],
                cumulative_training_episode_count=_checkpoint_episode_count(checkpoint),
                evaluation_decision_count=checkpoint["evaluation_decision_count"],
                terminal_transition_count=eval_summary["terminal_transition_count"],
                completed_task_count=eval_summary["completed_task_count"],
                dropped_task_count=eval_summary["dropped_task_count"],
                raw_terminal_event_count=recon["raw_terminal_event_count"],
                canonical_terminal_task_count=recon["canonical_terminal_task_count"],
                terminal_event_coverage_ratio=recon["terminal_event_coverage_ratio"],
                raw_vs_canonical_reward_delta=recon["raw_vs_canonical_reward_delta"],
            )
        )
    checkpoint_comparison = payload.get(
        "checkpoint_comparison",
        {
            "checkpoint_budgets": [checkpoint["training_budget"] for checkpoint in payload.get("checkpoint_metrics", [])],
            "by_checkpoint": [],
            "comparison": {},
        },
    )
    sections = [
        "# Terminal Lifecycle Accounting and 50/100 Comparison Repair",
        "",
        f"- feature_id: `{payload['feature_id']}`",
        f"- final_verdict: `{payload['final_verdict']}`",
        f"- diagnostic_decision: `{payload['diagnostic_decision']['recommended_next_action']}`",
        f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
        "",
        "## 1. Feature 066 Prerequisite Verification",
        json_dump(
            {
                "feature_066_prerequisite_verified": payload["feature_066_prerequisite_verified"],
                "prerequisite_tags": payload["prerequisite_tags_verified"],
                "prerequisite_artifacts": payload["prerequisite_artifacts"],
            }
        ).strip(),
        "",
        "## 2. Terminal Event Classification Result",
        json_dump(payload["terminal_event_classification"]).strip(),
        "",
        "## 3. Canonical Terminal Task Summary",
        json_dump(payload["canonical_terminal_task_summary"]).strip(),
        "",
        "## 4. Raw vs Canonical Terminal Reconciliation",
        json_dump(payload["raw_vs_canonical_terminal_reconciliation"]).strip(),
        "",
        "## 5. Reward Reconciliation After Terminal Repair",
        json_dump(payload["reward_reconciliation_after_terminal_repair"]).strip(),
        "",
        "## 6. Completion Path Audit",
        json_dump(payload["completion_path_audit"]).strip(),
        "",
        "## 7. Policy-Effect Diagnostic Result",
        json_dump(payload["policy_effect_50_100_after_terminal_repair"]).strip(),
        "",
        "## 8. Why the Previous Outputs Looked Static",
        json_dump(payload["explanation_of_previous_static_outputs"]).strip(),
        "",
        "## 9. Whether Terminal and Reward Metrics Are Still Static",
        json_dump(
            {
                "evaluation_reward_static_after_terminal_repair": payload["evaluation_reward_static_after_terminal_repair"],
                "evaluation_action_distribution_static_across_budget": payload["evaluation_action_distribution_static_across_budget"],
                "candidate_policy_vertical_collapse_in_evaluation": payload["candidate_policy_vertical_collapse_in_evaluation"],
                "candidate_policy_vertical_collapse_in_training_replay_window": payload["candidate_policy_vertical_collapse_in_training_replay_window"],
            }
        ).strip(),
        "",
        "## 10. Whether Candidate Policy Collapses During Evaluation, Training, or Both",
        json_dump(
            {
                "policy_affects_reward": payload["policy_affects_reward"],
                "policy_affects_terminal_outcomes": payload["policy_affects_terminal_outcomes"],
            }
        ).strip(),
        "",
        "## 11. Whether Larger Training Is Still Blocked",
        json_dump({"remaining_blockers": payload["remaining_blockers"]}).strip(),
        "",
        "## 12. Recommended Next Feature",
        payload["recommended_next_feature"],
        "",
        "## 13. Final Verdict",
        payload["final_verdict"],
        "",
        "## 50/100 Comparison",
        json_dump(checkpoint_comparison).strip(),
        "",
        "## Paper-Aligned Metrics",
        json_dump(payload["paper_aligned_50_100_metrics"]).strip(),
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


def render_final_terminal_lifecycle_summary_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Final Terminal Lifecycle Summary",
            "",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- diagnostic_decision: `{payload['diagnostic_decision']['recommended_next_action']}`",
            f"- terminal_reconciled: `{payload['raw_vs_canonical_terminal_reconciliation']['overall']['terminal_reconciled']}`",
            f"- reward_reconciled: `{payload['reward_reconciliation_after_terminal_repair']['overall']['reward_reconciled']}`",
            f"- remaining_blockers: `{payload['remaining_blockers']}`",
            "",
            payload["explanation_of_previous_static_outputs"]["why_previous_outputs_looked_static"],
        ]
    ) + "\n"


def write_terminal_lifecycle_comparison_report(
    report: TerminalLifecycleComparisonReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = report.to_dict()
    json_path = target_dir / REPORT_JSON.name
    md_path = target_dir / REPORT_MD.name
    summary_path = target_dir / FINAL_TERMINAL_LIFECYCLE_SUMMARY_MD.name
    json_path.write_text(json_dump(payload), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    summary_path.write_text(render_final_terminal_lifecycle_summary_markdown(payload), encoding="utf-8")
    return json_path, md_path, summary_path
