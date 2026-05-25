from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import OUTPUT_DIR, REPORT_JSON, REPORT_MD, BASELINE_RESULTS_JSON, TRAINED_POLICY_RESULTS_JSON, COMPARISON_READINESS_JSON, COMPARISON_JSON, COMPARISON_MD
from .model import CampaignIntegrityEvaluationComparisonBatchReport


def json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _render_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Campaign Integrity Evaluation Comparison Batch Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
            "",
            "## Campaign Integrity Summary",
            json_dump(payload["campaign_integrity_summary"]).strip(),
            "",
            "## Baseline Evaluation Summary",
            json_dump(payload["baseline_evaluation_summary"]).strip(),
            "",
            "## Trained Policy Evaluation Summary",
            json_dump(payload["trained_policy_evaluation_summary"]).strip(),
            "",
            "## Comparison Readiness Summary",
            json_dump(payload["comparison_readiness_summary"]).strip(),
            "",
            "## Comparison Report Summary",
            json_dump(payload["comparison_report_summary"]).strip(),
            "",
            "## Artifact Manifest Summary",
            json_dump(payload["artifact_manifest_summary"]).strip(),
            "",
            "## Safety Summary",
            json_dump(payload["safety_summary"]).strip(),
            "",
            "## Remaining Blockers",
            json_dump(payload["remaining_blockers"]).strip(),
        ]
    ) + "\n"


def write_campaign_integrity_evaluation_comparison_batch_report(report: CampaignIntegrityEvaluationComparisonBatchReport, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = report.to_dict()
    json_path = target_dir / REPORT_JSON.name
    md_path = target_dir / REPORT_MD.name
    json_path.write_text(json_dump(payload), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    return json_path, md_path
