# Tasks: Task Completion Lifecycle and Formula Audit

## Phase 1: Setup

- [ ] T001 Verify prerequisite gates for Feature 043 in `specs/043-task-completion-lifecycle-formula-audit/plan.md`, including branch identity, main/origin parity, Feature 042 predecessor SHA diff emptiness, local-only `.specify/feature.json` pointer handling, and no unrelated dirty files
- [ ] T002 Verify prior feature gate artifacts for Features 037, 038, 039, 040, 041, and 042 in `src/analysis/` and `artifacts/analysis/`, including the committed report paths referenced by the plan

## Phase 2: Foundational

- [ ] T003 Define `CompletionLifecycleAuditConfig` and `CompletionLifecycleAuditReport` schemas in `src/analysis/task_completion_lifecycle_formula_audit/config.py` and `src/analysis/task_completion_lifecycle_formula_audit/report.py`
- [ ] T004 Define `FormulaAuditCalculator` and `ExpectedCompletionEstimate` helpers in `src/analysis/task_completion_lifecycle_formula_audit/formula.py`
- [ ] T005 Define `LifecycleTraceCounters` and breakpoint classification enums/constants in `src/analysis/task_completion_lifecycle_formula_audit/model.py`
- [ ] T006 Create the analysis package entrypoint and artifact writer in `src/analysis/task_completion_lifecycle_formula_audit/__main__.py` and `src/analysis/task_completion_lifecycle_formula_audit/runner.py`

## Phase 3: User Story 1 - Explain zero completions [US1]

**Goal**: Produce a diagnostic lifecycle audit that explains why paper-default `T = 110` probes show reward-bearing terminal drops but no completions.

**Independent Test**: Run the audit on the existing probe outputs and confirm it classifies the zero-completion case without changing runtime behavior.

- [ ] T007 [US1] Implement paper-default runtime and formula inputs for `T = 110`, `timeout_slots = 20`, `arrival_probability = 0.5`, `node_count = 20`, and the approved Figure 7 topology in `src/analysis/task_completion_lifecycle_formula_audit/config.py`
- [ ] T008 [P] [US1] Implement hand-calculation logic for task cycles and expected compute/transmission slot estimates in `src/analysis/task_completion_lifecycle_formula_audit/formula.py`
- [ ] T009 [US1] Implement deterministic example calculations for 2 Mbits and 5 Mbits in `src/analysis/task_completion_lifecycle_formula_audit/formula.py` and document the results in `specs/043-task-completion-lifecycle-formula-audit/research.md`
- [ ] T010 [US1] Implement passive lifecycle trace extraction from existing runtime outputs only in `src/analysis/task_completion_lifecycle_formula_audit/runner.py`
- [ ] T011 [US1] Implement zero-completion classification logic in `src/analysis/task_completion_lifecycle_formula_audit/runner.py` for queue pressure, counter bug, runtime lifecycle bug, formula/unit mismatch, and insufficient metadata
- [ ] T012 [US1] Implement the lifecycle audit report payload and JSON/Markdown writers in `src/analysis/task_completion_lifecycle_formula_audit/report.py`

## Phase 4: User Story 2 - Verify formula expectations [US2]

**Goal**: Expose hand-calculated expectations for local, horizontal, cloud, and mixed task paths so observed behavior can be compared to paper-derived formulas.

**Independent Test**: Validate the expected compute/transmission slot outputs against the paper-default values and confirm the calculations are deterministic.

- [ ] T013 [US2] Encode expected local, public, and cloud compute slot formulas in `src/analysis/task_completion_lifecycle_formula_audit/formula.py`
- [ ] T014 [P] [US2] Encode horizontal and vertical/cloud transmission slot formulas using `R_H = 30 Mbps` and `R_V = 10 Mbps` in `src/analysis/task_completion_lifecycle_formula_audit/formula.py`
- [ ] T015 [US2] Add lifecycle counters for generated, admitted, transmission, execution, completion, drop, pending, reward, and terminal events in `src/analysis/task_completion_lifecycle_formula_audit/model.py`
- [ ] T016 [US2] Aggregate per-strategy lifecycle traces into report-ready results in `src/analysis/task_completion_lifecycle_formula_audit/runner.py`

## Phase 5: User Story 3 - Classify the breakpoint [US3]

**Goal**: Classify the zero-completion cause honestly and identify the next feature path.

**Independent Test**: Inspect the report and confirm it emits a single evidence-backed classification or an inconclusive verdict with a recommended next feature.

- [ ] T017 [US3] Implement evidence-backed lifecycle breakpoint classification in `src/analysis/task_completion_lifecycle_formula_audit/runner.py`
- [ ] T018 [P] [US3] Implement report fields for diagnosis, suspected root causes, lifecycle breakpoint summary, and recommended next feature in `src/analysis/task_completion_lifecycle_formula_audit/report.py`
- [ ] T019 [US3] Add scope guard tests that reject runtime mutation, training, optimizer, replay training, target update, reward timing changes, and paper reproduction claims in `tests/integration/test_task_completion_lifecycle_scope_guard.py`
- [ ] T020 [US3] Add report schema validation tests that require all audit flags to be true in `tests/unit/test_task_completion_lifecycle_schema.py`

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T021 [P] Add unit tests for formula examples, slot expectations, and pending-at-horizon behavior in `tests/unit/test_task_completion_formula_audit.py`
- [ ] T022 [P] Add integration tests for the audit runner and report generation in `tests/integration/test_task_completion_lifecycle_audit.py` and `tests/integration/test_task_completion_lifecycle_report.py`
- [ ] T023 Update `specs/043-task-completion-lifecycle-formula-audit/quickstart.md` so the validation command exactly matches the approved Feature 043 regression set, including the relevant 032-035 runtime repair regressions and the existing 036/038/039/040/042 checks
- [ ] T024 Document the missing `tests.integration.test_feature_032_runtime_assumption_contract_not_changed` module as absent and point to the closest existing regression in `specs/043-task-completion-lifecycle-formula-audit/quickstart.md` and `specs/043-task-completion-lifecycle-formula-audit/tasks.md`
- [ ] T025 Update `AGENTS.md` feature reference text if needed so it points at `specs/043-task-completion-lifecycle-formula-audit/plan.md` and `specs/043-task-completion-lifecycle-formula-audit/spec.md`

## Dependencies

- T001-T002 must complete before all design and implementation tasks.
- T003-T006 depend on T001-T002.
- T007-T012 depend on T003-T006.
- T013-T016 depend on T004-T012.
- T017-T020 depend on T010-T016.
- T021-T025 depend on T012-T020.

## Parallel Execution Examples

- T008 and T009 can proceed in parallel after T007.
- T014 can proceed in parallel with T013.
- T018 can proceed in parallel with T017.
- T021 and T022 can proceed in parallel after the core runner and report design are in place.
- T023 and T024 can be completed after the validation command is finalized.

## Implementation Strategy

1. Deliver the audit config, formula math, and lifecycle trace model first.
2. Add passive trace extraction and breakpoint classification next.
3. Write the report schema and tests that enforce the diagnostic-only contract.
4. Finish with the quickstart and agent-context documentation updates.

## MVP Scope

- User Story 1 only: explain zero completions with a deterministic lifecycle audit and hand-calculated formula expectations.

## Validation Command

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_task_completion_formula_audit \
  tests.unit.test_task_completion_lifecycle_schema \
  tests.integration.test_task_completion_lifecycle_audit \
  tests.integration.test_task_completion_lifecycle_report \
  tests.integration.test_task_completion_lifecycle_scope_guard \
  tests.integration.test_paper_default_terminal_exposure_report \
  tests.unit.test_paper_default_terminal_exposure_schema \
  tests.unit.test_paper_default_terminal_exposure_config \
  tests.integration.test_runtime_adoption_scope_guard \
  tests.integration.test_runtime_adoption_report \
  tests.integration.test_execution_time_flow \
  tests.integration.test_evaluation_runner \
  tests.integration.test_transmission_delay_runtime_wiring \
  tests.unit.test_public_cloud_capacity_sharing \
  tests.integration.test_public_cloud_capacity_sharing_flow \
  tests.integration.test_deadline_timeout_off_by_one_audit \
  tests.unit.test_paper_hoodie_network_config \
  tests.unit.test_paper_hoodie_network_shapes \
  tests.integration.test_paper_hoodie_network_report \
  tests.unit.test_training_foundation_contract \
  tests.integration.test_training_foundation_contract_report \
  tests.integration.test_deadline_timeout_off_by_one_report
```
