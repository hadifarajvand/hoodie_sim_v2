# Implementation Plan: Reference Task Lifecycle Kernel

**Branch**: `017-reference-task-lifecycle-kernel` | **Date**: 2026-05-09 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from `/specs/017-reference-task-lifecycle-kernel/spec.md`

**Note**: This plan is for a reference-only lifecycle kernel. It is deliberately isolated from the simulator and does not repair, tune, or mutate `HoodieGymEnvironment`.

## Summary

Build a small, deterministic Python reference model that accepts a hand-fed task plus a hand-fed action and emits a stable task ledger for the lifecycle cases defined in the spec. The implementation will be isolated under a new package, use only the Python standard library, and provide exact testable ledgers for local compute, horizontal offload, vertical offload, timeout/drop, delayed reward timing, and same-slot ordering. No simulator lifecycle code, policy logic, campaign orchestration, neural network code, or metric repair will be touched.

## Technical Context

**Language/Version**: Python 3.x using the existing approved environment at `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`  
**Primary Dependencies**: Python standard library only  
**Storage**: N/A; the reference model is in-memory and emits deterministic ledger objects for tests  
**Testing**: `unittest` in the existing repository test layout  
**Target Platform**: Local development and CI on the existing project environment  
**Project Type**: Library-style internal reference model  
**Performance Goals**: Deterministic output for a single task lifecycle with trivial runtime overhead  
**Constraints**: No dependency installation or lockfile changes; no Gymnasium, ns-3, ns-3-gym, TorchRL, neural-network, DRL, baseline policy, campaign runner, simulator repair, or environment mutation  
**Scale/Scope**: One-task reference traces and deterministic test fixtures, not large-scale simulation

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

No violations are required by this plan. Any deviation from these checked gates would be a plan failure.

## Project Structure

### Documentation (this feature)

```text
specs/017-reference-task-lifecycle-kernel/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── reference_model/
    ├── __init__.py
    ├── lifecycle.py
    ├── ledger.py
    └── models.py

tests/
├── integration/
│   └── test_reference_task_lifecycle_kernel_flow.py
└── unit/
    └── test_reference_task_lifecycle_kernel.py
```

**Structure Decision**: Use a new isolated `src/reference_model/` package so the kernel remains clearly separate from `src/environment`, `src/policies`, `src/training`, and the existing artifact pipeline. This is the cleanest way to keep the reference kernel auditable without perturbing the simulator.

## Boundary Isolation Guard

Feature 017 is not merely architecturally isolated; it must be source/import isolated. The `src/reference_model` package must not import or reference `HoodieGymEnvironment`, `SlotEngine`, `src/environment`, `src/policies`, `src/training`, `src/metrics`, campaign runners, or existing campaign artifacts. This is enforced by an integration guard test before implementation is accepted. Any violation fails the feature, even if lifecycle tests pass.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No complexity exceptions are required.
