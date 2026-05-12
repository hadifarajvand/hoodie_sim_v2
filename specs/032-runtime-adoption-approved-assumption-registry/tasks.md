# Tasks: Runtime Adoption of Approved Assumption Registry

**Input**: Design documents from `/specs/032-runtime-adoption-approved-assumption-registry/`
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish branch hygiene, provenance inputs, and scope boundaries before any runtime code is changed.

- [ ] T001 Verify current branch is `032-runtime-adoption-approved-assumption-registry` and fail immediately if the branch is `main`
- [ ] T002 Verify the current branch was created from updated `main` by checking the branch base against `main`
- [ ] T003 Verify the `031-user-approved-assumption-patch-registry-complete` tag exists
- [ ] T004 Verify the `031-user-approved-assumption-patch-registry-complete` tag resolves to the same commit as `main`
- [ ] T005 Verify `resources/papers/hoodie/recovered/user-approved-assumption-registry.json` exists and is readable
- [ ] T006 Verify `artifacts/analysis/user-approved-assumption-patch-registry/assumption-patch-report.json` exists and is readable
- [ ] T007 Verify the working tree does not already contain runtime, training, dependency, policy, baseline, campaign, or paper-recovery drift before implementation begins

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the provenance helpers and runtime adoption boundaries used by all downstream tasks.

- [ ] T008 Create a registry ingestion helper in `src/analysis/runtime_adoption_approved_assumption_registry/__init__.py` that loads the Feature 031 registry and report artifacts without rewriting paper-recovery status
- [ ] T009 Create a provenance loader in `src/analysis/runtime_adoption_approved_assumption_registry/runner.py` that exposes consumed assumption IDs and source paths for runtime adoption
- [ ] T010 Add a runtime-adoption report schema in `src/analysis/runtime_adoption_approved_assumption_registry/report.py` with consumed assumptions, runtime components changed or validated, tests run, and final verdict
- [ ] T011 Add a minimal shared helper boundary in `src/evaluation/aggregate_metrics.py` and `src/evaluation/metrics.py` for reward aggregation reuse by runtime and reporting

## Phase 3: User Story 1 - Adopt Compute, Link-Rate, and Timeout Contracts (Priority: P1)

**Goal**: Apply approved CPU capacities, link-rate values, and timeout contract values to runtime-facing configuration without changing training or dependency behavior.

**Independent Test**: A reviewer can validate ComputeConfig, LinkRateConfig, and TrafficConfig values directly from runtime configuration and confirm the approved values are present.

### Tests for User Story 1

- [ ] T012 [P] [US1] Add `test_compute_config_uses_approved_assumption_capacities` in `tests/unit/test_compute_config.py` to assert `cpu_capacity_per_slot_agent=0.5`, `cpu_capacity_per_slot_edge=0.5`, and `cpu_capacity_per_slot_cloud=3.0`
- [ ] T013 [P] [US1] Add a unit test in `tests/unit/test_compute_config.py` that proves the stale defaults `32.0`, `64.0`, and `128.0` are not used by the runtime default ComputeConfig path
- [ ] T014 [P] [US1] Add `test_cloud_vertical_rate_uses_RV_10mbps_no_fake_cloud_rate` in `tests/unit/test_link_rate_config.py` to assert `vertical_data_rate_mbps=10.0` and no separate cloud-specific rate is introduced
- [ ] T015 [P] [US1] Add `test_timeout_contract_20_slots_2_seconds` in `tests/unit/test_traffic_config.py` to assert `timeout_slots=20`, `slot_duration_seconds=0.1`, and `timeout_seconds=2.0`
- [ ] T016 [P] [US1] Add `test_timeout_drop_behavior_consumes_runtime_contract` in `tests/integration/test_gym_environment.py` to prove the runtime drop path uses the approved timeout contract end-to-end

### Implementation for User Story 1

- [ ] T017 [US1] Update `src/environment/compute_config.py` to set runtime defaults to `0.5`, `0.5`, and `3.0` gcycles/slot and preserve unit validation
- [ ] T018 [US1] Update `src/environment/link_rate_config.py` to preserve `R_H = 30 Mbps`, set cloud-facing vertical rate to `R_V = 10 Mbps`, and avoid introducing a separate cloud-specific rate
- [ ] T019 [US1] Update `src/environment/traffic_config.py` to ensure the runtime timeout contract exposes `timeout_slots=20`, `slot_duration_seconds=0.1`, and `timeout_seconds=2.0` consistently
- [ ] T020 [US1] Update `src/environment/gym_adapter.py` so runtime observations and action masks consume the approved runtime config values without changing reward timing

## Phase 4: User Story 2 - Adopt Topology and Horizontal Legality Contracts (Priority: P2)

**Goal**: Load the approved Figure 7 adjacency directly from the Feature 031 registry snapshot and enforce neighbor-only horizontal legality while keeping vertical/cloud legality separate.

**Independent Test**: A reviewer can validate the topology matrix, action mask, and legality rules from the runtime environment without any campaign rerun or training change.

### Tests for User Story 2

- [ ] T021 [P] [US2] Add `test_topology_figure7_adjacency_invariants` in `tests/unit/test_gym_environment.py` or `tests/unit/test_topology.py` to validate 20 nodes, 20x20 matrix shape, symmetry, zero diagonal, and degree 3 for every node
- [ ] T022 [P] [US2] Add `test_horizontal_legality_neighbor_only_no_self_no_non_neighbor` in `tests/unit/test_gym_environment.py` to forbid self-offload and non-neighbor horizontal offload
- [ ] T023 [P] [US2] Add `test_action_mask_rejects_non_neighbor_horizontal_destinations` in `tests/unit/test_gym_environment.py` to prove the horizontal action mask blocks non-neighbor destinations
- [ ] T024 [P] [US2] Add `test_vertical_cloud_action_not_constrained_by_horizontal_adjacency` in `tests/unit/test_gym_environment.py` to prove vertical/cloud actions stay legal independently of horizontal adjacency
- [ ] T025 [P] [US2] Add a provenance assertion in `tests/integration/test_runtime_adoption_registry_report.py` that the approved adjacency is consumed directly from the Feature 031 registry snapshot and not from a copied runtime artifact

### Implementation for User Story 2

- [ ] T026 [US2] Update `src/environment/topology.py` and `src/environment/gym_adapter.py` so the approved Figure 7 adjacency is loaded directly from `resources/papers/hoodie/recovered/user-approved-assumption-registry.json`
- [ ] T027 [US2] Update `src/environment/gym_adapter.py` and `src/policies/action_masking.py` to enforce neighbor-only horizontal legality, forbid self-offload, and forbid non-neighbor horizontal offload
- [ ] T028 [US2] Update `src/environment/gym_adapter.py` so vertical/cloud legality remains separate from horizontal adjacency legality
- [ ] T029 [US2] Preserve the existing internal indexing convention in topology handling, including 0-based indices if the runtime internals use them

## Phase 5: User Story 3 - Adopt Aggregation and Produce Runtime Adoption Report (Priority: P3)

**Goal**: Reuse the shared aggregation helper/contract, preserve delayed reward timing, and generate a runtime adoption report that proves provenance without claiming paper recovery.

**Independent Test**: A reviewer can inspect the aggregation helper, the report artifact, and the tests to confirm the approved aggregation semantics and audit boundaries.

### Tests for User Story 3

- [ ] T030 [P] [US3] Add `test_aggregation_per_agent_episode_sum_then_mean` in `tests/unit/test_aggregate_metrics.py` or `tests/unit/test_evaluation_metrics.py` to assert per-agent episode sum first, then arithmetic mean across agents
- [ ] T031 [P] [US3] Add `test_aggregation_excludes_nan_no_task_omitted_slots` in `tests/unit/test_aggregate_metrics.py` or `tests/unit/test_evaluation_metrics.py` to assert no-task, NaN, and omitted slots are excluded from numeric aggregation
- [ ] T032 [P] [US3] Add `test_reward_emission_timing_remains_unchanged` in `tests/integration/test_gym_environment.py` to assert reward is still emitted only on task completion or drop
- [ ] T033 [P] [US3] Add `test_feature_032_scope_guard_no_training_policy_dependency_drift` in `tests/integration/test_runtime_adoption_scope_guard.py` to fail on training, neural-network, dependency, policy, baseline, or campaign drift
- [ ] T034 [P] [US3] Add `test_runtime_adoption_report_contents` in `tests/integration/test_runtime_adoption_report.py` to assert consumed assumptions, runtime components changed or validated, tests run, and final verdict are present

### Implementation for User Story 3

- [ ] T035 [US3] Update `src/evaluation/aggregate_metrics.py` and `src/evaluation/metrics.py` to expose a shared helper/contract that performs per-agent episode terminal-reward sum followed by arithmetic mean across agents
- [ ] T036 [US3] Update `src/environment/gym_adapter.py` and `src/evaluation/runner.py` so reward emission timing stays delayed and no-task/NaN/omitted slots are excluded rather than coerced to zero
- [ ] T037 [US3] Generate `artifacts/analysis/runtime-adoption-approved-assumption-registry/runtime-adoption-report.json` in `src/analysis/runtime_adoption_approved_assumption_registry/report.py`
- [ ] T038 [US3] Generate `artifacts/analysis/runtime-adoption-approved-assumption-registry/runtime-adoption-report.md` in `src/analysis/runtime_adoption_approved_assumption_registry/report.py`
- [ ] T039 [US3] Record consumed assumption IDs from `resources/papers/hoodie/recovered/user-approved-assumption-registry.json` and `artifacts/analysis/user-approved-assumption-patch-registry/assumption-patch-report.json` in `src/analysis/runtime_adoption_approved_assumption_registry/report.py`

## Phase 6: Scope Guards and Validation

**Purpose**: Prove only the explicitly scoped runtime/config/evaluation files changed and run the targeted tests with the approved interpreter.

- [ ] T040 Create a git diff scope guard in `tests/integration/test_runtime_adoption_scope_guard.py` that fails if dependency files, training files, neural-network files, policy/baseline/campaign files, or Feature 030 artifacts change
- [ ] T041 Create a paper-registry guard in `tests/integration/test_runtime_adoption_scope_guard.py` that fails if any paper registry is mutated to claim paper recovery
- [ ] T042 Run the targeted unit tests from the approved interpreter in `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python` and record the exact command in `specs/032-runtime-adoption-approved-assumption-registry/quickstart.md`
- [ ] T043 Run the targeted integration tests from the approved interpreter in `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python` and record the exact command in `specs/032-runtime-adoption-approved-assumption-registry/quickstart.md`
- [ ] T044 Capture the final changed-file inventory and classify each path as runtime/config/adoption implementation or intentional analysis artifact in `artifacts/analysis/runtime-adoption-approved-assumption-registry/runtime-adoption-report.md`

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 must complete before any runtime implementation begins.
- Phase 2 blocks all user-story work.
- Phase 3 depends on the registry ingestion helpers from Phase 2.
- Phase 4 depends on the runtime configuration contracts and branch hygiene checks.
- Phase 5 depends on the runtime config and topology changes being in place.
- Phase 6 depends on all runtime adoption work being implemented.

### User Story Dependencies

- **US1**: Can start after Phase 2 and is independent of topology and aggregation work.
- **US2**: Can start after Phase 2 and depends only on the approved topology snapshot.
- **US3**: Can start after Phase 2 and depends on the shared helper/contract and runtime boundary rules.

### Within Each User Story

- Tests must be written before implementation for the corresponding user story.
- Runtime adoption must preserve assumption labels and provenance at every step.
- Scope guards must fail fast on any polluted diff.

## Parallel Opportunities

- `T012`, `T013`, `T014`, `T015`, and `T016` can run in parallel because they validate distinct runtime contract surfaces.
- `T021`, `T022`, `T023`, and `T024` can run in parallel because they exercise separate topology and legality checks.
- `T030`, `T031`, `T032`, and `T034` can run in parallel because they cover distinct aggregation, reward timing, and report concerns.

## Implementation Strategy

### MVP First

1. Complete Phases 1-2.
2. Complete User Story 1 runtime config adoption.
3. Stop and validate the approved CPU, link-rate, and timeout values before topology or aggregation work.

### Incremental Delivery

1. Adopt compute, link-rate, and timeout contracts first.
2. Add topology and legality adoption next.
3. Finish with aggregation, report generation, and scope guards.

### Parallel Team Strategy

1. One contributor handles US1 runtime config adoption.
2. One contributor handles US2 topology and legality adoption.
3. One contributor handles US3 aggregation, reporting, and scope guards.

