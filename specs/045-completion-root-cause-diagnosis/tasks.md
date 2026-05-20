# Tasks: Completion Root-Cause Diagnosis Using Passive Lifecycle Traces

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish prerequisite gates, committed artifact checks, and the analysis package/report artifact locations before any diagnosis logic is built.

**Quality Gate**: Confirm the branch and prior-feature prerequisites are in place, and that the diagnostic feature stays isolated from runtime repair and training.

- [x] T001 Verify prerequisite gates for Feature 045 in `specs/045-completion-root-cause-diagnosis/plan.md`, including branch identity, main/origin parity, Feature 044 predecessor SHA diff emptiness, local-only `.specify/feature.json` handling, and no unrelated dirty files
- [x] T002 Verify prior feature gate artifacts for Features 037, 038, 039, 040, 041, 042, 043, and 044 in `artifacts/analysis/`, including the committed report paths referenced by the plan and quickstart
- [x] T003 Create the passive diagnosis package scaffolding in `src/analysis/completion_root_cause_diagnosis/` and the report artifact directory in `artifacts/analysis/completion-root-cause-diagnosis/`
- [x] T004 Define the Feature 045 report contract and analysis entrypoint scaffolding in `src/analysis/completion_root_cause_diagnosis/__main__.py`, `runner.py`, `model.py`, and `report.py`

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core configuration, trace ingestion, lifecycle reconstruction, and classifier infrastructure that all user stories depend on.

**Checkpoint**: Foundation ready - Feature 045 can consume passive traces from Feature 044 and reconstruct task lifecycles without changing runtime behavior.

- [x] T005 Define `CompletionRootCauseConfig` in `src/analysis/completion_root_cause_diagnosis/config.py` with `feature_id`, `episode_length`, `timeout_slots`, `node_count`, `arrival_probability`, `seeds`, `strategies`, `no_runtime_repair`, and `no_training`
- [x] T006 Define the `TaskLifecycleReconstructor` data model in `src/analysis/completion_root_cause_diagnosis/model.py` for task-level lifecycle reconstruction
- [x] T007 Define the `RootCauseEvaluation` and `RootCauseClassifier` data models in `src/analysis/completion_root_cause_diagnosis/model.py` for ranked evidence-backed diagnosis
- [x] T008 Define the `CompletionRootCauseReport` schema payload in `src/analysis/completion_root_cause_diagnosis/report.py`
- [x] T009 Define the analysis runner contract and report writer scaffolding in `src/analysis/completion_root_cause_diagnosis/runner.py`

## Phase 3: User Story 1 - Diagnose the completion bottleneck root cause (Priority: P1) 🎯 MVP

**Goal**: Produce an evidence-backed diagnosis for paper-default `T = 110` runs using passive lifecycle traces from Feature 044, and recommend the next feature type without repairing anything.

**Independent Test**: Run the diagnosis on paper-default traces and confirm the report classifies the dominant root cause or marks the evidence inconclusive with an explicit reason.

### Tests for User Story 1

- [x] T010 [P] [US1] Add schema tests for the exact report contract in `tests/unit/test_completion_root_cause_schema.py`
- [x] T011 [P] [US1] Add trace-ingestion tests that reject non-paper-default trace samples and fake events in `tests/unit/test_completion_root_cause_schema.py`
- [x] T012 [P] [US1] Add lifecycle reconstruction tests covering generated, admitted, transmission, execution, deadline, terminal outcome, and reward paths in `tests/unit/test_completion_root_cause_schema.py`
- [x] T013 [P] [US1] Add classifier tests for queue pressure, admission overload, action exposure bias, queue blockage, transmission mismatch, and formula unit mismatch in `tests/unit/test_completion_root_cause_classifiers.py`

### Implementation for User Story 1

- [x] T014 [US1] Implement paper-default trace ingestion from Feature 044 reports in `src/analysis/completion_root_cause_diagnosis/runner.py`
- [x] T015 [US1] Implement per-task lifecycle reconstruction in `src/analysis/completion_root_cause_diagnosis/model.py` and `runner.py`
- [x] T016 [US1] Implement root-cause classification for queue pressure, task-generation/admission overload, action exposure bias, local/private queue blockage, public/cloud queue blockage, and transmission-delay/admission mismatch in `src/analysis/completion_root_cause_diagnosis/model.py`
- [x] T017 [US1] Implement evidence aggregation, confidence scoring, and dominant-root-cause ranking in `src/analysis/completion_root_cause_diagnosis/model.py`
- [x] T018 [US1] Implement report generation for task-level lifecycle reconstruction and next-feature routing in `src/analysis/completion_root_cause_diagnosis/report.py`
- [x] T019 [US1] Wire the Feature 045 analysis entrypoint to emit JSON and Markdown artifacts in `src/analysis/completion_root_cause_diagnosis/__main__.py` and `runner.py`

**Checkpoint**: User Story 1 should now produce a passive diagnosis of completion bottlenecks without any runtime repair.

## Phase 4: User Story 2 - Explain whether completions are blocked by the system or by the load pattern (Priority: P2)

**Goal**: Separate load-driven causes from ordering, reward/counter, and formula issues so the diagnosis can clearly route follow-up work.

**Independent Test**: Confirm the report distinguishes the major root-cause classes and supports each classification with task-level evidence.

### Tests for User Story 2

- [x] T020 [P] [US2] Add classifier tests for execution-progress-before-deadline-expiry and deadline/drop ordering issues in `tests/unit/test_completion_root_cause_classifiers.py`
- [x] T021 [P] [US2] Add classifier tests for completion-emitted-but-reward-or-counter-path-wrong and no-completion-problem-detected in `tests/unit/test_completion_root_cause_classifiers.py`
- [x] T022 [P] [US2] Add classifier tests for inconclusive trace evidence and dominant-root-cause ranking in `tests/unit/test_completion_root_cause_classifiers.py`
- [x] T023 [P] [US2] Add integration tests that verify the diagnosis report recommends the correct next feature type without any runtime repair in `tests/integration/test_completion_root_cause_diagnosis.py`

### Implementation for User Story 2

- [x] T024 [US2] Implement task-level evidence summaries for queue wait time, task age over time, remaining cycles over time, and completion-before-deadline checks in `src/analysis/completion_root_cause_diagnosis/model.py`
- [x] T025 [US2] Implement per-action and per-queue root-cause summaries in `src/analysis/completion_root_cause_diagnosis/report.py`
- [x] T026 [US2] Implement formula-consistency, deadline-ordering, and reward-counter-path summaries in `src/analysis/completion_root_cause_diagnosis/report.py`
- [x] T027 [US2] Implement recommendation routing for Feature 046 versus observation-vector, exploration, loss-sequence, and load/configuration follow-up in `src/analysis/completion_root_cause_diagnosis/report.py`

**Checkpoint**: User Story 2 should now separate runtime bugs from load/configuration explanations and preserve the no-repair boundary.

## Phase 5: User Story 3 - Produce diagnosis-ready trace artifacts (Priority: P3)

**Goal**: Generate JSON and Markdown diagnosis artifacts that are readable, auditable, and aligned to the approved paper-default runtime scope.

**Independent Test**: Generate the report from paper-default traces and confirm it includes lifecycle reconstruction, ranked root causes, confidence values, and follow-up routing.

### Tests for User Story 3

- [x] T028 [P] [US3] Add integration tests that verify JSON and Markdown report artifacts are written to `artifacts/analysis/completion-root-cause-diagnosis/` in `tests/integration/test_completion_root_cause_report.py`
- [x] T029 [P] [US3] Add integration tests that verify the report uses paper-default `T = 110`, seeds `[0, 1, 2]`, and the approved Feature 044 strategy set in `tests/integration/test_completion_root_cause_report.py`
- [x] T030 [P] [US3] Add integration tests that verify multiple root causes can be ranked and confidence values are low/medium/high in `tests/integration/test_completion_root_cause_report.py`
- [x] T031 [P] [US3] Add scope-guard tests that reject runtime repair, environment mutation, policy mutation, dependency changes, training, and fake trace evidence in `tests/integration/test_completion_root_cause_scope_guard.py`

### Implementation for User Story 3

- [x] T032 [US3] Implement the report writer that emits JSON and Markdown artifacts in `src/analysis/completion_root_cause_diagnosis/report.py`
- [x] T033 [US3] Implement the diagnosis runner that coordinates passive trace ingestion, reconstruction, classification, and reporting in `src/analysis/completion_root_cause_diagnosis/runner.py`
- [x] T034 [US3] Implement the report schema payload for feature metadata, dominance ranking, and next-feature routing in `src/analysis/completion_root_cause_diagnosis/report.py`

**Checkpoint**: User Story 3 should now produce diagnosis-ready artifacts for review and downstream planning.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, scope protection, and documentation alignment.

- [x] T035 Update `specs/045-completion-root-cause-diagnosis/quickstart.md` so the validation command exactly matches the approved Feature 045 regression set and excludes pointer-sensitive older Feature 044 report tests
- [x] T036 Update `specs/045-completion-root-cause-diagnosis/plan.md` and `specs/045-completion-root-cause-diagnosis/data-model.md` if needed to keep the diagnostic-only boundary, confidence model, and next-feature routing explicit
- [x] T037 Check whether `AGENTS.md` is dirty, restore or stash it before report generation if needed, and stop immediately if it remains dirty; do not commit `AGENTS.md` or add it to `.gitignore`
- [x] T038 Validate report cleanliness before regeneration by enforcing that `.specify/feature.json` may only remain as a local active pointer, must not be staged, must not appear in `git diff --name-only main...HEAD`, `AGENTS.md` must not be staged or appear in `git diff --name-only main...HEAD`, any dirty path outside the active feature scope blocks report generation, `no_unrelated_dirty_files` must be `true`, and report validation must fail if `AGENTS.md` appears in dirty paths/details or any prerequisite/prior-feature gate is false
- [x] T039 Regenerate `artifacts/analysis/completion-root-cause-diagnosis/completion-root-cause-report.json` and `artifacts/analysis/completion-root-cause-diagnosis/completion-root-cause-report.md`
- [x] T040 Re-run the approved validation command from `specs/045-completion-root-cause-diagnosis/quickstart.md` and confirm no runtime behavior drift in `tests/integration/test_completion_root_cause_scope_guard.py`

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
- **User Story 2 (P2)**: Can start after User Story 1 is ready enough to validate ranking and routing
- **User Story 3 (P3)**: Can start after the report logic and scope guard rules are in place

### Within Each User Story

- Tests MUST be written and fail before implementation for the story-specific validations.
- Configuration and model work come before classifiers.
- Classifiers and reconstruction come before report aggregation.
- Report aggregation comes before report regeneration.
- Scope guard rules come before the final validation pass.

## Parallel Opportunities

- T010, T011, T012, and T013 can proceed in parallel because they target different test concerns.
- T020, T021, T022, and T023 can proceed in parallel after the foundational work because they target different classifier and integration concerns.
- T028, T029, T030, and T031 can proceed in parallel after the report contract exists because they target different report and scope checks.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. STOP and validate the passive diagnosis path independently

### Incremental Delivery

1. Complete Setup + Foundational → diagnosis infrastructure is ready
2. Add User Story 1 → passive completion diagnosis exists
3. Add User Story 2 → dominant causes and routing are evidence-backed
4. Add User Story 3 → generate the diagnosis report and artifacts
5. Finish with cleanup, quickstart alignment, and the approved validation command

## Validation Command

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_completion_root_cause_schema \
  tests.unit.test_completion_root_cause_classifiers \
  tests.integration.test_completion_root_cause_diagnosis \
  tests.integration.test_completion_root_cause_report \
  tests.integration.test_completion_root_cause_scope_guard \
  tests.unit.test_lifecycle_trace_schema \
  tests.integration.test_passive_lifecycle_trace_report \
  tests.unit.test_task_completion_formula_audit \
  tests.unit.test_task_completion_lifecycle_schema \
  tests.unit.test_paper_default_terminal_exposure_config \
  tests.unit.test_smoke_training_contract \
  tests.unit.test_paper_hoodie_network_config \
  tests.unit.test_paper_hoodie_network_shapes \
  tests.unit.test_training_foundation_contract \
  tests.integration.test_deadline_timeout_off_by_one_audit \
  tests.integration.test_execution_time_flow \
  tests.integration.test_transmission_delay_runtime_wiring \
  tests.integration.test_public_cloud_capacity_sharing_flow
```
