# Tasks: Paper Mechanism Registry

## Phase 1: Setup (Shared Infrastructure)

- [X] T001 Create the 016 spec structure under `specs/016-paper-mechanism-registry/` with `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, and `quickstart.md`
- [X] T002 Create the registry output directory path convention for `artifacts/analysis/paper-mechanism-registry/` in `src/analysis/paper_mechanism_registry.py`

## Phase 2: Foundational (Blocking Prerequisites)

- [X] T003 Define the registry data schema and validation rules in `src/analysis/paper_mechanism_registry.py`
- [X] T004 Define the OCR source loader and deterministic snippet extraction helpers in `src/analysis/paper_mechanism_registry.py`
- [X] T005 Define the mechanism classification vocabulary for paper status, implementation status, assumption risk, and next-action values in `src/analysis/paper_mechanism_registry.py`
- [X] T006 Define the output render contract for `paper-mechanism-registry.json` and `paper-mechanism-registry.md` in `src/analysis/paper_mechanism_registry.py`

## Phase 3: User Story 1 - Read the Mechanism Registry (Priority: P1) 🎯 MVP

**Goal**: Build a read-only registry that covers all required mechanism categories with explicit paper evidence or missing markers.

**Independent Test**: Run the registry builder against committed OCR inputs and verify all 25 required mechanism categories appear with a status, evidence, and gap summary.

### Tests for User Story 1

- [X] T007 [P] [US1] Add unit coverage for OCR evidence extraction and missing-evidence handling in `tests/unit/test_paper_mechanism_registry.py`
- [X] T008 [P] [US1] Add integration coverage for the real OCR source and artifact inputs in `tests/integration/test_paper_mechanism_registry_flow.py`

### Implementation for User Story 1

- [X] T009 [P] [US1] Implement OCR loading and evidence snippet extraction from `resources/papers/hoodie/ocr/merged.tex` in `src/analysis/paper_mechanism_registry.py`
- [X] T010 [US1] Implement mechanism entries for the required 25 categories in `src/analysis/paper_mechanism_registry.py`
- [X] T011 [US1] Implement missing and ambiguous detail handling in `src/analysis/paper_mechanism_registry.py`

## Phase 4: User Story 2 - Trace Claims to Evidence (Priority: P2)

**Goal**: Preserve deterministic OCR traceability for every mechanism claim.

**Independent Test**: Inspect the generated registry and confirm each entry includes OCR evidence metadata with source path and deterministic snippet location.

### Tests for User Story 2

- [X] T012 [P] [US2] Add unit coverage for schema fields, deterministic ordering, and OCR evidence metadata in `tests/unit/test_paper_mechanism_registry.py`
- [X] T013 [P] [US2] Add integration coverage for repeated identical registry generation in `tests/integration/test_paper_mechanism_registry_flow.py`

### Implementation for User Story 2

- [X] T014 [US2] Implement deterministic evidence references with source path, context, figure or equation reference, and snippet index in `src/analysis/paper_mechanism_registry.py`
- [X] T015 [US2] Implement JSON rendering for `paper-mechanism-registry.json` in `src/analysis/paper_mechanism_registry.py`
- [X] T016 [US2] Implement Markdown rendering for `paper-mechanism-registry.md` in `src/analysis/paper_mechanism_registry.py`

## Phase 5: User Story 3 - Separate Paper Facts From Project Mapping (Priority: P3)

**Goal**: Separate paper-documented mechanisms from project-side mappings and assumptions.

**Independent Test**: Verify each entry includes a current project mapping field and a next-action field that clearly distinguishes project mapping from paper evidence.

### Tests for User Story 3

- [X] T017 [P] [US3] Add unit coverage for project mapping labels, high-risk assumptions, and blocking gaps in `tests/unit/test_paper_mechanism_registry.py`
- [X] T018 [P] [US3] Add integration coverage for read-only behavior and forbidden-path protection in `tests/integration/test_paper_mechanism_registry_flow.py`

### Implementation for User Story 3

- [X] T019 [US3] Implement project mapping support and next-action classification in `src/analysis/paper_mechanism_registry.py`
- [X] T020 [US3] Integrate optional secondary evidence inputs and optional analysis artifacts as context only in `src/analysis/paper_mechanism_registry.py`
- [X] T021 [US3] Add report summary sections for blocking gaps, high-risk assumptions, and implementation gap summary in `src/analysis/paper_mechanism_registry.py`

## Final Phase: Polish & Cross-Cutting Concerns

- [X] T022 Update `docs/paper_notes/paper_to_code_mapping.md` only if a registry-specific mapping note is required
- [X] T023 Run `src/.venvmac/bin/python -m unittest tests.unit.test_paper_mechanism_registry tests.integration.test_paper_mechanism_registry_flow`
- [X] T024 Verify repeated runs produce byte-identical JSON and Markdown outputs for `artifacts/analysis/paper-mechanism-registry/`
- [X] T025 Verify forbidden paths remain unchanged: `src/environment/*`, `src/policies/*`, `src/evaluation/metrics.py`, `src/training/*`, `src/agents/*`, dependency files, and simulator configs
- [X] T026 Verify registry outputs are written only to the caller-provided analysis output directory and do not mutate committed paper or campaign artifacts
- [X] T027 Update `specs/016-paper-mechanism-registry/tasks.md` checkboxes only after validation passes

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories
- **User Stories (Phase 3+)**: Depend on Foundational completion
- **Final Phase**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can begin after Foundational tasks complete
- **User Story 2 (P2)**: Can begin after Foundational tasks complete and may reuse User Story 1 helpers
- **User Story 3 (P3)**: Can begin after Foundational tasks complete and may reuse prior story outputs, but must remain independently testable

### Within Each User Story

- Tests must be added before the corresponding implementation tasks are finalized
- Shared registry schema work must precede story-specific rendering details
- Evidence extraction must precede summary and classification rendering

## Parallel Opportunities

- T007 and T008 can run in parallel because they touch different test files
- T009 can run in parallel with T007 and T008 because it touches the implementation file
- T012 and T013 can run in parallel because they touch different test behaviors
- T014, T015, and T016 can proceed in sequence after the evidence model is in place
- T017 and T018 can run in parallel because they touch different integration and unit concerns

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational phases
2. Complete User Story 1
3. Stop and validate the registry against the committed OCR inputs

### Incremental Delivery

1. Deliver the core registry and evidence extraction first
2. Add deterministic traceability and rendering
3. Add project mapping and gap classification
4. Finish with validation, forbidden-path checks, and determinism verification
