from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from .config import FEATURE_ID, DEFAULT_OUTPUT_DIR
from .model import ExposureMatrixPaperMechanismReport

JSON_FILENAME = "exposure-matrix-paper-mechanism-report.json"
MARKDOWN_FILENAME = "exposure-matrix-paper-mechanism-report.md"


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_exposure_matrix_paper_mechanism_report(report: ExposureMatrixPaperMechanismReport, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / JSON_FILENAME
    md_path = target_dir / MARKDOWN_FILENAME
    payload = report.to_dict()
    json_path.write_text(_json_dump(payload), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    return json_path, md_path


def _render_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Exposure Matrix Paper Mechanism Alignment Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
            "",
            "## Exposure Matrix Rerun Summary",
            _json_dump(payload["exposure_matrix_rerun_summary"]).strip(),
            "",
            "## Legal vs Selected Action Matrix",
            _json_dump(payload["legal_vs_selected_action_matrix"]).strip(),
            "",
            "## Observation Vector Audit",
            _json_dump(payload["observation_vector_audit"]).strip(),
            "",
            "## Paper Formula Unit Audit",
            _json_dump(payload["paper_formula_unit_audit"]).strip(),
            "",
            "## Training Readiness Decision",
            _json_dump(payload["training_readiness_decision"]).strip(),
        ]
    )
