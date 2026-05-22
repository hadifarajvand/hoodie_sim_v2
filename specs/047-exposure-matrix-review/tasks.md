# Tasks: Exposure-Matrix Review

## Phase 1: Setup

**Purpose**: Establish prerequisite verification, prior-feature artifact gates, and the analysis package/artifact locations before any matrix logic is built.  
**Independent Test**: Branch, predecessor, and workspace cleanliness gates can be verified without touching analysis logic.

- [x] T001 Verify prerequisite gates for Feature 047 in `specs/047-exposure-matrix-review/plan.md`, including branch identity, branch != `main`, `main == origin/main`, `main == 046-load-admission-action-exposure-review-complete^{}`, empty diff between `046-load-admission-action-exposure-review-complete^{}` and `main`, `.specify/feature.json` local-only handling, AGENTS.md cleanliness before report regeneration, and no unrelated dirty files
- [x] T002 Verify committed prior-feature artifacts for Features 037 through 046 in `artifacts/analysis/`, including the report paths for the baseline revalidation, training foundation, network implementation, smoke training, full-training campaign gate, terminal exposure, completion lifecycle audit, passive lifecycle trace instrumentation, completion root-cause diagnosis, and load/admission/action exposure review reports
- [x] T003 Create the passive analysis package scaffolding in `src/analysis/exposure_matrix_review/` and the report artifact directory in `artifacts/analysis/exposure-matrix-review/`
- [x] T004 Define the Feature 047 report contract and analysis entrypoint scaffolding in `src/analysis/exposure_matrix_review/__main__.py`, `runner.py`, `model.py`, and `report.py`

## Phase 2: Foundational

**Purpose**: Build the shared configuration, record schema, and report schema required by the exposure-matrix review.  
**Checkpoint**: Feature 047 can represent one decision opportunity, one matrix row, and one report payload without using sample slices as aggregate evidence.

- [x] T005 Define `ExposureMatrixConfig` in `src/analysis/exposure_matrix_review/config.py` with `feature_id`, `episode_length`, `timeout_slots`, `node_count`, `arrival_probability`, `seeds`, `strategies`, `no_runtime_repair`, and `no_training`
- [x] T006 Define `ExposureDecisionRecord` in `src/analysis/exposure_matrix_review/model.py` with the record fields for strategy, seed, slot, task, action legality, selected-illegal-action evidence, queue, offload, and terminal outcome evidence
- [x] T007 Define `ExposureMatrixMetrics` in `src/analysis/exposure_matrix_review/model.py` for the aggregate exposure matrix, per-action outcomes, selected-illegal-action counts and rates, per-queue counts, and offload exposure counts
- [x] T008 Define `ExposureMatrixReport` in `src/analysis/exposure_matrix_review/report.py` with the required report fields, illegal-action summary, final verdict field, and report writers for JSON and Markdown
- [x] T009 Define evidence-population metadata fields in `src/analysis/exposure_matrix_review/report.py` for `exposure_matrix_input_sources`, `exposure_matrix_population`, `legal_action_evidence_source`, and `legal_action_evidence_coverage_ratio`
- [x] T010 Define the prior-feature-gate contract in `src/analysis/exposure_matrix_review/report.py` so Features 037 through 046 must be verified before the matrix verdict is accepted, and so selected-illegal-action metrics cannot be omitted from the report contract

## Phase 3: User Story 1 - Validate full-population legal-vs-selected exposure coverage (Priority: P1) 🎯 MVP

**Goal**: Reconstruct the complete legal-vs-selected action exposure matrix across the paper-default strategy/seed grid and identify whether the matrix is complete or legally incomplete.  
**Independent Test**: Run the review on the full paper-default evidence and confirm the report counts every decision opportunity, traces legal action counts back to evidence, and marks missing legality evidence as incomplete instead of inventing zero counts.

### Tests for User Story 1

- [x] T011 [US1] Add report-schema tests for the exact top-level fields, evidence-population fields, and final verdict values in `tests/unit/test_exposure_matrix_schema.py`
- [x] T012 [US1] Add config tests that lock `ExposureMatrixConfig` to the paper-default grid, seeds, and diagnostic-only flags in `tests/unit/test_exposure_matrix_schema.py`
- [x] T013 [US1] Add record-schema tests for `ExposureDecisionRecord` covering the required legality, selected-illegal-action, queue, offload, and terminal outcome fields in `tests/unit/test_exposure_matrix_schema.py`
- [x] T014 [US1] Add full-population guard tests that reject `lifecycle_trace_sample` as an aggregate denominator for legal or selected-illegal-action metrics in `tests/unit/test_exposure_matrix_metrics.py`
- [x] T015 [US1] Add legal evidence source tests that require trace legality snapshots, action masks, or the approved public legality helper for legal and selected-illegal-action counts in `tests/unit/test_exposure_matrix_metrics.py`
- [x] T016 [US1] Add unavailable-legal-evidence tests that require null/unavailable values instead of fake zero legal counts or fake zero selected-illegal-action counts in `tests/unit/test_exposure_matrix_metrics.py`

### Implementation for User Story 1

- [x] T017 [US1] Implement `ExposureMatrixConfig` parsing and validation in `src/analysis/exposure_matrix_review/config.py`
- [x] T018 [US1] Implement `ExposureDecisionRecord` normalization and evidence-source tagging in `src/analysis/exposure_matrix_review/model.py`
- [x] T019 [US1] Implement the full-population matrix reconstruction path in `src/analysis/exposure_matrix_review/runner.py`, including selected-illegal-action counting from full legal evidence and null/unavailable handling when legal evidence is absent

## Phase 4: User Story 2 - Distinguish action exposure from load and offload dominance (Priority: P2)

**Goal**: Measure action exposure, load dominance, and offload underexposure from the same full evidence population and produce an honest routing recommendation.  
**Independent Test**: Confirm the report ranks exposure bias, load dominance, and offload underexposure from the matrix and does not route to repair or overclaim completeness when legality evidence is missing.

### Tests for User Story 2

- [x] T020 [US2] Add metrics tests for `decision_opportunity_count`, legal counts, selected counts, selected-illegal-action counts and rates, legal-but-unselected counts, and `action_entropy` in `tests/unit/test_exposure_matrix_metrics.py`
- [x] T021 [US2] Add metrics tests for per-action completion, drop, pending, wait, execution-progress, terminal-age rates, and selected-illegal-action examples in `tests/unit/test_exposure_matrix_metrics.py`
- [x] T022 [US2] Add metrics tests for per-queue matrix and offload exposure matrix counts in `tests/unit/test_exposure_matrix_metrics.py`
- [x] T023 [US2] Add integration tests that verify matrix completeness, legal-evidence coverage ratio, selected-illegal-action handling, and final verdict routing in `tests/integration/test_exposure_matrix_review.py`
- [x] T024 [US2] Add integration tests that verify complete exposure evidence routes to `Feature 048 — Paper HOODIE Observation Vector` and incomplete legal evidence routes to legality evidence expansion before Feature 048 in `tests/integration/test_exposure_matrix_review.py`

### Implementation for User Story 2

- [x] T025 [US2] Implement per-action outcome aggregation, selected-illegal-action aggregation, per-queue aggregation, and offload exposure aggregation in `src/analysis/exposure_matrix_review/runner.py`
- [x] T026 [US2] Implement exposure-bias ranking, load-vs-exposure summary, selected-illegal-action summary, and dominant-exposure findings in `src/analysis/exposure_matrix_review/report.py`

## Phase 5: User Story 3 - Preserve diagnostic-only scope and honest routing (Priority: P3)

**Goal**: Keep the feature passive, preserve the contract that sample slices are illustrative only, and emit the final report and quickstart artifacts.  
**Independent Test**: Confirm that the report stays diagnostic-only, marks missing legality evidence explicitly, and never recommends runtime repair.

### Tests for User Story 3

- [x] T027 [US3] Add integration tests that verify `no_runtime_repair_performed`, `no_training_started`, `no_optimizer_step`, `no_replay_training`, and `no_target_update_execution` remain true in `tests/integration/test_exposure_matrix_scope_guard.py`
- [x] T028 [US3] Add integration tests that verify `no_dependency_drift`, `no_environment_contract_drift`, `no_policy_drift`, `no_reward_timing_change`, `no_timeout_contract_drift`, `no_capacity_contract_drift`, `no_transmission_contract_drift`, and `no_action_legality_drift` remain true in `tests/integration/test_exposure_matrix_scope_guard.py`
- [x] T029 [US3] Add integration tests that verify `no_curve_fitting`, `no_simulator_output_tuning`, and `no_paper_reproduction_claim` remain true in `tests/integration/test_exposure_matrix_scope_guard.py`
- [x] T030 [US3] Add integration tests that fail if representative examples are used as aggregate denominators, if missing legal evidence is reported as zero, or if selected-illegal-action counts are omitted from the report in `tests/integration/test_exposure_matrix_report.py`
- [x] T031 [US3] Add integration tests that verify the report writes the JSON and Markdown artifacts under `artifacts/analysis/exposure-matrix-review/` in `tests/integration/test_exposure_matrix_report.py`

### Implementation for User Story 3

- [x] T032 [US3] Implement report payload assembly, JSON writer, and Markdown writer in `src/analysis/exposure_matrix_review/report.py`
- [x] T033 [US3] Implement the runner entrypoint that writes `artifacts/analysis/exposure-matrix-review/exposure-matrix-report.json` and `artifacts/analysis/exposure-matrix-review/exposure-matrix-report.md` in `src/analysis/exposure_matrix_review/runner.py`
- [x] T034 [US3] Update `specs/047-exposure-matrix-review/quickstart.md` so the validation command matches the approved Feature 047 regression bundle and excludes dirty-worktree-sensitive older report tests

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, scope protection, and documentation alignment.  
**Checkpoint**: The feature is ready for review with no runtime, training, or policy drift.

- [x] T035 Verify `specs/047-exposure-matrix-review/data-model.md` and `specs/047-exposure-matrix-review/contracts/exposure-matrix-report-schema.md` remain aligned with the implemented report fields, verdict values, and evidence-population discipline
- [x] T036 Verify `specs/047-exposure-matrix-review/research.md` stays consistent with the implemented choices for legality evidence priority, full-population matrix requirements, and routing rules
- [x] T037 Verify `.specify/feature.json` remains a local pointer only, is not staged, and is not committed; stop if it is dirty in committed history
- [x] T038 Verify `AGENTS.md` is clean before report generation, do not commit it, and do not add it to `.gitignore`
- [x] T039 Re-run the approved Feature 047 validation command and confirm that the report rejects sample-only aggregate exposure metrics and illegal zero counts
- [x] T040 Rerun `/speckit.analyze` after the task repair and before any implementation work resumes

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 and Foundational phase completion
- **User Story 3 (Phase 5)**: Depends on User Story 2 and Foundational phase completion
- **Polish (Phase 6)**: Depends on the desired user stories and report generation being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - no dependencies on other stories
- **User Story 2 (P2)**: Can start after User Story 1 is ready enough to validate exposure bias, load dominance, and offload underexposure findings
- **User Story 3 (P3)**: Can start after the matrix logic and routing rules are in place

### Within Each User Story

- Tests MUST be written and fail before implementation for the story-specific validations.
- Shared configuration and record schema come before matrix aggregation.
- Matrix aggregation and legality handling come before report assembly.
- Report assembly comes before report regeneration.
- Scope guard rules come before the final validation pass.

## Parallel Opportunities

Only the following tasks are safely parallelizable because they touch disjoint files and do not depend on incomplete work:

- T011, T012, and T013 can proceed in parallel after the foundational schema exists because they target separate schema concerns in `tests/unit/test_exposure_matrix_schema.py`.
- T020, T021, and T022 can proceed in parallel after the matrix model exists because they target separate metric families in `tests/unit/test_exposure_matrix_metrics.py`.
- T027, T028, and T029 can proceed in parallel after the report payload exists because they target separate scope-guard assertions in `tests/integration/test_exposure_matrix_scope_guard.py`.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. STOP and validate the exposure matrix entrypoint independently

### Incremental Delivery

1. Complete Setup + Foundational → the matrix schema is stable
2. Add User Story 1 → complete legal-vs-selected coverage is measurable or explicitly incomplete
3. Add User Story 2 → action exposure, load dominance, and offload underexposure are distinguished
4. Add User Story 3 → the feature stays diagnostic only and the report artifacts are regenerated
5. Finish with documentation alignment and the approved validation command

## Validation Command

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_exposure_matrix_schema \
  tests.unit.test_exposure_matrix_metrics \
  tests.integration.test_exposure_matrix_review \
  tests.integration.test_exposure_matrix_report \
  tests.integration.test_exposure_matrix_scope_guard \
  tests.unit.test_load_admission_action_exposure_schema \
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
