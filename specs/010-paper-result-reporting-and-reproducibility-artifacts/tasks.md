# Tasks: 010-paper-result-reporting-and-reproducibility-artifacts

**Input**: Design documents from `/specs/010-paper-result-reporting-and-reproducibility-artifacts/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the reproducibility bundle spec artifacts and keep implementation scoped to artifact packaging only.

- [x] T001 Create `specs/010-paper-result-reporting-and-reproducibility-artifacts/spec.md` with reproducibility bundle scope, artifact outputs, and strict no-training/no-plot/no-metric-change constraints
- [x] T002 Create `specs/010-paper-result-reporting-and-reproducibility-artifacts/clarifications.md` capturing the scope locks for no plotting, no metric recomputation, stdlib-only checksums, deterministic timestamps, and missing-artifact reporting
- [x] T003 Create `specs/010-paper-result-reporting-and-reproducibility-artifacts/plan.md` with constitution gate, architecture, affected modules, and no-dependency policy
- [x] T004 Create `specs/010-paper-result-reporting-and-reproducibility-artifacts/data-model.md` describing `ReproducibilityBundleConfig`, `ArtifactRecord`, `ValidationSummary`, and bundle outputs
- [x] T005 Create `specs/010-paper-result-reporting-and-reproducibility-artifacts/contracts/reproducibility-bundle.md` defining the bundle input and output contract
- [x] T006 Create `specs/010-paper-result-reporting-and-reproducibility-artifacts/quickstart.md` showing how to package matrix outputs into a reproducibility bundle

**Checkpoint**: Feature docs are in place and the implementation surface is bounded.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the shared bundle config and artifact model before bundle generation exists.

- [x] T007 Add `src/analysis/reproducibility_bundle.py` with `ReproducibilityBundleConfig`, `ArtifactRecord`, `ValidationSummary`, and `ReproducibilityBundleBuilder`
- [x] T008 [P] Add `tests/unit/test_reproducibility_bundle.py` covering checksum calculation, relative path indexing, missing artifact validation, and deterministic timestamp override

**Checkpoint**: Bundle config and artifact model are ready for the builder.

## Phase 3: User Story 1 - Package a completed evaluation run (Priority: P1)

**Goal**: Package a completed evaluation matrix output directory into a reproducibility bundle.

**Independent Test**: Run the packager on a completed matrix output directory and confirm it writes the required bundle files.

- [x] T009 [US1] Implement `manifest.json` generation in `src/analysis/reproducibility_bundle.py`
- [x] T010 [US1] Implement `run-config.json` generation in `src/analysis/reproducibility_bundle.py`
- [x] T011 [US1] Implement `artifact-index.json` generation in `src/analysis/reproducibility_bundle.py`
- [x] T012 [US1] Implement `validation-summary.json` generation in `src/analysis/reproducibility_bundle.py`
- [x] T013 [US1] Implement `README.md` generation in `src/analysis/reproducibility_bundle.py`

**Checkpoint**: The packager can emit the full reproducibility bundle.

## Phase 4: User Story 2 - Preserve run provenance (Priority: P2)

**Goal**: Record the exact evaluation configuration and checksum-bearing artifact inventory for later audit.

**Independent Test**: Generate the bundle twice with the same inputs and deterministic timestamp override and confirm the metadata is identical.

- [x] T014 [US2] Extend `src/analysis/reproducibility_bundle.py` to scan `matrix_output_dir` for per-run JSON files, `matrix-summary.csv`, and `traces/` files
- [x] T015 [US2] Extend `src/analysis/reproducibility_bundle.py` to compute SHA-256 checksums and file sizes for discovered artifacts
- [x] T016 [P] [US2] Add stable artifact sorting and deterministic JSON serialization in `src/analysis/reproducibility_bundle.py`

**Checkpoint**: Bundle provenance and inventory are reproducible and auditable.

## Phase 5: User Story 3 - Validate bundle completeness (Priority: P3)

**Goal**: Produce a clear completeness signal for the artifact bundle.

**Independent Test**: Validate a bundle directory and confirm the summary reports expected runs, discovered runs, missing artifacts, and pass/fail status.

- [x] T017 [US3] Extend `src/analysis/reproducibility_bundle.py` to compute expected run count from policies, scenarios, and seeds
- [x] T018 [US3] Extend `src/analysis/reproducibility_bundle.py` to record missing expected artifacts in `validation-summary.json`
- [x] T019 [P] [US3] Add bundle completeness assertions to `tests/integration/test_reproducibility_bundle_flow.py`

**Checkpoint**: The bundle carries an explicit completeness result.

## Phase 6: Matrix Integration and Regression Coverage

**Purpose**: Prove the packager works with real evaluation matrix output and remains deterministic.

- [x] T020 [P] Add `tests/integration/test_reproducibility_bundle_flow.py` that runs a tiny `EvaluationMatrixRunner` matrix and packages the output
- [x] T021 [P] Extend `tests/integration/test_reproducibility_bundle_flow.py` to verify required files exist: `manifest.json`, `run-config.json`, `artifact-index.json`, `validation-summary.json`, and `README.md`
- [x] T022 [P] Extend `tests/integration/test_reproducibility_bundle_flow.py` to verify repeated bundle generation with the same timestamp override is deterministic

**Checkpoint**: Matrix output can be packaged and reproduced deterministically.

## Phase 7: Documentation and Traceability

**Purpose**: Keep the paper-to-code mapping honest and document the artifact lifecycle.

- [x] T023 Update `docs/paper_notes/paper_to_code_mapping.md` with mappings for the reproducibility bundle builder, manifest, index, and validation summary
- [x] T024 Update `docs/assumptions/hoodie_assumptions.md` only if a new assumption is introduced, and explicitly document any omission of commit/ref metadata when unavailable
- [x] T025 Add a no-dependency-change note in `specs/010-paper-result-reporting-and-reproducibility-artifacts/quickstart.md`

**Checkpoint**: Paper traceability and artifact rules are explicit.

## Phase 8: Guardrails and Validation

**Purpose**: Prove nothing outside scope changed and the bundle builder works under the existing simulator stack.

- [x] T026 Verify no dependency files changed: `pyproject.toml`, `requirements.txt`, `setup.cfg`, `setup.py`, and lockfiles
- [x] T027 Verify no files under `src/training/` or `src/agents/` changed for this feature
- [x] T028 Verify no metric formula changes were introduced
- [x] T029 Verify no environment lifecycle files changed except import-only wiring if required
- [x] T030 Run unit tests: `tests/unit/test_reproducibility_bundle.py`
- [x] T031 Run integration tests: `tests/integration/test_reproducibility_bundle_flow.py`, `tests/integration/test_evaluation_matrix_runner.py`, and `tests/unit/test_slot_engine.py`
- [x] T032 Update `specs/010-paper-result-reporting-and-reproducibility-artifacts/tasks.md` checkboxes only after code, docs, and tests are complete

**Checkpoint**: Scope guardrails and regression coverage are satisfied.

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) has no dependencies
- Foundational (Phase 2) depends on Setup and blocks all user stories
- User Story 1 (Phase 3) depends on Foundational
- User Story 2 (Phase 4) depends on Foundational and the bundle builder
- User Story 3 (Phase 5) depends on Foundational and the bundle builder
- Matrix Integration (Phase 6) depends on the builder and bundle outputs
- Documentation (Phase 7) depends on stable behavior from the user-story phases
- Guardrails and Validation (Phase 8) runs last

### User Story Dependencies

- **US1** can start after Foundational
- **US2** can start after Foundational and the bundle builder
- **US3** can start after Foundational and the bundle builder

### Parallel Opportunities

- `T008`, `T016`, `T019`, `T020`, `T021`, and `T022` can run in parallel with their non-overlapping implementation counterparts
- `T026` through `T031` are independent validation tasks and can be scheduled separately

## Implementation Strategy

### MVP First

1. Complete Phase 1 docs
2. Complete Phase 2 bundle config and artifact model
3. Complete Phase 3 bundle file generation
4. Stop and validate deterministic bundle output and validation summary

### Incremental Delivery

1. Add the bundle config and artifact record model
2. Add the serial bundle builder
3. Add artifact emission and validation summary generation
4. Add strict validation and traceability

### Parallel Team Strategy

1. One developer handles `reproducibility_bundle.py` and the bundle file generation logic
2. One developer handles unit tests for checksums, indexing, and missing-artifact validation
3. One developer handles the integration flow using `EvaluationMatrixRunner`
4. One developer handles documentation, assumptions, and validation checks
