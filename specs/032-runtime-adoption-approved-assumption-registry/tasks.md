# Tasks: Runtime Adoption of Approved Assumption Registry

**Input**: Design documents from `/specs/032-runtime-adoption-approved-assumption-registry/`
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the correction scope and keep the repository on the approved runtime-adoption branch before touching code.

- [ ] T001 Verify current branch is `032-runtime-adoption-approved-assumption-registry` and fail immediately if the branch is `main`
- [ ] T002 Verify the current branch was created from updated `main` by checking the branch base against `main`
- [ ] T003 Verify the `031-user-approved-assumption-patch-registry-complete` tag exists and resolves to the same commit as `main`
- [ ] T004 Verify `resources/papers/hoodie/recovered/user-approved-assumption-registry.json` and `artifacts/analysis/user-approved-assumption-patch-registry/assumption-patch-report.json` are readable
- [ ] T005 Verify the working tree does not already contain runtime, training, dependency, policy, baseline, campaign, or paper-recovery drift before the correction starts

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Record the vertical/cloud legality correction in the feature artifacts before runtime code is patched.

- [ ] T006 Update `specs/032-runtime-adoption-approved-assumption-registry/spec.md` so Figure 7 adjacency is horizontal-only and vertical/cloud legality is independent of the adjacency map
- [ ] T007 Update `specs/032-runtime-adoption-approved-assumption-registry/plan.md` so the validation strategy and dependency order explicitly require `TopologyGraph.from_approved_assumption_registry()` to keep vertical/cloud offload legal without requiring `cloud` in `legal_adjacency`
- [ ] T008 Update `specs/032-runtime-adoption-approved-assumption-registry/tasks.md` so the correction tasks and report validation mention the approved-topology vertical/cloud legality test by name
- [ ] T009 Update `specs/032-runtime-adoption-approved-assumption-registry/quickstart.md` if needed so the validation command list includes the approved-topology vertical/cloud legality test

## Phase 3: User Story 1 - Separate Vertical/Cloud Legality From Figure 7 Topology (Priority: P1)

**Goal**: Make the approved Figure 7 topology govern horizontal offloading only, while keeping vertical/cloud offload legal independently and resolving it to `cloud`.

**Independent Test**: A reviewer can load `TopologyGraph.from_approved_assumption_registry()` and confirm that horizontal destinations are only approved EA neighbors, `cloud` is absent from horizontal destinations, and vertical/offload_vertical remains legal and resolves to `cloud`.

### Tests for User Story 1

- [ ] T010 [US1] Add `test_approved_figure7_topology_keeps_vertical_cloud_offload_legal` in `tests/unit/test_runtime_adoption_approved_assumption_registry.py` using `TopologyGraph.from_approved_assumption_registry()` to assert `cloud` is not in `legal_horizontal_destinations(source_id)`, is not injected into `topology.legal_adjacency[source_id]`, `env.legal_action_mask(task)["vertical"]` is `True`, `env.legal_action_mask(task)["offload_vertical"]` is `True`, `env._resolve_destination(task, "vertical") == "cloud"`, `env._resolve_destination(task, "offload_vertical") == "cloud"`, and horizontal resolution returns only an approved EA neighbor
- [ ] T011 [US1] Add a unit regression in `tests/unit/test_gym_environment.py` that proves approved-topology vertical/cloud legality does not depend on `cloud` being present in the adjacency map
- [ ] T012 [US1] Add a targeted integration regression in `tests/integration/test_evaluation_runner.py` only if `EvaluationRunner` still contains reachable duplicate legality or destination-resolution logic that could contradict `HoodieGymEnvironment`
- [ ] T013 [US1] Add `test_runtime_adoption_report_mentions_vertical_cloud_separation_fix` in `tests/integration/test_runtime_adoption_report.py` to require the correction note and the approved-topology vertical/cloud test name in the report

### Implementation for User Story 1

- [ ] T014 [US1] Update `src/environment/gym_adapter.py` so `legal_action_mask(task)` derives `horizontal/offload_horizontal` only from approved neighbor-only topology and sets `vertical/offload_vertical` independently of Figure 7 adjacency
- [ ] T015 [US1] Update `src/environment/gym_adapter.py` so `_resolve_destination(task, "vertical")` and `_resolve_destination(task, "offload_vertical")` return `cloud` independently of Figure 7 adjacency, while horizontal resolution still returns only an approved neighboring EA
- [ ] T016 [US1] Update `src/evaluation/runner.py` to remove or align any duplicate reachable legality or destination-resolution helper logic so it does not contradict `HoodieGymEnvironment`
- [ ] T017 [US1] Update `src/analysis/runtime_adoption_approved_assumption_registry/report.py` to include the correction summary, the approved-topology vertical/cloud legality test name, and the unchanged no-paper-recovery/no-drift flags
- [ ] T018 [US1] Update `artifacts/analysis/runtime-adoption-approved-assumption-registry/runtime-adoption-report.json` and `artifacts/analysis/runtime-adoption-approved-assumption-registry/runtime-adoption-report.md` to reflect the corrected vertical/cloud legality behavior after tests pass

## Phase 4: Validation and Scope Guard

**Purpose**: Prove the correction is real, regression-safe, and still isolated from training/dependency/policy/campaign drift.

- [ ] T019 [US1] Run the approved-interpreter unit test command in `specs/032-runtime-adoption-approved-assumption-registry/quickstart.md` covering `tests.unit.test_runtime_adoption_approved_assumption_registry`, `tests.unit.test_gym_environment`, and `tests.unit.test_compute_config`
- [ ] T020 [US1] Run the approved-interpreter integration test command in `specs/032-runtime-adoption-approved-assumption-registry/quickstart.md` covering `tests.integration.test_runtime_adoption_report`, `tests.integration.test_evaluation_runner`, `tests.integration.test_execution_time_flow`, and `tests.integration.test_runtime_adoption_scope_guard`
- [ ] T021 [US1] Run `git status --short` and `git diff --name-only main...HEAD` and confirm the diff is limited to the approved Feature 032 correction files and generated runtime-adoption artifacts
- [ ] T022 [US1] Confirm the final report verdict remains blocked until `test_approved_figure7_topology_keeps_vertical_cloud_offload_legal` passes against `TopologyGraph.from_approved_assumption_registry()`

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 must complete before any file edits.
- Phase 2 must complete before runtime code changes.
- Phase 3 depends on the corrected feature artifact wording being in place.
- Phase 4 depends on the runtime code, tests, and report updates being implemented.

### User Story Dependencies

- **US1**: Can start after Phase 2 and is the only story for this correction.

### Within Each User Story

- Tests must be written before or alongside the code change they validate.
- `HoodieGymEnvironment` is the source of truth for legality and destination resolution.
- `TopologyGraph.from_approved_assumption_registry()` must be the topology fixture used in the approved-topology vertical/cloud test.
- Report verdict must not claim completion until the approved-topology vertical/cloud legality test passes.

## Parallel Opportunities

- `T006`, `T007`, `T008`, and `T009` can run sequentially or in a small batch because they only update feature artifacts and should not conflict if edited carefully.
- `T010` and `T011` can be parallelized only if they touch different test files and do not overlap with each other.
- `T019` and `T020` can run after implementation but should not be treated as fake parallelism because the integration command depends on the unit-level correction being present.

## Implementation Strategy

### MVP First

1. Complete Phase 2 feature-artifact correction.
2. Patch `HoodieGymEnvironment` legality and destination resolution.
3. Prove the approved-topology vertical/cloud legality test passes.

### Incremental Delivery

1. Fix topology vertical/cloud separation.
2. Update the report to name the correction and the approved-topology test.
3. Run the targeted validation commands and reject any polluted diff.

### Parallel Team Strategy

1. One contributor updates the feature artifacts and quickstart.
2. One contributor patches `gym_adapter.py`.
3. One contributor updates the report and tests.

