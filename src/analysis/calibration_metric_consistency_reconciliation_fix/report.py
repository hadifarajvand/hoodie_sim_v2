from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import (
    ACTION_PATH_DIVERSITY_CHECK_JSON,
    BEFORE_AFTER_CONSISTENCY_COMPARISON_JSON,
    CONSISTENT_50_100_COMPARISON_JSON,
    CONSISTENT_POLICY_EFFECT_COMPARISON_JSON,
    DIAGNOSTIC_DECISION_JSON,
    FIGURE_MANIFEST_JSON,
    FINAL_CONSISTENCY_SUMMARY_MD,
    METRIC_UNIVERSE_DEFINITIONS_JSON,
    OUTPUT_DIR,
    POLICY_METRIC_CONSISTENCY_CHECKS_JSON,
    REWARD_TERMINAL_RECONCILIATION_FIX_JSON,
    REPORT_JSON,
    REPORT_MD,
)


def json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _render_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Calibration Metric Consistency Reconciliation Fix",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- diagnostic_decision: `{payload['diagnostic_decision']['recommended_next_action']}`",
            f"- calibration_profile_name: `{payload['calibration_profile_name']}`",
            "",
            "## Metric Universes",
            json_dump(payload["metric_universe_definitions"]).strip(),
            "",
            "## Policy Metric Consistency",
            json_dump(payload["policy_metric_consistency_checks"]).strip(),
            "",
            "## Reward / Terminal Reconciliation",
            json_dump(payload["reward_terminal_reconciliation_fix"]).strip(),
            "",
            "## Action Path Diversity",
            json_dump(payload["action_path_diversity_check"]).strip(),
            "",
            "## Consistent Policy Effect Comparison",
            json_dump(payload["consistent_policy_effect_comparison"]).strip(),
            "",
            "## 50 / 100 Comparison",
            json_dump(payload["consistent_50_100_comparison"]).strip(),
            "",
            "## Before / After Comparison",
            json_dump(payload["before_after_consistency_comparison"]).strip(),
            "",
            "## Claim Safety",
            json_dump(payload["claim_safety_status"]).strip(),
            "",
            "## Figure Manifest",
            json_dump(payload["figure_manifest"]).strip(),
        ]
    ) + "\n"


def write_calibration_metric_consistency_report(report: dict[str, Any], output_dir: Path | str | None = None) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / REPORT_JSON.name
    md_path = target_dir / REPORT_MD.name
    json_path.write_text(json_dump(report), encoding="utf-8")
    md_path.write_text(_render_markdown(report), encoding="utf-8")
    (target_dir / METRIC_UNIVERSE_DEFINITIONS_JSON.name).write_text(json_dump(report["metric_universe_definitions"]), encoding="utf-8")
    (target_dir / POLICY_METRIC_CONSISTENCY_CHECKS_JSON.name).write_text(json_dump(report["policy_metric_consistency_checks"]), encoding="utf-8")
    (target_dir / REWARD_TERMINAL_RECONCILIATION_FIX_JSON.name).write_text(json_dump(report["reward_terminal_reconciliation_fix"]), encoding="utf-8")
    (target_dir / ACTION_PATH_DIVERSITY_CHECK_JSON.name).write_text(json_dump(report["action_path_diversity_check"]), encoding="utf-8")
    (target_dir / CONSISTENT_POLICY_EFFECT_COMPARISON_JSON.name).write_text(json_dump(report["consistent_policy_effect_comparison"]), encoding="utf-8")
    (target_dir / CONSISTENT_50_100_COMPARISON_JSON.name).write_text(json_dump(report["consistent_50_100_comparison"]), encoding="utf-8")
    (target_dir / BEFORE_AFTER_CONSISTENCY_COMPARISON_JSON.name).write_text(json_dump(report["before_after_consistency_comparison"]), encoding="utf-8")
    (target_dir / DIAGNOSTIC_DECISION_JSON.name).write_text(json_dump(report["diagnostic_decision"]), encoding="utf-8")
    (target_dir / FINAL_CONSISTENCY_SUMMARY_MD.name).write_text(
        "\n".join(
            [
                "# Final Consistency Summary",
                "",
                f"- final_verdict: `{report['final_verdict']}`",
                f"- diagnostic_decision: `{report['diagnostic_decision']['recommended_next_action']}`",
                f"- actions_have_different_feasibility: `{report['action_path_diversity_check']['actions_have_different_feasibility']}`",
                f"- reward_reconciliation_status: `{report['reward_terminal_reconciliation_fix']['reward_reconciliation_status']}`",
                f"- terminal_reconciled: `{report['reward_terminal_reconciliation_fix']['terminal_reconciled']}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (target_dir / FIGURE_MANIFEST_JSON.name).write_text(json_dump(report["figure_manifest"]), encoding="utf-8")
    return json_path, md_path
