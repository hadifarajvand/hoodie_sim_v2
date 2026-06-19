from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import OUTPUT_DIR, REPORT_JSON, REPORT_MD, STAGED_FINDINGS_MD
from .model import StagedTrainingBudgetLearningCurveReport


def json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _render_markdown(payload: dict[str, Any]) -> str:
    checkpoint_lines = [
        "| budget | cumulative episodes | eval episodes | optimizer steps | replay size | loss finite | comparison ready |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for checkpoint in payload["checkpoint_metrics"]:
        checkpoint_lines.append(
            "| {training_budget} | {cumulative_training_episode_count} | {evaluation_episode_count} | {optimizer_step_count} | {replay_size} | {loss_finite} | {comparison_ready} |".format(
                **checkpoint
            )
        )
    sections = [
        "# Staged Training Budget Learning Curve Report",
        "",
        f"- feature_id: `{payload['feature_id']}`",
        f"- final_verdict: `{payload['final_verdict']}`",
        f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
        "",
        "## Training Mode",
        json_dump(
            {
                "training_mode": payload["training_mode"],
                "checkpoint_budgets": payload["checkpoint_budgets"],
                "evaluation_episode_count_per_checkpoint": payload["evaluation_episode_count_per_checkpoint"],
                "episode_length": payload["episode_length"],
                "training_rerun_from_scratch": payload["training_rerun_from_scratch"],
                "total_max_training_budget": payload["total_max_training_budget"],
            }
        ).strip(),
        "",
        "## Checkpoint Metrics",
        "\n".join(checkpoint_lines),
        "",
        "## Comparison Readiness Summary",
        json_dump(payload["comparison_readiness_summary"]).strip(),
        "",
        "## Staged Comparative Table Summary",
        json_dump(payload["staged_comparative_table_summary"]).strip(),
        "",
        "## Figure Manifest",
        json_dump(payload["figure_manifest"]).strip(),
        "",
        "## Claim Safety Status",
        json_dump(payload["claim_safety_status"]).strip(),
        "",
        "## Remaining Blockers",
        json_dump(payload["remaining_blockers"]).strip(),
    ]
    return "\n".join(sections) + "\n"


def render_staged_findings_markdown(payload: dict[str, Any]) -> str:
    rows = payload.get("staged_comparative_table_summary", {}).get("rows", [])
    lines = [
        "# Staged Training Budget Learning Curve Findings",
        "",
        "This feature provides descriptive trend analysis only.",
        "It does not claim paper reproduction, performance superiority, or baseline superiority.",
        "",
        "| budget | eval reward | replay size | optimizer steps | comparison ready |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.get('training_budget')} | {row.get('evaluation_mean_reward')} | {row.get('replay_size')} | {row.get('optimizer_step_count')} | {row.get('comparison_ready')} |"
        )
    lines.extend(
        [
            "",
            f"- claim_safety_passed: `{payload['claim_safety_status'].get('claim_safety_passed')}`",
            f"- comparison_ready: `{payload['comparison_readiness_summary'].get('comparison_ready')}`",
        ]
    )
    return "\n".join(lines) + "\n"


def write_staged_training_budget_learning_curve_report(
    report: StagedTrainingBudgetLearningCurveReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = report.to_dict()
    json_path = target_dir / REPORT_JSON.name
    md_path = target_dir / REPORT_MD.name
    json_path.write_text(json_dump(payload), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    findings_path = target_dir / STAGED_FINDINGS_MD.name
    findings_path.write_text(render_staged_findings_markdown(payload), encoding="utf-8")
    return json_path, md_path
