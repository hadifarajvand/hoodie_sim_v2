---

description: "Task list for TorchRL-backed HOODIE training"
---

# Tasks: TorchRL-backed HOODIE Training

**Input**: Design documents from `/specs/003-torchrl-hoodie-training/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by setup, foundational prerequisites, user stories, and polish to preserve the required build order and keep simulator, evaluation, validation, packaging, and reproducibility behavior separated from the TorchRL-backed learning path.

## Format: `[ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel if it does not depend on incomplete tasks
- **[US1] / [US2] / [US3]**: User story labels from spec.md
- File paths must be explicit in every task

## Phase 1: Setup

**Purpose**: Establish the documentation and config scaffolding for a TorchRL-backed learning path without changing runtime behavior.

- [X] T001 Create the Phase 12 feature quick reference in `specs/003-torchrl-hoodie-training/quickstart.md` for deterministic training and validation handoff expectations
- [X] T002 Record the TorchRL dependency boundary and environment requirements in `docs/assumptions/hoodie_assumptions.md`
- [X] T003 Update `docs/reproducibility.md` with explicit training, replay, torch, and checkpoint seed provenance fields
- [X] T004 Update `docs/analysis/workflow_reconstruction_audit.md` to distinguish fresh validation from trained validation for the Phase 12 handoff path

## Phase 2: Foundational

**Purpose**: Add the shared config and provenance hooks required before any story-specific learner work can proceed.

- [X] T005 Add explicit TorchRL training config fields, learner type, checkpoint paths, and seed derivation fields in `src/config/config_loader.py`
- [X] T006 Extend the reproducibility guard to validate TorchRL training config presence and fail clearly when learner dependencies or checkpoint sources are unavailable in `src/repro/repro_guard.py`
- [X] T007 Define the deterministic checkpoint manifest schema and validation-mode provenance fields in `src/repro/output_packager.py`
- [X] T008 Preserve unified config compatibility while surfacing new training/checkpoint fields in `src/config/config_loader.py`

## Phase 3: User Story 1 - Train HOODIE with DRL tooling (Priority: P1)

**Goal**: Train HOODIE through a TorchRL-backed learner while keeping the simulator and evaluation contract unchanged.

**Independent Test**: A deterministic training workflow produces a trained HOODIE state and byte-identical packaged outputs for repeated identical runs.

### Tests for User Story 1

- [X] T009 [P] [US1] Add unit tests for state/history tensorization and legal-mask preservation for `src/agents/torchrl_tensor_adapter.py` in `tests/unit/test_agent_components.py`
- [X] T010 [P] [US1] Add unit tests for deterministic learner update and replay-sample consumption for `src/agents/torchrl_hoodie_learner.py` in `tests/unit/test_agent_components.py`
- [X] T011 [P] [US1] Add unit tests for checkpoint manifest round-trip and schema versioning in `tests/unit/test_agent_components.py`
- [X] T012 [P] [US1] Add integration tests for deterministic training and byte-identical packaging in `tests/integration/test_full_pipeline.py`

### Implementation for User Story 1

- [X] T013 [US1] Add the TorchRL-backed HOODIE learner behind the existing agent API in `src/agents/torchrl_hoodie_learner.py`
- [X] T014 [US1] Extend `src/agents/hoodie_agent.py` so the TorchRL learner remains hidden behind the existing `HoodieAgent` contract
- [X] T015 [US1] Convert `PolicyContext` history and legal masks into learner tensors in `src/agents/torchrl_tensor_adapter.py`
- [X] T016 [US1] Route replay sampling and loss computation through `src/agents/hoodie_agent.py`
- [X] T017 [US1] Preserve delayed reward semantics while replacing the current scalar preference fallback through the new learner path in `src/training/delayed_reward_training.py`
- [X] T018 [US1] Implement deterministic checkpoint export/import completeness for learner-enabled HOODIE state in `src/agents/hoodie_agent.py`
- [X] T019 [US1] Package the learned-state manifest and binary payload for training runs in `src/repro/output_packager.py`

## Phase 4: User Story 2 - Preserve existing reproduction contracts (Priority: P1)

**Goal**: Keep validation-only behavior, simulator ownership, baseline evaluation, and packaging stable while optionally consuming a trained HOODIE state.

**Independent Test**: Validation-only runs still work without a checkpoint, and trained-mode validation consumes an explicit trained state without changing metrics or artifact structure.

### Tests for User Story 2

- [X] T020 [P] [US2] Add integration tests for fresh validation default behavior in `tests/integration/test_full_pipeline.py`
- [X] T021 [P] [US2] Add integration tests for explicit trained-state reload during validation in `tests/integration/test_full_pipeline.py`
- [X] T022 [P] [US2] Add integration tests for clear failure when trained validation is requested without a trained state in `tests/integration/test_full_pipeline.py`
- [X] T023 [P] [US2] Add integration tests for packaged metadata byte identity across repeated deterministic runs in `tests/integration/test_full_pipeline.py`

### Implementation for User Story 2

- [X] T024 [US2] Wire trained-state loading into the pipeline handoff in `src/run_pipeline.py`
- [X] T025 [US2] Keep validation-only defaulting to a fresh HOODIE agent in `src/run_pipeline.py`
- [X] T026 [US2] Ensure validation artifacts record trained versus fresh validation mode in `src/repro/output_packager.py`
- [X] T027 [US2] Preserve baseline, evaluation, validation-comparison, analysis, and packaging behavior while isolating TorchRL to HOODIE training in `src/run_pipeline.py`
- [X] T028 [US2] Document the validation handoff and fresh-by-default behavior in `docs/reproducibility.md`

## Phase 5: User Story 3 - Keep training auditable and reproducible (Priority: P2)

**Goal**: Make trained HOODIE state, provenance, and output identity traceable across deterministic runs.

**Independent Test**: Packaged artifacts expose the config snapshot, validation mode, and trained-state source unambiguously and remain byte-identical for identical runs.

### Tests for User Story 3

- [X] T029 [P] [US3] Add tests for explicit provenance fields in `tests/integration/test_full_pipeline.py`
- [X] T030 [P] [US3] Add tests for deterministic seed derivation and reproducible checkpoint identity in `tests/unit/test_agent_components.py`
- [X] T031 [P] [US3] Add tests for validation packaging provenance clarity in `tests/integration/test_full_pipeline.py`

### Implementation for User Story 3

- [ ] T032 [US3] Define the deterministic checkpoint manifest and validation provenance schema in `src/repro/output_packager.py`
- [ ] T033 [US3] Add deterministic seed derivation for training, replay, and TorchRL internals in `src/config/config_loader.py`
- [ ] T034 [US3] Record trained-state provenance in packaged metadata in `src/repro/output_packager.py`
- [ ] T035 [US3] Update `docs/analysis/workflow_reconstruction_audit.md` and `docs/reproducibility.md` to document fresh/trained validation provenance and unresolved paper-exact learning details

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Clean up documentation, assumptions, and final reproducibility notes without changing behavior.

- [ ] T036 [P] Update `docs/assumptions/hoodie_assumptions.md` to mark unresolved HOODIE learning math and TorchRL-specific details as assumption-backed
- [ ] T037 [P] Update `docs/analysis/hoodie_superiority_gap.md` to reflect TorchRL-backed training while keeping the no-superiority caveat
- [ ] T038 Verify the full deterministic test suite with `python3 -m unittest discover -s tests -p 'test*.py'`

## Dependencies

- Phase 1 tasks establish the documentation and config scaffolding.
- Phase 2 tasks must complete before any user-story implementation.
- US1 is the first deliverable and is the minimum viable TorchRL-backed training slice.
- US2 depends on the trained-state handoff from US1.
- US3 depends on the provenance and checkpoint artifacts from US1 and US2.
- Phase 6 runs after all user stories are implemented.

## Parallel Execution Examples

### User Story 1

- `T009`, `T010`, and `T011` can run in parallel because they target different test concerns in the same test file.
- `T013`, `T014`, and `T015` are sequential because they touch the shared HOODIE learner path.
- `T016` can follow once the learner path exists.

### User Story 2

- `T020`, `T021`, `T022`, and `T023` can run in parallel because they are independent integration checks.
- `T024` and `T025` are sequential because they both affect pipeline handoff behavior.

### User Story 3

- `T029`, `T030`, and `T031` can run in parallel because they cover distinct provenance concerns.
- `T032`, `T033`, and `T034` are sequential with the packaging/provenance layer.

## Implementation Strategy

1. Deliver US1 first so the TorchRL learner can train and produce a reusable trained state.
2. Deliver US2 next so validation can consume trained state while preserving fresh validation defaults.
3. Deliver US3 last so provenance and deterministic packaging are explicit and auditable.
4. Finish with documentation cleanup and a full deterministic test run.
