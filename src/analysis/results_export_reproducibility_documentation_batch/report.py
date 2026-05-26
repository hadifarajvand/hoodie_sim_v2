from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import OUTPUT_DIR, REPORT_JSON, REPORT_MD
from .model import ResultsExportReproducibilityDocumentationBatchReport


def json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _render_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Results Export, Reproducibility, and Final Documentation Batch Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
            "",
            "## Final Integrity Audit Summary",
            json_dump(payload["final_integrity_audit_summary"]).strip(),
            "",
            "## Results Export Summary",
            json_dump(payload["results_export_summary"]).strip(),
            "",
            "## Reproducibility Package Summary",
            json_dump(payload["reproducibility_package_summary"]).strip(),
            "",
            "## Mechanism Documentation Summary",
            json_dump(payload["mechanism_documentation_summary"]).strip(),
            "",
            "## Artifact Index Summary",
            json_dump(payload["artifact_index_summary"]).strip(),
            "",
            "## Claim Boundary Summary",
            json_dump(payload["claim_boundary_summary"]).strip(),
            "",
            "## Safety Summary",
            json_dump(payload["safety_summary"]).strip(),
            "",
            "## Remaining Blockers",
            json_dump(payload["remaining_blockers"]).strip(),
        ]
    ) + "\n"


def write_results_export_reproducibility_documentation_batch_report(report: ResultsExportReproducibilityDocumentationBatchReport, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = report.to_dict()
    json_path = target_dir / REPORT_JSON.name
    md_path = target_dir / REPORT_MD.name
    json_path.write_text(json_dump(payload), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    return json_path, md_path
