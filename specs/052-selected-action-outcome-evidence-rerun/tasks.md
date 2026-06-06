# Tasks: Selected-Action Outcome Evidence Rerun

**Input**: Design documents from `/specs/052-selected-action-outcome-evidence-rerun/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are required for this feature. They must validate committed prior-artifact gates, Feature 051 readiness gating, rerun evidence recomputation, exposure consistency, and behavior equivalence without dirty-worktree-sensitive prior-feature report builders.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the Feature 052 workspace and audit inputs before implementation.

### Quality Gate

- [X] T001 Confirm committed prior-artifact gates for Features 048, 049, 050, and 051 in `tests/integration/test_selected_action_outcome_rerun.py`
- [X] T002 Confirm validation scope excludes dirty-worktree-sensitive prior-feature report builders in `specs/052-selected-action-outcome-evidence-rerun/quickstart.md`
- [X] T003 Define report schema contract for Feature 052 in `specs/052-selected-action-outcome-evidence-rerun/contracts/selected-action-outcome-evidence-rerun-report-schema.md`, including top-level `per_action_outcome_evidence_status` plus nested `per_action_outcome_join_summary.per_action_outcome_evidence_status` and `feature_049_unblock_assessment.per_action_outcome_evidence_status`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core rerun report plumbing and committed-artifact gating that all user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 [P] Implement Feature 052 config and report model in `src/analysis/selected_action_outcome_evidence_rerun/config.py` and `src/analysis/selected_action_outcome_evidence_rerun/model.py`
- [X] T005 [P] Implement Feature 052 CLI entrypoint and report writer in `src/analysis/selected_action_outcome_evidence_rerun/__main__.py`, `src/analysis/selected_action_outcome_evidence_rerun/runner.py`, and `src/analysis/selected_action_outcome_evidence_rerun/report.py`
- [X] T006 [P] Add Feature 052 report artifact directory scaffolding under `artifacts/analysis/selected-action-outcome-evidence-rerun/`
- [X] T007 [P] Implement committed Feature 051 readiness gate loading in `src/analysis/selected_action_outcome_evidence_rerun/runner.py`
- [X] T008 [P] Implement committed Feature 048/049/050/051 prior-artifact loading in `src/analysis/selected_action_outcome_evidence_rerun/runner.py`

**Checkpoint**: Feature 051 readiness gate and prior-artifact inputs are ready; user story implementation can now proceed.

---

## Phase 3: User Story 1 - Recompute Selected-Action Evidence From Populated Traces (Priority: P1)

**Goal**: Recompute selected-action family and selected-action-to-task evidence from the populated Feature 051 trace evidence.

**Independent Test**: The Feature 052 evidence tests can confirm the rerun report consumes Feature 051 readiness and recomputes the selected-action evidence without using dirty-worktree-sensitive prior-feature report builders.

### Tests for User Story 1

- [X] T009 [P] [US1] Add Feature 051 readiness gate assertions in `tests/integration/test_selected_action_outcome_rerun_scope_guard.py`
- [X] T010 [P] [US1] Add selected-action family evidence recomputation coverage in `tests/unit/test_selected_action_outcome_rerun_metrics.py`
- [X] T011 [P] [US1] Add selected-action-to-task join recomputation coverage in `tests/unit/test_selected_action_outcome_rerun_metrics.py`

### Implementation for User Story 1

- [X] T012 [US1] Implement `feature_051_trace_readiness_verified` and selected-action family evidence summary in `src/analysis/selected_action_outcome_evidence_rerun/model.py`
- [X] T013 [US1] Implement selected-action family count recomputation in `src/analysis/selected_action_outcome_evidence_rerun/runner.py` for `selected_local_count`, `selected_horizontal_count`, `selected_vertical_count`, `selected_action_count`, `selected_action_count_consistency_verified`, and `per_strategy_seed_selected_action_family_matrix`
- [X] T014 [US1] Implement selected-action-to-task join rerun summary in `src/analysis/selected_action_outcome_evidence_rerun/model.py` for `selected_action_to_task_join_count`, `selected_action_to_task_join_ratio`, `missing_selected_action_task_join_count`, and `selected_action_to_task_join_status`
- [X] T015 [US1] Implement selected-action family and join reporting in `src/analysis/selected_action_outcome_evidence_rerun/report.py`

**Checkpoint**: Selected-action family and join evidence are recomputed from the populated Feature 051 trace evidence.

---

## Phase 4: User Story 2 - Reassess Per-Action Outcome Evidence and Exposure Consistency (Priority: P2)

**Goal**: Recompute per-action terminal outcome evidence and legal-but-unselected consistency so Feature 049 rerun readiness can be assessed.

**Independent Test**: The per-action evidence tests verify that completion, drop, and pending outcomes are recomputed, rates use the selected-action-family denominator, and internal consistency is enforced.

### Tests for User Story 2

- [X] T016 [P] [US2] Add per-action outcome join coverage in `tests/unit/test_selected_action_outcome_rerun_metrics.py`
- [X] T017 [P] [US2] Add explicit denominator and null/zero-denominator coverage for per-action rates in `tests/unit/test_selected_action_outcome_rerun_metrics.py`
- [X] T018 [P] [US2] Add legal-but-unselected consistency coverage in `tests/unit/test_selected_action_outcome_rerun_metrics.py`
- [X] T019 [P] [US2] Add internal consistency, count conservation, and no-fake-zero coverage in `tests/integration/test_selected_action_outcome_rerun_report.py`

### Implementation for User Story 2

- [X] T020 [US2] Implement per-action outcome join summary in `src/analysis/selected_action_outcome_evidence_rerun/model.py` for `per_action_completion_count`, `per_action_drop_count`, `per_action_pending_count`, `per_action_completion_rate`, `per_action_drop_rate`, `per_action_pending_rate`, and `per_action_outcome_evidence_status`
- [X] T021 [US2] Implement per-action rate denominator rules in `src/analysis/selected_action_outcome_evidence_rerun/model.py` so each family rate uses its selected-action-family denominator, null/zero denominators are not faked, and count conservation is enforced when evidence is available
- [X] T022 [US2] Implement legal-but-unselected consistency summary in `src/analysis/selected_action_outcome_evidence_rerun/model.py` for `legal_but_unselected_local_count`, `legal_but_unselected_horizontal_count`, `legal_but_unselected_vertical_count`, and `legal_but_unselected_consistency_verified`
- [X] T023 [US2] Implement exposure matrix internal consistency checks in `src/analysis/selected_action_outcome_evidence_rerun/model.py` for `selected_action_count = selected_local_count + selected_horizontal_count + selected_vertical_count`, `selected_illegal_action_count <= selected_action_count`, per-action outcome bounds, non-negative legal-but-unselected counts, and no sample-derived aggregate counts
- [X] T024 [US2] Implement per-action outcome and exposure consistency reporting in `src/analysis/selected_action_outcome_evidence_rerun/report.py`

**Checkpoint**: Per-action outcome evidence and exposure consistency are recomputed and auditable.

---

## Phase 5: User Story 3 - Assess Feature 049 Rerun Readiness (Priority: P3)

**Goal**: Publish the unblock assessment that says whether Feature 049 can be rerun safely using the recomputed evidence.

**Independent Test**: The readiness tests confirm that Feature 049 rerun readiness is blocked when any required evidence or consistency gate fails and passes only when all evidence checks succeed.

### Tests for User Story 3

- [X] T025 [P] [US3] Add behavior-equivalence coverage in `tests/unit/test_selected_action_outcome_rerun_behavior_equivalence.py`
- [X] T026 [P] [US3] Add final readiness and unblock-assessment coverage in `tests/integration/test_selected_action_outcome_rerun_report.py`
- [X] T027 [P] [US3] Add feature 049 rerun gating coverage in `tests/integration/test_selected_action_outcome_rerun_scope_guard.py`

### Implementation for User Story 3

- [X] T028 [US3] Implement `feature_049_can_be_rerun`, `feature_049_remaining_blockers`, and `feature_049_unblock_assessment` in `src/analysis/selected_action_outcome_evidence_rerun/model.py`, including top-level `per_action_outcome_evidence_status` consistency
- [X] T029 [US3] Implement behavior-equivalence summary and unique check naming in `src/analysis/selected_action_outcome_evidence_rerun/model.py`
- [X] T030 [US3] Implement top-level report fields and final verdict routing in `src/analysis/selected_action_outcome_evidence_rerun/report.py`

**Checkpoint**: The report can now state whether Feature 049 is unblocked or still blocked by missing or inconsistent rerun evidence.

---

## Phase 6: Report Artifacts

**Purpose**: Generate the rerun artifacts required by the feature.

- [X] T031 [P] Generate `artifacts/analysis/selected-action-outcome-evidence-rerun/selected-action-outcome-evidence-rerun-report.json` from `src/analysis/selected_action_outcome_evidence_rerun`
- [X] T032 [P] Generate `artifacts/analysis/selected-action-outcome-evidence-rerun/selected-action-outcome-evidence-rerun-report.md` from `src/analysis/selected_action_outcome_evidence_rerun`

**Checkpoint**: The JSON and Markdown report artifacts exist and match the report contract.

---

## Phase 7: Final Commit Hygiene

**Purpose**: Classify dirty paths and stage only approved Feature 052 paths before any commit.

- [X] T033 Classify dirty paths before staging in the working tree and exclude `.specify/feature.json`, `AGENTS.md`, `.gitignore`, dependency files, `src/policies/`, Feature 037–051 artifacts, checkpoints, training artifacts, and campaign outputs
- [X] T034 Stage only approved Feature 052 paths for `specs/052-selected-action-outcome-evidence-rerun/`, `src/analysis/selected_action_outcome_evidence_rerun/`, `tests/unit/test_selected_action_outcome_rerun_schema.py`, `tests/unit/test_selected_action_outcome_rerun_metrics.py`, `tests/unit/test_selected_action_outcome_rerun_behavior_equivalence.py`, `tests/integration/test_selected_action_outcome_rerun.py`, `tests/integration/test_selected_action_outcome_rerun_report.py`, `tests/integration/test_selected_action_outcome_rerun_scope_guard.py`, and `artifacts/analysis/selected-action-outcome-evidence-rerun/`

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
- **User Story 3 (P3)**: Starts after Foundational; depends on User Stories 1 and 2 outputs for readiness checks but remains independently verifiable.

### Within Each User Story

- Tests MUST be written and fail before implementation.
- Summary and recomputation tasks come before readiness and report routing.
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
# Run selected-action family and join tests together:
Task: "Add selected-action family evidence recomputation coverage in tests/unit/test_selected_action_outcome_rerun_metrics.py"
Task: "Add selected-action-to-task join recomputation coverage in tests/unit/test_selected_action_outcome_rerun_metrics.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Stop and validate selected-action family and join evidence independently.

### Incremental Delivery

1. Complete Setup + Foundational.
2. Add User Story 1 and validate selected-action evidence rerun.
3. Add User Story 2 and validate per-action outcome and consistency checks.
4. Add User Story 3 and validate Feature 049 rerun readiness.
5. Generate report artifacts.
6. Perform commit hygiene classification and stage only approved Feature 052 paths.

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
