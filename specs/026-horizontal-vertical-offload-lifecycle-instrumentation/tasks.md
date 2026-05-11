# Tasks: Horizontal and Vertical Offload Lifecycle Instrumentation

**Input**: Design documents from `/specs/026-horizontal-vertical-offload-lifecycle-instrumentation/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md  
**Tests**: Required. This feature is trace-observability instrumentation only and must prove no behavior mutation, no topology fabrication, and no regression of Feature 019 / 024 repairs.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Lock down required source gates and the current failure mode before any instrumentation is written.

- [ ] T001 Add the source-gate validation test in `tests/integration/test_offload_instrumentation_source_gates.py` to confirm Feature 018 differential audit, Feature 019 repair summary, Feature 024 repair summary, Feature 025 topology registry, and the current differential audit all exist before instrumentation begins

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Prove the current observability gap and define the trace contract before any trace exposure or audit updates are implemented.

- [ ] T002 [P] Add the pre-instrumentation confirmation test in `tests/integration/test_offload_instrumentation_precheck.py` to prove case-horizontal-offload and case-vertical-offload currently fail because lifecycle trace visibility is incomplete
- [ ] T003 Add the trace event schema definition in `src/environment/offload_trace_schema.py` to define the required ordered events `selected_action`, `queued_public`, `offloaded_cloud`, `transmission_started`, `transmission_completed`, `execution_started`, `execution_completed`, `dropped_timeout`, and `reward_emitted`

**Checkpoint**: The trace contract and current observability gap are explicit before any implementation work begins.

---

## Phase 3: User Story 1 - Horizontal and Vertical Trace Visibility (Priority: P1)

**Goal**: Make horizontal and vertical offload lifecycle events observable in HoodieGymEnvironment traces.

**Independent Test**: Can be verified by producing traces for horizontal and vertical offload paths and confirming the required lifecycle events appear in deterministic order without changing behavior.

### Tests for User Story 1

- [ ] T004 [P] [US1] Add the deterministic trace event schema and ordering test in `tests/unit/test_offload_trace_schema.py` to verify event names, sequence stability, and trace payload shape
- [ ] T005 [P] [US1] Add the horizontal offload lifecycle trace visibility test in `tests/integration/test_offload_lifecycle_trace_visibility_horizontal.py` to verify the full horizontal path is observable in traces
- [ ] T006 [P] [US1] Add the vertical offload lifecycle trace visibility test in `tests/integration/test_offload_lifecycle_trace_visibility_vertical.py` to verify the full vertical path is observable in traces
- [ ] T007 [P] [US2] Add the Feature 024 regression test in `tests/unit/test_offload_instrumentation_feature024_regression.py` to confirm local-compute and deterministic-ordering matches remain preserved
- [ ] T008 [P] [US2] Add the Feature 019 regression test in `tests/unit/test_offload_instrumentation_feature019_regression.py` to confirm timeout/drop behavior remains preserved
- [ ] T009 [P] [US1] Add the no-behavior-change test in `tests/integration/test_offload_instrumentation_no_behavior_change.py` to prove trace instrumentation does not change rewards, metrics, policy decisions, arrivals, or final outcomes

### Implementation for User Story 1

- [ ] T010 [US1] Add the surgical trace/ledger instrumentation in `src/environment/offload_trace_ledger.py` and `src/environment/offload_trace_emitter.py` to expose lifecycle events without changing simulator behavior unless a bug is proven by a failing test

**Parallel Example**: `T004`, `T005`, `T006`, and `T009` can be implemented in parallel after `T003` because they target different test files.

---

## Phase 4: User Story 2 - Audit Consumer and Regression Coverage (Priority: P2)

**Goal**: Preserve prior repaired behavior while teaching the differential audit to consume the richer lifecycle trace data if needed.

**Independent Test**: Can be verified by running the audit and regression tests to confirm Feature 019 and Feature 024 remain stable and the new trace data is consumed correctly.

### Tests for User Story 2

### Implementation for User Story 2

- [ ] T011 [US2] Update the differential audit consumer in `src/audits/differential_environment/audit.py` and `src/audits/differential_environment/classifier.py` only if needed to consume richer lifecycle traces and separate observability gaps from topology or legality blockers
- [ ] T012 [US2] Regenerate the differential environment audit in `artifacts/analysis/differential-environment-audit/differential-audit.json` and `artifacts/analysis/differential-environment-audit/differential-audit.md` so horizontal and vertical cases are no longer unsupported solely because only `selected_action` was visible

**Parallel Example**: `T007` and `T008` can run in parallel after `T009` and `T010` are understood, and `T011` can proceed after the trace schema is in place.

---

## Phase 5: User Story 3 - Summary Artifact, Topology Guard, and Scope Guard (Priority: P3)

**Goal**: Produce the instrumentation summary and prove the feature did not fabricate topology or drift into forbidden areas.

**Independent Test**: Can be verified by checking the regenerated audit, summary artifact, and guard tests without any forbidden-path mutations.

### Tests for User Story 3

- [ ] T013 [P] [US3] Add the instrumentation summary artifact generation test in `tests/integration/test_offload_instrumentation_summary.py` to verify `artifacts/analysis/offload-lifecycle-instrumentation/instrumentation-summary.json` and `artifacts/analysis/offload-lifecycle-instrumentation/instrumentation-summary.md` are produced deterministically
- [ ] T014 [P] [US3] Add the topology-fabrication guard test in `tests/integration/test_offload_instrumentation_topology_guard.py` to prove Figure 7 adjacency, legal horizontal destinations, and paper topology are not invented or injected
- [ ] T015 [P] [US3] Add the scope guard test in `tests/integration/test_offload_instrumentation_scope_guard.py` to prove no `src/policies`, `src/metrics`, `src/training`, dependency files, lockfiles, campaign artifacts, baselines, training stacks, or paper-validity claims were introduced
- [ ] T016 [US3] Add the final validation test in `tests/integration/test_offload_instrumentation_final_validation.py` to report remaining lifecycle gaps honestly after instrumentation and audit regeneration

### Implementation for User Story 3

- [ ] T017 [US3] Build the instrumentation summary writer in `src/audits/differential_environment/report.py` and `src/audits/differential_environment/runner.py` to produce `artifacts/analysis/offload-lifecycle-instrumentation/instrumentation-summary.json` and `artifacts/analysis/offload-lifecycle-instrumentation/instrumentation-summary.md`

**Parallel Example**: `T013`, `T014`, and `T015` can run in parallel after `T012` because they target distinct guard and summary files.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: No dependencies. Establish source gates first.
- **Phase 2**: Depends on Phase 1. Confirm the current failure mode and define the trace contract before instrumentation.
- **Phase 3**: Depends on Phase 2. Horizontal and vertical trace visibility work starts only after the contract is established.
- **Phase 4**: Depends on Phase 3. Audit consumer and regression coverage follow the trace exposure.
- **Phase 5**: Depends on Phases 3 and 4. Summary artifacts and guards finalize the feature after the traces and audit are in place.

### Task Dependencies

- `T001` must complete before any other work begins.
- `T002` and `T003` must complete before `T010`, `T011`, `T012`, and `T017`.
- `T004`, `T005`, `T006`, and `T009` must complete before `T012`, `T013`, `T014`, `T015`, and `T016`.
- `T007` and `T008` must complete before `T012` and `T017`.
- `T011` must complete before `T012` and `T017`.
- `T012` must complete before `T013`, `T014`, `T015`, `T016`, and `T017`.
- `T010` must complete before any runtime trace changes are accepted.

## Parallel Opportunities

- `T002` and `T003` can run in parallel after `T001`.
- `T004`, `T005`, `T006`, and `T009` can run in parallel after `T003`.
- `T007` and `T008` can run in parallel with one another after the trace contract exists.
- `T013`, `T014`, and `T015` can run in parallel after the audit regeneration path is understood.

## Implementation Strategy

### MVP First

1. Complete `T001`-`T003` to lock down the source gates and trace contract.
2. Complete `T004`-`T010` to prove offload trace visibility without behavior mutation.
3. Complete `T011`-`T012` to update and regenerate the differential audit.
4. Complete `T013`-`T017` to produce the summary artifact and enforce the topology and scope guards.

### Incremental Delivery

1. Start with source-gate and precheck coverage.
2. Add trace visibility next, keeping local-compute and timeout/drop regressions active.
3. Teach the audit consumer only if the richer trace data requires it.
4. Finish with the instrumentation summary and explicit guards against topology fabrication and forbidden-path drift.

## Notes

- This feature is trace-observability instrumentation only.
- No simulator behavior change is allowed unless a test proves a bug and the fix is documented.
- Feature 025 topology conclusions remain authoritative: Figure 7 adjacency and legal horizontal destinations are still unrecoverable from paper evidence.

## Acceptance Mapping

- `Source gate requirement` is satisfied by `T001`.
- `Pre-instrumentation confirmation requirement` is satisfied by `T002`.
- `Trace event schema requirement` is satisfied by `T003` and `T004`.
- `Horizontal trace visibility requirement` is satisfied by `T005`.
- `Vertical trace visibility requirement` is satisfied by `T006`.
- `Feature 024 regression coverage` is satisfied by `T007`.
- `Feature 019 regression coverage` is satisfied by `T008`.
- `No-behavior-change requirement` is satisfied by `T009`.
- `Instrumentation requirement` is satisfied by `T010`.
- `Audit consumer update requirement` is satisfied by `T011`.
- `Differential audit regeneration requirement` is satisfied by `T012`.
- `Instrumentation summary requirement` is satisfied by `T013` and `T017`.
- `Topology-fabrication guard` is satisfied by `T014`.
- `Scope guard` is satisfied by `T015`.
- `Final validation requirement` is satisfied by `T016`.
