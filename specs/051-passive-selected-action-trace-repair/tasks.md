# Tasks: Passive Selected-Action Trace Repair

**Input**: Design documents from `/specs/051-passive-selected-action-trace-repair/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are required for this feature. They are listed per user story and must validate passive trace repair, committed prior-artifact gates, and behavior equivalence without dirty-worktree-sensitive prior-feature report builders.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the Feature 051 workspace and audit inputs before implementation.

### Quality Gate

- [x] T001 Confirm committed prior-artifact gates for Features 044, 048, 049, and 050 in `tests/integration/test_passive_selected_action_trace_repair.py`
- [x] T002 Confirm validation scope excludes dirty-worktree-sensitive prior-feature report builders in `specs/051-passive-selected-action-trace-repair/quickstart.md`
- [x] T003 Define report schema contract for Feature 051 in `specs/051-passive-selected-action-trace-repair/contracts/passive-selected-action-trace-repair-report-schema.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core passive trace schema and report plumbing that all user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T004 [P] Implement Feature 051 config and report model in `src/analysis/passive_selected_action_trace_repair/config.py` and `src/analysis/passive_selected_action_trace_repair/model.py`
- [x] T005 [P] Implement Feature 051 CLI entrypoint and report writer in `src/analysis/passive_selected_action_trace_repair/__main__.py`, `src/analysis/passive_selected_action_trace_repair/runner.py`, and `src/analysis/passive_selected_action_trace_repair/report.py`
- [x] T006 [P] Extend passive trace schema with selected-action fields in `src/environment/lifecycle_trace.py`
- [x] T007 [P] Extend passive selected-action emission in `src/environment/gym_adapter.py`
- [x] T008 [P] Add Feature 051 report artifact directory scaffolding under `artifacts/analysis/passive-selected-action-trace-repair/`

**Checkpoint**: Passive trace schema and emission scaffolding are ready; user story implementation can now proceed.

---

## Phase 3: User Story 1 - Emit Selected-Action Trace Evidence (Priority: P1)

**Goal**: Expose selected action, action index, selected action family, trace source, and deterministic decision identifiers from passive trace evidence.

**Independent Test**: The Feature 051 schema and emission tests can confirm the passive trace contains the required selected-action fields without changing runtime behavior.

### Tests for User Story 1

- [x] T009 [P] [US1] Add schema coverage for selected-action trace fields in `tests/unit/test_passive_selected_action_trace_schema.py`
- [x] T010 [P] [US1] Add emission coverage for actual selected action metadata in `tests/unit/test_passive_selected_action_trace_metrics.py`

### Implementation for User Story 1

- [x] T011 [P] [US1] Implement selected-action trace schema extension in `src/environment/lifecycle_trace.py` for `selected_action`, `action_index`, `selected_action_family`, `selected_action_trace_source`, `decision_event_id`, `selected_action_to_task_join_key`, and `terminal_outcome_join_key`
- [x] T012 [US1] Implement passive selected-action emission at the decision point in `src/environment/gym_adapter.py` for `strategy`, `seed`, `slot`, `agent_id`, `task_id`, `selected_action`, `action_index`, `selected_action_family`, and `decision_event_id`
- [x] T013 [US1] Implement selected-action family mapping logic in `src/analysis/passive_selected_action_trace_repair/model.py` so `local`, `horizontal`, `vertical`, and `unknown` are derived from the actual selected action only
- [x] T014 [US1] Wire the selected-action trace summary into `src/analysis/passive_selected_action_trace_repair/runner.py` and `src/analysis/passive_selected_action_trace_repair/report.py`

**Checkpoint**: Selected-action trace evidence is emitted passively and can be inspected independently.

---

## Phase 4: User Story 2 - Preserve Join Keys for Task and Terminal Outcome Evidence (Priority: P2)

**Goal**: Preserve deterministic join keys so selected actions can be linked to task identity and terminal outcomes.

**Independent Test**: The join-key tests verify that selected actions, task identity, and terminal outcomes are connected by deterministic keys rather than heuristics or placeholders.

### Tests for User Story 2

- [x] T015 [P] [US2] Add deterministic decision-event and join-key assertions in `tests/unit/test_passive_selected_action_trace_metrics.py`
- [x] T016 [P] [US2] Add selected-action-to-task join readiness coverage in `tests/integration/test_passive_selected_action_trace_repair.py`

### Implementation for User Story 2

- [x] T017 [US2] Implement selected-action-to-task join summary in `src/analysis/passive_selected_action_trace_repair/model.py`
- [x] T018 [US2] Implement terminal outcome join key summary in `src/analysis/passive_selected_action_trace_repair/model.py`
- [x] T019 [US2] Implement selected-action join reporting in `src/analysis/passive_selected_action_trace_repair/report.py` for `selected_action_to_task_join_status`, `terminal_outcome_join_status`, and `per_action_outcome_join_readiness`

**Checkpoint**: Selected actions can be traced into task identity and terminal outcome join readiness without altering runtime semantics.

---

## Phase 5: User Story 3 - Assess Feature 050 Rerun Readiness (Priority: P3)

**Goal**: Publish readiness and blocker summaries that say whether Feature 050 can be rerun safely using the repaired passive trace.

**Independent Test**: The readiness tests confirm the report blocks rerun readiness when any required join evidence is missing and passes only when all trace evidence exists.

### Tests for User Story 3

- [x] T020 [P] [US3] Add readiness-blocking coverage for missing join fields in `tests/integration/test_passive_selected_action_trace_scope_guard.py`
- [x] T021 [P] [US3] Add readiness-pass coverage when all trace evidence exists in `tests/integration/test_passive_selected_action_trace_report.py`
- [x] T022 [P] [US3] Add behavior-equivalence uniqueness and drift coverage in `tests/unit/test_passive_selected_action_trace_behavior_equivalence.py`

### Implementation for User Story 3

- [x] T023 [US3] Implement `selected_action_family_evidence_status`, `selected_action_to_task_join_status`, `terminal_outcome_join_status`, `per_action_outcome_join_readiness`, `behavior_equivalence_passed`, `evidence_readiness_for_feature_050_rerun`, and `remaining_blockers` in `src/analysis/passive_selected_action_trace_repair/model.py`
- [x] T024 [US3] Implement behavior-equivalence summary and unique check naming in `src/analysis/passive_selected_action_trace_repair/model.py`
- [x] T025 [US3] Implement top-level report fields and final verdict routing in `src/analysis/passive_selected_action_trace_repair/report.py`

**Checkpoint**: The report can now state whether Feature 050 is unblocked or still blocked by missing trace evidence.

---

## Phase 6: Report Artifacts

**Purpose**: Generate the passive trace repair artifacts required by the feature.

- [x] T026 [P] Generate `artifacts/analysis/passive-selected-action-trace-repair/passive-selected-action-trace-repair-report.json` from `src/analysis/passive_selected_action_trace_repair`
- [x] T027 [P] Generate `artifacts/analysis/passive-selected-action-trace-repair/passive-selected-action-trace-repair-report.md` from `src/analysis/passive_selected_action_trace_repair`

**Checkpoint**: The JSON and Markdown report artifacts exist and match the report contract.

---

## Phase 7: Final Commit Hygiene

**Purpose**: Classify dirty paths and stage only approved Feature 051 paths before any commit.

- [x] T028 Classify dirty paths before staging in the working tree and exclude `.specify/feature.json`, `AGENTS.md`, `.gitignore`, dependency files, `src/policies/`, Feature 037–050 artifacts, checkpoints, training artifacts, and campaign outputs
- [x] T029 Stage only approved Feature 051 paths for `specs/051-passive-selected-action-trace-repair/`, `src/analysis/passive_selected_action_trace_repair/`, `src/environment/lifecycle_trace.py`, `src/environment/gym_adapter.py`, `tests/unit/test_passive_selected_action_trace_schema.py`, `tests/unit/test_passive_selected_action_trace_metrics.py`, `tests/unit/test_passive_selected_action_trace_behavior_equivalence.py`, `tests/integration/test_passive_selected_action_trace_repair.py`, `tests/integration/test_passive_selected_action_trace_report.py`, `tests/integration/test_passive_selected_action_trace_scope_guard.py`, and `artifacts/analysis/passive-selected-action-trace-repair/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately.
- **Phase 2 (Foundational)**: Depends on Setup completion - blocks all user stories.
- **User Stories (Phases 3-5)**: Depend on Foundational completion.
- **Phase 6 (Report Artifacts)**: Depends on User Story 3 completion.
- **Phase 7 (Commit Hygiene)**: Depends on all desired implementation and validation tasks being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational; no dependency on other stories.
- **User Story 2 (P2)**: Starts after Foundational; can use User Story 1 outputs but remains independently testable.
- **User Story 3 (P3)**: Starts after Foundational; depends on User Story 1 and 2 outputs for readiness checks but remains independently verifiable.

### Within Each User Story

- Tests MUST be written and fail before implementation.
- Schema and emission tasks come before readiness and report routing.
- Story complete before moving to the next priority.

### Parallel Opportunities

- Setup tasks T001-T003 can run in parallel where they touch different files.
- Foundational tasks T004-T008 can run in parallel where files do not overlap.
- User Story 1 test and implementation tasks are parallelizable across separate files.
- User Story 2 tests can run in parallel with User Story 1 implementation once foundational work is complete.
- User Story 3 tests can run in parallel with report artifact generation after implementation is complete.

---

## Parallel Example: User Story 1

```bash
# Run schema and emission tests together:
Task: "Add schema coverage for selected-action trace fields in tests/unit/test_passive_selected_action_trace_schema.py"
Task: "Add emission coverage for actual selected action metadata in tests/unit/test_passive_selected_action_trace_metrics.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Stop and validate selected-action trace emission independently.

### Incremental Delivery

1. Complete Setup + Foundational.
2. Add User Story 1 and validate passive trace emission.
3. Add User Story 2 and validate deterministic join readiness.
4. Add User Story 3 and validate Feature 050 rerun readiness.
5. Generate report artifacts.
6. Perform commit hygiene classification and stage only approved Feature 051 paths.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together.
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Artifacts and commit hygiene are finalized after the implementation tasks are complete.

---

## Notes

- [P] tasks = different files, no dependencies.
- [Story] label maps task to specific user story for traceability.
- Each user story should be independently completable and testable.
- Verify tests fail before implementing.
