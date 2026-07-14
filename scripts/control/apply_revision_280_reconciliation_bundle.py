#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BUNDLE_B64 = REPO / "artifacts/reconciliation/revision_280/ECHO_REVISION_280_RECONCILIATION_BUNDLE.zip.b64"
EXPECTED_ZIP_SHA256 = "f8802a75397dc7ee6df2fa981ab95ca6b69e9cf252fe3a238bc1ee3adeff1989"
EXPECTED_SNAPSHOT_SHA256 = "3a3382e0ab0a49fb10bda7cc1740ea3a771032d7962e1957fa105eae5a5c06cc"

DESTINATIONS = {
    "ECHO_PROPOSED_METHOD.md": REPO / "research/authority/echo/live/ECHO_PROPOSED_METHOD.md",
    "source_metadata.json": REPO / "research/authority/echo/live/source_metadata.json",
    "SHA256SUMS": REPO / "research/authority/echo/live/SHA256SUMS",
    "RECONCILIATION_REPORT.md": REPO / "research/authority/echo/audit/REVISION_280_RECONCILIATION_REPORT.md",
    "revision_278_to_280.diff": REPO / "research/authority/echo/audit/revision_278_to_280.diff",
    "ECHO_MEP_V4_3_AMENDMENT.md": REPO / "artifacts/reports/ECHO_MEP_V4_3_AMENDMENT.md",
    "AGENT_PROMPT.txt": REPO / "artifacts/reconciliation/revision_280/AGENT_PROMPT.txt",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if not BUNDLE_B64.is_file():
        raise SystemExit(f"missing bundle: {BUNDLE_B64}")

    raw = base64.b64decode(BUNDLE_B64.read_text(encoding="ascii"), validate=False)
    actual_zip_sha = hashlib.sha256(raw).hexdigest()
    if actual_zip_sha != EXPECTED_ZIP_SHA256:
        raise SystemExit(f"bundle SHA mismatch: {actual_zip_sha}")

    with tempfile.TemporaryDirectory(prefix="echo-rev280-") as temp_dir:
        temp = Path(temp_dir)
        archive = temp / "bundle.zip"
        archive.write_bytes(raw)
        with zipfile.ZipFile(archive) as zf:
            names = set(zf.namelist())
            missing = set(DESTINATIONS) - names
            if missing:
                raise SystemExit(f"bundle missing entries: {sorted(missing)}")
            zf.extractall(temp / "unpacked")

        unpacked = temp / "unpacked"
        snapshot = unpacked / "ECHO_PROPOSED_METHOD.md"
        if sha256(snapshot) != EXPECTED_SNAPSHOT_SHA256:
            raise SystemExit("revision-280 snapshot SHA mismatch")

        metadata = json.loads((unpacked / "source_metadata.json").read_text(encoding="utf-8"))
        if metadata.get("google_drive_revision_id") != "280":
            raise SystemExit("metadata does not declare Drive revision 280")
        if metadata.get("tab_title_asserted") is not False or metadata.get("tab_title") is not None:
            raise SystemExit("unsupported tab-title assertion detected")
        if metadata.get("equation_count") != 67:
            raise SystemExit("equation count is not 67")
        if metadata.get("algorithm_1_line_count") != 23:
            raise SystemExit("Algorithm 1 count is not 23")
        if metadata.get("algorithm_2_line_count") != 14:
            raise SystemExit("Algorithm 2 count is not 14")

        for name, destination in DESTINATIONS.items():
            source = unpacked / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)

    print("Applied revision-280 reconciliation bundle.")
    print(f"Snapshot SHA-256: {EXPECTED_SNAPSHOT_SHA256}")
    for destination in DESTINATIONS.values():
        print(destination.relative_to(REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
