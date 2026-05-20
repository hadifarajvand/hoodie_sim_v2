# Tasks: Passive Runtime Lifecycle Trace Instrumentation

## Phase 1: Setup

- [X] T001 Verify prerequisite gates for Feature 044 in `specs/044-passive-runtime-lifecycle-trace-instrumentation/plan.md`, including branch identity, main/origin parity, Feature 043 predecessor SHA diff emptiness, local-only `.specify/feature.json` pointer handling, and no unrelated dirty files
- [X] T002 Verify prior feature gate artifacts for Features 037, 038, 039, 040, 041, 042, and 043 in `src/analysis/` and `artifacts/analysis/`, including the committed report paths referenced by the plan

## Phase 2: Foundational

- [X] T003 Define the passive lifecycle trace event schema in `src/environment/lifecycle_trace.py` with the required fields and JSON-safe serialization
- [X] T004 Define the passive lifecycle trace recorder in `src/environment/lifecycle_trace.py` with enabled/disabled mode and no runtime-state mutation
- [X] T005 Define trace-aware configuration and flag wiring in `src/environment/lifecycle_trace.py` or the smallest existing environment config surface that can carry the toggle without semantic changes
- [X] T006 Create the analysis package entrypoint and report writer in `src/analysis/passive_runtime_lifecycle_trace_instrumentation/__main__.py` and `src/analysis/passive_runtime_lifecycle_trace_instrumentation/runner.py`

## Phase 3: User Story 1 - Expose lifecycle evidence [US1]

**Goal**: Expose enough passive lifecycle evidence to distinguish completion, drop, execution-progress, and deadline ordering without changing simulator behavior.

**Independent Test**: Run a paper-default `T = 110` probe with tracing enabled and confirm the trace contains the required lifecycle breakpoints while the same run with tracing disabled remains behaviorally identical.

- [X] T007 [US1] Implement passive task-generation and task-admission trace emission in `src/environment/lifecycle_trace.py` and the minimal calling sites in `src/environment/`
- [X] T008 [US1] Implement passive transmission-start and transmission-completion trace emission in `src/environment/lifecycle_trace.py` and the minimal calling sites in `src/environment/`
- [X] T009 [US1] Implement passive execution-start, execution-progress, and execution-completion trace emission in `src/environment/lifecycle_trace.py` and the minimal calling sites in `src/environment/`
- [X] T010 [US1] Implement passive deadline-reached, deadline-expired, task-completed, task-dropped, reward-emitted, and pending-at-horizon trace emission in `src/environment/lifecycle_trace.py` and the minimal calling sites in `src/environment/`
- [X] T011 [US1] Implement passive trace exposure through the existing environment `info` dict and analysis runner collection path in `src/environment/` and `src/analysis/passive_runtime_lifecycle_trace_instrumentation/runner.py`
- [X] T012 [US1] Implement the paper-default `T = 110` trace runner for seeds `[0, 1, 2]` and strategies `environment_default_policy_probe`, `force_local_legal_probe`, `force_horizontal_legal_probe`, `force_vertical_legal_probe`, and `mixed_legal_round_robin_probe` in `src/analysis/passive_runtime_lifecycle_trace_instrumentation/runner.py`

## Phase 4: User Story 2 - Preserve simulator behavior [US2]

**Goal**: Prove that tracing is passive and does not alter runtime decisions, rewards, or final outcomes.

**Independent Test**: Compare the same paper-default run with tracing disabled and enabled and confirm externally visible behavior is unchanged.

- [X] T013 [US2] Implement behavior-equivalence collection for disabled-vs-enabled tracing runs in `src/analysis/passive_runtime_lifecycle_trace_instrumentation/runner.py`
- [X] T014 [US2] Implement disabled-by-default trace configuration assertions in `tests/unit/test_lifecycle_trace_behavior_equivalence.py`
- [X] T015 [US2] Implement trace JSON-safe serialization and exact schema assertions in `tests/unit/test_lifecycle_trace_schema.py`
- [X] T016 [US2] Implement equivalence tests proving tracing does not change rewards, finalized tasks, terminal/truncated flags, queue load, legal action selection, or outcomes in `tests/unit/test_lifecycle_trace_behavior_equivalence.py`

## Phase 5: User Story 3 - Produce readiness report [US3]

**Goal**: Generate a diagnosis-ready report that states whether the trace is sufficient to explain the Feature 043 completion gap.

**Independent Test**: Generate the report from a traced paper-default run and confirm it summarizes coverage, source components, ordering evidence, and readiness status.

- [X] T017 [US3] Implement the trace coverage summary and lifecycle readiness report payload in `src/analysis/passive_runtime_lifecycle_trace_instrumentation/report.py`
- [X] T018 [US3] Implement the report writer for JSON and Markdown artifacts in `src/analysis/passive_runtime_lifecycle_trace_instrumentation/report.py`
- [X] T019 [US3] Implement the passive analysis report runner that writes `artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/lifecycle-trace-instrumentation-report.json` and `.md` in `src/analysis/passive_runtime_lifecycle_trace_instrumentation/runner.py`
- [X] T020 [US3] Implement the integration report tests for trace coverage, readiness, and artifact generation in `tests/integration/test_passive_lifecycle_trace_report.py`

## Phase 6: Scope Guard & Cross-Cutting Concerns

- [X] T021 [US3] Implement the scope guard test that rejects all committed paths outside passive trace instrumentation in `tests/integration/test_passive_lifecycle_trace_scope_guard.py`
- [X] T022 [US3] Implement the runtime trace integration test that proves ordering evidence includes execution progress, completion/drop separation, and deadline ordering in `tests/integration/test_passive_lifecycle_trace_runtime.py`
- [X] T023 [US3] Implement the no-training, no-optimizer, no-replay-training, no-target-update, no-policy-drift, and no-reward-timing-drift checks in `tests/integration/test_passive_lifecycle_trace_scope_guard.py`
- [X] T024 [US3] Implement the report schema validation tests that require all audit flags to be true in `tests/unit/test_lifecycle_trace_schema.py`
- [X] T025 Update `specs/044-passive-runtime-lifecycle-trace-instrumentation/quickstart.md` so the validation command exactly matches the approved Feature 044 regression set and excludes pointer-sensitive older Feature 042 report tests
- [X] T026 Update `specs/044-passive-runtime-lifecycle-trace-instrumentation/plan.md` and `specs/044-passive-runtime-lifecycle-trace-instrumentation/research.md` if needed so the trace toggle, event ordering, and passive-only boundaries remain explicit

## Dependencies

- T001-T002 must complete before all design and implementation tasks.
- T003-T006 depend on T001-T002.
- T007-T012 depend on T003-T006.
- T013-T016 depend on T007-T012.
- T017-T020 depend on T013-T016.
- T021-T026 depend on T017-T020.

## Parallel Execution Examples

- T014 and T015 can proceed after T013 because they write different test files.
- T017 and T018 can proceed sequentially in the same report module; no parallelism.
- T023 and T024 can proceed in parallel after the scope guard and report schema are in place because they write different test files.

## Implementation Strategy

1. Add the trace schema and recorder first, with disabled tracing remaining behaviorally inert.
2. Wire passive emission at lifecycle breakpoints without changing runtime semantics.
3. Prove behavior equivalence under disabled vs enabled tracing.
4. Add the diagnosis report and scope guard.
5. Finish with the corrected validation command and doc updates.

## MVP Scope

- User Story 1 only: expose passive lifecycle evidence without changing simulator behavior.

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
