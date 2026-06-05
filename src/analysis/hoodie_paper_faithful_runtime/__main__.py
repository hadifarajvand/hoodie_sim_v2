from __future__ import annotations

import argparse
from pathlib import Path

from .runtime import generate_runtime_artifacts, validate_runtime_artifacts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-artifacts", type=Path, default=None)
    parser.add_argument("--validate-artifacts", action="store_true")
    parser.add_argument("--artifact-dir", type=Path, default=None)
    args = parser.parse_args()

    if args.write_artifacts is not None:
        generate_runtime_artifacts(args.write_artifacts)
    if args.validate_artifacts:
        if args.artifact_dir is None:
            raise SystemExit("--artifact-dir is required with --validate-artifacts")
        validate_runtime_artifacts(args.artifact_dir)


if __name__ == "__main__":
    main()

