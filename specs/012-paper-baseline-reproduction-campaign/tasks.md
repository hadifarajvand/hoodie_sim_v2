# Tasks: 012-paper-baseline-reproduction-campaign

**Input**: Design documents from `/specs/012-paper-baseline-reproduction-campaign/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the campaign spec artifacts and keep implementation scoped to orchestration only.

- [x] T001 Create `specs/012-paper-baseline-reproduction-campaign/spec.md` with campaign reproduction scope, approved policies/scenarios, and strict no-training/no-plot/no-metric-change constraints
- [x] T002 Create `specs/012-paper-baseline-reproduction-campaign/clarifications.md` capturing the scope locks for no DRL/training, no policy-behavior changes, stdlib-only orchestration, exact registry names, and no silent suppression of missing runs
- [x] T003 Create `specs/012-paper-baseline-reproduction-campaign/plan.md` with constitution gate, architecture, affected modules, and no-dependency policy
- [x] T004 Create `specs/012-paper-baseline-reproduction-campaign/data-model.md` describing `CampaignConfig`, `CampaignRunResult`, and the campaign artifact set
- [x] T005 Create `specs/012-paper-baseline-reproduction-campaign/contracts/campaign.md` defining the campaign orchestration and reporting contract
- [x] T006 Create `specs/012-paper-baseline-reproduction-campaign/quickstart.md` showing how to run a campaign and inspect its artifacts

**Checkpoint**: Feature docs are in place and the implementation surface is bounded.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the shared campaign config before campaign execution exists.

- [x] T007 Add `src/evaluation/campaign_config.py` with `CampaignConfig`
- [x] T008 [P] Add `tests/unit/test_campaign_config.py` covering campaign_name validation, non-empty policies/scenarios/seeds, seed integer validation, output_dir normalization, and deterministic timestamp override

**Checkpoint**: Campaign config is ready for the runner.

## Phase 3: User Story 1 - Run a full reproduction campaign (Priority: P1)

**Goal**: Execute a baseline reproduction campaign across approved policies, scenarios, and seeds.

**Independent Test**: Given a valid campaign configuration, the runner executes the approved policies and scenarios via the shared matrix workflow and records campaign artifacts.

- [x] T009 [US1] Add `src/evaluation/campaign_runner.py`
- [x] T010 [US1] Implement construction of `EvaluationMatrixConfig` in `src/evaluation/campaign_runner.py`
- [x] T011 [US1] Ensure `src/evaluation/campaign_runner.py` calls `EvaluationMatrixRunner` instead of duplicating environment stepping logic
- [x] T012 [US1] Ensure `src/evaluation/campaign_runner.py` calls `ReproducibilityBundleBuilder` after matrix outputs exist
- [x] T013 [US1] Implement campaign artifact writing in `src/evaluation/campaign_runner.py` for `campaign-manifest.json`, `campaign-summary.json`, `policy-summary.json`, `scenario-summary.json`, `determinism-check.json`, and `README.md`

**Checkpoint**: The campaign can execute the shared matrix workflow and emit campaign-level artifacts.

## Phase 4: User Story 2 - Audit campaign outputs (Priority: P2)

**Goal**: Produce grouped summaries and determinism checks that validate campaign outputs without re-running the simulator.

**Independent Test**: Given campaign results, the runner writes grouped summaries and a determinism check using existing final metrics only.

- [x] T014 [US2] Add deterministic aggregation helpers in `src/evaluation/campaign_runner.py`
- [x] T015 [US2] Ensure aggregation in `src/evaluation/campaign_runner.py` uses only `final_metrics` fields from matrix output
- [x] T016 [P] [US2] Add `tests/unit/test_campaign_summary.py` covering aggregate-all-results, group-by-policy, group-by-scenario, no metric formula mutation, and deterministic ordering

**Checkpoint**: Campaign outputs are grouped, auditable, and deterministic.

## Phase 5: User Story 3 - Package campaign reproduction outputs (Priority: P3)

**Goal**: Reference the reproducibility bundle so the campaign remains audit-ready.

**Independent Test**: Given campaign output directories, the campaign references or triggers the reproducibility bundle and records that reference in its artifacts.

- [x] T017 [US3] Add `tests/integration/test_baseline_reproduction_campaign.py`
- [x] T018 [US3] Make the integration test run a tiny campaign with `FLC` + `ADAPTIVE`, `paper_default` + `moderate`, seed `1`, and a small `episode_length` override
- [x] T019 [US3] Extend `tests/integration/test_baseline_reproduction_campaign.py` to verify matrix outputs exist
- [x] T020 [US3] Extend `tests/integration/test_baseline_reproduction_campaign.py` to verify reproducibility bundle outputs exist
- [x] T021 [US3] Extend `tests/integration/test_baseline_reproduction_campaign.py` to verify campaign artifacts exist
- [x] T022 [US3] Extend `tests/integration/test_baseline_reproduction_campaign.py` to verify repeated campaigns with the same timestamp override produce identical campaign artifacts

**Checkpoint**: The campaign references the reproducibility bundle and validates repeated runs.

## Phase 6: Documentation and Traceability

**Purpose**: Keep the paper-to-code mapping honest and document the campaign artifact lifecycle.

- [x] T023 Update `docs/paper_notes/paper_to_code_mapping.md` with mappings for the campaign runner, campaign config, grouped summaries, determinism checks, and bundle reference
- [x] T024 Update `docs/assumptions/hoodie_assumptions.md` only if a new assumption is introduced, and explicitly document any omission of commit/ref metadata when unavailable
- [x] T025 Add a no-dependency-change note in `specs/012-paper-baseline-reproduction-campaign/quickstart.md`
- [x] T026 Add a no-training/no-plotting note in the campaign README output generated by `src/evaluation/campaign_runner.py`

**Checkpoint**: Paper traceability and artifact rules are explicit.

## Phase 7: Guardrails and Validation

**Purpose**: Prove nothing outside scope changed and the campaign workflow works under the existing simulator stack.

- [x] T027 Verify no dependency files changed: `pyproject.toml`, `requirements.txt`, `setup.cfg`, `setup.py`, and lockfiles
- [x] T028 Verify no files under `src/training/` or `src/agents/` changed for this feature
- [x] T029 Verify no policy behavior files changed except import/export wiring if strictly needed
- [x] T030 Verify no environment lifecycle files changed for this feature
- [x] T031 Verify `src/environment/slot_engine.py` still remains helper-only
- [x] T032 Run unit/integration validation for campaign config, campaign summary, and baseline reproduction campaign
- [x] T033 Update `specs/012-paper-baseline-reproduction-campaign/tasks.md` checkboxes only after code, docs, and tests are complete

**Checkpoint**: Scope guardrails and regression coverage are satisfied.

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) has no dependencies
- Foundational (Phase 2) depends on Setup and blocks all user stories
- User Story 1 (Phase 3) depends on Foundational
- User Story 2 (Phase 4) depends on Foundational and the campaign runner
- User Story 3 (Phase 5) depends on Foundational and the campaign runner
- Documentation (Phase 6) depends on stable behavior from the user-story phases
- Guardrails and Validation (Phase 7) runs last

### User Story Dependencies

- **US1** can start after Foundational
- **US2** can start after Foundational and the campaign runner
- **US3** can start after Foundational and the campaign runner

### Parallel Opportunities

- `T008`, `T016`, and `T017` through `T022` can run in parallel with their non-overlapping implementation counterparts
- `T027` through `T032` are independent validation tasks and can be scheduled separately

## Implementation Strategy

### MVP First

1. Complete Phase 1 docs
2. Complete Phase 2 campaign config and validation
3. Complete Phase 3 campaign runner orchestration
4. Stop and validate deterministic campaign output and artifact reference

### Incremental Delivery

1. Add the campaign config and validation
2. Add the serial campaign runner
3. Add artifact emission and grouped summaries
4. Add strict validation and traceability

### Parallel Team Strategy

1. One developer handles `campaign_config.py` and its tests
2. One developer handles `campaign_runner.py` and summary generation
3. One developer handles integration tests for the tiny reproduction campaign
4. One developer handles documentation, assumptions, and validation checks
