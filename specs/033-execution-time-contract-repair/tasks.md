# Tasks: Execution-Time Contract Repair

**Input**: Design documents from `/specs/033-execution-time-contract-repair/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required. This feature specifically requests unit and integration tests.

**Organization**: Tasks are ordered to fix execution accounting first, then validate completion-slot, timeout/drop, and reward timing semantics.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel only when explicitly marked and truly independent
- **[Story]**: User story or cross-cutting phase this task belongs to
- Include exact file paths in descriptions

## Phase 1: Preflight

**Purpose**: Verify branch hygiene and scope before any implementation work.

- [X] T001 Verify current branch is not `main`, branch base is current `main`, and `032-runtime-adoption-approved-assumption-registry-complete` equals `main`; stop immediately if any check fails.
- [X] T002 Verify the working tree contains no uncommitted unrelated changes; stop if there are unrelated files outside the Feature 033 scope.

## Phase 2: Foundational Contract Repair

**Purpose**: Remove the invalid execution shortcut and establish the repaired per-slot contract.

- [X] T003 Inspect `src/environment/execution_helper.py` and record the current invalid local/private shortcut behavior in the Feature 033 report inputs.
- [X] T004 Remove the local/private shortcut from `src/environment/execution_helper.py` so `step_execution()` always applies uniform per-slot accounting.
- [X] T005 In `src/environment/execution_helper.py`, enforce `cycles_consumed = min(cycles_before, compute_capacity)` and `cycles_after = max(0, cycles_before - compute_capacity)` for every destination kind.
- [X] T006 In `src/environment/execution_helper.py`, ensure `cycles_remaining` never increases and completion cannot occur before `cycles_remaining` reaches zero.
- [X] T007 Document the exact completion-slot behavior in `src/environment/execution_helper.py` metadata or adjacent contract text so completion is recorded at the end of the finishing slot.

## Phase 3: User Story 1 - Capacity-Bounded Execution (Priority: P1)

**Goal**: Each destination consumes at most its configured per-slot capacity.

**Independent Test**: A task larger than capacity spans multiple slots without the shortcut finishing it immediately.

### Tests for User Story 1

- [X] T008 Add unit tests in `tests/unit/test_execution_helper.py` covering local/private execution with `cycles_required > capacity` not completing in one slot.
- [X] T009 Add unit tests in `tests/unit/test_execution_helper.py` covering local/private, public/edge, and cloud execution each consuming at most the configured capacity per slot.
- [X] T010 Add unit tests in `tests/unit/test_execution_helper.py` covering the exact boundary case where `cycles_required == capacity`.
- [X] T011 Add unit tests in `tests/unit/test_execution_helper.py` covering monotonic decrease of `cycles_remaining` across multiple slots.

### Implementation for User Story 1

- [X] T012 Verify `src/environment/execution_helper.py` preserves or clarifies metadata fields for execution progress, and update tests if any metadata semantics must change.
- [X] T013 Verify `src/environment/runtime_model.py` does not conflict with the repaired execution contract; patch only if tests prove `SharedRuntimeParameters` / `advance_shared_runtime` contradict the execution helper.

## Phase 4: User Story 2 - Completion, Timeout, and Reward Integrity (Priority: P2)

**Goal**: Completion, timeout/drop, and delayed reward emission remain correct when execution spans multiple slots.

**Independent Test**: Multi-slot execution completes only after the last required cycles are consumed and timeout/drop still resolves afterward.

### Tests for User Story 2

- [X] T014 Add integration tests in `tests/integration/test_execution_time_flow.py` proving `HoodieGymEnvironment._maybe_finalize_head()` uses `ComputeConfig.capacity_for(destination_kind)` for local, public, and cloud execution.
- [X] T015 Add integration tests in `tests/integration/test_execution_time_flow.py` proving multi-slot local completion follows the documented completion-slot contract.
- [X] T016 Add regression tests in `tests/integration/test_mechanism_repair_timeout_drop.py` or `tests/integration/test_execution_time_flow.py` proving timeout/drop still works when execution spans multiple slots.
- [X] T017 Add regression tests in `tests/integration/test_execution_time_flow.py` proving reward is emitted only after terminal completion or drop.

### Implementation for User Story 2

- [X] T018 Patch `src/environment/gym_adapter.py` only if required so finalization uses the repaired execution contract without changing the delayed-reward boundary.
- [X] T019 Verify `src/environment/gym_adapter.py` routes local, public, and cloud destination kinds to the correct `ComputeConfig.capacity_for(...)` values and does not reintroduce a shortcut.
- [X] T020 Verify `src/environment/execution_helper.py` and `src/environment/gym_adapter.py` agree on completion-slot semantics and terminal-state timing.

## Phase 5: Cross-Cutting Validation and Reporting

**Purpose**: Lock the repair down with scope guards and a final report.

- [X] T021 Add scope-guard tests proving no dependency, training, neural-network, policy, or campaign drift in `tests/integration/test_runtime_adoption_scope_guard.py` or the equivalent Feature 033 scope-guard file.
- [X] T022 Create `artifacts/analysis/execution-time-contract-repair/execution-time-contract-report.json` and `artifacts/analysis/execution-time-contract-repair/execution-time-contract-report.md`.
- [X] T023 Populate the Feature 033 report with `feature_id`, `repaired_runtime_components`, `old_invalid_behavior`, `new_execution_contract`, `completion_slot_contract`, `destination_kinds_validated`, `tests_added`, `tests_run`, and final verdict fields.
- [X] T024 Run the approved interpreter against the targeted unit tests for `src/environment/execution_helper.py`.
- [X] T025 Run the approved interpreter against the relevant integration tests for `src/environment/gym_adapter.py` and timeout/reward flow.
- [X] T026 Run the approved interpreter against any affected runtime/evaluation smoke tests if the repaired execution contract changes runtime behavior.
- [X] T027 Verify `git status --short` and `git diff --name-only` show only Feature 033 files and approved analysis artifacts.

## Dependencies & Execution Order

- T001-T002 must complete before any file edits.
- T003-T007 must complete before testing the repaired execution contract.
- T008-T013 depend on T004-T007.
- T014-T020 depend on T004-T007 and the execution helper repair.
- T021-T027 depend on the implementation and test changes being complete.

## Parallel Opportunities

None. This feature is intentionally sequential because the execution-helper fix, environment validation, timeout/reward regression tests, and report generation depend on one another.

## Implementation Strategy

1. Remove the local/private shortcut and normalize per-slot execution accounting.
2. Prove the completion-slot contract with unit tests.
3. Prove multi-slot completion, timeout/drop, and delayed reward behavior with integration tests.
4. Confirm no scope drift with a final report and diff check.
