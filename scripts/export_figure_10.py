#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from src.analysis.figure_generator import plot_figure_10_offloading_schemes


OUTPUT_DIR = Path("artifacts/analysis/figure8-11-validation/figure_10")
SOURCE_DIR = Path("artifacts/analysis/figure8-11-validation/figure_10_baselines")


def _render_status_png(path: Path, title: str, missing: list[str]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis("off")
    ax.text(0.02, 0.95, "\n".join([title, "", "Export blocked.", "Missing/invalid:", *[f"- {item}" for item in missing]]), va="top", ha="left", family="monospace")
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _check(results: list[dict], sweep_type: str) -> dict[str, object]:
    rows = []
    for r in results:
        meta = (r.get("config", {}).get("sweep_metadata", {}) or {})
        if meta.get("sweep_type") == sweep_type:
            rows.append(r)
    delays = [r.get("training_metrics", {}).get("average_delays", []) or [] for r in rows]
    drops = [r.get("training_metrics", {}).get("drop_ratios", []) or [] for r in rows]
    return {
        "present": bool(rows),
        "delay_nonempty": any(delays),
        "drop_nonempty": any(drops),
        "delay_flat": any(len(set(s)) <= 1 for s in delays if s),
        "drop_flat": any(len(set(s)) <= 1 for s in drops if s),
        "max_delay_points": max((len(s) for s in delays), default=0),
        "max_drop_points": max((len(s) for s in drops), default=0),
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
        if int(chk["max_delay_points"]) < 2:
            missing.append(f"{name} delay points < 2")
        if int(chk["max_drop_points"]) < 2:
            missing.append(f"{name} drop points < 2")
    output_png = OUTPUT_DIR / "figure10_offloading_schemes.png"
    if missing:
        _render_status_png(output_png, "Figure 10: data incomplete", missing)
        status = "blocked"
    else:
        plot_figure_10_offloading_schemes(results, str(output_png), "Figure 10: 5-episode baseline comparison")
        status = "exported"
    if status == "exported":
        print("[figure10] policy order forced: RO, VO, VCO, hoodie, FLC, HO, MLEO")
    manifest = {
        "figure_id": "Figure 10",
        "episodes_expected": 5,
        "status": status,
        "source": str(SOURCE_DIR / "sweep_results.json"),
        "output": str(output_png),
        "missing_or_invalid": missing,
        "subfigures": [
            {"id": "10a", "series": "arrival_probability_delay", "present": checks["arrival_probability"]["delay_nonempty"], "points": checks["arrival_probability"]["max_delay_points"]},
            {"id": "10b", "series": "arrival_probability_drop", "present": checks["arrival_probability"]["drop_nonempty"], "points": checks["arrival_probability"]["max_drop_points"]},
            {"id": "10c", "series": "cpu_capacity_delay", "present": checks["cpu_capacity"]["delay_nonempty"], "points": checks["cpu_capacity"]["max_delay_points"]},
            {"id": "10d", "series": "cpu_capacity_drop", "present": checks["cpu_capacity"]["drop_nonempty"], "points": checks["cpu_capacity"]["max_drop_points"]},
            {"id": "10e", "series": "timeout_delay", "present": checks["task_timeout"]["delay_nonempty"], "points": checks["task_timeout"]["max_delay_points"]},
            {"id": "10f", "series": "timeout_drop", "present": checks["task_timeout"]["drop_nonempty"], "points": checks["task_timeout"]["max_drop_points"]},
        ],
    }
    (OUTPUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
