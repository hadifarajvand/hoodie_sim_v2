# Tasks: Smoke Training

**Input**: Design artifacts from `specs/040-smoke-training/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`
**Branch**: `040-smoke-training`

**Dependency gate**: This feature is blocked unless `torch` is already available in the approved interpreter. If `torch` is unavailable, implementation stops after generating a `dependency_blocked` report and no dependency files are edited.

## Format: `[ID] [P?] [US?] Description`

- **[P]**: Can run in parallel with other tasks only when it does not depend on incomplete work in the same files.
- **[US1]**: Smoke contract and runner.
- **[US2]**: Delayed reward and replay contract.
- **[US3]**: Reporting and scope guard.
- No task in this feature may authorize full training, target-network updates, campaign runners, baseline comparison, or environment/runtime/policy/reward changes.

## Phase 1: Setup and Gates

- [X] T001 Verify the feature branch and repository prerequisite state before any implementation work:
  - current branch == `040-smoke-training`
  - current branch != `main`
  - `main == origin/main`
  - `main == 039-paper-hoodie-network-implementation-complete^{}`
  - `git diff --name-only 039-paper-hoodie-network-implementation-complete^{} main` is empty
  - `.specify/feature.json` may be present only as a local active-feature pointer
  - `.specify/feature.json` must not be staged
  - `.specify/feature.json` must not appear in `git diff --name-only main...HEAD`
  - implementation is blocked if any assertion fails
- [X] T002 Check dependency availability in the approved interpreter and record the result for the feature:
  - verify whether `torch` imports successfully in `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`
  - verify no dependency files are modified
  - if `torch` is unavailable, generate the `dependency_blocked` report and stop without dependency edits
  - do not add, remove, or edit dependency declarations

## Phase 2: Foundational Prerequisites

- [X] T003 Define the smoke execution contract in `src/analysis/smoke_training/`:
  - `SmokeTrainingConfig`
  - `SmokeReplayTransition`
  - `SmokeBatchSummary`
  - `SmokeTrainingReport`
  - validate `optimizer_steps == 1`
  - validate `state_dim == 3`
  - validate `lookback_w == 10`
  - validate `action_count == 3`
  - validate deterministic seed bundle handling
  - validate that target update/sync is disabled
- [X] T004 Define the smoke reporting schema in `src/analysis/smoke_training/`:
  - required report fields from the spec
  - dependency status handling
  - smoke scope labeling
  - target-update blocked reason
  - no-performance-metrics rule

## Phase 3: User Story 1 - Smoke Contract and Runner (Priority: P1)

**Goal**: Execute a tiny deterministic smoke run that proves the Feature 039 network surface can take exactly one optimizer step with a finite loss and at least one parameter change.

**Independent Test**: The smoke run completes once on a fixture-first batch, reports finite loss, and changes at least one online-network parameter without updating the target network.

- [X] T005 [US1] Implement `SmokeTrainingConfig` validation and tiny smoke-batch constraints in `src/analysis/smoke_training/`
- [X] T006 [P] [US1] Add contract tests in `tests/unit/test_smoke_training_contract.py` for tiny deterministic config, batch size, state/action shape, and optimizer-step bounds
- [X] T007 [US1] Implement the smoke runner entrypoint in `src/analysis/smoke_training/` that builds the Feature 039 online and target networks, constructs the deterministic smoke batch, runs one optimizer step, checks finite loss, and records parameter changes
- [X] T008 [P] [US1] Add determinism tests in `tests/integration/test_smoke_training_determinism.py` to verify the same seed bundle yields the same smoke summary and parameter-update verdict

## Phase 4: User Story 2 - Delayed Reward and Replay Contract (Priority: P2)

**Goal**: Preserve delayed reward semantics in the smoke path without inventing terminal rewards or pretending pending transitions are terminal.

**Independent Test**: The smoke batch obeys delayed reward rules, labels fixture transitions as smoke fixtures, and keeps pending-at-horizon transitions non-terminal.

- [X] T009 [P] [US2] Define the smoke fixture transition schema in `src/analysis/smoke_training/` with `reward_available`, `pending_at_horizon`, and `source_type` rules
- [X] T010 [P] [US2] Add replay and delayed-reward contract tests in `tests/unit/test_smoke_training_contract.py` covering non-terminal reward handling, terminal reward handling, pending-at-horizon handling, and smoke-fixture labeling
- [X] T011 [US2] Implement the smoke batch builder in `src/analysis/smoke_training/` to emit deterministic fixture transitions only, with optional environment rollout limited to interface validation
- [X] T012 [US2] Ensure the smoke runner never converts pending-at-horizon transitions into terminal rewards and never injects fake rewards in `src/analysis/smoke_training/`

## Phase 5: User Story 3 - Reporting and Scope Guard (Priority: P3)

**Goal**: Produce smoke reports that record bounded engineering outcomes and prove no paper reproduction, campaign execution, or target update occurred.

**Independent Test**: The report artifacts show the smoke scope, finite loss, parameter change, deterministic repeatability, and explicit no-target-update status.

- [X] T013 [P] [US3] Generate the smoke report artifacts in `artifacts/analysis/smoke-training/` as JSON and Markdown
- [X] T014 [P] [US3] Add report schema tests in `tests/integration/test_smoke_training_report.py` for required fields, smoke scope, and banned claims
- [X] T015 [US3] Add the scope guard test in `tests/integration/test_smoke_training_scope_guard.py` to allow only the approved smoke paths and read-only imports from Feature 039 and Feature 038 analysis packages
- [X] T016 [US3] Ensure the smoke report records `feature_038_training_readiness_block_respected=true`, `no_target_update_execution=true`, and `no_paper_reproduction_claim=true` in `src/analysis/smoke_training/`

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T017 Run the required validation command exactly as specified:
  - `PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \`
  - `  tests.unit.test_smoke_training_contract \`
  - `  tests.integration.test_smoke_training_report \`
  - `  tests.integration.test_smoke_training_determinism \`
  - `  tests.integration.test_smoke_training_scope_guard \`
  - `  tests.unit.test_paper_hoodie_network_config \`
  - `  tests.unit.test_paper_hoodie_network_shapes \`
  - `  tests.integration.test_paper_hoodie_network_report \`
  - `  tests.integration.test_paper_hoodie_network_scope_guard \`
  - `  tests.unit.test_training_foundation_contract \`
  - `  tests.integration.test_training_foundation_contract_report \`
  - `  tests.integration.test_training_readiness_gate`
- [X] T018 Confirm `AGENTS.md` is not in Feature 040 committed scope; update only `specs/040-smoke-training/quickstart.md` if smoke validation text needs tightening

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in priority order
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Uses the same smoke data and runner but must remain independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on the smoke runner outputs but must remain independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Implementation tasks should be completed in file order to avoid overlapping edits
- Story complete before moving to next priority

### Parallel Opportunities

- T006 and T008 can run in parallel because they touch separate test files
- T009 and T010 can run in parallel because one defines fixture schema and the other validates it
- T013 and T014 can run in parallel because one writes report artifacts and the other validates the report schema

## Parallel Example: User Story 1

```bash
# Launch the smoke contract tests and determinism tests together:
Task: "Add contract tests in tests/unit/test_smoke_training_contract.py"
Task: "Add determinism tests in tests/integration/test_smoke_training_determinism.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational prerequisites
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Confirm one optimizer step, finite loss, parameter change, and no target update

### Incremental Delivery

1. Complete Setup + Foundational → smoke contract ready
2. Add User Story 1 → execute bounded smoke step and validate determinism
3. Add User Story 2 → validate delayed reward semantics and fixture labeling
4. Add User Story 3 → write reports and enforce scope guard

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- The smoke run is not paper reproduction
- Feature 038 readiness stays blocked; Feature 040 is a smoke-only technical exception
