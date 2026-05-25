from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from .config import OUTPUT_DIR, REPORT_JSON, REPORT_MD
from .model import FullPaperDefaultTrainingCampaignGateReport


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _render_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Full Paper-Default Training Campaign Gate Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
            f"- feature_058_harness_verified: `{payload['feature_058_harness_verified']}`",
            "",
            "## Campaign Scope Summary",
            _json_dump(payload["campaign_scope_summary"]).strip(),
            "",
            "## Training Execution Gate Summary",
            _json_dump(payload["training_execution_gate_summary"]).strip(),
            "",
            "## Evaluation Harness Gate Summary",
            _json_dump(payload["evaluation_harness_gate_summary"]).strip(),
            "",
            "## Artifact Output Contract Summary",
            _json_dump(payload["artifact_output_contract_summary"]).strip(),
            "",
            "## Resource Control Summary",
            _json_dump(payload["resource_control_summary"]).strip(),
            "",
            "## Checkpoint Contract Summary",
            _json_dump(payload["checkpoint_contract_summary"]).strip(),
            "",
            "## Metric Collection Contract Summary",
            _json_dump(payload["metric_collection_contract_summary"]).strip(),
            "",
            "## Safety Summary",
            _json_dump(payload["safety_summary"]).strip(),
            "",
            "## Remaining Blockers",
            _json_dump(payload["remaining_blockers"]).strip(),
        ]
    )


def write_full_paper_default_training_campaign_gate_report(
    report: FullPaperDefaultTrainingCampaignGateReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = report.to_dict()
    json_path = target_dir / REPORT_JSON.name
    md_path = target_dir / REPORT_MD.name
    json_path.write_text(_json_dump(payload), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    return json_path, md_path
