# Implementation Plan: 004-environment-lifecycle-gym-boundary

**Branch**: `004-environment-lifecycle-gym-boundary` | **Date**: 2026-04-30 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from [`specs/004-environment-lifecycle-gym-boundary/spec.md`](./spec.md)

## Summary

This plan only enforces the final orchestration model for the environment boundary. `HoodieGymEnvironment` owns the episode and slot lifecycle orchestration. `SlotEngine` remains a helper module only. No lifecycle ownership moves into `SlotEngine`, and no execution-flow refactor is permitted for this task.

## Technical Context

**Language/Version**: Python 3.14.3 in the workspace; repository code is Python and uses modern dataclass/typing features  
**Primary Dependencies**: Standard library only for this feature; no new dependencies, no Gymnasium requirement  
**Storage**: File-backed specs and reference docs only; no database  
**Testing**: Existing unittest-based tests plus plan/spec verification updates  
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

No constitution violations are required. This task is documentation/alignment only.

## Project Structure

### Documentation (this feature)

```text
specs/004-environment-lifecycle-gym-boundary/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    └── environment-boundary.md
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
│   ├── action_masking.py
│   ├── policy_interface.py
│   ├── flc.py
│   ├── ho.py
│   ├── vo.py
│   ├── ro.py
│   ├── bco.py
│   └── mleo.py
└── evaluation/
    ├── metrics.py
    ├── evaluation_module.py
    ├── runner.py
    └── validation_runner.py

tests/
├── unit/
└── integration/
```

**Structure Decision**: Keep the adapter and lifecycle docs aligned to `src/environment/`, keep policy legality in `src/policies/`, and keep shared metrics/evaluation in `src/evaluation/`. No new source tree is introduced.

## Current-State Audit

### Already implemented

- `src/environment/gym_adapter.py`: existing boundary implementation and compatibility helper.
- `src/environment/slot_engine.py`: slot-phase helper methods.
- `src/environment/environment.py`: state snapshots and task finalization helpers.
- `src/environment/reward_timing.py`: terminal reward emission.
- `src/environment/runtime_model.py`: shared runtime progression and terminal-state resolution.
- `src/policies/action_masking.py` and `src/policies/policy_interface.py`: legality enforcement and policy contract.
- `src/evaluation/metrics.py` and `src/evaluation/evaluation_module.py`: shared metric formulas and aggregation.

### Gap to document

- The source comments and plan/contract language must consistently say that `HoodieGymEnvironment` owns orchestration and `SlotEngine` only provides helper methods.

## Research

`research.md` already resolves the architectural decision: keep `HoodieGymEnvironment` as the episode orchestrator and keep `SlotEngine` as helper-only.

## Architecture Decision

- **Adapter location**: `src/environment/gym_adapter.py`.
- **Episode state owner**: `HoodieGymEnvironment`.
- **Helper module**: `SlotEngine` only.
- **Rule**: no lifecycle control moves into `SlotEngine`; no execution-flow refactor is part of this task.

## Contract / Docs Alignment Plan

1. Update `specs/004-environment-lifecycle-gym-boundary/research.md` to state the fixed orchestration model.
2. Update `specs/004-environment-lifecycle-gym-boundary/contracts/environment-boundary.md` so baseline integration and ownership language match the fixed model.
3. Update relevant comments in `src/environment/gym_adapter.py` and `src/environment/slot_engine.py` to say the same thing.
4. Keep the rest of the feature docs unchanged.

## Constitution Gate

- **Dependency impact**: None.
- **Environment impact**: None.
- **Assumption impact**: None.
- **Fidelity impact**: None.
- **Test impact**: None.
- **Reproducibility impact**: None.
- **Config/schema impact**: None.
- **Public interface impact**: None.
- **Artifact impact**: None.
- **Security/secret impact**: None.
- **Performance budget impact**: None.
- **Baseline fairness impact**: None.
- **Paper-to-code mapping impact**: Keep mapping intact; only alignment wording changes.
- **Definition-of-done impact**: The task is complete when the plan, research, contract, and source comments all state the same ownership model.

## Migration Plan

- No runtime migration is expected.
- No tests need to change for this documentation-only task.
- No dependency files should change.

