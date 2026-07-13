#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.analysis.figure_generator import (
    plot_figure_11_lstm_comparison,
    render_status_figure,
    write_export_manifest,
)


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "artifacts/analysis/figure8-11-validation/figure_11"
LSTM_DIR = ROOT_DIR / "artifacts/analysis/figure8-11-validation/figure_11_lstm"
NO_LSTM_DIR = ROOT_DIR / "artifacts/analysis/figure8-11-validation/figure_11_no_lstm"
BASE_DIR = ROOT_DIR / "artifacts/analysis/figure8-11-validation"


# Keep paths absolute; export fallback writes into same tree from any cwd.


def _series_check(results: list[dict]) -> dict[str, object]:
    if not results:
        return {"present": False, "nonempty": False, "flat": False, "points": 0}
    series = results[0].get("training_metrics", {}).get("average_delays", []) or []
    return {"present": True, "nonempty": bool(series), "flat": len(set(series)) <= 1 if series else False, "points": len(series)}


def _training_reward_signature(results: list[dict]) -> tuple[float, ...]:
    if not results:
        return ()
    rewards = results[0].get("training_metrics", {}).get("episode_rewards", []) or []
    return tuple(float(value) for value in rewards)


def _evaluation_reward(results: list[dict]) -> float | None:
    if not results:
        return None
    payload = results[0]
    aggregate = (payload.get("result", {}) or {}).get("evaluation_summary", {}) or {}
    value = aggregate.get("mean_reward")
    return float(value) if value is not None else None


def _is_effectively_same(lstm_results: list[dict], no_lstm_results: list[dict]) -> bool:
    reward_a = _training_reward_signature(lstm_results)
    reward_b = _training_reward_signature(no_lstm_results)
    if reward_a and reward_b:
        return reward_a == reward_b
    eval_a = _evaluation_reward(lstm_results)
    eval_b = _evaluation_reward(no_lstm_results)
    if eval_a is None or eval_b is None:
        return False
    return abs(eval_a - eval_b) < 1e-9


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not (LSTM_DIR / "sweep_results.json").exists() or not (NO_LSTM_DIR / "sweep_results.json").exists():
        from src.analysis.paper_figures_campaign import run_figure_11
        run_figure_11(BASE_DIR, quick=True)
    lstm_results = json.loads((LSTM_DIR / "sweep_results.json").read_text(encoding="utf-8"))
    no_lstm_results = json.loads((NO_LSTM_DIR / "sweep_results.json").read_text(encoding="utf-8"))
    lstm = _series_check(lstm_results)
    no_lstm = _series_check(no_lstm_results)
    missing: list[str] = []
    if not lstm["present"] or not lstm["nonempty"]:
        missing.append("with_lstm delay missing")
    if not no_lstm["present"] or not no_lstm["nonempty"]:
        missing.append("without_lstm delay missing")
    if lstm["flat"] and int(lstm["points"]) > 1:
        missing.append("with_lstm delay flat")
    if no_lstm["flat"] and int(no_lstm["points"]) > 1:
        missing.append("without_lstm delay flat")
    if _is_effectively_same(lstm_results, no_lstm_results):
        missing.append("no_lstm identical to with_lstm")

    output_png = OUTPUT_DIR / "figure11_lstm_comparison.png"
    if missing:
        render_status_figure(output_png, "Figure 11: data incomplete", missing)
        status = "blocked"
    else:
        plot_figure_11_lstm_comparison(lstm_results, no_lstm_results, str(output_png), "Figure 11: 100-episode LSTM ablation")
        status = "exported"
    manifest = {
        "figure_id": "Figure 11",
        "episodes_expected": 100,
        "status": status,
        "source": [str(LSTM_DIR / "sweep_results.json"), str(NO_LSTM_DIR / "sweep_results.json")],
        "output": str(output_png),
        "missing_or_invalid": missing,
        "subfigures": [
            {"id": "fig11a", "series": "with_lstm", "present": lstm["present"], "nonempty": lstm["nonempty"], "flat": lstm["flat"], "points": lstm["points"]},
            {"id": "fig11b", "series": "without_lstm", "present": no_lstm["present"], "nonempty": no_lstm["nonempty"], "flat": no_lstm["flat"], "points": no_lstm["points"]},
        ],
    }
    write_export_manifest(OUTPUT_DIR, manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
