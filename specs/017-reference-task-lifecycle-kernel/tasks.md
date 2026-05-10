# Tasks: Reference Task Lifecycle Kernel

**Input**: Design documents from `/specs/017-reference-task-lifecycle-kernel/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Test-first implementation is required for this feature.

**Organization**: Tasks are grouped by user story so each lifecycle case can be built and verified independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the isolated reference-model package and confirm the repository boundary before lifecycle code is added.

### Quality Gate

- [X] T001 Confirm 017 scope guards and repository hygiene against `main` and document the result in `specs/017-reference-task-lifecycle-kernel/quickstart.md`
- [X] T002 Create the isolated package skeleton `src/reference_model/__init__.py`, `src/reference_model/lifecycle.py`, `src/reference_model/ledger.py`, and `src/reference_model/models.py`
- [X] T003 [P] Add the unit test module shell `tests/unit/test_reference_task_lifecycle_kernel.py`
- [X] T004 [P] Add the integration test module shell `tests/integration/test_reference_task_lifecycle_kernel_flow.py`

**Checkpoint**: Isolated package and test targets exist, and no simulator, policy, training, metric, or campaign files are touched.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define the reference model data structures and deterministic ledger primitives that all lifecycle tests depend on.

**⚠️ CRITICAL**: No user story work begins until the foundational reference types exist.

- [X] T005 Implement immutable task identity and workload dataclasses in `src/reference_model/models.py`
- [X] T006 Implement immutable action and terminal-status dataclasses in `src/reference_model/models.py`
- [X] T007 Implement deterministic ledger event and task ledger dataclasses in `src/reference_model/ledger.py`
- [X] T008 Implement the reference lifecycle transition API shell in `src/reference_model/lifecycle.py`
- [X] T009 Implement deterministic ordering helpers for same-slot or tie conditions in `src/reference_model/ledger.py`

**Checkpoint**: Core reference data structures and deterministic ordering primitives are ready for test-driven lifecycle behavior.

---

## Phase 3: User Story 1 - Deterministic local task ledger (Priority: P1) 🎯 MVP

**Goal**: Verify a single hand-fed task with a local-compute action emits the exact reference ledger in deterministic order.

**Independent Test**: A local-compute input produces `created`, `selected_action`, `execution_started`, `execution_completed`, and terminal-slot `reward_emitted`, with no queue or transmission events.

### Tests for User Story 1

- [X] T010 [US1] Add local-compute ledger test coverage in `tests/unit/test_reference_task_lifecycle_kernel.py`
- [X] T011 [US1] Add repeated-run determinism test coverage in `tests/unit/test_reference_task_lifecycle_kernel.py`

### Implementation for User Story 1

- [X] T012 [US1] Implement local-compute lifecycle emission in `src/reference_model/lifecycle.py`
- [X] T013 [US1] Implement local-compute ledger assembly in `src/reference_model/ledger.py`
- [X] T014 [US1] Expose local-compute transition entry point from `src/reference_model/__init__.py`

**Checkpoint**: Local compute reference behavior is fully testable and isolated from simulator code.

---

## Phase 4: User Story 2 - Deterministic offload lifecycles (Priority: P2)

**Goal**: Verify horizontal and vertical offload paths produce explicit deterministic ledgers with the required queue, transmission, and execution events.

**Independent Test**: A horizontal-offload input emits `selected_action`, `queued_public`, `transmission_started`, `transmission_completed`, `execution_started`, `execution_completed`, and `reward_emitted`; a vertical-offload input emits `selected_action`, `offloaded_cloud`, `transmission_started`, `transmission_completed`, `execution_started`, `execution_completed`, and `reward_emitted`.

### Tests for User Story 2

- [X] T015 [US2] Add horizontal-offload ledger test coverage in `tests/unit/test_reference_task_lifecycle_kernel.py`
- [X] T016 [US2] Add vertical-offload ledger test coverage in `tests/unit/test_reference_task_lifecycle_kernel.py`
- [X] T017 [US2] Add same-slot tie ordering test coverage for offload completions in `tests/unit/test_reference_task_lifecycle_kernel.py`

### Implementation for User Story 2

- [X] T018 [US2] Implement horizontal-offload lifecycle emission in `src/reference_model/lifecycle.py`
- [X] T019 [US2] Implement vertical-offload lifecycle emission in `src/reference_model/lifecycle.py`
- [X] T020 [US2] Extend deterministic ledger assembly for offload paths in `src/reference_model/ledger.py`

**Checkpoint**: Offload reference behavior is testable independently of any policy logic.

---

## Phase 5: User Story 3 - Timeout and delayed reward reference behavior (Priority: P3)

**Goal**: Verify timeout/drop behavior and delayed reward timing are terminal-only and deterministic.

**Independent Test**: A timeout case emits `dropped_timeout` followed by terminal-slot `reward_emitted`, and a non-terminal decision never emits reward.

### Tests for User Story 3

- [X] T021 [US3] Add timeout/drop ledger test coverage in `tests/unit/test_reference_task_lifecycle_kernel.py`
- [X] T022 [US3] Add delayed-reward timing test coverage in `tests/unit/test_reference_task_lifecycle_kernel.py`

### Implementation for User Story 3

- [X] T023 [US3] Implement timeout boundary handling in `src/reference_model/lifecycle.py`
- [X] T024 [US3] Implement terminal-only reward emission in `src/reference_model/lifecycle.py`
- [X] T025 [US3] Extend integration flow coverage for timeout/drop and delayed reward in `tests/integration/test_reference_task_lifecycle_kernel_flow.py`

**Checkpoint**: Timeout and reward timing are reference-fixed and test-covered.

---

## Phase 6: Final Validation & Repository Guard

**Purpose**: Prove the feature is isolated, deterministic, and limited to the approved package and tests.

- [X] T026 Add static source/import isolation guard assertions to `tests/integration/test_reference_task_lifecycle_kernel_flow.py` proving `src/reference_model` does not import, depend on, or reference `HoodieGymEnvironment`, `SlotEngine`, `src/environment`, `src/policies`, `src/training`, `src/metrics`, `campaign` modules, or existing simulator lifecycle modules
- [X] T027 Run the targeted validation command with `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest tests.unit.test_reference_task_lifecycle_kernel tests.integration.test_reference_task_lifecycle_kernel_flow`
- [X] T028 Compare the diff against `main` and verify no forbidden paths changed, no forbidden imports or references exist inside `src/reference_model`, no dependency files changed, no existing campaign artifacts changed, and no simulator lifecycle drift was introduced

**Checkpoint**: Scope, determinism, and repository hygiene are verified before merge.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Stories (Phases 3-5)**: Depend on Foundational completion
- **Final Validation (Phase 6)**: Depends on all targeted user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent MVP path after Foundational
- **User Story 2 (P2)**: Independent offload path after Foundational; does not require policy or baseline work
- **User Story 3 (P3)**: Independent timeout/reward path after Foundational; depends only on shared reference types

### Within Each User Story

- Tests are written first and must fail before implementation
- Data structures before transition logic
- Transition logic before integration coverage
- Each story is complete before moving to the next priority

### Parallel Opportunities

- `T003` and `T004` can run in parallel because they touch different test files
- `T010` and `T011` can run in parallel
- `T015`, `T016`, and `T017` are not parallel-safe because they touch the same file
- `T021` and `T022` are not parallel-safe because they touch the same file
- `T026` must run before `T027` and `T028`

---

## Parallel Example: User Story 1

```bash
Task: "Add local-compute ledger test coverage in tests/unit/test_reference_task_lifecycle_kernel.py"
Task: "Add repeated-run determinism test coverage in tests/unit/test_reference_task_lifecycle_kernel.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate the local-compute ledger and determinism tests

### Incremental Delivery

1. Build the isolated reference package
2. Add local-compute behavior and validate it
3. Add horizontal and vertical offload behavior and validate them
4. Add timeout/drop and delayed reward behavior and validate them
5. Run the repository-scope guard and final diff audit

---

## Format Validation

- All tasks follow the required checklist format
- Every task is atomic and file-specific
- Tests precede implementation for each story
- No task modifies forbidden simulator, policy, campaign, metric, dependency, or artifact paths
- The final audit task explicitly checks source/import isolation from simulator lifecycle modules
- No task introduces DRL, neural networks, Gymnasium, TorchRL, ns-3, or ns-3-gym
