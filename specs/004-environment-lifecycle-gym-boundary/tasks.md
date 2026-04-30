# Tasks: 004-environment-lifecycle-gym-boundary

## Phase 1: Setup

**Goal**: confirm the feature scope, contract, and existing adapter entry points before touching behavior.

**Independent Test Criteria**: The existing plan, contract, and quickstart describe the same adapter boundary and same-slot handling rules.

- [ ] T001 Review `specs/004-environment-lifecycle-gym-boundary/plan.md`, `specs/004-environment-lifecycle-gym-boundary/contracts/environment-boundary.md`, and `src/environment/gym_adapter.py` to confirm the documented single-active-task contract matches the current adapter shape and note any remaining implementation mismatches in `specs/004-environment-lifecycle-gym-boundary/research.md`
- [ ] T002 [P] Update paper-to-code mapping in `docs/paper_notes/paper_to_code_mapping.md` for the adapter boundary, one-slot step contract, delayed reward timing, and same-slot deterministic presentation order

## Phase 2: Foundational

**Goal**: make the environment contract explicit before story-specific implementation work begins.

**Independent Test Criteria**: the adapter contract, observation shape, and truncation semantics are documented and traceable before code changes land.

- [ ] T003 [P] Add or refine the environment contract section in `specs/004-environment-lifecycle-gym-boundary/contracts/environment-boundary.md` so it explicitly states slot-horizon truncation, single-active-task presentation, and the external baseline control model
- [ ] T004 [P] Update `specs/004-environment-lifecycle-gym-boundary/data-model.md` to reflect the slot-scoped observation mapping, active-task lifecycle, and pending-arrival ordering used by the adapter
- [ ] T005 [P] Update `specs/004-environment-lifecycle-gym-boundary/quickstart.md` so it describes the external baseline loop and the no-dependency adapter usage clearly enough for implementers and testers

## Phase 3: User Story 1 - Deterministic Environment Boundary

**Goal**: reset/step must be deterministic, policy-agnostic, and compatible with the current baseline loop.

**Independent Test Criteria**: resetting with the same seed and running the same baseline twice yields the same trace, reward sequence, and terminal outcomes.

- [X] T006 [US1] Implement configured slot-horizon truncation in `src/environment/gym_adapter.py::step()` and propagate the truncation flag through the returned tuple and `info`
- [X] T007 [US1] Add deterministic same-slot presentation ordering in `src/environment/gym_adapter.py` so multiple arrivals in one slot are queued and exposed one active task at a time without losing pending tasks
- [X] T008 [P] [US1] Update `specs/004-environment-lifecycle-gym-boundary/plan.md`, `specs/004-environment-lifecycle-gym-boundary/research.md`, `specs/004-environment-lifecycle-gym-boundary/contracts/environment-boundary.md`, and any relevant comments in `src/environment/gym_adapter.py` or `src/environment/slot_engine.py` to state the final orchestration decision: `HoodieGymEnvironment` owns episode orchestration; `SlotEngine` provides helper methods only. Do not move lifecycle ownership into `SlotEngine` in this feature.
- [ ] T009 [US1] Extend or adjust `tests/unit/test_gym_environment.py` to verify `reset(seed)` determinism, `terminated` versus `truncated`, and that the same seed plus same baseline policy produces the same trace

## Phase 4: User Story 2 - Shared Lifecycle Semantics

**Goal**: keep queueing, offload progression, public queue admission, terminal resolution, delayed reward, and metrics on the shared path.

**Independent Test Criteria**: one full episode through the adapter exercises local execution, horizontal offload, vertical offload, delayed reward timing, and shared metric updates.

- [X] T010 [US2] Implement or wire the queue/admission progression in `src/environment/gym_adapter.py` and `src/environment/slot_engine.py` so local execution, horizontal offload, vertical offload, and public-queue admission after offload all flow through the same lifecycle state
- [X] T011 [US2] Ensure delayed reward emission stays terminal-only in `src/environment/reward_timing.py`, `src/environment/gym_adapter.py`, and `src/environment/environment.py`, and that reward is emitted only after completion/drop timing
- [X] T012 [P] [US2] Update `src/evaluation/metrics.py`, `src/evaluation/evaluation_module.py`, and any adapter info assembly in `src/environment/gym_adapter.py` so per-slot finalized task records feed the shared evaluation path without changing metric formulas
- [ ] T013 [US2] Add or update `tests/unit/test_delayed_reward.py`, `tests/unit/test_offload_next_slot.py`, `tests/unit/test_public_queue_routing.py`, and `tests/unit/test_task_lifecycle.py` to cover local admission, horizontal offload, vertical cloud offload, public queue admission after offload, and delayed reward timing

## Phase 5: User Story 3 - Topology-Constrained Action Selection

**Goal**: keep legality checks and observation masks consistent with topology and policy expectations.

**Independent Test Criteria**: the action mask reflects topology, illegal actions are rejected, and the observation shape is usable by the existing baseline policies.

- [X] T014 [US3] Update `src/environment/gym_adapter.py::observe()` to return the contract shape: a slot-scoped mapping keyed by edge-agent ID with per-agent task fields, legal-action masks, and lifecycle/debug metadata
- [X] T015 [US3] Add a compatibility or migration layer in `src/environment/gym_adapter.py` or `src/policies/policy_interface.py` so existing callers that expect a flat observation are either preserved through a wrapper or explicitly migrated in code comments and docs
- [ ] T016 [P] [US3] Verify `src/policies/action_masking.py`, `src/policies/policy_interface.py`, and `src/environment/topology.py` continue to reject illegal actions and expose the same shared legality semantics to all baselines
- [X] T017 [US3] Add or update `tests/unit/test_topology_legality.py`, `tests/unit/test_gym_environment.py`, and `tests/integration/test_policy_interface_flow.py` to cover illegal action rejection and the slot-scoped observation contract

## Phase 6: User Story 4 - Gymnasium-Style Adapter Boundary

**Goal**: ensure the adapter is the clean external boundary for baseline evaluation and not a hidden policy runner.

**Independent Test Criteria**: a baseline can run through the adapter externally, with no internal policy execution requirement.

- [X] T018 [US4] Make the adapter/baseline ownership explicit in `src/environment/gym_adapter.py`, `src/environment/environment.py`, and `specs/004-environment-lifecycle-gym-boundary/contracts/environment-boundary.md` so the adapter stays policy-agnostic and any convenience episode runner remains a thin wrapper only
- [X] T019 [P] [US4] Update `src/evaluation/runner.py`, `src/evaluation/validation_runner.py`, and any baseline entry points that call the environment so they continue to drive `reset()` and `step()` externally
- [X] T020 [US4] Add or update `tests/integration/test_evaluation_runner.py` and `tests/integration/test_flc_episode.py` so at least one baseline completes a full episode through the adapter boundary

## Phase 7: Polish & Cross-Cutting

**Goal**: close the remaining traceability, documentation, and verification gaps without broad cleanup.

**Independent Test Criteria**: the feature docs, tests, and mapping files agree on the final adapter contract and no dependency changes were introduced.

- [ ] T021 [P] Update `docs/paper_notes/paper_to_code_mapping.md` with the final environment boundary, same-slot arrival handling, and delayed reward lifecycle notes after implementation lands
- [ ] T022 [P] Update `docs/assumptions/hoodie_assumptions.md` only if the implementation introduces any new assumption beyond the documented single-active-task contract for same-slot arrivals
- [ ] T023 [P] Add a no-dependency-change verification note in `specs/004-environment-lifecycle-gym-boundary/quickstart.md` or a short test note in `tests/unit/test_gym_environment.py` that confirms the feature did not alter dependency files
- [ ] T024 Remove any now-unused imports only in the files already touched by this feature, and only if those imports are in the direct edit path for the lifecycle changes

## Dependencies

- Phase 1 establishes the feature scope and paper-to-code mapping.
- Phase 2 documents the interface and data model before behavior changes.
- Phase 3 depends on Phase 2 and resolves deterministic reset/step behavior first.
- Phase 4 depends on Phase 3 because queueing, offload, and reward timing must run on the stabilized boundary.
- Phase 5 depends on Phase 3 because the observation contract and legality semantics depend on the stable adapter shape.
- Phase 6 depends on Phases 3-5 because the external baseline loop must use the finalized boundary.
- Phase 7 depends on all previous phases being complete.

## Parallel Execution Examples

### User Story 1

- `T006` can run in parallel with `T007` once the expected truncation and same-slot contract are agreed.
- `T008` can run alongside `T009` because documentation/orchestration clarification and test coverage are mostly independent.

### User Story 2

- `T010` can run in parallel with `T011` if queue orchestration and reward emission are split across different files.
- `T012` can run in parallel with `T013` because metrics/evaluation updates and lifecycle tests target different surfaces.

### User Story 3

- `T014` can run in parallel with `T015` because observation shape migration and compatibility handling can be split across adapter and policy-facing surfaces.
- `T016` can run in parallel with `T017` because legality verification and test coverage target different files.

### User Story 4

- `T018` can run in parallel with `T019` because adapter ownership documentation and runner wiring touch different layers.
- `T019` can run in parallel with `T020` because baseline runner wiring and integration test updates are separate.

## Implementation Strategy

### MVP first

1. Land Phase 2 contract/data-model updates.
2. Implement Phase 3 deterministic reset/step behavior, including truncation and same-slot ordering.
3. Run the baseline flow through the adapter with the existing external policy loop.

### Incremental delivery

1. Add lifecycle progression and delayed reward validation.
2. Add observation-shape migration and legality tests.
3. Finish with traceability, paper mapping, and the no-dependency verification note.

## Validation Checklist

- [ ] All tasks use the required checklist format with IDs and file paths
- [ ] Every user story has at least one implementation task and one test task
- [ ] The known mismatches from the current codebase are each covered by at least one task
- [ ] No TorchRL, neural-network, ns-3-gym, or dependency-change tasks were added
- [ ] The task list is ordered so the environment boundary is stabilized before baseline and evaluation wiring
