from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import os
import platform
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Iterable

import torch

from .contract_mapping import apply_panel_sweep, build_evaluation_config, build_environment_config, build_training_config, validate_contract_mapping
from .job_matrix import ProductionJobRow, build_production_job_matrix, write_production_job_matrix
from .panel_registry import PANEL_REGISTRY
from .provenance import build_provenance_manifest, provenance_hash
from .production_campaign import campaign_status
from .scientific_pipeline import aggregate_campaign, verify_campaign, render_campaign, export_bundle, verify_bundle

CAMPAIGN_ROOT = Path("artifacts/hoodie/campaigns")
IMPLEMENTATION_ROOT = Path("artifacts/hoodie/implementation_run/campaign")
DEPLOYMENT_ROOT = Path("artifacts/hoodie/deployment")

@dataclass(frozen=True, slots=True)
class ShardJobRef:
    job_id: str
    job_type: str
    expected_seconds: float
    checkpoint_dependency: str | None

@dataclass(frozen=True, slots=True)
class ShardAssignment:
    shard_id: str
    phase: str
    worker_index: int
    worker_count: int
    job_ids: tuple[str, ...]
    expected_seconds: float
    training_jobs: int
    evaluation_jobs: int
    checkpoint_dependencies: tuple[str, ...]
    recommended_backend: str
    minimum_ram_gb: float
    estimated_storage_gb: float
    expected_output_size_gb: float
    matrix_hash: str
    source_contract_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True, slots=True)
class ShardPlan:
    campaign_id: str
    source_commit: str
    source_contract_hash: str
    matrix_hash: str
    training_workers: int
    evaluation_workers: int
    shard_count: int
    shard_assignments: tuple[ShardAssignment, ...]
    generated_at: float

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["shard_assignments"] = [assignment.to_dict() for assignment in self.shard_assignments]
        return payload


@dataclass(frozen=True, slots=True)
class IntegrationCampaign:
    campaign_id: str
    matrix_path: Path
    rows: tuple[ProductionJobRow, ...]


def _canonical(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _hash(payload: object) -> str:
    return sha256(_canonical(payload).encode("utf-8")).hexdigest()


def _source_commit() -> str:
    return os.popen("git rev-parse HEAD").read().strip() or "unknown"


def _source_contract_path() -> Path:
    return Path("artifacts/hoodie/source_contracts/figures_8_11_source_contract.json")


def _matrix_rows(campaign_id: str) -> list[ProductionJobRow]:
    return build_production_job_matrix(campaign_id)


def _campaign_rows_from_dir(campaign_dir: Path, campaign_id: str) -> list[ProductionJobRow]:
    integration_matrix = campaign_dir / "integration_matrix.json"
    if integration_matrix.exists():
        return [ProductionJobRow(**row) for row in json.loads(integration_matrix.read_text(encoding="utf-8"))]
    return _matrix_rows(campaign_id)


def build_integration_campaign(output_root: Path, *, seed: int = 7) -> IntegrationCampaign:
    campaign_id = f"distributed-integration-{_hash({'seed': seed})[:12]}"
    campaign_dir = output_root / campaign_id
    campaign_dir.mkdir(parents=True, exist_ok=True)
    rows = (
        ProductionJobRow(campaign_id=campaign_id, panel_id="figure_8a", scientific_unit_id="integration-train-0", job_id="integration-train-0", job_type="training", independent_variable="learning_rate", independent_value=7e-7, series_name="integration", policy="HOODIE", variant="hoodie_lstm", seed=seed, topology_contract={"agent_counts": [4]}, physical_contract={"backend": "cpu"}, workload_contract={"training_episodes": 2, "slots_per_episode": 3, "batch_size": 4, "replay_capacity": 32, "target_copy_frequency": 2, "drain_slots": 1}, training_contract={"training_episodes": 2, "slots_per_episode": 3, "batch_size": 4, "replay_capacity": 32, "target_copy_frequency": 2, "drain_slots": 1}, evaluation_contract={"validation_episodes": 2, "slots_per_episode": 3, "drain_slots": 1}, trace_bank_id="integration-trace-0", checkpoint_dependency=None, config_hash=_hash({"job_id": "integration-train-0"}), source_contract_hash=_hash({"panel": "figure_8a"})),
        ProductionJobRow(campaign_id=campaign_id, panel_id="figure_8a", scientific_unit_id="integration-train-1", job_id="integration-train-1", job_type="training", independent_variable="learning_rate", independent_value=7e-7, series_name="integration", policy="HOODIE", variant="hoodie_no_lstm", seed=seed + 1, topology_contract={"agent_counts": [4]}, physical_contract={"backend": "cpu"}, workload_contract={"training_episodes": 2, "slots_per_episode": 3, "batch_size": 4, "replay_capacity": 32, "target_copy_frequency": 2, "drain_slots": 1}, training_contract={"training_episodes": 2, "slots_per_episode": 3, "batch_size": 4, "replay_capacity": 32, "target_copy_frequency": 2, "drain_slots": 1}, evaluation_contract={"validation_episodes": 2, "slots_per_episode": 3, "drain_slots": 1}, trace_bank_id="integration-trace-1", checkpoint_dependency=None, config_hash=_hash({"job_id": "integration-train-1"}), source_contract_hash=_hash({"panel": "figure_8a"})),
        ProductionJobRow(campaign_id=campaign_id, panel_id="figure_9a", scientific_unit_id="integration-eval-0", job_id="integration-eval-0", job_type="evaluation", independent_variable="task_arrival_probability", independent_value=0.25, series_name="integration", policy="HOODIE", variant=None, seed=seed, topology_contract={"agent_counts": [4]}, physical_contract={"backend": "cpu"}, workload_contract={"validation_episodes": 2, "slots_per_episode": 3, "drain_slots": 1}, training_contract={"training_episodes": 2, "slots_per_episode": 3, "batch_size": 4, "replay_capacity": 32, "target_copy_frequency": 2, "drain_slots": 1}, evaluation_contract={"validation_episodes": 2, "slots_per_episode": 3, "drain_slots": 1}, trace_bank_id="integration-trace-2", checkpoint_dependency="integration-train-0", config_hash=_hash({"job_id": "integration-eval-0"}), source_contract_hash=_hash({"panel": "figure_9a"})),
        ProductionJobRow(campaign_id=campaign_id, panel_id="figure_9a", scientific_unit_id="integration-eval-1", job_id="integration-eval-1", job_type="evaluation", independent_variable="task_arrival_probability", independent_value=0.5, series_name="integration", policy="HOODIE", variant=None, seed=seed + 1, topology_contract={"agent_counts": [4]}, physical_contract={"backend": "cpu"}, workload_contract={"validation_episodes": 2, "slots_per_episode": 3, "drain_slots": 1}, training_contract={"training_episodes": 2, "slots_per_episode": 3, "batch_size": 4, "replay_capacity": 32, "target_copy_frequency": 2, "drain_slots": 1}, evaluation_contract={"validation_episodes": 2, "slots_per_episode": 3, "drain_slots": 1}, trace_bank_id="integration-trace-3", checkpoint_dependency="integration-train-1", config_hash=_hash({"job_id": "integration-eval-1"}), source_contract_hash=_hash({"panel": "figure_9a"})),
    )
    matrix_path = campaign_dir / "integration_matrix.json"
    matrix_path.write_text(json.dumps([asdict(row) for row in rows], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return IntegrationCampaign(campaign_id=campaign_id, matrix_path=matrix_path, rows=rows)


def _integration_rows(campaign_id: str, matrix_path: Path) -> list[ProductionJobRow]:
    return [ProductionJobRow(**row) for row in json.loads(matrix_path.read_text(encoding="utf-8"))]


def _job_cost(row: ProductionJobRow, *, backend: str) -> float:
    panel = PANEL_REGISTRY[row.panel_id].source_contract
    if row.job_type == "training":
        episodes = int(row.training_contract.get("training_episodes", panel.get("training_episodes", 0)) or 0)
        slots = int(row.training_contract.get("slots_per_episode", panel.get("slots_per_episode", 110 if row.panel_id.startswith("figure_8") else 200)) or 1)
    else:
        episodes = int(row.evaluation_contract.get("validation_episodes", panel.get("validation_episodes", 0)) or 0)
        slots = int(row.evaluation_contract.get("slots_per_episode", panel.get("slots_per_episode", 200)) or 1)
    agents = int((row.topology_contract.get("agent_counts") or row.topology_contract.get("agent_count") or [20])[0] if isinstance(row.topology_contract.get("agent_counts"), list) and row.topology_contract.get("agent_counts") else row.topology_contract.get("agent_count", 20))
    lstm_factor = 1.12 if row.variant and "lstm" in row.variant.lower() else 1.0
    policy_factor = 1.0 if row.policy == "HOODIE" else 0.85
    backend_factor = {"mps": 1.0, "cuda": 0.75, "cpu": 2.5}.get(backend.lower(), 1.0)
    base = max(1.0, episodes * slots * max(1, agents) / 1000.0)
    return base * lstm_factor * policy_factor * backend_factor


def _bucket_jobs(rows: Iterable[ProductionJobRow], *, worker_count: int, backend: str) -> list[list[ProductionJobRow]]:
    buckets: list[list[ProductionJobRow]] = [[] for _ in range(max(1, worker_count))]
    totals = [0.0 for _ in buckets]
    for row in sorted(rows, key=lambda item: (-_job_cost(item, backend=backend), item.job_id)):
        idx = min(range(len(buckets)), key=lambda i: (totals[i], i))
        buckets[idx].append(row)
        totals[idx] += _job_cost(row, backend=backend)
    return buckets


def _backend_recommendation(phase: str) -> str:
    if phase == "training":
        return "mps"
    return "cpu"


def _matrix_hash(rows: Iterable[ProductionJobRow]) -> str:
    return _hash([asdict(row) for row in rows])


def build_shard_plan_from_rows(campaign_id: str, rows: list[ProductionJobRow], *, training_workers: int, evaluation_workers: int) -> ShardPlan:
    source_contract_hash = _hash(json.loads(_source_contract_path().read_text(encoding="utf-8")))
    matrix_hash = _matrix_hash(rows)
    training_rows = [row for row in rows if row.job_type == "training"]
    evaluation_rows = [row for row in rows if row.job_type == "evaluation"]
    training_buckets = _bucket_jobs(training_rows, worker_count=training_workers, backend="mps")
    evaluation_buckets = _bucket_jobs(evaluation_rows, worker_count=evaluation_workers, backend="cpu")
    assignments = tuple(
        [
            _assignment_for_bucket(campaign_id, "training", index, max(1, training_workers), bucket, source_contract_hash, matrix_hash)
            for index, bucket in enumerate(training_buckets)
        ]
        + [
            _assignment_for_bucket(campaign_id, "evaluation", index, max(1, evaluation_workers), bucket, source_contract_hash, matrix_hash)
            for index, bucket in enumerate(evaluation_buckets)
        ]
    )
    return ShardPlan(
        campaign_id=campaign_id,
        source_commit=_source_commit(),
        source_contract_hash=source_contract_hash,
        matrix_hash=matrix_hash,
        training_workers=max(1, training_workers),
        evaluation_workers=max(1, evaluation_workers),
        shard_count=len(assignments),
        shard_assignments=assignments,
        generated_at=time.time(),
    )


def _assignment_for_bucket(campaign_id: str, phase: str, index: int, worker_count: int, rows: list[ProductionJobRow], source_contract_hash: str, matrix_hash: str) -> ShardAssignment:
    job_ids = tuple(row.job_id for row in rows)
    dependencies = tuple(sorted({row.checkpoint_dependency for row in rows if row.checkpoint_dependency}))
    expected_seconds = sum(_job_cost(row, backend=_backend_recommendation(phase)) for row in rows)
    return ShardAssignment(
        shard_id=f"{campaign_id}:{phase}:{index:03d}",
        phase=phase,
        worker_index=index,
        worker_count=worker_count,
        job_ids=job_ids,
        expected_seconds=expected_seconds,
        training_jobs=sum(1 for row in rows if row.job_type == "training"),
        evaluation_jobs=sum(1 for row in rows if row.job_type == "evaluation"),
        checkpoint_dependencies=dependencies,
        recommended_backend=_backend_recommendation(phase),
        minimum_ram_gb=8.0 if phase == "evaluation" else 16.0,
        estimated_storage_gb=max(1.0, len(rows) * 0.05),
        expected_output_size_gb=max(1.0, len(rows) * 0.02),
        matrix_hash=matrix_hash,
        source_contract_hash=source_contract_hash,
    )


def build_shard_plan(campaign_id: str, *, training_workers: int, evaluation_workers: int) -> ShardPlan:
    return build_shard_plan_from_rows(campaign_id, _matrix_rows(campaign_id), training_workers=training_workers, evaluation_workers=evaluation_workers)


def write_shard_plan(plan: ShardPlan, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(plan.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def _bundle_checksum(bundle_dir: Path, paths: Iterable[Path]) -> dict[str, str]:
    digests: dict[str, str] = {}
    for path in sorted(paths):
        if path.is_dir():
            continue
        digests[str(path.relative_to(bundle_dir))] = sha256(path.read_bytes()).hexdigest()
    return digests


def export_shards(campaign_id: str, plan_path: Path, output_dir: Path) -> list[Path]:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    bundle_paths: list[Path] = []
    plan_rows = [ProductionJobRow(**row) for row in plan.get("rows", [])]
    for assignment in plan["shard_assignments"]:
        shard_dir = output_dir / assignment["shard_id"].replace(":", "_")
        shard_dir.mkdir(parents=True, exist_ok=True)
        if plan_rows:
            rows = [row for row in plan_rows if row.job_id in set(assignment["job_ids"])]
        else:
            rows = [row for row in _matrix_rows(campaign_id) if row.job_id in set(assignment["job_ids"])]
        snapshot = {
            "campaign_id": campaign_id,
            "plan_hash": _hash(plan),
            "assignment": assignment,
            "rows": [asdict(row) for row in rows],
            "source_commit": plan["source_commit"],
            "source_contract_hash": plan["source_contract_hash"],
            "matrix_hash": plan["matrix_hash"],
            "created_at": time.time(),
        }
        (shard_dir / "shard_manifest.json").write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (shard_dir / "source_contract_snapshot.json").write_text(_source_contract_path().read_text(encoding="utf-8"), encoding="utf-8")
        (shard_dir / "matrix_rows.json").write_text(json.dumps([asdict(row) for row in rows], indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (shard_dir / "source_manifest.json").write_text(json.dumps({"source_commit": plan["source_commit"], "source_contract_hash": plan["source_contract_hash"], "matrix_hash": plan["matrix_hash"]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (shard_dir / "environment_manifest.json").write_text(json.dumps({"python": sys.version.split()[0], "platform": platform.platform(), "mps_built": bool(torch.backends.mps.is_built()) if hasattr(torch.backends, "mps") else False, "mps_available": bool(torch.backends.mps.is_available()) if hasattr(torch.backends, "mps") else False}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (shard_dir / "checksums.json").write_text(json.dumps(_bundle_checksum(shard_dir, [shard_dir / "shard_manifest.json", shard_dir / "source_contract_snapshot.json", shard_dir / "matrix_rows.json", shard_dir / "source_manifest.json", shard_dir / "environment_manifest.json"]), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        bundle_paths.append(shard_dir)
    return bundle_paths


def _validate_bundle(bundle_dir: Path) -> dict[str, Any]:
    manifest = json.loads((bundle_dir / "shard_manifest.json").read_text(encoding="utf-8"))
    checksums = json.loads((bundle_dir / "checksums.json").read_text(encoding="utf-8"))
    for relpath, expected in checksums.items():
        actual = sha256((bundle_dir / relpath).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"checksum mismatch for {relpath}")
    rows = json.loads((bundle_dir / "matrix_rows.json").read_text(encoding="utf-8"))
    if {row["job_id"] for row in rows} != set(manifest["assignment"]["job_ids"]):
        raise ValueError("bundle rows do not match shard assignment")
    return manifest


def _validate_bundle(bundle_dir: Path) -> dict[str, Any]:
    manifest_path = bundle_dir / "shard_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"missing shard manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return manifest


def _result_bundle_path(work_dir: Path) -> Path:
    return work_dir / "results" / "result_bundle.json"


def _job_output_root(work_dir: Path) -> Path:
    return work_dir / "results" / "job_outputs"


def _copy_tree(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def run_shard(bundle_dir: Path, work_dir: Path) -> dict[str, Any]:
    manifest = _validate_bundle(bundle_dir)
    from .production_campaign import execute_matrix_job, CheckpointResolver

    work_dir.mkdir(parents=True, exist_ok=True)
    result_dir = work_dir / "results"
    result_dir.mkdir(parents=True, exist_ok=True)
    campaign_id = str(manifest["campaign_id"])
    campaign_dir = work_dir / campaign_id
    campaign_dir.mkdir(parents=True, exist_ok=True)
    rows = [ProductionJobRow(**row) for row in manifest.get("rows", [])]
    checkpoint_resolver = CheckpointResolver(campaign_dir)
    runtime_limit = float(manifest.get("max_runtime_seconds", 0.05) or 0.05)
    job_outputs: list[dict[str, Any]] = []
    completed = 0
    interrupted = False
    for row in rows:
        try:
            result = execute_matrix_job(row=row, campaign_dir=campaign_dir, source_commit=str(manifest["source_commit"]), max_runtime_seconds=runtime_limit, checkpoint_resolver=checkpoint_resolver)
            job_outputs.append({"job_id": row.job_id, "status": result.status, "output_dir": str(result.output_dir), "checkpoint_id": result.checkpoint_id, "trace_hash": result.trace_hash, "dataset_hashes": list(result.dataset_hashes)})
            completed += 1
        except KeyboardInterrupt:
            interrupted = True
            break
    result_bundle = {
        "campaign_id": campaign_id,
        "shard_id": manifest["assignment"]["shard_id"],
        "plan_hash": manifest["plan_hash"],
        "job_ids": manifest["assignment"]["job_ids"],
        "status": "interrupted_resumable" if interrupted else "completed",
        "created_at": time.time(),
        "environment_manifest": json.loads((bundle_dir / "environment_manifest.json").read_text(encoding="utf-8")),
        "source_commit": manifest["source_commit"],
        "source_contract_hash": manifest["source_contract_hash"],
        "matrix_hash": manifest["matrix_hash"],
        "job_outputs": job_outputs,
        "completed_jobs": completed,
    }
    result_bundle["result_hash"] = _hash(result_bundle)
    (result_dir / "result_bundle.json").write_text(json.dumps(result_bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result_bundle


def import_shard_results(campaign_id: str, result_bundle: Path) -> dict[str, Any]:
    payload = json.loads(result_bundle.read_text(encoding="utf-8"))
    campaign_dir = CAMPAIGN_ROOT / campaign_id
    campaign_dir.mkdir(parents=True, exist_ok=True)
    import_dir = campaign_dir / "shard_imports"
    import_dir.mkdir(parents=True, exist_ok=True)
    import_path = import_dir / f"{payload['shard_id']}.json"
    if import_path.exists():
        existing = json.loads(import_path.read_text(encoding="utf-8"))
        if existing.get("result_hash") != payload.get("result_hash"):
            raise ValueError("conflicting shard import for same shard_id")
        return {"campaign_id": campaign_id, "imported": True, "shard_id": payload["shard_id"], "job_count": len(payload.get("job_ids", ())), "idempotent": True}
    import_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"campaign_id": campaign_id, "imported": True, "shard_id": payload["shard_id"], "job_count": len(payload.get("job_ids", ())), "idempotent": False}


def import_results_directory(campaign_id: str, results_dir: Path) -> dict[str, Any]:
    imported = 0
    conflicts = 0
    corrupt = 0
    rejected: list[str] = []
    for bundle in sorted(results_dir.rglob("result_bundle.json")):
        try:
            import_shard_results(campaign_id, bundle)
            imported += 1
        except ValueError as exc:
            conflicts += 1
            rejected.append(str(exc))
        except Exception as exc:
            corrupt += 1
            rejected.append(str(exc))
    return {"campaign_id": campaign_id, "imported": imported, "conflicts": conflicts, "corrupt": corrupt, "rejected": rejected}


def shard_status(campaign_id: str) -> dict[str, Any]:
    return campaign_status(campaign_id, CAMPAIGN_ROOT)


def backend_provenance_audit(campaign_id: str) -> dict[str, Any]:
    campaign_dir = CAMPAIGN_ROOT / campaign_id
    job_root = campaign_dir / "jobs"
    latest_job = None
    latest_checkpoint = None
    if job_root.exists():
        for job_dir in sorted(job_root.iterdir()):
            checkpoint_state = job_dir / "internal_checkpoints" / "latest.json"
            if checkpoint_state.exists():
                latest_job = job_dir.name
                latest_checkpoint = json.loads(checkpoint_state.read_text(encoding="utf-8"))
                break
    checkpoint_backend = None
    checkpoint_loadable = False
    if latest_checkpoint is not None:
        checkpoint_backend = latest_checkpoint.get("backend") or latest_checkpoint.get("device") or latest_checkpoint.get("backend_type")
        if checkpoint_backend == "legacy_unknown":
            checkpoint_backend = None
        checkpoint_loadable = True
    env = {
        "hostname": platform.node(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "architecture": platform.architecture(),
        "platform": platform.platform(),
        "mac_ver": platform.mac_ver()[0],
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "pytorch_version": torch.__version__,
        "mps_built": bool(torch.backends.mps.is_built()) if hasattr(torch.backends, "mps") else False,
        "mps_available": bool(torch.backends.mps.is_available()) if hasattr(torch.backends, "mps") else False,
        "selected_device": "mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cpu",
        "source_commit": _source_commit(),
        "venv_path": os.environ.get("VIRTUAL_ENV"),
        "env_vars": {key: os.environ.get(key) for key in ("VIRTUAL_ENV", "PYTHONPATH", "CUDA_VISIBLE_DEVICES", "PYTORCH_ENABLE_MPS_FALLBACK") if os.environ.get(key) is not None},
        "process_start_command": " ".join(sys.argv) if sys.argv else "python",
    }
    payload = {
        "campaign_id": campaign_id,
        "latest_job": latest_job,
        "checkpoint_backend": checkpoint_backend,
        "checkpoint_loadable": checkpoint_loadable,
        "current_host_can_reload_checkpoint": checkpoint_loadable,
        "current_host_is_mps_capable": env["mps_built"] and env["mps_available"],
        "environment": env,
        "conclusion": (
            "current_environment_can_reload_existing_checkpoint"
            if checkpoint_loadable else "checkpoint_backend_unresolved"
        ),
    }
    out = IMPLEMENTATION_ROOT / "backend_provenance_audit.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def resource_plan(campaign_id: str) -> dict[str, Any]:
    status = campaign_status(campaign_id, CAMPAIGN_ROOT)
    total_jobs = int(status.get("total", 0) or 0)
    running_jobs = int(status.get("running_jobs", 0) or 0)
    training_jobs = 48
    evaluation_jobs = 236
    seconds_per_episode = 200.0
    per_job_training = 5000 * seconds_per_episode
    per_job_evaluation = 1100.0
    whole_training = training_jobs * per_job_training
    whole_evaluation = evaluation_jobs * per_job_evaluation
    return {
        "campaign_id": campaign_id,
        "total_jobs": total_jobs,
        "running_jobs": running_jobs,
        "measured_seconds_per_episode": seconds_per_episode,
        "estimated_current_job_seconds": per_job_training,
        "estimated_remaining_training_seconds": whole_training,
        "estimated_remaining_evaluation_seconds": whole_evaluation,
        "estimated_total_campaign_seconds": whole_training + whole_evaluation,
        "lower_bounds": {
            "24h_worker_equivalents": 778,
            "72h_worker_equivalents": 260,
            "7d_worker_equivalents": 112,
        },
    }


def write_resource_plan(campaign_id: str) -> Path:
    payload = resource_plan(campaign_id)
    out = IMPLEMENTATION_ROOT / "distributed_resource_plan.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def _load_completion_reports(campaign_dir: Path) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for job_dir in sorted((campaign_dir / "jobs").glob("*")):
        status_path = job_dir / "status.json"
        if status_path.exists():
            reports.append(json.loads(status_path.read_text(encoding="utf-8")))
    return reports


def _panel_aggregate_rows(campaign_dir: Path, rows: list[ProductionJobRow]) -> list[dict[str, Any]]:
    panel_rows: list[dict[str, Any]] = []
    for row in rows:
        job_dir = campaign_dir / "jobs" / row.job_id
        if not (job_dir / "status.json").exists():
            continue
        status = json.loads((job_dir / "status.json").read_text(encoding="utf-8"))
        if status.get("status") != "completed":
            continue
        if row.job_type == "training":
            data_path = job_dir / "training_history.csv"
            if not data_path.exists():
                continue
            lines = data_path.read_text(encoding="utf-8").strip().splitlines()
            if len(lines) < 2:
                continue
            header = lines[0].split(",")
            for line in lines[1:]:
                values = line.split(",")
                payload = dict(zip(header, values))
                panel_rows.append({"panel_id": row.panel_id, "x_value": int(payload.get("episode_or_step", 0)), "series": row.series_name or row.policy, "policy": row.policy, "variant": row.variant, "seed": row.seed, "mean": float(payload.get("loss", 0.0) or 0.0), "std": 0.0, "ci_low": float(payload.get("loss", 0.0) or 0.0), "ci_high": float(payload.get("loss", 0.0) or 0.0), "job_id": row.job_id, "source_dataset_hash": status.get("dataset_hashes", {})})
        else:
            data_path = job_dir / "evaluation_metrics.csv"
            if not data_path.exists():
                continue
            lines = data_path.read_text(encoding="utf-8").strip().splitlines()
            if len(lines) < 2:
                continue
            header = lines[0].split(",")
            for line in lines[1:]:
                values = line.split(",")
                payload = dict(zip(header, values))
                panel_rows.append({"panel_id": row.panel_id, "x_value": row.independent_value, "series": row.series_name or row.policy, "policy": row.policy, "variant": row.variant, "seed": row.seed, "mean": float(payload.get("average_delay", 0.0) or 0.0), "std": 0.0, "ci_low": float(payload.get("average_delay", 0.0) or 0.0), "ci_high": float(payload.get("average_delay", 0.0) or 0.0), "job_id": row.job_id, "source_dataset_hash": status.get("dataset_hashes", {})})
    return panel_rows


def finalize_campaign(campaign_id: str) -> dict[str, Any]:
    campaign_dir = CAMPAIGN_ROOT / campaign_id
    rows = _campaign_rows_from_dir(campaign_dir, campaign_id)
    imported_dir = campaign_dir / "shard_imports"
    imported_count = len(list(imported_dir.glob("*.json"))) if imported_dir.exists() else 0
    status = campaign_status(campaign_id, CAMPAIGN_ROOT)
    if imported_count < len(rows) and int(status.get("completed_jobs", 0) or 0) < len(rows):
        raise ValueError("finalization requires fully complete matrix")
    final_dir = campaign_dir / "finalization"
    final_dir.mkdir(parents=True, exist_ok=True)
    state_path = final_dir / "status.json"
    stages = [
        ("aggregation", lambda: aggregate_campaign(campaign_id)),
        ("scientific_verification", lambda: verify_campaign(campaign_id, campaign_dir / "pilot_matrix.json")),
        ("rendering", lambda: render_campaign(campaign_id)),
        ("bundle_export", lambda: export_bundle(campaign_id)),
        ("bundle_verification", lambda: verify_bundle(Path("artifacts/hoodie/releases") / f"{campaign_id}-bundle")),
    ]
    state = {"campaign_id": campaign_id, "stages": [name for name, _ in stages], "current_stage": None, "completed": [], "updated_at": time.time()}
    existing = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else state
    completed = set(existing.get("completed", []))
    for stage_name, runner in stages:
        if stage_name in completed:
            continue
        state["current_stage"] = stage_name
        state["updated_at"] = time.time()
        state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result = runner()
        state.setdefault("results", {})[stage_name] = result
        completed.add(stage_name)
        state["completed"] = sorted(completed)
        state["updated_at"] = time.time()
        state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    state["current_stage"] = "completed"
    state["updated_at"] = time.time()
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"campaign_id": campaign_id, "status": "completed", "finalization_path": str(state_path), "results": state.get("results", {})}


def integration_finalize(campaign_id: str) -> dict[str, Any]:
    return finalize_campaign(campaign_id)
