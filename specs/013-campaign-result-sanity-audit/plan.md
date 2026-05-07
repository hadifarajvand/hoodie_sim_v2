# Implementation Plan: Campaign Result Sanity Audit

**Branch**: `013-campaign-result-sanity-audit` | **Date**: 2026-05-07 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from `/specs/013-campaign-result-sanity-audit/spec.md`

## Summary

Add a read-only forensic audit layer for completed campaign artifacts. The audit inspects existing campaign, matrix, bundle, and trace outputs; reports anomalies in drop ratio, policy separation, and scenario separation; and checks finalized-task accounting consistency without rerunning simulations or mutating artifacts.

## Technical Context

**Language/Version**: Python 3.x  
**Primary Dependencies**: Python standard library only  
**Storage**: Filesystem inputs and audit reports under campaign artifact directories  
**Testing**: `python -m unittest`  
**Target Platform**: Local development and CI on the existing repository environment  
**Project Type**: library/analysis tooling  
**Performance Goals**: Audit a completed campaign artifact set deterministically with serial filesystem reads and bounded report generation  
**Constraints**: No new dependencies, no simulation reruns, no artifact mutation, no policy changes, no metric formula changes, no lifecycle changes, read-only analysis only  
**Scale/Scope**: Small-to-moderate completed campaign outputs with per-run JSON, CSV, traces, and summary artifacts

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
specs/013-campaign-result-sanity-audit/
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
    └── campaign_audit.py

tests/
├── integration/
│   └── test_campaign_result_sanity_audit.py
└── unit/
    ├── test_campaign_audit_config.py
    └── test_campaign_audit_report.py
```

**Structure Decision**: Keep the audit under `src/analysis/` so it consumes completed artifacts as inputs and produces reports without touching simulator, policy, or evaluation execution code.

## Complexity Tracking

No constitution violations require special justification.

