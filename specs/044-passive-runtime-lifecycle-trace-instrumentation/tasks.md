# Tasks: Passive Runtime Lifecycle Trace Instrumentation

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the passive trace package, report artifact locations, and the report cleanliness gate before story work begins.

**Quality Gate**: Confirm tests are identified, config validation is explicit, artifact handling rules are explicit, and the review gate blocks dirty workspaces except the optional `.specify/feature.json` pointer.

- [ ] T001 Verify prerequisite gates for Feature 044 in `specs/044-passive-runtime-lifecycle-trace-instrumentation/plan.md`, including branch identity, main/origin parity, Feature 043 predecessor SHA diff emptiness, local-only `.specify/feature.json` handling, and explicit rejection of `AGENTS.md` dirtiness for report regeneration
- [ ] T002 Verify prior feature gate artifacts for Features 037, 038, 039, 040, 041, 042, and 043 in `artifacts/analysis/`, including the committed report paths referenced by the plan and quickstart
- [ ] T003 Create the passive trace module scaffolding in `src/environment/lifecycle_trace.py` and the analysis package scaffolding in `src/analysis/passive_runtime_lifecycle_trace_instrumentation/`
- [ ] T004 Create the Feature 044 report artifact directory in `artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/`

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core trace schema, recorder, and report infrastructure that all user stories depend on.

**Checkpoint**: Foundation ready - trace events can be recorded passively and surfaced without changing runtime outcomes.

- [ ] T005 Define the passive `LifecycleTraceEvent` schema and JSON-safe serialization in `src/environment/lifecycle_trace.py`
- [ ] T006 Define the passive `LifecycleTraceRecorder` with enabled/disabled mode and no runtime-state mutation in `src/environment/lifecycle_trace.py`
- [ ] T007 Define trace-aware configuration/flag wiring in `src/environment/lifecycle_trace.py` or the smallest existing environment config surface that can carry the toggle without semantic changes
- [ ] T008 Create the analysis package entrypoint and report writer scaffolding in `src/analysis/passive_runtime_lifecycle_trace_instrumentation/__main__.py`, `runner.py`, and `report.py`
- [ ] T009 Define the report schema payload for support-vs-observation tracking, sample cleanliness, and deduplicated behavior-equivalence checks in `src/analysis/passive_runtime_lifecycle_trace_instrumentation/report.py`

## Phase 3: User Story 1 - Expose lifecycle evidence for diagnosis (Priority: P1) 🎯 MVP

**Goal**: Expose passive trace evidence for paper-default runs so downstream diagnosis can distinguish generated/admitted/transmission/execution/completion/drop/reward/pending states without changing simulator behavior.

**Independent Test**: Run a paper-default `T = 110` probe with tracing enabled and confirm the trace includes lifecycle breakpoints while the same run with tracing disabled remains behaviorally identical.

### Tests for User Story 1

- [ ] T010 [P] [US1] Add schema tests for required lifecycle trace event fields and event-type coverage in `tests/unit/test_lifecycle_trace_schema.py`
- [ ] T011 [P] [US1] Add recorder tests proving tracing is disabled by default and emits JSON-safe events in `tests/unit/test_lifecycle_trace_schema.py`
- [ ] T012 [P] [US1] Add behavior-equivalence tests proving tracing changes only metadata and not rewards, finalized tasks, flags, queue load, or action selection in `tests/unit/test_lifecycle_trace_behavior_equivalence.py`
- [ ] T013 [US1] Add runtime integration tests proving execution progress is emitted without inferring completion and pending-at-horizon remains non-terminal in `tests/integration/test_passive_lifecycle_trace_runtime.py`

### Implementation for User Story 1

- [ ] T014 [US1] Wire passive task-generation and task-admission trace emission in `src/environment/gym_adapter.py` and `src/environment/lifecycle_trace.py`
- [ ] T015 [US1] Wire passive transmission-start and transmission-completion trace emission in `src/environment/gym_adapter.py` and `src/environment/lifecycle_trace.py`
- [ ] T016 [US1] Wire passive execution-start, execution-progress, and execution-completion trace emission in `src/environment/gym_adapter.py` and `src/environment/lifecycle_trace.py`
- [ ] T017 [US1] Wire passive deadline-reached, deadline-expired, task-completed, task-dropped, reward-emitted, and pending-at-horizon trace emission in `src/environment/gym_adapter.py` and `src/environment/lifecycle_trace.py`
- [ ] T018 [US1] Expose passive trace events through the existing environment `info` dict and analysis runner collection path in `src/environment/gym_adapter.py` and `src/analysis/passive_runtime_lifecycle_trace_instrumentation/runner.py`
- [ ] T019 [US1] Implement the paper-default `T = 110` trace runner for seeds `[0, 1, 2]` and strategies `environment_default_policy_probe`, `force_local_legal_probe`, `force_horizontal_legal_probe`, `force_vertical_legal_probe`, and `mixed_legal_round_robin_probe` in `src/analysis/passive_runtime_lifecycle_trace_instrumentation/runner.py`

**Checkpoint**: User Story 1 should now expose passive lifecycle evidence without changing runtime outcomes.

## Phase 4: User Story 2 - Preserve simulator behavior while tracing (Priority: P2)

**Goal**: Prove tracing is passive and that enabled-vs-disabled runs produce identical externally visible outcomes.

**Independent Test**: Compare the same paper-default run with tracing disabled and enabled and confirm externally visible behavior is unchanged.

### Tests for User Story 2

- [ ] T020 [P] [US2] Add report tests that reject non-paper-default sample values, require `task_completed_supported=true` even when not observed, and require `no_unrelated_dirty_files=true` when only the pointer is dirty in `tests/integration/test_passive_lifecycle_trace_report.py`
- [ ] T021 [P] [US2] Add report tests that reject duplicate behavior-equivalence check names and require the unique checks `same_rewards`, `same_finalized_tasks`, `same_terminal_flags`, `same_queue_load`, `same_action_sequence`, and `same_outcomes` in `tests/unit/test_lifecycle_trace_behavior_equivalence.py`
- [ ] T022 [P] [US2] Add scope-guard tests that reject committed paths outside the approved Feature 044 scope and reject `.specify/feature.json` being staged in `tests/integration/test_passive_lifecycle_trace_scope_guard.py`
- [ ] T023 [P] [US2] Add runtime contract tests that require `deadline_expired` on observed drop paths and `reward_emitted` after terminal completion or drop in `tests/integration/test_passive_lifecycle_trace_runtime.py`

### Implementation for User Story 2

- [ ] T024 [US2] Implement behavior-equivalence aggregation and deduplication in `src/analysis/passive_runtime_lifecycle_trace_instrumentation/runner.py`
- [ ] T025 [US2] Implement paper-default sample gating and support-vs-observation classification in `src/analysis/passive_runtime_lifecycle_trace_instrumentation/report.py`
- [ ] T026 [US2] Implement report cleanliness checks that accept only an optional local `.specify/feature.json` pointer and explicitly reject unrelated dirty paths, including `AGENTS.md`, in `src/analysis/passive_runtime_lifecycle_trace_instrumentation/report.py`
- [ ] T027 [US2] Implement report ordering evidence for drop and completion paths in `src/analysis/passive_runtime_lifecycle_trace_instrumentation/report.py`

**Checkpoint**: User Story 2 should now prove tracing does not alter runtime behavior and that the report logic is strict about sample provenance and dirty-workspace state.

## Phase 5: User Story 3 - Produce readiness report (Priority: P3)

**Goal**: Generate a diagnosis-ready report that summarizes trace coverage, support-vs-observation state, and readiness for downstream Feature 043 diagnosis.

**Independent Test**: Generate the report from a traced paper-default run and confirm it summarizes coverage, trace sources, ordering evidence, sample provenance, and readiness status.

### Tests for User Story 3

- [ ] T028 [P] [US3] Add integration tests that verify the generated report writes JSON and Markdown artifacts to `artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/` in `tests/integration/test_passive_lifecycle_trace_report.py`
- [ ] T029 [P] [US3] Add integration tests that verify paper-default sample bounds (`T = 110`, `timeout_slots = 20`, task sizes `[2.0, 5.0]`, density `0.297`, capacities `0.5/0.5/3.0`, rates `30/10 Mbps`) in `tests/integration/test_passive_lifecycle_trace_report.py`
- [ ] T030 [US3] Add integration tests that verify `deadline_expired` ordering is present on observed drop paths and that `task_completed` support is retained even when not observed in `tests/integration/test_passive_lifecycle_trace_report.py`
- [ ] T031 [US3] Add report schema tests that require all audit flags to be true and reject false drift flags in `tests/unit/test_lifecycle_trace_schema.py`

### Implementation for User Story 3

- [ ] T032 [US3] Implement the trace coverage summary and lifecycle readiness report payload in `src/analysis/passive_runtime_lifecycle_trace_instrumentation/report.py`
- [ ] T033 [US3] Implement the passive analysis report runner that writes `artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/lifecycle-trace-instrumentation-report.json` and `.md` in `src/analysis/passive_runtime_lifecycle_trace_instrumentation/runner.py`
- [ ] T034 [US3] Implement the report serializer and Markdown writer in `src/analysis/passive_runtime_lifecycle_trace_instrumentation/report.py`

**Checkpoint**: User Story 3 should now generate a diagnosis-ready report with the correct sample provenance and support-vs-observation semantics.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, scope protection, and documentation alignment.

- [ ] T035 Restore or stash `AGENTS.md` before report regeneration, do not commit `AGENTS.md`, stop immediately if it remains dirty, forbid report generation while `AGENTS.md` is dirty, and require the final report to omit `AGENTS.md` from `dirty_paths` and all cleanliness details
- [ ] T036 Update `specs/044-passive-runtime-lifecycle-trace-instrumentation/quickstart.md` so the validation command exactly matches the approved Feature 044 regression set and excludes pointer-sensitive older Feature 042 report tests
- [ ] T037 Update `specs/044-passive-runtime-lifecycle-trace-instrumentation/plan.md` and `specs/044-passive-runtime-lifecycle-trace-instrumentation/data-model.md` if needed to keep the support-vs-observation model and cleanliness gate explicit
- [ ] T038 Add the dedicated three-way event-status report test in `tests/integration/test_passive_lifecycle_trace_report.py` to assert `event_type_supported`, `event_type_observed`, and `event_type_missing_from_instrumentation` are distinct, to require `task_completed_supported=true` even when `task_completed_observed=false`, to require `deadline_expired_supported=true`, to require drop-path `deadline_expired` observation whenever `task_dropped` is observed, and to fail if `event_type_missing_from_instrumentation` incorrectly includes `task_completed` or `deadline_expired` in an observed drop path
- [ ] T039 Regenerate `artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/lifecycle-trace-instrumentation-report.json` and `artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/lifecycle-trace-instrumentation-report.md`
- [ ] T040 Re-run the approved validation command from `specs/044-passive-runtime-lifecycle-trace-instrumentation/quickstart.md` and confirm no simulator semantic drift in `tests/integration/test_passive_lifecycle_trace_scope_guard.py`

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 and Foundational phase completion
- **User Story 3 (Phase 5)**: Depends on User Story 2 and Foundational phase completion
- **Polish (Phase 6)**: Depends on the desired user stories and report regeneration being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - no dependencies on other stories
- **User Story 2 (P2)**: Can start after User Story 1 is ready enough to validate behavior equivalence and report strictness
- **User Story 3 (P3)**: Can start after the report logic and scope guard rules are in place

### Within Each User Story

- Tests MUST be written and fail before implementation for the story-specific validations.
- Passive trace schema comes before recorder behavior.
- Recorder and runtime wiring come before report aggregation.
- Report aggregation comes before report regeneration.
- Scope guard rules come before the final validation pass.

## Parallel Opportunities

- T010 and T011 can proceed in parallel because they write different unit test files.
- T020, T021, T022, and T023 can proceed in parallel after the foundational work because they target different test files or distinct validations.
- T028, T029, T030, and T031 can proceed in parallel after the report payload exists because they target different report/schema checks.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. STOP and validate the passive trace evidence path independently

### Incremental Delivery

1. Complete Setup + Foundational → passive trace infrastructure is ready
2. Add User Story 1 → trace evidence exists without behavior drift
3. Add User Story 2 → prove behavior equivalence and strict sample gating
4. Add User Story 3 → generate the readiness report and artifacts
5. Finish with cleanup, quickstart alignment, and the approved validation command

## Validation Command

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_lifecycle_trace_schema \
  tests.unit.test_lifecycle_trace_behavior_equivalence \
  tests.integration.test_passive_lifecycle_trace_runtime \
  tests.integration.test_passive_lifecycle_trace_report \
  tests.integration.test_passive_lifecycle_trace_scope_guard \
  tests.unit.test_task_completion_formula_audit \
  tests.unit.test_task_completion_lifecycle_schema \
  tests.unit.test_paper_default_terminal_exposure_config \
  tests.unit.test_smoke_training_contract \
  tests.integration.test_smoke_training_report \
  tests.unit.test_paper_hoodie_network_config \
  tests.unit.test_paper_hoodie_network_shapes \
  tests.integration.test_paper_hoodie_network_report \
  tests.unit.test_training_foundation_contract \
  tests.integration.test_training_foundation_contract_report \
  tests.integration.test_deadline_timeout_off_by_one_audit \
  tests.integration.test_execution_time_flow \
  tests.integration.test_transmission_delay_runtime_wiring \
  tests.integration.test_public_cloud_capacity_sharing_flow
```
