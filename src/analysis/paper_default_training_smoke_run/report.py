from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from .config import OUTPUT_DIR, REPORT_JSON, REPORT_MD
from .model import PaperDefaultTrainingSmokeReport


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_paper_default_training_smoke_report(report: PaperDefaultTrainingSmokeReport, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = report.to_dict()
    json_path = target_dir / REPORT_JSON.name
    md_path = target_dir / REPORT_MD.name
    json_path.write_text(_json_dump(payload), encoding="utf-8")
    md_path.write_text("# Paper Default Smoke Report\n\n" + _json_dump(payload), encoding="utf-8")
    return json_path, md_path
