#!/usr/bin/env python3
"""Run Figure 8-11 campaign with 50 episodes per experiment, export PNGs."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from src.analysis.figure_generator import generate_all_figures
from src.analysis.paper_figures_campaign import (
    run_figure_8,
    run_figure_9,
    run_figure_10,
    run_figure_11,
    DEFAULT_MANUAL_EPISODES,
)

OUTPUT = Path("artifacts/analysis/paper-figures-50ep")
EPISODES = 50


def main() -> int:
    t0 = time.time()
    OUTPUT.mkdir(parents=True, exist_ok=True)

    print(f"[figures] Starting 50-episode campaign (paper default: {DEFAULT_MANUAL_EPISODES})")
    print(f"[figures] Figure 8: 11 experiments = {11 * EPISODES} episodes")
    print(f"[figures] Figure 9: ~51 experiments = {51 * EPISODES} episodes")
    print(f"[figures] Figure 10: ~140 experiments = {140 * EPISODES} episodes")
    print(f"[figures] Figure 11: 2 experiments = {2 * EPISODES} episodes")
    print(f"[figures] Total: ~{204 * EPISODES} episodes, ~{204 * EPISODES * 110} env steps")
    print()

    # Override the internal episode count — paper_figures_campaign uses
    # _quick_or_full(DEFAULT_MANUAL_EPISODES, quick=False) = DEFAULT_MANUAL_EPISODES.
    # We monkey-patch the module-level constant so run_figure_* use 50.
    import src.analysis.paper_figures_campaign as pfc
    pfc.DEFAULT_MANUAL_EPISODES = EPISODES

    t1 = time.time()
    print("[figures] Figure 8: reward timecourse + LR/gamma sweeps...")
    fig8 = run_figure_8(OUTPUT, quick=False)
    print(f"  done in {time.time() - t1:.0f}s ({len(fig8)} experiments)")

    t1 = time.time()
    print("[figures] Figure 9: parameter sensitivity sweeps...")
    fig9 = run_figure_9(OUTPUT, quick=False)
    print(f"  done in {time.time() - t1:.0f}s ({len(fig9)} experiments)")

    t1 = time.time()
    print("[figures] Figure 10: baseline policy comparison sweeps...")
    fig10 = run_figure_10(OUTPUT, quick=False)
    print(f"  done in {time.time() - t1:.0f}s ({len(fig10)} experiments)")

    t1 = time.time()
    print("[figures] Figure 11: LSTM ablation...")
    fig11_with, fig11_without = run_figure_11(OUTPUT, quick=False)
    print(f"  done in {time.time() - t1:.0f}s ({len(fig11_with) + len(fig11_without)} experiments)")

    # Combine and generate figures
    combined_dir = OUTPUT / "combined_sweeps"
    combined_results = fig8 + fig9 + fig10
    combined_dir.mkdir(parents=True, exist_ok=True)
    (combined_dir / "sweep_results.json").write_text(
        json.dumps(combined_results, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )

    figures_dir = OUTPUT / "figures"
    print(f"\n[figures] Generating plots → {figures_dir}/")
    generate_all_figures(
        str(combined_dir),
        str(figures_dir),
        lstm_sweep_dir=str(OUTPUT / "figure_11_lstm"),
        no_lstm_sweep_dir=str(OUTPUT / "figure_11_no_lstm"),
    )

    pngs = sorted(figures_dir.glob("*.png"))
    elapsed = time.time() - t0
    print(f"\n[figures] Done in {elapsed:.0f}s ({len(pngs)} PNGs)")
    for p in pngs:
        print(f"  {p}")
    print(f"\n[figures] Manifest: {OUTPUT / 'run-manifest.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
