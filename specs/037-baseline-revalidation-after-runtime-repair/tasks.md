---

description: "Task list for Feature 037 - Baseline Revalidation After Runtime Repair"
---

# Tasks: Baseline Revalidation After Runtime Repair

**Input**: Design documents from `/specs/037-baseline-revalidation-after-runtime-repair/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`

**Tests**: Required by the feature spec and quickstart. Include targeted registry, environment, metric-schema, reproducibility, drift-guard, and report-validation tests.

**Organization**: Tasks are grouped by user story so baseline inventory, environment validation, reproducibility, and report generation can be implemented and verified independently.

## Format: `[ID] [P?] [US?] Description with exact file path`

- **[P]**: Can run in parallel with other marked tasks because it touches different files and has no dependency on incomplete work
- **[US?]**: Required for user story phases only
- Every task description must name the file path it changes or verifies

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Lock down branch hygiene, prerequisite tags, and repository scope before any evaluation work.

- [ ] T001 Verify branch hygiene and clean-worktree preconditions in shell: current branch is not `main`, branch base matches current `main`, `036-deadline-timeout-off-by-one-audit-complete` equals `main`, and no unrelated uncommitted files are present
- [ ] T002 Verify prerequisite complete tags for Features 032, 033, 034, 035, and 036 are present and reachable in shell, and record the verified tag set for `specs/037-baseline-revalidation-after-runtime-repair/research.md`

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define the revalidation inventory, environment contract, metrics schema, and report contract before any baseline run is attempted.

- [ ] T003 Define the revalidation scope, baseline inventory, deterministic seed policy, scenario policy, and no-reproduction claim boundary in `specs/037-baseline-revalidation-after-runtime-repair/data-model.md`
- [ ] T004 Define the revalidation report schema and no-drift flags in `src/analysis/baseline_revalidation_after_runtime_repair/report.py`
- [ ] T005 Update the feature quickstart validation flow in `specs/037-baseline-revalidation-after-runtime-repair/quickstart.md` to name the approved interpreter, baseline policies, deterministic seeds, runtime-contract checks, and report artifacts
- [ ] T006 Update `AGENTS.md` for Feature 037 so it references `specs/037-baseline-revalidation-after-runtime-repair/plan.md` and `specs/037-baseline-revalidation-after-runtime-repair/spec.md`, states baseline revalidation only, and states no policy redesign, training, dependency, runtime-contract, or paper-reproduction changes

**Checkpoint**: Foundation ready - baseline revalidation can now be implemented.

## Phase 3: User Story 1 - Baseline Interface Revalidation (Priority: P1) 🎯 MVP

**Goal**: Prove each in-scope baseline policy runs through the shared `HoodieGymEnvironment` interface and obeys the legal action mask.

**Independent Test**: FLC, VO, HO, RO, BCO, MLEO, and ADAPTIVE each complete a revalidation episode through the same environment path, and every selected action is legal at the time it is chosen.

### Tests for User Story 1

- [ ] T007 [P] [US1] Add registry coverage proving the in-scope baselines are present in the policy source of truth in `tests/unit/test_baseline_registry_revalidation.py`
- [ ] T008 [P] [US1] Add environment-path coverage proving each baseline runs through `HoodieGymEnvironment` and receives `legal_action_mask` in `tests/integration/test_baseline_revalidation_after_runtime_repair.py`
- [ ] T009 [P] [US1] Add legal-action coverage proving every selected action is legal at selection time in `tests/integration/test_baseline_revalidation_after_runtime_repair.py`

### Implementation for User Story 1

- [ ] T010 [US1] Implement baseline registry and policy inventory helpers for the seven in-scope baselines in `src/analysis/baseline_revalidation_after_runtime_repair/registry.py`
- [ ] T011 [US1] Implement the shared environment revalidation harness that runs baselines through `HoodieGymEnvironment` in `src/analysis/baseline_revalidation_after_runtime_repair/runner.py`
- [ ] T012 [US1] Verify baseline selection always flows through the standard environment action path in `src/environment/gym_adapter.py`

**Checkpoint**: Each baseline should run through the shared environment path and honor the legal action mask.

## Phase 4: User Story 2 - Deterministic Baseline Revalidation (Priority: P2)

**Goal**: Re-run the baselines with deterministic seeds and verify reproducible results for deterministic policies and RO.

**Independent Test**: Fixed-seed runs reproduce artifact contents and metric outputs for deterministic baselines, and RO reproduces its action/result trace for the same seed.

### Tests for User Story 2

- [ ] T013 [P] [US2] Add deterministic-seed reproducibility coverage for the baseline revalidation runner in `tests/integration/test_baseline_revalidation_after_runtime_repair.py`
- [ ] T014 [P] [US2] Add RO seed-controlled reproducibility coverage in `tests/integration/test_baseline_revalidation_after_runtime_repair.py`
- [ ] T015 [P] [US2] Add metrics-schema and numeric sanity coverage in `tests/integration/test_baseline_revalidation_report.py`

### Implementation for User Story 2

- [ ] T016 [US2] Implement deterministic seed configuration for the baseline revalidation runner in `src/analysis/baseline_revalidation_after_runtime_repair/runner.py`
- [ ] T017 [US2] Implement scenario selection for paper-default or approved smoke validation in `src/analysis/baseline_revalidation_after_runtime_repair/runner.py`
- [ ] T018 [US2] Verify the evaluation payload includes policy name, scenario name, seed, final metrics, task counts, drop ratio, throughput, average delay, and runtime-contract markers in `src/analysis/baseline_revalidation_after_runtime_repair/report.py`

**Checkpoint**: Revalidation runs should be deterministic for fixed seeds and reproducible for RO.

## Phase 5: User Story 3 - Baseline Sanity Reporting (Priority: P3)

**Goal**: Produce a baseline revalidation report that records the post-repair sanity results without claiming paper reproduction.

**Independent Test**: The report records policies, scenarios, seeds, runtime-contract verification, environment-interface verification, legal-action verification, reproducibility status, and the explicit no-paper-reproduction boundary.

### Tests for User Story 3

- [ ] T019 [P] [US3] Add report-schema coverage for the required fields in `tests/integration/test_baseline_revalidation_report.py`
- [ ] T020 [P] [US3] Add report-write coverage for JSON and Markdown artifacts in `tests/integration/test_baseline_revalidation_report.py`
- [ ] T021 [P] [US3] Add no-curve-fitting and no-paper-reproduction claim coverage in `tests/integration/test_baseline_revalidation_report.py`
- [ ] T022 [P] [US3] Add runtime-contract drift-guard coverage for Features 032, 033, 034, 035, and 036 in `tests/integration/test_baseline_revalidation_scope_guard.py`
- [ ] T023 [P] [US3] Add scope-guard coverage proving no dependency, training, policy-redesign, or runtime-contract drift in `tests/integration/test_baseline_revalidation_scope_guard.py`

### Implementation for User Story 3

- [ ] T024 [US3] Add the baseline revalidation analysis package in `src/analysis/baseline_revalidation_after_runtime_repair/__init__.py`
- [ ] T025 [US3] Implement the baseline revalidation report builder in `src/analysis/baseline_revalidation_after_runtime_repair/report.py`
- [ ] T026 [US3] Generate the JSON report at `artifacts/analysis/baseline-revalidation-after-runtime-repair/baseline-revalidation-report.json`
- [ ] T027 [US3] Generate the Markdown report at `artifacts/analysis/baseline-revalidation-after-runtime-repair/baseline-revalidation-report.md`
- [ ] T028 [US3] Write optional evaluation artifacts, if supported by the existing runner, under `artifacts/evaluation/baseline-revalidation-after-runtime-repair/`

**Checkpoint**: Baseline sanity reporting should now be covered.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup across all stories.

- [ ] T029 Validate the full targeted test suite with the approved interpreter in `specs/037-baseline-revalidation-after-runtime-repair/quickstart.md`
- [ ] T030 Verify the report schema fields, prerequisite tags, deterministic seeds, and no-curve-fitting / no-paper-reproduction flags in `tests/integration/test_baseline_revalidation_report.py`
- [ ] T031 Verify `git status --short` and `git diff --name-only main...HEAD` show only Feature 037 scoped changes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories
- **User Stories (Phase 3+)**: Depend on the Foundation; proceed in priority order
- **Polish (Phase 6)**: Depends on all required user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can begin after Foundation; no dependency on later stories
- **User Story 2 (P2)**: Can begin after Foundation; depends on the baseline inventory and environment harness from US1 but remains independently testable
- **User Story 3 (P3)**: Can begin after Foundation; depends on runtime behavior from US1 and US2 for sanity reporting only

### Within Each User Story

- Tests are written before implementation tasks in the same story
- Environment verification comes before any runner wiring
- Report generation comes after the revalidation harness and metrics checks are in place

## Parallel Execution Examples

### User Story 1

```bash
Task: "Add registry coverage proving the in-scope baselines are present in the policy source of truth in tests/unit/test_baseline_registry_revalidation.py"
Task: "Add environment-path coverage proving each baseline runs through HoodieGymEnvironment and receives legal_action_mask in tests/integration/test_baseline_revalidation_flow.py"
Task: "Add legal-action coverage proving every selected action is legal at selection time in tests/integration/test_baseline_revalidation_flow.py"
```

### User Story 2

```bash
Task: "Add deterministic-seed reproducibility coverage for the baseline revalidation runner in tests/integration/test_baseline_revalidation_flow.py"
Task: "Add RO seed-controlled reproducibility coverage in tests/integration/test_baseline_revalidation_flow.py"
Task: "Add metrics-schema and numeric sanity coverage in tests/integration/test_baseline_revalidation_report.py"
```

### User Story 3

```bash
Task: "Add report-schema coverage for the required fields in tests/integration/test_baseline_revalidation_report.py"
Task: "Add report-write coverage for JSON and Markdown artifacts in tests/integration/test_baseline_revalidation_report.py"
Task: "Add no-curve-fitting and no-paper-reproduction claim coverage in tests/integration/test_baseline_revalidation_report.py"
Task: "Add runtime-contract drift-guard coverage for Features 032, 033, 034, 035, and 036 in tests/integration/test_baseline_revalidation_scope_guard.py"
Task: "Add scope-guard coverage proving no dependency, training, policy-redesign, or runtime-contract drift in tests/integration/test_baseline_revalidation_scope_guard.py"
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 preflight checks.
2. Complete Phase 2 inventory, harness, and report scaffolding.
3. Deliver User Story 1 for the shared environment-interface revalidation.
4. Validate deterministic seeds and legal-action handling before any report polishing.

### Incremental Delivery

1. Lock the baseline inventory and shared environment path.
2. Verify deterministic revalidation behavior for fixed seeds.
3. Add report generation and drift guards.
4. Generate and validate the baseline sanity report.

## Notes

- Keep the task list narrow: no fake parallelism, no baseline policy redesign, no training, no curve fitting, no runtime-contract mutation, no dependency changes, and no paper-reproduction claims.
- Old artifacts may be used only as drift references after the runtime repairs.
- The feature is a baseline sanity revalidation, not a paper reproduction effort.
