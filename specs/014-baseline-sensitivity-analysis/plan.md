# Implementation Plan: Baseline Sensitivity Analysis

**Branch**: `014-baseline-sensitivity-analysis` | **Date**: 2026-05-07 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from `/specs/014-baseline-sensitivity-analysis/spec.md`

## Summary

Add a deterministic, read-only sensitivity analysis layer that explains whether the committed baseline collapse is driven by trace collapse, policy behavior collapse, environment saturation, timeout/finalization pressure, or metric aggregation masking. The analysis consumes existing campaign artifacts and emits separate sensitivity reports without modifying simulator behavior or committed outputs.

## Technical Context

**Language/Version**: Python 3.x  
**Primary Dependencies**: Python standard library only  
**Storage**: Filesystem inputs and separate report outputs under a user-provided analysis directory  
**Testing**: `python -m unittest`  
**Target Platform**: Local development and CI on the existing repository environment  
**Project Type**: library/analysis tooling  
**Performance Goals**: Deterministically analyze a completed artifact set with serial filesystem reads and bounded report generation  
**Constraints**: No new dependencies, no simulator reruns, no artifact mutation, no policy changes, no metric formula changes, no lifecycle changes, no training or agent changes, analysis-only inputs and outputs  
**Scale/Scope**: Completed baseline campaign artifact trees with per-run JSON, matrix summaries, trace JSON, and optional audit reports

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Constitution Gate

- [x] Dependency impact checked
- [x] Environment impact checked
- [x] Assumption impact checked
- [x] Fidelity impact checked
- [x] Test impact checked
- [x] Reproducibility impact checked
- [x] Config/schema impact checked
- [x] Public interface impact checked
- [x] Artifact impact checked
- [x] Security/secret impact checked
- [x] Performance budget impact checked
- [x] Baseline fairness impact checked
- [x] Paper-to-code mapping impact checked
- [x] Definition-of-done impact checked

No constitution violations require justification for this feature.

## Project Structure

### Documentation (this feature)

```text
specs/014-baseline-sensitivity-analysis/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── analysis/
    └── baseline_sensitivity.py

tests/
├── integration/
│   └── test_baseline_sensitivity_flow.py
└── unit/
    └── test_baseline_sensitivity.py
```

**Structure Decision**: Keep the analyzer under `src/analysis/` so it can inspect committed artifacts and write separate report outputs without touching simulator, policy, or evaluation execution code.

## Complexity Tracking

No constitution violations require special justification.

