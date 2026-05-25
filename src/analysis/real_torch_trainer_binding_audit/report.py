from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import OUTPUT_DIR, REPORT_JSON, REPORT_MD
from .model import RealTorchTrainerBindingAuditReport


def json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _render_markdown(payload: dict[str, Any]) -> str:
    sections = [
        "# Real Torch Trainer Binding Audit Report",
        "",
        f"- feature_id: `{payload['feature_id']}`",
        f"- final_verdict: `{payload['final_verdict']}`",
        f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
        "",
        "## Python Environment Summary",
        json_dump(payload["python_environment_summary"]).strip(),
        "",
        "## Torch Availability Summary",
        json_dump(payload["torch_availability_summary"]).strip(),
        "",
        "## Feature 060 Claim Summary",
        json_dump(payload["feature_060_claim_summary"]).strip(),
        "",
        "## Feature 060 Code Binding Summary",
        json_dump(payload["feature_060_code_binding_summary"]).strip(),
        "",
        "## Real Trainer Candidate Summary",
        json_dump(payload["real_trainer_candidate_summary"]).strip(),
        "",
        "## Simulation Fallback Summary",
        json_dump(payload["simulation_fallback_summary"]).strip(),
        "",
        "## Binding Audit Summary",
        json_dump(payload["binding_audit_summary"]).strip(),
        "",
        "## Remaining Blockers",
        json_dump(payload["remaining_blockers"]).strip(),
    ]
    return "\n".join(sections) + "\n"


def write_real_torch_trainer_binding_audit_report(
    report: RealTorchTrainerBindingAuditReport,
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
