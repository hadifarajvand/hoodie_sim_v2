# Tasks: Environment Lifecycle Divergence Repair

**Input**: Design documents from `/specs/024-environment-lifecycle-divergence-repair/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md  
**Tests**: Required. This feature repairs lifecycle correctness and must be driven by tests before and after the repair.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Lock down the lifecycle evidence and scope guardrails before any environment repair is written.

- [X] T001 Add the source-gate validation test in `tests/unit/test_environment_lifecycle_repair.py` to confirm Feature 018 `differential-audit.json` and Feature 019 `repair-summary.json` are present, readable, and still show `case-local-compute` and `case-deterministic-ordering` as `divergence / likely_environment_bug` before any repair

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Prove the repair target, the reference alignment, and the blocker boundaries before implementing the lifecycle fix.

- [X] T002 [US1] Add the reference-alignment precheck in `tests/unit/test_environment_lifecycle_repair.py` to assert `case-local-compute` is still a likely environment bug before repair and to capture the current local-compute terminal sequence from `artifacts/analysis/differential-environment-audit/differential-audit.md`
- [X] T003 [US2] Add the reference-alignment precheck in `tests/unit/test_environment_lifecycle_repair.py` to assert `case-deterministic-ordering` is still a likely environment bug before repair and to capture the current deterministic-ordering terminal sequence from `artifacts/analysis/differential-environment-audit/differential-audit.md`
- [X] T004 [US3] Add the delayed-reward evidence review in `tests/unit/test_environment_lifecycle_repair.py` to confirm reward timing stays classified as `assumption_gap` unless `resources/papers/hoodie/ocr/merged.tex` plus lifecycle evidence explicitly justify a repair
- [X] T005 Add the forbidden-path scope guard in `tests/integration/test_environment_lifecycle_scope_guard.py` to reject any diff that touches `src/policies`, `src/metrics`, `src/training`, dependency files, lockfiles, baselines, or campaign artifacts

**Checkpoint**: Evidence gates, pre-repair divergence status, and allowed repair boundaries are locked before implementation begins.

---

## Phase 3: User Story 1 - Local Compute Lifecycle Repair (Priority: P1) 🎯 MVP

**Goal**: Repair local compute lifecycle behavior so `HoodieGymEnvironment` matches the reference lifecycle kernel when local compute is actually supported by the evidence.

**Independent Test**: The repaired environment completes a local-compute task before timeout when capacity/deadline allow, and the integration check matches the reference kernel’s terminal sequence.

### Tests for User Story 1

- [X] T006 [US1] Add the local-compute lifecycle completion regression in `tests/unit/test_environment_lifecycle_repair.py` to prove a local-compute task completes before timeout when capacity and deadline allow
- [X] T007 [US1] Add the integration regression in `tests/integration/test_environment_lifecycle_repair_flow.py` that compares `HoodieGymEnvironment` local-compute terminal status and event ordering against `src/reference_model/lifecycle.py`

### Implementation for User Story 1

- [X] T008 [US1] Repair the local-compute lifecycle path in `src/environment/environment.py` and `src/environment/deadline_rules.py` only where required to align completion timing and terminal status with the reference lifecycle kernel

### Validation for User Story 1

- [X] T009 [US1] Add the final local-compute confirmation in `tests/integration/test_environment_lifecycle_reference_alignment.py` to prove the repaired local-compute flow no longer diverges from the reference lifecycle kernel

---

## Phase 4: User Story 2 - Deterministic Ordering Repair (Priority: P1)

**Goal**: Repair deterministic same-slot ordering so the environment no longer misorders or incorrectly finalizes tasks in the audit case.

**Independent Test**: The repaired environment preserves same-slot ordering deterministically and the integration check no longer reports incorrect drop/finalization behavior.

### Tests for User Story 2

- [X] T010 [US2] Add the deterministic same-slot ordering regression in `tests/unit/test_environment_lifecycle_repair.py` or `tests/integration/test_environment_lifecycle_repair_flow.py` to prove same-slot ordering remains stable under the reference lifecycle expectation
- [X] T011 [US2] Add the integration regression in `tests/integration/test_environment_lifecycle_reference_alignment.py` that proves deterministic ordering no longer causes incorrect drop or finalization behavior

### Implementation for User Story 2

- [X] T012 [US2] Repair the deterministic same-slot ordering path in `src/environment/environment.py` and `src/environment/deadline_rules.py` only where required to align ordering and finalization semantics with the reference lifecycle kernel

### Validation for User Story 2

- [X] T013 [US2] Add the final ordering confirmation in `tests/unit/test_environment_lifecycle_repair.py` to verify the repaired ordering behavior is deterministic across repeated runs

---

## Phase 5: User Story 3 - Reward Timing and Repair Boundaries (Priority: P2)

**Goal**: Tighten delayed reward timing only if OCR-backed evidence supports it, otherwise preserve the assumption gap and keep the repair scope surgical.

**Independent Test**: The feature either documents a paper-backed reward timing change or explicitly keeps the assumption gap and reports why the change was not applied.

### Tests for User Story 3

- [X] T014 [US3] Add the optional reward-timing review in `tests/unit/test_environment_lifecycle_repair.py` to require paper/OCR plus lifecycle evidence before changing delayed reward handling

### Implementation for User Story 3

- [X] T015 [US3] Update delayed reward handling in `src/environment/deadline_rules.py` only if the paper OCR and lifecycle evidence explicitly support the change; otherwise preserve the existing assumption gap and document the blocker

### Validation for User Story 3

- [X] T016 [US3] Add the regression note in `tests/integration/test_environment_lifecycle_reference_alignment.py` or `tests/unit/test_environment_lifecycle_repair.py` confirming reward timing remains assumption-gap classified when evidence is insufficient

---

## Phase 6: Final Validation & Repair Artifacts

**Purpose**: Regenerate the differential audit, write the repair summary, and prove no forbidden paths changed.

- [X] T017 Regenerate `artifacts/analysis/differential-environment-audit/differential-audit.json` and `artifacts/analysis/differential-environment-audit/differential-audit.md` after the environment repair is applied
- [X] T018 Create `artifacts/analysis/environment-lifecycle-divergence-repair/repair-summary.json` and `artifacts/analysis/environment-lifecycle-divergence-repair/repair-summary.md` summarizing the repaired cases, remaining findings, and blocked scope
- [X] T019 Add horizontal/vertical instrumentation scope-creep guard in `tests/integration/test_environment_lifecycle_divergence_repair_scope_guard.py` that fails if Feature 024 changes horizontal offload instrumentation, vertical offload instrumentation, topology-backed destination instrumentation, transmission/offload event tracing, or offload trace cleanup unless the repair summary documents a direct lifecycle-correctness dependency for `case-local-compute` or `case-deterministic-ordering`
- [X] T020 [US1] Add the final diff scope guard in `tests/integration/test_environment_lifecycle_final_diff.py` to verify no forbidden paths changed, including `src/policies`, `src/metrics`, `src/training`, dependency files, lockfiles, baselines, or campaign artifacts

**Checkpoint**: The regenerated differential audit and repair summary prove whether the lifecycle divergences were actually repaired.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: No dependencies. Establish the evidence and guardrails first.
- **Phase 2**: Depends on Phase 1. Pre-repair evidence and boundaries must exist before any environment repair.
- **Phase 3**: Depends on Phase 2. Local-compute repair can begin only after the source gate and pre-repair checks are in place.
- **Phase 4**: Depends on Phase 3. Deterministic ordering is validated after the environment repair path exists.
- **Phase 5**: Depends on Phase 4. Reward timing and repair artifacts are finalized after the core lifecycle changes are in place.

### Task Dependencies

- `T001` must complete before any repair work begins.
- `T002`, `T003`, `T004`, and `T005` must be written before `T006`, `T007`, `T008`, `T010`, `T011`, `T012`, `T013`, `T014`, `T015`, `T016`, `T017`, `T018`, `T019`, and `T020`.
- `T006` must complete before `T007` and `T008`.
- `T007` must complete before `T009`.
- `T010` must complete before `T011` and `T012`.
- `T011` must complete before `T013`.
- `T014` must complete before `T015`.
- `T017` must complete before `T018`.

### Within the User Story

- Tests first, then the surgical environment repair.
- The regenerated differential audit is the success gate, not the code change itself.
- Reward timing remains blocked unless the evidence supports a repair.

## Parallel Opportunities

- `T002` and `T003` can run in parallel after `T001`.
- `T006` and `T010` can run in parallel once the pre-repair checks are in place.
- `T014` and `T019` can run in parallel after the core repair path exists.

## Implementation Strategy

### MVP First

1. Complete `T001`-`T007` to prove the divergences are still real and test the local-compute path.
2. Complete `T008`-`T013` to repair and verify deterministic ordering and local compute.
3. Complete `T014`-`T016` only if delayed reward timing is paper-backed.
4. Complete `T017`-`T020` to regenerate the audit, write the repair summary, and prove the diff stayed surgical.

### Incremental Delivery

1. Start with pre-repair evidence and scope guards.
2. Repair local compute first, because it is the primary lifecycle divergence.
3. Repair deterministic ordering second, because it is the other explicit likely environment bug.
4. Leave reward timing unchanged unless the evidence is strong enough to justify the change.
5. Regenerate the audit and repair summary last.

## Notes

- The feature is diagnostic and surgical only.
- No campaign reruns are allowed.
- No paper-validity claim is permitted.
- Horizontal and vertical offload instrumentation gaps remain deferred unless strictly necessary for lifecycle correctness.

## Acceptance Mapping

- `Source gate requirement` is satisfied by `T001`.
- `Pre-repair divergence confirmation` is satisfied by `T002` and `T003`.
- `Local compute repair requirement` is satisfied by `T006`, `T007`, `T008`, and `T009`.
- `Deterministic ordering repair requirement` is satisfied by `T010`, `T011`, `T012`, and `T013`.
- `Delayed reward boundary requirement` is satisfied by `T004`, `T014`, `T015`, and `T016`.
- `Audit regeneration requirement` is satisfied by `T017` and `T018`.
- `Scope guard requirement` is satisfied by `T005`, `T019`, and `T020`.
