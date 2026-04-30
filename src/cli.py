from __future__ import annotations

import argparse
from pathlib import Path
import sys

from src.run_pipeline import run_analysis_only, run_pipeline, run_validation_only


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hoodie-sim")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--config", required=True, type=Path)
        subparser.add_argument("--output-dir", required=True, type=Path)
        subparser.add_argument("--deterministic", action="store_true")
        subparser.add_argument("--timestamp", default=None)

    run_parser = subparsers.add_parser("run", help="Run training, validation, and analysis")
    add_common(run_parser)
    run_parser.add_argument("--with-training", action="store_true", help="Run the training loop before validation")

    validation_parser = subparsers.add_parser("validation", help="Run validation only")
    add_common(validation_parser)

    analysis_parser = subparsers.add_parser("analysis", help="Run analysis only from packaged validation artifacts")
    add_common(analysis_parser)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        run_pipeline(
            args.config,
            args.output_dir,
            run_training=args.with_training,
            deterministic=args.deterministic,
            timestamp=args.timestamp,
        )
    elif args.command == "validation":
        run_validation_only(
            args.config,
            args.output_dir,
            deterministic=args.deterministic,
            timestamp=args.timestamp,
        )
    elif args.command == "analysis":
        run_analysis_only(
            args.config,
            args.output_dir,
            deterministic=args.deterministic,
            timestamp=args.timestamp,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

