from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import FINAL_DIAGNOSTIC_SUMMARY_MD, OUTPUT_DIR, REPORT_JSON, REPORT_MD
from .model import EvaluationInstrumentationDiagnosticReport


def json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _render_markdown(payload: dict[str, Any]) -> str:
    checkpoint_lines = [
        "| budget | cumulative episodes | eval decisions | optimizer steps | replay size | eval mean reward | comparison ready |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for checkpoint in payload["checkpoint_metrics"]:
        checkpoint_lines.append(
            "| {training_budget} | {cumulative_training_episode_count} | {evaluation_decision_count} | {optimizer_step_count} | {replay_size} | {mean_reward} | {comparison_ready} |".format(
                mean_reward=checkpoint["evaluation_reward_summary"]["mean_reward"],
                **checkpoint,
            )
        )
    sections = [
        "# Evaluation Instrumentation and Reward/State Diagnostic Report",
        "",
        f"- feature_id: `{payload['feature_id']}`",
        f"- final_verdict: `{payload['final_verdict']}`",
        f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
        f"- diagnostic_decision: `{payload['diagnostic_decision']['recommended_next_action']}`",
        "",
        "## Feature 064 Prerequisite Verification",
        json_dump(
            {
                "feature_064_prerequisite_verified": payload["feature_064_prerequisite_verified"],
                "prerequisite_tags_verified": payload["prerequisite_tags_verified"],
                "prerequisite_artifacts": payload["prerequisite_artifacts"],
            }
        ).strip(),
        "",
        "## Checkpoint Metrics",
        "\n".join(checkpoint_lines),
        "",
        "## Evaluation Action Logging Repair Result",
        json_dump(payload["evaluation_action_logging_repair_result"]).strip(),
        "",
        "## Replay Rolling-Window Interpretation Repair Result",
        json_dump(payload["replay_rolling_window_interpretation_repair_result"]).strip(),
        "",
        "## Per-Action Outcome Attribution Result",
        json_dump(payload["per_action_outcome_attribution_result"]).strip(),
        "",
        "## Reward Decomposition Result",
        json_dump(payload["reward_decomposition_result"]).strip(),
        "",
        "## State Feature Coverage Audit Result",
        json_dump(payload["state_feature_coverage_audit_result"]).strip(),
        "",
        "## Policy-Effect Diagnostic Result",
        json_dump(payload["policy_effect_diagnostic_result"]).strip(),
        "",
        "## Why Previous Outputs Were Static",
        json_dump(payload["explanation_of_previous_static_outputs"]).strip(),
        "",
        "## Instrumentation Verdict",
        json_dump(
            {
                "evaluation_reward_static_after_instrumentation": payload["evaluation_reward_static_after_instrumentation"],
                "evaluation_action_distribution_changed_by_budget": payload["evaluation_action_distribution_changed_by_budget"],
                "candidate_policy_vertical_collapse_in_evaluation": payload["candidate_policy_vertical_collapse_in_evaluation"],
                "candidate_policy_vertical_collapse_in_training_replay_window": payload["candidate_policy_vertical_collapse_in_training_replay_window"],
                "policy_affects_reward": payload["policy_affects_reward"],
                "policy_affects_terminal_outcomes": payload["policy_affects_terminal_outcomes"],
                "most_likely_root_cause": payload["most_likely_root_cause"],
            }
        ).strip(),
        "",
        "## Diagnostic Decision",
        json_dump(payload["diagnostic_decision"]).strip(),
        "",
        "## Claim Safety",
        json_dump(payload["claim_safety_status"]).strip(),
        "",
        "## Figure Manifest",
        json_dump(payload["figure_manifest"]).strip(),
        "",
        "## Remaining Blockers",
        json_dump(payload["remaining_blockers"]).strip(),
    ]
    return "\n".join(sections) + "\n"


def render_final_diagnostic_summary_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Final Diagnostic Summary",
            "",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- diagnostic_decision: `{payload['diagnostic_decision']['recommended_next_action']}`",
            f"- evaluation_reward_static_after_instrumentation: `{payload['evaluation_reward_static_after_instrumentation']}`",
            f"- candidate_policy_vertical_collapse_in_evaluation: `{payload['candidate_policy_vertical_collapse_in_evaluation']}`",
            f"- candidate_policy_vertical_collapse_in_training_replay_window: `{payload['candidate_policy_vertical_collapse_in_training_replay_window']}`",
            f"- policy_affects_reward: `{payload['policy_affects_reward']}`",
            f"- policy_affects_terminal_outcomes: `{payload['policy_affects_terminal_outcomes']}`",
            "",
            "## Recommended Next Feature",
            payload["recommended_next_feature"],
        ]
    ) + "\n"


def write_evaluation_instrumentation_reward_state_diagnostic_report(
    report: EvaluationInstrumentationDiagnosticReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = report.to_dict()
    json_path = target_dir / REPORT_JSON.name
    md_path = target_dir / REPORT_MD.name
    summary_path = target_dir / FINAL_DIAGNOSTIC_SUMMARY_MD.name
    json_path.write_text(json_dump(payload), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    summary_path.write_text(render_final_diagnostic_summary_markdown(payload), encoding="utf-8")
    return json_path, md_path, summary_path
