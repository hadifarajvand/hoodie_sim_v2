from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json
from pathlib import Path
from typing import Any, Iterable

from .job_matrix import ProductionJobRow
from .matrix_patch import install_matrix_patch
from . import distributed_v2 as v2

CAMPAIGN_ROOT = v2.CAMPAIGN_ROOT
IMPLEMENTATION_ROOT = Path("artifacts/hoodie/implementation_run/campaign")
DEPLOYMENT_ROOT = Path("artifacts/hoodie/deployment")


@dataclass(frozen=True, slots=True)
class ShardJobRef:
    job_id: str


@dataclass(frozen=True, slots=True)
class ShardAssignment:
    shard_id: str
    phase: str
    job_ids: tuple[str, ...]
    checkpoint_dependencies: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ShardPlan:
    campaign_id: str
    source_commit: str
    source_contract_hash: str
    matrix_hash: str
    plan_hash: str
    total_jobs: int
    training_jobs: int
    evaluation_jobs: int
    rows: tuple[dict[str, Any], ...]
    shard_assignments: tuple[ShardAssignment, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 2,
            "campaign_id": self.campaign_id,
            "source_commit": self.source_commit,
            "source_contract_hash": self.source_contract_hash,
            "matrix_hash": self.matrix_hash,
            "plan_hash": self.plan_hash,
            "total_jobs": self.total_jobs,
            "training_jobs": self.training_jobs,
            "evaluation_jobs": self.evaluation_jobs,
            "rows": list(self.rows),
            "shard_assignments": [asdict(item) for item in self.shard_assignments],
            "execution_order": [
                "training",
                "import-training",
                "evaluation",
                "import-evaluation",
                "finalize",
            ],
        }


def _wrap_plan(payload: dict[str, Any]) -> ShardPlan:
    return ShardPlan(
        campaign_id=str(payload["campaign_id"]),
        source_commit=str(payload["source_commit"]),
        source_contract_hash=str(payload["source_contract_hash"]),
        matrix_hash=str(payload["matrix_hash"]),
        plan_hash=str(payload["plan_hash"]),
        total_jobs=int(payload["total_jobs"]),
        training_jobs=int(payload["training_jobs"]),
        evaluation_jobs=int(payload["evaluation_jobs"]),
        rows=tuple(payload["rows"]),
        shard_assignments=tuple(
            ShardAssignment(
                shard_id=str(item["shard_id"]),
                phase=str(item["phase"]),
                job_ids=tuple(item["job_ids"]),
                checkpoint_dependencies=tuple(item.get("checkpoint_dependencies", ())),
            )
            for item in payload["shard_assignments"]
        ),
    )


def build_shard_plan(
    campaign_id: str,
    *,
    training_workers: int | None = None,
    evaluation_workers: int | None = None,
    training_shards: int | None = None,
    evaluation_shards: int | None = None,
    matrix_path: Path | None = None,
) -> ShardPlan:
    payload = v2.build_shard_plan(
        campaign_id,
        training_shards=training_shards or training_workers or 17,
        evaluation_shards=evaluation_shards or evaluation_workers or 48,
        matrix_path=matrix_path,
    )
    return _wrap_plan(payload)


def build_shard_plan_from_rows(
    campaign_id: str,
    rows: Iterable[ProductionJobRow],
    *,
    training_workers: int = 1,
    evaluation_workers: int = 1,
) -> ShardPlan:
    temporary = IMPLEMENTATION_ROOT / f"{campaign_id}-temporary-matrix.json"
    temporary.parent.mkdir(parents=True, exist_ok=True)
    temporary.write_text(
        json.dumps([asdict(row) for row in rows], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return build_shard_plan(
        campaign_id,
        training_workers=training_workers,
        evaluation_workers=evaluation_workers,
        matrix_path=temporary,
    )


def write_shard_plan(plan: ShardPlan | dict[str, Any], output_path: Path) -> Path:
    payload = plan.to_dict() if isinstance(plan, ShardPlan) else plan
    # Recreate the exact v2 plan-hash payload if a compatibility object was used.
    if isinstance(plan, ShardPlan):
        payload = {
            **payload,
            "created_at": 0.0,
        }
        payload.pop("plan_hash", None)
        payload["plan_hash"] = v2._hash(payload)
    return v2.write_shard_plan(payload, output_path)


def export_shards(
    campaign_id: str,
    plan_path: Path,
    output_dir: Path,
    *,
    phase: str | None = None,
) -> list[Path]:
    return v2.export_shards(
        campaign_id, plan_path, output_dir, phase=phase
    )


def run_shard(
    bundle_dir: Path,
    work_dir: Path,
    *,
    max_runtime_seconds: float | None = None,
) -> dict[str, Any]:
    return v2.run_shard(
        bundle_dir, work_dir, max_runtime_seconds=max_runtime_seconds
    )


def import_shard_results(campaign_id: str, result: Path) -> dict[str, Any]:
    root = result.parent if result.is_file() else result
    return v2.import_shard_results(campaign_id, root)


def import_results_directory(campaign_id: str, results_dir: Path) -> dict[str, Any]:
    return v2.import_results_directory(campaign_id, results_dir)


def shard_status(campaign_id: str) -> dict[str, Any]:
    return v2.shard_status(campaign_id)


def backend_provenance_audit(campaign_id: str) -> dict[str, Any]:
    return v2.backend_provenance_audit(campaign_id)


def resource_plan(campaign_id: str, matrix_path: Path | None = None) -> dict[str, Any]:
    return v2.resource_plan(campaign_id, matrix_path)


def write_resource_plan(payload: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return output_path


def finalize_campaign(campaign_id: str) -> dict[str, Any]:
    result = v2.finalize(campaign_id)
    return {"status": "completed", **result}


def finalize(campaign_id: str) -> dict[str, Any]:
    return finalize_campaign(campaign_id)


@dataclass(frozen=True, slots=True)
class IntegrationCampaign:
    campaign_id: str
    matrix_path: Path
    rows: tuple[ProductionJobRow, ...]


def build_integration_campaign(output_dir: Path, seed: int = 7) -> IntegrationCampaign:
    """Build a tiny dependency-valid campaign for transport/integration tests only."""
    install_matrix_patch()
    from . import job_matrix

    base = job_matrix.build_production_job_matrix("distributed-integration-v2")
    training = next(row for row in base if row.job_id == job_matrix.CANONICAL_CHECKPOINT_JOB_ID)
    training = replace(
        training,
        seed=seed,
        training_contract={
            **training.training_contract,
            "training_episodes": 2,
            "slots_per_episode": 4,
            "decision_slots": 3,
            "drain_slots": 1,
            "batch_size": 2,
            "replay_capacity": 16,
            "target_copy_frequency": 2,
        },
        workload_contract={
            **training.workload_contract,
            "training_episodes": 2,
            "slots_per_episode": 4,
            "decision_slots": 3,
            "drain_slots": 1,
            "task_arrival_probability": 0.2,
        },
    )
    evaluation = next(
        row
        for row in base
        if row.job_type == "evaluation"
        and row.policy == "HOODIE"
        and row.checkpoint_dependency == job_matrix.CANONICAL_CHECKPOINT_JOB_ID
    )
    evaluation = replace(
        evaluation,
        seed=seed,
        evaluation_contract={
            **evaluation.evaluation_contract,
            "validation_episodes": 2,
            "slots_per_episode": 4,
            "decision_slots": 3,
            "drain_slots": 1,
        },
        workload_contract={
            **evaluation.workload_contract,
            "validation_episodes": 2,
            "slots_per_episode": 4,
            "decision_slots": 3,
            "drain_slots": 1,
            "task_arrival_probability": 0.2,
        },
    )
    rows = (training, evaluation)
    matrix_path = output_dir / "integration_matrix.json"
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_path.write_text(
        json.dumps([asdict(row) for row in rows], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return IntegrationCampaign(
        campaign_id="distributed-integration-v2",
        matrix_path=matrix_path,
        rows=rows,
    )
