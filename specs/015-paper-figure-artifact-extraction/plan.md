# Implementation Plan: Paper Figure Artifact Extraction and Comparison Scaffold

**Branch**: `015-paper-figure-artifact-extraction` | **Date**: 2026-05-07 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from `/specs/015-paper-figure-artifact-extraction/spec.md`

## Summary

Add a deterministic, read-only extraction layer that maps the HOODIE paper's evaluation figures to committed paper OCR and campaign artifacts. The feature identifies which paper figure requirements are supported, partially supported, or unsupported; extracts artifact-backed metrics where available; preserves OCR evidence; and writes separate machine-readable and human-readable reports without mutating paper or campaign artifacts.

## Technical Context

**Language/Version**: Python 3.x  
**Primary Dependencies**: Python standard library only  
**Storage**: Filesystem inputs and caller-provided report output directory  
**Testing**: `python -m unittest` through `src/.venvmac/bin/python`  
**Target Platform**: Local development and CI on the existing repository environment  
**Project Type**: library/analysis tooling  
**Performance Goals**: Deterministically analyze a single OCR file and one completed campaign artifact tree with serial bounded reads  
**Constraints**: No new dependencies, no simulator reruns, no artifact mutation, no policy changes, no metric formula changes, no lifecycle changes, no training, DRL, TorchRL, LSTM, neural-network, or agent changes  
**Scale/Scope**: Paper OCR for Figures 7-11 plus committed baseline campaign artifacts, optional audit report, and optional sensitivity report

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
specs/015-paper-figure-artifact-extraction/
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
    └── paper_figure_extraction.py

tests/
├── integration/
│   └── test_paper_figure_extraction_flow.py
└── unit/
    └── test_paper_figure_extraction.py
```

**Structure Decision**: Keep the extractor under `src/analysis/` so it can consume committed paper and campaign artifacts as read-only inputs and write reports into a caller-provided output directory.

## Complexity Tracking

No constitution violations require special justification.
