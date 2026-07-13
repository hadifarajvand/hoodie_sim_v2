#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.analysis.figure_generator import (
    plot_figure_10_offloading_schemes,
    render_status_figure,
    write_export_manifest,
)


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "artifacts/analysis/figure8-11-validation/figure_10"
SOURCE_DIR = ROOT_DIR / "artifacts/analysis/figure8-11-validation/figure_10_baselines"


def _check(results: list[dict], sweep_type: str) -> dict[str, object]:
    rows = []
    x_values: set[float] = set()
    policies: set[str] = set()
    delay_points = 0
    drop_points = 0
    for r in results:
        meta = (r.get("config", {}).get("sweep_metadata", {}) or {})
        if meta.get("sweep_type") != sweep_type:
            continue
        rows.append(r)
        policy = str(meta.get("policy") or "")
        if policy:
            policies.add(policy)
        if sweep_type == "arrival_probability":
            x_value = meta.get("arrival_probability")
        elif sweep_type == "cpu_capacity":
            x_value = meta.get("cpu_capacity")
        else:
            x_value = meta.get("task_timeout_slots")
        if x_value is not None:
            x_values.add(float(x_value))
        delay_series = r.get("training_metrics", {}).get("average_delays", []) or []
        drop_series = r.get("training_metrics", {}).get("drop_ratios", []) or []
        delay_points += len(delay_series)
        drop_points += len(drop_series)
    return {
        "present": bool(rows),
        "delay_nonempty": delay_points > 0,
        "drop_nonempty": drop_points > 0,
        "row_count": len(rows),
        "x_count": len(x_values),
        "policy_count": len(policies),
    }


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = json.loads((SOURCE_DIR / "sweep_results.json").read_text(encoding="utf-8"))
    checks = {name: _check(results, name) for name in ["arrival_probability", "cpu_capacity", "task_timeout"]}
    missing: list[str] = []
    for name, chk in checks.items():
        if not chk["present"]:
            missing.append(f"{name} rows missing")
        if not chk["delay_nonempty"]:
            missing.append(f"{name} delay missing")
        if not chk["drop_nonempty"]:
            missing.append(f"{name} drop missing")
        if int(chk["x_count"]) < 2:
            missing.append(f"{name} x-values < 2")
        if int(chk["policy_count"]) < 2:
            missing.append(f"{name} policies < 2")
    output_png = OUTPUT_DIR / "figure10_offloading_schemes.png"
    if missing:
        render_status_figure(output_png, "Figure 10: data incomplete", missing)
        status = "blocked"
    else:
        plot_figure_10_offloading_schemes(results, str(output_png), "Figure 10: 100-episode baseline comparison")
        status = "exported"
    if status == "exported":
        print("[figure10] policy order forced: RO, VO, VCO, hoodie, FLC, HO, MLEO")
    manifest = {
        "figure_id": "Figure 10",
        "episodes_expected": 100,
        "status": status,
        "source": str(SOURCE_DIR / "sweep_results.json"),
        "output": str(output_png),
        "missing_or_invalid": missing,
        "subfigures": [
            {"id": "fig10a", "series": "arrival_probability_delay", "present": checks["arrival_probability"]["delay_nonempty"], "x_count": checks["arrival_probability"]["x_count"], "policy_count": checks["arrival_probability"]["policy_count"]},
            {"id": "fig10b", "series": "arrival_probability_drop", "present": checks["arrival_probability"]["drop_nonempty"], "x_count": checks["arrival_probability"]["x_count"], "policy_count": checks["arrival_probability"]["policy_count"]},
            {"id": "fig10c", "series": "cpu_capacity_delay", "present": checks["cpu_capacity"]["delay_nonempty"], "x_count": checks["cpu_capacity"]["x_count"], "policy_count": checks["cpu_capacity"]["policy_count"]},
            {"id": "fig10d", "series": "cpu_capacity_drop", "present": checks["cpu_capacity"]["drop_nonempty"], "x_count": checks["cpu_capacity"]["x_count"], "policy_count": checks["cpu_capacity"]["policy_count"]},
            {"id": "fig10e", "series": "timeout_delay", "present": checks["task_timeout"]["delay_nonempty"], "x_count": checks["task_timeout"]["x_count"], "policy_count": checks["task_timeout"]["policy_count"]},
            {"id": "fig10f", "series": "timeout_drop", "present": checks["task_timeout"]["drop_nonempty"], "x_count": checks["task_timeout"]["x_count"], "policy_count": checks["task_timeout"]["policy_count"]},
        ],
    }
    write_export_manifest(OUTPUT_DIR, manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
