from __future__ import annotations

from collections.abc import Sequence
from sys import argv
from pathlib import Path

from .report import build_feature_079_report, render_feature_079_report, write_feature_079_report


def main(args: Sequence[str] | None = None) -> int:
    parsed = list(argv[1:] if args is None else args)
    report = build_feature_079_report()
    if not parsed:
        print(render_feature_079_report(report))
        return 0
    output_path = write_feature_079_report(Path(parsed[0]), report)
    print(output_path)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
