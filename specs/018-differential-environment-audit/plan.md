# Implementation Plan: Differential Environment Audit

**Branch**: `018-differential-environment-audit` | **Date**: 2026-05-10 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from `/specs/018-differential-environment-audit/spec.md`

**Note**: This plan is for a diagnostic-only audit. It compares the Feature 017 reference kernel against the current HoodieGymEnvironment and must not repair, tune, normalize, or mutate simulator behavior.

## Summary

Build an isolated audit module that runs deterministic toy cases against the Feature 017 reference kernel and the current environment through the public `reset`/`step` lifecycle interface only. The audit emits deterministic JSON and Markdown comparison artifacts that classify matches, divergences, assumption gaps, unsupported traces, and instrumentation gaps without collapsing them into a single mismatch. No simulator repair, policy work, baseline work, campaign orchestration, metric formula changes, or dependency drift are allowed.

## Technical Context

**Language/Version**: Python 3.x using the existing approved interpreter at `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`  
**Primary Dependencies**: Python standard library only  
**Storage**: Deterministic JSON and Markdown artifacts under `artifacts/analysis/differential-environment-audit/`  
**Testing**: `unittest` in the existing repository layout  
**Target Platform**: Local development and CI on the existing project environment  
**Project Type**: Internal analysis / audit module  
**Performance Goals**: Deterministic report generation for a small fixed set of toy cases  
**Constraints**: No dependency installation or lockfile changes; no Gymnasium, ns-3, ns-3-gym, TorchRL, DRL, neural networks, campaign orchestration, metric formula changes, or simulator repair  
**Scale/Scope**: A bounded audit over a small deterministic toy-case set, not a simulator replay engine

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

No violations are required by this plan. Any attempt to repair or normalize environment behavior would fail the feature boundary.

## Project Structure

### Documentation (this feature)

```text
specs/018-differential-environment-audit/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── audits/
    └── differential_environment/
        ├── __init__.py
        ├── audit.py
        ├── cases.py
        ├── report.py
        └── classify.py

tests/
├── integration/
│   └── test_differential_environment_audit_flow.py
└── unit/
    └── test_differential_environment_audit.py
```

**Structure Decision**: Use a new isolated `src/audits/differential_environment/` package so the feature is clearly separated from `src/environment`, `src/policies`, `src/training`, and the simulator lifecycle code. The audit may import `src/reference_model` and the current environment public interface, but it must never modify either target.

## Boundary Isolation Guard

Feature 018 is diagnostic only. The audit module must not import, patch, or depend on `HoodieGymEnvironment`, `SlotEngine`, `src/environment`, `src/policies`, `src/training`, `src/metrics`, campaign runners, or existing campaign artifacts. The integration guard must assert that the audit remains read-only and that any unsupported trace support is classified as `instrumentation_gap` or `unsupported_by_environment_trace`, not repaired. Any violation fails the feature even if comparison tests pass.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No complexity exceptions are required.

