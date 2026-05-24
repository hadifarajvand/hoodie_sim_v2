# Tasks: Selected-Action Family and Per-Action Outcome Evidence Expansion

**Input**: Design documents from `/specs/050-selected-action-family-per-action-outcome-evidence/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Include tests because the feature specification explicitly requires schema, metrics, integration, behavior-equivalence, and scope-guard coverage.

**Organization**: Tasks are grouped by user story and by blocking prerequisites so the passive evidence expansion can be delivered incrementally and verified independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story the task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the passive-analysis package, scope guards, and artifact wiring used by every story

### Quality Gate

- [ ] T001 [P] Add Feature 050 prerequisite and scope-guard coverage in `tests/integration/test_selected_action_outcome_scope_guard.py` for branch == `050-selected-action-family-per-action-outcome-evidence`, branch != `main`, `main == origin/main`, `main == 049-exposure-matrix-paper-mechanism-alignment-complete^{}`, empty prerequisite diff, pointer hygiene, clean `AGENTS.md`, committed prior-artifact gates, and dirty-path rejection
- [ ] T002 [P] Scaffold the passive-analysis package in `src/analysis/selected_action_family_per_action_outcome_evidence/__init__.py`, `src/analysis/selected_action_family_per_action_outcome_evidence/__main__.py`, `src/analysis/selected_action_family_per_action_outcome_evidence/config.py`, `src/analysis/selected_action_family_per_action_outcome_evidence/model.py`, `src/analysis/selected_action_family_per_action_outcome_evidence/runner.py`, and `src/analysis/selected_action_family_per_action_outcome_evidence/report.py`
- [ ] T003 [P] Wire the Feature 050 report output paths and filenames in `src/analysis/selected_action_family_per_action_outcome_evidence/config.py` and `src/analysis/selected_action_family_per_action_outcome_evidence/report.py`

**Checkpoint**: Passive-analysis package scaffold exists and scope-guard coverage is in place before evidence logic is added

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish passive trace inputs, committed-artifact validation, and shared report structures that every user story depends on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 [P] Audit committed Feature 044, Feature 048, and Feature 049 artifact inputs and add only passive loading helpers in `src/analysis/selected_action_family_per_action_outcome_evidence/runner.py`
- [ ] T005 [P] Extend passive trace schema/emission only if required for selected-action family and terminal-outcome join keys in `src/environment/lifecycle_trace.py` and `src/environment/gym_adapter.py`
- [ ] T006 [P] Define the Feature 050 report dataclasses for selected-action family evidence, selected-action-to-task joins, per-action outcome joins, legal-but-unselected consistency, internal consistency, and Feature 049 unblock assessment in `src/analysis/selected_action_family_per_action_outcome_evidence/model.py`
- [ ] T007 [P] Add committed-artifact gate and pointer-hygiene checks to `tests/integration/test_selected_action_outcome_scope_guard.py` so prior feature validation uses committed artifacts only and never dirty-worktree-sensitive tests

**Checkpoint**: Foundation ready - story work can now begin in parallel

---

## Phase 3: User Story 1 - Capture Selected-Action Family Evidence (Priority: P1) 🎯 MVP

**Goal**: Capture selected local, horizontal, and vertical evidence for every decision opportunity without placeholder zeros or sample-derived counts

**Independent Test**: The selected-action family report fields can be generated from passive evidence alone, and unavailable evidence is reported explicitly instead of being faked as zero

### Tests for User Story 1

- [ ] T008 [P] [US1] Add schema tests for `selected_action_family_evidence_status`, selected-family count fields, and unavailable/null handling in `tests/unit/test_selected_action_outcome_evidence_schema.py`
- [ ] T009 [P] [US1] Add metrics tests for selected family count summation, `selected_action_count` consistency, and rejection of fake zero placeholders in `tests/unit/test_selected_action_outcome_evidence_metrics.py`

### Implementation for User Story 1

- [ ] T010 [US1] Implement selected-action family extraction and `per_strategy_seed_selected_action_family_matrix` generation in `src/analysis/selected_action_family_per_action_outcome_evidence/runner.py`
- [ ] T011 [US1] Populate selected family evidence status and summary rendering in `src/analysis/selected_action_family_per_action_outcome_evidence/report.py`
- [ ] T012 [US1] Implement `selected_action_count` and `selected_action_count_consistency_verified` calculation in `src/analysis/selected_action_family_per_action_outcome_evidence/runner.py`

**Checkpoint**: Selected-action family evidence is trace-backed, not placeholder-driven

---

## Phase 4: User Story 2 - Selected-Action-to-Task and Per-Action Outcome Joins (Priority: P2)

**Goal**: Join selected actions to task identifiers and terminal outcomes so completion, drop, and pending evidence can be computed without fake zeros

**Independent Test**: A selected action can be traced to its task and terminal outcome when join keys exist, and missing joins are reported as unavailable evidence

### Tests for User Story 2

- [ ] T013 [P] [US2] Add join and outcome metric tests for `selected_action_to_task_join_count`, `selected_action_to_task_join_ratio`, `missing_selected_action_task_join_count`, `selected_action_to_task_join_status`, and per-action outcome evidence in `tests/unit/test_selected_action_outcome_evidence_metrics.py`
- [ ] T014 [P] [US2] Add integration coverage for selected-action-to-task joins and terminal outcome joins using committed artifacts only in `tests/integration/test_selected_action_outcome_evidence.py`

### Implementation for User Story 2

- [ ] T015 [US2] Implement selected-action-to-task join logic using `strategy`, `seed`, `slot`, `agent_id`, `task_id`, and deterministic decision-event identifiers in `src/analysis/selected_action_family_per_action_outcome_evidence/runner.py`
- [ ] T016 [US2] Implement per-action completion, drop, and pending counts and rates, plus `per_action_outcome_evidence_status`, in `src/analysis/selected_action_family_per_action_outcome_evidence/runner.py`
- [ ] T017 [US2] Implement legal-but-unselected counts and `legal_but_unselected_consistency_verified` in `src/analysis/selected_action_family_per_action_outcome_evidence/runner.py`
- [ ] T018 [US2] Render selected-action-to-task join and per-action outcome summaries in `src/analysis/selected_action_family_per_action_outcome_evidence/report.py`

**Checkpoint**: Selected actions are joined to task and terminal outcome evidence when the join keys exist

---

## Phase 5: User Story 3 - Feature 049 Unblock Assessment and Behavior Equivalence (Priority: P3)

**Goal**: Provide a strict readiness decision for rerunning Feature 049 and prove passive evidence capture did not change runtime behavior

**Independent Test**: The report emits a correct unblock assessment, blocks Feature 049 when evidence is incomplete, and contains unique behavior-equivalence checks with no duplicate names

### Tests for User Story 3

- [ ] T019 [P] [US3] Add report contract tests for `feature_049_can_be_rerun`, `feature_049_remaining_blockers`, `recommended_next_feature`, and all required top-level report fields in `tests/integration/test_selected_action_outcome_report.py`
- [ ] T020 [P] [US3] Add behavior-equivalence tests with unique check names in `tests/unit/test_selected_action_outcome_behavior_equivalence.py`

### Implementation for User Story 3

- [ ] T021 [US3] Implement exposure-matrix internal consistency checks and `exposure_matrix_internal_consistency_verified` in `src/analysis/selected_action_family_per_action_outcome_evidence/runner.py`
- [ ] T022 [US3] Implement Feature 049 unblock assessment fields and readiness routing in `src/analysis/selected_action_family_per_action_outcome_evidence/runner.py`
- [ ] T023 [US3] Implement behavior-equivalence summary generation with unique check names in `src/analysis/selected_action_family_per_action_outcome_evidence/runner.py`
- [ ] T024 [US3] Ensure the final report writer emits JSON and Markdown artifacts for `artifacts/analysis/selected-action-family-per-action-outcome-evidence/` in `src/analysis/selected_action_family_per_action_outcome_evidence/report.py`

**Checkpoint**: Feature 049 can be rerun only when selected-action family evidence, task joins, outcome joins, and consistency all pass

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, artifact generation, and consistency checks across the passive evidence package

- [ ] T025 [P] Reconcile `spec.md`, `plan.md`, `research.md`, `data-model.md`, and `contracts/selected-action-family-outcome-evidence-report-schema.md` with the final implementation contract
- [ ] T026 [P] Generate the Feature 050 JSON and Markdown reports in `artifacts/analysis/selected-action-family-per-action-outcome-evidence/`
- [ ] T027 Run the approved Feature 050 validation command from `specs/050-selected-action-family-per-action-outcome-evidence/quickstart.md`
- [ ] T028 Verify the final report blocks Feature 049 rerun readiness unless `selected_action_family_evidence_status = available`, `per_action_outcome_evidence_status = available`, `selected_action_count_consistency_verified = true`, `legal_but_unselected_consistency_verified = true`, and `exposure_matrix_internal_consistency_verified = true`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Uses the selected family evidence from US1 but must remain independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses outputs from US1/US2 but remains independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Data-model or schema work before report rendering
- Passive trace emission changes before evidence extraction
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- T001-T003 can run in parallel because they touch different files
- T004-T007 can run in parallel after Setup because they target separate concerns
- T008-T009 can run in parallel as the User Story 1 tests
- T013-T014 can run in parallel as the User Story 2 tests
- T019-T020 can run in parallel as the User Story 3 tests
- T025-T026 can run in parallel during polish

---

## Parallel Example: User Story 1

```bash
# Launch the User Story 1 tests together:
Task: "Add schema tests for selected_action_family_evidence_status in tests/unit/test_selected_action_outcome_evidence_schema.py"
Task: "Add metrics tests for selected family summation and fake-zero rejection in tests/unit/test_selected_action_outcome_evidence_metrics.py"

# Launch the User Story 1 implementation tasks together:
Task: "Implement selected-action family extraction in src/analysis/selected_action_family_per_action_outcome_evidence/runner.py"
Task: "Populate selected family status rendering in src/analysis/selected_action_family_per_action_outcome_evidence/report.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. STOP and VALIDATE: Ensure selected-action family evidence is trace-backed and does not fake zeros
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → passive-analysis foundation ready
2. Add User Story 1 → selected-action family evidence is visible
3. Add User Story 2 → joins and outcome evidence become available
4. Add User Story 3 → Feature 049 unblock assessment is authoritative
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Keep all evidence passive and trace-backed
- Do not introduce fake zeros, sample-derived aggregates, training, optimizer, replay, target updates, or policy/runtime semantic changes
