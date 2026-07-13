#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.analysis.figure_generator import (
    plot_figure_9_parameter_sweep,
    render_status_figure,
    write_export_manifest,
)


OUTPUT_DIR = ROOT_DIR / "artifacts/analysis/figure8-11-validation/figure_9"
SOURCE_DIR = ROOT_DIR / "artifacts/analysis/figure8-11-validation/sweep"


def _subseries(rows: list[dict], sweep_type: str) -> list[list[float]]:
    out: list[list[float]] = []
    for r in rows:
        meta = (r.get("config", {}).get("sweep_metadata", {}) or {})
        if meta.get("sweep_type") == sweep_type:
            out.append(r.get("training_metrics", {}).get("episode_rewards", []) or [])
    return out


def _check(rows: list[dict], sweep_type: str) -> dict[str, object]:
    series = _subseries(rows, sweep_type)
    return {
        "present": bool(series),
        "nonempty": any(series),
        "flat": any(len(set(s)) <= 1 for s in series if s),
        "max_episodes": max((len(s) for s in series), default=0),
    }


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("[figure9] load sweep_results.json")
    results = json.loads((SOURCE_DIR / "sweep_results.json").read_text(encoding="utf-8"))
    print(f"[figure9] rows={len(results)}")
    checks = {
        "arrival_probability": _check(results, "arrival_probability"),
        "cpu_capacity": _check(results, "cpu_capacity"),
        "num_drl_agents": _check(results, "num_drl_agents"),
        "offload_data_rate": _check(results, "offload_data_rate"),
    }
    missing: list[str] = []
    for name, chk in checks.items():
        if not chk["present"] or not chk["nonempty"]:
            missing.append(f"{name} episode_rewards missing")
        if chk["flat"]:
            missing.append(f"{name} episode_rewards flat")
        if int(chk["max_episodes"]) < 5:
            missing.append(f"{name} episodes < 5")
    action_present = any(((r.get("training_metrics", {}).get("action_counts", []) or [])) for r in results if ((r.get("config", {}).get("sweep_metadata", {}) or {}).get("sweep_type") == "arrival_probability") )
    if not action_present:
        missing.append("action_distribution missing")
    # Figure 9 only export relies on renderer and sweep metadata; keep status
    # PNG fallback if data is incomplete.
    if not action_present:
        missing.append("action_distribution missing")

    output_png = OUTPUT_DIR / "figure9_parameter_sweep.png"
    if missing:
        render_status_figure(output_png, "Figure 9: data incomplete", missing)
        status = "blocked"
    else:
        plot_figure_9_parameter_sweep(results, str(output_png), "Figure 9: 100-episode parameter sweeps")
        status = "exported"
    manifest = {
        "figure_id": "Figure 9",
        "episodes_expected": 100,
        "status": status,
        "source": str(SOURCE_DIR / "sweep_results.json"),
        "output": str(output_png),
        "missing_or_invalid": missing,
        "subfigures": [
            {"id": "fig09a", "series": "arrival_probability", "present": checks["arrival_probability"]["present"], "nonempty": checks["arrival_probability"]["nonempty"], "flat": checks["arrival_probability"]["flat"], "max_episodes": checks["arrival_probability"]["max_episodes"]},
            {"id": "fig09b", "series": "action_distribution", "present": action_present},
            {"id": "fig09c", "series": "cpu_capacity", "present": checks["cpu_capacity"]["present"], "nonempty": checks["cpu_capacity"]["nonempty"], "flat": checks["cpu_capacity"]["flat"], "max_episodes": checks["cpu_capacity"]["max_episodes"]},
            {"id": "fig09d", "series": "num_drl_agents", "present": checks["num_drl_agents"]["present"], "nonempty": checks["num_drl_agents"]["nonempty"], "flat": checks["num_drl_agents"]["flat"], "max_episodes": checks["num_drl_agents"]["max_episodes"]},
            {"id": "fig09e", "series": "offload_data_rate", "present": checks["offload_data_rate"]["present"], "nonempty": checks["offload_data_rate"]["nonempty"], "flat": checks["offload_data_rate"]["flat"], "max_episodes": checks["offload_data_rate"]["max_episodes"]},
        ],
    }
    write_export_manifest(OUTPUT_DIR, manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
