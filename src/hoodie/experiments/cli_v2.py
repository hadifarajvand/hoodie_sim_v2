from __future__ import annotations

import argparse
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import shutil
import sys
from typing import Any

from .campaign import campaign_status, resume_production_campaign, run_production_campaign
from .contract_mapping import validate_contract_mapping
from .distributed_v2 import (
    backend_provenance_audit,
    build_shard_plan,
    export_shards,
    finalize,
    import_results_directory,
    import_shard_results,
    resource_plan,
    run_shard,
    shard_status,
    write_shard_plan,
)
from .job_matrix import validate_production_job_matrix
from .matrix_patch import install_matrix_patch
from .panel_registry import PANEL_REGISTRY
from .preflight import run_preflight
from .scientific_pipeline import (
    aggregate_campaign,
    export_bundle,
    render_campaign,
    verify_bundle,
    verify_campaign,
)


def _print(payload: object) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def _matrix_hash(rows: list[object]) -> str:
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(payload.encode("utf-8")).hexdigest()


def _campaign_id(rows_payload: list[dict[str, Any]]) -> str:
    scientific_payload = [
        {key: value for key, value in row.items() if key != "campaign_id"}
        for row in rows_payload
    ]
    return f"figures-8-11-corrected-{_matrix_hash(scientific_payload)[:12]}"


def _plan(args: argparse.Namespace) -> dict[str, Any]:
    install_matrix_patch()
    from . import job_matrix

    provisional = job_matrix.build_production_job_matrix("campaign-pending")
    payload = [asdict(row) for row in provisional]
    campaign_id = args.campaign_id or _campaign_id(payload)
    rows = job_matrix.build_production_job_matrix(campaign_id)
    counts = validate_production_job_matrix(rows)
    matrix_path = Path(args.matrix)
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_path.write_text(
        json.dumps([asdict(row) for row in rows], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    campaign_dir = Path(args.campaign_root) / campaign_id
    campaign_dir.mkdir(parents=True, exist_ok=True)
    (campaign_dir / "job_plan.json").write_text(matrix_path.read_text(encoding="utf-8"), encoding="utf-8")
    plan = build_shard_plan(
        campaign_id,
        training_shards=args.training_shards,
        evaluation_shards=args.evaluation_shards,
        matrix_path=matrix_path,
    )
    shard_plan_path = Path(args.shard_plan)
    write_shard_plan(plan, shard_plan_path)
    return {
        "campaign_id": campaign_id,
        "matrix_path": str(matrix_path),
        "matrix_hash": plan["matrix_hash"],
        "shard_plan_path": str(shard_plan_path),
        "shard_plan_hash": plan["plan_hash"],
        **counts,
        "next_step": "Run preflight and tests before exporting or executing shards.",
    }


def _validate_contracts(args: argparse.Namespace) -> dict[str, Any]:
    install_matrix_patch()
    from . import job_matrix

    rows = (
        job_matrix.build_production_job_matrix(args.campaign_id)
        if args.matrix is None
        else _load_matrix(Path(args.matrix))
    )
    errors: dict[str, list[str]] = {}
    for row in rows:
        mismatches = validate_contract_mapping(
            row, PANEL_REGISTRY[row.panel_id].source_contract
        )
        if mismatches:
            errors[row.job_id] = mismatches
    if errors:
        raise ValueError(f"contract mapping failed for {len(errors)} jobs: {errors}")
    return {"valid": True, "jobs_checked": len(rows), "campaign_id": args.campaign_id}


def _load_matrix(path: Path):
    from dataclasses import fields
    from .job_matrix import ProductionJobRow

    allowed = {field.name for field in fields(ProductionJobRow)}
    return [
        ProductionJobRow(**{key: value for key, value in row.items() if key in allowed})
        for row in json.loads(path.read_text(encoding="utf-8"))
    ]


def _clean(args: argparse.Namespace) -> dict[str, Any]:
    if not args.confirm:
        raise ValueError("clean requires --confirm")
    path = Path(args.path).resolve()
    allowed_root = Path("artifacts/hoodie").resolve()
    if allowed_root not in path.parents and path != allowed_root:
        raise ValueError("clean is restricted to artifacts/hoodie")
    if path.exists():
        shutil.rmtree(path)
    return {"removed": str(path)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m hoodie.experiments")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("preflight")
    sub.add_parser("list-panels")

    validate = sub.add_parser("validate-contracts")
    validate.add_argument("--campaign-id", default="figures-8-11-contract-check")
    validate.add_argument("--matrix")

    plan = sub.add_parser("plan")
    plan.add_argument("--campaign-id")
    plan.add_argument(
        "--matrix",
        default="artifacts/hoodie/implementation_run/campaign/expected_production_job_matrix_v2.json",
    )
    plan.add_argument(
        "--shard-plan",
        default="artifacts/hoodie/implementation_run/campaign/shard_plan_v2.json",
    )
    plan.add_argument("--campaign-root", default="artifacts/hoodie/campaigns")
    plan.add_argument("--training-shards", type=int, default=17)
    plan.add_argument("--evaluation-shards", type=int, default=48)

    for name in ("run", "resume"):
        command = sub.add_parser(name)
        command.add_argument("--campaign-id", required=True)
        command.add_argument("--output-dir", default="artifacts/hoodie/campaigns")
        command.add_argument("--matrix")
        command.add_argument("--max-jobs", type=int)
        command.add_argument("--max-runtime-seconds", type=float)
        command.add_argument("--job-id")
        command.add_argument("--allow-paused-recovery", action="store_true")

    status = sub.add_parser("status")
    status.add_argument("--campaign-id", required=True)
    status.add_argument("--output-dir", default="artifacts/hoodie/campaigns")
    status.add_argument("--matrix")

    for name in ("aggregate", "verify", "render", "export-bundle", "finalize"):
        command = sub.add_parser(name)
        command.add_argument("--campaign-id", required=True)

    verify_release = sub.add_parser("verify-bundle")
    verify_release.add_argument("--bundle", required=True)

    shard_plan = sub.add_parser("shard-plan")
    shard_plan.add_argument("--campaign-id", required=True)
    shard_plan.add_argument("--matrix")
    shard_plan.add_argument("--training-shards", type=int, default=17)
    shard_plan.add_argument("--evaluation-shards", type=int, default=48)
    shard_plan.add_argument("--output", required=True)

    export = sub.add_parser("export-shards")
    export.add_argument("--campaign-id", required=True)
    export.add_argument("--plan", required=True)
    export.add_argument("--output-dir", required=True)
    export.add_argument("--phase", choices=("training", "evaluation"))

    run_worker = sub.add_parser("run-shard")
    run_worker.add_argument("--bundle", required=True)
    run_worker.add_argument("--work-dir", required=True)
    run_worker.add_argument("--max-runtime-seconds", type=float)

    import_one = sub.add_parser("import-shard-results")
    import_one.add_argument("--campaign-id", required=True)
    import_one.add_argument("--result-dir", required=True)

    import_many = sub.add_parser("import-results-directory")
    import_many.add_argument("--campaign-id", required=True)
    import_many.add_argument("--results-dir", required=True)

    shard_state = sub.add_parser("shard-status")
    shard_state.add_argument("--campaign-id", required=True)

    audit = sub.add_parser("backend-audit")
    audit.add_argument("--campaign-id", required=True)

    resources = sub.add_parser("resource-plan")
    resources.add_argument("--campaign-id", required=True)
    resources.add_argument("--matrix")

    clean = sub.add_parser("clean")
    clean.add_argument("--path", required=True)
    clean.add_argument("--confirm", action="store_true")
    return parser


def dispatch(args: argparse.Namespace) -> object:
    if args.command == "preflight":
        return run_preflight()
    if args.command == "list-panels":
        return {
            panel_id: {
                "metric": contract.spec.metric,
                "independent_variable": contract.spec.independent_variable,
                "evaluation_required": contract.spec.evaluation_required,
            }
            for panel_id, contract in PANEL_REGISTRY.items()
        }
    if args.command == "validate-contracts":
        return _validate_contracts(args)
    if args.command == "plan":
        return _plan(args)
    if args.command in {"run", "resume"}:
        function = run_production_campaign if args.command == "run" else resume_production_campaign
        return function(
            campaign_id=args.campaign_id,
            output_dir=Path(args.output_dir),
            matrix_path=Path(args.matrix) if args.matrix else None,
            max_jobs=args.max_jobs,
            max_runtime_seconds=args.max_runtime_seconds,
            job_id=args.job_id,
            allow_paused_recovery=args.allow_paused_recovery,
        )
    if args.command == "status":
        return campaign_status(
            args.campaign_id,
            Path(args.output_dir),
            matrix_path=Path(args.matrix) if args.matrix else None,
        )
    if args.command == "aggregate":
        return aggregate_campaign(args.campaign_id)
    if args.command == "verify":
        return verify_campaign(args.campaign_id)
    if args.command == "render":
        return render_campaign(args.campaign_id)
    if args.command == "export-bundle":
        return export_bundle(args.campaign_id)
    if args.command == "verify-bundle":
        return verify_bundle(Path(args.bundle))
    if args.command == "finalize":
        return finalize(args.campaign_id)
    if args.command == "shard-plan":
        plan = build_shard_plan(
            args.campaign_id,
            training_shards=args.training_shards,
            evaluation_shards=args.evaluation_shards,
            matrix_path=Path(args.matrix) if args.matrix else None,
        )
        write_shard_plan(plan, Path(args.output))
        return {"output": args.output, **{key: plan[key] for key in ("campaign_id", "plan_hash", "total_jobs", "training_jobs", "evaluation_jobs")}}
    if args.command == "export-shards":
        paths = export_shards(
            args.campaign_id,
            Path(args.plan),
            Path(args.output_dir),
            phase=args.phase,
        )
        return {"campaign_id": args.campaign_id, "bundles": [str(path) for path in paths]}
    if args.command == "run-shard":
        return run_shard(
            Path(args.bundle),
            Path(args.work_dir),
            max_runtime_seconds=args.max_runtime_seconds,
        )
    if args.command == "import-shard-results":
        return import_shard_results(args.campaign_id, Path(args.result_dir))
    if args.command == "import-results-directory":
        return import_results_directory(args.campaign_id, Path(args.results_dir))
    if args.command == "shard-status":
        return shard_status(args.campaign_id)
    if args.command == "backend-audit":
        return backend_provenance_audit(args.campaign_id)
    if args.command == "resource-plan":
        return resource_plan(
            args.campaign_id, Path(args.matrix) if args.matrix else None
        )
    if args.command == "clean":
        return _clean(args)
    raise ValueError(f"unsupported command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        _print(dispatch(args))
        return 0
    except Exception as exc:
        _print(
            {
                "status": "failed",
                "command": args.command,
                "error_type": exc.__class__.__name__,
                "error": str(exc),
            }
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
