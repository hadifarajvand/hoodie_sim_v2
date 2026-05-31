from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
import sys

from .report import build_feature_078_report, render_feature_078_report, write_feature_078_report


class CampaignExecutionEngineRunner:
    def build(self):
        return build_feature_078_report()

    def render(self) -> str:
        return render_feature_078_report(self.build())

    def write(self, output_dir: str | Path) -> Path:
        return write_feature_078_report(output_dir, self.build())


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    runner = CampaignExecutionEngineRunner()
    if not args:
        print(runner.render())
        return 0
    output_path = runner.write(args[0])
    print(output_path)
    return 0
