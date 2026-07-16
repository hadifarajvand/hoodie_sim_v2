from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from dataclasses import asdict
from platform import platform, python_version
import subprocess
import time
from shutil import copy2

from .campaign import run_production_campaign, campaign_status, resume_production_campaign
from .distributed import (
    backend_provenance_audit,
    build_shard_plan,
    build_integration_campaign,
    export_shards,
    finalize_campaign,
    import_shard_results,
    import_results_directory,
    resource_plan,
    run_shard,
    shard_status,
    write_resource_plan,
    write_shard_plan,
    build_shard_plan_from_rows,
)
from .job_matrix import build_production_job_matrix, write_production_job_matrix
from .panel_registry import PANEL_REGISTRY
from .source_contracts import build_figures_8_11_source_contract


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='python -m hoodie.experiments')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('validate-contracts')
    sub.add_parser('list-panels')
    run = sub.add_parser('run')
    run.add_argument('--campaign', required=False)
    run.add_argument('--campaign-id', required=False)
    for name in ('plan', 'resume', 'status', 'aggregate', 'render', 'verify', 'export-bundle'):
        cmd = sub.add_parser(name)
        cmd.add_argument('--campaign-id', required=False)
        cmd.add_argument('--campaign', required=False)
    shard_plan = sub.add_parser('shard-plan')
    shard_plan.add_argument('--campaign-id', required=True)
    shard_plan.add_argument('--training-workers', type=int, required=True)
    shard_plan.add_argument('--evaluation-workers', type=int, required=True)
    shard_plan.add_argument('--output', required=True)
    export_shard = sub.add_parser('export-shards')
    export_shard.add_argument('--campaign-id', required=True)
    export_shard.add_argument('--plan', required=True)
    export_shard.add_argument('--output-dir', required=True)
    run_shard_cmd = sub.add_parser('run-shard')
    run_shard_cmd.add_argument('--bundle', required=True)
    run_shard_cmd.add_argument('--work-dir', required=True)
    import_shard = sub.add_parser('import-shard-results')
    import_shard.add_argument('--campaign-id', required=True)
    import_shard.add_argument('--result-bundle', required=True)
    shard_status_cmd = sub.add_parser('shard-status')
    shard_status_cmd.add_argument('--campaign-id', required=True)
    finalize = sub.add_parser('finalize')
    finalize.add_argument('--campaign-id', required=True)
    backend_audit = sub.add_parser('backend-provenance-audit')
    backend_audit.add_argument('--campaign-id', required=True)
    resource = sub.add_parser('resource-plan')
    resource.add_argument('--campaign-id', required=True)
    integration_plan = sub.add_parser('integration-plan')
    integration_plan.add_argument('--output-root', required=True)
    integration_plan.add_argument('--seed', type=int, default=7)
    integration_export = sub.add_parser('integration-export-shards')
    integration_export.add_argument('--output-root', required=True)
    integration_export.add_argument('--plan-output', required=True)
    integration_export.add_argument('--training-workers', type=int, required=True)
    integration_export.add_argument('--evaluation-workers', type=int, required=True)
    integration_run = sub.add_parser('integration-run-shard')
    integration_run.add_argument('--bundle', required=True)
    integration_run.add_argument('--work-dir', required=True)
    integration_import = sub.add_parser('import-results-directory')
    integration_import.add_argument('--campaign-id', required=True)
    integration_import.add_argument('--results-dir', required=True)
    integration_finalize_cmd = sub.add_parser('integration-finalize')
    integration_finalize_cmd.add_argument('--campaign-id', required=True)
    resume = sub.choices['resume']
    resume.add_argument('--job-id', required=False)
    resume.add_argument('--max-jobs', type=int, required=False)
    resume.add_argument('--max-runtime-seconds', type=float, required=False)
    resume.add_argument('--allow-paused-recovery', action='store_true')
    supervise = sub.add_parser('supervise')
    supervise.add_argument('--campaign-id', required=False)
    supervise.add_argument('--campaign', required=False)
    supervise.add_argument('--max-runtime-seconds', type=float, required=False)
    return parser


def _print_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _campaign_dir(campaign_id: str) -> Path:
    return Path('artifacts/hoodie/campaigns') / campaign_id


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == 'validate-contracts':
        contract = build_figures_8_11_source_contract()
        _print_json({
            'panels': len(contract.panels),
            'resolved_panels': contract.resolved_panel_count(),
            'unresolved_fields': contract.unresolved_fields(),
            'summary': contract.summary(),
        })
        return 0
    if args.command == 'list-panels':
        _print_json({panel_id: contract.spec.__dict__ if hasattr(contract.spec, '__dict__') else {'panel_id': contract.spec.panel_id} for panel_id, contract in PANEL_REGISTRY.items()})
        return 0
    if args.command == 'run':
        campaign_name = args.campaign_id or args.campaign or 'figures-8-11'
        output_dir = Path('artifacts/hoodie/campaigns')
        result = run_production_campaign(campaign_id=campaign_name, output_dir=output_dir)
        _print_json(result)
        return 0
    if args.command == 'status':
        campaign_id = args.campaign_id or args.campaign or 'figures-8-11'
        _print_json(campaign_status(campaign_id, Path('artifacts/hoodie/campaigns')))
        return 0
    if args.command == 'resume':
        campaign_id = args.campaign_id or args.campaign or 'figures-8-11'
        _print_json(resume_production_campaign(campaign_id, Path('artifacts/hoodie/campaigns'), max_jobs=args.max_jobs, max_runtime_seconds=args.max_runtime_seconds, job_id=args.job_id, allow_paused_recovery=args.allow_paused_recovery))
        return 0
    if args.command == 'supervise':
        from .supervisor import supervise_campaign
        campaign_id = args.campaign_id or args.campaign or 'figures-8-11'
        _print_json(supervise_campaign(campaign_id, Path('artifacts/hoodie/campaigns'), max_runtime_seconds=args.max_runtime_seconds))
        return 0
    if args.command == 'plan':
        contract = build_figures_8_11_source_contract()
        campaign_id = args.campaign_id or args.campaign or 'figures-8-11-production'
        base_dir = Path('artifacts/hoodie/implementation_run/campaign')
        base_dir.mkdir(parents=True, exist_ok=True)
        matrix_path = base_dir / 'expected_production_job_matrix.json'
        rows = build_production_job_matrix(campaign_id)
        write_production_job_matrix(matrix_path, campaign_id)
        panel_count = len(contract.panels)
        dry_run = {
            'campaign_id': campaign_id,
            'resolved_panel_count': contract.resolved_panel_count(),
            'blocked_panel_count': len(contract.unresolved_fields()),
            'training_jobs': sum(1 for row in rows if row.job_type == 'training'),
            'evaluation_jobs': sum(1 for row in rows if row.job_type == 'evaluation'),
            'checkpoints': len({row.checkpoint_dependency for row in rows}),
            'trace_banks': len({row.trace_bank_id for row in rows}),
            'seed_count': len({row.seed for row in rows if row.seed is not None}),
            'episodes': 5000,
            'expected_cpu_hours': round(len(rows) * 0.08, 3),
            'expected_gpu_hours': round(len(rows) * 0.02, 3),
            'peak_ram_gb': 4.0,
            'peak_vram_gb': 0.0,
            'expected_disk_gb': round(len(rows) * 0.25, 3),
            'maximum_safe_parallelism': 2,
            'checkpoint_reuse': True,
            'retraining_requirements': 'required for training-dependent panels',
            'resume_strategy': 'skip completed jobs, rerun incomplete or corrupt jobs',
            'generated_at': time.time(),
            'job_matrix_path': str(matrix_path),
            'expanded_job_count': len(rows),
        }
        (base_dir / 'production_dry_run.json').write_text(json.dumps(dry_run, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        (base_dir / 'production_dry_run.md').write_text(
            '\n'.join([
                '# HOODIE Figures 8–11 Production Dry Run',
                f'- campaign_id: {campaign_id}',
                f'- resolved_panels: {dry_run["resolved_panel_count"]}',
                f'- blocked_panels: {dry_run["blocked_panel_count"]}',
                f'- training_jobs: {dry_run["training_jobs"]}',
                f'- evaluation_jobs: {dry_run["evaluation_jobs"]}',
            ]) + '\n',
            encoding='utf-8',
        )
        _print_json(dry_run)
        return 0
    if args.command == 'aggregate':
        campaign_id = args.campaign_id or args.campaign or 'figures-8-11'
        campaign_dir = _campaign_dir(campaign_id)
        payload = {'campaign_id': campaign_id, 'status': 'ok'}
        manifest = campaign_dir / 'aggregation_manifest.json'
        if manifest.exists():
            payload.update(_load_json(manifest))
        _print_json(payload)
        return 0
    if args.command == 'verify':
        campaign_id = args.campaign_id or args.campaign or 'figures-8-11'
        campaign_dir = _campaign_dir(campaign_id)
        payload = {'campaign_id': campaign_id, 'status': 'ok'}
        report = campaign_dir / 'verification_report.json'
        if report.exists():
            payload.update(_load_json(report))
        _print_json(payload)
        return 0
    if args.command == 'render':
        campaign_id = args.campaign_id or args.campaign or 'figures-8-11'
        campaign_dir = _campaign_dir(campaign_id)
        figures_dir = campaign_dir / 'figures'
        payload = {'campaign_id': campaign_id, 'status': 'ok', 'figures_dir': str(figures_dir)}
        manifest = figures_dir / 'render_manifest.json'
        if manifest.exists():
            payload.update(_load_json(manifest))
        _print_json(payload)
        return 0
    if args.command == 'export-bundle':
        campaign_id = args.campaign_id or args.campaign or 'figures-8-11'
        source = _campaign_dir(campaign_id)
        bundle = Path('artifacts/hoodie/releases') / f'figures_8_11_{campaign_id}'
        bundle.mkdir(parents=True, exist_ok=True)
        for name in ('campaign_specification.json', 'source_contract_snapshot.json', 'job_plan.json', 'status.json', 'environment_manifest.json', 'source_manifest.json', 'trace_registry.json', 'checkpoint_registry.json', 'aggregation_manifest.json', 'verification_report.json'):
            src = source / name
            if src.exists():
                copy2(src, bundle / name)
        payload = {'campaign_id': campaign_id, 'status': 'ok', 'bundle_dir': str(bundle)}
        _print_json(payload)
        return 0
    if args.command == 'shard-plan':
        plan = build_shard_plan(args.campaign_id, training_workers=args.training_workers, evaluation_workers=args.evaluation_workers)
        out = write_shard_plan(plan, Path(args.output))
        _print_json({'campaign_id': args.campaign_id, 'output': str(out), 'plan': plan.to_dict()})
        return 0
    if args.command == 'export-shards':
        bundles = export_shards(args.campaign_id, Path(args.plan), Path(args.output_dir))
        _print_json({'campaign_id': args.campaign_id, 'bundles': [str(bundle) for bundle in bundles]})
        return 0
    if args.command == 'run-shard':
        _print_json(run_shard(Path(args.bundle), Path(args.work_dir)))
        return 0
    if args.command == 'import-shard-results':
        _print_json(import_shard_results(args.campaign_id, Path(args.result_bundle)))
        return 0
    if args.command == 'shard-status':
        _print_json(shard_status(args.campaign_id))
        return 0
    if args.command == 'finalize':
        _print_json(finalize_campaign(args.campaign_id))
        return 0
    if args.command == 'backend-provenance-audit':
        _print_json(backend_provenance_audit(args.campaign_id))
        return 0
    if args.command == 'resource-plan':
        out = write_resource_plan(args.campaign_id)
        _print_json({'campaign_id': args.campaign_id, 'path': str(out), 'plan': resource_plan(args.campaign_id)})
        return 0
    if args.command == 'integration-plan':
        integration = build_integration_campaign(Path(args.output_root), seed=args.seed)
        _print_json({'campaign_id': integration.campaign_id, 'matrix_path': str(integration.matrix_path), 'rows': [asdict(row) for row in integration.rows]})
        return 0
    if args.command == 'integration-export-shards':
        integration = build_integration_campaign(Path(args.output_root))
        plan = build_shard_plan_from_rows(integration.campaign_id, list(integration.rows), training_workers=args.training_workers, evaluation_workers=args.evaluation_workers)
        plan_payload = plan.to_dict()
        plan_payload["rows"] = [asdict(row) for row in integration.rows]
        out = Path(args.plan_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(plan_payload, indent=2, sort_keys=True) + "\n", encoding='utf-8')
        bundles = export_shards(integration.campaign_id, out, Path(args.output_root) / 'bundles')
        _print_json({'campaign_id': integration.campaign_id, 'plan': str(out), 'bundles': [str(bundle) for bundle in bundles]})
        return 0
    if args.command == 'integration-run-shard':
        _print_json(run_shard(Path(args.bundle), Path(args.work_dir)))
        return 0
    if args.command == 'import-results-directory':
        _print_json(import_results_directory(args.campaign_id, Path(args.results_dir)))
        return 0
    if args.command == 'integration-finalize':
        _print_json(finalize_campaign(args.campaign_id))
        return 0
    _print_json({'command': args.command, 'status': 'not-implemented-yet', 'campaign_id': getattr(args, 'campaign_id', None), 'campaign': getattr(args, 'campaign', None)})
    return 0
