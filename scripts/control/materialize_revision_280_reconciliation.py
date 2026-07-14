#!/usr/bin/env python3
from __future__ import annotations

import difflib
import hashlib
import json
import re
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STAGING = REPO / "artifacts/reconciliation/revision_280"
SOURCE_PARTS = STAGING / "source_parts"
EXPECTED_SOURCE_PARTS = [SOURCE_PARTS / f"part_{index:03d}.txt" for index in range(7)]
EXPECTED_SNAPSHOT_SHA256 = "3a3382e0ab0a49fb10bda7cc1740ea3a771032d7962e1957fa105eae5a5c06cc"

LIVE_DIR = REPO / "research/authority/echo/live"
AUDIT_DIR = REPO / "research/authority/echo/audit"
SNAPSHOT = LIVE_DIR / "ECHO_PROPOSED_METHOD.md"
METADATA = LIVE_DIR / "source_metadata.json"
CHECKSUMS = LIVE_DIR / "SHA256SUMS"
REPORT = AUDIT_DIR / "REVISION_280_RECONCILIATION_REPORT.md"
REVISION_DIFF = AUDIT_DIR / "revision_278_to_280.diff"
AMENDMENT = REPO / "artifacts/reports/ECHO_MEP_V4_3_AMENDMENT.md"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalized_lines(text: str) -> list[str]:
    result: list[str] = []
    blank = False
    for raw in text.replace("\r\n", "\n").replace("\r", "\n").splitlines():
        line = raw.rstrip()
        if line:
            result.append(line)
            blank = False
        elif not blank:
            result.append("")
            blank = True
    return result


def main() -> int:
    missing = [str(path.relative_to(REPO)) for path in EXPECTED_SOURCE_PARTS if not path.is_file()]
    if missing:
        raise SystemExit(f"missing revision-280 source parts: {missing}")

    source_text = "".join(path.read_text(encoding="utf-8") for path in EXPECTED_SOURCE_PARTS)
    source_bytes = source_text.encode("utf-8")
    actual_sha = sha256_bytes(source_bytes)
    if actual_sha != EXPECTED_SNAPSHOT_SHA256:
        raise SystemExit(
            f"revision-280 snapshot SHA mismatch: expected {EXPECTED_SNAPSHOT_SHA256}, got {actual_sha}"
        )

    staging_metadata = STAGING / "source_metadata.json"
    staging_checksums = STAGING / "SHA256SUMS"
    staging_report = STAGING / "RECONCILIATION_REPORT.md"
    staging_amendment = STAGING / "ECHO_MEP_V4_3_AMENDMENT.md"
    required_staging = [staging_metadata, staging_checksums, staging_report, staging_amendment]
    absent = [str(path.relative_to(REPO)) for path in required_staging if not path.is_file()]
    if absent:
        raise SystemExit(f"missing revision-280 staging files: {absent}")

    metadata = json.loads(staging_metadata.read_text(encoding="utf-8"))
    required_metadata = {
        "google_drive_revision_id": "280",
        "normalized_sha256": EXPECTED_SNAPSHOT_SHA256,
        "equation_count": 67,
        "algorithm_1_line_count": 23,
        "algorithm_2_line_count": 14,
        "tab_title": None,
        "tab_title_asserted": False,
    }
    for key, expected in required_metadata.items():
        if metadata.get(key) != expected:
            raise SystemExit(f"metadata mismatch for {key}: {metadata.get(key)!r} != {expected!r}")

    tags = [int(value) for value in re.findall(r"\\tag\{(\d+)\}", source_text)]
    if tags != list(range(1, 68)):
        raise SystemExit(f"equation tags are not exactly 1..67: {tags}")

    algorithm_1_match = re.search(
        r"Algorithm 1\. Training procedure of ECHO\n(.*?)\n\n\n2\) Inference Procedure",
        source_text,
        re.S,
    )
    algorithm_2_match = re.search(
        r"Algorithm 2\. Inference procedure of ECHO\n(.*?)\n\n\n3\) Method Summary",
        source_text,
        re.S,
    )
    if not algorithm_1_match or not algorithm_2_match:
        raise SystemExit("could not locate both algorithm blocks")
    algorithm_1_lines = re.findall(r"(?m)^(\d+):", algorithm_1_match.group(1))
    algorithm_2_lines = re.findall(r"(?m)^(\d+):", algorithm_2_match.group(1))
    if algorithm_1_lines != [str(value) for value in range(1, 24)]:
        raise SystemExit(f"Algorithm 1 numbering mismatch: {algorithm_1_lines}")
    if algorithm_2_lines != [str(value) for value in range(1, 15)]:
        raise SystemExit(f"Algorithm 2 numbering mismatch: {algorithm_2_lines}")

    previous_text: str | None = None
    if SNAPSHOT.is_file():
        previous_text = SNAPSHOT.read_text(encoding="utf-8")

    LIVE_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    AMENDMENT.parent.mkdir(parents=True, exist_ok=True)

    SNAPSHOT.write_bytes(source_bytes)
    shutil.copyfile(staging_metadata, METADATA)
    shutil.copyfile(staging_checksums, CHECKSUMS)
    shutil.copyfile(staging_report, REPORT)
    shutil.copyfile(staging_amendment, AMENDMENT)

    if previous_text and sha256_bytes(previous_text.encode("utf-8")) != EXPECTED_SNAPSHOT_SHA256:
        revision_diff = "\n".join(
            difflib.unified_diff(
                normalized_lines(previous_text),
                normalized_lines(source_text),
                fromfile="previous-authority/ECHO_PROPOSED_METHOD.md",
                tofile="revision-280/ECHO_PROPOSED_METHOD.md",
                lineterm="",
            )
        ) + "\n"
    else:
        revision_diff = (
            "# Revision 278 to 280 diff was not generated locally because a verified revision-278 "
            "snapshot was not present at the authority path before materialization.\n"
            "# Use the committed reconciliation report and reclassify the historical revision-278 "
            "audits against the revision-280 snapshot.\n"
        )
    REVISION_DIFF.write_text(revision_diff, encoding="utf-8")

    print("Revision-280 reconciliation payload materialized and verified.")
    print(f"snapshot_sha256={actual_sha}")
    print("equations=67")
    print("algorithm_1_lines=23")
    print("algorithm_2_lines=14")
    for path in [SNAPSHOT, METADATA, CHECKSUMS, REPORT, REVISION_DIFF, AMENDMENT]:
        print(path.relative_to(REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
