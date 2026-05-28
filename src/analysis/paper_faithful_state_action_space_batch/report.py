from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import OUTPUT_DIR, REPORT_JSON, REPORT_MD
from .model import PaperFaithfulStateActionSpaceBatchReport


def json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _render_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Paper-Faithful State and Action Space Batch Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
            "",
            "## Paper State Contract Summary",
            json_dump(payload["paper_state_contract_summary"]).strip(),
            "",
            "## Waiting Time Summary",
            json_dump(payload["waiting_time_summary"]).strip(),
            "",
            "## Public Queue Vector Summary",
            json_dump(payload["public_queue_vector_summary"]).strip(),
            "",
            "## Load History Summary",
            json_dump(payload["load_history_summary"]).strip(),
            "",
            "## Forecast Input Summary",
            json_dump(payload["forecast_input_summary"]).strip(),
            "",
            "## Destination Action Space Summary",
            json_dump(payload["destination_action_space_summary"]).strip(),
            "",
            "## Legal Mask Summary",
            json_dump(payload["legal_mask_summary"]).strip(),
            "",
            "## Compatibility Summary",
            json_dump(payload["compatibility_summary"]).strip(),
            "",
            "## Safety Summary",
            json_dump(payload["safety_summary"]).strip(),
            "",
            "## Remaining Blockers",
            json_dump(payload["remaining_blockers"]).strip(),
        ]
    ) + "\n"


def write_paper_faithful_state_action_space_batch_report(report: PaperFaithfulStateActionSpaceBatchReport, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = report.to_dict()
    json_path = target_dir / REPORT_JSON.name
    md_path = target_dir / REPORT_MD.name
    json_path.write_text(json_dump(payload), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    return json_path, md_path
