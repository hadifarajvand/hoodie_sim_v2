from __future__ import annotations

from pathlib import Path

from .report import build_unit_validation_report, write_unit_validation_report


def run_unit_validation() -> dict[str, Path]:
    report = build_unit_validation_report()
    json_path, md_path = write_unit_validation_report(report)
    return {"json": json_path, "markdown": md_path}
