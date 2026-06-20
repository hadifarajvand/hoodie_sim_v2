from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import FINAL_REPAIR_SUMMARY_MD, OUTPUT_DIR, REPORT_JSON, REPORT_MD
from .model import RewardEmissionAggregationRepairReport


def json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _render_markdown(payload: dict[str, Any]) -> str:
    checkpoint_lines = [
        "| budget | cumulative episodes | eval decisions | optimizer steps | replay size | raw reward events | canonical reward tasks | reward reconciled |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for checkpoint in payload["checkpoint_metrics"]:
        reward_summary = checkpoint["evaluation_reward_summary"]
        raw_reward_event_count = reward_summary.get("raw_event_reward_count", reward_summary.get("raw_reward_emission_count", 0))
        checkpoint_lines.append(
            "| {training_budget} | {cumulative_training_episode_count} | {evaluation_decision_count} | {optimizer_step_count} | {replay_size} | {raw_reward_event_count} | {canonical_task_reward_count} | {reward_reconciled} |".format(
                raw_reward_event_count=raw_reward_event_count,
                canonical_task_reward_count=reward_summary.get("canonical_task_reward_count", 0),
                reward_reconciled=payload["raw_vs_canonical_reward_reconciliation"]["reward_reconciled"],
                **checkpoint,
            )
        )
    sections = [
        "# Reward Emission and Evaluation Metric Aggregation Repair",
        "",
        f"- feature_id: `{payload['feature_id']}`",
        f"- final_verdict: `{payload['final_verdict']}`",
        f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
        f"- diagnostic_decision: `{payload['diagnostic_decision']['recommended_next_action']}`",
        "",
        "## 1. Feature 065 Prerequisite Verification",
        json_dump(
            {
                "feature_065_prerequisite_verified": payload["feature_065_prerequisite_verified"],
                "prerequisite_tags_verified": payload["prerequisite_tags_verified"],
                "prerequisite_artifacts": payload["prerequisite_artifacts"],
            }
        ).strip(),
        "",
        "## 2. Evaluation Action Logging Repair Result",
        json_dump(payload["decision_records_summary"]).strip(),
        "",
        "## 3. Replay Rolling-Window Interpretation Repair Result",
        json_dump(
            {
                "training_mode": payload["training_mode"],
                "checkpoint_budgets": payload["checkpoint_budgets"],
                "replay_window_warning": True,
                "replay_window_capacity": 10_000,
            }
        ).strip(),
        "",
        "## 4. Per-Action Outcome Attribution Result",
        json_dump(payload["checkpoint_metrics"][-1]["per_action_outcome_summary"]).strip(),
        "",
        "## 5. Reward Decomposition Result",
        json_dump(payload["checkpoint_metrics"][-1]["reward_decomposition"]).strip(),
        "",
        "## 6. State Feature Coverage Audit Result",
        json_dump(payload.get("state_feature_coverage_audit", {"status": "not captured in this repair"})).strip(),
        "",
        "## 7. Policy-Effect Diagnostic Result",
        json_dump(payload["policy_effect_after_repair"]).strip(),
        "",
        "## 8. Why Previous Outputs Were Static",
        json_dump(payload["explanation_of_previous_static_outputs"]).strip(),
        "",
        "## 9. Whether Evaluation Reward Is Genuinely Static After Instrumentation",
        json_dump(
            {
                "evaluation_reward_static_after_instrumentation": payload["evaluation_reward_static_after_instrumentation"],
                "raw_event_reward_static_across_budget": payload["raw_event_reward_static_across_budget"],
                "canonical_task_reward_static_across_budget": payload["canonical_task_reward_static_across_budget"],
                "canonical_completion_rate_static_across_budget": payload["canonical_completion_rate_static_across_budget"],
                "canonical_drop_rate_static_across_budget": payload["canonical_drop_rate_static_across_budget"],
                "evaluation_action_distribution_static_across_budget": payload["evaluation_action_distribution_static_across_budget"],
            }
        ).strip(),
        "",
        "## 10. Whether Candidate Policy Collapses During Evaluation, Training, or Both",
        json_dump(
            {
                "candidate_policy_vertical_collapse_in_evaluation": payload["candidate_policy_vertical_collapse_in_evaluation"],
                "candidate_policy_vertical_collapse_in_training_replay_window": payload["candidate_policy_vertical_collapse_in_training_replay_window"],
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
        "## Checkpoint Metrics",
        "\n".join(checkpoint_lines),
        "",
        "## Raw vs Canonical Reward Reconciliation",
        json_dump(payload["raw_vs_canonical_reward_reconciliation"]).strip(),
        "",
        "## Paper-Aligned Diagnostic Metrics",
        json_dump(payload["paper_aligned_evaluation_metrics"]).strip(),
        "",
        "## Claim Safety",
        json_dump(payload["claim_safety_status"]).strip(),
        "",
        "## Figure Manifest",
        json_dump(payload["figure_manifest"]).strip(),
    ]
    return "\n".join(sections) + "\n"


def render_final_repair_summary_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Final Repair Summary",
            "",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- diagnostic_decision: `{payload['diagnostic_decision']['recommended_next_action']}`",
            f"- reward_reconciled: `{payload['raw_vs_canonical_reward_reconciliation']['reward_reconciled']}`",
            f"- raw_reward_event_recovery_blocked: `{payload['raw_reward_event_recovery_blocked']}`",
            f"- terminal_event_recovery_blocked: `{payload['terminal_event_recovery_blocked']}`",
            "",
            payload["explanation_of_previous_static_outputs"]["why_previous_outputs_were_identical_or_static"],
        ]
    ) + "\n"


def write_reward_emission_aggregation_repair_report(
    report: RewardEmissionAggregationRepairReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = report.to_dict()
    json_path = target_dir / REPORT_JSON.name
    md_path = target_dir / REPORT_MD.name
    summary_path = target_dir / FINAL_REPAIR_SUMMARY_MD.name
    json_path.write_text(json_dump(payload), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    summary_path.write_text(render_final_repair_summary_markdown(payload), encoding="utf-8")
    return json_path, md_path, summary_path
