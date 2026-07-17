from __future__ import annotations

import csv
import json
from pathlib import Path

from src.echo_verified.smoke import run_smoke


def test_verified_smoke_exports_traceable_nonpaper_outputs(tmp_path: Path) -> None:
    result = run_smoke(tmp_path)

    assert result["status"] == "ECHO_VERIFIED_MECHANISM_SMOKE_PASSED"
    assert result["paper_scale_started"] is False
    assert result["ert_absent_from_neural_observation"] is True
    assert result["tasks"]["generated"] == 4
    assert result["tasks"]["successful"] == 3
    assert result["tasks"]["dropped"] == 1

    expected = {
        "summary.json",
        "queue_decisions.csv",
        "route_decisions.csv",
        "destination_fifo.csv",
        "task_ledger.csv",
        "diagnostics.csv",
        "README.txt",
    }
    assert expected == {path.name for path in tmp_path.iterdir()}

    summary = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    assert summary == result

    with (tmp_path / "task_ledger.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 4
    assert sum(row["dropped"] == "True" for row in rows) == 1

    with (tmp_path / "route_decisions.csv").open(encoding="utf-8", newline="") as handle:
        route_rows = list(csv.DictReader(handle))
    assert any(
        row["case"] == "all_late"
        and row["route_id"] == "horizontal_2"
        and row["allowed_after_echo_filter"] == "True"
        for row in route_rows
    )
