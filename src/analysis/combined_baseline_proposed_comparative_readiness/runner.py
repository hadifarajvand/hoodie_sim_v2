from __future__ import annotations

from pathlib import Path
import sys
from typing import Sequence

from .config import DEFAULT_OUTPUT_DIR
from .report import build_feature_076_report, render_feature_076_report, write_feature_076_report


class CombinedBaselineProposedComparativeReadinessRunner:
    def __init__(self, output_dir: Path | str | None = None):
        self.output_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR

    def run(self):
        return build_feature_076_report()

    def write(self) -> Path:
        return write_feature_076_report(self.output_dir)


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    report = build_feature_076_report()
    if not args:
        print(render_feature_076_report(report))
        return 0
    output_dir = Path(args[0])
    write_feature_076_report(output_dir)
    return 0
