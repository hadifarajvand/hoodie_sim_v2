# Tasks: Differential Environment Audit

**Input**: Design documents from `/specs/018-differential-environment-audit/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Test-first implementation is required for this feature.

**Organization**: Tasks are grouped by user story so the audit can be built and verified independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the isolated audit package and the repository guard before audit logic is added.

### Quality Gate

- [ ] T001 Confirm 018 branch hygiene and repository scope against `main` and document the result in `specs/018-differential-environment-audit/quickstart.md`
- [ ] T002 Create the isolated audit package skeleton `src/audits/differential_environment/__init__.py`, `src/audits/differential_environment/audit.py`, `src/audits/differential_environment/cases.py`, `src/audits/differential_environment/report.py`, and `src/audits/differential_environment/classify.py`
- [ ] T003 [P] Add the unit test module shell `tests/unit/test_differential_environment_audit.py`
- [ ] T004 [P] Add the integration test module shell `tests/integration/test_differential_environment_audit_flow.py`

**Checkpoint**: Audit package and test targets exist, and no simulator, policy, training, metric, campaign, or dependency files are touched.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define the toy-case schema, comparison taxonomy, and deterministic report structure that all audit tests depend on.

**⚠️ CRITICAL**: No user story work begins until the audit data model and schema primitives exist.

- [ ] T005 Implement deterministic toy-case fixtures and stable fields in `src/audits/differential_environment/cases.py`
- [ ] T006 Implement comparison and finding enums in `src/audits/differential_environment/classify.py`
- [ ] T007 Implement the audit report schema dataclasses in `src/audits/differential_environment/report.py`
- [ ] T008 Implement deterministic report metadata helpers in `src/audits/differential_environment/report.py`
- [ ] T009 Implement deterministic ordering helpers for cases and findings in `src/audits/differential_environment/report.py`

**Checkpoint**: Core audit case definitions and report schema are ready for test-driven classification behavior.

---

## Phase 3: User Story 1 - Deterministic differential audit report (Priority: P1) 🎯 MVP

**Goal**: Verify the audit can compare identical toy lifecycle cases between the reference kernel and the current environment and emit deterministic report artifacts.

**Independent Test**: A fixed toy-case set produces JSON and Markdown outputs with reference summaries, environment summaries, and per-case comparison results in stable order.

### Tests for User Story 1

- [ ] T010 [P] [US1] Add toy-case definition tests in `tests/unit/test_differential_environment_audit.py`
- [ ] T011 [P] [US1] Add report schema and deterministic ordering tests in `tests/unit/test_differential_environment_audit.py`

### Implementation for User Story 1

- [ ] T012 [US1] Implement audit runner scaffolding in `src/audits/differential_environment/audit.py`
- [ ] T013 [US1] Implement deterministic JSON and Markdown writers in `src/audits/differential_environment/report.py`
- [ ] T014 [US1] Expose the audit package entry point in `src/audits/differential_environment/__init__.py`

**Checkpoint**: The audit can generate deterministic artifacts for the required toy-case set.

---

## Phase 4: User Story 2 - Classified divergence reporting (Priority: P2)

**Goal**: Verify the audit classifies mismatches, assumptions, unsupported traces, and scope differences without normalizing them away.

**Independent Test**: Timeout/drop, delayed reward timing, and deterministic ordering cases produce stable classification labels and separate finding causes.

### Tests for User Story 2

- [ ] T015 [P] [US2] Add comparison classification tests in `tests/unit/test_differential_environment_audit.py`
- [ ] T016 [P] [US2] Add finding-cause classification tests in `tests/unit/test_differential_environment_audit.py`
- [ ] T017 [P] [US2] Add no-normalization coverage tests in `tests/unit/test_differential_environment_audit.py`

### Implementation for User Story 2

- [ ] T018 [US2] Implement classification logic in `src/audits/differential_environment/classify.py`
- [ ] T019 [US2] Implement per-case comparison assembly in `src/audits/differential_environment/audit.py`
- [ ] T020 [US2] Extend report rendering to include assumptions, unsupported observations, and no-fix disclaimer sections in `src/audits/differential_environment/report.py`

**Checkpoint**: Divergences and gaps are classified explicitly and remain visible in the report.

---

## Phase 5: User Story 3 - Reproducible no-fix audit artifacts (Priority: P3)

**Goal**: Verify the audit artifacts are reproducible, contain the required disclaimer, and remain diagnostic only.

**Independent Test**: Two runs over the same toy inputs produce deterministic artifact content and the report states that no fixes were applied.

### Tests for User Story 3

- [ ] T021 [P] [US3] Add integration coverage for the end-to-end audit run in `tests/integration/test_differential_environment_audit_flow.py`
- [ ] T022 [P] [US3] Add deterministic artifact output tests in `tests/integration/test_differential_environment_audit_flow.py`
- [ ] T023 [P] [US3] Add public-interface-only environment probe tests in `tests/integration/test_differential_environment_audit_flow.py`

### Implementation for User Story 3

- [ ] T024 [US3] Implement the current-environment probe using the public `reset`/`step` interface in `src/audits/differential_environment/audit.py`
- [ ] T025 [US3] Implement the deterministic output path writer for `artifacts/analysis/differential-environment-audit/` in `src/audits/differential_environment/report.py`
- [ ] T026 [US3] Add the no-fix disclaimer and reproducibility metadata to report output in `src/audits/differential_environment/report.py`

**Checkpoint**: The audit remains diagnostic only and produces reproducible artifacts.

---

## Phase 6: Final Validation & Repository Guard

**Purpose**: Prove the feature is isolated, deterministic, and limited to the approved audit package and tests.

- [ ] T027 [P] Add repository-scope guard assertions to `tests/integration/test_differential_environment_audit_flow.py` proving the audit does not import or modify `src/environment`, `src/policies`, `src/training`, `src/metrics`, `campaign` runners, dependency files, or existing campaign artifacts
- [ ] T028 Run the targeted validation command with `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest tests.unit.test_differential_environment_audit tests.integration.test_differential_environment_audit_flow`
- [ ] T029 Compare the diff against `main` and verify no forbidden paths changed, no environment repair was introduced, no simulator lifecycle drift was introduced, and no assumption was normalized into a validated paper claim

**Checkpoint**: Scope, determinism, and repository hygiene are verified before merge.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Stories (Phases 3-5)**: Depend on Foundational completion
- **Final Validation (Phase 6)**: Depends on all targeted user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent MVP path after Foundational
- **User Story 2 (P2)**: Independent classification path after Foundational; does not require environment mutation or fixes
- **User Story 3 (P3)**: Independent reproducibility and disclaimer path after Foundational; depends only on shared audit schema

### Within Each User Story

- Tests are written first and must fail before implementation
- Data structures before runner logic
- Runner logic before integration coverage
- Each story is complete before moving to the next priority

### Parallel Opportunities

- `T003` and `T004` can run in parallel because they touch different test files
- `T010` and `T011` can run in parallel
- `T015`, `T016`, and `T017` are not parallel-safe because they touch the same file
- `T021`, `T022`, and `T023` are not parallel-safe because they touch the same file
- `T027` must run before `T028` and `T029`

---

## Parallel Example: User Story 1

```bash
Task: "Add toy-case definition tests in tests/unit/test_differential_environment_audit.py"
Task: "Add report schema and deterministic ordering tests in tests/unit/test_differential_environment_audit.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate the deterministic JSON and Markdown outputs

### Incremental Delivery

1. Build the isolated audit package
2. Add deterministic toy-case fixtures and report schema
3. Add comparison classification and no-normalization behavior
4. Add public-interface probe and reproducible outputs
5. Run the repository-scope guard and final diff audit

---

## Format Validation

- All tasks follow the required checklist format
- Every task is atomic and file-specific
- Tests precede implementation for each story
- No task modifies forbidden simulator, policy, campaign, metric, dependency, or artifact paths
- The final audit task explicitly checks source/import isolation from simulator lifecycle modules
- No task introduces DRL, neural networks, Gymnasium, TorchRL, ns-3, or ns-3-gym

