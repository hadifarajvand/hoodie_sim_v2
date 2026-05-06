# Tasks: 009-paper-backed-evaluation-matrix

**Input**: Design documents from `/specs/009-paper-backed-evaluation-matrix/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the feature docs and keep the implementation scoped to evaluation-only orchestration.

- [x] T001 Create `specs/009-paper-backed-evaluation-matrix/spec.md` with reproducible matrix runs, auditable artifacts, and strict scope enforcement
- [x] T002 Create `specs/009-paper-backed-evaluation-matrix/clarifications.md` capturing the scope locks from user clarification, including no training, no plot reproduction, no metric changes, no policy-specific environment paths, and stdlib-only output
- [x] T003 Create `specs/009-paper-backed-evaluation-matrix/plan.md` with constitution gate, architecture, affected modules, and no-dependency policy
- [x] T004 Create `specs/009-paper-backed-evaluation-matrix/data-model.md` describing `EvaluationMatrixConfig`, registries, run records, and aggregate summary
- [x] T005 Create `specs/009-paper-backed-evaluation-matrix/contracts/evaluation-matrix.md` defining the config, registry, and runner contract
- [x] T006 Create `specs/009-paper-backed-evaluation-matrix/quickstart.md` showing how to run the serial evaluation matrix and inspect artifacts

**Checkpoint**: Feature docs are in place and the implementation surface is bounded.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the shared config and lookup surfaces before the matrix runner exists.

- [x] T007 Add `src/evaluation/matrix_config.py` with `EvaluationMatrixConfig`, validation, and deterministic ordering rules
- [x] T008 [P] Add `tests/unit/test_evaluation_matrix_config.py` covering config validation, default behavior, and deterministic ordering
- [x] T009 Add `src/evaluation/policy_registry.py` for `FLC`, `VO`, `HO`, `RO`, `BCO`, `MLEO`, and `ADAPTIVE`
- [x] T010 [P] Add `tests/unit/test_policy_registry.py` covering approved policy lookup and unsupported policy rejection
- [x] T011 Add `src/evaluation/scenario_registry.py` for `paper_default`, `moderate`, `heavy`, and `extreme`
- [x] T012 [P] Add `tests/unit/test_scenario_registry.py` covering approved scenario lookup and unsupported scenario rejection

**Checkpoint**: Matrix config and lookup surfaces are ready for the runner.

## Phase 3: User Story 1 - Reproducible Matrix Runs (Priority: P1)

**Goal**: Execute each implemented policy across each paper-backed scenario and seed using the shared environment boundary.

**Independent Test**: Run the matrix twice with the same configuration and confirm the same policy/scenario/seed combinations produce the same traces and metric records.

- [x] T013 [US1] Add `src/evaluation/matrix_runner.py` with serial orchestration over policy × scenario × seed combinations
- [x] T014 [US1] Integrate `src/evaluation/matrix_runner.py` with `src/environment/traffic_generator.py` and `src/environment/gym_adapter.py` through the existing reset/step loop only
- [x] T015 [US1] Ensure `src/evaluation/matrix_runner.py` collects existing metrics without changing formulas
- [x] T016 [US1] Ensure `src/evaluation/matrix_runner.py` writes per-run result records using stdlib `json`
- [x] T017 [US1] Ensure `src/evaluation/matrix_runner.py` writes aggregate summary output using stdlib `csv` when feasible
- [x] T018 [P] [US1] Add `tests/integration/test_evaluation_matrix_runner.py` for serial execution across a small policy/scenario/seed matrix

**Checkpoint**: The matrix can run implemented policies reproducibly through the shared environment boundary.

## Phase 4: User Story 2 - Auditable Metric Artifacts (Priority: P1)

**Goal**: Produce machine-readable per-run records and summary artifacts that can be reloaded later without ambiguity.

**Independent Test**: Execute a small matrix and verify the runner writes per-run records and an aggregate summary that preserve policy, scenario, seed, trace identifier, and config metadata.

- [x] T019 [US2] Extend `src/evaluation/matrix_runner.py` to include reproducibility metadata in each run record, including policy, scenario, seed, trace identifier, config snapshot, and dependency-change note
- [x] T020 [P] [US2] Extend `tests/integration/test_evaluation_matrix_runner.py` to verify artifact shape and reloadability for per-run records and aggregate summaries
- [x] T021 [US2] Add stable artifact naming / file layout in `src/evaluation/matrix_runner.py` so repeated serial runs preserve deterministic output ordering

**Checkpoint**: Result artifacts are auditable and reproducible.

## Phase 5: User Story 3 - Strict Scope Enforcement (Priority: P2)

**Goal**: Reject unsupported policy and scenario names before any matrix execution begins.

**Independent Test**: Attempt to run the matrix with an unsupported policy or scenario name and verify the request is rejected before simulation starts.

- [x] T022 [US3] Add fast-fail validation for unsupported policy names in `src/evaluation/policy_registry.py`
- [x] T023 [US3] Add fast-fail validation for unsupported scenario names in `src/evaluation/scenario_registry.py`
- [x] T024 [P] [US3] Extend `tests/unit/test_policy_registry.py` and `tests/unit/test_scenario_registry.py` to verify explicit rejection of unsupported names
- [x] T025 [P] [US3] Extend `tests/integration/test_evaluation_matrix_runner.py` to prove unsupported policy/scenario combinations fail before the environment loop starts

**Checkpoint**: Unsupported names are rejected and the matrix scope stays paper-backed.

## Phase 6: Documentation and Traceability

**Purpose**: Keep the paper-to-code mapping and assumptions honest while the matrix runner is added.

- [x] T026 Update `docs/paper_notes/paper_to_code_mapping.md` with mappings for evaluation matrix config, policy/scenario registries, matrix runner, and matrix artifacts
- [x] T027 Update `docs/assumptions/hoodie_assumptions.md` only if a new assumption is introduced, and explicitly document any omission of commit/ref metadata when unavailable
- [x] T028 Add a no-dependency-change note in `specs/009-paper-backed-evaluation-matrix/quickstart.md`

**Checkpoint**: Paper traceability and artifact rules are explicit.

## Phase 7: Guardrails and Validation

**Purpose**: Prove nothing outside scope changed and the matrix runner works under the existing simulator stack.

- [x] T029 Verify no dependency files changed: `pyproject.toml`, `requirements.txt`, `setup.cfg`, `setup.py`, and lockfiles
- [x] T030 Verify no files under `src/training/`, `src/agents/`, or neural-network modules changed for this feature
- [x] T031 Verify `src/environment/slot_engine.py` still has no `run_slot`, `slot_flow`, or controller-shaped lifecycle API
- [x] T032 Run unit tests: `tests/unit/test_evaluation_matrix_config.py`, `tests/unit/test_policy_registry.py`, and `tests/unit/test_scenario_registry.py`
- [x] T033 Run integration tests: `tests/integration/test_evaluation_matrix_runner.py`, `tests/integration/test_dynamic_traffic_environment_flow.py`, `tests/integration/test_execution_time_flow.py`, `tests/integration/test_flc_episode.py`, and `tests/integration/test_evaluation_runner.py`
- [x] T034 Update `specs/009-paper-backed-evaluation-matrix/tasks.md` checkboxes only after code, docs, and tests are complete

**Checkpoint**: Scope guardrails and regression coverage are satisfied.

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) has no dependencies
- Foundational (Phase 2) depends on Setup and blocks all user stories
- User Story 1 (Phase 3) depends on Foundational
- User Story 2 (Phase 4) depends on Foundational and the matrix runner
- User Story 3 (Phase 5) depends on Foundational and the registries
- Documentation (Phase 6) depends on stable behavior from the user-story phases
- Guardrails and Validation (Phase 7) runs last

### User Story Dependencies

- **US1** can start after Foundational
- **US2** can start after Foundational and the matrix runner
- **US3** can start after Foundational and can proceed alongside US1/US2 once the registries exist

### Parallel Opportunities

- `T008`, `T010`, `T012`, and `T018` can run in parallel with their non-overlapping implementation counterparts
- `T020`, `T024`, and `T025` can run in parallel after the matrix behavior stabilizes
- `T029` through `T033` are independent validation tasks and can be scheduled separately

## Implementation Strategy

### MVP First

1. Complete Phase 1 docs
2. Complete Phase 2 registries and config
3. Complete Phase 3 serial matrix runner
4. Stop and validate deterministic serial execution and artifact output

### Incremental Delivery

1. Add config and registries
2. Add the serial matrix runner
3. Add artifact emission
4. Add strict validation and traceability

### Parallel Team Strategy

1. One developer handles `matrix_config.py` and its tests
2. One developer handles policy/scenario registries and their tests
3. One developer handles `matrix_runner.py` and integration tests
4. One developer handles documentation, assumptions, and validation checks
