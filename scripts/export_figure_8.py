#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.analysis.figure_generator import (
    plot_figure_8_reward_timecourse,
    render_status_figure,
    write_export_manifest,
)


OUTPUT_DIR = ROOT_DIR / "artifacts/analysis/figure8-11-validation/figure_8"
SOURCE_DIR = ROOT_DIR / "artifacts/analysis/figure8-11-validation/sweep"


def _series_stats(rows: list[dict], sweep_type: str) -> dict[str, object]:
    subset = [r for r in rows if ((r.get("config", {}).get("sweep_metadata", {}) or {}).get("sweep_type") == sweep_type)]
    rewards = [r.get("training_metrics", {}).get("episode_rewards", []) or [] for r in subset]
    flat = any(len(set(series)) <= 1 for series in rewards if series)
    return {
        "present": bool(subset),
        "count": len(subset),
        "nonempty": any(bool(series) for series in rewards),
        "flat": flat,
        "max_episodes": max((len(series) for series in rewards), default=0),
    }


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("[figure8] load sweep_results.json")
    results = json.loads((SOURCE_DIR / "sweep_results.json").read_text(encoding="utf-8"))
    print(f"[figure8] rows={len(results)}")
    lr = _series_stats(results, "learning_rate")
    gamma = _series_stats(results, "discount_factor")
    print(f"[figure8] lr={lr} gamma={gamma}")
    missing: list[str] = []
    if not lr["present"] or not lr["nonempty"]:
        missing.append("learning_rate episode_rewards missing")
    if not gamma["present"] or not gamma["nonempty"]:
        missing.append("discount_factor episode_rewards missing")
    if lr["flat"]:
        missing.append("learning_rate episode_rewards flat")
    if gamma["flat"]:
        missing.append("discount_factor episode_rewards flat")
    if int(lr["max_episodes"]) < 5:
        missing.append("learning_rate episodes < 5")
    if int(gamma["max_episodes"]) < 5:
        missing.append("discount_factor episodes < 5")

    output_png = OUTPUT_DIR / "figure8_reward_timecourse.png"
    if missing:
        render_status_figure(output_png, "Figure 8: data incomplete", missing)
        status = "blocked"
    else:
        plot_figure_8_reward_timecourse(results, str(output_png), "Figure 8: 100-episode training reward")
        status = "exported"
    manifest = {
        "figure_id": "Figure 8",
        "episodes_expected": 100,
        "status": status,
        "source": str(SOURCE_DIR / "sweep_results.json"),
        "output": str(output_png),
        "missing_or_invalid": missing,
        "subfigures": [
            {"id": "fig08a", "series": "learning_rate", "present": lr["present"], "nonempty": lr["nonempty"], "flat": lr["flat"], "max_episodes": lr["max_episodes"]},
            {"id": "fig08b", "series": "discount_factor", "present": gamma["present"], "nonempty": gamma["nonempty"], "flat": gamma["flat"], "max_episodes": gamma["max_episodes"]},
        ],
    }
    write_export_manifest(OUTPUT_DIR, manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
