#!/usr/bin/env python3
import json
from pathlib import Path

def main():
    repo = Path(__file__).resolve().parents[1]
    template_hp = repo / 'artifacts' / 'figure10_validation' / 'sweep_configs' / 'smoke' / 'task_arrival_probability' / '0.5' / 'hyperparameters.json'
    template_cfg = repo / 'artifacts' / 'figure10_validation' / 'sweep_configs' / 'smoke' / 'task_arrival_probability' / '0.5' / 'config.yml'
    out_root = repo / 'artifacts' / 'figure10_validation' / 'sweep_configs' / 'smoke' / 'task_arrival_probability'
    values = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
    if not template_hp.exists() or not template_cfg.exists():
        raise SystemExit('Template files not found: ' + str(template_hp))
    template = json.loads(template_hp.read_text())
    cfg_text = template_cfg.read_text()
    for v in values:
        sval = str(v)
        out_dir = out_root / sval
        out_dir.mkdir(parents=True, exist_ok=True)
        # write hyperparameters
        hp = dict(template)
        hp['task_arrive_probabilities'] = [v] * int(hp.get('number_of_servers', 20))
        (out_dir / 'hyperparameters.json').write_text(json.dumps(hp, indent=2, sort_keys=True))
        # write config.yml based on template but with updated paths and fixed fields
        cfg = cfg_text.replace('/0.5/', f'/{sval}/')
        # ensure episodes/policies/trace_level/etc are set correctly
        # naive approach: overwrite keys by writing a minimal config file
        cfg_lines = []
        cfg_lines.append(f'output_dir: "{repo}/artifacts/figure10_validation/sweeps/smoke/task_arrival_probability/{sval}"')
        cfg_lines.append(f'hyperparameters_file: "{repo}/artifacts/figure10_validation/sweep_configs/smoke/task_arrival_probability/{sval}/hyperparameters.json"')
        cfg_lines.append('paper_contract: "config/paper_table4_contract.json"')
        cfg_lines.append('episodes: 10')
        cfg_lines.append('policies: "RO,FLC,VO,HO,BCO,MLEO"')
        cfg_lines.append('seed: 42')
        cfg_lines.append('trace_level: "summary"')
        cfg_lines.append('test_mode: false')
        cfg_lines.append('strict_paper_contract: false')
        cfg_lines.append('strict_readiness: false')
        (out_dir / 'config.yml').write_text('\n'.join(cfg_lines) + '\n')
    print('Generated configs for values:', values)

if __name__ == '__main__':
    main()
