# Tasks: Controlled Mechanistic Sweeps

**Input**: Design documents from `/specs/020-controlled-mechanistic-sweeps/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md  
**Tests**: Required. This feature is a diagnostic analysis workflow and must be driven by tests before implementation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Lock down branch hygiene and forbidden-path guardrails before any analysis code is written.

- [X] T001 Add the branch hygiene and scope-guard integration test in `tests/integration/test_controlled_mechanistic_sweeps_scope_guard.py` to reject changes to `src/environment`, `src/policies`, `src/training`, `src/metrics`, campaign runners, dependency files, lockfiles, existing campaign artifacts, and plot outputs

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define the tiny controlled sweep schema and the qualitative classification rules before implementation.

- [X] T002 [US1] Add sweep-definition schema tests for the `arrival_probability` family in `tests/unit/test_controlled_mechanistic_sweeps.py`
- [X] T003 [US1] Add sweep-definition schema tests for the `timeout` family in `tests/unit/test_controlled_mechanistic_sweeps.py`
- [X] T004 [US1] Add sweep-definition schema tests for the `cpu_capacity` family in `tests/unit/test_controlled_mechanistic_sweeps.py`
- [X] T005 [US1] Add sweep-definition schema tests for the `link_rate` family in `tests/unit/test_controlled_mechanistic_sweeps.py`
- [X] T006 [US1] Add sweep-definition schema tests for the `topology_density` family in `tests/unit/test_controlled_mechanistic_sweeps.py`
- [X] T007 [US1] Add monotonic classification tests in `tests/unit/test_controlled_mechanistic_sweeps.py` for pass, warn, inconclusive, and instrumentation_gap behavior
- [X] T008 [US2] Add report schema tests in `tests/unit/test_controlled_mechanistic_sweeps.py` for metadata, sweep definitions, fixed inputs, observations, monotonic checks, warnings, instrumentation gaps, limitations, reproducibility, and overall status
- [X] T009 [US2] Add no-paper-validity and no-campaign-rerun disclaimer tests in `tests/unit/test_controlled_mechanistic_sweeps.py`
- [X] T010 [US1] Add the integration test in `tests/integration/test_controlled_mechanistic_sweeps_flow.py` that runs the tiny controlled sweeps through existing public interfaces where possible
- [X] T011 [US1] Add the integration test in `tests/integration/test_controlled_mechanistic_sweeps_flow.py` that verifies unsupported or unobservable sweep dimensions are reported as inconclusive or instrumentation_gap

**Checkpoint**: The sweep schema, qualitative checks, and public-interface limitations are covered before implementation begins.

---

## Phase 3: User Story 1 - Diagnostic Tiny Sweeps (Priority: P1) 🎯 MVP

**Goal**: Execute tiny deterministic sweeps and summarize only qualitative monotonic behavior from the current public interfaces.

**Independent Test**: The tiny sweeps produce deterministic output on repeated runs, and each sweep family is classified as pass, warn, inconclusive, or instrumentation_gap without any plotting or campaign reruns.

### Implementation for User Story 1

- [X] T012 [US1] Create the isolated analysis package scaffold in `src/analysis/controlled_mechanistic_sweeps/__init__.py`
- [X] T013 [US1] Implement sweep definition and fixed-input modeling in `src/analysis/controlled_mechanistic_sweeps/sweeps.py`
- [X] T014 [US1] Implement qualitative monotonic classification logic in `src/analysis/controlled_mechanistic_sweeps/classify.py`
- [X] T015 [US1] Implement the tiny deterministic sweep runner in `src/analysis/controlled_mechanistic_sweeps/runner.py`
- [X] T016 [US1] Implement the deterministic JSON and Markdown report writer in `src/analysis/controlled_mechanistic_sweeps/report.py`

### Validation for User Story 1

- [X] T017 [US1] Add the quick validation guidance in `specs/020-controlled-mechanistic-sweeps/quickstart.md` with the exact approved interpreter and artifact paths
- [X] T018 [US1] Add the final diff and scope audit in `tests/integration/test_controlled_mechanistic_sweeps_final_diff.py` to verify no forbidden source paths, dependency files, campaign artifacts, plots, or simulator changes are introduced

**Checkpoint**: Tiny sweeps run deterministically, report only qualitative monotonic behavior, and stay within diagnostic-only scope.

---

## Phase 4: User Story 2 - Limitations and Diagnostic Framing (Priority: P2)

**Goal**: Ensure the report clearly states what the sweeps do not prove.

**Independent Test**: The generated report contains the required no-paper-validity and no-campaign-rerun disclaimers and remains explicitly non-optimizing and non-reproducing.

### Implementation for User Story 2

- [X] T019 [US2] Document the report framing and limitation language in `specs/020-controlled-mechanistic-sweeps/research.md` so the feature remains diagnostic-only

### Validation for User Story 2

- [X] T020 [US2] Add the no-paper-validity and limitation coverage assertions to `tests/unit/test_controlled_mechanistic_sweeps.py`

**Checkpoint**: The report and documentation clearly state the feature is diagnostic only and not a paper-validity claim.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: No dependencies. Establish the scope guard first.
- **Phase 2**: Depends on Phase 1. Sweep schema and test scaffolding must exist before implementation.
- **Phase 3**: Depends on Phase 2. The implementation can start only after the tiny sweep definitions and monotonic tests are in place.
- **Phase 4**: Depends on Phase 3. The limitation framing is validated after the sweep workflow exists.

### Task Dependencies

- `T001` must complete before any implementation work begins.
- `T002`, `T003`, `T004`, `T005`, `T006`, `T007`, `T008`, `T009`, `T010`, and `T011` must be written before `T012`.
- `T012` must complete before `T013`, `T014`, `T015`, and `T016`.
- `T016` must complete before `T017` and `T018`.
- `T019` must complete before `T020`.

### Within the User Story

- Tests first, then the isolated analysis package implementation.
- Deterministic report writing follows the runner and classification logic.
- Documentation and final diff audit happen after the core sweep workflow exists.

## Parallel Opportunities

- None are marked here to avoid fake parallelism. The task list is intentionally serialized around the single diagnostic workflow.

## Implementation Strategy

### MVP First

1. Complete `T001` to lock the scope guard and branch hygiene.
2. Complete `T002`-`T011` so the tiny sweep definitions, monotonic checks, and public-interface constraints are covered before implementation.
3. Complete `T012`-`T016` to build the isolated analysis workflow.
4. Complete `T017`-`T020` to validate the report, scope, and diagnostic-only framing.

### Incremental Delivery

1. Add the schema and monotonic tests first.
2. Implement the tiny sweep runner and report writer second.
3. Verify the output artifacts third.
4. Tighten the report language and scope guard last.

## Notes

- The feature is diagnostic analysis only.
- No baseline campaigns are rerun.
- No plots are introduced.
- No simulator or environment behavior changes are allowed.
- No paper-level completeness claim is permitted.

## Acceptance Mapping

- `CHK021` is satisfied by `T002`, `T003`, `T004`, `T005`, and `T006` because they define sweep schema coverage for all five dimensions.
- `CHK022` is satisfied by `T007`, `T008`, `T010`, and `T011` because they enforce qualitative monotonic behavior and no-optimization behavior.
- `CHK023` is satisfied by `T001`, `T009`, `T017`, `T018`, `T019`, and `T020` because they guard against campaign reruns and preserve diagnostic-only scope.
- `CHK024` is satisfied by `T015`, `T016`, and `T017` because they produce deterministic JSON/Markdown summaries without plotting.
- `CHK025` is satisfied by `T009`, `T019`, and `T020` because they require the report to state limitations and avoid paper-validity claims.
