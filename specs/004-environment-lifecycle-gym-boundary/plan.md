# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Enforce a hard architecture boundary for the environment lifecycle. `HoodieGymEnvironment` remains the only lifecycle orchestrator, while `SlotEngine` is reduced to helper-only scope and must not expose any controller-shaped API capable of running or sequencing a full slot lifecycle.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.14.3 in the workspace; repository code is Python and uses modern dataclass/typing features  
**Primary Dependencies**: Standard library only for this feature; no new dependencies, no Gymnasium requirement  
**Storage**: File-backed specs and reference docs only; no database  
**Testing**: Existing unittest-based tests plus lifecycle regression checks for helper-only enforcement  
**Target Platform**: Local development and evaluation on the approved workstation / Linux-compatible Python runtime
**Project Type**: Research reproduction simulator / library-style package with evaluation and baseline runners  
**Performance Goals**: None beyond preserving the existing environment behavior and avoiding new asymptotic work  
**Constraints**: No dependency changes, no TorchRL or neural-network changes, no ns-3-gym, no broad refactors, no controller-shaped `SlotEngine` API  
**Scale/Scope**: Single repository, one environment boundary feature, no new external services

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

No constitution violations are required. This task is documentation/alignment only at the plan phase, but it explicitly hardens the helper-only boundary and rejects a controller-shaped `SlotEngine` API.

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
│   ├── gym_adapter.py
│   ├── slot_engine.py
│   ├── environment.py
│   ├── reward_timing.py
│   ├── runtime_model.py
│   ├── topology.py
│   ├── trace_source.py
│   ├── public_queue.py
│   ├── private_queue.py
│   ├── offloading_queue.py
│   └── task.py
├── policies/
└── evaluation/

tests/
├── unit/
└── integration/
```

**Structure Decision**: Keep orchestration in `src/environment/gym_adapter.py` and keep `src/environment/slot_engine.py` helper-only. The plan does not introduce a new source tree or a new lifecycle runner.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No complexity exceptions are required for this plan.
