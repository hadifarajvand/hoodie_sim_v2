# Implementation Plan: 009-paper-backed-evaluation-matrix

**Branch**: `008-adaptive-policy-offloading` | **Date**: 2026-05-06 | **Spec**: `/Users/hadi/Documents/GitHub/hoodie_sim_v2/specs/009-paper-backed-evaluation-matrix/spec.md`
**Input**: Feature specification from `/specs/009-paper-backed-evaluation-matrix/spec.md`

## Summary

Build a serial, deterministic evaluation matrix runner that iterates implemented policies across paper-backed traffic scenarios and seeds using the shared `HoodieGymEnvironment` reset/step boundary, then stores auditable per-run and aggregate artifacts without changing metric formulas or adding dependencies.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Standard library only for the matrix feature; existing project dependencies unchanged  
**Storage**: File-based specs and machine-readable evaluation artifacts on disk  
**Testing**: Existing `unittest` suite plus new unit and integration tests for the matrix runner  
**Target Platform**: Local developer execution on the repo’s standard Linux/macOS workflow  
**Project Type**: Simulation evaluation tool layered over the existing simulator  
**Performance Goals**: Deterministic serial matrix execution with reproducible output ordering  
**Constraints**: No dependency changes; no training, agent, neural-network, TorchRL, ns-3, or policy-specific environment paths; no lifecycle ownership changes; no parallel execution  
**Scale/Scope**: Feature-local orchestration under `src/evaluation/` plus tests and docs

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
- The runner stays inside evaluation orchestration and does not touch lifecycle ownership.
- Policies remain external and are selected from an approved registry.
- Traffic scenarios are limited to the paper-backed set already recovered in the repository.
- Matrix output is reproducible, serial, and artifact-driven.

## Project Structure

### Documentation (this feature)

```text
specs/009-paper-backed-evaluation-matrix/
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
└── evaluation/
    ├── matrix_config.py
    ├── policy_registry.py
    ├── scenario_registry.py
    └── matrix_runner.py

tests/
├── integration/
│   └── test_evaluation_matrix_runner.py
└── unit/
    ├── test_evaluation_matrix_config.py
    ├── test_policy_registry.py
    └── test_scenario_registry.py
```

**Structure Decision**: Keep all matrix orchestration under `src/evaluation/` so the feature stays in the evaluation layer and does not introduce special policy or environment code paths.

## Complexity Tracking

No constitution violations are expected. The feature is intentionally narrow: serial orchestration, registry validation, and artifact emission only.
