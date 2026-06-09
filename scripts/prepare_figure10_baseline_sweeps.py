from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE_POLICIES = ["RO", "FLC", "VO", "HO", "BCO", "MLEO"]
SWEEP_ROOT = ROOT / "artifacts" / "figure10_validation" / "sweep_configs" / "baseline-only"
RUN_ROOT = ROOT / "artifacts" / "figure10_validation" / "sweeps" / "baseline-only"

TASK_ARRIVAL_VALUES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
PRIVATE_CPU_GHZ_VALUES = [2.5, 5.0, 7.5, 10.0]
TIMEOUT_SLOTS_VALUES = [10, 15, 20, 25, 30]


def _render_yaml(mapping: dict[str, object]) -> str:
    lines: list[str] = []
    for key, value in mapping.items():
        if isinstance(value, str):
            rendered = json.dumps(value)
        elif isinstance(value, bool):
            rendered = "true" if value else "false"
        elif isinstance(value, list):
            rendered = json.dumps(value)
        elif value is None:
            rendered = "null"
        else:
            rendered = str(value)
        lines.append(f"{key}: {rendered}")
    return "\n".join(lines) + "\n"


def _load_base_hyperparameters() -> dict[str, object]:
    path = ROOT / "hyperparameters" / "hyperparameters.json"
    if path.exists():
        return json.loads(path.read_text())
    return {
        "task_arrive_probabilities": [0.5],
        "private_cpu_capacities": [5.0],
        "timeout_delay_mins": [20],
        "number_of_servers": 1,
    }


def _write_config_files(sweep_name: str, value_label: str, hyperparameters_overrides: dict[str, object]) -> Path:
    sweep_dir = SWEEP_ROOT / sweep_name / value_label
    sweep_dir.mkdir(parents=True, exist_ok=True)
    hyperparameters_path = sweep_dir / "hyperparameters.json"
    config_path = sweep_dir / "config.yml"
    hyperparameters_path.write_text(json.dumps(hyperparameters_overrides, indent=2, sort_keys=True))
    config_path.write_text(
        _render_yaml(
            {
                "output_dir": str(RUN_ROOT / sweep_name / value_label),
                "hyperparameters_file": str(hyperparameters_path),
                "paper_contract": "config/paper_table4_contract.json",
                "episodes": 200,
                "policies": ",".join(BASELINE_POLICIES),
                "seed": 42,
                "trace_level": "summary",
                "test_mode": False,
                "strict_paper_contract": False,
                "strict_readiness": False,
            }
        )
    )
    return config_path


def _build_sweep_configs() -> dict[str, list[Path]]:
    base_hyperparameters = _load_base_hyperparameters()
    generated: dict[str, list[Path]] = {"task_arrival_probability": [], "private_cpu_ghz": [], "timeout_slots": []}

    for value in TASK_ARRIVAL_VALUES:
        hp = json.loads(json.dumps(base_hyperparameters))
        hp["task_arrive_probabilities"] = [value] * len(hp.get("task_arrive_probabilities", [value]))
        generated["task_arrival_probability"].append(_write_config_files("task_arrival_probability", str(value), hp))

    for value in PRIVATE_CPU_GHZ_VALUES:
        hp = json.loads(json.dumps(base_hyperparameters))
        hp["private_cpu_capacities"] = [value] * len(hp.get("private_cpu_capacities", [value]))
        generated["private_cpu_ghz"].append(_write_config_files("private_cpu_ghz", str(value), hp))

    for value in TIMEOUT_SLOTS_VALUES:
        hp = json.loads(json.dumps(base_hyperparameters))
        hp["timeout_delay_mins"] = [value] * len(hp.get("timeout_delay_mins", [value]))
        generated["timeout_slots"].append(_write_config_files("timeout_slots", str(value), hp))

    return generated


def _command_for(config_path: Path, sweep_name: str, value_label: str) -> str:
    return "\n".join(
        [
            "./.venvmac/bin/python scripts/run_figure10_validation.py \\",
            f"  --config {config_path} \\",
            f"  --output-dir {RUN_ROOT / sweep_name / value_label} \\",
            "  --episodes 200 \\",
            f"  --policies {','.join(BASELINE_POLICIES)} \\",
            "  --seed 42",
        ]
    )


def main() -> int:
    generated = _build_sweep_configs()
    print("Phase 5 Figure 10 baseline-only sweep preparation")
    print("This is baseline-only. HOODIE is intentionally excluded.")
    print("This is not the full official HOODIE Figure 10 reproduction.")
    print("No simulation is run by this script.")
    print("Generated sweep configs live under artifacts/figure10_validation/sweep_configs/baseline-only/")
    print("Generated sweep outputs should live under artifacts/figure10_validation/sweeps/baseline-only/")
    print("Large traces must remain disabled via trace_level=summary.")
    print("")
    for sweep_name, configs in generated.items():
        print(f"=== {sweep_name} ===")
        for config_path in configs:
            value_label = config_path.parent.name
            print(_command_for(config_path, sweep_name, value_label))
            print("")
    print("Post-run inspection example:")
    print("./.venvmac/bin/python - <<'PY'")
    print("import json")
    print("from pathlib import Path")
    print('run_dir = Path("artifacts/figure10_validation/sweeps/baseline-only/task_arrival_probability/0.5")')
    print('summary = json.loads((run_dir / "figure10_policy_metrics_summary.json").read_text())')
    print('readiness = json.loads((run_dir / "figure10_policy_readiness.json").read_text())')
    print('print("baseline_validation_ready:", readiness.get("baseline_validation_ready"))')
    print('print("figure10_data_ready:", readiness.get("figure10_data_ready"))')
    print('print("rows:", len(summary.get("summary_rows", [])))')
    print("PY")
    print("")
    print("Git hygiene:")
    print("git status --short")
    print("git check-ignore -v artifacts/figure10_validation/sweeps/baseline-only/task_arrival_probability/0.5/figure10_policy_metrics_raw.csv || true")
    print("find artifacts/figure10_validation/sweeps -type f \\( -name \"*.png\" -o -name \"*.pdf\" -o -name \"*.pth\" -o -name \"*.pt\" -o -name \"*.pkl\" -o -name \"*.pickle\" \\)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
