---

description: "Task list for Feature 036 - Deadline/Timeout Off-by-One Audit"
---

# Tasks: Deadline/Timeout Off-by-One Audit

**Input**: Design documents from `/specs/036-deadline-timeout-off-by-one-audit/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`

**Tests**: Required by the feature spec and quickstart. Include targeted runtime, regression, and report validation tests.

**Organization**: Tasks are grouped by user story so the boundary contract, helper agreement, and report can be implemented and verified independently.

## Format: `[ID] [P?] [US?] Description with exact file path`

- **[P]**: Can run in parallel with other marked tasks because it touches different files and has no dependency on incomplete work
- **[US?]**: Required for user story phases only
- Every task description must name the file path it changes or verifies

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Lock down the audit scope and capture the current boundary behavior before any repair work.

- [X] T001 Verify branch hygiene and clean-worktree preconditions in shell: current branch is not `main`, branch base matches current `main`, `035-public-cloud-queue-capacity-sharing-contract-complete` equals `main`, and no unrelated uncommitted files are present
- [X] T002 Record the current timeout source values and boundary behavior by inspecting `src/environment/traffic_config.py` and `src/environment/deadline_rules.py` for `timeout_slots = 20`, `slot_duration_seconds = 0.1`, `timeout_seconds = 2.0`, and the current exact-boundary expiration rule

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define the exact timeout contract and the runtime helpers that must agree before any repair is applied.

- [X] T003 Define the audited timeout contract and exact-boundary semantics in `specs/036-deadline-timeout-off-by-one-audit/data-model.md`
- [X] T004 Define the audit/report schema and no-drift flags in `src/analysis/deadline_timeout_off-by-one_audit/report.py`
- [X] T005 Update the feature quickstart validation flow in `specs/036-deadline-timeout-off-by-one-audit/quickstart.md` to name the approved interpreter, targeted tests, and report artifacts
- [X] T006 Update `AGENTS.md` for Feature 036 so it references `specs/036-deadline-timeout-off-by-one-audit/plan.md` and `specs/036-deadline-timeout-off-by-one-audit/spec.md`, states timeout/deadline boundary semantics only, states no execution-time / transmission-delay / capacity-sharing / policy / training changes, states no paper-recovery claim, and keeps the guidance minimal and feature-scoped

**Checkpoint**: Foundation ready - user story implementation can now begin.

## Phase 3: User Story 1 - Exact Boundary Contract (Priority: P1) 🎯 MVP

**Goal**: Prove and enforce that exact-boundary completion is on time and completion after the deadline is late.

**Independent Test**: Tasks completing at slots 19, 20, and 21 with `arrival_slot = 0` are classified as completed, completed, and dropped respectively, and the same rule works for a nonzero arrival slot.

### Tests for User Story 1

- [X] T007 [P] [US1] Add boundary unit coverage for `deadline_rules.has_expired` in `tests/unit/test_timeout_boundary_contract.py`
- [X] T008 [P] [US1] Add boundary unit coverage for `runtime_model.resolve_runtime_terminal_state` in `tests/unit/test_timeout_boundary_contract.py`
- [X] T009 [P] [US1] Add boundary unit coverage for `environment.finalize_task_runtime_state_with_parameters` in `tests/unit/test_timeout_boundary_contract.py`

### Implementation for User Story 1

- [X] T010 [US1] Audit and, if needed, minimally repair the exact-boundary expiration rule in `src/environment/deadline_rules.py`
- [X] T011 [US1] Audit and, if needed, minimally repair terminal-state resolution for exact-boundary completion in `src/environment/runtime_model.py`
- [X] T012 [US1] Audit and, if needed, minimally repair environment finalization so exact-boundary completion is not dropped in `src/environment/environment.py`
- [X] T013 [US1] Confirm `HoodieGymEnvironment` finalization path uses the inclusive boundary contract in `src/environment/gym_adapter.py`

**Checkpoint**: Exact-boundary completion should be classified consistently across runtime helpers.

## Phase 4: User Story 2 - Runtime Helper Agreement (Priority: P2)

**Goal**: Ensure all timeout helpers agree on the same inclusive boundary rule and that the paper-approved timeout values are surfaced consistently.

**Independent Test**: The helper chain agrees on exact-boundary completion for zero and nonzero arrival slots, and `TrafficScenarioPreset.paper_default` yields the audited timeout values.

### Tests for User Story 2

- [X] T014 [P] [US2] Add config coverage proving `TrafficScenarioPreset.paper_default` and `TrafficConfig.timeout_seconds()` produce the audited values in `tests/unit/test_timeout_boundary_contract.py`
- [X] T015 [P] [US2] Add nonzero-arrival boundary coverage in `tests/unit/test_timeout_boundary_contract.py`
- [X] T016 [P] [US2] Add helper-agreement coverage proving the audited helpers classify exact-boundary completion the same way in `tests/unit/test_timeout_boundary_contract.py`

### Implementation for User Story 2

- [X] T017 [US2] Verify `TrafficScenarioPreset.paper_default` and timeout derivation stay aligned with the audited contract in `src/environment/traffic_config.py`
- [X] T018 [US2] Verify `HoodieGymEnvironment` boundary handling remains consistent for nonzero arrival slots in `src/environment/gym_adapter.py`
- [X] T019 [US2] Confirm the runtime helper agreement is reflected in `src/environment/deadline_rules.py`, `src/environment/runtime_model.py`, and `src/environment/environment.py`

**Checkpoint**: Timeout source values and helper agreement should be auditable and consistent.

## Phase 5: User Story 3 - Regression Safety and Reporting (Priority: P3)

**Goal**: Lock in regression coverage for reward timing, drop penalties, drift guards, and the boundary audit report.

**Independent Test**: The exact-deadline and after-deadline runtime scenarios produce the expected terminal outcomes and report artifacts without altering Features 033-035 behavior.

### Tests for User Story 3

- [X] T020 [P] [US3] Add integration coverage for exact-deadline completion and after-deadline drop in `tests/integration/test_deadline_timeout_off_by_one_audit.py`
- [X] T021 [P] [US3] Add integration coverage for reward emission only after terminal outcome and drop-penalty application only for dropped tasks in `tests/integration/test_deadline_timeout_off_by_one_audit.py`
- [X] T022 [P] [US3] Add report validation coverage in `tests/integration/test_deadline_timeout_off_by_one_report.py`
- [X] T023 [P] [US3] Add scope-guard coverage for no training, policy, dependency, or campaign drift in `tests/integration/test_deadline_timeout_off_by_one_scope_guard.py`
- [X] T024 [P] [US3] Add drift coverage proving Feature 033 execution contract remains unchanged in `tests/integration/test_execution_time_flow.py`
- [X] T025 [P] [US3] Add drift coverage proving Feature 034 transmission-delay contract remains unchanged in `tests/integration/test_transmission_delay_runtime_wiring.py`
- [X] T026 [P] [US3] Add drift coverage proving Feature 035 capacity-sharing contract remains unchanged in `tests/integration/test_public_cloud_capacity_sharing_flow.py`

### Implementation for User Story 3

- [X] T027 [US3] Add the audit report package in `src/analysis/deadline_timeout_off_by_one_audit/__init__.py`
- [X] T028 [US3] Implement the deadline boundary audit report builder in `src/analysis/deadline_timeout_off_by_one_audit/report.py`
- [X] T029 [US3] Generate the JSON report at `artifacts/analysis/deadline-timeout-off-by-one-audit/deadline-timeout-off-by-one-report.json`
- [X] T030 [US3] Generate the Markdown report at `artifacts/analysis/deadline-timeout-off-by-one-audit/deadline-timeout-off-by-one-report.md`

**Checkpoint**: Regression safety and report generation should now be covered.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup across all stories.

- [X] T031 Validate the full targeted test suite with the approved interpreter in `specs/036-deadline-timeout-off-by-one-audit/quickstart.md`
- [X] T032 Verify the report schema fields, exact deadline contract, contradiction status, and no-drift flags in `tests/integration/test_deadline_timeout_off_by_one_report.py`
- [X] T033 Verify `git status --short` and `git diff --name-only main...HEAD` show only Feature 036 scoped changes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories
- **User Stories (Phase 3+)**: Depend on the Foundation; proceed in priority order
- **Polish (Phase 6)**: Depends on all required user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can begin after Foundation; no dependency on later stories
- **User Story 2 (P2)**: Can begin after Foundation; depends on the audited contract from US1 but remains independently testable
- **User Story 3 (P3)**: Can begin after Foundation; depends on runtime behavior from US1 and US2 for regression validation only

### Within Each User Story

- Tests are written before implementation tasks in the same story
- Runtime auditing comes before any minimal repair
- Report generation comes after the audit and regression coverage are in place

## Parallel Execution Examples

### User Story 1

```bash
Task: "Add boundary unit coverage for deadline_rules.has_expired in tests/unit/test_timeout_contract_boundary.py"
Task: "Add boundary unit coverage for runtime_model.resolve_runtime_terminal_state in tests/unit/test_timeout_contract_boundary.py"
Task: "Add boundary unit coverage for environment.finalize_task_runtime_state_with_parameters in tests/unit/test_timeout_contract_boundary.py"
```

### User Story 2

```bash
Task: "Add config coverage proving TrafficScenarioPreset.paper_default and TrafficConfig.timeout_seconds() produce the audited values in tests/unit/test_timeout_contract_boundary.py"
Task: "Add nonzero-arrival boundary coverage in tests/unit/test_timeout_contract_boundary.py"
Task: "Add helper-agreement coverage proving the audited helpers classify exact-boundary completion the same way in tests/unit/test_timeout_contract_boundary.py"
```

### User Story 3

```bash
Task: "Add integration coverage for exact-deadline completion and after-deadline drop in tests/integration/test_timeout_boundary_audit_flow.py"
Task: "Add integration coverage for reward emission only after terminal outcome and drop-penalty application only for dropped tasks in tests/integration/test_timeout_boundary_audit_flow.py"
Task: "Add report validation coverage in tests/integration/test_timeout_boundary_audit_report.py"
Task: "Add scope-guard coverage for no training, policy, dependency, or campaign drift in tests/integration/test_timeout_boundary_audit_scope_guard.py"
Task: "Add drift coverage proving Feature 033 execution contract remains unchanged in tests/integration/test_execution_time_flow.py"
Task: "Add drift coverage proving Feature 034 transmission-delay contract remains unchanged in tests/integration/test_transmission_delay_runtime_wiring.py"
Task: "Add drift coverage proving Feature 035 capacity-sharing contract remains unchanged in tests/integration/test_public_cloud_capacity_sharing_flow.py"
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 preflight checks.
2. Complete Phase 2 contract and report scaffolding.
3. Deliver User Story 1 for the exact-boundary contract.
4. Validate the helper agreement before touching any minimal repair.

### Incremental Delivery

1. Lock the inclusive boundary contract.
2. Verify helper agreement against the approved timeout values.
3. Add regression and drift coverage.
4. Generate and validate the audit report.

## Notes

- Keep the task list narrow: no fake parallelism, no baseline reruns, no training/policy changes, no transmission-delay changes, no execution-time changes, no capacity-sharing changes.
- Report artifacts must distinguish old boundary behavior from the audited inclusive contract.
- The feature is a runtime audit with minimal repair only if a contradiction is proven.
