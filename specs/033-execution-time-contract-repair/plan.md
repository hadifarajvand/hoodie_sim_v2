# Implementation Plan: Execution-Time Contract Repair

**Branch**: `034-execution-time-contract-repair` | **Date**: 2026-05-12 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from `/specs/033-execution-time-contract-repair/spec.md`

## Summary

Repair the simulator execution contract so each supported destination consumes at most its configured per-slot compute capacity. Remove the local/private shortcut that can consume all remaining cycles in one slot. Preserve Feature 032 capacities, preserve reward timing, and keep timeout/drop evaluation correct when tasks require multiple slots.

## Technical Context

**Language/Version**: Python 3.x  
**Primary Dependencies**: Existing project modules only  
**Storage**: Files for configs, specs, tests, and analysis artifacts  
**Testing**: `unittest` with integration coverage  
**Target Platform**: Local simulator/runtime execution  
**Project Type**: Simulation/research codebase  
**Performance Goals**: Slot execution must remain deterministic and bounded by configured capacity  
**Constraints**: No dependency changes, no training changes, no neural-network changes, no transmission-delay wiring  
**Scale/Scope**: Feature-scoped repair affecting execution helper, runtime parity, and targeted tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

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

No constitution violations require justification. The repair stays inside execution-time semantics and preserves Feature 032 runtime contracts.

## Project Structure

### Documentation (this feature)

```text
specs/033-execution-time-contract-repair/
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
└── evaluation/

tests/
├── unit/
└── integration/
```

**Structure Decision**: This is a single-repo simulator repair. Scope is limited to `src/environment/`, `src/evaluation/`, `tests/unit/`, `tests/integration/`, and feature analysis artifacts under `artifacts/analysis/execution-time-contract-repair/`.

## Phase 0: Outline & Research

### Research Notes

- The local/private shortcut in `src/environment/execution_helper.py` is the only behavior that violates the repaired contract.
- The runtime model can stay intact unless tests prove its progress or terminal-state handling contradicts the execution helper.
- Completion-slot semantics must be explicit so tests can assert the exact slot boundary without changing reward timing.

## Phase 1: Design & Contracts

### Data Model

- `ExecutionProgressRecord`: captures cycles before/consumed/after, destination kind, and completion state for one slot.
- `Task Cycle State`: tracks remaining cycles, completion slot, terminal outcome, and reward emission status.
- `Destination Kind`: identifies the execution path and the corresponding per-slot capacity.

### Contracts

- [`execution-time-contract.md`](./contracts/execution-time-contract.md): documents per-slot execution accounting and completion semantics.

### Quickstart

1. Run the targeted unit and integration tests for execution progression.
2. Verify a task requiring more than the configured capacity spans multiple slots.
3. Verify timeout/drop still resolves after execution progress.
4. Verify reward is emitted only on terminal completion or drop.

## Complexity Tracking

No constitution violations require a complexity waiver. The work remains a narrow runtime repair.
