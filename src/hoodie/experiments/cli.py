from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pathlib import Path

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


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == 'validate-contracts':
        contract = build_figures_8_11_source_contract()
        _print_json({'panels': len(contract.panels), 'unresolved_fields': contract.unresolved_fields()})
        return 0
    if args.command == 'list-panels':
        _print_json({panel_id: contract.spec.__dict__ if hasattr(contract.spec, '__dict__') else {'panel_id': contract.spec.panel_id} for panel_id, contract in PANEL_REGISTRY.items()})
        return 0
    if args.command == 'run':
        campaign_name = args.campaign_id or args.campaign or 'figures-8-11-smoke'
        output_dir = Path('artifacts/hoodie/campaigns')
        result = run_smoke_campaign(campaign_id=campaign_name, output_dir=output_dir, smoke=True)
        _print_json(result)
        return 0
    _print_json({'command': args.command, 'status': 'not-implemented-yet', 'campaign_id': getattr(args, 'campaign_id', None), 'campaign': getattr(args, 'campaign', None)})
    return 0
