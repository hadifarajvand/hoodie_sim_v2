#!/usr/bin/env python3
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys


def digest(path: Path) -> str:
    value = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tex", type=Path, required=True)
    parser.add_argument("--source-zip", type=Path, required=True)
    parser.add_argument("--hoodie-pdf", type=Path, required=True)
    parser.add_argument(
        "--lock",
        type=Path,
        default=Path("configs/echo/authoritative_source_lock.json"),
    )
    args = parser.parse_args()
    lock = json.loads(args.lock.read_text(encoding="utf-8"))
    expected = {item["name"]: item.get("sha256") for item in lock["sources"]}
    actual = {
        "02_ECHO-Article_Current.tex": digest(args.tex),
        "03_ECHO-Article_Current_Source.zip": digest(args.source_zip),
        "HOODIE_paper.pdf": digest(args.hoodie_pdf),
    }
    failures = {
        name: {"expected": expected[name], "actual": value}
        for name, value in actual.items()
        if expected.get(name) != value
    }
    result = {"passed": not failures, "actual": actual, "failures": failures}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
