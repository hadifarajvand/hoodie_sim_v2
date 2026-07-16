from __future__ import annotations

import csv
from hashlib import sha256
import json
from pathlib import Path

import pytest

from src.hoodie.experiments.finalization import verify_bundle
from src.hoodie.experiments.job_matrix import ProductionJobRow
from src.hoodie.experiments.verification import (
    _aggregate_checks,
    _checkpoint_registry_checks,
    _evaluation_checks,
)


def _row(
    *,
    job_id: str,
    job_type: str,
    panel_id: str = "figure_10a",
    policy: str = "FLC",
    dependency: str | None = None,
    training_episodes: int = 0,
    validation_episodes: int = 2,
) -> ProductionJobRow:
    return ProductionJobRow(
        campaign_id="campaign",
        panel_id=panel_id,
        scientific_unit_id=f"unit:{job_id}",
        job_id=job_id,
        job_type=job_type,
        independent_variable="task_arrival_probability",
        independent_value=0.5,
        series_name=policy,
        policy=policy,
        variant="hoodie_lstm" if policy == "HOODIE" else None,
        seed=7,
        topology_contract={"agent_counts": [20]},
        physical_contract={"backend": "cpu"},
        workload_contract={},
        training_contract={"training_episodes": training_episodes},
        evaluation_contract={"validation_episodes": validation_episodes},
        trace_bank_id="paired-trace",
        checkpoint_dependency=dependency,
        config_hash=f"config:{job_id}",
        source_contract_hash="source-contract",
    )


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _metric(episode: int, *, trace_id: str, total: int = 1) -> dict[str, object]:
    return {
        "episode": episode,
        "trace_id": trace_id,
        "average_reward": -1.0,
        "average_delay": 1.0,
        "drop_ratio": 0.0,
        "throughput": total,
        "completed_tasks": total,
        "dropped_tasks": 0,
        "total_tasks": total,
        "local_actions": total,
        "horizontal_actions": 0,
        "vertical_actions": 0,
    }


def _task(trace_id: str, task_id: int) -> dict[str, object]:
    return {
        "run_id": trace_id,
        "task_id": task_id,
        "source_agent": "1",
        "arrival_slot": 0,
        "deadline": 10,
        "workload": "{}",
    }


def _decision(trace_id: str, task_id: int) -> dict[str, object]:
    return {"observation_ref": f"{trace_id}:{task_id}"}


def test_baseline_evaluation_episode_count_is_executable_check(tmp_path: Path) -> None:
    row = _row(job_id="baseline", job_type="evaluation", validation_episodes=2)
    job = tmp_path / "jobs" / row.job_id
    _write_csv(job / "evaluation_metrics.csv", [_metric(0, trace_id="trace-0")])
    _write_csv(job / "task_records.csv", [_task("trace-0", 1)])
    _write_csv(job / "decision_records.csv", [_decision("trace-0", 1)])
    (job / "status.json").write_text(
        json.dumps({"status": "completed", "checkpoint_hash": "baseline-no-checkpoint"}),
        encoding="utf-8",
    )

    checks = []
    _evaluation_checks(tmp_path, [row], {}, checks)
    episode = next(
        check for check in checks if check.check_id == "evaluation.episode_range:baseline"
    )
    assert episode.passed is False
    assert episode.expected["count"] == 2
    assert episode.observed["count"] == 1


def test_checkpoint_registry_recomputes_file_sha256(tmp_path: Path) -> None:
    row = _row(
        job_id="train",
        job_type="training",
        panel_id="figure_8a",
        policy="HOODIE",
        training_episodes=1,
    )
    job = tmp_path / "jobs" / row.job_id
    checkpoint = job / "internal_checkpoints" / "checkpoint-a" / "checkpoint.pt"
    checkpoint.parent.mkdir(parents=True)
    checkpoint.write_bytes(b"real checkpoint bytes")
    (job / "checkpoint_retention_manifest.json").write_text(
        json.dumps(
            {
                "maximum_retained_checkpoints": 1,
                "replay_snapshot_count": 0,
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "checkpoint_registry.json").write_text(
        json.dumps(
            {
                "checkpoints": [
                    {
                        "training_job_id": row.job_id,
                        "checkpoint_path": str(checkpoint),
                        "checkpoint_hash": "wrong-hash",
                        "policy": "HOODIE",
                        "variant": "hoodie_lstm",
                        "seed": 7,
                        "source_contract_hash": "source-contract",
                        "scientifically_complete": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    checks = []
    _checkpoint_registry_checks(tmp_path, [row], checks)
    integrity = next(
        check for check in checks if check.check_id == "checkpoint.valid:train"
    )
    assert integrity.passed is False
    assert integrity.observed["actual_hash"] == sha256(
        b"real checkpoint bytes"
    ).hexdigest()


def test_aggregate_verification_requires_all_fourteen_panels(tmp_path: Path) -> None:
    (tmp_path / "aggregation_manifest.json").write_text(
        json.dumps({"datasets": {}}), encoding="utf-8"
    )
    checks = []
    _aggregate_checks(tmp_path, [], set(), checks)
    coverage = next(
        check for check in checks if check.check_id == "aggregate.panel_manifest_coverage"
    )
    assert coverage.passed is False
    assert len(coverage.expected) == 14


def test_bundle_verification_rejects_tampered_scientific_file(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    scientific = bundle / "aggregates" / "figure_8a.csv"
    scientific.parent.mkdir()
    scientific.write_text("x,y\n0,1\n", encoding="utf-8")
    digest = sha256(scientific.read_bytes()).hexdigest()
    (bundle / "bundle_checksums.json").write_text(
        json.dumps({"aggregates/figure_8a.csv": digest}), encoding="utf-8"
    )
    assert verify_bundle(bundle)["verified"] is True

    scientific.write_text("x,y\n0,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="checksum mismatch"):
        verify_bundle(bundle)
