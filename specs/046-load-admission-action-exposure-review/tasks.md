# Tasks: Load, Admission, and Action-Exposure Review

## Phase 1: Setup

**Purpose**: Establish prerequisite gates, prior-feature artifact checks, and the analysis package/artifact locations before any review logic is built.  
**Independent Test**: Branch, predecessor, and workspace cleanliness gates can be verified without touching analysis logic.

- [X] T001 Verify prerequisite gates for Feature 046 in `specs/046-load-admission-action-exposure-review/plan.md`, including branch identity, branch != `main`, `main == origin/main`, `main == 045-completion-root-cause-diagnosis-complete^{}`, empty diff between `045-completion-root-cause-diagnosis-complete^{}` and `main`, `.specify/feature.json` local-only handling, AGENTS.md cleanliness before report regeneration, and no unrelated dirty files
- [X] T002 Verify prior feature gate artifacts for Features 037, 038, 039, 040, 041, 042, 043, 044, and 045 in `artifacts/analysis/`, including the committed report paths referenced by the plan, quickstart, and report contract
- [X] T003 Create the passive review package scaffolding in `src/analysis/load_admission_action_exposure_review/` and the report artifact directory in `artifacts/analysis/load-admission-action-exposure-review/`
- [X] T004 Define the Feature 046 report contract and analysis entrypoint scaffolding in `src/analysis/load_admission_action_exposure_review/__main__.py`, `runner.py`, `model.py`, and `report.py`

## Phase 2: Foundational

**Purpose**: Build the shared configuration, ingestion, reconstruction, and metric containers required by all user stories.  
**Checkpoint**: Feature 046 can ingest passive traces and reconstruct load/admission/action evidence without changing runtime behavior or mixing evidence populations.

- [X] T005 Define `LoadAdmissionActionExposureConfig` in `src/analysis/load_admission_action_exposure_review/config.py` with `feature_id`, `episode_length`, `timeout_slots`, `node_count`, `arrival_probability`, `seeds`, `strategies`, `no_runtime_repair`, and `no_training`
- [X] T006 Define the shared passive ingestion contract in `src/analysis/load_admission_action_exposure_review/runner.py` for consuming Feature 044 traces and the Feature 045 report without mutating runtime state
- [X] T007 Define `LoadPressureMetrics` in `src/analysis/load_admission_action_exposure_review/model.py`
- [X] T008 Define `AdmissionSerializationMetrics` in `src/analysis/load_admission_action_exposure_review/model.py`
- [X] T009 Define `ActionExposureMetrics` in `src/analysis/load_admission_action_exposure_review/model.py`
- [X] T010 Define `QueuePressureMetrics` in `src/analysis/load_admission_action_exposure_review/model.py`
- [X] T011 Define `OffloadPathPressureMetrics` and `BudgetComparisonMetrics` in `src/analysis/load_admission_action_exposure_review/model.py`
- [X] T012 Define the `LoadAdmissionActionExposureReport` schema payload in `src/analysis/load_admission_action_exposure_review/report.py`
- [X] T013 Define evidence-population metadata fields in `src/analysis/load_admission_action_exposure_review/report.py` for `evidence_population_by_metric_group`, `sample_usage_policy`, `action_exposure_data_status`, `legal_action_exposure_evidence_source`, `metric_population_consistency_verified`, and `aggregate_metrics_not_sample_derived`
- [X] T014 Define the final-verdict evidence gate contract in `src/analysis/load_admission_action_exposure_review/report.py` so sample-only exposure, queue, and offload evidence cannot emit a non-inconclusive verdict

## Phase 3: User Story 1 - Explain whether weak completion is load-driven (Priority: P1) 🎯 MVP

**Goal**: Quantify whether the paper-default completion weakness is primarily explained by load pressure rather than a runtime fault.  
**Independent Test**: Run the review on full paper-default evidence and confirm the report quantifies load pressure using generated, admitted, terminal, completed, dropped, and pending counts and rates from the same evidence population.

### Tests for User Story 1

- [X] T015 [P] [US1] Add full-evidence guard tests that reject sample-only aggregate action exposure, queue pressure, offload pressure, per-strategy, per-action, and final-verdict metrics in `tests/unit/test_load_admission_action_exposure_schema.py`
- [X] T016 [P] [US1] Add population-consistency tests that fail when load metrics use full totals but action/queue/offload metrics use sample-only denominators without explicit incomparability handling in `tests/unit/test_load_admission_action_exposure_metrics.py`
- [X] T017 [P] [US1] Add report schema tests for the exact top-level fields, evidence-population fields, and verdict constraints in `tests/unit/test_load_admission_action_exposure_schema.py`
- [X] T018 [P] [US1] Add trace-ingestion tests that reject non-paper-default task size, density, deadline metadata, fake traces, and sample-only verdict inputs in `tests/unit/test_load_admission_action_exposure_schema.py`
- [X] T019 [P] [US1] Add load-pressure metrics tests for generated, admitted, terminal, completed, dropped, and pending counts and rates in `tests/unit/test_load_admission_action_exposure_metrics.py`
- [X] T020 [P] [US1] Add a guard test that verifies load-pressure verdicts cannot be emitted when exposure metrics are sample-only and incomparable in `tests/integration/test_load_admission_action_exposure_report.py`

### Implementation for User Story 1

- [X] T021 [US1] Implement Feature 044/045 passive trace ingestion in `src/analysis/load_admission_action_exposure_review/runner.py`
- [X] T022 [US1] Implement load pressure quantification in `src/analysis/load_admission_action_exposure_review/model.py` and `runner.py`
- [X] T023 [US1] Implement load-focused diagnosis routing and load-pressure explanation selection in `src/analysis/load_admission_action_exposure_review/report.py`

## Phase 4: User Story 2 - Separate admission serialization from action exposure (Priority: P2)

**Goal**: Distinguish same-slot backlog from action-selection bias so the report can tell whether the weakness comes from serialized admissions or underexplored action exposure.  
**Independent Test**: Confirm the report distinguishes same-slot generation/admission backlog, legal-but-unselected actions, and per-action completion/drop/pending rates, while treating missing legal-mask data as insufficient.

### Tests for User Story 2

- [X] T024 [P] [US2] Add legal-mask evidence tests that require trace-backed legal local/horizontal/vertical counts and reject fake zero exposure without an explicit evidence source in `tests/unit/test_load_admission_action_exposure_metrics.py`
- [X] T025 [P] [US2] Add report-field tests for `action_exposure_data_status`, `legal_action_exposure_evidence_source`, and `metric_population_consistency_verified` in `tests/unit/test_load_admission_action_exposure_schema.py`
- [X] T026 [P] [US2] Add metrics tests for same-slot generation, serialized admission lag, and delayed/expired tasks in `tests/unit/test_load_admission_action_exposure_metrics.py`
- [X] T027 [P] [US2] Add metrics tests for legal local/horizontal/vertical exposure versus selected action distribution in `tests/unit/test_load_admission_action_exposure_metrics.py`
- [X] T028 [P] [US2] Add integration tests that verify the report recommends `Feature 047 — Paper HOODIE Observation Vector`, `exposure-matrix review`, or `diagnosis_inconclusive_requires_deeper_exposure_matrix` according to evidence population availability in `tests/integration/test_load_admission_action_exposure_review.py`

### Implementation for User Story 2

- [X] T029 [US2] Implement admission serialization quantification in `src/analysis/load_admission_action_exposure_review/model.py` and `runner.py`
- [X] T030 [US2] Implement action exposure quantification in `src/analysis/load_admission_action_exposure_review/model.py` and `runner.py`
- [X] T031 [US2] Implement same-slot backlog, evidence-population metadata, and action-routing summaries in `src/analysis/load_admission_action_exposure_review/report.py`

## Phase 5: User Story 3 - Explain queue and offload pressure (Priority: P3)

**Goal**: Break down private, public, cloud, and offload-path pressure so the dominant completion weakness can be attributed to queueing, transmission, or execution budget consumption.  
**Independent Test**: Confirm the report separates queue pressure from offload-path pressure and compares representative task budgets against observed waiting, transmission, execution, and deadline behavior only when the same evidence population supports the aggregates.

### Tests for User Story 3

- [X] T032 [P] [US3] Add verdict-guard tests that force `diagnosis_inconclusive_requires_deeper_exposure_matrix` when exposure, queue, or offload metrics are sample-only in `tests/integration/test_load_admission_action_exposure_report.py`
- [X] T033 [P] [US3] Add report-population tests that verify every metric group declares its evidence population and marks sample-only aggregates as incomparable in `tests/integration/test_load_admission_action_exposure_scope_guard.py`
- [X] T034 [P] [US3] Add metrics tests for private/public/cloud queue pressure in `tests/unit/test_load_admission_action_exposure_metrics.py`
- [X] T035 [P] [US3] Add metrics tests for offload-path transmission, admission, and execution delays in `tests/unit/test_load_admission_action_exposure_metrics.py`
- [X] T036 [P] [US3] Add metrics tests for representative task budget comparisons in `tests/unit/test_load_admission_action_exposure_metrics.py`
- [X] T037 [P] [US3] Add integration tests that verify the report distinguishes queue pressure, offload-path pressure, mixed pressure, and inconclusive evidence in `tests/integration/test_load_admission_action_exposure_report.py`

### Implementation for User Story 3

- [X] T038 [US3] Implement queue pressure quantification in `src/analysis/load_admission_action_exposure_review/model.py` and `runner.py`
- [X] T039 [US3] Implement offload-path pressure quantification in `src/analysis/load_admission_action_exposure_review/model.py` and `runner.py`
- [X] T040 [US3] Implement representative budget comparison summaries in `src/analysis/load_admission_action_exposure_review/model.py` and `runner.py`
- [X] T041 [US3] Implement dominant pressure source ranking, evidence-population consistency checks, and next-feature recommendation routing in `src/analysis/load_admission_action_exposure_review/report.py`

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, scope protection, and documentation alignment.  
**Checkpoint**: The feature is ready for review with no runtime, training, or policy drift.

- [X] T042 Update `specs/046-load-admission-action-exposure-review/quickstart.md` so the validation command exactly matches the approved Feature 046 regression set and excludes pointer-sensitive older report tests
- [X] T043 Update `specs/046-load-admission-action-exposure-review/data-model.md` and `specs/046-load-admission-action-exposure-review/contracts/load-admission-action-exposure-report-schema.md` if needed to keep the diagnostic-only boundary, metric definitions, verdict routing, next-feature guidance, and evidence-population discipline explicit
- [X] T044 Check whether `AGENTS.md` is dirty, restore or stash it before report generation if needed, and stop immediately if it remains dirty; do not commit `AGENTS.md` or add it to `.gitignore`
- [X] T045 Validate report cleanliness before regeneration by enforcing that `.specify/feature.json` may only remain as a local active pointer, must not be staged, must not appear in `git diff --name-only main...HEAD`, `AGENTS.md` must not be staged or appear in `git diff --name-only main...HEAD`, any dirty path outside the active feature scope blocks report generation, `no_unrelated_dirty_files` must be `true`, and report validation must fail if `AGENTS.md` appears in dirty paths/details or any prerequisite/prior-feature gate is false
- [X] T046 [P] [US3] Add report consistency tests that fail if `final_verdict` and `recommended_next_feature` contradict each other, if sample-only exposure/queue/offload metrics are used for a final verdict, if action-exposure verdicts do not route to `Feature 047 — Paper HOODIE Observation Vector`, if mixed pressure verdicts do not route to `exposure-matrix review` before Feature 047, if load/admission/queue/offload verdicts route directly to runtime repair, or if `diagnosis_inconclusive_requires_deeper_exposure_matrix` does not route to `exposure-matrix review` in `tests/integration/test_load_admission_action_exposure_report.py`
- [X] T047 [P] [US3] Add report runtime-fault contradiction tests that fail if runtime repair is recommended without a verified contradiction against Feature 045 trace evidence, or if the report claims a contradiction without including `contradiction_type`, `evidence_count > 0`, `representative_task_ids`, `supporting_event_types`, `explanation`, and an explicit explanation of why the contradiction conflicts with Feature 045 in `tests/integration/test_load_admission_action_exposure_report.py`
- [X] T048 [P] [US3] Add scope-guard tests that explicitly prove `no_optimizer_step = true`, `no_replay_training = true`, `no_target_update_execution = true`, `no_curve_fitting = true`, `no_simulator_output_tuning = true`, `no_paper_reproduction_claim = true`, `no_training_started = true`, `no_runtime_repair_performed = true`, `no_dependency_drift = true`, `no_environment_contract_drift = true`, `no_policy_drift = true`, `no_reward_timing_change = true`, `no_timeout_contract_drift = true`, `no_capacity_contract_drift = true`, `no_transmission_contract_drift = true`, and `no_action_legality_drift = true` in the report payload and committed diff in `tests/integration/test_load_admission_action_exposure_scope_guard.py`
- [X] T049 [US3] Add committed-artifact validation for Feature 045 in `tests/integration/test_load_admission_action_exposure_report.py` that asserts `artifacts/analysis/completion-root-cause-diagnosis/completion-root-cause-report.json` exists and contains `feature_id = 045-completion-root-cause-diagnosis`, `final_verdict = root_cause_identified_configuration_or_load_explanation`, `recommended_next_feature = load/admission/action-exposure review`, `no_runtime_repair_performed = true`, `no_paper_reproduction_claim = true`, and `runtime_repair_verdict_guard = false` when present
- [X] T050 Re-run the approved validation command from `specs/046-load-admission-action-exposure-review/quickstart.md` and confirm no runtime behavior drift in `tests/integration/test_load_admission_action_exposure_scope_guard.py`
- [X] T051 Rerun `/speckit-analyze` after the task repair and before any implementation work resumes

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
- **User Story 2 (P2)**: Can start after User Story 1 is ready enough to validate action exposure and serialization findings
- **User Story 3 (P3)**: Can start after the report logic and scope guard rules are in place

### Within Each User Story

- Tests MUST be written and fail before implementation for the story-specific validations.
- Shared configuration and ingestion come before metrics.
- Metrics and reconstruction come before report aggregation.
- Report aggregation comes before report regeneration.
- Scope guard rules come before the final validation pass.

## Parallel Opportunities

- T015, T016, and T017 can proceed in parallel because they target different User Story 1 guard concerns.
- T024 and T025 can proceed in parallel after the foundational report schema exists because they target different User Story 2 evidence-population concerns.
- T032 and T033 can proceed in parallel after the queue/offload/budget models exist because they target different User Story 3 verdict and population guard concerns.
- T034, T035, and T036 can proceed in parallel after the queue/offload/budget models exist because they target different User Story 3 metric concerns.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. STOP and validate the passive load-pressure path independently

### Incremental Delivery

1. Complete Setup + Foundational → review infrastructure is ready
2. Add User Story 1 → load pressure diagnosis exists
3. Add User Story 2 → action exposure and admission serialization are separated
4. Add User Story 3 → queue and offload pressure are explained
5. Finish with cleanup, quickstart alignment, and the approved validation command

## Validation Command

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_load_admission_action_exposure_schema \
  tests.unit.test_load_admission_action_exposure_metrics \
  tests.integration.test_load_admission_action_exposure_review \
  tests.integration.test_load_admission_action_exposure_report \
  tests.integration.test_load_admission_action_exposure_scope_guard \
  tests.unit.test_completion_root_cause_schema \
  tests.unit.test_completion_root_cause_classifiers \
  tests.unit.test_lifecycle_trace_schema \
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
