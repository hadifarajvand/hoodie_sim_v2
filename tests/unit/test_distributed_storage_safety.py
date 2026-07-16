from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.hoodie.experiments import distributed_storage_patch as storage_patch
from src.hoodie.experiments import distributed_v2
from src.hoodie.experiments.job_matrix import ProductionJobRow
from src.hoodie.experiments import production_patch


def _row(*, campaign_id: str, job_id: str, dependency: str | None = None) -> ProductionJobRow:
    return ProductionJobRow(
        campaign_id=campaign_id,
        panel_id="figure_10a" if dependency else "figure_8a",
        scientific_unit_id=f"unit:{job_id}",
        job_id=job_id,
        job_type="evaluation" if dependency else "training",
        independent_variable="task_arrival_probability",
        independent_value=0.5,
        series_name="HOODIE",
        policy="HOODIE",
        variant="hoodie_lstm",
        seed=7,
        topology_contract={"agent_counts": [20]},
        physical_contract={"backend": "cpu"},
        workload_contract={},
        training_contract={"training_episodes": 1} if dependency is None else {},
        evaluation_contract={"validation_episodes": 1} if dependency else {},
        trace_bank_id="trace",
        checkpoint_dependency=dependency,
        config_hash=f"config:{job_id}",
        source_contract_hash="source-hash",
    )


def _plan(campaign_id: str, row: ProductionJobRow, *, dependency: str | None = None) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": 2,
        "campaign_id": campaign_id,
        "source_commit": "commit",
        "source_contract_hash": "source-hash",
        "matrix_hash": "matrix-hash",
        "total_jobs": 1,
        "training_jobs": int(row.job_type == "training"),
        "evaluation_jobs": int(row.job_type == "evaluation"),
        "rows": [asdict(row)],
        "shard_assignments": [
            {
                "shard_id": f"{row.job_type}-001",
                "phase": row.job_type,
                "job_ids": [row.job_id],
                "checkpoint_dependencies": [dependency] if dependency else [],
            }
        ],
        "execution_order": [],
        "created_at": 1.0,
    }
    payload["plan_hash"] = distributed_v2._hash(payload)
    return payload


def test_evaluation_bundle_hardlinks_checkpoint_without_duplicate_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    campaign_id = "figures-8-11-corrected-test"
    campaign_root = tmp_path / "campaigns"
    monkeypatch.setattr(distributed_v2, "CAMPAIGN_ROOT", campaign_root)
    source_contract = tmp_path / "source-contract.json"
    source_contract.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(distributed_v2, "SOURCE_CONTRACT_PATH", source_contract)

    checkpoint = campaign_root / campaign_id / "jobs" / "train" / "internal_checkpoints" / "selected" / "checkpoint.pt"
    checkpoint.parent.mkdir(parents=True)
    checkpoint.write_bytes(b"checkpoint payload")
    checkpoint_hash = sha256(checkpoint.read_bytes()).hexdigest()
    (campaign_root / campaign_id / "checkpoint_registry.json").write_text(
        json.dumps(
            {
                "checkpoints": [
                    {
                        "training_job_id": "train",
                        "checkpoint_id": "selected",
                        "checkpoint_path": str(checkpoint),
                        "checkpoint_hash": checkpoint_hash,
                        "scientifically_complete": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    row = _row(campaign_id=campaign_id, job_id="eval", dependency="train")
    plan = _plan(campaign_id, row, dependency="train")
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    output = tmp_path / "bundles"

    bundles = storage_patch.export_shards_storage_safe(
        campaign_id, plan_path, output, phase="evaluation"
    )
    transported = bundles[0] / "checkpoints" / "train" / "checkpoint.pt"
    assert transported.read_bytes() == checkpoint.read_bytes()
    assert os.stat(transported).st_ino == os.stat(checkpoint).st_ino
    distributed_v2._validate_checksums(bundles[0])


def test_export_refuses_nonempty_destination(tmp_path: Path) -> None:
    output = tmp_path / "bundles"
    output.mkdir()
    (output / "sentinel").write_text("preserve", encoding="utf-8")
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        storage_patch._require_empty_destination(output)
    assert (output / "sentinel").read_text(encoding="utf-8") == "preserve"


def test_result_root_replacement_preserves_new_result_and_removes_only_verified_backup(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "result"
    destination.mkdir()
    (destination / "old.txt").write_text("old", encoding="utf-8")
    staged = tmp_path / "staged"
    staged.mkdir()
    (staged / "new.txt").write_text("new", encoding="utf-8")

    storage_patch._replace_derived_result_root(staged, destination)
    assert not staged.exists()
    assert not (destination / "old.txt").exists()
    assert (destination / "new.txt").read_text(encoding="utf-8") == "new"
    assert not list(tmp_path.glob(".result-previous-*"))


def test_run_shard_result_files_are_hardlinked_and_cwd_survives(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    campaign_id = "figures-8-11-corrected-test"
    row = _row(campaign_id=campaign_id, job_id="train")
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    manifest = {
        "schema_version": 3,
        "campaign_id": campaign_id,
        "shard_id": "training-001",
        "phase": "training",
        "plan_hash": "plan",
        "source_commit": "commit",
        "source_contract_hash": "source",
        "matrix_hash": "matrix",
        "job_ids": [row.job_id],
        "rows": [asdict(row)],
        "checkpoint_dependencies": [],
    }
    (bundle / "shard_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (bundle / "checkpoint_registry.json").write_text(
        json.dumps({"checkpoints": []}), encoding="utf-8"
    )
    (bundle / "checksums.json").write_text(
        json.dumps(distributed_v2._checksums(bundle, exclude=("checksums.json",))),
        encoding="utf-8",
    )

    work = tmp_path / "work"

    def fake_execute_matrix_job(**kwargs):
        campaign = kwargs["campaign_dir"]
        job = campaign / "jobs" / row.job_id
        job.mkdir(parents=True, exist_ok=True)
        (job / "status.json").write_text(
            json.dumps({"status": "completed", "completion_marker": True}),
            encoding="utf-8",
        )
        (job / "completion.marker").write_text("completed\n", encoding="utf-8")
        (job / "training_metrics.csv").write_text(
            "episode,accumulated_reward\n0,-1\n", encoding="utf-8"
        )
        return SimpleNamespace(
            job_id=row.job_id,
            status="completed",
            checkpoint_id=None,
            trace_hash="trace",
        )

    monkeypatch.setattr(production_patch, "execute_matrix_job", fake_execute_matrix_job)
    # The storage-safe runner imports the symbol inside the function from this module.
    result = storage_patch.run_shard_storage_safe(bundle, work)
    assert result["status"] == "completed"
    source = work / campaign_id / "jobs" / row.job_id / "training_metrics.csv"
    transported = work / "results" / "training-001" / "job_outputs" / row.job_id / "training_metrics.csv"
    assert os.stat(source).st_ino == os.stat(transported).st_ino
    assert Path.cwd().is_dir()
