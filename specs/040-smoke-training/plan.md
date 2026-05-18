# Implementation Plan: Smoke Training

**Branch**: `[040-smoke-training]` | **Date**: 2026-05-18 | **Spec**: [`spec.md`](spec.md)
**Input**: Feature specification from `/specs/040-smoke-training/spec.md`

**Note**: This plan is smoke-only. It defines a bounded deterministic validation run that exercises the Feature 039 model surface, replay-transition handling, delayed reward handling, and reporting path without becoming full training or paper reproduction.

## Summary

Build a tiny deterministic smoke training path that uses the Feature 039 network surface, consumes fixture-first smoke transitions, performs exactly one optimizer step, checks for a finite smoke loss and a parameter change, and writes smoke reports that explicitly state the target network was instantiated but not updated. The feature remains a smoke-only technical exception and does not override the Feature 038 training readiness block.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing HOODIE project code, torch from the approved interpreter, unittest, standard library  
**Storage**: Repository Markdown spec/planning files and JSON/Markdown smoke report artifacts  
**Testing**: `unittest` for contract, determinism, report, and scope validation  
**Target Platform**: Local development environment and repository CI  
**Project Type**: Single-project simulator/research codebase  
**Performance Goals**: One bounded smoke execution, exactly one optimizer step, no long-running training  
**Constraints**: No full training, no campaign runner, no paper reproduction, no target-network update, no dependency edits, no environment/runtime semantic changes, no policy changes, no reward-timing changes, no curve fitting  
**Scale/Scope**: Tiny deterministic smoke batch or fixture rollout; smoke-only engineering validation

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
- The smoke run reuses the Feature 039 model surface and does not change runtime semantics.
- The feature uses deterministic fixture transitions as the primary smoke source; environment rollout, if used, is interface validation only.
- The target-network update meaning from Feature 038 remains unresolved and is not reinterpreted here.
- The implementation stays bounded to a tiny smoke validation and does not become full training or paper reproduction.

## Project Structure

### Documentation (this feature)

```text
specs/040-smoke-training/
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
    └── smoke_training/

tests/
├── integration/
└── unit/
```

**Structure Decision**: This is a single-project smoke-validation feature. The implementation lives in `src/analysis/smoke_training/` and is exercised by focused unit/integration tests under `tests/unit/` and `tests/integration/`. No new runtime or dependency directories are introduced.

## Complexity Tracking

> No constitution violations require justification. The feature is deliberately scoped to a tiny deterministic smoke run, report artifacts, and contract validation.

## Phase 0: Outline & Research

### Research Questions

1. What is the safest smoke-only contract for using deterministic fixture transitions while preserving delayed reward handling?
2. How should the plan record that target-network sync remains blocked by Feature 038 without implying training readiness?
3. What minimal smoke-loss and repeatability checks are sufficient to prove the smoke path works without becoming paper reproduction?

### Research Deliverable

- `research.md` records:
  - smoke data source decision
  - optimizer step limit
  - target-network restriction
  - loss choice
  - replay-buffer scope
  - readiness-block interpretation
  - report-content restrictions

## Phase 1: Design & Contracts

### Deliverables

- `data-model.md` defining smoke config, transition fixtures, batch summary, and report entities
- `quickstart.md` showing the bounded smoke validation command and artifact locations
- `checklists/requirements.md` capturing spec-quality status

### Design Constraints

- The smoke run uses the Feature 039 model surface and the Feature 038 action/state/replay contract.
- The smoke data source is deterministic fixture transitions; environment rollout is optional and interface-only.
- The optimizer step count is fixed at exactly 1.
- Target-network sync or update must not occur.
- The smoke loss is a minimal MSE-style smoke loss over deterministic fixture targets, not paper reproduction.
- Feature 038’s readiness block remains active; this feature does not override it.
- Fixture transitions are validation artifacts only and do not constitute simulator evidence.

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

No dependency edits, runtime changes, policy changes, or reward-timing changes are authorized by this plan.
