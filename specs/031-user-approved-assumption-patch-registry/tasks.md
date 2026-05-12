# Tasks: User-Approved Assumption Patch Registry

**Input**: Design documents from `/specs/031-user-approved-assumption-patch-registry/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the feature gate, source gate, and output locations before any registry logic exists.

- [X] T001 Verify branch `031-user-approved-assumption-patch-registry` and confirm `.specify/feature.json` points to `specs/031-user-approved-assumption-patch-registry`
- [X] T002 Verify the branch base is `main` after the `030-paper-assumption-closure-evidence-exhaustion-pipeline-complete` tag and confirm the working tree is clean before analysis in `resources/papers/hoodie/recovered/` and `artifacts/analysis/`
- [X] T003 Verify required input artifact exists at `artifacts/analysis/paper-assumption-closure-evidence-exhaustion/assumption-closure-report.json`
- [X] T004 Verify no dependency, training, runtime simulator, TorchRL, Gymnasium, ns-3, baseline, policy, or campaign files are touched before implementation in `src/analysis/user_approved_assumption_patch_registry/`, `resources/papers/hoodie/recovered/`, and `artifacts/analysis/user-approved-assumption-patch-registry/`

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared registry and report substrate before candidate mapping or artifact generation.

- [X] T005 Create the analysis package scaffold in `src/analysis/user_approved_assumption_patch_registry/__init__.py` and `src/analysis/user_approved_assumption_patch_registry/runner.py`
- [X] T006 [P] Define the registry entry schema in `src/analysis/user_approved_assumption_patch_registry/registry.py` with `item_id`, `paper_status`, `paper_confidence`, `assumption_status`, `proposed_value`, `value_type`, `runtime_use_allowed`, `approval_required`, `approval_source`, `rationale`, `scientific_risk`, `affected_runtime_components`, `validation_plan`, and `no_paper_recovery_claim`
- [X] T007 [P] Define the report artifact schema in `src/analysis/user_approved_assumption_patch_registry/report.py` with `feature_id`, `schema_version`, `source_gates`, `registry_path`, `item_count`, `status_counts`, `runtime_usable_items`, `proposed_items`, `blocked_items`, `rejected_items`, `entries`, `no_paper_recovery_claims`, `no_runtime_behavior_change`, `no_training_or_policy_drift`, `no_dependency_drift`, and `final_verdict`
- [X] T008 Add deterministic source-loading helpers for the Feature 030 closure report in `src/analysis/user_approved_assumption_patch_registry/registry.py`
- [X] T009 Add candidate filtering helpers that reject any item not present in the Feature 030 closure report in `src/analysis/user_approved_assumption_patch_registry/registry.py`

## Phase 3: User Story 1 - Build the Assumption Registry (Priority: P1)

**Goal**: Build a closed, analysis-only registry of all in-scope Feature 030 gaps with explicit proposed/blocked decisions and preserved paper status.

**Independent Test**: The registry can be generated from the closure report without any runtime mutation and every candidate appears exactly once with its initial status.

### Tests for User Story 1

- [X] T010 [P] [US1] Add source-gate and registry-coverage tests in `tests/unit/test_user_approved_assumption_patch_registry_source_gate.py`
- [X] T011 [P] [US1] Add schema and initial-status tests in `tests/unit/test_user_approved_assumption_patch_registry_registry.py`

### Implementation for User Story 1

- [X] T012 [US1] Load and validate the Feature 030 closure report in `src/analysis/user_approved_assumption_patch_registry/registry.py`
- [X] T013 [US1] Extract only `unrecoverable_after_evidence_exhaustion` and `partially_recovered` items and filter to the in-scope Feature 031 candidates in `src/analysis/user_approved_assumption_patch_registry/registry.py`
- [X] T014 [US1] Map `Figure_7_adjacency`, `legal_horizontal_destinations`, and `timeout_value` to `blocked_no_assumption` in `src/analysis/user_approved_assumption_patch_registry/registry.py`
- [X] T015 [US1] Map `EA_private_cpu_capacity`, `EA_public_cpu_capacity`, `cloud_cpu_capacity`, `cloud_data_rate`, and `multi_agent_aggregation_reduction_order` to proposed report-only assumptions with `runtime_use_allowed=false` in `src/analysis/user_approved_assumption_patch_registry/registry.py`
- [X] T016 [US1] Preserve `paper_status` and `paper_confidence` unchanged while constructing registry entries in `src/analysis/user_approved_assumption_patch_registry/registry.py`
- [X] T017 [US1] Populate non-empty `rationale`, `scientific_risk`, `affected_runtime_components`, and `validation_plan` for every registry entry in `src/analysis/user_approved_assumption_patch_registry/registry.py`

## Phase 4: User Story 2 - Generate Audit Artifacts (Priority: P2)

**Goal**: Emit deterministic JSON and Markdown artifacts that separate blocked items from proposed assumptions and never claim paper recovery.

**Independent Test**: The registry report can be regenerated from unchanged inputs, parses as JSON, and clearly distinguishes blocked, proposed, and approved states.

### Tests for User Story 2

- [X] T018 [P] [US2] Add JSON parse and required-key tests for the registry and report artifacts in `tests/integration/test_user_approved_assumption_patch_registry_report.py`
- [X] T019 [P] [US2] Add deterministic output and no-paper-recovery-claim tests in `tests/unit/test_user_approved_assumption_patch_registry_determinism.py`
- [X] T020 [US2] Add validation tests that fail if any registry or report entry has empty `rationale`, `scientific_risk`, `affected_runtime_components`, or `validation_plan` in `tests/integration/test_user_approved_assumption_patch_registry_report.py`

### Implementation for User Story 2

- [X] T021 [US2] Generate `resources/papers/hoodie/recovered/user-approved-assumption-registry.json` in `src/analysis/user_approved_assumption_patch_registry/registry.py`
- [X] T022 [US2] Generate `artifacts/analysis/user-approved-assumption-patch-registry/assumption-patch-report.json` in `src/analysis/user_approved_assumption_patch_registry/report.py`
- [X] T023 [US2] Generate `artifacts/analysis/user-approved-assumption-patch-registry/assumption-patch-report.md` with deterministic ordering and explicit blocked/proposed/runtime-usable sections in `src/analysis/user_approved_assumption_patch_registry/report.py`
- [X] T024 [US2] Ensure no registry entry writes `no_paper_recovery_claim=false` and no approved assumption exists without an explicit approval source in `src/analysis/user_approved_assumption_patch_registry/report.py`

## Phase 5: User Story 3 - Validate Scope and Drift Guards (Priority: P3)

**Goal**: Prove the registry remains analysis-only, runtime-blocked unless approved, and free of forbidden-file drift.

**Independent Test**: Validation checks confirm that proposed assumptions remain report-only, blocked items stay blocked, and no runtime/training/dependency files are modified.

### Tests for User Story 3

- [X] T025 [P] [US3] Add runtime-gate tests that verify `runtime_use_allowed=true` is impossible unless `assumption_status=approved` in `tests/integration/test_user_approved_assumption_patch_registry_runtime_gate.py`
- [X] T026 [P] [US3] Add no-topology/no-timeout-invention tests in `tests/integration/test_user_approved_assumption_patch_registry_policy_guard.py`
- [X] T027 [P] [US3] Add diff-scope tests that reject runtime simulator, training, policy, baseline, dependency, TorchRL, Gymnasium, ns-3, and campaign-file edits in `tests/integration/test_user_approved_assumption_patch_registry_scope_guard.py`

### Implementation for User Story 3

- [X] T028 [US3] Enforce runtime-use gating, approval-required flags, and blocked/proposed/rejected status separation in `src/analysis/user_approved_assumption_patch_registry/registry.py`
- [X] T029 [US3] Mark `Figure_7_adjacency` and `legal_horizontal_destinations` as blocked-no-assumption unless manual topology is supplied in `src/analysis/user_approved_assumption_patch_registry/registry.py`
- [X] T030 [US3] Preserve `timeout_value` as blocked-no-assumption and prevent invented timeout values in `src/analysis/user_approved_assumption_patch_registry/registry.py`
- [X] T031 [US3] Keep CPU capacity, cloud data-rate, and aggregation-order values report-only unless an explicit approval source is present in `src/analysis/user_approved_assumption_patch_registry/registry.py`

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the full registry pipeline, ensure deterministic outputs, and prepare the final implementation summary.

- [X] T032 Run targeted Feature 031 tests, generate the registry and report artifacts, parse the JSON outputs, and inspect the git diff in `src/analysis/user_approved_assumption_patch_registry/runner.py`
- [X] T033 Verify `AGENTS.md` and `.specify/feature.json` are updated intentionally for Feature 031 and are not left as accidental pollution in the final diff
- [X] T034 Summarize files changed, commands run, tests run, generated artifacts, registry decisions, blocked items, any approved assumptions, final verdict, and next action in the completion note for `specs/031-user-approved-assumption-patch-registry/`

## Dependencies & Execution Order

### Phase Dependencies

- Setup tasks in Phase 1 must complete before any registry or report work begins.
- Foundational tasks in Phase 2 block all user-story work.
- User Story 1 must complete before later story phases can produce a meaningful registry artifact.
- User Story 2 depends on the registry substrate from User Story 1 and the shared report schema from Phase 2.
- User Story 3 depends on the registry decisions from User Story 1 and the artifact writer from User Story 2.
- Polish tasks depend on the report writer being available.

### User Story Dependencies

- **User Story 1**: Can start after Foundational phase completion.
- **User Story 2**: Depends on the registry produced by User Story 1 and the shared schema from Phase 2.
- **User Story 3**: Depends on the registry/report output from User Story 2 and the approval gating from User Story 1.

### Within Each User Story

- Source validation must be complete before candidate mapping.
- Candidate mapping must be complete before report generation.
- Report generation must be complete before scope and drift validation.
- Tests must name the exact source files they validate.

## Parallel Opportunities

- `T006` and `T007` can run in parallel because they define separate schemas.
- `T010` and `T011` can run in parallel because one validates source gates and one validates registry schema.
- `T017` and `T018` can run in parallel because they cover different artifact properties.
- `T023`, `T024`, and `T025` can run in parallel because they cover separate runtime, policy, and diff-scope guards.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 source gates.
2. Complete Phase 2 schema and loading substrate.
3. Complete User Story 1 registry mapping.
4. Stop and validate that every in-scope item is either blocked or proposed before artifact generation.

### Incremental Delivery

1. Build registry construction and initial decision mapping first.
2. Add report generation next.
3. Finish with runtime and scope guards.
4. Validate deterministic outputs and forbidden-file drift last.
