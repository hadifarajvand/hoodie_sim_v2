# Tasks: User-Approved Assumption Patch Registry

**Input**: Design documents from `/specs/031-user-approved-assumption-patch-registry/`
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`, `data-model.md`, `quickstart.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the branch and source artifacts before any file edits.

- [X] T001 Verify branch `031-user-approved-assumption-patch-registry` and confirm `.specify/feature.json` points to `specs/031-user-approved-assumption-patch-registry`
- [X] T002 Confirm the current source documents are present for `specs/031-user-approved-assumption-patch-registry/plan.md`, `specs/031-user-approved-assumption-patch-registry/spec.md`, `specs/031-user-approved-assumption-patch-registry/research.md`, `specs/031-user-approved-assumption-patch-registry/data-model.md`, and `specs/031-user-approved-assumption-patch-registry/quickstart.md`
- [X] T003 Confirm the approved interpreter path is available at `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python` and record it as the only interpreter boundary for governance checks
- [X] T004 Verify the working tree does not already contain unintended drift in `.specify/memory/constitution.md`, `AGENTS.md`, `docs/reproducibility.md`, `resources/papers/hoodie/recovered/user-approved-assumption-registry.json`, or `artifacts/analysis/user-approved-assumption-patch-registry/`

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared validation helpers for registry counts, governance consistency, and diff-scope guards.

- [X] T005 Create shared validation helpers for registry counts, status buckets, and no-paper-recovery assertions in `tests/unit/test_user_approved_assumption_patch_registry_registry.py`
- [X] T006 Create shared validation helpers for constitution version consistency, semver classification, and interpreter-path consistency in `tests/integration/test_user_approved_assumption_patch_registry_policy_guard.py`
- [X] T007 Define the final diff classification rules for Feature 031 in `tests/integration/test_user_approved_assumption_patch_registry_scope_guard.py`
- [X] T008 Record the intentional governance/docs scope in `specs/031-user-approved-assumption-patch-registry/spec.md` so the branch diff is treated as one combined feature

## Phase 3: User Story 1 - Registry Validation and Audit Controls (Priority: P1)

**Goal**: Prove the assumption registry stays at 8 approved entries with no paper-recovery claim, no runtime drift, and no proposed or blocked spillover.

**Independent Test**: The registry and report checks pass from the generated JSON artifacts alone, with no need to inspect runtime code.

### Tests for User Story 1

- [X] T009 [P] [US1] Add a unit test in `tests/unit/test_user_approved_assumption_patch_registry_registry.py` that asserts `resources/papers/hoodie/recovered/user-approved-assumption-registry.json` contains exactly 8 entries
- [X] T010 [P] [US1] Add a unit test in `tests/unit/test_user_approved_assumption_patch_registry_registry.py` that asserts all 8 registry entries are `approved`
- [X] T011 [P] [US1] Add a unit test in `tests/unit/test_user_approved_assumption_patch_registry_registry.py` that asserts `proposed_items` is empty, `blocked_items` is empty, and `rejected_items` is empty
- [X] T012 [P] [US1] Add a unit test in `tests/unit/test_user_approved_assumption_patch_registry_registry.py` that asserts `runtime_usable_items` contains all 8 entries
- [X] T013 [P] [US1] Add an integration test in `tests/integration/test_user_approved_assumption_patch_registry_report.py` that asserts every entry preserves `no_paper_recovery_claim=true`
- [X] T014 [P] [US1] Add an integration test in `tests/integration/test_user_approved_assumption_patch_registry_report.py` that asserts `runtime_patch_applied=false` wherever `proposed_value` is present
- [X] T015 [P] [US1] Add an integration test in `tests/integration/test_user_approved_assumption_patch_registry_report.py` that asserts `no_runtime_behavior_change=true`, `no_training_or_policy_drift=true`, and `no_dependency_drift=true`
- [X] T016 [US1] Add a deterministic JSON sanity test for `artifacts/analysis/user-approved-assumption-patch-registry/assumption-patch-report.json` in `tests/integration/test_user_approved_assumption_patch_registry_report.py`

### Implementation for User Story 1

- [X] T017 [US1] Validate that `resources/papers/hoodie/recovered/user-approved-assumption-registry.json` still contains the 8 approved entries and no extra status buckets in `src/analysis/user_approved_assumption_patch_registry/registry.py`
- [X] T018 [US1] Validate that `Figure_7_adjacency`, `legal_horizontal_destinations`, `EA_private_cpu_capacity`, `EA_public_cpu_capacity`, `cloud_cpu_capacity`, `cloud_data_rate`, `timeout_value`, and `multi_agent_aggregation_reduction_order` remain the only registry items in `src/analysis/user_approved_assumption_patch_registry/registry.py`
- [X] T019 [US1] Validate that every approved entry preserves `paper_status`, `paper_confidence`, and `no_paper_recovery_claim=true` in `src/analysis/user_approved_assumption_patch_registry/registry.py`
- [X] T020 [US1] Regenerate `resources/papers/hoodie/recovered/user-approved-assumption-registry.json` and `artifacts/analysis/user-approved-assumption-patch-registry/assumption-patch-report.json` from the registry source in `src/analysis/user_approved_assumption_patch_registry/registry.py` and `src/analysis/user_approved_assumption_patch_registry/report.py`
- [X] T021 [US1] Regenerate `artifacts/analysis/user-approved-assumption-patch-registry/assumption-patch-report.md` with the approved 8-item summary in `src/analysis/user_approved_assumption_patch_registry/report.py`

## Phase 4: User Story 2 - Governance and Runtime Guidance Reconciliation (Priority: P2)

**Goal**: Make the governance/docs reconciliation explicit and internally consistent while keeping it MINOR-level and aligned to `1.4.0`.

**Independent Test**: The constitution, reproducibility guidance, and active feature metadata can be checked for version/path consistency without touching runtime behavior.

### Tests for User Story 2

- [X] T022 [P] [US2] Add a version-consistency test for `.specify/memory/constitution.md` in `tests/integration/test_user_approved_assumption_patch_registry_policy_guard.py`
- [X] T023 [P] [US2] Add an interpreter-path consistency test for `.specify/memory/constitution.md` and `docs/reproducibility.md` in `tests/integration/test_user_approved_assumption_patch_registry_policy_guard.py`
- [X] T024 [P] [US2] Add a semver-scope test that fails if `1.4.0` is not the selected constitution version in `specs/031-user-approved-assumption-patch-registry/spec.md`, `specs/031-user-approved-assumption-patch-registry/plan.md`, or `specs/031-user-approved-assumption-patch-registry/tasks.md`, or if the constitution does not retain principles 21 through 30 as an intentional MINOR governance expansion
- [X] T025 [P] [US2] Add a metadata-scope test for `.specify/feature.json` in `tests/integration/test_user_approved_assumption_patch_registry_scope_guard.py`

### Implementation for User Story 2

- [X] T026 [US2] Inspect `.specify/memory/constitution.md` and validate the Sync Impact Report version is `Version change: 1.3.0 -> 1.4.0`
- [X] T027 [US2] Validate `.specify/memory/constitution.md` footer is `**Version**: 1.4.0` and that principles 21 through 30 are intentionally retained
- [X] T028 [US2] Update `docs/reproducibility.md` only if needed so interpreter/runtime guidance matches `.specify/memory/constitution.md`
- [X] T029 [US2] Update `AGENTS.md` only if needed to keep the governance entry point aligned with `specs/031-user-approved-assumption-patch-registry/plan.md`
- [X] T030 [US2] Decide the final handling of `.specify/feature.json` and restore it to the main-branch value if active-feature metadata is not intentionally tracked for this feature
- [X] T031 [US2] Confirm the approved interpreter path is exactly `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python` in the constitution and reproducibility guidance

## Phase 5: User Story 3 - Scope Guards and Final Diff Classification (Priority: P3)

**Goal**: Prove the feature does not drift into runtime, training, dependency, topology, or Feature 030 pollution and that the final diff can be classified cleanly.

**Independent Test**: The final validation suite can fail the feature if any forbidden file family changes or if runtime adoption is implied.

### Tests for User Story 3

- [X] T032 [P] [US3] Add a diff-scope test in `tests/integration/test_user_approved_assumption_patch_registry_scope_guard.py` that fails if runtime config files change
- [X] T033 [P] [US3] Add a diff-scope test in `tests/integration/test_user_approved_assumption_patch_registry_scope_guard.py` that fails if training or neural-network files change
- [X] T034 [P] [US3] Add a diff-scope test in `tests/integration/test_user_approved_assumption_patch_registry_scope_guard.py` that fails if dependency files, policy files, baseline files, or campaign files change
- [X] T035 [P] [US3] Add a drift-guard test in `tests/integration/test_user_approved_assumption_patch_registry_scope_guard.py` that fails if Feature 030 artifacts are mutated to claim paper recovery
- [X] T036 [P] [US3] Add a runtime-adoption test in `tests/integration/test_user_approved_assumption_patch_registry_policy_guard.py` that confirms no runtime patches are applied by Feature 031

### Implementation for User Story 3

- [X] T037 [US3] Wire the scope-guard checks into the registry validation flow in `tests/integration/test_user_approved_assumption_patch_registry_scope_guard.py`
- [X] T038 [US3] Wire the constitution/version checks into the governance reconciliation validation flow in `tests/integration/test_user_approved_assumption_patch_registry_policy_guard.py`
- [X] T039 [US3] Run the Feature 031 targeted test suite and capture the final validation output in `tests/integration/test_user_approved_assumption_patch_registry_report.py`
- [X] T040 [US3] Verify `src/environment/compute_config.py`, `src/environment/link_rate_config.py`, runtime topology loading, timeout/drop runtime logic, reward runtime changes, training code, neural networks, dependency files, and campaign/baseline/policy files remain unchanged in `tests/integration/test_user_approved_assumption_patch_registry_scope_guard.py`

## Phase 6: Final Diff and Reporting

**Purpose**: Produce the final diff summary and classify every changed file by feature type.

- [X] T041 Prepare the final changed-file inventory for Feature 031 in `specs/031-user-approved-assumption-patch-registry/tasks.md`
- [X] T042 Classify each changed file as Feature 031 spec artifact, Feature 031 plan artifact, Feature 031 tasks artifact, Feature 031 registry/report implementation, Feature 031 generated artifact, or intentional governance/runtime-guidance file in `specs/031-user-approved-assumption-patch-registry/tasks.md`
- [X] T043 Confirm the final report states that all 8 items are approved, no proposed items remain, no blocked items remain, no rejected items remain, and no runtime behavior changed in `artifacts/analysis/user-approved-assumption-patch-registry/assumption-patch-report.md`

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 must complete before any validation or file updates begin.
- Phase 2 blocks both registry validation and governance reconciliation work.
- Phase 3 depends on the shared registry substrate from Phases 1-2.
- Phase 4 depends on the governance scope having been explicitly accepted in the spec and plan.
- Phase 5 depends on the registry and governance work both being in place.
- Phase 6 depends on every prior phase being complete.

### User Story Dependencies

- **US1**: Can start after Phase 2 and is independent of governance edits.
- **US2**: Can start after Phase 2 and should not modify registry behavior.
- **US3**: Depends on the validation hooks established by US1 and US2.

### Within Each User Story

- Tests must be written before the corresponding implementation validation task.
- Registry validation must confirm the 8-entry approved state before any diff-scope work.
- Governance reconciliation must confirm version/path consistency before final diff classification.

## Parallel Opportunities

- `T009`, `T010`, `T011`, `T012`, `T013`, `T014`, `T015`, and `T016` can run in parallel because they inspect distinct registry properties.
- `T022`, `T023`, and `T025` can run in parallel because they cover independent governance checks.
- `T032`, `T033`, `T034`, and `T035` can run in parallel because they cover separate forbidden file classes.

## Implementation Strategy

### MVP First

1. Complete Phases 1-2.
2. Complete User Story 1 registry validation.
3. Stop and verify the 8 approved entries, empty proposed/blocked/rejected lists, and preserved no-paper-recovery claims.

### Incremental Delivery

1. Lock registry validation first.
2. Add governance reconciliation checks next.
3. Finish with scope guards and final diff classification.

### Parallel Team Strategy

1. One contributor handles US1 registry validation.
2. One contributor handles US2 governance reconciliation.
3. One contributor handles US3 scope guards and final diff reporting.
