# Tasks: Task Execution Time & Compute Resource Modeling

**Input**: Design documents from `/specs/006-task-execution-time-compute-model/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Organization**: Tasks are grouped by user story and dependency phase so compute execution can be added without changing lifecycle ownership, traffic generation, or baseline policy behavior.

## Phase 1: Setup (Shared Documentation and Traceability)

**Purpose**: Align the paper-backed compute feature docs with the planned execution boundary before code changes begin.

- [X] T001 [P] Review and align `specs/006-task-execution-time-compute-model/spec.md` so the compute-budget, destination-based execution, and reward-timing scope match the approved feature plan.
- [X] T002 [P] Review and align `specs/006-task-execution-time-compute-model/plan.md` so the constitution gate, architecture, affected modules, and no-dependency policy match the approved compute feature boundary.
- [X] T003 [P] Review and align `specs/006-task-execution-time-compute-model/research.md` so it records only paper-backed compute decisions and explicitly documents unresolved capacity assumptions instead of inventing behavior.
- [X] T004 [P] Review and align `specs/006-task-execution-time-compute-model/data-model.md` so `ComputeConfig`, `TaskExecutionState`, `ExecutionProgressRecord`, and `TerminalOutcome` are described consistently.
- [X] T005 [P] Review and align `specs/006-task-execution-time-compute-model/contracts/compute-execution.md` so the execution API and environment compatibility contract match the planned compute boundary.
- [X] T006 [P] Review and align `specs/006-task-execution-time-compute-model/quickstart.md` so it shows compute capacity setup, execution progression, and the no-dependency-change note.

**Checkpoint**: Compute docs are aligned to the paper-backed boundary and ready for implementation.

## Phase 2: Foundational Compute Configuration and State

**Purpose**: Establish the paper-backed compute configuration and task state fields that all execution helpers depend on.

- [X] T007 [P] Add `src/environment/compute_config.py` with `ComputeConfig` and deterministic preset capacity fields for local, edge, and cloud execution contexts.
- [X] T008 [P] Update `src/environment/task.py` and `src/evaluation/trace_protocol.py` so task records carry `cycles_required` and `cycles_remaining` alongside the existing lifecycle fields and preserve float-valued compute budgets.
- [X] T009 [P] Add `tests/unit/test_compute_config.py` and `tests/unit/test_task_compute_state.py` verifying compute-capacity values, derived compute budgets, and backward-compatible task construction.

**Checkpoint**: Compute capacity and task execution state are executable and validated.

## Phase 3: User Story 1 - Compute-Based Execution Timing (Priority: P1)

**Goal**: Derive task execution budgets from task size and processing density, then decrement them deterministically as execution advances.

**Independent Test**: Create a task with known size and processing density, then verify the required cycles are computed from those inputs and decrease predictably slot by slot.

- [X] T010 [P] [US1] Add `src/environment/execution_helper.py` implementing deterministic cycle decrement logic for a single active task under a configured destination capacity.
- [X] T011 [P] [US1] Add `tests/unit/test_execution_model.py` verifying compute-budget calculation, cycle decrement behavior, exact-zero completion handling, and persistence of fractional paper values.
- [X] T012 [US1] Integrate compute-budget initialization into `src/environment/gym_adapter.py` and `src/environment/traffic_generator.py` only as needed so generated tasks enter execution with required and remaining cycles populated.

**Checkpoint**: Task compute budgets are paper-backed and execution can progress deterministically by slot.

## Phase 4: User Story 2 - Destination-Based Execution Progression (Priority: P1)

**Goal**: Keep offloaded tasks executing at their destination compute rate until they complete or drop.

**Independent Test**: Execute the same task through local, edge, and cloud paths and verify that each path consumes compute budget according to the configured destination capacity.

- [X] T013 [P] [US2] Extend `src/environment/gym_adapter.py` so execution progression applies destination-specific compute capacity during slot advancement without changing lifecycle ownership.
- [X] T014 [P] [US2] Add `tests/integration/test_execution_time_flow.py` proving a generated task completes in the expected number of slots under known local, edge, and cloud capacities.
- [X] T015 [US2] Update `src/environment/reward_timing.py` and `src/environment/gym_adapter.py` only as needed so reward emission remains delayed until completion or drop after compute exhaustion.

**Checkpoint**: Offloaded and local tasks progress through execution with deterministic destination-specific compute timing.

## Phase 5: User Story 3 - Reward Timing and Execution Visibility (Priority: P2)

**Goal**: Surface compute progression in observability and keep reward timing aligned with terminal execution outcomes.

**Independent Test**: Run a task through execution and confirm reward is emitted only after completion or drop, never during intermediate execution slots.

- [X] T016 [P] [US3] Extend `src/environment/traffic_observer.py` so execution timing summaries report compute-budget progression and terminal timing statistics.
- [X] T017 [P] [US3] Add `tests/unit/test_execution_observer.py` verifying execution summary metrics, terminal timing counts, and reward-visible terminal outcomes.

**Checkpoint**: Execution progression is observable and reward timing stays terminal-only.

## Phase 6: Documentation and Mapping

**Purpose**: Record the paper-to-code mapping, assumptions, and no-dependency note for the feature.

- [X] T018 [P] Update `docs/paper_notes/paper_to_code_mapping.md` with mappings for compute budget derivation, execution helper logic, capacity configuration, and reward timing.
- [X] T019 [P] Update `docs/assumptions/hoodie_assumptions.md` only for unresolved paper gaps in compute capacity or cycle mapping, and record any remaining unit-conversion blockers explicitly if they remain unresolved.
- [X] T020 [P] Add the no-dependency-change verification note to `specs/006-task-execution-time-compute-model/quickstart.md`.

**Checkpoint**: The feature is traceable and its paper-backed boundaries are documented.

## Phase 7: Guardrails and Validation

**Purpose**: Lock the compute feature down with rejection tests and repository-level verification.

- [X] T021 [P] Add regression coverage in `tests/unit/test_execution_model.py` or `tests/unit/test_task_compute_state.py` ensuring unsupported stochastic compute models or silent capacity remapping are rejected and never silently accepted.
- [X] T022 Verify no dependency files changed by checking `pyproject.toml`, `requirements.txt`, `setup.cfg`, and `setup.py` remain untouched for this feature.
- [X] T023 Run relevant unit tests: `tests/unit/test_compute_config.py`, `tests/unit/test_task_compute_state.py`, `tests/unit/test_execution_model.py`, `tests/unit/test_execution_observer.py`, and the existing environment boundary tests that cover `HoodieGymEnvironment` and `SlotEngine`.
- [X] T024 Run relevant integration tests: `tests/integration/test_execution_time_flow.py`, `tests/integration/test_flc_episode.py`, and `tests/integration/test_evaluation_runner.py`.
- [X] T025 Update `specs/006-task-execution-time-compute-model/tasks.md` checkboxes only after the code, docs, and tests are complete.

**Checkpoint**: Compute execution is verified, traceable, and still dependency-clean.

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: No dependencies, can start immediately.
- **Phase 2**: Depends on Phase 1 completion.
- **Phase 3**: Depends on Phase 2 completion.
- **Phase 4**: Depends on Phase 3 completion.
- **Phase 5**: Depends on Phases 3 and 4 completion.
- **Phase 6**: Depends on Phases 3 through 5 being stable.
- **Phase 7**: Depends on all implementation, documentation, and compatibility work being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2. No dependency on observability or destination-specific progression.
- **User Story 2 (P1)**: Depends on User Story 1 so it can validate compute timing on completed task state.
- **User Story 3 (P2)**: Depends on User Story 1 and User Story 2 so it can validate reward timing and observability against compute progression.

### Within Each Story

- Tests or validation tasks must exist for every implementation task.
- Configuration before execution helper.
- Execution helper before environment integration.
- Environment integration before execution timing regression validation.
- Documentation and traceability updates after behavior is stable.

## Parallel Execution Examples

```bash
# Phase 1 documentation alignment can be split across files
Task: "Review and align specs/006-task-execution-time-compute-model/spec.md"
Task: "Review and align specs/006-task-execution-time-compute-model/plan.md"
Task: "Review and align specs/006-task-execution-time-compute-model/research.md"

# Phase 2 config and state work can proceed separately once the files exist
Task: "Add src/environment/compute_config.py with ComputeConfig and capacities"
Task: "Update src/environment/task.py and src/evaluation/trace_protocol.py for cycles tracking"

# Phase 3 execution helper and unit test drafting can proceed in parallel if the API is stable
Task: "Add src/environment/execution_helper.py implementing deterministic cycle decrement"
Task: "Add tests/unit/test_execution_model.py verifying compute-budget and decrement behavior"

# Phase 4 integration work can be split across runtime wiring and reward timing checks
Task: "Integrate compute progression into src/environment/gym_adapter.py"
Task: "Update src/environment/reward_timing.py for terminal-only reward emission"
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 documentation alignment.
2. Complete Phase 2 compute capacities and task state fields.
3. Complete Phase 3 deterministic compute decrement logic.
4. Validate one generated task through `HoodieGymEnvironment` using the existing external loop.
5. Stop and confirm compute timing is reproducible before expanding observability.

### Incremental Delivery

1. Add paper-backed compute capacities.
2. Add deterministic compute budget derivation.
3. Add execution helper decrement logic.
4. Wire execution into the existing environment boundary.
5. Add paper-to-code mapping, assumptions, and no-dependency verification.
6. Finish with regression tests and repository validation.

### Suggested MVP Scope

- User Story 1 only, with a minimal environment compatibility smoke path from User Story 2 if needed to prove the generated execution state can actually be consumed.
