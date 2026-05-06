# Implementation Plan: 007-adaptive-policy-offloading-decisions

**Branch**: `008-adaptive-policy-offloading` | **Date**: 2026-05-06 | **Spec**: `/Users/hadi/Documents/GitHub/hoodie_sim_v2/specs/007-adaptive-policy-offloading-decisions/spec.md`
**Input**: Feature specification from `/specs/007-adaptive-policy-offloading-decisions/spec.md`

## Summary

Add a conservative adaptive offloading layer that enriches the existing `PolicyContext` with paper-backed task, load, traffic, and compute signals, then chooses a single legal action deterministically without changing environment lifecycle ownership or introducing learned policy behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Standard library only for feature code; existing project dependencies unchanged  
**Storage**: File-based specs, code, and test artifacts; no new persistent store  
**Testing**: `unittest` suite already used by the repo  
**Target Platform**: Local simulation and evaluation on the existing Linux/macOS development workflow  
**Project Type**: Simulation environment plus policy layer  
**Performance Goals**: Deterministic action selection with no measurable lifecycle overhead beyond observation enrichment  
**Constraints**: No dependency changes; no TorchRL, neural-network, or training code changes; no Gymnasium/ns-3/ns-3-gym; no lifecycle ownership changes; no silent illegal-action remapping  
**Scale/Scope**: Single-repository feature touching policy/evaluation context layers, docs, and tests only

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

Constitution review:
- The feature stays inside policy and evaluation context layers.
- `HoodieGymEnvironment` remains policy-agnostic and lifecycle-owned.
- `SlotEngine` remains helper-only.
- The adaptive policy is a conservative heuristic, not a learned controller.
- Any paper gap is documented as an assumption, not filled silently.

## Project Structure

### Documentation (this feature)

```text
specs/007-adaptive-policy-offloading-decisions/
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
├── policies/
│   ├── adaptive_context.py
│   ├── adaptive_offloading.py
│   ├── policy_interface.py
│   └── __init__.py
├── evaluation/
│   └── runner.py
└── environment/
    └── gym_adapter.py

tests/
├── integration/
│   └── test_adaptive_policy_environment_flow.py
└── unit/
    ├── test_adaptive_context.py
    └── test_adaptive_offloading_policy.py
```

**Structure Decision**: Add two policy modules under `src/policies/` and keep all environment lifecycle behavior in `src/environment/gym_adapter.py` unchanged except for the already-existing policy-facing observation surface. Keep validation in unit and integration tests only.

## Complexity Tracking

No constitution violations are expected. This plan deliberately avoids new dependencies, environment lifecycle changes, training code, and metric formula changes.
