# Tasks: Transmission Delay Runtime Wiring

**Input**: Design documents from `/specs/034-transmission-delay-runtime-wiring/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Explicitly requested by the feature specification and user instructions.

**Organization**: Tasks are grouped by user story to keep transmission-delay wiring independently testable from queue admission and timeout/reward behavior.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel if it touches different files and does not depend on incomplete tasks
- **[Story]**: Required for user story phases only
- Include exact file paths in every task description

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the implementation boundary and keep the feature scoped to transmission-delay wiring only.

- [X] T001 Verify the approved interpreter, branch hygiene, and clean-tree preconditions in `git` and `.specify/scripts/bash/check-prerequisites.sh`
- [X] T002 Record the old fixed-one-slot transmission behavior for the feature report in `src/analysis/transmission_delay_runtime_wiring/report.py`
- [X] T003 [P] Confirm the existing transmission helper contract and rounding policy in `src/environment/link_rate_config.py`

**Checkpoint**: Transmission-delay scope and helper contract are confirmed before runtime edits begin.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared runtime contract needed by all user stories.

- [X] T004 Define the transmission metadata shape and boundary semantics in `specs/034-transmission-delay-runtime-wiring/data-model.md`
- [X] T005 [P] Document the runtime transmission contract in `specs/034-transmission-delay-runtime-wiring/contracts/transmission-delay-runtime-contract.md`
- [X] T006 Update the quickstart validation and report expectations in `specs/034-transmission-delay-runtime-wiring/quickstart.md`
- [X] T007 Update the agent reference pointer in `AGENTS.md` to `specs/034-transmission-delay-runtime-wiring/plan.md`

**Checkpoint**: Transmission contract, metadata, and plan references are ready for runtime wiring.

---

## Phase 3: User Story 1 - Payload-Based Offload Delay (Priority: P1)

**Goal**: Horizontal and vertical offloads spend deterministic transmission delay slots proportional to payload size and link rate instead of completing in one fixed slot.

**Independent Test**: A horizontal offload and a vertical offload for the same payload produce different delay slots, and both are derived from `compute_transmission_delay()` rather than fixed admission.

### Tests for User Story 1

- [X] T008 [P] [US1] Add helper tests for payload conversion, `compute_transmission_delay()` as the single source of `delay_slots`, and `LinkRateConfig.rounding_policy` propagation in `tests/unit/test_link_rate_conversion.py` and `tests/unit/test_link_rate_transmission_delay.py`
- [X] T009 [P] [US1] Add horizontal/vertical delay selection tests in `tests/unit/test_slot_engine.py`
- [X] T010 [P] [US1] Add integration tests for horizontal and vertical runtime transmission delay and stored rounding policy metadata in `tests/integration/test_transmission_delay_runtime_wiring.py`
- [X] T011 [P] [US1] Add boundary tests for exact delay-slot admission and rounding-policy boundary behavior in `tests/integration/test_transmission_delay_runtime_wiring.py`

### Implementation for User Story 1

- [X] T012 [US1] Compute transmission delay metadata for horizontal and vertical offloads only by calling `compute_transmission_delay()` and passing `LinkRateConfig.rounding_policy` in `src/environment/gym_adapter.py`
- [X] T013 [US1] Store `transmission_started_at`, `transmission_delay_slots`, `transmission_delay_seconds`, `transmission_payload_bits`, `transmission_data_rate_bps`, `transmission_rate_source`, and `transmission_rounding_policy` on the task metadata in `src/environment/gym_adapter.py`
- [X] T014 [US1] Keep local execution free of transmission metadata in `src/environment/gym_adapter.py`
- [X] T015 [US1] Keep `SlotEngine` helper-only while making admission read the recorded transmission boundary in `src/environment/slot_engine.py`
- [X] T016 [US1] Move tasks into the downstream public/cloud execution queue only after the transmission boundary is satisfied in `src/environment/gym_adapter.py`

**Checkpoint**: Horizontal and vertical offloads no longer behave like one-slot transfers.

---

## Phase 4: User Story 2 - Deterministic Offload Queue Admission (Priority: P2)

**Goal**: Offloading queues admit tasks only at the documented transmission boundary and record the completion timestamp deterministically.

**Independent Test**: A task remains in the offloading queue before the boundary and is admitted exactly once at the boundary with completion metadata recorded.

### Tests for User Story 2

- [X] T017 [P] [US2] Add offload queue admission boundary regression tests in `tests/unit/test_slot_engine.py`
- [X] T018 [P] [US2] Add offloading queue state regression tests in `tests/unit/test_offload_next_slot.py`
- [X] T019 [P] [US2] Add integration tests that verify transmission completion metadata is recorded in `tests/integration/test_transmission_delay_runtime_wiring.py`

### Implementation for User Story 2

- [X] T020 [US2] Record `transmission_completed_at` when the boundary is first satisfied in `src/environment/gym_adapter.py`
- [X] T021 [US2] Prevent offloading queue completion before `current_slot >= transmission_started_at + transmission_delay_slots` in `src/environment/slot_engine.py`
- [X] T022 [US2] Preserve queue state and trace transitions for transmission start/completion in `src/environment/offloading_queue.py` and `src/environment/gym_adapter.py`

**Checkpoint**: Admission is deterministic, boundary-driven, and traceable.

---

## Phase 5: User Story 3 - Timeout and Reward Integrity (Priority: P3)

**Goal**: Transmission delay counts toward runtime delay for timeout/drop decisions without changing terminal-only reward timing.

**Independent Test**: A task that times out while transmitting drops before reward emission, and a task that completes transmission keeps existing delayed reward behavior unchanged.

### Tests for User Story 3

- [X] T023 [P] [US3] Add timeout regression coverage for transmitting tasks in `tests/integration/test_mechanism_repair_timeout_drop.py`
- [X] T024 [P] [US3] Add reward-timing regression coverage ensuring no reward is emitted during transmission in `tests/integration/test_transmission_delay_runtime_wiring.py`
- [X] T025 [P] [US3] Add feature scope-guard coverage for execution, training, policy, dependency, and campaign drift in `tests/integration/test_transmission_delay_runtime_wiring.py`

### Implementation for User Story 3

- [X] T026 [US3] Ensure timeout/drop evaluation includes offloading-queue time in `src/environment/gym_adapter.py`
- [X] T027 [US3] Preserve terminal-only reward emission while transmission is still in progress in `src/environment/gym_adapter.py`
- [X] T028 [US3] Add report generation in `src/analysis/transmission_delay_runtime_wiring/report.py` that explicitly includes `feature_id`, `wired_runtime_components`, `validated_runtime_components`, `old_invalid_behavior`, `new_transmission_contract`, `horizontal_rate_mbps`, `vertical_rate_mbps`, `slot_duration_seconds`, `rounding_policy`, `admission_boundary_contract`, `transmission_metadata_fields`, `tests_added`, `tests_run`, all no-drift flags, and `final_verdict`
- [X] T029 [US3] Write the JSON and Markdown report artifacts in `artifacts/analysis/transmission-delay-runtime-wiring/transmission-delay-runtime-report.json` and `artifacts/analysis/transmission-delay-runtime-wiring/transmission-delay-runtime-report.md`, and add report tests that assert those fields exist with the exact expected values

**Checkpoint**: Timeout/drop and reward timing remain correct under transmission delay.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the full scope, ensure no drift, and lock the report artifacts.

- [X] T030 [P] Run targeted unit tests with the approved interpreter in `tests/unit/test_link_rate_conversion.py`, `tests/unit/test_link_rate_transmission_delay.py`, `tests/unit/test_slot_engine.py`
- [X] T031 [P] Run relevant integration tests with the approved interpreter in `tests/integration/test_transmission_delay_runtime_wiring.py`, `tests/integration/test_mechanism_repair_timeout_drop.py`, `tests/integration/test_execution_time_flow.py`, `tests/integration/test_execution_time_contract_scope_guard.py`
- [X] T032 [P] Confirm `git status --short` and `git diff --name-only main...HEAD` show only the Feature 034 footprint
- [X] T033 Finalize the transmission-delay report summary and mark the feature complete in `src/analysis/transmission_delay_runtime_wiring/report.py` after the report tests confirm the required field set and values

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion; blocks user stories
- **User Story 1 (P1)**: Depends on Foundational completion
- **User Story 2 (P2)**: Depends on User Story 1 because it relies on the same transmission metadata and queue boundary contract
- **User Story 3 (P3)**: Depends on User Stories 1 and 2 because it validates timeout and reward behavior after transmission is wired
- **Polish**: Depends on all user stories being complete

### User Story Dependencies

- **US1**: Can start after Phase 2
- **US2**: Requires the transmission metadata and admission boundary from US1
- **US3**: Requires the transmission wiring and boundary behavior from US1 and US2

### Within Each User Story

- Tests are written before implementation tasks for that story
- The runtime helper boundary is preserved
- Environment orchestration changes happen before report generation
- Reports are generated only after the runtime behavior and tests are in place

### Parallel Opportunities

- `T003`, `T005`, and `T006` can run in parallel with `T004` if file paths do not overlap
- `T008` through `T011` can run in parallel because they touch different test files
- `T012` through `T016` should be implemented sequentially because they all touch `src/environment/gym_adapter.py` or `src/environment/slot_engine.py`
- `T017` through `T019` can run in parallel after US1 implementation lands
- `T023` through `T025` can run in parallel after the runtime wiring is complete

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Deliver User Story 1 so transmission delay is computed and stored deterministically.
3. Validate that horizontal and vertical offloads are no longer fixed one-slot transfers.

### Incremental Delivery

1. Wire delay metadata and queue admission for offloads.
2. Record boundary completion and keep `SlotEngine` helper-only.
3. Add timeout and reward regression coverage.
4. Generate and validate the transmission-delay report artifacts.

## Validation Summary

- **US1 independent test**: Delay slots are derived from payload and rate, not fixed admission.
- **US2 independent test**: Admission occurs exactly at the documented boundary.
- **US3 independent test**: Timeout and reward behavior remain terminal-only and delayed.

## Notes

- All tasks must preserve Feature 033 execution behavior and Feature 032 topology legality.
- No task may introduce a new cloud-specific transmission rate.
- No task may touch training, neural-network, policy, or campaign code.
