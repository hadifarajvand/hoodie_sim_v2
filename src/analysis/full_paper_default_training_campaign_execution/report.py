from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from .config import REPORT_JSON, REPORT_MD, OUTPUT_DIR
from .model import FullPaperDefaultTrainingCampaignExecutionReport


def json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _render_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Full Paper-Default Training Campaign Execution Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
            f"- feature_059_gate_verified: `{payload['feature_059_gate_verified']}`",
            "",
            "## Campaign Execution Summary",
            json_dump(payload["campaign_execution_summary"]).strip(),
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
            "## Checkpoint Metadata Summary",
            json_dump(payload["checkpoint_metadata_summary"]).strip(),
            "",
            "## Artifact Manifest Summary",
            json_dump(payload["artifact_manifest_summary"]).strip(),
            "",
            "## Resource Control Summary",
            json_dump(payload["resource_control_summary"]).strip(),
            "",
            "## Safety Summary",
            json_dump(payload["safety_summary"]).strip(),
            "",
            "## Remaining Blockers",
            json_dump(payload["remaining_blockers"]).strip(),
        ]
    )


def write_full_paper_default_training_campaign_execution_report(
    report: FullPaperDefaultTrainingCampaignExecutionReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = report.to_dict()
    json_path = target_dir / REPORT_JSON.name
    md_path = target_dir / REPORT_MD.name
    json_path.write_text(json_dump(payload), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    return json_path, md_path
