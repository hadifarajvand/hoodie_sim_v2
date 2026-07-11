# 2026-07-10 Figure Subfigure Wiring Fix

- Scope: wire paper figure reproduction pipeline to simulator metadata and drain-phase action handling.
- Changed: `src/analysis/full_training_reproduction_campaign/config.py`, `src/analysis/paper_figures_campaign.py`, `src/analysis/paper_figure_reproduction.py`, `src/analysis/figure_generator.py`.
- Result: figure export now includes Figure 7 topology PNG plus per-figure panel PNG export hooks for Figures 8-11.
- Validation: `python -m pytest tests/unit/test_paper_figure_reproduction.py -q`.
- Result: `13 passed` before longer end-to-end export run hit runtime on full sweep.
