from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import OUTPUT_DIR, REPORT_JSON, REPORT_MD
from .model import FinalReviewReleaseGateBatchReport


def json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _render_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Final Review and Release Gate Batch Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
            "",
            "## Repository State Audit Summary",
            json_dump(payload["repository_state_audit_summary"]).strip(),
            "",
            "## Artifact Completeness Summary",
            json_dump(payload["artifact_completeness_summary"]).strip(),
            "",
            "## Claim Boundary Review Summary",
            json_dump(payload["claim_boundary_review_summary"]).strip(),
            "",
            "## Release Tag Readiness Summary",
            json_dump(payload["release_tag_readiness_summary"]).strip(),
            "",
            "## Handoff Summary",
            json_dump(payload["handoff_summary"]).strip(),
            "",
            "## Safety Summary",
            json_dump(payload["safety_summary"]).strip(),
            "",
            "## Remaining Blockers",
            json_dump(payload["remaining_blockers"]).strip(),
        ]
    ) + "\n"


def write_final_review_release_gate_batch_report(report: FinalReviewReleaseGateBatchReport, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = report.to_dict()
    json_path = target_dir / REPORT_JSON.name
    md_path = target_dir / REPORT_MD.name
    json_path.write_text(json_dump(payload), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    return json_path, md_path
