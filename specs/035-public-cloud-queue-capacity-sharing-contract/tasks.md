---

description: "Task list for Feature 035 - Public/Cloud Queue Capacity Sharing Contract"
---

# Tasks: Public/Cloud Queue Capacity Sharing Contract

**Input**: Design documents from `/specs/035-public-cloud-queue-capacity-sharing-contract/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Required by the feature spec and quickstart. Include targeted runtime, regression, and report validation tests.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Format: `[ID] [P?] [US?] Description with exact file path`

- **[P]**: Can run in parallel with other marked tasks because it touches different files and has no dependency on incomplete work
- **[US?]**: Required for user story phases only
- Every task description must name the file path it changes or verifies

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Lock down the preflight conditions and record the current invalid runtime behavior before code changes.

- [X] T001 Verify branch hygiene and clean-worktree preconditions in shell: current branch is not `main`, branch base matches current `main`, `034-transmission-delay-runtime-wiring-complete` equals `main`, and no unrelated uncommitted files are present
- [X] T002 Record the current invalid per-queue full-capacity behavior in notes for the feature report by inspecting `src/environment/gym_adapter.py` and capturing the pre-change runtime path for `_progress_execution_queues()` and `_maybe_finalize_head()`
- [X] T003 Update `AGENTS.md` for Feature 035 so it references `specs/035-public-cloud-queue-capacity-sharing-contract/plan.md` and `specs/035-public-cloud-queue-capacity-sharing-contract/spec.md`, states public/cloud capacity sharing only, states no execution-helper formula changes, states no transmission-delay changes, states no training/neural-network/policy/dependency/campaign changes, states no paper-recovery claim, and keeps the guidance minimal and feature-scoped

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the capacity-sharing contract and report schema before any runtime wiring starts.

- [X] T004 Define the host-grouping and equal-share capacity-sharing contract in `specs/035-public-cloud-queue-capacity-sharing-contract/contracts/public-cloud-capacity-sharing-contract.md`
- [X] T005 Define the runtime data model for host pools, active heads, and capacity shares in `specs/035-public-cloud-queue-capacity-sharing-contract/data-model.md`
- [X] T006 Define the analysis/report schema and required no-drift flags in `src/analysis/public_cloud_queue_capacity_sharing/report.py`
- [X] T007 Update the feature quickstart validation flow in `specs/035-public-cloud-queue-capacity-sharing-contract/quickstart.md` to name the approved interpreter and targeted tests

**Checkpoint**: Foundation ready - user story implementation can now begin.

## Phase 3: User Story 1 - Shared Public Capacity (Priority: P1) 🎯 MVP

**Goal**: Public EA queues targeting the same host share that host's fixed public CPU capacity deterministically at slot start.

**Independent Test**: Two active public queues targeting the same EA host split that host's edge capacity equally, while a single queue gets the full edge capacity and different EA hosts remain independent.

### Tests for User Story 1

- [X] T008 [P] [US1] Add unit coverage for shared public capacity rules in `tests/unit/test_public_cloud_capacity_sharing.py`
- [X] T009 [P] [US1] Add integration coverage for same-host and different-host public queue sharing in `tests/integration/test_public_cloud_capacity_sharing_flow.py`

### Implementation for User Story 1

- [X] T010 [US1] Add deterministic host-grouping helpers for public EA queues in `src/environment/gym_adapter.py`
- [X] T011 [US1] Wire host-level edge capacity allocation into `_progress_execution_queues()` in `src/environment/gym_adapter.py`
- [X] T012 [US1] Pass per-head edge capacity shares into `step_execution()` instead of full host capacity in `src/environment/gym_adapter.py`
- [X] T013 [US1] Preserve local/private queue progression while routing only public EA queues through the shared-capacity path in `src/environment/gym_adapter.py`

**Checkpoint**: Public EA capacity sharing should be fully functional and independently testable.

## Phase 4: User Story 2 - Shared Cloud Capacity (Priority: P2)

**Goal**: Cloud-bound queues share the fixed global cloud CPU capacity deterministically without multiplying capacity by queue count.

**Independent Test**: Multiple active cloud queues split the configured cloud capacity equally, and total cloud consumption never exceeds the cloud limit.

### Tests for User Story 2

- [X] T014 [P] [US2] Add unit coverage for cloud capacity sharing rules in `tests/unit/test_public_cloud_capacity_sharing.py`
- [X] T015 [P] [US2] Add integration coverage for cloud queue sharing and cloud capacity limits in `tests/integration/test_public_cloud_capacity_sharing_flow.py`

### Implementation for User Story 2

- [X] T016 [US2] Route cloud queue heads into a single deterministic `"cloud"` host pool in `src/environment/gym_adapter.py`
- [X] T017 [US2] Allocate cloud capacity shares from `ComputeConfig.cpu_capacity_per_slot_cloud` in `src/environment/gym_adapter.py`
- [X] T018 [US2] Enforce no same-slot redistribution for cloud queue heads in `src/environment/gym_adapter.py`

**Checkpoint**: Cloud capacity sharing should now be independently functional and bounded by the configured pool.

## Phase 5: User Story 3 - Deterministic Scheduling and Regression Safety (Priority: P3)

**Goal**: Keep the sharing contract deterministic and prove it does not drift into local/private execution, Feature 033 execution, Feature 034 transmission delay, or reward timing.

**Independent Test**: Re-running the same multi-queue scenario yields the same host/head ordering and the same shares, while regression checks confirm local/private execution, execution timing, transmission delay, and reward timing remain unchanged.

### Tests for User Story 3

- [X] T019 [P] [US3] Add deterministic-order regression coverage for host groups and active heads in `tests/unit/test_public_cloud_capacity_sharing.py`
- [X] T020 [P] [US3] Add local/private regression coverage in `tests/integration/test_public_cloud_capacity_sharing_flow.py`
- [X] T021 [P] [US3] Add Feature 033 execution-contract drift coverage in `tests/integration/test_execution_time_flow.py`
- [X] T022 [P] [US3] Add Feature 034 transmission-delay drift coverage in `tests/integration/test_transmission_delay_runtime_wiring.py`
- [X] T023 [P] [US3] Add reward-timing regression coverage in `tests/integration/test_mechanism_repair_timeout_drop.py`
- [X] T024 [P] [US3] Add scope-guard regression coverage for dependency, training, policy, and campaign drift in `tests/integration/test_public_cloud_capacity_sharing_scope_guard.py`

### Implementation for User Story 3

- [X] T025 [US3] Add deterministic stable ordering for host groups and active queue heads in `src/environment/gym_adapter.py`
- [X] T026 [US3] Add optional capacity-sharing metadata fields to task state in `src/environment/gym_adapter.py` for provenance and report generation
- [X] T027 [US3] Add the report generator package in `src/analysis/public_cloud_queue_capacity_sharing/__init__.py`
- [X] T028 [US3] Implement the capacity-sharing report builder in `src/analysis/public_cloud_queue_capacity_sharing/report.py`
- [X] T029 [US3] Generate the JSON report at `artifacts/analysis/public-cloud-queue-capacity-sharing/public-cloud-capacity-sharing-report.json`
- [X] T030 [US3] Generate the Markdown report at `artifacts/analysis/public-cloud-queue-capacity-sharing/public-cloud-capacity-sharing-report.md`

**Checkpoint**: Deterministic behavior, regression safety, and report generation should all be covered.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup across all stories.

- [X] T031 Validate the full targeted test suite with the approved interpreter in `specs/035-public-cloud-queue-capacity-sharing-contract/quickstart.md`
- [X] T032 Verify `AGENTS.md` references the current Feature 035 plan and spec, does not retain stale active-feature guidance, and is classified as intentional feature guidance metadata in the final diff
- [X] T033 Verify the report schema fields and no-drift flags in `tests/integration/test_public_cloud_capacity_sharing_report.py`
- [X] T034 Verify `git status --short` and `git diff --name-only main...HEAD` show only Feature 035 scoped changes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories
- **User Stories (Phase 3+)**: Depend on the Foundation; proceed in priority order
- **Polish (Phase 6)**: Depends on all required user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can begin after Foundation; no dependency on later stories
- **User Story 2 (P2)**: Can begin after Foundation; may reuse runtime helpers from US1 but remains testable on its own
- **User Story 3 (P3)**: Can begin after Foundation; depends on runtime behavior from US1 and US2 for regression validation only

### Within Each User Story

- Tests are written before implementation tasks in the same story
- Runtime wiring comes before report generation
- Regression guards are added before final polish

## Parallel Execution Examples

### User Story 1

```bash
Task: "Add unit coverage for shared public capacity rules in tests/unit/test_public_cloud_capacity_sharing.py"
Task: "Add integration coverage for same-host and different-host public queue sharing in tests/integration/test_public_cloud_capacity_sharing_flow.py"
```

### User Story 2

```bash
Task: "Add unit coverage for cloud capacity sharing rules in tests/unit/test_public_cloud_capacity_sharing.py"
Task: "Add integration coverage for cloud queue sharing and cloud capacity limits in tests/integration/test_public_cloud_capacity_sharing_flow.py"
```

### User Story 3

```bash
Task: "Add deterministic-order regression coverage for host groups and active heads in tests/unit/test_public_cloud_capacity_sharing.py"
Task: "Add local/private regression coverage in tests/integration/test_public_cloud_capacity_sharing_flow.py"
Task: "Add Feature 033 execution-contract drift coverage in tests/integration/test_execution_time_flow.py"
Task: "Add Feature 034 transmission-delay drift coverage in tests/integration/test_transmission_delay_runtime_wiring.py"
Task: "Add reward-timing regression coverage in tests/integration/test_mechanism_repair_timeout_drop.py"
Task: "Add scope-guard regression coverage for dependency, training, policy, and campaign drift in tests/integration/test_public_cloud_capacity_sharing_scope_guard.py"
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 preflight checks.
2. Complete Phase 2 contract and report scaffolding.
3. Deliver User Story 1 for same-host public capacity sharing.
4. Validate the edge sharing behavior before touching cloud logic.

### Incremental Delivery

1. Lock down the host-sharing contract.
2. Add public EA capacity sharing.
3. Add cloud capacity sharing.
4. Add deterministic ordering and regression guards.
5. Generate and validate the analysis report.

## Notes

- Keep the task list narrow: no fake parallelism, no baseline reruns, no training/policy changes, no transmission-delay changes, no execution-time changes.
- Report artifacts must distinguish wired runtime components from validated runtime components.
- The feature is a runtime engineering contract, not paper recovery.
