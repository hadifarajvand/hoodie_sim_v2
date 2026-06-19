from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import REPORT_JSON, REPORT_MD
from .model import UnifiedCampaignAnalysisReport


def json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def render_markdown(payload: dict[str, Any]) -> str:
    sections = [
        "# Unified Campaign Result Analysis, Figures, and Findings",
        "",
        f"- feature_id: `{payload['feature_id']}`",
        f"- final_verdict: `{payload['final_verdict']}`",
        f"- recommended_next_step: `{payload['recommended_next_step']}`",
        "",
        "## Feature 060 Prerequisite Verification",
        json_dump(payload["feature_060_prerequisite_verification"]).strip(),
        "",
        "## Result Integrity Audit",
        json_dump(payload["integrity_audit_result"]).strip(),
        "",
        "## Training Metrics Summary",
        json_dump(payload["training_metrics_summary"]).strip(),
        "",
        "## Evaluation Metrics Summary",
        json_dump(payload["evaluation_metrics_summary"]).strip(),
        "",
        "## Baseline Evaluation Summary",
        json_dump(payload["baseline_evaluation_summary"]).strip(),
        "",
        "## Comparison Readiness Decision",
        json_dump(payload["comparison_readiness"]).strip(),
        "",
        "## Result Tables",
        json_dump(payload["result_tables_summary"]).strip(),
        "",
        "## Figure Manifest",
        json_dump(payload["figure_manifest"]).strip(),
        "",
        "## Claim Safety Review",
        json_dump(payload["claim_safety_review"]).strip(),
        "",
        "## Remaining Blockers",
        json_dump(payload["remaining_blockers"]).strip(),
    ]
    return "\n".join(sections) + "\n"


def write_unified_campaign_analysis_report(
    report: UnifiedCampaignAnalysisReport,
    output_dir: Path | str,
) -> tuple[Path, Path]:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = report.to_dict()
    json_path = target_dir / REPORT_JSON.name
    md_path = target_dir / REPORT_MD.name
    json_path.write_text(json_dump(payload), encoding="utf-8")
    md_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, md_path
