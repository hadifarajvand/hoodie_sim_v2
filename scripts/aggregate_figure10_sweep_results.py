#!/usr/bin/env python3
"""Aggregate lightweight Figure 10 smoke sweep results.

This script reads per-sweep summary JSON and readiness JSON files and
produces CSV/JSON summaries and matplotlib plots. It does NOT run
simulations or import/run the simulator.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import csv
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASELINE_POLICIES = ["RO", "FLC", "VO", "HO", "BCO", "MLEO"]
REGIMES = ["delay", "drop_ratio"]
EXPECTED_VALUES = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]


def load_json(p: Path) -> Any:
    return json.loads(p.read_text())


def numeric_sort_key(s: str) -> float:
    try:
        return float(s)
    except Exception:
        return float('inf')


def aggregate(input_root: Path, output_dir: Path, sweep_name: str, label: str, strict: bool=False) -> Dict[str, Any]:
    input_root = Path(input_root)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    values_found = []
    missing_values = []
    rows = []
    validation_status = {"missing_values": [], "missing_regimes": {}, "missing_policies": {}, "episodes_mismatch": []}

    # collect directories
    dirs = [p for p in input_root.iterdir() if p.is_dir()]
    dirs_sorted = sorted(dirs, key=lambda p: numeric_sort_key(p.name))
    for d in dirs_sorted:
        sval = d.name
        try:
            vnum = float(sval)
        except Exception:
            continue
        values_found.append(vnum)
        summary_p = d / 'figure10_policy_metrics_summary.json'
        readiness_p = d / 'figure10_policy_readiness.json'
        if not summary_p.exists() or not readiness_p.exists():
            validation_status['missing_values'].append(sval)
            continue
        summary = load_json(summary_p)
        # some summaries nest regimes under a 'regimes' key
        if isinstance(summary, dict) and 'regimes' in summary:
            summary_regimes = summary['regimes']
        else:
            summary_regimes = summary
        readiness = load_json(readiness_p)

        # validate regimes present
        for regime in REGIMES:
            regime_summary = summary_regimes.get(regime)
            if regime_summary is None:
                validation_status['missing_regimes'].setdefault(sval, []).append(regime)
                continue
            # expect policies
            for policy in BASELINE_POLICIES:
                psummary = regime_summary.get(policy)
                if psummary is None:
                    validation_status['missing_policies'].setdefault(sval, []).append((regime, policy))
                    continue
                episodes_requested = psummary.get('episodes_requested', 10)
                episodes_completed = psummary.get('episodes_completed', 0)
                if episodes_completed != 10:
                    validation_status['episodes_mismatch'].append((sval, regime, policy, episodes_completed))
                # read metrics (use defensive keys)
                mean_delay = psummary.get('mean_delay') or psummary.get('mean_average_computation_delay') or None
                std_delay = psummary.get('std_delay') or psummary.get('std_average_computation_delay') or 0.0
                mean_drop = psummary.get('mean_drop_ratio') or psummary.get('mean_drop') or None
                std_drop = psummary.get('std_drop_ratio') or psummary.get('std_drop') or 0.0
                total_tasks = psummary.get('total_tasks') or psummary.get('task_count') or None
                completed_tasks = psummary.get('completed_tasks') or psummary.get('tasks_completed') or None
                dropped_tasks = psummary.get('dropped_tasks') or psummary.get('tasks_dropped') or None
                pending_tasks = psummary.get('pending_tasks') or psummary.get('tasks_pending') or None

                row = {
                    'sweep_name': sweep_name,
                    'sweep_value': vnum,
                    'regime_id': regime,
                    'policy_name': policy,
                    'episodes_requested': episodes_requested,
                    'episodes_completed': episodes_completed,
                    'mean_average_computation_delay': mean_delay,
                    'std_average_computation_delay': std_delay,
                    'mean_drop_ratio': mean_drop,
                    'std_drop_ratio': std_drop,
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks,
                    'dropped_tasks': dropped_tasks,
                    'pending_tasks': pending_tasks,
                    'baseline_validation_ready': readiness.get('baseline_validation_ready', False),
                    'figure10_data_ready': readiness.get('figure10_data_ready', False),
                    # derive row-level hoodie inclusion only from the active policy set
                    'hoodie_included': 'HOODIE' in readiness.get('active_policy_set', []),
                    'figure_claim': 'not_full_official_figure10',
                    'label': label,
                }
                rows.append(row)

    # handle missing expected values
    expected_set = set(EXPECTED_VALUES)
    found_set = set(values_found)
    not_found = sorted(list(expected_set - found_set))
    if not_found:
        missing_values = not_found
        validation_status['missing_values'] = missing_values

    # strict validation
    if strict:
        errors = []
        if missing_values:
            errors.append(f'missing sweep values: {missing_values}')
        if validation_status.get('missing_regimes'):
            errors.append(f'missing regimes: {validation_status.get("missing_regimes")}')
        if validation_status.get('missing_policies'):
            errors.append(f'missing policies: {validation_status.get("missing_policies")}')
        if validation_status.get('episodes_mismatch'):
            errors.append(f'episodes mismatch: {validation_status.get("episodes_mismatch")}')
        if errors:
            raise SystemExit('\n'.join(errors))

    # write CSV
    csv_path = output_dir / f"{sweep_name}_smoke_summary.csv"
    fieldnames = [
        'sweep_name','sweep_value','regime_id','policy_name','episodes_requested','episodes_completed',
        'mean_average_computation_delay','std_average_computation_delay','mean_drop_ratio','std_drop_ratio',
        'total_tasks','completed_tasks','dropped_tasks','pending_tasks',
        'baseline_validation_ready','figure10_data_ready','hoodie_included','figure_claim','label'
    ]
    with csv_path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    # write JSON summary
    json_path = output_dir / f"{sweep_name}_smoke_summary.json"
    with json_path.open('w') as f:
        json.dump({'rows': rows}, f, indent=2)

    # plots
    try:
        plot_delay(output_dir, rows, sweep_name, label)
        plot_drop_ratio(output_dir, rows, sweep_name, label)
        plot_combined(output_dir, rows, sweep_name, label)
    except Exception as e:
        print('Plotting failed:', e)

    # metadata
    metadata = {
        'plot_scope': 'smoke_sweep_baseline_only',
        'figure_claim': 'not_full_official_figure10',
        'sweep_name': sweep_name,
        'episode_count': 10,
        'hoodie_included': False,
        'policies_plotted': BASELINE_POLICIES,
        'source_input_root': str(input_root),
        'output_dir': str(output_dir),
        'values_found': sorted(values_found),
        'missing_values': missing_values,
        'validation_status': validation_status,
        'simulation_rerun': False,
        'paper_performance_claims_made': False,
        'warning': 'Smoke sweep plots are for workflow validation only and must not be used as final paper reproduction.'
    }
    meta_path = output_dir / f"{sweep_name}_smoke_metadata.json"
    with meta_path.open('w') as f:
        json.dump(metadata, f, indent=2)

    return {
        'csv': str(csv_path),
        'json': str(json_path),
        'metadata': str(meta_path),
        'plots': [str(output_dir / f"{sweep_name}_smoke_delay.png"), str(output_dir / f"{sweep_name}_smoke_drop_ratio.png"), str(output_dir / f"{sweep_name}_smoke_combined.png")],
        'values_aggregated': len(set(values_found)),
        'policies_plotted': BASELINE_POLICIES,
        'hoodie_excluded': True,
    }


def plot_delay(output_dir: Path, rows: List[Dict[str, Any]], sweep_name: str, label: str) -> None:
    out = output_dir / f"{sweep_name}_smoke_delay.png"
    plt.figure(figsize=(6,4))
    # group by policy and regime=delay
    data = {}
    for r in rows:
        if r['regime_id'] != 'delay':
            continue
        pol = r['policy_name']
        data.setdefault(pol, []).append((r['sweep_value'], r['mean_average_computation_delay']))
    for pol in BASELINE_POLICIES:
        if pol not in data:
            continue
        vals = sorted(data[pol], key=lambda x: x[0])
        xs = [v for v,_ in vals]
        ys = [y if y is not None else float('nan') for _,y in vals]
        plt.plot(xs, ys, marker='o', label=pol)
    plt.xlabel('task_arrival_probability')
    plt.ylabel('mean average computation delay')
    plt.title(f'{label} delay (smoke only, 10 episodes, baseline only)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(out)
    plt.close()


def plot_drop_ratio(output_dir: Path, rows: List[Dict[str, Any]], sweep_name: str, label: str) -> None:
    out = output_dir / f"{sweep_name}_smoke_drop_ratio.png"
    plt.figure(figsize=(6,4))
    data = {}
    for r in rows:
        if r['regime_id'] != 'drop_ratio':
            continue
        pol = r['policy_name']
        data.setdefault(pol, []).append((r['sweep_value'], r['mean_drop_ratio']))
    for pol in BASELINE_POLICIES:
        if pol not in data:
            continue
        vals = sorted(data[pol], key=lambda x: x[0])
        xs = [v for v,_ in vals]
        ys = [y if y is not None else float('nan') for _,y in vals]
        plt.plot(xs, ys, marker='o', label=pol)
    plt.xlabel('task_arrival_probability')
    plt.ylabel('mean drop ratio')
    plt.title(f'{label} drop ratio (smoke only, 10 episodes, baseline only)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(out)
    plt.close()


def plot_combined(output_dir: Path, rows: List[Dict[str, Any]], sweep_name: str, label: str) -> None:
    out = output_dir / f"{sweep_name}_smoke_combined.png"
    fig, axes = plt.subplots(1,2,figsize=(10,4))
    # delay
    data_delay = {}
    data_drop = {}
    for r in rows:
        pol = r['policy_name']
        if r['regime_id']=='delay':
            data_delay.setdefault(pol, []).append((r['sweep_value'], r['mean_average_computation_delay']))
        if r['regime_id']=='drop_ratio':
            data_drop.setdefault(pol, []).append((r['sweep_value'], r['mean_drop_ratio']))
    ax = axes[0]
    for pol in BASELINE_POLICIES:
        if pol not in data_delay:
            continue
        vals = sorted(data_delay[pol], key=lambda x: x[0])
        xs = [v for v,_ in vals]
        ys = [y if y is not None else float('nan') for _,y in vals]
        ax.plot(xs, ys, marker='o', label=pol)
    ax.set_xlabel('task_arrival_probability')
    ax.set_ylabel('mean average computation delay')
    ax.set_title('Delay')

    ax2 = axes[1]
    for pol in BASELINE_POLICIES:
        if pol not in data_drop:
            continue
        vals = sorted(data_drop[pol], key=lambda x: x[0])
        xs = [v for v,_ in vals]
        ys = [y if y is not None else float('nan') for _,y in vals]
        ax2.plot(xs, ys, marker='o', label=pol)
    ax2.set_xlabel('task_arrival_probability')
    ax2.set_ylabel('mean drop ratio')
    ax2.set_title('Drop ratio')

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=6)
    fig.suptitle(f'{label} (smoke only, 10 episodes, baseline only)')
    plt.tight_layout(rect=[0,0,1,0.95])
    fig.savefig(out)
    plt.close(fig)


def parse_args(argv: List[str]=None):
    p = argparse.ArgumentParser()
    p.add_argument('--input-root', required=True)
    p.add_argument('--output-dir', required=True)
    p.add_argument('--sweep-name', required=True)
    p.add_argument('--label', required=True)
    p.add_argument('--strict', action='store_true')
    return p.parse_args(argv)


def main(argv: List[str]=None):
    args = parse_args(argv)
    res = aggregate(Path(args.input_root), Path(args.output_dir), args.sweep_name, args.label, strict=args.strict)
    print('Wrote:', res)


if __name__ == '__main__':
    main()
