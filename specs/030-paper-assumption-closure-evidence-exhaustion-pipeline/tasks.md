# Tasks: Paper Assumption Closure and Evidence Exhaustion Pipeline

**Input**: Design documents from `/specs/030-paper-assumption-closure-evidence-exhaustion-pipeline/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the feature boundary, source gates, and report paths before any classification logic exists.

- [ ] T001 Verify branch `030-paper-assumption-closure-evidence-exhaustion-pipeline` and confirm the feature directory in `.specify/feature.json` resolves to `specs/030-paper-assumption-closure-evidence-exhaustion-pipeline`
- [ ] T002 Verify the branch base is `main` after the `029-reward-equation-terminal-reward-contract-complete` tag and confirm the working tree is clean before analysis in `artifacts/analysis/`
- [ ] T003 Verify required input artifacts exist at `resources/papers/hoodie/ocr/merged.tex`, `resources/papers/hoodie/ocr/merged.md`, `resources/papers/hoodie/ocr/merged.txt`, `resources/papers/hoodie/ocr/merged.json`, `resources/papers/hoodie/HOODIE_paper.pdf`, `resources/papers/hoodie/recovered/topology-g.json`, `resources/papers/hoodie/recovered/paper-parameter-registry.json`, `artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.json`, `artifacts/analysis/structured-paper-topology-linkrate-registry/topology-recovery-report.json`, `artifacts/analysis/computation-delay-cpu-unit-validation/unit-validation-report.json`, and `artifacts/analysis/reward-equation-terminal-reward-contract/reward-contract-report.json`
- [ ] T004 Define the source gate list and report output paths in `src/analysis/paper_assumption_closure_evidence_exhaustion/runner.py` and `src/analysis/paper_assumption_closure_evidence_exhaustion/report.py`

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the reusable inventory, evidence, and reporting substrate before item classification.

- [ ] T005 Create the analysis package scaffold in `src/analysis/paper_assumption_closure_evidence_exhaustion/__init__.py` and `src/analysis/paper_assumption_closure_evidence_exhaustion/runner.py`
- [ ] T006 [P] Define the inventory item and evidence record structures in `src/analysis/paper_assumption_closure_evidence_exhaustion/data.py`
- [ ] T007 [P] Define the report summary and report artifact structures in `src/analysis/paper_assumption_closure_evidence_exhaustion/report.py`
- [ ] T008 Add deterministic source loading helpers for paper OCR, recovered registries, and prior feature reports in `src/analysis/paper_assumption_closure_evidence_exhaustion/source_loader.py`
- [ ] T009 Add canonical item-key normalization and deduplication helpers in `src/analysis/paper_assumption_closure_evidence_exhaustion/inventory.py`
- [ ] T010 Add report schema constants, final-status vocabulary, and confidence vocabulary in `src/analysis/paper_assumption_closure_evidence_exhaustion/schema.py`

## Phase 3: User Story 1 - Exhaust Paper Gaps (Priority: P1)

**Goal**: Inventory every known paper-related uncovered or assumption-backed item from the approved source set and produce a deduplicated working set for evidence search.

**Independent Test**: The inventory can be produced from the source inputs without any runtime mutation and includes all known high-risk items.

### Tests for User Story 1

- [ ] T011 [P] [US1] Add inventory extraction tests for prior reports in `tests/unit/test_paper_assumption_closure_inventory.py`
- [ ] T012 [P] [US1] Add source-gate tests for required artifact presence in `tests/integration/test_paper_assumption_closure_source_gates.py`

### Implementation for User Story 1

- [ ] T013 [US1] Read Feature 025 topology/link-rate report and Feature 028 unit validation report in `src/analysis/paper_assumption_closure_evidence_exhaustion/source_loader.py`
- [ ] T014 [US1] Read Feature 029 reward contract report, `resources/papers/hoodie/recovered/paper-parameter-registry.json`, and `resources/papers/hoodie/recovered/topology-g.json` in `src/analysis/paper_assumption_closure_evidence_exhaustion/source_loader.py`
- [ ] T015 [US1] Extract `unrecoverable_items`, `assumption_backed_items`, `partially_recovered` fields, runtime assumption-backed fields, and blocked topology/legal-destination fields in `src/analysis/paper_assumption_closure_evidence_exhaustion/inventory.py`
- [ ] T016 [US1] Deduplicate inventory items by canonical key and emit the in-memory inventory for later classification in `src/analysis/paper_assumption_closure_evidence_exhaustion/inventory.py`

## Phase 4: User Story 2 - Distinguish Evidence From Assumption (Priority: P2)

**Goal**: Search all approved evidence sources for each inventory item, record contradictions, and classify each item with the approved final-status vocabulary.

**Independent Test**: A full item-by-item classification can be produced, and every item resolves to exactly one final status.

### Tests for User Story 2

- [ ] T017 [P] [US2] Add evidence-search coverage tests for topology, CPU capacity, timeout, reward aggregation, and Phi_n^pub formatting in `tests/unit/test_paper_assumption_closure_evidence_search.py`
- [ ] T018 [P] [US2] Add contradiction and classification tests in `tests/integration/test_paper_assumption_closure_classification.py`

### Implementation for User Story 2

- [ ] T019 [US2] Search OCR text sources for topology, adjacency, connectivity, CPU capacity, timeout, deadline, reward aggregation, and `Phi_n^pub` formatting terms in `src/analysis/paper_assumption_closure_evidence_exhaustion/evidence_search.py`
- [ ] T020 [US2] Cross-check each candidate against recovered registries and prior analysis reports, recording contradictions explicitly in `src/analysis/paper_assumption_closure_evidence_exhaustion/evidence_search.py`
- [ ] T021 [US2] Implement the final item classifier with statuses `recovered`, `partially_recovered`, `contradicted`, `assumption_backed_requires_user_approval`, `unrecoverable_after_evidence_exhaustion`, and `out_of_scope` in `src/analysis/paper_assumption_closure_evidence_exhaustion/classifier.py`
- [ ] T022 [US2] Annotate each classified item with source methods, snippets, confidence, runtime approval requirement, and evidence-exhaustion rationale in `src/analysis/paper_assumption_closure_evidence_exhaustion/classifier.py`

## Phase 5: User Story 3 - Produce Audit-Ready Evidence (Priority: P3)

**Goal**: Generate deterministic JSON and Markdown closure reports that clearly distinguish recovered items, assumption-backed items, unrecoverable items, and manual-review cases.

**Independent Test**: The report artifact can be regenerated from unchanged inputs and produces the same structure and classifications.

### Tests for User Story 3

- [ ] T023 [P] [US3] Add JSON schema and report-shape tests in `tests/integration/test_paper_assumption_closure_report.py`
- [ ] T024 [P] [US3] Add deterministic output and no-drift tests in `tests/unit/test_paper_assumption_closure_report_determinism.py`

### Implementation for User Story 3

- [ ] T025 [US3] Add manual evidence fields and `manual_review_required` flags to the item schema in `src/analysis/paper_assumption_closure_evidence_exhaustion/data.py`
- [ ] T026 [US3] Support per-edge confidence entries for Figure 7 manual topology recovery without fabricating edges in `src/analysis/paper_assumption_closure_evidence_exhaustion/data.py`
- [ ] T027 [US3] Implement the JSON report writer with `summary`, `items`, per-status arrays, `runtime_dependency_decisions`, and drift booleans in `src/analysis/paper_assumption_closure_evidence_exhaustion/report.py`
- [ ] T028 [US3] Implement the Markdown report writer and deterministic ordering rules in `src/analysis/paper_assumption_closure_evidence_exhaustion/report.py`
- [ ] T029 [US3] Generate `artifacts/analysis/paper-assumption-closure-evidence-exhaustion/assumption-closure-report.json` and `artifacts/analysis/paper-assumption-closure-evidence-exhaustion/assumption-closure-report.md` from `src/analysis/paper_assumption_closure_evidence_exhaustion/runner.py`

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the full closure pipeline, guard against forbidden drift, and prepare the final summary.

- [ ] T030 [P] Add tests proving known high-risk items are present, C=40 stays recovered from Feature 029, unrecoverable items include evidence-exhaustion rationale, and assumption-backed items require approval in `tests/integration/test_paper_assumption_closure_completeness.py`
- [ ] T031 [P] Add a no-forbidden-files diff guard that blocks changes to training, dependency, topology fabrication, policy, or runtime files in `tests/integration/test_paper_assumption_closure_scope_guard.py`
- [ ] T032 Run targeted Feature 030 tests, generate the report, parse the JSON, and inspect the git diff in `/Users/hadi/Documents/GitHub/hoodie_sim_v2/.venv/bin/python` via `src/analysis/paper_assumption_closure_evidence_exhaustion/runner.py`
- [ ] T033 Summarize files changed, commands run, tests run, generated artifacts, recovered items, unrecoverable items, assumption-backed items needing approval, final verdict, and next action in the completion note for `specs/030-paper-assumption-closure-evidence-exhaustion-pipeline/`

## Dependencies & Execution Order

### Phase Dependencies

- Setup tasks in Phase 1 must complete before any inventory or evidence work begins.
- Foundational tasks in Phase 2 block all user-story work.
- User Story 1 must complete before later story phases can produce a meaningful closure report.
- User Stories 2 and 3 depend on the inventory substrate from User Story 1 and the shared schema from Phase 2.
- Polish tasks depend on the report writer being available.

### User Story Dependencies

- **User Story 1**: Can start after Foundational phase completion.
- **User Story 2**: Depends on the inventory produced by User Story 1 and the shared schema from Phase 2.
- **User Story 3**: Depends on the classification output from User Story 2 and the manual-review fields from User Story 2/Phase 2.

### Within Each User Story

- Inventory and source loading must be complete before evidence search.
- Evidence search must be complete before final classification.
- Classification must be complete before report generation.
- Tests must name the exact source files they validate.

## Parallel Opportunities

- `T006` and `T007` can run in parallel because they define separate data/report structures.
- `T011` and `T012` can run in parallel because they validate separate gates and artifact discovery paths.
- `T017` and `T018` can run in parallel because they cover different evidence and contradiction concerns.
- `T023` and `T024` can run in parallel because one checks schema shape and the other checks determinism.
- `T030` and `T031` can run in parallel because they validate completeness and forbidden-drift scope independently.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 source gates.
2. Complete Phase 2 inventory substrate.
3. Complete User Story 1 inventory extraction.
4. Stop and validate that every known paper-gap item is represented before evidence search.

### Incremental Delivery

1. Build inventory extraction and deduplication first.
2. Add evidence search and classification next.
3. Add manual-review and report generation last.
4. Finish with deterministic validation and scope guards.
