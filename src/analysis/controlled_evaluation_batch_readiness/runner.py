from __future__ import annotations

from pathlib import Path
import sys
from typing import Sequence

from .config import DEFAULT_OUTPUT_DIR
from .report import write_feature_073_report


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    output_dir = Path(args[0]) if args else DEFAULT_OUTPUT_DIR
    write_feature_073_report(output_dir)
    return 0
