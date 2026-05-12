from __future__ import annotations

from pathlib import Path

from .report import build_assumption_closure_report, write_assumption_closure_report


def run_paper_assumption_closure_evidence_exhaustion() -> dict[str, Path]:
    report = build_assumption_closure_report()
    json_path, markdown_path = write_assumption_closure_report(report)
    return {"json": json_path, "markdown": markdown_path}
