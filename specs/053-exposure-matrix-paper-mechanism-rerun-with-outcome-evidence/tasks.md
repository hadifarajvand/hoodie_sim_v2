# Tasks: Exposure Matrix Paper Mechanism Rerun with Outcome Evidence

**Input**: Design documents from `/specs/053-exposure-matrix-paper-mechanism-rerun-with-outcome-evidence/`  
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are explicitly requested and included below. Each story includes its own tests so the feature can be validated incrementally.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and baseline analysis package structure

- [ ] T001 [P] Create the Feature 053 analysis package scaffold in `src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/{__init__.py,__main__.py,config.py,model.py,runner.py,report.py}`
- [ ] T002 [P] Define Feature 053 artifact paths and committed-input file map in `src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/config.py`
- [ ] T003 [P] Create report status enums, verdict vocabulary, and shared model containers in `src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/model.py`

**Checkpoint**: Feature 053 package exists and the report vocabulary is defined.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core shared logic that MUST be complete before any user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 [P] Implement committed prior-artifact loaders for Features 048, 049, 050, 051, and 052 in `src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/runner.py`
- [ ] T005 [P] Implement shared alignment-status validation helpers for `available`, `partial`, and `unavailable` in `src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/model.py`
- [ ] T006 [P] Implement report serialization and Markdown rendering scaffolding in `src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/report.py`

**Checkpoint**: Foundation ready - all user stories can now be implemented in parallel.

---

## Phase 3: User Story 1 - Verify Feature 052 Unblock Gate (Priority: P1) 🎯 MVP

**Goal**: Confirm that Feature 052 is truly rerun-ready using committed prior artifacts only, so the paper-mechanism rerun is not built on a stale or invalid gate.

**Independent Test**: The rerun report must fail closed when Feature 052 is not ready and must pass the prerequisite gate only when the committed Feature 052 report proves rerun readiness.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T007 [P] [US1] Add schema tests for Feature 052 readiness gate and prerequisite report fields in `tests/unit/test_exposure_matrix_paper_mechanism_rerun_schema.py`
- [ ] T008 [P] [US1] Add integration tests for committed prior-artifact gates in `tests/integration/test_exposure_matrix_paper_mechanism_rerun.py`

### Implementation for User Story 1

- [ ] T009 [US1] Implement Feature 052 readiness gate evaluation from committed report artifacts in `src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/runner.py`
- [ ] T010 [US1] Emit the Feature 052 prerequisite verification summary and prior-feature gate status in `src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/report.py`

**Checkpoint**: Feature 052 gate behavior is verified independently.

---

## Phase 4: User Story 2 - Rerun Paper-Mechanism Alignment (Priority: P2)

**Goal**: Recompute observation-vector, formula/unit, exposure-matrix, and selected-action-outcome alignment so the report can identify the exact layer that blocks readiness.

**Independent Test**: The rerun report must classify each alignment layer independently and produce the correct blocker list when any layer is partial or unavailable.

### Tests for User Story 2

- [ ] T011 [P] [US2] Add metrics tests for observation-vector, formula/unit, exposure-matrix, and selected-action-outcome alignment statuses in `tests/unit/test_exposure_matrix_paper_mechanism_rerun_metrics.py`
- [ ] T012 [P] [US2] Add integration tests for blocker classification and verdict routing in `tests/integration/test_exposure_matrix_paper_mechanism_rerun_report.py`

### Implementation for User Story 2

- [ ] T013 [P] [US2] Implement observation-vector alignment assessment in `src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/runner.py`
- [ ] T014 [P] [US2] Implement formula/unit alignment assessment in `src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/runner.py`
- [ ] T015 [P] [US2] Implement selected-action outcome alignment assessment in `src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/runner.py`
- [ ] T016 [P] [US2] Implement exposure-matrix alignment assessment in `src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/runner.py`
- [ ] T017 [US2] Emit `remaining_blockers` and `recommended_next_feature` from alignment results in `src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/report.py`

**Checkpoint**: Alignment rerun is independently testable and produces a specific blocker when it fails.

---

## Phase 5: User Story 3 - Assess Training-Readiness Contract and Behavior Equivalence (Priority: P3)

**Goal**: Determine whether the evidence chain is strong enough to move into the next training-readiness phase without introducing behavior drift or false readiness.

**Independent Test**: The report must only mark readiness when every alignment gate passes, and it must preserve behavior-equivalence evidence with unique check names.

### Tests for User Story 3

- [ ] T018 [P] [US3] Add behavior-equivalence unit tests with unique check names in `tests/unit/test_exposure_matrix_paper_mechanism_rerun_behavior_equivalence.py`
- [ ] T019 [P] [US3] Add scope-guard integration tests for no training, no drift, and no prior artifact rewrites in `tests/integration/test_exposure_matrix_paper_mechanism_rerun_scope_guard.py`

### Implementation for User Story 3

- [ ] T020 [P] [US3] Implement training-readiness contract assessment and final verdict routing in `src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/runner.py`
- [ ] T021 [P] [US3] Implement behavior-equivalence summary fields and unique check-name enforcement in `src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/model.py`
- [ ] T022 [US3] Emit `paper_mechanism_alignment_ready`, `training_readiness_contract_status`, and `final_verdict` in `src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/report.py`

**Checkpoint**: Readiness decision and behavior-equivalence audit are complete.

---

## Phase 6: Report Generation & Cross-Cutting Concerns

**Purpose**: Final artifact generation and hygiene validation

- [ ] T023 [P] Generate the JSON report artifact in `artifacts/analysis/exposure-matrix-paper-mechanism-rerun-with-outcome-evidence/exposure-matrix-paper-mechanism-rerun-report.json`
- [ ] T024 [P] Generate the Markdown report artifact in `artifacts/analysis/exposure-matrix-paper-mechanism-rerun-with-outcome-evidence/exposure-matrix-paper-mechanism-rerun-report.md`
- [ ] T025 [P] Add dirty-path classification and commit-scope hygiene assertions to `tests/integration/test_exposure_matrix_paper_mechanism_rerun_scope_guard.py`
- [ ] T026 [P] Validate the Feature 053 quickstart workflow against `specs/053-exposure-matrix-paper-mechanism-rerun-with-outcome-evidence/quickstart.md`

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
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on the Feature 052 gate from US1 for its prerequisite check, but is otherwise independently testable
- **User Story 3 (P3)**: Can start after User Stories 1 and 2 - Depends on the alignment results and behavior-equivalence evidence produced in the earlier stories

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
Task: "Add metrics tests for observation-vector, formula/unit, exposure-matrix, and selected-action-outcome alignment statuses in tests/unit/test_exposure_matrix_paper_mechanism_rerun_metrics.py"
Task: "Add integration tests for blocker classification and verdict routing in tests/integration/test_exposure_matrix_paper_mechanism_rerun_report.py"

# Launch all alignment assessments together:
Task: "Implement observation-vector alignment assessment in src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/runner.py"
Task: "Implement formula/unit alignment assessment in src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/runner.py"
Task: "Implement selected-action outcome alignment assessment in src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/runner.py"
Task: "Implement exposure-matrix alignment assessment in src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/runner.py"
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
