# Phase 1 Figure Reproduction Preparation Plan

## Objective
Prepare reproducible generation of HOODIE baseline figures from bounded/full campaign outputs.

## Scope
- Phase 1 only
- Paper-faithful HOODIE baseline
- No Phase 2/DCQ-MADRL

## Candidate Figures to Prepare
- Convergence / reward curve
- Average delay curve
- Deadline violation or drop ratio curve (if available)
- Queue stability / backlog curve (if available)
- Comparison table/plot for legacy 3D/3A vs paper_default 74D/22A

## Required Data Inputs
- Bounded comparison artifacts
- Future campaign JSON/CSV outputs
- Config snapshots
- Random seed metadata

## Required Modules/Files for Later Implementation
- `src/analysis/figure_reproduction/`
- `tests/integration/test_phase1_figure_reproduction_preparation.py`
- `docs/run-logs/2026-06-30-phase1-figure-reproduction-preparation-evidence.md`

## Acceptance Criteria for Future Implementation
- Figures generated only from committed code + runtime artifacts
- No manual spreadsheet editing
- No Phase 2 metrics mixed in
- Source data paths embedded in generated metadata
- Deterministic output names

## Risks
- Bounded metrics are zero-heavy and not suitable for final paper claims
- Full campaign may be required before meaningful curves
- Current 50-slot bounded outputs prove mechanics, not convergence

## Decision Gate
If bounded data is insufficient for meaningful figure, create a full-campaign readiness plan instead of running full campaign immediately.

## Non-goals
- Do not run full training
- Do not generate figures yet
- Do not start Phase 2
- Do not tune hyperparameters