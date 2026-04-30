# Implementation Plan: 004-environment-lifecycle-gym-boundary

**Branch**: `004-environment-lifecycle-gym-boundary` | **Date**: 2026-04-30 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from [`specs/004-environment-lifecycle-gym-boundary/spec.md`](./spec.md)

## Summary

This plan hardens the environment boundary against architectural drift. `HoodieGymEnvironment` must remain the only lifecycle orchestrator. `SlotEngine` must be helper-only, and any controller-shaped lifecycle API such as `run_slot()` must be removed or reduced so it cannot advance a slot or sequence the lifecycle.

## Technical Context

**Language/Version**: Python 3.14.3 in the workspace; repository code is Python and uses modern dataclass/typing features  
**Primary Dependencies**: Standard library only for this feature; no new dependencies, no Gymnasium requirement  
**Storage**: File-backed specs and reference docs only; no database  
**Testing**: Existing unittest-based tests plus lifecycle regression checks for helper-only enforcement  
**Target Platform**: Local development and evaluation on the approved workstation / Linux-compatible Python runtime  
**Project Type**: Research reproduction simulator / library-style package with evaluation and baseline runners  
**Performance Goals**: None beyond preserving the existing environment behavior and avoiding new asymptotic work  
**Constraints**: No dependency changes, no virtual-environment changes, no neural-network code, no ns-3-gym, no reward/metric formula changes, no source-wide refactors  
**Scale/Scope**: Single repository, single environment adapter, shared baseline evaluation path

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

No constitution violations are required. This task is documentation/alignment only, but it explicitly hardens the helper-only boundary and rejects a controller-shaped `SlotEngine`.

## Project Structure

### Documentation (this feature)

```text
specs/004-environment-lifecycle-gym-boundary/
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
├── environment/
│   ├── environment.py
│   ├── gym_adapter.py
│   ├── slot_engine.py
│   ├── private_queue.py
│   ├── public_queue.py
│   ├── offloading_queue.py
│   ├── topology.py
│   ├── trace_source.py
│   ├── runtime_model.py
│   ├── reward_timing.py
│   ├── deadline_rules.py
│   └── task.py
├── policies/
└── evaluation/

tests/
├── unit/
└── integration/
```

**Structure Decision**: Keep orchestration in `src/environment/gym_adapter.py` and keep `src/environment/slot_engine.py` helper-only. The plan does not introduce a new source tree or a new lifecycle runner.

## Current-State Audit

### Already implemented

- `src/environment/gym_adapter.py`: owns the adapter boundary and already contains lifecycle logic.
- `src/environment/slot_engine.py`: currently exposes helper methods and a controller-shaped `run_slot()` API.
- `src/environment/environment.py`: contains state snapshots and finalization helpers.
- `src/environment/reward_timing.py`: contains terminal reward emission.
- `src/environment/runtime_model.py`: contains shared runtime progression helpers.

### Gap to close

- `SlotEngine.run_slot()` exists and sequences lifecycle phases, which is architectural drift against the fixed ownership model.
- The docs need to say that `HoodieGymEnvironment` is the only lifecycle orchestrator and that `SlotEngine` must not expose controller-shaped lifecycle control.

## Research

`research.md` should reflect the fixed architectural decision:

- `HoodieGymEnvironment` owns all episode and slot lifecycle orchestration.
- `SlotEngine` is helper-only.
- `SlotEngine.run_slot()` is drift and must be removed or replaced by a helper-only API that cannot advance a slot or sequence lifecycle phases.

## Architecture Decision

- **Adapter location**: `src/environment/gym_adapter.py`
- **Episode state owner**: `HoodieGymEnvironment`
- **Helper module**: `SlotEngine`
- **Enforcement rule**: `SlotEngine` must not own lifecycle control, must not sequence lifecycle phases, and must not provide a controller-shaped API that can advance a slot.

## Documentation / Contract Alignment Plan

1. Update `research.md` to explicitly state that `SlotEngine.run_slot()` is architectural drift.
2. Update `contracts/environment-boundary.md` to say the adapter owns orchestration and `SlotEngine` is helper-only.
3. Update comments/docstrings in `src/environment/gym_adapter.py` and `src/environment/slot_engine.py` so they do not imply controller ownership.
4. Keep the rest of the feature docs unchanged.

## Constitution Gate

- **Dependency impact**: None.
- **Environment impact**: None.
- **Assumption impact**: None.
- **Fidelity impact**: None.
- **Test impact**: Regression tests are required in the implementation phase, but this plan itself remains documentation-only.
- **Reproducibility impact**: None.
- **Config/schema impact**: None.
- **Public interface impact**: The helper-only boundary wording is aligned.
- **Artifact impact**: None.
- **Security/secret impact**: None.
- **Performance budget impact**: None.
- **Baseline fairness impact**: None.
- **Paper-to-code mapping impact**: Keep mapping intact.
- **Definition-of-done impact**: The task is complete only when the docs and code both prevent `SlotEngine` from acting as a lifecycle controller.

## Migration Plan

- No runtime migration is expected from this planning pass.
- No dependency files should change.
- Implementation should add regression tests later so `SlotEngine` cannot regain lifecycle orchestration.

