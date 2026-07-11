#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from src.analysis.figure_generator import plot_figure_11_lstm_comparison


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "artifacts/analysis/figure8-11-validation/figure_11"
LSTM_DIR = ROOT_DIR / "artifacts/analysis/figure8-11-validation/lstm"
NO_LSTM_DIR = ROOT_DIR / "artifacts/analysis/figure8-11-validation/no_lstm"
BASE_DIR = ROOT_DIR / "artifacts/analysis/figure8-11-validation"


# Keep paths absolute; export fallback writes into same tree from any cwd.


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


def _series_check(results: list[dict]) -> dict[str, object]:
    if not results:
        return {"present": False, "nonempty": False, "flat": False, "points": 0}
    series = results[0].get("training_metrics", {}).get("average_delays", []) or []
    return {"present": True, "nonempty": bool(series), "flat": len(set(series)) <= 1 if series else False, "points": len(series)}


def _is_effectively_same(lstm_results: list[dict], no_lstm_results: list[dict]) -> bool:
    if not lstm_results or not no_lstm_results:
        return False
    a = lstm_results[0].get("training_metrics", {}).get("average_delays", []) or []
    b = no_lstm_results[0].get("training_metrics", {}).get("average_delays", []) or []
    return a == b


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
    if lstm["flat"]:
        missing.append("with_lstm delay flat")
    if no_lstm["flat"]:
        missing.append("without_lstm delay flat")
    if int(lstm["points"]) < 2:
        missing.append("with_lstm points < 2")
    if int(no_lstm["points"]) < 2:
        missing.append("without_lstm points < 2")
    if _is_effectively_same(lstm_results, no_lstm_results):
        missing.append("no_lstm identical to with_lstm")

    output_png = OUTPUT_DIR / "figure11_lstm_comparison.png"
    if missing:
        _render_status_png(output_png, "Figure 11: data incomplete", missing)
        status = "blocked"
    else:
        plot_figure_11_lstm_comparison(lstm_results, no_lstm_results, str(output_png), "Figure 11: 5-episode LSTM ablation")
        status = "exported"
    manifest = {
        "figure_id": "Figure 11",
        "episodes_expected": 5,
        "status": status,
        "source": [str(LSTM_DIR / "sweep_results.json"), str(NO_LSTM_DIR / "sweep_results.json")],
        "output": str(output_png),
        "missing_or_invalid": missing,
        "subfigures": [
            {"id": "11a", "series": "with_lstm", "present": lstm["present"], "nonempty": lstm["nonempty"], "flat": lstm["flat"], "points": lstm["points"]},
            {"id": "11b", "series": "without_lstm", "present": no_lstm["present"], "nonempty": no_lstm["nonempty"], "flat": no_lstm["flat"], "points": no_lstm["points"]},
        ],
    }
    (OUTPUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
