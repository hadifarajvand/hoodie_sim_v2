from __future__ import annotations

from pathlib import Path
import argparse

from .config import DEFAULT_OUTPUT_DIR
from .report import build_feature_081_report, render_feature_081_report, write_feature_081_report


class HoodieProposedFidelityRunner:
    def build(self):
        return build_feature_081_report()

    def render(self) -> str:
        return render_feature_081_report(self.build())

    def write(self, output_dir: Path | str = DEFAULT_OUTPUT_DIR) -> Path:
        return write_feature_081_report(output_dir)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the HOODIE proposed-method fidelity report.")
    parser.add_argument("--output-dir", default=None, help="Optional directory for markdown/json output.")
    args = parser.parse_args(argv)
    runner = HoodieProposedFidelityRunner()
    if args.output_dir:
        output_path = runner.write(args.output_dir)
        print(output_path)
    else:
        print(runner.render())
    return 0
