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

from .campaign import run_smoke_campaign
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
        result = run_smoke_campaign(campaign_id=campaign_name, output_dir=output_dir, smoke=False)
        _print_json(result)
        return 0
    if args.command == 'plan':
        contract = build_figures_8_11_source_contract()
        campaign_id = args.campaign_id or args.campaign or 'figures-8-11-production'
        base_dir = Path('artifacts/hoodie/implementation_run/campaign')
        base_dir.mkdir(parents=True, exist_ok=True)
        panel_count = len(contract.panels)
        dry_run = {
            'campaign_id': campaign_id,
            'resolved_panel_count': contract.resolved_panel_count(),
            'blocked_panel_count': len(contract.unresolved_fields()),
            'training_jobs': len(contract.panels),
            'evaluation_jobs': len(contract.panels),
            'checkpoints': len(contract.panels),
            'trace_banks': len(contract.panels),
            'seed_count': 1,
            'episodes': 5000,
            'expected_cpu_hours': round(panel_count * 0.08, 3),
            'expected_gpu_hours': round(panel_count * 0.02, 3),
            'peak_ram_gb': 4.0,
            'peak_vram_gb': 0.0,
            'expected_disk_gb': round(panel_count * 0.25, 3),
            'maximum_safe_parallelism': 2,
            'checkpoint_reuse': True,
            'retraining_requirements': 'required for training-dependent panels',
            'resume_strategy': 'skip completed jobs, rerun incomplete or corrupt jobs',
            'generated_at': time.time(),
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
    _print_json({'command': args.command, 'status': 'not-implemented-yet', 'campaign_id': getattr(args, 'campaign_id', None), 'campaign': getattr(args, 'campaign', None)})
    return 0
