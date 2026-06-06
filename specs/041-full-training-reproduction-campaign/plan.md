# Implementation Plan: Full Training/Reproduction Campaign

**Branch**: `[041-full-training-reproduction-campaign]` | **Date**: 2026-05-18 | **Spec**: [`spec.md`](spec.md)
**Input**: Feature specification from `/specs/041-full-training-reproduction-campaign/spec.md`

## Summary

Build a staged campaign pipeline that starts with a readiness probe, proceeds through a bounded pilot stage, and only then permits a gated full-training candidate run. The campaign uses live `HoodieGymEnvironment` rollouts, the Feature 039 network API, and Feature 038 contracts, while preserving delayed reward integrity, disjoint train/eval traces, and honest reporting. The plan is explicitly not blind 5000-episode training and does not claim paper reproduction by default.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing HOODIE project code, torch from the approved interpreter, unittest, standard library  
**Storage**: Repository Markdown plan/spec files, JSON/Markdown report artifacts, checkpoint files  
**Testing**: `unittest` contract, pilot, report, and regression suites  
**Target Platform**: Local development environment and repository CI  
**Project Type**: Single-project simulator / research codebase  
**Performance Goals**: Staged execution only; readiness probe and pilot must be bounded, and the full campaign must stay behind explicit approval  
**Constraints**: No dependency changes, no Gymnasium, no TorchRL, no ns-3/ns-3-gym, no reward-timing changes, no topology changes, no baseline-policy changes, no output tuning, no curve fitting, no automatic reproduction claim  
**Scale/Scope**: Readiness probe, 10-episode pilot, optional 25-episode follow-on pilot, and configurable 5000-episode full-campaign candidate behind explicit flag

**Dependency Status**: `available_existing_torch`
**Torch Check**: `import torch` succeeds in `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python` (`2.12.0`)

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
- The campaign is staged and bounded before it ever becomes a 5000-episode run.
- `optimizer_step` is the approved target-update unit; the campaign records it as a user-approved assumption rather than a paper fact.
- The readiness probe reports exposure evidence and requires explicit manual approval instead of fabricating a numeric readiness promise.
- Live environment rollouts are the training source; smoke fixtures are not treated as training evidence.
- Evaluation traces stay disjoint from training traces.
- The final report may record a candidate reproduction claim only when metrics justify it.

## Project Structure

### Documentation (this feature)

```text
specs/041-full-training-reproduction-campaign/
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
└── analysis/
    └── full_training_reproduction_campaign/

tests/
├── unit/
└── integration/

artifacts/
└── analysis/
    └── full-training-reproduction-campaign/
```

**Structure Decision**: This is a single-project analysis/campaign feature. The implementation stays inside `src/analysis/full_training_reproduction_campaign/`, with unit and integration tests under `tests/`, and JSON/Markdown artifacts under `artifacts/analysis/full-training-reproduction-campaign/`. No `contracts/` directory is required because the feature is internally orchestrated and validated through tests and reports rather than external interfaces.

## Complexity Tracking

> No constitution violations require justification. The staged plan is intentionally conservative and keeps the full campaign behind readiness and pilot gates.

## Phase 0: Outline & Research

### Research Questions

1. How should the readiness probe encode “manual approval” without inventing a fake threshold?
2. What minimum campaign policy is needed to support a 10-episode pilot, optional 25-episode follow-on, and an explicitly gated 5000-episode candidate run?
3. How should checkpoint and report metadata distinguish readiness evidence, pilot evidence, and reproduction-candidate evidence?

### Research Deliverable

- `research.md` records:
  - readiness gate policy
  - target-update unit assumption
  - staged budget policy
  - replay source and delayed-reward policy
  - evaluation split policy
  - baseline-reference policy
  - reproduction-claim policy

## Phase 1: Design & Contracts

### Deliverables

- `data-model.md` defining campaign config, stages, readiness results, replay transitions, checkpoints, and report entities
- `quickstart.md` showing the full validation gate with Feature 041 tests plus the required Feature 040, 039, 038, and runtime regression tests
- `checklists/requirements.md` confirming spec quality

### Design Constraints

- `HoodieGymEnvironment` owns orchestration.
- SlotEngine remains helper-only.
- Delayed rewards are emitted only on completion or drop.
- Pending-at-horizon transitions remain non-terminal.
- Legal action masks must not be bypassed.
- Vertical/cloud actions remain independent of Figure 7 adjacency.
- Horizontal actions remain neighbor-only.
- Target updates are allowed only after the approved `optimizer_step` assumption is encoded.
- Training and evaluation traces must remain disjoint.
- The default report must not claim paper reproduction.

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
