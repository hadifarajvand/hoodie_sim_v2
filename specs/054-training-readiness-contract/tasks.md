# Tasks: Training Readiness Contract

**Input**: Design documents from `/specs/054-training-readiness-contract/`  
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are explicitly requested in the feature brief. Each story includes its own tests so the feature can be validated incrementally.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and baseline analysis package structure

- [X] T001 [P] Create the Feature 054 analysis package scaffold in `src/analysis/training_readiness_contract/{__init__.py,__main__.py,config.py,model.py,runner.py,report.py}`
- [X] T002 [P] Define Feature 054 committed-input file map, output paths, and feature metadata in `src/analysis/training_readiness_contract/config.py`
- [X] T003 [P] Define report model containers, verdict vocabulary, and alignment/lock validation helpers in `src/analysis/training_readiness_contract/model.py`
- [X] T004 [P] Create the report serialization and Markdown rendering scaffolding in `src/analysis/training_readiness_contract/report.py`

**Checkpoint**: Feature 054 package exists and the report vocabulary is defined.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core shared logic that MUST be complete before any user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 [P] Implement committed prior-artifact loaders for Features 048, 049, 050, 051, 052, and 053 in `src/analysis/training_readiness_contract/runner.py`
- [X] T006 [P] Implement Feature 053 readiness gate validation from committed report artifacts in `src/analysis/training_readiness_contract/runner.py`
- [X] T007 [P] Implement shared training-contract lock evaluation helpers for the paper-default config and contract families in `src/analysis/training_readiness_contract/model.py`
- [X] T008 [P] Implement shared blocker routing and verdict selection helpers in `src/analysis/training_readiness_contract/runner.py`

**Checkpoint**: Foundation ready - all user stories can now be implemented in parallel.

---

## Phase 3: User Story 1 - Verify the Evidence Chain Before Training Is Considered (Priority: P1) 🎯 MVP

**Goal**: Verify that the committed Feature 048 through 053 evidence chain is intact before any training-readiness decision is made.

**Independent Test**: Generate the report and confirm it accepts only the committed Feature 048 through 053 reports as inputs, marks the evidence chain as ready only when those reports are present and internally consistent, and blocks the contract otherwise.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T009 [P] [US1] Add schema tests for the Feature 053 readiness gate and evidence-chain fields in `tests/unit/test_training_readiness_contract_schema.py`
- [X] T010 [P] [US1] Add integration tests for committed prior-artifact gate verification in `tests/integration/test_training_readiness_contract.py`

### Implementation for User Story 1

- [X] T011 [US1] Implement the Feature 053 readiness gate evaluation and evidence-chain readiness decision in `src/analysis/training_readiness_contract/runner.py`
- [X] T012 [US1] Emit the Feature 053 prerequisite verification summary and evidence-chain gate fields in `src/analysis/training_readiness_contract/report.py`

**Checkpoint**: Feature 053 evidence-chain readiness is independently testable.

---

## Phase 4: User Story 2 - Lock the Training Contract Boundaries (Priority: P2)

**Goal**: Expose and evaluate each training-boundary contract lock independently so the first failing family is explicit.

**Independent Test**: Generate the report and verify that the paper-default config, observation, action, legality, reward, timeout, capacity, transmission, queue, metric, seed, and artifact contracts are reported independently with lock states and blockers.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [X] T013 [P] [US2] Add metrics tests for all contract lock fields and their failure routing in `tests/unit/test_training_readiness_contract_metrics.py`
- [X] T014 [P] [US2] Add integration tests for contract-family blocker classification in `tests/integration/test_training_readiness_contract_report.py`

### Implementation for User Story 2

- [X] T015 [P] [US2] Implement the paper-default configuration lock check in `src/analysis/training_readiness_contract/runner.py`
- [X] T016 [P] [US2] Implement the observation, action, and legality contract lock checks in `src/analysis/training_readiness_contract/runner.py`
- [X] T017 [P] [US2] Implement the reward, timeout, capacity, transmission, and queue contract lock checks in `src/analysis/training_readiness_contract/runner.py`
- [X] T018 [P] [US2] Implement the metric, seed, and artifact contract lock checks in `src/analysis/training_readiness_contract/runner.py`
- [X] T019 [US2] Emit the contract-lock bundle and family-specific blocker list in `src/analysis/training_readiness_contract/report.py`

**Checkpoint**: Training-contract lock behavior is independently testable.

---

## Phase 5: User Story 3 - Decide Whether the Next Smoke Run Is Allowed (Priority: P3)

**Goal**: Produce the final go/no-go decision for the next controlled paper-default training smoke run.

**Independent Test**: Generate the report and verify that the final verdict, training-allowed flag, and recommended next feature all match the lock status without referencing implementation internals.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [X] T020 [P] [US3] Add behavior-equivalence tests with unique check names in `tests/unit/test_training_readiness_contract_behavior_equivalence.py`
- [X] T021 [P] [US3] Add integration tests for training execution routing and verdict selection in `tests/integration/test_training_readiness_contract_scope_guard.py`

### Implementation for User Story 3

- [X] T022 [P] [US3] Implement training_execution_allowed_next and next-feature routing in `src/analysis/training_readiness_contract/runner.py`
- [X] T023 [P] [US3] Implement behavior-equivalence summary emission and duplicate-name protection in `src/analysis/training_readiness_contract/model.py`
- [X] T024 [US3] Emit `training_execution_allowed_next`, `remaining_blockers`, `recommended_next_feature`, and `final_verdict` in `src/analysis/training_readiness_contract/report.py`

**Checkpoint**: Readiness decision and behavior-equivalence audit are complete.

---

## Phase 6: Report Generation & Cross-Cutting Concerns

**Purpose**: Final artifact generation and hygiene validation

- [X] T025 [P] Generate the JSON report artifact in `artifacts/analysis/training-readiness-contract/training-readiness-contract-report.json`
- [X] T026 [P] Generate the Markdown report artifact in `artifacts/analysis/training-readiness-contract/training-readiness-contract-report.md`
- [X] T027 Add scope-guard tests for no training, no optimizer, no replay, no target update, no checkpoint, no campaign, and no drift in `tests/integration/test_training_readiness_contract_scope_guard.py`
- [X] T028 Add commit-hygiene tests that reject staging or committing `.specify/feature.json` and forbid dirty-worktree-sensitive prior-feature validation in `tests/integration/test_training_readiness_contract_scope_guard.py`
- [X] T029 [P] Validate the Feature 054 quickstart workflow against `specs/054-training-readiness-contract/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Report Generation & Cross-Cutting Concerns (Phase 6)**: Depends on the user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on the Feature 053 gate from US1 for its prerequisite check, but is otherwise independently testable
- **User Story 3 (P3)**: Can start after User Stories 1 and 2 - Depends on the evidence-chain gate, contract locks, and behavior-equivalence evidence produced in the earlier stories

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Shared model/helpers before runner/report wiring
- Runner evaluation before report summary emission
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, US1 and the non-dependent parts of US2 can proceed in parallel
- All tests for a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members once prerequisites are satisfied

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together:
Task: "Add metrics tests for all contract lock fields and their failure routing in tests/unit/test_training_readiness_contract_metrics.py"
Task: "Add integration tests for contract-family blocker classification in tests/integration/test_training_readiness_contract_report.py"

# Launch all contract-lock evaluations together:
Task: "Implement the paper-default configuration lock check in src/analysis/training_readiness_contract/runner.py"
Task: "Implement the observation, action, and legality contract lock checks in src/analysis/training_readiness_contract/runner.py"
Task: "Implement the reward, timeout, capacity, transmission, and queue contract lock checks in src/analysis/training_readiness_contract/runner.py"
Task: "Implement the metric, seed, and artifact contract lock checks in src/analysis/training_readiness_contract/runner.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Generate final reports and validate scope/hygiene

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Cross-cutting report generation and hygiene checks complete after the stories are integrated

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
