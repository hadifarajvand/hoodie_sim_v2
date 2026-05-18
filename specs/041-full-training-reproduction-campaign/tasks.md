# Tasks: Full Training/Reproduction Campaign

**Input**: Design artifacts from `specs/041-full-training-reproduction-campaign/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`
**Branch**: `041-full-training-reproduction-campaign`

**Dependency gate**: This feature is blocked unless the Feature 041 prerequisite state is clean and the approved interpreter can use the existing `torch` install. Do not add dependency files or guess the target-update unit.

## Format: `[ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel only when it does not depend on incomplete work in the same files.
- **[US1]**: Readiness gate and target-update approval.
- **[US2]**: Replay, pilot training, and campaign execution.
- **[US3]**: Evaluation, reporting, and scope guard.
- No task in this feature may authorize blind 5000-episode execution, fake terminal rewards, target-update guessing, output tuning, or environment/runtime/policy drift.

## Phase 1: Setup and Gates

- [X] T001 Verify the feature branch and repository prerequisite state before any implementation work:
  - current branch == `041-full-training-reproduction-campaign`
  - current branch != `main`
  - `main == origin/main`
  - `main == 040-smoke-training-complete^{}` 
  - `git diff --name-only 040-smoke-training-complete^{} main` is empty
  - `.specify/feature.json` may be present only as a local active-feature pointer
  - `.specify/feature.json` must not be staged
  - `.specify/feature.json` must not appear in `git diff --name-only main...HEAD`
  - no unrelated dirty files are present
  - implementation is blocked if any assertion fails
- [X] T002 Check prior feature gate artifacts and record the result for the campaign:
  - verify Feature 037 baseline revalidation report exists and is valid
  - verify Feature 038 training foundation report exists and is valid
  - verify Feature 039 paper HOODIE network report exists and is valid
  - verify Feature 040 smoke training report exists and is valid
  - do not modify prior feature artifacts
- [X] T003 Check the campaign dependency state in the approved interpreter and record the result:
  - verify whether `torch` imports successfully in `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`
  - verify no dependency files are modified
  - if `torch` is unavailable, the campaign must stop after emitting a readiness-blocked or dependency-blocked report
  - do not add, remove, or edit dependency declarations

## Phase 2: Foundational Prerequisites

- [X] T004 Define the campaign config and approval contract in `src/analysis/full_training_reproduction_campaign/`:
  - `CampaignConfig`
  - `TargetUpdateContract`
  - `CampaignStage`
  - `ReadinessProbeResult`
  - `PilotBudget`
  - validate `target_update_unit == optimizer_step`
  - validate first pilot budget is 10 episodes
  - validate optional follow-on pilot budget is 25 episodes
  - validate full campaign budget is configured but not auto-executed
- [X] T005 [P] Define the campaign reporting schema in `src/analysis/full_training_reproduction_campaign/`:
  - required readiness report fields from the spec
  - required training-campaign report fields from the spec
  - baseline-reference-only status handling
  - candidate reproduction claim status handling
  - no-performance-metrics rule
- [X] T006 [P] Define the campaign replay contract in `src/analysis/full_training_reproduction_campaign/`:
  - campaign-scoped `ReplayBuffer`
  - `ReplayTransition` fields for `reward_available`, `terminal_slot`, `outcome`, and `pending_at_horizon`
  - preserve Feature 038 schema compatibility
  - reject fake terminal samples
  - preserve delayed reward metadata

## Phase 3: User Story 1 - Readiness Gate and Target-Update Approval (Priority: P1)

**Goal**: Prove the campaign is explicitly approved to progress before any pilot or full training starts.

**Independent Test**: The readiness probe reports the exposure evidence, target-update approval status, and a block reason when the campaign is not ready.

- [X] T007 [US1] Implement the readiness probe in `src/analysis/full_training_reproduction_campaign/` to run through `HoodieGymEnvironment`, measure and report `probe_episode_count`, `probe_step_count`, `generated_task_count`, `transition_count`, `completed_task_count`, `dropped_task_count`, `pending_at_horizon_count`, `terminal_transition_count`, `reward_bearing_transition_count`, `non_terminal_transition_count`, `terminal_transition_ratio`, `reward_bearing_transition_ratio`, `pending_at_horizon_ratio`, `illegal_action_count`, `illegal_action_ratio`, `action_count_by_type`, `local_action_count`, `horizontal_action_count`, `vertical_action_count`, `readiness_manual_approval_required`, `readiness_manual_approval_status`, and `readiness_block_reason`, and emit a readiness-blocked report when the gate is not met
- [X] T008 [P] [US1] Add contract tests in `tests/unit/test_full_training_campaign_config.py` for target-update approval, staged budgets, explicit 5000-episode gating, and config validation
- [X] T009 [P] [US1] Add readiness-gate tests in `tests/integration/test_campaign_readiness_gate.py` for blocked readiness, exposure summaries, and manual approval requirements
- [X] T010 [P] [US1] Add readiness-report schema tests in `tests/integration/test_campaign_readiness_gate.py` verifying `probe_episode_count`, `probe_step_count`, `generated_task_count`, `transition_count`, `completed_task_count`, `dropped_task_count`, `pending_at_horizon_count`, `terminal_transition_count`, `reward_bearing_transition_count`, `non_terminal_transition_count`, `terminal_transition_ratio`, `reward_bearing_transition_ratio`, `pending_at_horizon_ratio`, `illegal_action_count`, `illegal_action_ratio`, `action_count_by_type`, `local_action_count`, `horizontal_action_count`, `vertical_action_count`, `readiness_manual_approval_required`, `readiness_manual_approval_status`, and `readiness_block_reason`
- [X] T011 [US1] Record the approved target-update unit and rationale in `src/analysis/full_training_reproduction_campaign/` without silently inferring paper “iteration” semantics

## Phase 4: User Story 2 - Replay, Pilot Training, and Campaign Execution (Priority: P2)

**Goal**: Execute a bounded pilot campaign that proves the training loop, replay contract, and target-update schedule without becoming blind full training.

**Independent Test**: A pilot run completes on live environment replay, produces finite DDQN loss, updates legal actions only, and records checkpoint metadata while respecting the approved target-update unit. The gated full-campaign runner remains blocked until readiness and pilot gates pass and the explicit 5000-episode flag/command is supplied.

- [X] T012 [P] [US2] Implement the campaign replay buffer in `src/analysis/full_training_reproduction_campaign/` to store live `HoodieGymEnvironment` rollouts only, preserve delayed rewards, and keep pending-at-horizon explicit
- [X] T013 [US2] Implement the DDQN trainer and pilot runner in `src/analysis/full_training_reproduction_campaign/` using the Feature 039 online/target networks, Adam, learning_rate `7e-7`, gamma `0.99`, and the approved target-update unit
- [X] T014 [P] [US2] Add replay-contract tests in `tests/unit/test_full_training_replay_contract.py` covering delayed rewards, pending-at-horizon handling, terminal-slot/outcome storage, and rejection of fake terminal samples
- [X] T015 [P] [US2] Add pilot-training tests in `tests/integration/test_full_training_pilot.py` covering finite loss, legal action selection, replay growth, checkpoint metadata, and approved-unit target sync behavior
- [X] T016 [US2] Implement checkpoint metadata writing in `src/analysis/full_training_reproduction_campaign/` and emit checkpoints only when the metadata schema passes
- [X] T017 [US2] Implement the gated `full_training_candidate` / `final_reproduction_campaign` runner in `src/analysis/full_training_reproduction_campaign/` so that 5000-episode execution stays blocked by default until readiness and pilot gates pass and an explicit command/flag is supplied
- [X] T018 [P] [US2] Add full-campaign gate tests in `tests/integration/test_full_training_candidate_gate.py` proving the campaign cannot run before readiness approval, cannot run before pilot success, cannot run without explicit flag/command, and exposes the discoverable command path in `quickstart.md`

## Phase 5: User Story 3 - Evaluation, Reporting, and Scope Guard (Priority: P3)

**Goal**: Report campaign outcomes honestly with disjoint evaluation traces and explicit no-reproduction-by-default language.

**Independent Test**: The report artifacts distinguish readiness evidence, pilot evidence, baseline reference context, and candidate reproduction status without curve fitting or automatic success claims.

- [X] T019 [P] [US3] Implement the campaign evaluation flow in `src/analysis/full_training_reproduction_campaign/` using fixed disjoint evaluation trace banks and no training-trace reuse
- [X] T020 [P] [US3] Generate the campaign report artifacts in `artifacts/analysis/full-training-reproduction-campaign/` as JSON and Markdown
- [X] T021 [P] [US3] Add report schema tests in `tests/integration/test_full_training_report.py` for readiness evidence, pilot evidence, baseline-reference-only status, and candidate reproduction claim handling
- [X] T022 [US3] Add the scope guard in `tests/integration/test_full_training_scope_guard.py` to allow only the approved campaign paths and read-only imports from Feature 039, Feature 040, and Feature 038 analysis packages
- [X] T023 [US3] Ensure the campaign report records `no_curve_fitting=true`, `no_simulator_output_tuning=true`, `no_target_update_execution=false` only when explicitly approved, and `no_paper_reproduction_claim` by default in `src/analysis/full_training_reproduction_campaign/`

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T024 Run the required validation command exactly as specified:
  - `PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \`
  - `  tests.unit.test_full_training_campaign_config \`
  - `  tests.unit.test_full_training_replay_contract \`
  - `  tests.integration.test_campaign_readiness_gate \`
  - `  tests.integration.test_full_training_candidate_gate \`
  - `  tests.integration.test_full_training_pilot \`
  - `  tests.integration.test_full_training_report \`
  - `  tests.integration.test_full_training_scope_guard \`
  - `  tests.unit.test_smoke_training_contract \`
  - `  tests.integration.test_smoke_training_report \`
  - `  tests.integration.test_smoke_training_determinism \`
  - `  tests.unit.test_paper_hoodie_network_config \`
  - `  tests.unit.test_paper_hoodie_network_shapes \`
  - `  tests.integration.test_paper_hoodie_network_report \`
  - `  tests.unit.test_training_foundation_contract \`
  - `  tests.integration.test_training_foundation_contract_report \`
  - `  tests.integration.test_training_readiness_gate \`
  - `  tests.unit.test_execution_model \`
  - `  tests.unit.test_task_compute_state \`
  - `  tests.unit.test_deadline_expiration \`
  - `  tests.unit.test_link_rate_config \`
  - `  tests.unit.test_link_rate_transmission_delay \`
  - `  tests.unit.test_public_cloud_capacity_sharing \`
  - `  tests.unit.test_reproducibility_bundle \`
  - `  tests.unit.test_runtime_adoption_approved_assumption_registry \`
  - `  tests.integration.test_execution_time_contract_report \`
  - `  tests.integration.test_execution_time_flow \`
  - `  tests.integration.test_transmission_delay_runtime_report \`
  - `  tests.integration.test_transmission_delay_runtime_wiring \`
  - `  tests.integration.test_public_cloud_capacity_sharing_report \`
  - `  tests.integration.test_public_cloud_capacity_sharing_flow \`
  - `  tests.integration.test_deadline_timeout_off_by_one_report \`
  - `  tests.integration.test_reproducibility_bundle_flow`
- [X] T025 Confirm `.specify/feature.json` remains local-only and is not included in the committed 041 diff; update `specs/041-full-training-reproduction-campaign/quickstart.md` only if the validation text needs tightening

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in priority order
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on the approved target-update unit, campaign replay contract, and explicit full-campaign gating
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on readiness and pilot outputs, but remains independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Readiness gates before pilot execution
- Replay before trainer
- Trainer before checkpointing and reporting
- Story complete before moving to next priority

### Parallel Opportunities

- T005 and T006 can run in parallel because they touch separate schema files
- T008 and T009 can run in parallel because one covers config contract and the other covers readiness-gate behavior
- T013 and T014 can run in parallel because one covers replay contracts and the other covers pilot execution
- T019 and T021 can run in parallel because one covers evaluation flow and the other covers report schema

## Parallel Example: User Story 2

```bash
# Launch the replay contract tests and pilot tests together:
Task: "Add replay-contract tests in tests/unit/test_full_training_replay_contract.py"
Task: "Add pilot-training tests in tests/integration/test_full_training_pilot.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational prerequisites
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Confirm readiness probe evidence, explicit target-update approval, and readiness-blocked behavior when gates fail

### Incremental Delivery

1. Complete Setup + Foundational → campaign contracts ready
2. Add User Story 1 → readiness probe and approval gate
3. Add User Story 2 → bounded pilot training with live replay and checkpointing
4. Add User Story 3 → evaluation, reporting, and scope guard

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- The campaign is not paper reproduction by default
- Feature 038 readiness stays blocked; Feature 041 is a staged campaign feature, not a readiness override
- The approved target-update unit is `optimizer_step` and is a user-approved campaign assumption, not a paper-defined fact
