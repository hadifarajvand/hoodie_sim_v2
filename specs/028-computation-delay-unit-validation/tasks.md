# Tasks: Computation Delay and CPU Unit Validation

## Phase 1: Setup

- [ ] T001 Validate required source gates and paper OCR inputs in `artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.json`, `resources/papers/hoodie/recovered/paper-parameter-registry.json`, `artifacts/analysis/link-rate-transmission-delay-contract/link-rate-contract-report.json`, `artifacts/analysis/offload-lifecycle-instrumentation/instrumentation-summary.json`, and `resources/papers/hoodie/ocr/merged.tex`
- [ ] T002 Precheck the Feature 027 slot-duration mismatch and runtime context in `artifacts/analysis/link-rate-transmission-delay-contract/link-rate-contract-report.json` and `src/environment/link_rate_config.py`
- [ ] T003 Define the exact unit-validation report schema in `src/analysis/computation_delay_cpu_unit_validation/report.py` and document it in `specs/028-computation-delay-unit-validation/data-model.md`

## Phase 2: Foundational

- [ ] T004 Extract and map task-size unit evidence from `resources/papers/hoodie/recovered/paper-parameter-registry.json` and `resources/papers/hoodie/ocr/merged.tex` into `src/analysis/computation_delay_cpu_unit_validation/unit_evidence.py`
- [ ] T005 Extract and map processing-density unit evidence from `resources/papers/hoodie/recovered/paper-parameter-registry.json` and `resources/papers/hoodie/ocr/merged.tex` into `src/analysis/computation_delay_cpu_unit_validation/unit_evidence.py`
- [ ] T006 Define the cycles-required formula contract and deterministic examples in `src/analysis/computation_delay_cpu_unit_validation/computation_delay.py`
- [ ] T007 Recover or classify EA private, EA public, and cloud CPU capacity evidence in `resources/papers/hoodie/recovered/paper-parameter-registry.json` and `src/analysis/computation_delay_cpu_unit_validation/cpu_capacity.py`
- [ ] T008 Define the seconds-to-slots conversion contract for `Δ = 0.1 s` and the current runtime value in `src/analysis/computation_delay_cpu_unit_validation/slot_duration.py`
- [ ] T009 Define the completion-slot calculation contract in `src/analysis/computation_delay_cpu_unit_validation/completion_slot.py`

## Phase 3: User Story 1 - Audit Unit Semantics

**Goal**: Explicitly audit unit meanings for task size, processing density, cycles required, CPU capacities, and slot duration mismatch.

**Independent Test**: The report distinguishes recovered, unrecoverable, and mismatched semantics without inventing missing values.

- [ ] T010 [US1] Implement the task-size conversion tests in `tests/unit/test_computation_delay_cpu_unit_validation_task_size.py`
- [ ] T011 [US1] Implement the processing-density conversion tests in `tests/unit/test_computation_delay_cpu_unit_validation_processing_density.py`
- [ ] T012 [US1] Implement the CPU-capacity recoverability and unrecoverability tests in `tests/unit/test_computation_delay_cpu_unit_validation_cpu_capacity.py`
- [ ] T013 [US1] Implement the report generation and schema-population logic in `src/analysis/computation_delay_cpu_unit_validation/report.py`
- [ ] T014 [US1] Implement the unit-validation report runner in `src/analysis/computation_delay_cpu_unit_validation/runner.py`

## Phase 4: User Story 2 - Validate Computation Delay

**Goal**: Validate deterministic computation-delay and completion-slot behavior against explicit unit contracts.

**Independent Test**: The completion-slot calculation and seconds-to-slots conversion are reproducible across repeated runs.

- [ ] T015 [US2] Implement the cycles-required example tests in `tests/unit/test_computation_delay_cpu_unit_validation_cycles_required.py`
- [ ] T016 [US2] Implement the seconds-to-slots tests for `Δ = 0.1 s` and the current runtime value in `tests/unit/test_computation_delay_cpu_unit_validation_seconds_to_slots.py`
- [ ] T017 [US2] Implement the completion-slot calculation tests in `tests/integration/test_computation_delay_cpu_unit_validation_completion_slot.py`
- [ ] T018 [US2] Implement the mismatch-detection or narrow-repair test for the Feature 027 slot-duration contract in `tests/integration/test_computation_delay_cpu_unit_validation_slot_duration_mismatch.py`
- [ ] T019 [US2] Implement the narrow repair gate in `src/environment/link_rate_config.py` only if tests prove a minimal unit bug and the fix must remain isolated

## Phase 5: User Story 3 - Preserve Honest Boundaries

**Goal**: Preserve honest labeling for unrecoverable CPU capacities, runtime/paper Δ mismatch, and cross-feature regressions.

**Independent Test**: The validation report recommends repair or blocker handling explicitly and never claims recovered values without evidence.

- [ ] T020 [US3] Implement the Feature 019 timeout/drop regression tests in `tests/integration/test_computation_delay_cpu_unit_validation_regression_feature019.py`
- [ ] T021 [US3] Implement the Feature 024 local-compute and deterministic-ordering regression tests in `tests/integration/test_computation_delay_cpu_unit_validation_regression_feature024.py`
- [ ] T022 [US3] Implement the Feature 027 link-rate transmission-delay and monotonicity regression tests in `tests/integration/test_computation_delay_cpu_unit_validation_regression_feature027.py`
- [ ] T023 [US3] Generate the unit-validation report artifacts in `artifacts/analysis/computation-delay-cpu-unit-validation/unit-validation-report.json` and `artifacts/analysis/computation-delay-cpu-unit-validation/unit-validation-report.md`
- [ ] T024 [US3] Regenerate the Feature 027 link-rate report in `artifacts/analysis/link-rate-transmission-delay-contract/link-rate-contract-report.json` and `artifacts/analysis/link-rate-transmission-delay-contract/link-rate-contract-report.md` only if T019 proves the slot-duration contract changed
- [ ] T025 [US3] Add the scope guard tests blocking policy, training, dependency, lockfile, campaign, baseline redesign, curve-fitting, and paper-validity changes in `tests/integration/test_computation_delay_cpu_unit_validation_scope_guard.py`
- [ ] T026 [US3] Finalize the validation summary logic for repaired items, unrecoverable CPU-capacity fields, Δ handling, formulas, and remaining blockers in `src/analysis/computation_delay_cpu_unit_validation/report.py`

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T027 Re-run the targeted Feature 028 validation suite and confirm the report schema keys in `tests/integration/test_computation_delay_cpu_unit_validation_report_generation.py`
- [ ] T028 Verify no forbidden paths changed and no campaign artifacts were mutated in `tests/integration/test_computation_delay_cpu_unit_validation_scope_guard.py`

## Dependencies

- T001 -> T002 -> T003
- T004 -> T005 -> T006 -> T007 -> T008 -> T009
- T010 -> T011 -> T012 -> T013 -> T014
- T015 -> T016 -> T017 -> T018 -> T019
- T020 -> T021 -> T022 -> T023 -> T024 -> T025 -> T026
- T027 -> T028

## Parallel Execution Examples

- US1: T010, T011, and T012 can run in parallel after T004 through T009 are complete.
- US2: T015 and T016 can run in parallel once the foundational contracts are defined; T017 depends on T009, and T018 depends on T002.
- US3: T020, T021, and T022 can run in parallel; T023 and T026 depend on the contract/report logic; T024 is conditional on T019.

## Implementation Strategy

1. Build the evidence and schema foundation first so the report cannot drift.
2. Lock down unit conversions, cycles-required math, and slot-duration semantics with tests before touching runtime behavior.
3. Keep any runtime correction narrow and evidence-backed only.
4. Preserve Feature 019, Feature 024, and Feature 027 behavior with regression tests before considering the feature done.

## MVP Scope

Complete User Story 1 first: evidence recovery, semantic classification, and mismatch reporting. If that fails, stop. The rest is noise until the report is honest.
