from __future__ import annotations

from pathlib import Path

from .config import DEFAULT_CHANGED_FILES, validate_scope
from .report import build_feature_072_report, render_feature_072_report, write_feature_072_report


def build_report():
    validate_scope(DEFAULT_CHANGED_FILES)
    return build_feature_072_report(changed_files=DEFAULT_CHANGED_FILES)


def run(output_dir: Path | str | None = None):
    report = build_report()
    if output_dir is not None:
        write_feature_072_report(report, output_dir)
    return report


def main() -> int:
    report = build_report()
    print(render_feature_072_report(report))
    return 0
