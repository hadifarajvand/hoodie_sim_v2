from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import OUTPUT_DIR, REPORT_JSON, REPORT_MD
from .model import BindFullCampaignRealTorchTrainerReport


def json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _render_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Bind Full Campaign Real Torch Trainer Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
            "",
            "## Real Trainer Binding Summary",
            json_dump(payload["real_trainer_binding_summary"]).strip(),
            "",
            "## Feature 060 Repair Summary",
            json_dump(payload["feature_060_repair_summary"]).strip(),
            "",
            "## Artifact Regeneration Summary",
            json_dump(payload["artifact_regeneration_summary"]).strip(),
            "",
            "## Remaining Blockers",
            json_dump(payload["remaining_blockers"]).strip(),
        ]
    ) + "\n"


def write_bind_full_campaign_real_torch_trainer_report(
    report: BindFullCampaignRealTorchTrainerReport,
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
