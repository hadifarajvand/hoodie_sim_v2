# Tasks: Paper-default Terminal Exposure Probe

**Input**: Design artifacts from `specs/042-paper-default-terminal-exposure-probe/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`
**Branch**: `042-paper-default-terminal-exposure-probe`

**Dependency gate**: This feature is blocked unless the Feature 042 prerequisite state is clean and the approved interpreter can run the repaired runtime contracts. Do not add dependency files, training logic, or runtime-semantic changes.

## Format: `[ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel only when it does not depend on incomplete work in the same files.
- **[US1]**: Paper-default probe config and lifecycle counters.
- **[US2]**: Probe strategies and runtime execution.
- **[US3]**: Reporting, diagnosis, and scope guard.
- No task in this feature may authorize training, optimizer steps, replay training, target updates, runtime mutation, reward-timing changes, or fake terminal outcomes.

## Phase 1: Setup and Gates

- [X] T001 Verify the feature branch and repository prerequisite state before any implementation work:
  - current branch == `042-paper-default-terminal-exposure-probe`
  - current branch != `main`
  - `main == origin/main`
  - `main == 041-full-training-reproduction-campaign-complete^{}`
  - `git diff --name-only 041-full-training-reproduction-campaign-complete^{} main` is empty
  - `.specify/feature.json` may be present only as a local active-feature pointer
  - `.specify/feature.json` must not be staged
  - `.specify/feature.json` must not appear in `git diff --name-only main...HEAD`
  - no unrelated dirty files are present
  - implementation is blocked if any assertion fails
- [X] T002 Check prior feature gate artifacts and record the result for the probe:
  - verify Feature 037 baseline revalidation report exists and is valid
  - verify Feature 038 training foundation report exists and is valid
  - verify Feature 039 paper HOODIE network report exists and is valid
  - verify Feature 040 smoke training report exists and is valid
  - verify Feature 041 full-training campaign gate report exists and is valid
  - do not modify prior feature artifacts
- [X] T003 Check the approved interpreter and runtime dependency state in `specs/042-paper-default-terminal-exposure-probe/` context:
  - verify `torch` imports successfully in `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`
  - verify no dependency files are modified
  - verify the feature is diagnostic only and does not authorize training
  - do not add, remove, or edit dependency declarations

## Phase 2: Foundational Prerequisites

- [X] T004 Define the terminal exposure probe config and strategy contract in `src/analysis/paper_default_terminal_exposure_probe/`:
  - `TerminalExposureProbeConfig`
  - `ProbeStrategy` constants or enum
  - `T = 110` paper-default horizon
  - `timeout_slots = 20`
  - deterministic seed list `[0, 1, 2]`
  - strategy list for default, forced local, forced horizontal, forced vertical, and mixed legal round robin
  - `no_training = true`
  - `no_runtime_mutation = true`
- [X] T005 [P] Define the terminal exposure counters and report schema in `src/analysis/paper_default_terminal_exposure_probe/`:
  - per-strategy counters from the spec
  - aggregate exposure summary
  - lifecycle integrity flag
  - diagnosis and recommended-next-feature fields
  - no paper-reproduction claim handling
- [X] T006 [P] Define the probe report writer in `src/analysis/paper_default_terminal_exposure_probe/`:
  - JSON artifact
  - Markdown artifact
  - consistent field names between formats
  - diagnostic-only final verdicts

## Phase 3 - User Story 1: Probe Operator (Priority: P1)

**Goal**: Prove whether reward-bearing terminal outcomes appear when the paper-default horizon is used.

**Independent Test**: Run the probe at `T = 110` and verify that terminal exposure counters are recorded per strategy without changing simulator semantics.

- [X] T007 [US1] Implement the paper-default probe runner in `src/analysis/paper_default_terminal_exposure_probe/` to run the repaired runtime at `T = 110` and collect lifecycle counters for each seed
- [X] T008 [P] [US1] Add config tests in `tests/unit/test_paper_default_terminal_exposure_config.py` covering `T = 110`, `timeout_slots = 20`, the deterministic seed list, and the full probe strategy set
- [X] T009 [P] [US1] Add schema tests in `tests/unit/test_paper_default_terminal_exposure_schema.py` covering the exact counter fields and report fields required by the spec
- [X] T010 [US1] Implement the lifecycle counter collection in `src/analysis/paper_default_terminal_exposure_probe/` to record terminal, reward-bearing, pending-at-horizon, deadline, and reward-emission counts without fabricating outcomes

## Phase 4 - User Story 2: Strategy Analyst (Priority: P2)

**Goal**: Compare deterministic strategies to determine whether terminal exposure depends on action-selection behavior.

**Independent Test**: Run each strategy across the configured seeds and verify that local, horizontal, and vertical/cloud behavior is reported separately with legal-mask compliance.

- [X] T011 [US2] Implement deterministic probe strategies in `src/analysis/paper_default_terminal_exposure_probe/` for default policy, forced local, forced horizontal, forced vertical, and mixed legal round robin
- [X] T012 [P] [US2] Add execution tests in `tests/integration/test_paper_default_terminal_exposure_probe.py` covering environment usage, legal action mask compliance, reward timing preservation, and non-terminal pending-at-horizon behavior
- [X] T013 [P] [US2] Add lifecycle-contract tests in `tests/integration/test_paper_default_terminal_exposure_probe.py` covering local/horizontal/vertical action separation, illegal mask-failure recording, and rejection of fake terminal outcomes
- [X] T014 [US2] Implement strategy selection and per-strategy aggregation in `src/analysis/paper_default_terminal_exposure_probe/` using only existing environment interfaces and no policy redesign

## Phase 5 - User Story 3: Diagnostic Reporter (Priority: P3)

**Goal**: Produce an honest report that states whether terminal exposure exists under the paper-default probe.

**Independent Test**: Generate the JSON and Markdown reports and verify that they record the paper-default runtime, per-strategy results, aggregate exposure, and final verdict.

- [X] T015 [P] [US3] Add report schema tests in `tests/integration/test_paper_default_terminal_exposure_report.py` for the required JSON/Markdown fields, final verdicts, and recommended-next-feature handling
- [X] T016 [US3] Implement the diagnostic report assembly in `src/analysis/paper_default_terminal_exposure_probe/` including aggregate terminal exposure diagnosis and recommended next feature
- [X] T017 [US3] Generate the report artifacts in `artifacts/analysis/paper-default-terminal-exposure-probe/` as JSON and Markdown
- [X] T018 [P] [US3] Add the scope guard in `tests/integration/test_paper_default_terminal_exposure_scope_guard.py` to allow only the approved probe paths and read-only imports from Feature 041, Feature 040, Feature 039, and Feature 038 analysis packages
- [X] T019 [US3] Add exact report-schema tests in `tests/integration/test_paper_default_terminal_exposure_report.py` that fail if any audit flag is missing or false, and require `final_verdict`, `diagnosis`, and `recommended_next_feature` alongside the JSON/Markdown fields
- [X] T020 [US3] Ensure the report schema in `src/analysis/paper_default_terminal_exposure_probe/` requires these audit flags to be present and true: `no_training_started`, `no_optimizer_step`, `no_replay_training`, `no_target_update_execution`, `no_dependency_drift`, `no_environment_contract_drift`, `no_policy_drift`, `no_reward_timing_change`, `no_curve_fitting`, `no_simulator_output_tuning`, `no_paper_reproduction_claim`
- [X] T021 [US3] Ensure the report records `final_verdict = terminal_exposure_absent_under_paper_default` when aggregate reward-bearing terminal exposure remains zero, and `final_verdict = terminal_exposure_present` only when reward-bearing exposure is observed
- [X] T022 [US3] Add negative-path tests in `tests/integration/test_paper_default_terminal_exposure_report.py` that fail if the report claims paper reproduction, approves training, or omits the required no-training/no-drift/no-reproduction audit flags

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T023 Run the required validation command exactly as specified:
  - `PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \`
  - `  tests.unit.test_paper_default_terminal_exposure_config \`
  - `  tests.unit.test_paper_default_terminal_exposure_schema \`
  - `  tests.integration.test_paper_default_terminal_exposure_probe \`
  - `  tests.integration.test_paper_default_terminal_exposure_report \`
  - `  tests.integration.test_paper_default_terminal_exposure_scope_guard \`
  - `  tests.unit.test_smoke_training_contract \`
  - `  tests.integration.test_smoke_training_report \`
  - `  tests.unit.test_paper_hoodie_network_config \`
  - `  tests.unit.test_paper_hoodie_network_shapes \`
  - `  tests.integration.test_paper_hoodie_network_report \`
  - `  tests.unit.test_training_foundation_contract \`
  - `  tests.integration.test_training_foundation_contract_report \`
  - `  tests.integration.test_deadline_timeout_off_by_one_audit \`
  - `  tests.integration.test_execution_time_flow \`
  - `  tests.integration.test_transmission_delay_runtime_wiring \`
  - `  tests.integration.test_public_cloud_capacity_sharing_flow`
- [X] T024 Confirm `.specify/feature.json` remains local-only and is not included in the committed 042 diff; update `specs/042-paper-default-terminal-exposure-probe/quickstart.md` only if the validation text needs tightening

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in priority order
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on the paper-default runtime probe contract and lifecycle counter schema
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on probe outputs but remains independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Probe configuration before runner implementation
- Runner before lifecycle counters and report assembly
- Story complete before moving to next priority

### Parallel Opportunities

- T005 and T006 can run in parallel because they touch separate report-schema and writer concerns
- T008 and T009 can run in parallel because one covers config contract and the other covers schema contract
- T012 and T013 can run in parallel because they touch different integration assertions on the same probe flow
- T015 and T018 can run in parallel because one covers report schema and the other covers scope guard

## Parallel Example: User Story 2

```bash
# Launch the execution and lifecycle-contract tests together:
Task: "Add execution tests in tests/integration/test_paper_default_terminal_exposure_probe.py"
Task: "Add lifecycle-contract tests in tests/integration/test_paper_default_terminal_exposure_probe.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational prerequisites
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Confirm paper-default horizon, lifecycle counters, and honest terminal-exposure reporting

### Incremental Delivery

1. Complete Setup + Foundational → probe contract ready
2. Add User Story 1 → paper-default terminal exposure counters
3. Add User Story 2 → deterministic strategy comparison
4. Add User Story 3 → diagnostic reporting and scope guard

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
- Feature 042 is diagnostic only and does not approve training
- Feature 041 remains readiness-blocked unless separately approved later
- The probe must not fake terminal outcomes or change runtime semantics to create them
