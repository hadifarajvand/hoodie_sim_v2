# Tasks: Training Foundation Contract

**Input**: Design documents from `/specs/038-training-foundation-contract/`
**Prerequisites**: `plan.md` (required), `spec.md` (required for user stories), `research.md`, `data-model.md`, `quickstart.md`

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and shared documentation scaffolding

- [ ] T001 Verify preconditions from the active branch and commit state in `tests/integration/test_training_foundation_scope_guard.py`, and block implementation unless all of these assertions pass exactly: `git branch --show-current == 038-training-foundation-contract`; current branch != `main`; `git fetch --all --tags --prune` has been run; `git rev-parse main == git rev-parse origin/main`; `git rev-parse main == git rev-parse 037-baseline-revalidation-after-runtime-repair-complete^{}`; `git diff --name-only 037-baseline-revalidation-after-runtime-repair-complete^{} main` is empty; `git status --short` has no unrelated files; Feature 038 is based on `main` after Feature 037 tag-complete; stale branches `037-baseline-revalidation`, `037-baseline-revalidation-after-runtime-repair`, and any `039-*` branch are not used as the implementation base; implementation is blocked if any prerequisite assertion fails
- [ ] T002 Create analysis package scaffold for `src/analysis/training_foundation_contract/__init__.py` and `src/analysis/training_foundation_contract/report.py`
- [ ] T003 [P] Create artifact output directories for `artifacts/analysis/training-foundation-contract/`
- [ ] T004 [P] Create contract documentation folder for `specs/038-training-foundation-contract/contracts/`

**Checkpoint**: Shared structure and output locations are ready.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Contract definitions and readiness gate foundations that MUST exist before any story work can be considered complete

- [ ] T005 Define the state contract schema and canonical field ordering in `specs/038-training-foundation-contract/data-model.md`
- [ ] T006 Define the action index contract schema and helper-resolved horizontal semantics in `specs/038-training-foundation-contract/data-model.md`
- [ ] T007 Define the replay transition schema with delayed rewards and explicit pending-at-horizon handling in `specs/038-training-foundation-contract/data-model.md`
- [ ] T008 Define the target update frequency contract and record the `2000 iterations` assumption in `specs/038-training-foundation-contract/plan.md`
- [ ] T009 Define the seed protocol and separate train/eval/replay/model/exploration seeds in `specs/038-training-foundation-contract/data-model.md`
- [ ] T010 Define the train/eval split protocol and disjoint trace-bank rules in `specs/038-training-foundation-contract/data-model.md`
- [ ] T011 Define the checkpoint schema metadata contract in `specs/038-training-foundation-contract/data-model.md`
- [ ] T012 Define the terminal outcome exposure gate schema and training-blocked semantics in `specs/038-training-foundation-contract/data-model.md`
- [ ] T013 Define the training foundation report schema and required report fields in `specs/038-training-foundation-contract/research.md`
- [ ] T014 Add the readiness gate audit flow that consumes existing Feature 037 evidence or lightweight HoodieGymEnvironment trace evidence in `src/analysis/training_foundation_contract/report.py`

**Checkpoint**: Foundational contracts are explicit and training remains blocked until the gate is satisfied.

---

## Phase 3: User Story 1 - Training Data Contract (Priority: P1) 🎯 MVP

**Goal**: Define and verify the state, action, and replay contracts so future DRL work consumes a stable, auditable training input/output contract.

**Independent Test**: The contract schema can be inspected and validated without running training code; replay transitions distinguish terminal, non-terminal, and pending-at-horizon samples.

### Tests for User Story 1

- [ ] T015 [P] [US1] Add unit tests for stable state field ordering and paper/runtime-supported-only state scope in `tests/unit/test_training_foundation_contract.py`
- [ ] T016 [P] [US1] Add unit tests for stable action indexing and mask-aware horizontal legality in `tests/unit/test_training_foundation_contract.py`
- [ ] T017 [P] [US1] Add unit tests for delayed rewards and explicit pending-at-horizon replay handling in `tests/unit/test_training_foundation_contract.py`

### Implementation for User Story 1

- [ ] T018 [US1] Implement the state contract schema object in `src/analysis/training_foundation_contract/report.py`
- [ ] T019 [US1] Implement the action index contract schema object in `src/analysis/training_foundation_contract/report.py`
- [ ] T020 [US1] Implement the replay transition schema object in `src/analysis/training_foundation_contract/report.py`

**Checkpoint**: Training-data contract is explicit, versioned, and testable.

---

## Phase 4: User Story 2 - Training Control Contract (Priority: P2)

**Goal**: Define deterministic seed, split, checkpoint, and target-update contracts so future training is reproducible and auditable before any optimizer exists.

**Independent Test**: The seed bundle, train/eval separation, checkpoint metadata, and target-update contract can be inspected independently of any model code.

### Tests for User Story 2

- [ ] T021 [P] [US2] Add unit tests for target update frequency contract recording and explicit iteration-unit handling in `tests/unit/test_training_foundation_contract.py`
- [ ] T022 [P] [US2] Add unit tests for seed protocol separation across train/eval/replay/model/exploration in `tests/unit/test_training_foundation_contract.py`
- [ ] T023 [P] [US2] Add unit tests for disjoint train/eval trace banks in `tests/unit/test_training_foundation_contract.py`
- [ ] T024 [P] [US2] Add unit tests for checkpoint metadata completeness in `tests/unit/test_training_foundation_contract.py`

### Implementation for User Story 2

- [ ] T025 [US2] Implement the target update frequency contract object in `src/analysis/training_foundation_contract/report.py`
- [ ] T026 [US2] Implement the seed protocol schema object in `src/analysis/training_foundation_contract/report.py`
- [ ] T027 [US2] Implement the train/eval split protocol schema object in `src/analysis/training_foundation_contract/report.py`
- [ ] T028 [US2] Implement the checkpoint schema object in `src/analysis/training_foundation_contract/report.py`

**Checkpoint**: Reproducibility and split hygiene are explicit and auditable.

---

## Phase 5: User Story 3 - Readiness Gate and Audit Contract (Priority: P3)

**Goal**: Define the terminal-outcome exposure gate and report contract so training stays blocked while terminal reward exposure is sparse.

**Independent Test**: A lightweight readiness audit or ingestion of existing Feature 037 evidence reports generated arrivals, exposed decisions, terminal outcomes, pending-at-horizon, and blocking status without changing runtime behavior.

### Tests for User Story 3

- [ ] T029 [P] [US3] Add integration tests for terminal-outcome exposure gate blocking behavior when terminal ratio is insufficient in `tests/integration/test_training_readiness_gate.py`
- [ ] T030 [P] [US3] Add integration tests for training-foundation report schema and required no-drift/no-training flags in `tests/integration/test_training_foundation_contract_report.py`
- [ ] T031 [P] [US3] Add integration tests for report artifact generation in `tests/integration/test_training_foundation_contract_report.py`

### Implementation for User Story 3

- [ ] T032 [US3] Implement readiness-gate audit ingestion of Feature 037 evidence in `src/analysis/training_foundation_contract/report.py`
- [ ] T033 [US3] Implement terminal-outcome exposure metrics and training-blocked computation in `src/analysis/training_foundation_contract/report.py`
- [ ] T034 [US3] Emit JSON and Markdown readiness reports under `artifacts/analysis/training-foundation-contract/`

**Checkpoint**: Training remains blocked until the readiness gate explicitly passes.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Repository hygiene, contract documentation, and guardrails

- [ ] T035 [P] Add contract notes for the readiness gate and sparse-terminal blocker in `specs/038-training-foundation-contract/quickstart.md`
- [ ] T036 [P] Update `AGENTS.md` to point to `specs/038-training-foundation-contract/plan.md`
- [ ] T037 Add scope-guard integration tests in `tests/integration/test_training_foundation_scope_guard.py` that explicitly block any change outside these allowed paths: `specs/038-training-foundation-contract/`, `src/analysis/training_foundation_contract/`, `tests/unit/test_training_foundation_contract.py`, `tests/integration/test_training_foundation_contract_report.py`, `tests/integration/test_training_readiness_gate.py`, `tests/integration/test_training_foundation_scope_guard.py`, and `artifacts/analysis/training-foundation-contract/`; and explicitly block these file families: dependency files `requirements*.txt`, `pyproject.toml`, `poetry.lock`, `Pipfile`, `Pipfile.lock`, `environment*.yml`, `setup.py`, `setup.cfg`; runtime/environment contract files `src/environment/`; baseline policy files `src/policies/`; training loop files `src/training/`; neural-network/model/agent/learning files `src/models/`, `src/agents/`, `src/learning/`; replay execution or replay buffer implementation outside schema-only contract definitions `src/replay/`, `src/memory/`; optimizer code; campaign/experiment runners `src/campaigns/`, `artifacts/campaigns/`, and scripts that launch training/evaluation campaigns; and paper registries/resources `resources/papers/`, `artifacts/analysis/user-approved-assumption-patch-registry/`, `artifacts/analysis/runtime-adoption-approved-assumption-registry/`, `artifacts/analysis/baseline-revalidation-after-runtime-repair/`
- [ ] T038 Add report file content checks for `artifacts/analysis/training-foundation-contract/training-foundation-contract-report.json` and `.md` in `tests/integration/test_training_foundation_contract_report.py`

**Checkpoint**: Documentation, guardrails, and report validation are complete.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May reference US1 contracts but remains independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May reference US1/US2 contracts but remains independently testable

### Within Each User Story

- Tests (if included) MUST be written and fail before implementation
- Contracts before report generation
- Report generation before scope-gate finalization
- Story complete before moving to next priority

---

## Parallel Opportunities

- T003 and T004 can run in parallel
- T005 through T014 are sequential contract-definition tasks with minimal overlap
- T015, T016, and T017 can run in parallel
- T021, T022, T023, and T024 can run in parallel
- T029, T030, and T031 can run in parallel
- T035 and T036 can run in parallel
- T037 and T038 can run in parallel once report schema and scope gates exist

---

## Implementation Strategy

### MVP First

1. Lock down the foundational contract schemas and the terminal-outcome exposure gate.
2. Validate the state/action/replay contract behavior.
3. Validate the reproducibility contract behavior.
4. Validate the readiness gate and report artifacts.

### Incremental Delivery

1. Deliver US1 first to establish stable training data contracts.
2. Deliver US2 next to lock reproducibility and split hygiene.
3. Deliver US3 last to prove training remains blocked until terminal exposure is sufficient.
4. Finish with scope and report guardrails so later implementation cannot drift into training code or runtime changes.
