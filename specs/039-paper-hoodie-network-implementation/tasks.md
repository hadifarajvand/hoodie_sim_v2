# Tasks: Paper HOODIE Network Implementation

**Input**: Design artifacts from `specs/039-paper-hoodie-network-implementation/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`, `checklists/requirements.md`
**Branch**: `039-paper-hoodie-network-implementation`

**Dependency gate**: This feature is dependency-blocked unless `torch` is already available in the approved interpreter. If `torch` is unavailable, the implementation stops after generating a `dependency_blocked` report and no dependency files are edited.

## Format: `[ID] [P?] [US?] Description`

- **[P]**: Can run in parallel with other tasks only when it does not depend on incomplete work in the same files.
- **[US1]**: Architecture contract for future training.
- **[US2]**: Dueling, Double-DQN, and LSTM separation.
- **[US3]**: Readiness-aware network surface.
- No task in this feature may authorize training, optimizer steps, replay execution, campaign runners, or environment/runtime/policy changes.

## Phase 1: Setup and gates

- [X] T001 Verify the feature branch and repository prerequisite state before any implementation work:
  - `git branch --show-current == 039-paper-hoodie-network-implementation`
  - current branch != main
  - `git rev-parse main == git rev-parse origin/main`
  - git rev-parse main == git rev-parse 038-training-foundation-contract-complete^{}
  - `git diff --name-only 038-training-foundation-contract-complete^{} main` is empty
  - `.specify/feature.json points to specs/039-paper-hoodie-network-implementation`
  - `.specify/feature.json does not point to specs/036-deadline-timeout-off-by-one-audit`
  - `specs/039-paper-hoodie-network-implementation/ exists`
  - `git status --short may contain .specify/feature.json only as a local active-feature pointer`
  - `git status --short may contain specs/039-paper-hoodie-network-implementation/`
  - `git status --short must not contain other dirty files`
  - `.specify/feature.json must not be staged`
  - `.specify/feature.json must not appear in git diff --name-only main...HEAD`
  - implementation is blocked if any assertion fails
- [X] T002 Check dependency availability in the approved interpreter and record the result for the feature:
  - verify whether `torch` imports successfully in `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`
  - verify no dependency files are modified
  - if `torch` is unavailable, generate the `dependency_blocked` report and stop without dependency edits
  - do not add, remove, or edit dependency declarations

## Phase 2: Foundation

- [X] T003 [US1] Define the `PaperHoodieNetworkConfig` contract in `src/analysis/paper_hoodie_network_implementation/` and validate the architecture-only fields:
  - separate `q_network_hidden_layers` from `lstm_hidden_size` and `lstm_num_layers`
  - require `q_network_hidden_layers == [1024, 1024, 1024]`
  - require `lstm_num_layers == 1`
  - require `lstm_hidden_size == 20`
  - require `lstm_lookback_w == 10`
  - require `action_count == 3`
  - reject sloppy `N_L` coupling or any reused field that conflates Q-network and LSTM configuration
  - reject any config that expands the stable Feature 038 action space
- [X] T004 [US3] Define the architecture data model and report schema contracts in `src/analysis/paper_hoodie_network_implementation/`:
  - `PaperHoodieNetworkConfig`
  - `LstmEncoder`
  - `QNetworkBody`
  - `DuelingHeads`
  - `OnlineTargetNetworkPair`
  - `ShapeValidationReport`
  - include explicit dependency status reporting and no-training flags in the report schema

## Phase 3: User Story 1 - Architecture Contract for Future Training

**Goal**: Instantiate and validate the architecture deterministically without training, replay, or optimization.

**Independent Test**: The architecture can be instantiated deterministically and its shapes can be validated without any optimizer step, replay sampling, or campaign execution.

- [X] T005 [P] [US1] Add config validation tests in `tests/unit/test_paper_hoodie_network_config.py`:
  - `test_network_config_separates_q_and_lstm_layers`
  - `test_network_config_rejects_sloppy_n_l_coupling`
  - `test_action_count_matches_feature_038_contract`
  - reject `q_network_hidden_layers == 20`
  - reject `lstm_hidden_size == 1024`
  - reject missing separate `q_network_hidden_layers`
  - reject missing separate `lstm_hidden_size` and `lstm_num_layers`
- [ ] T006 [US1] Implement the LSTM encoder and shared Q-network body contract in `src/analysis/paper_hoodie_network_implementation/`:
  - accept input in `batch_size x lookback_w x state_dim`
  - encode the `W=10` history with one LSTM layer before the body
  - implement the `3 x 1024` Q-network body
  - keep the LSTM configuration independent from the Q-network hidden-layer configuration

## Phase 4: User Story 2 - Dueling, Double-DQN, and LSTM Separation

**Goal**: Separate value/advantage processing and expose compatible online/target network APIs without training logic.

**Independent Test**: The configuration and shape checks confirm that Q-network hidden layers and LSTM hidden settings are independently defined and that online/target networks are architecture-compatible.

- [ ] T007 [P] [US2] Add shape and determinism tests in `tests/unit/test_paper_hoodie_network_shapes.py`:
  - `test_lstm_forward_accepts_lookback_w_10`
  - `test_dueling_network_outputs_batch_by_action_count`
  - `test_dueling_q_aggregation_shape`
  - `test_online_target_networks_are_architecture_compatible`
  - `test_deterministic_initialization_with_model_seed`
  - validate input shape `batch_size x W x state_dim`
  - validate output shape `batch_size x 3`
- [ ] T008 [US2] Implement the dueling heads and Q aggregation contract in `src/analysis/paper_hoodie_network_implementation/`:
  - add separate value and advantage heads after the shared body
  - combine outputs with `Q(s,a) = V(s) + A(s,a) - mean_a A(s,a)`
  - emit stable Q-values for action count 3
  - preserve the generic horizontal action as metadata-resolved, not per-destination
- [ ] T009 [US2] Implement the online/target network factory surface in `src/analysis/paper_hoodie_network_implementation/`:
  - build architecture-compatible online and target network instances
  - expose forward APIs needed for later Double-DQN-compatible use
  - do not implement target updates
  - do not implement Double-DQN loss
  - do not implement any optimizer or training loop
  - if `torch` is already approved and present, keep `src/models/hoodie_network.py` aligned with the same contract

## Phase 5: User Story 3 - Readiness-Aware Network Surface

**Goal**: Produce report artifacts and guardrails that prove the feature did not start training or drift into runtime behavior.

**Independent Test**: Report artifacts and tests show that no training loop, optimizer step, replay execution, or environment change was introduced.

- [X] T010 [P] [US3] Add regression tests in `tests/unit/test_paper_hoodie_network_shapes.py` and `tests/integration/test_paper_hoodie_network_scope_guard.py`:
  - `test_no_training_optimizer_replay_execution_added`
  - `test_no_dependency_environment_policy_reward_drift`
  - ensure no training loop, optimizer step, replay execution, environment drift, policy drift, or reward timing drift is introduced
  - keep the Feature 038 readiness block respected
- [X] T011 [US3] Generate the architecture report artifacts under `artifacts/analysis/paper-hoodie-network-implementation/`:
  - `network-implementation-report.json`
  - `network-implementation-report.md`
  - include `dependency_status`
  - include `no_training_started = true`
  - include `no_optimizer_step = true`
  - include `no_replay_execution = true`
  - include `no_environment_contract_drift = true`
  - include `no_reward_timing_change = true`
  - include `no_policy_drift = true`
  - include `no_dependency_drift = true`
  - include `no_curve_fitting = true`
  - include `no_paper_reproduction_claim = true`
  - if `torch` is unavailable, the report must state `dependency_status=blocked_missing_existing_torch`
- [X] T012 [US3] Add the scope-guard test in `tests/integration/test_paper_hoodie_network_scope_guard.py`:
  - Allowed committed paths:
    - `specs/039-paper-hoodie-network-implementation/`
    - `src/analysis/paper_hoodie_network_implementation/`
    - `src/models/hoodie_network.py` only if torch is already available
    - `tests/unit/test_paper_hoodie_network_config.py`
    - `tests/unit/test_paper_hoodie_network_shapes.py`
    - `tests/integration/test_paper_hoodie_network_report.py`
    - `tests/integration/test_paper_hoodie_network_scope_guard.py`
    - `artifacts/analysis/paper-hoodie-network-implementation/`
  - Local-only allowed path:
    - `.specify/feature.json`, only while it points to `specs/039-paper-hoodie-network-implementation` and only if it is not staged and not included in `main...HEAD`
  - Forbidden in committed branch diff:
    - `.specify/feature.json`
    - dependency files
    - `src/environment/`
    - `src/policies/`
    - `src/training/`
    - `src/replay/`
    - `src/memory/`
    - optimizer code
    - campaign runners
    - resources/papers/
    - paper registries
    - Feature 038 artifacts
    - Feature 037 artifacts

## Phase 6: Final verification

- [ ] T013 Run the required validation command exactly as specified and record the outcome:
  - `PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \`
    - `tests.unit.test_paper_hoodie_network_config`
    - `tests.unit.test_paper_hoodie_network_shapes`
    - `tests.integration.test_paper_hoodie_network_report`
    - `tests.integration.test_paper_hoodie_network_scope_guard`
    - `tests.unit.test_training_foundation_contract`
    - `tests.integration.test_training_foundation_contract_report`
    - `tests.integration.test_training_readiness_gate`
    - `tests.integration.test_training_foundation_scope_guard`
  - fail the feature if any test implies training, optimizer, replay execution, or dependency edits are needed

## Dependency Order

1. T001
2. T002
3. T003
4. T004
5. T005
6. T006
7. T007
8. T008
9. T009
10. T010
11. T011
12. T012
13. T013

## Parallel Opportunities

- T005 and T010 can run in parallel because they touch separate test files.
- T007 can run in parallel with T008 and T009 after T006 is in place, because the tests validate the implemented network contract.
- T011 can run after T009 without waiting on T012 if the report generator only reads the architecture contract and writes the report artifacts.

## Implementation Strategy

- MVP: complete T001 through T006 so the architecture config and encoder/body contract exist.
- Next: complete T007 through T009 so the dueling heads, online/target APIs, and shape tests lock the architecture surface.
- Final: complete T010 through T013 so the scope guard, report artifacts, and validation command prove no training or dependency drift occurred.

## Notes

- This task graph is intentionally architecture-only.
- Any task that would require training, replay execution, optimizer steps, dependency edits, or runtime/policy/reward drift is out of scope and must not be added later without an explicit spec update.
