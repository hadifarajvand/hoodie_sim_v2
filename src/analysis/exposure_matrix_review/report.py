from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json
from typing import Any

from .config import FEATURE_ID
from .model import ExposureMatrixReport, IllegalActionSummary

DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/exposure-matrix-review")
JSON_FILENAME = "exposure-matrix-report.json"
MARKDOWN_FILENAME = "exposure-matrix-report.md"


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _report_dict(report: ExposureMatrixReport) -> dict[str, Any]:
    payload = report.to_dict()
    if isinstance(payload["illegal_action_summary"], IllegalActionSummary):
        payload["illegal_action_summary"] = payload["illegal_action_summary"].to_dict()
    return payload


def write_exposure_matrix_report(report: ExposureMatrixReport, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / JSON_FILENAME
    md_path = target_dir / MARKDOWN_FILENAME
    payload = _report_dict(report)
    json_path.write_text(_json_dump(payload), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    return json_path, md_path


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Exposure-Matrix Review Report",
        "",
        f"- feature_id: `{payload['feature_id']}`",
        f"- final_verdict: `{payload['final_verdict']}`",
        f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
        "",
        "## Matrix Completeness",
        _json_dump(payload["matrix_completeness_summary"]).strip(),
        "",
        "## Illegal Action Summary",
        _json_dump(payload["illegal_action_summary"]).strip(),
        "",
        "## Exposure Bias Summary",
        _json_dump(payload["exposure_bias_summary"]).strip(),
        "",
        "## Load vs Exposure Summary",
        _json_dump(payload["load_vs_exposure_summary"]).strip(),
        "",
        "## Dominant Exposure Findings",
        _json_dump(payload["dominant_exposure_findings"]).strip(),
    ]
    return "\n".join(lines)
