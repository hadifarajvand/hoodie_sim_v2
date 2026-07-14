from __future__ import annotations

import csv
import json

from scripts.run_echo_hoodie_paired_pilot import run_pilot


def test_paired_pilot_writes_real_accounted_simulator_evidence(tmp_path) -> None:
    output_dir = tmp_path / "paired-pilot"
    manifest = run_pilot(
        output_dir=output_dir,
        train_episodes=1,
        evaluation_episodes=2,
        episode_length=12,
        drain_slots=2,
        training_seed=101,
        evaluation_seed=303,
        arrival_probability=0.2,
        timeout_slots=6,
    )

    assert manifest["scientific_status"] == (
        "bounded_real_simulator_pilot_not_publication_campaign"
    )
    assert manifest["digitized_curves_used"] is False
    assert manifest["paired_trace_contract"] is True
    assert manifest["train_eval_seeds_disjoint"] is True
    assert set(manifest["aggregate_results"]) == {"ECHO", "HOODIE"}

    for relative_path in manifest["files"]:
        assert (output_dir / relative_path).exists()

    with (output_dir / "paired_trace_metrics.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert all(row["echo_total_tasks"] == row["hoodie_total_tasks"] for row in rows)

    for method in ("echo", "hoodie"):
        payload = json.loads(
            (output_dir / "raw" / f"{method}_result.json").read_text(
                encoding="utf-8"
            )
        )
        for trace in payload["per_trace"]:
            assert trace["completed_tasks"] + trace["dropped_tasks"] == trace[
                "total_tasks"
            ]
            assert all(
                record["selected_action"]
                for record in trace.get("raw_records", [])
            )
