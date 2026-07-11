# 2026-07-10 Figure 7 Export Gap Fix

- Scope: add paper topology export to paper figure reproduction pipeline.
- Changed: `src/analysis/figure_generator.py`, `src/analysis/paper_figure_reproduction.py`.
- Result: Figure 7 topology heatmap now exports to PNG plus CSV/JSON rows in `artifacts/analysis/paper-figure-reproduction`.
- Validation: `python -m pytest tests/unit/test_paper_figure_reproduction.py tests/unit/test_paper_state_vector.py -q`.
- Result: `15 passed`.
