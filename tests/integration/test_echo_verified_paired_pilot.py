from __future__ import annotations

import csv
import json
from pathlib import Path

from src.echo_verified.paired_pilot import run_paired_pilot


def test_paired_pilot_exports_traceable_nonpaper_evidence(tmp_path: Path) -> None:
    output = tmp_path / "paired-pilot"
    manifest = run_paired_pilot(
        output_root=output,
        seeds=(11, 22),
        episodes_per_seed=2,
    )
    assert manifest["status"] == "PAIRED_PHYSICAL_KERNEL_PILOT_PASSED"
    assert manifest["paper_evidence"] is False
    assert manifest["paper_scale_started"] is False
    assert manifest["echo_disabled_equivalence_passed"] is True
    assert manifest["task_conservation_passed"] is True
    assert manifest["projected_or_surrogate_values_used"] is False
    payload = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert payload["source_lock"]["echo_tex"]["sha256"].startswith("636688a4")
    with (output / "data" / "paired_differences.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 4
    assert (output.parent / f"{output.name}.zip").is_file()
