# Implementation Plan: Paper HOODIE Network Implementation

**Branch**: `[039-paper-hoodie-network-implementation]` | **Date**: 2026-05-14 | **Spec**: [`spec.md`](spec.md)
**Input**: Feature specification from `/specs/039-paper-hoodie-network-implementation/spec.md`

**Note**: This plan is architecture-only. It defines the network surface, shape validation, and report artifacts needed before any training implementation is approved.

## Summary

Define the paper HOODIE network architecture surface only: a Dueling DQN-compatible network family with separate Q-network and LSTM configuration, online and target network instantiation, and Double-DQN-compatible forward surfaces. The feature is dependency-blocked in the current approved interpreter because torch is not available; no dependency files may be edited to bypass that blocker.

## Technical Context

**Language/Version**: Python 3.11, documentation-plus-architecture feature  
**Primary Dependencies**: Existing HOODIE project code; torch is currently unavailable in the approved interpreter and must not be added via dependency edits  
**Storage**: Repository Markdown specs plus JSON/Markdown architecture analysis artifacts  
**Testing**: `unittest` for config, shape, report, and scope validation  
**Target Platform**: Local development environment and repository CI  
**Project Type**: Single-project simulator/research codebase  
**Performance Goals**: No runtime performance change; shape validation must remain lightweight  
**Constraints**: No training loop, no optimizer step, no replay execution, no campaign runner, no environment/runtime changes, no policy changes, no dependency changes, no reward-timing changes, no paper reproduction claims  
**Scale/Scope**: Architecture surface only; future training remains blocked by Feature 038 readiness gates

**Dependency Status**: `dependency_blocked`
**Torch Check**: `ModuleNotFoundError: No module named 'torch'` in the approved interpreter at `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`

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

Constitution summary:
- The feature does not add or modify runtime semantics.
- The feature does not add training code or dependencies.
- The feature preserves baseline fairness by keeping the Feature 038 contracts as the input/output boundary.
- If torch remains unavailable in the approved interpreter, implementation is blocked and must stop with a dependency-blocked report.

## Project Structure

### Documentation (this feature)

```text
specs/039-paper-hoodie-network-implementation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/
├── analysis/
│   └── paper_hoodie_network_implementation/
└── models/
    └── hoodie_network.py   # only if torch is already available and dependency-approved

tests/
├── integration/
└── unit/
```

**Structure Decision**: This feature is architecture- and validation-first. The expected source-code surface is the new analysis package and, only if torch is already available in the approved interpreter, the model definition file under `src/models/hoodie_network.py`. If torch remains unavailable, the source model file is not created and the feature remains dependency-blocked.

## Complexity Tracking

> No constitution violations require a complexity justification at this stage. The feature is deliberately scoped to architecture, validation, and report artifacts.

## Phase 0: Outline & Research

### Research Questions

1. What architecture-only contract is safest for the paper HOODIE network surface given the existing Feature 038 training foundation contracts?
2. How should the plan record torch unavailability so the branch remains dependency-blocked without mutating dependency files?
3. What config validation rules best prevent the paper’s sloppy reused `N_L` notation from leaking into code or report artifacts?

### Research Deliverable

- `research.md` must record decisions, rationale, and alternatives considered for:
  - dependency status handling
  - input/output shape contract
  - action count contract
  - generic horizontal action handling
  - LSTM placement and shape contract
  - dueling architecture contract
  - Double-DQN-compatible API surface
  - deterministic initialization protocol

## Phase 1: Design & Contracts

### Deliverables

- `data-model.md` defining the architecture config, network entities, and validation rules
- `quickstart.md` showing how to validate architecture and report artifacts with the approved interpreter
- `checklists/requirements.md` capturing specification quality status
- updated agent context reference in `AGENTS.md`

### Design Constraints

- The architecture consumes Feature 038 contracts only.
- The stable action count remains 3.
- The architecture keeps q-network hidden layers separate from LSTM configuration.
- The LSTM encodes the W=10 history before the Q-network body.
- Dueling value and advantage heads branch after the shared body.
- Online and target networks are architecture-compatible and expose the same forward API shape.
- Double-DQN scope is limited to architecture surfaces only; no loss, target update, or training step is implemented.
- If torch remains unavailable in the approved interpreter, the feature is dependency-blocked and no dependency files are edited.

## Constitution Re-check After Design

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

No runtime or dependency changes are authorized by this plan.
