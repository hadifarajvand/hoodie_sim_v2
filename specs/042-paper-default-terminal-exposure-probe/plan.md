# Implementation Plan: Paper-default Terminal Exposure Probe

**Branch**: `[042-paper-default-terminal-exposure-probe]` | **Date**: 2026-05-18 | **Spec**: [`spec.md`](spec.md)
**Input**: Feature specification from `/specs/042-paper-default-terminal-exposure-probe/spec.md`

## Summary

Build a diagnostic-only probe that runs the repaired paper-default runtime at `T = 110`, compares deterministic probe strategies, and reports whether terminal or reward-bearing terminal outcomes appear without changing simulator semantics, reward timing, or policy behavior. The feature is explicitly not training and does not authorize Feature 041 progression.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing HOODIE project code, approved interpreter torch install, standard library, unittest  
**Storage**: Repository Markdown/JSON artifacts and trace outputs  
**Testing**: `unittest` unit and integration suites  
**Target Platform**: Local development environment and repository CI  
**Project Type**: Single-project diagnostic probe  
**Performance Goals**: Bounded probe runs with reproducible counters per strategy and seed  
**Constraints**: No dependency changes, no training, no optimizer steps, no replay training, no target updates, no reward-timing changes, no runtime/environment semantic changes, no policy redesign, no curve fitting, no paper reproduction claim  
**Scale/Scope**: Paper-default horizon probe with deterministic strategies and diagnostic reporting only

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
- The probe must stay diagnostic and must not become a training pathway.
- `T = 110` is the paper-default horizon used to answer the terminal-exposure question.
- Delayed reward timing remains unchanged and pending-at-horizon stays non-terminal.
- Local, horizontal, and vertical/cloud action behavior must be reported separately.
- Any result that lacks terminal exposure must be reported honestly without tuning the simulator.

## Project Structure

### Documentation (this feature)

```text
specs/042-paper-default-terminal-exposure-probe/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── analysis/
    └── paper_default_terminal_exposure_probe/

tests/
├── unit/
└── integration/

artifacts/
└── analysis/
    └── paper-default-terminal-exposure-probe/
```

**Structure Decision**: Keep the implementation inside `src/analysis/paper_default_terminal_exposure_probe/` with unit and integration tests under `tests/`, and report artifacts under `artifacts/analysis/paper-default-terminal-exposure-probe/`.

## Complexity Tracking

> No constitution violations require justification. The plan is intentionally narrow and diagnostic-only.

## Phase 0: Outline & Research

### Research Questions

1. Which deterministic probe strategies are the least misleading for separating action-legality effects from environment exposure effects?
2. What report schema is needed to make terminal exposure, reward-bearing exposure, pending-at-horizon behavior, and lifecycle integrity explicit?
3. How should the probe preserve the paper-default runtime assumptions without changing semantics?

### Research Deliverable

- `research.md` records:
  - paper-default horizon policy
  - probe strategy policy
  - reward timing and pending-at-horizon policy
  - lifecycle integrity policy
  - no-training / no-reproduction policy

## Phase 1: Design & Contracts

### Deliverables

- `data-model.md` defining probe configuration, strategies, per-strategy counters, aggregate summary, and report entities
- `quickstart.md` showing the probe command and validation gate
- `checklists/requirements.md` confirming spec quality

### Design Constraints

- Use the repaired paper-default runtime horizon `T = 110`, not the short readiness probe horizon.
- Do not alter timeout, deadline, CPU capacity, transmission delay, queue execution, or reward timing.
- Delayed rewards remain tied only to completion or drop.
- Pending-at-horizon remains non-terminal.
- Local, horizontal, and vertical/cloud action counts must be separated in reporting.
- Legal action masks must be respected.
- No training is performed.
- Feature 041 remains readiness-blocked unless a separate manual approval occurs later.

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

No dependency edits, environment semantic changes, policy changes, or reward-timing changes are authorized by this plan.
