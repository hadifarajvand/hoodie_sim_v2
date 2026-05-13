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

- [X] T001 Verify branch hygiene and clean-worktree preconditions in shell: current branch is not `main`, branch base matches current `main`, `036-deadline-timeout-off-by-one-audit-complete` equals `main`, and no unrelated uncommitted files are present
- [X] T002 Verify prerequisite complete tags for Features 032, 033, 034, 035, and 036 are present and reachable in shell, and record the verified tag set for `specs/037-baseline-revalidation-after-runtime-repair/research.md`

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define the revalidation inventory, approved topology source, workload sanity rules, environment contract, metrics schema, and report contract before any baseline run is attempted.

- [X] T003 Define the revalidation scope, approved Figure 7 topology requirement, baseline inventory, deterministic seed policy, workload sanity rule, scenario policy, and no-reproduction claim boundary in `specs/037-baseline-revalidation-after-runtime-repair/data-model.md`
- [X] T004 Define the revalidation report schema, approved-topology provenance, trace-count fields, pending-at-horizon count, and no-drift flags in `src/analysis/baseline_revalidation_after_runtime_repair/report.py`
- [X] T005 Update the feature quickstart validation flow in `specs/037-baseline-revalidation-after-runtime-repair/quickstart.md` to name the approved interpreter, baseline policies, deterministic seeds, approved Figure 7 topology checks, workload sanity checks, and report artifacts
- [X] T006 Update `AGENTS.md` for Feature 037 so it references `specs/037-baseline-revalidation-after-runtime-repair/plan.md` and `specs/037-baseline-revalidation-after-runtime-repair/spec.md`, states baseline revalidation only, and states no policy redesign, training, dependency, runtime-contract, or paper-reproduction changes

**Checkpoint**: Foundation ready - baseline revalidation can now be implemented.

## Phase 3: User Story 1 - Baseline Interface Revalidation (Priority: P1) 🎯 MVP

**Goal**: Prove each in-scope baseline policy runs through the shared `HoodieGymEnvironment` interface and obeys the legal action mask.

**Independent Test**: FLC, VO, HO, RO, BCO, MLEO, and ADAPTIVE each complete a revalidation episode through the same `HoodieGymEnvironment` path, the approved Figure 7 topology is used for `paper_default`, and every selected action is legal at the time it is chosen against the real environment mask.

### Tests for User Story 1

- [X] T007 [P] [US1] Add registry coverage proving the in-scope baselines are present in the policy source of truth in `tests/unit/test_baseline_registry_revalidation.py`
- [X] T008 [P] [US1] Add approved-topology coverage proving `paper_default` uses `TopologyGraph.from_approved_assumption_registry()` and satisfies the Figure 7 invariants in `tests/unit/test_baseline_registry_revalidation.py`
- [X] T009 [P] [US1] Add horizontal-legal-mask coverage proving every baseline only offloads to approved Figure 7 neighbors, never to self or non-neighbors, in `tests/integration/test_baseline_revalidation_after_runtime_repair.py`
- [X] T010 [P] [US1] Add environment-path coverage proving each baseline runs through `HoodieGymEnvironment`, not a direct SlotEngine path, and receives the real `legal_action_mask` in `tests/integration/test_baseline_revalidation_after_runtime_repair.py`
- [X] T011 [P] [US1] Add vertical/cloud-legality coverage proving cloud offload remains legal independently of Figure 7 horizontal adjacency in `tests/integration/test_baseline_revalidation_after_runtime_repair.py`

### Implementation for User Story 1

- [X] T012 [US1] Implement baseline registry and policy inventory helpers for the seven in-scope baselines in `src/analysis/baseline_revalidation_after_runtime_repair/registry.py`
- [X] T013 [US1] Implement the shared revalidation harness that runs baselines through `HoodieGymEnvironment` with `TopologyGraph.from_approved_assumption_registry()` for `paper_default` in `src/analysis/baseline_revalidation_after_runtime_repair/runner.py`
- [X] T014 [US1] Remove any synthetic complete-graph or all-to-all topology fallback from the Feature 037 runner path in `src/analysis/baseline_revalidation_after_runtime_repair/runner.py`

**Checkpoint**: Each baseline should run through the shared environment path and honor the legal action mask.

## Phase 4: User Story 2 - Deterministic Baseline Revalidation (Priority: P2)

**Goal**: Re-run the baselines with deterministic seeds and verify reproducible results for deterministic policies and RO.

**Independent Test**: Fixed-seed runs reproduce artifact contents and metric outputs for deterministic baselines, RO reproduces its action/result trace for the same seed, and the trace artifacts include arrivals, finalized terminal tasks, and pending-at-horizon counts.

### Tests for User Story 2

- [X] T015 [P] [US2] Add deterministic-seed reproducibility coverage for the baseline revalidation runner in `tests/integration/test_baseline_revalidation_after_runtime_repair.py`
- [X] T016 [P] [US2] Add RO seed-controlled reproducibility coverage in `tests/integration/test_baseline_revalidation_after_runtime_repair.py`
- [X] T017 [P] [US2] Add workload-sanity coverage proving `N=20`, `T=110`, `P=0.5`, `Δ=0.1`, and `timeout_slots=20` in `tests/integration/test_baseline_revalidation_after_runtime_repair.py`
- [X] T018 [P] [US2] Add metrics-schema and numeric sanity coverage in `tests/integration/test_baseline_revalidation_report.py`
- [X] T019 [P] [US2] Add trace-artifact validity coverage proving per-run JSON, trace JSON, and summary CSV are non-empty valid files in `tests/integration/test_baseline_revalidation_report.py`

### Implementation for User Story 2

- [X] T020 [US2] Implement deterministic seed configuration for the baseline revalidation runner in `src/analysis/baseline_revalidation_after_runtime_repair/runner.py`
- [X] T021 [US2] Implement paper-default scenario selection and reject any complete-graph fallback in `src/analysis/baseline_revalidation_after_runtime_repair/runner.py`
- [X] T022 [US2] Record generated arrivals, finalized terminal tasks, and pending-at-horizon count in the baseline revalidation payload in `src/analysis/baseline_revalidation_after_runtime_repair/runner.py`
- [X] T023 [US2] Verify the evaluation payload includes policy name, scenario name, seed, final metrics, task counts, drop ratio, throughput, average delay, runtime-contract markers, and topology provenance in `src/analysis/baseline_revalidation_after_runtime_repair/report.py`

**Checkpoint**: Revalidation runs should be deterministic for fixed seeds and reproducible for RO.

## Phase 5: User Story 3 - Baseline Sanity Reporting (Priority: P3)

**Goal**: Produce a baseline revalidation report that records the post-repair sanity results without claiming paper reproduction.

**Independent Test**: The report records policies, scenarios, seeds, runtime-contract verification, environment-interface verification, legal-action verification, reproducibility status, topology provenance, trace-count sanity, and the explicit no-paper-reproduction boundary.

### Tests for User Story 3

- [X] T024 [P] [US3] Add report-schema coverage for the required fields in `tests/integration/test_baseline_revalidation_report.py`
- [X] T025 [P] [US3] Add report-write coverage for JSON and Markdown artifacts in `tests/integration/test_baseline_revalidation_report.py`
- [X] T026 [P] [US3] Add no-curve-fitting and no-paper-reproduction claim coverage in `tests/integration/test_baseline_revalidation_report.py`
- [X] T027 [P] [US3] Add runtime-contract drift-guard coverage for Features 032, 033, 034, 035, and 036 in `tests/integration/test_baseline_revalidation_scope_guard.py`
- [X] T028 [P] [US3] Add scope-guard coverage proving no dependency, training, policy-redesign, or runtime-contract drift in `tests/integration/test_baseline_revalidation_scope_guard.py`
- [X] T029 [P] [US3] Add approved-topology regression coverage proving the runner rejects complete-graph / all-to-all topology fallback in `tests/integration/test_baseline_revalidation_after_runtime_repair.py`
- [X] T030 [P] [US3] Add trace-count and pending-task coverage proving revalidation reports arrivals, finalized terminal tasks, and pending-at-horizon counts in `tests/integration/test_baseline_revalidation_report.py`

### Implementation for User Story 3

- [X] T031 [US3] Add the baseline revalidation analysis package exports in `src/analysis/baseline_revalidation_after_runtime_repair/__init__.py`
- [X] T032 [US3] Implement the baseline revalidation report builder with required topology provenance, trace-count fields, and no-paper-reproduction wording in `src/analysis/baseline_revalidation_after_runtime_repair/report.py`
- [X] T033 [US3] Generate the JSON report at `artifacts/analysis/baseline-revalidation-after-runtime-repair/baseline-revalidation-report.json`
- [X] T034 [US3] Generate the Markdown report at `artifacts/analysis/baseline-revalidation-after-runtime-repair/baseline-revalidation-report.md`
- [X] T035 [US3] Write optional evaluation artifacts, including per-run JSON, trace JSON, and summary CSV, under `artifacts/evaluation/baseline-revalidation-after-runtime-repair/`

**Checkpoint**: Baseline sanity reporting should now be covered.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup across all stories.

- [X] T036 Validate the full targeted test suite with the approved interpreter in `specs/037-baseline-revalidation-after-runtime-repair/quickstart.md`
- [X] T037 Verify the report schema fields, prerequisite tags, deterministic seeds, topology provenance, and no-curve-fitting / no-paper-reproduction flags in `tests/integration/test_baseline_revalidation_report.py`
- [X] T038 Verify `git status --short` and `git diff --name-only main...HEAD` show only Feature 037 scoped changes

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
Task: "Add approved-topology coverage proving paper_default uses TopologyGraph.from_approved_assumption_registry() and satisfies the Figure 7 invariants in tests/unit/test_baseline_registry_revalidation.py"
Task: "Add horizontal-legal-mask coverage proving every baseline only offloads to approved Figure 7 neighbors, never to self or non-neighbors, in tests/integration/test_baseline_revalidation_after_runtime_repair.py"
Task: "Add environment-path coverage proving each baseline runs through HoodieGymEnvironment, not a direct SlotEngine path, and receives the real legal_action_mask in tests/integration/test_baseline_revalidation_after_runtime_repair.py"
Task: "Add vertical/cloud-legality coverage proving cloud offload remains legal independently of Figure 7 horizontal adjacency in tests/integration/test_baseline_revalidation_after_runtime_repair.py"
```

### User Story 2

```bash
Task: "Add deterministic-seed reproducibility coverage for the baseline revalidation runner in tests/integration/test_baseline_revalidation_after_runtime_repair.py"
Task: "Add RO seed-controlled reproducibility coverage in tests/integration/test_baseline_revalidation_after_runtime_repair.py"
Task: "Add workload-sanity coverage proving N=20, T=110, P=0.5, Δ=0.1, and timeout_slots=20 in tests/integration/test_baseline_revalidation_after_runtime_repair.py"
Task: "Add metrics-schema and numeric sanity coverage in tests/integration/test_baseline_revalidation_report.py"
Task: "Add trace-artifact validity coverage proving per-run JSON, trace JSON, and summary CSV are non-empty valid files in tests/integration/test_baseline_revalidation_report.py"
```

### User Story 3

```bash
Task: "Add report-schema coverage for the required fields in tests/integration/test_baseline_revalidation_report.py"
Task: "Add report-write coverage for JSON and Markdown artifacts in tests/integration/test_baseline_revalidation_report.py"
Task: "Add no-curve-fitting and no-paper-reproduction claim coverage in tests/integration/test_baseline_revalidation_report.py"
Task: "Add runtime-contract drift-guard coverage for Features 032, 033, 034, 035, and 036 in tests/integration/test_baseline_revalidation_scope_guard.py"
Task: "Add scope-guard coverage proving no dependency, training, policy-redesign, or runtime-contract drift in tests/integration/test_baseline_revalidation_scope_guard.py"
Task: "Add approved-topology regression coverage proving the runner rejects complete-graph / all-to-all topology fallback in tests/integration/test_baseline_revalidation_after_runtime_repair.py"
Task: "Add trace-count and pending-task coverage proving revalidation reports arrivals, finalized terminal tasks, and pending-at-horizon counts in tests/integration/test_baseline_revalidation_report.py"
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
