# Tasks: Mechanism Repair

**Input**: Design documents from `/specs/019-mechanism-repair/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md  
**Tests**: Required. This feature is a surgical repair and must be driven by regression tests first.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Lock the confirmed repair gate before any code changes.

- [ ] T001 Record the confirmed Feature 018 repair gate and unrepaired findings in `specs/019-mechanism-repair/research.md` by reading `artifacts/analysis/differential-environment-audit/differential-audit.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Prepare the regression scaffolding that proves the timeout/drop defect before repair.

- [ ] T002 [US1] Add the timeout/drop regression test in `tests/unit/test_mechanism_repair_timeout_drop.py` that reproduces the pre-repair `case-timeout-drop` divergence through the public environment `step` lifecycle
- [ ] T003 [US1] Add the delayed-reward regression in `tests/unit/test_mechanism_repair_timeout_drop.py` that asserts reward is emitted only at terminal drop/finalization, never at decision time
- [ ] T004 [US1] Add the local-compute non-regression test in `tests/unit/test_mechanism_repair_timeout_drop.py` that confirms the existing completion path still works unchanged
- [ ] T005 [US1] Add the scope-guard test in `tests/integration/test_mechanism_repair_scope_guard.py` that rejects changes to metrics, policies, baselines, campaigns, training, dependencies, or lockfiles

**Checkpoint**: Regression coverage exists before the environment patch is written.

---

## Phase 3: User Story 1 - Repair Confirmed Timeout/Drop Divergence (Priority: P1) 🎯 MVP

**Goal**: Fix only the confirmed `case-timeout-drop` divergence so timeout/drop terminal accounting reports a dropped outcome correctly.

**Independent Test**: The timeout/drop regression fails before the patch, passes after the patch, and delayed reward still occurs only at terminal finalization.

### Implementation for User Story 1

- [ ] T006 [US1] Implement the smallest timeout/drop terminal accounting patch in `src/environment/gym_adapter.py`

### Validation for User Story 1

- [ ] T007 [US1] Rerun the Feature 017 reference tests in `tests/unit/test_reference_task_lifecycle_kernel.py` and `tests/integration/test_reference_task_lifecycle_kernel_flow.py`
- [ ] T008 [US1] Rerun the Feature 018 differential audit tests in `tests/unit/test_differential_environment_audit.py` and `tests/integration/test_differential_environment_audit_flow.py`
- [ ] T009 [US1] Regenerate the Feature 018 differential audit artifacts in `artifacts/analysis/differential-environment-audit/differential-audit.json` and `artifacts/analysis/differential-environment-audit/differential-audit.md`

**Checkpoint**: The confirmed divergence is repaired and the audit evidence is refreshed.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Preserve traceability for the repair and validate the final diff surface.

- [ ] T010 Add the optional repair summary artifact in `artifacts/analysis/mechanism-repair/repair-summary.json` and `artifacts/analysis/mechanism-repair/repair-summary.md`
- [ ] T011 Add the final diff audit in `tests/integration/test_mechanism_repair_final_diff.py` to verify the repair only touches the allowed environment path and leaves forbidden paths unchanged

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: No dependencies. Start by confirming the repair gate from Feature 018.
- **Phase 2**: Depends on Phase 1. Regression tests must exist before the repair patch.
- **Phase 3**: Depends on Phase 2. The timeout/drop patch comes after failing tests are in place.
- **Phase 4**: Depends on Phase 3. Summary and diff audits happen after the repair and validation pass.

### Task Dependencies

- `T001` must complete before any implementation work begins.
- `T002`, `T003`, `T004`, and `T005` must be written before `T006`.
- `T006` must complete before `T007`, `T008`, `T009`, `T010`, and `T011`.
- `T009` must complete before the optional repair summary and final diff report are considered done.

### Within the User Story

- Regression tests first, then the surgical environment patch.
- Validation reruns before audit regeneration.
- Audit regeneration before the repair summary and final diff report.

## Parallel Opportunities

- None are marked here to avoid false parallelism. Each task is intentionally serialized around the single confirmed repair target.

## Implementation Strategy

### MVP First

1. Complete `T001` to lock the gate.
2. Complete `T002`-`T005` so the defect is reproducible and bounded.
3. Complete `T006` to fix only timeout/drop terminal accounting.
4. Complete `T007`-`T009` to prove the repair and refresh the Feature 018 audit.
5. Complete `T010`-`T011` for traceability and final scope verification.

### Incremental Delivery

1. Make the timeout/drop regression fail first.
2. Patch the smallest public environment accounting path.
3. Re-run Feature 017 and Feature 018 validation.
4. Regenerate the differential audit.
5. Produce the repair summary and final diff audit.

## Notes

- `case-timeout-drop` is the only confirmed repair target.
- Metrics, policies, baselines, campaigns, training, dependencies, and lockfiles are out of scope.
- Offload instrumentation gaps remain unrepaired unless separately proven by a new audit artifact.
