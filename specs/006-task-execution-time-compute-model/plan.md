# Implementation Plan: Task Execution Time & Compute Resource Modeling

**Branch**: `006-task-compute-model` | **Date**: 2026-05-01 | **Spec**: [`specs/006-task-execution-time-compute-model/spec.md`](specs/006-task-execution-time-compute-model/spec.md)
**Input**: Feature specification from `/specs/006-task-execution-time-compute-model/spec.md`

**Note**: This plan continues the completed environment boundary from feature 004 and the paper-backed traffic substrate from feature 005 without changing lifecycle ownership.

## Summary

Add deterministic compute-budget tracking to each task so execution progression reflects the paper-backed relationship between task size, processing density, and destination capacity. The feature keeps `HoodieGymEnvironment` as the lifecycle owner, keeps `SlotEngine` helper-only, and introduces a small execution helper plus compute configuration so tasks can accumulate or spend compute budget across slots until completion or drop.

## Technical Context

**Language/Version**: Python 3.14.3 in the workspace; repository code is Python and uses modern dataclass/typing features  
**Primary Dependencies**: Standard library only for this feature; existing repo modules under `src/environment` and `src/evaluation`; no new external packages  
**Storage**: File-backed specs, docs, and optional JSON trace payloads; no database  
**Testing**: Existing `unittest`-based unit and integration tests plus new compute-execution regression coverage  
**Target Platform**: Local development and Linux-compatible Python runtime  
**Project Type**: Research reproduction simulator / library-style package with environment and evaluation runners  
**Performance Goals**: Compute-budget updates should remain linear in active tasks and should not change slot-step complexity materially  
**Constraints**: No dependency changes, no Gymnasium/ns-3/ns-3-gym, no TorchRL/training/agent/neural-network changes, no lifecycle ownership changes, no stochastic compute model  
**Scale/Scope**: Single repository feature that adds deterministic compute execution and observability only

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

No constitution violations are required. The plan preserves the existing environment lifecycle and adds compute progression as a deterministic execution layer beneath it.

## Project Structure

### Documentation (this feature)

```text
specs/006-task-execution-time-compute-model/
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
│   ├── task.py
│   ├── compute_config.py
│   ├── execution_helper.py
│   ├── gym_adapter.py
│   ├── traffic_generator.py
│   ├── traffic_observer.py
│   ├── reward_timing.py
│   ├── runtime_model.py
│   ├── slot_engine.py
│   └── trace_source.py
├── evaluation/
│   ├── trace_protocol.py
│   └── runner.py
└── policies/

tests/
├── integration/
└── unit/
```

**Structure Decision**: Keep compute configuration and execution helpers in `src/environment/`, keep task state on the shared task model, and integrate compute progression through the existing environment lifecycle and runtime model. `HoodieGymEnvironment` remains the only lifecycle orchestrator and `SlotEngine` remains helper-only.

## Complexity Tracking

No complexity exceptions are required for this plan.
