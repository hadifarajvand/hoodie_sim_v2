# Tasks: 007-adaptive-policy-offloading-decisions

**Input**: Design documents from `/specs/007-adaptive-policy-offloading-decisions/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the feature docs and keep the implementation scoped to policy/evaluation layers only.

- [x] T001 Create `specs/007-adaptive-policy-offloading-decisions/spec.md` with adaptive policy context, conservative offloading behavior, paper-backed inputs, and strict out-of-scope items
- [x] T002 Create `specs/007-adaptive-policy-offloading-decisions/clarifications.md` capturing the scope locks from `/speckit.clarify`, including no DRL training, no LSTM, no model switching, and no environment-internal policy execution
- [x] T003 Create `specs/007-adaptive-policy-offloading-decisions/plan.md` with constitution gate, architecture, affected modules, risk controls, and no-dependency policy
- [x] T004 Create `specs/007-adaptive-policy-offloading-decisions/data-model.md` describing `AdaptiveDecisionContext`, optional traffic summary inputs, optional execution/load inputs, legal masks, and fallback behavior
- [x] T005 Create `specs/007-adaptive-policy-offloading-decisions/contracts/adaptive-policy.md` defining the context-builder API and adaptive policy API
- [x] T006 Create `specs/007-adaptive-policy-offloading-decisions/quickstart.md` showing how an external loop builds policy context, chooses an adaptive action, and calls `HoodieGymEnvironment.step(action)`

**Checkpoint**: Feature docs are in place and the implementation surface is bounded.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the shared context model before policy logic exists.

- [x] T007 Create `src/policies/adaptive_context.py` with immutable `AdaptiveDecisionContext` and `build_adaptive_context(policy_context, traffic_summary=None, execution_summary=None)`
- [x] T008 [P] Add `tests/unit/test_adaptive_context.py` covering extraction from observation / `observe_flat`, legal mask preservation, missing traffic summary fallback, task size/density/cycles/deadline fields, and observed arrival probability handling

**Checkpoint**: Adaptive context can be built without mutating environment state.

## Phase 3: User Story 1 - Adaptive Decision Context (Priority: P1)

**Goal**: Expose a paper-backed adaptive decision bundle from existing policy inputs and optional summaries.

**Independent Test**: Build an adaptive decision context from an existing environment observation and confirm it contains the current task, legal actions, queue/load state, compute estimates, and optional traffic summary data without changing environment state.

- [x] T009 [US1] Extend `src/policies/adaptive_context.py` so the context preserves task features, legal mask, queue/load state, deadlines, and optional traffic/execution summaries
- [x] T010 [P] [US1] Add regression coverage in `tests/unit/test_adaptive_context.py` for missing optional summaries, legal mask preservation, and context immutability from the caller perspective

**Checkpoint**: Adaptive context is ready for policy consumption.

## Phase 4: User Story 2 - Conservative Adaptive Policy (Priority: P1)

**Goal**: Provide a deterministic adaptive offloading policy that only selects legal actions.

**Independent Test**: Feed the same adaptive context into the policy repeatedly and verify it returns the same legal action each time for the same inputs.

- [x] T011 [US2] Create `src/policies/adaptive_offloading.py` implementing `AdaptiveOffloadingPolicy` through the existing policy interface
- [x] T012 [US2] Implement deterministic legal-action ranking in `src/policies/adaptive_offloading.py` using latency/execution/load hints when present and canonical fallback order when adaptive fields are absent
- [x] T013 [P] [US2] Add `tests/unit/test_adaptive_offloading_policy.py` covering local-only topology, horizontal-legal/vertical-illegal, vertical-legal/horizontal-illegal, all-actions-legal, high-load, low-load, missing adaptive fields, deterministic repeated calls, and illegal-action rejection

**Checkpoint**: Adaptive policy chooses only legal actions and behaves deterministically.

## Phase 5: User Story 3 - Baseline Compatibility and No Lifecycle Bypass (Priority: P2)

**Goal**: Keep existing policies working through the same `PolicyContext` path while leaving environment lifecycle ownership untouched.

**Independent Test**: Run baseline policies and the adaptive policy through the same policy interface and verify the environment remains unchanged and policy selection stays external.

- [x] T014 [US3] Update `src/policies/policy_interface.py` only if needed to support adaptive context compatibility without breaking existing policies
- [x] T015 [US3] Update `src/policies/__init__.py` only if policy exports are centralized there and adaptive policy exports must be surfaced
- [x] T016 [P] [US3] Add regression coverage in `tests/unit/test_policy_interface.py` or existing policy interface tests proving FLC, HO, VO, RO, BCO, and MLEO still construct and choose actions through the existing `PolicyContext`
- [x] T017 [P] [US3] Add `tests/integration/test_adaptive_policy_environment_flow.py` proving `AdaptiveOffloadingPolicy` runs through `HoodieGymEnvironment` using an external reset/step loop
- [x] T018 [US3] Extend `tests/integration/test_adaptive_policy_environment_flow.py` to use generated traffic from feature 005 and execution/cycles fields from feature 006 when available
- [x] T019 [US3] Extend `tests/integration/test_adaptive_policy_environment_flow.py` to prove no environment-internal policy execution, unchanged reset/step boundary, delayed reward ownership stays in the environment, and `SlotEngine` remains helper-only

**Checkpoint**: Adaptive policy integrates through the existing external policy path without lifecycle drift.

## Phase 6: Documentation and Traceability

**Purpose**: Lock the paper-to-code mapping and record assumption-backed fallback behavior.

- [x] T020 Update `docs/paper_notes/paper_to_code_mapping.md` with mappings for adaptive decision inputs, conservative adaptive baseline, observed load from `traffic_observer.py`, and compute/execution estimates
- [x] T021 Update `docs/assumptions/hoodie_assumptions.md` only if the adaptive ranking heuristic is not fully paper-specified, and label it as a conservative baseline/fallback rather than learned HOODIE
- [x] T022 Add a no-dependency-change verification note in `specs/007-adaptive-policy-offloading-decisions/quickstart.md`

**Checkpoint**: Paper traceability and assumption boundaries are explicit.

## Phase 7: Guardrails and Validation

**Purpose**: Prove nothing outside scope changed and the new policy works under the existing simulation stack.

- [x] T023 Verify no dependency files changed: `pyproject.toml`, `requirements.txt`, `setup.cfg`, `setup.py`, and lockfiles
- [x] T024 Verify no files under `src/training/`, `src/agents/`, or neural-network modules changed for this feature
- [x] T025 Verify `src/environment/slot_engine.py` still has no `run_slot`, `slot_flow`, or controller-shaped lifecycle API
- [x] T026 Run unit tests: `tests/unit/test_adaptive_context.py`, `tests/unit/test_adaptive_offloading_policy.py`, existing policy interface tests, and existing topology legality tests
- [x] T027 Run integration tests: `tests/integration/test_adaptive_policy_environment_flow.py`, `tests/integration/test_dynamic_traffic_environment_flow.py`, `tests/integration/test_execution_time_flow.py`, `tests/integration/test_flc_episode.py`, and `tests/integration/test_evaluation_runner.py`
- [x] T028 Update `specs/007-adaptive-policy-offloading-decisions/tasks.md` checkboxes only after code, docs, and tests are complete

**Checkpoint**: Scope guardrails and regression coverage are satisfied.

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) has no dependencies
- Foundational (Phase 2) depends on Setup and blocks all user stories
- User Story 1 (Phase 3) depends on Foundational
- User Story 2 (Phase 4) depends on Foundational and the adaptive context
- User Story 3 (Phase 5) depends on Foundational and can proceed in parallel with US1/US2 once the shared context exists
- Documentation (Phase 6) depends on stable behavior from the user-story phases
- Guardrails and Validation (Phase 7) runs last

### User Story Dependencies

- **US1** can start after Foundational
- **US2** can start after Foundational and the adaptive context model
- **US3** can start after Foundational, but integration tests should use the completed US1/US2 behavior

### Parallel Opportunities

- `T008` can run in parallel with other non-overlapping context work
- `T010` can run in parallel with `T009`
- `T013` can run in parallel with `T011` and `T012`
- `T016` and `T017` can run in parallel with policy implementation once the shared interface is stable
- `T020` through `T022` can run in parallel after behavior stabilizes
- `T023` through `T027` are independent validation tasks and can be scheduled separately

## Implementation Strategy

### MVP First

1. Complete Phase 1 docs
2. Complete Phase 2 adaptive context
3. Complete Phase 3 adaptive policy
4. Stop and validate the policy can choose a legal action deterministically

### Incremental Delivery

1. Add adaptive context
2. Add deterministic policy
3. Prove existing baselines still work
4. Add traceability and guardrails

### Parallel Team Strategy

1. One developer handles `adaptive_context.py` and its tests
2. One developer handles `adaptive_offloading.py` and its tests
3. One developer handles policy compatibility and integration tests
4. One developer handles documentation and traceability updates
