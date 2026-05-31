from __future__ import annotations

from pathlib import Path
import json
from typing import Any, Sequence

from .config import validate_scope
from .report import build_feature_071_report, render_feature_071_report, write_feature_071_report


def build_report() -> Any:
    changed_files = validate_scope()
    return build_feature_071_report(changed_files=changed_files)


def run(output_dir: Path | str | None = None) -> Any:
    report = build_report()
    if output_dir is not None:
        return report, write_feature_071_report(report, output_dir)
    return report


def main(argv: Sequence[str] | None = None) -> int:
    report = build_report()
    if argv and "--json" in argv:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(render_feature_071_report(report))
    return 0
