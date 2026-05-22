# Tasks: Load, Admission, and Action-Exposure Review

## Phase 1: Setup

**Purpose**: Establish prerequisite gates, prior-feature artifact checks, and the analysis package/artifact locations before any review logic is built.  
**Independent Test**: Branch, predecessor, and workspace cleanliness gates can be verified without touching analysis logic.

- [ ] T001 Verify prerequisite gates for Feature 046 in `specs/046-load-admission-action-exposure-review/plan.md`, including branch identity, branch != `main`, `main == origin/main`, `main == 045-completion-root-cause-diagnosis-complete^{}`, empty diff between `045-completion-root-cause-diagnosis-complete^{}` and `main`, `.specify/feature.json` local-only handling, AGENTS.md cleanliness before report regeneration, and no unrelated dirty files
- [ ] T002 Verify prior feature gate artifacts for Features 037, 038, 039, 040, 041, 042, 043, 044, and 045 in `artifacts/analysis/`, including the committed report paths referenced by the plan, quickstart, and report contract
- [ ] T003 Create the passive review package scaffolding in `src/analysis/load_admission_action_exposure_review/` and the report artifact directory in `artifacts/analysis/load-admission-action-exposure-review/`
- [ ] T004 Define the Feature 046 report contract and analysis entrypoint scaffolding in `src/analysis/load_admission_action_exposure_review/__main__.py`, `runner.py`, `model.py`, and `report.py`

## Phase 2: Foundational

**Purpose**: Build the shared configuration, ingestion, reconstruction, and metric containers required by all user stories.  
**Checkpoint**: Feature 046 can ingest passive traces and reconstruct load/admission/action evidence without changing runtime behavior.

- [ ] T005 Define `LoadAdmissionActionExposureConfig` in `src/analysis/load_admission_action_exposure_review/config.py` with `feature_id`, `episode_length`, `timeout_slots`, `node_count`, `arrival_probability`, `seeds`, `strategies`, `no_runtime_repair`, and `no_training`
- [ ] T006 Define the shared passive ingestion contract in `src/analysis/load_admission_action_exposure_review/runner.py` for consuming Feature 044 traces and the Feature 045 report without mutating runtime state
- [ ] T007 Define `LoadPressureMetrics` in `src/analysis/load_admission_action_exposure_review/model.py`
- [ ] T008 Define `AdmissionSerializationMetrics` in `src/analysis/load_admission_action_exposure_review/model.py`
- [ ] T009 Define `ActionExposureMetrics` in `src/analysis/load_admission_action_exposure_review/model.py`
- [ ] T010 Define `QueuePressureMetrics` in `src/analysis/load_admission_action_exposure_review/model.py`
- [ ] T011 Define `OffloadPathPressureMetrics` and `BudgetComparisonMetrics` in `src/analysis/load_admission_action_exposure_review/model.py`
- [ ] T012 Define the `LoadAdmissionActionExposureReport` schema payload in `src/analysis/load_admission_action_exposure_review/report.py`

## Phase 3: User Story 1 - Explain whether weak completion is load-driven (Priority: P1) 🎯 MVP

**Goal**: Quantify whether the paper-default completion weakness is primarily explained by load pressure rather than a runtime fault.  
**Independent Test**: Run the review on paper-default traces and confirm the report quantifies load pressure using generated, admitted, terminal, completed, dropped, and pending counts and rates.

### Tests for User Story 1

- [ ] T013 [P] [US1] Add report schema tests for the exact top-level fields and verdict constraints in `tests/unit/test_load_admission_action_exposure_schema.py`
- [ ] T014 [P] [US1] Add trace-ingestion tests that reject non-paper-default task size, density, deadline metadata, and fake traces in `tests/unit/test_load_admission_action_exposure_schema.py`
- [ ] T015 [P] [US1] Add load-pressure metrics tests for generated, admitted, terminal, completed, dropped, and pending counts and rates in `tests/unit/test_load_admission_action_exposure_metrics.py`

### Implementation for User Story 1

- [ ] T016 [US1] Implement Feature 044/045 passive trace ingestion in `src/analysis/load_admission_action_exposure_review/runner.py`
- [ ] T017 [US1] Implement load pressure quantification in `src/analysis/load_admission_action_exposure_review/model.py` and `runner.py`
- [ ] T018 [US1] Implement load-focused diagnosis routing and load-pressure explanation selection in `src/analysis/load_admission_action_exposure_review/report.py`

## Phase 4: User Story 2 - Separate admission serialization from action exposure (Priority: P2)

**Goal**: Distinguish same-slot backlog from action-selection bias so the report can tell whether the weakness comes from serialized admissions or underexplored action exposure.  
**Independent Test**: Confirm the report distinguishes same-slot generation/admission backlog, legal-but-unselected actions, and per-action completion/drop/pending rates.

### Tests for User Story 2

- [ ] T019 [P] [US2] Add metrics tests for same-slot generation, serialized admission lag, and delayed/expired tasks in `tests/unit/test_load_admission_action_exposure_metrics.py`
- [ ] T020 [P] [US2] Add metrics tests for legal local/horizontal/vertical exposure versus selected action distribution in `tests/unit/test_load_admission_action_exposure_metrics.py`
- [ ] T021 [P] [US2] Add integration tests that verify the report recommends `Feature 047 — Paper HOODIE Observation Vector` or `exposure-matrix review` when action exposure is dominant in `tests/integration/test_load_admission_action_exposure_review.py`

### Implementation for User Story 2

- [ ] T022 [US2] Implement admission serialization quantification in `src/analysis/load_admission_action_exposure_review/model.py` and `runner.py`
- [ ] T023 [US2] Implement action exposure quantification in `src/analysis/load_admission_action_exposure_review/model.py` and `runner.py`
- [ ] T024 [US2] Implement same-slot backlog and action-routing summaries in `src/analysis/load_admission_action_exposure_review/report.py`

## Phase 5: User Story 3 - Explain queue and offload pressure (Priority: P3)

**Goal**: Break down private, public, cloud, and offload-path pressure so the dominant completion weakness can be attributed to queueing, transmission, or execution budget consumption.  
**Independent Test**: Confirm the report separates queue pressure from offload-path pressure and compares representative task budgets against observed waiting, transmission, execution, and deadline behavior.

### Tests for User Story 3

- [ ] T025 [P] [US3] Add metrics tests for private/public/cloud queue pressure in `tests/unit/test_load_admission_action_exposure_metrics.py`
- [ ] T026 [P] [US3] Add metrics tests for offload-path transmission, admission, and execution delays in `tests/unit/test_load_admission_action_exposure_metrics.py`
- [ ] T027 [P] [US3] Add metrics tests for representative task budget comparisons in `tests/unit/test_load_admission_action_exposure_metrics.py`
- [ ] T028 [P] [US3] Add integration tests that verify the report distinguishes queue pressure, offload-path pressure, mixed pressure, and inconclusive evidence in `tests/integration/test_load_admission_action_exposure_report.py`

### Implementation for User Story 3

- [ ] T029 [US3] Implement queue pressure quantification in `src/analysis/load_admission_action_exposure_review/model.py` and `runner.py`
- [ ] T030 [US3] Implement offload-path pressure quantification in `src/analysis/load_admission_action_exposure_review/model.py` and `runner.py`
- [ ] T031 [US3] Implement representative budget comparison summaries in `src/analysis/load_admission_action_exposure_review/model.py` and `runner.py`
- [ ] T032 [US3] Implement dominant pressure source ranking and next-feature recommendation routing in `src/analysis/load_admission_action_exposure_review/report.py`

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, scope protection, and documentation alignment.  
**Checkpoint**: The feature is ready for review with no runtime, training, or policy drift.

- [ ] T033 Update `specs/046-load-admission-action-exposure-review/quickstart.md` so the validation command exactly matches the approved Feature 046 regression set and excludes pointer-sensitive older report tests
- [ ] T034 Update `specs/046-load-admission-action-exposure-review/data-model.md` and `specs/046-load-admission-action-exposure-review/contracts/load-admission-action-exposure-report-schema.md` if needed to keep the diagnostic-only boundary, metric definitions, verdict routing, and next-feature guidance explicit
- [ ] T035 Check whether `AGENTS.md` is dirty, restore or stash it before report generation if needed, and stop immediately if it remains dirty; do not commit `AGENTS.md` or add it to `.gitignore`
- [ ] T036 Validate report cleanliness before regeneration by enforcing that `.specify/feature.json` may only remain as a local active pointer, must not be staged, must not appear in `git diff --name-only main...HEAD`, `AGENTS.md` must not be staged or appear in `git diff --name-only main...HEAD`, any dirty path outside the active feature scope blocks report generation, `no_unrelated_dirty_files` must be `true`, and report validation must fail if `AGENTS.md` appears in dirty paths/details or any prerequisite/prior-feature gate is false
- [ ] T037 [P] [US3] Add report consistency tests that fail if `final_verdict` and `recommended_next_feature` contradict each other, if action-exposure verdicts do not route to `Feature 047 — Paper HOODIE Observation Vector`, if mixed pressure verdicts do not route to `exposure-matrix review` before Feature 047, if load/admission/queue/offload verdicts route directly to runtime repair, or if `diagnosis_inconclusive_requires_deeper_exposure_matrix` does not route to `exposure-matrix review` in `tests/integration/test_load_admission_action_exposure_report.py`
- [ ] T038 [P] [US3] Add report runtime-fault contradiction tests that fail if runtime repair is recommended without a verified contradiction against Feature 045 trace evidence, or if the report claims a contradiction without including `contradiction_type`, `evidence_count > 0`, `representative_task_ids`, `supporting_event_types`, `explanation`, and an explicit explanation of why the contradiction conflicts with Feature 045 in `tests/integration/test_load_admission_action_exposure_report.py`
- [ ] T039 [P] [US3] Add scope-guard tests that explicitly prove `no_optimizer_step = true`, `no_replay_training = true`, `no_target_update_execution = true`, `no_curve_fitting = true`, `no_simulator_output_tuning = true`, `no_paper_reproduction_claim = true`, `no_training_started = true`, `no_runtime_repair_performed = true`, `no_dependency_drift = true`, `no_environment_contract_drift = true`, `no_policy_drift = true`, `no_reward_timing_change = true`, `no_timeout_contract_drift = true`, `no_capacity_contract_drift = true`, `no_transmission_contract_drift = true`, and `no_action_legality_drift = true` in the report payload and committed diff in `tests/integration/test_load_admission_action_exposure_scope_guard.py`
- [ ] T040 Re-run the approved validation command from `specs/046-load-admission-action-exposure-review/quickstart.md` and confirm no runtime behavior drift in `tests/integration/test_load_admission_action_exposure_scope_guard.py`

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

- T013, T014, and T015 can proceed in parallel because they target different User Story 1 test concerns.
- T019 and T020 can proceed in parallel after the serialization metrics model exists because they target different User Story 2 metric concerns.
- T025, T026, and T027 can proceed in parallel after the queue/offload/budget models exist because they target different User Story 3 metric concerns.

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
