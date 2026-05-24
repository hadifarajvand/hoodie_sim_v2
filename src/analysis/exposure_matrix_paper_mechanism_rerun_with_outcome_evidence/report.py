from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from .config import DEFAULT_MARKDOWN_FILENAME, DEFAULT_OUTPUT_DIR, DEFAULT_JSON_FILENAME
from .model import ExposureMatrixPaperMechanismRerunReport


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _render_markdown(payload: dict[str, Any]) -> str:
    sections = [
        "# Exposure Matrix Paper Mechanism Rerun with Outcome Evidence",
        "",
        f"- feature_id: `{payload['feature_id']}`",
        f"- final_verdict: `{payload['final_verdict']}`",
        f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
        f"- feature_052_readiness_verified: `{payload['feature_052_readiness_verified']}`",
        f"- paper_mechanism_alignment_ready: `{payload['paper_mechanism_alignment_ready']}`",
        f"- observation_vector_alignment_status: `{payload['observation_vector_alignment_status']}`",
        f"- formula_unit_alignment_status: `{payload['formula_unit_alignment_status']}`",
        f"- exposure_matrix_alignment_status: `{payload['exposure_matrix_alignment_status']}`",
        f"- selected_action_outcome_alignment_status: `{payload['selected_action_outcome_alignment_status']}`",
        f"- training_readiness_contract_status: `{payload['training_readiness_contract_status']}`",
        "",
        "## Behavior Equivalence Summary",
        _json_dump(payload["behavior_equivalence_summary"]).strip(),
        "",
        "## Remaining Blockers",
        _json_dump(payload["remaining_blockers"]).strip(),
    ]
    return "\n".join(sections)


def write_exposure_matrix_paper_mechanism_rerun_report(
    report: ExposureMatrixPaperMechanismRerunReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / DEFAULT_JSON_FILENAME
    md_path = target_dir / DEFAULT_MARKDOWN_FILENAME
    payload = report.to_dict()
    json_path.write_text(_json_dump(payload), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    return json_path, md_path
