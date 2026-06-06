from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase2_mechanisms import build_validation_report, write_validation_artifacts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace_dir")
    parser.add_argument("--output-dir", default="artifacts/phase2_mechanism_repair")
    parser.add_argument("--write-artifacts", action="store_true")
    args = parser.parse_args()
    trace_dir = Path(args.trace_dir)
    report = build_validation_report(trace_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.write_artifacts:
        write_validation_artifacts(trace_dir, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
