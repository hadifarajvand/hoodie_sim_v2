from __future__ import annotations

from pathlib import Path
import json
import sys
from typing import Sequence

from .config import DEFAULT_OUTPUT_DIR
from .report import build_feature_075_report, render_feature_075_report, write_feature_075_report


class ProposedMethodIntegrationReadinessRunner:
    def __init__(self, output_dir: Path | str | None = None):
        self.output_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR

    def run(self):
        return build_feature_075_report()

    def write(self) -> Path:
        return write_feature_075_report(self.output_dir)


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    output_dir = Path(args[0]) if args else DEFAULT_OUTPUT_DIR
    report = build_feature_075_report()
    if "--json" in args:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(render_feature_075_report(report))
    write_feature_075_report(output_dir)
    return 0
