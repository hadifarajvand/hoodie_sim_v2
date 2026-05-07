# Tasks: Baseline Sensitivity Analysis

**Input**: Design documents from `/specs/014-baseline-sensitivity-analysis/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the read-only analysis skeleton and keep scope limited to committed artifact inspection.

- [ ] T001 Create `src/analysis/baseline_sensitivity.py` with deterministic analyzer entry points and report data structures described in the plan
- [ ] T002 Create `tests/unit/test_baseline_sensitivity.py` covering read-only artifact loading, deterministic ordering, and missing-artifact handling for sensitivity inputs

**Checkpoint**: The analyzer has a defined source file and a focused unit test surface.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the shared artifact loading and signature helpers that all sensitivity stories depend on.

- [ ] T003 Implement artifact loading in `src/analysis/baseline_sensitivity.py` for campaign summaries, matrix per-run JSON, matrix-summary.csv, trace JSON, and optional audit-report.json inputs
- [ ] T004 Implement deterministic artifact ordering and stable path normalization in `src/analysis/baseline_sensitivity.py`
- [ ] T005 Implement helper routines in `src/analysis/baseline_sensitivity.py` for trace grouping by scenario and seed
- [ ] T006 Implement helper routines in `src/analysis/baseline_sensitivity.py` for policy grouping and scenario grouping

**Checkpoint**: The analyzer can load existing artifacts and derive stable grouped views without mutating inputs.

## Phase 3: User Story 1 - Explain Trace Collapse (Priority: P1)

**Goal**: Compare trace inputs across scenarios and seeds to determine whether the baseline collapse begins in the traffic realization itself.

**Independent Test**: Given the committed campaign artifacts, the analyzer reports trace identity, task-count differences, arrival-slot distribution differences, and task-size differences without rerunning the campaign.

- [ ] T007 [US1] Implement trace comparison across scenario pairs and seeds in `src/analysis/baseline_sensitivity.py`
- [ ] T008 [P] [US1] Add `tests/unit/test_baseline_sensitivity.py` coverage for identical trace detection and different trace detection
- [ ] T009 [US1] Implement moderate vs paper_default trace comparison reporting in `src/analysis/baseline_sensitivity.py`
- [ ] T010 [US1] Implement trace-level report classification in `src/analysis/baseline_sensitivity.py` for `trace_input_collapsed` and `insufficient_evidence`

**Checkpoint**: The analyzer can prove whether trace inputs are collapsed or distinguishable.

## Phase 4: User Story 2 - Explain Policy Collapse (Priority: P2)

**Goal**: Compare policy action and terminal outcome behavior to determine whether several baselines are effectively equivalent.

**Independent Test**: Given the committed campaign artifacts, the analyzer reports policy signatures and identifies identical or near-identical behavior without relying on simulator reruns.

- [ ] T011 [US2] Implement policy action distribution analysis in `src/analysis/baseline_sensitivity.py`
- [ ] T012 [US2] Implement terminal outcome distribution analysis in `src/analysis/baseline_sensitivity.py`
- [ ] T013 [US2] Implement policy signature comparison in `src/analysis/baseline_sensitivity.py`
- [ ] T014 [P] [US2] Extend `tests/unit/test_baseline_sensitivity.py` coverage for identical policy signature detection and near-identical outcome detection
- [ ] T015 [US2] Implement policy-level report classification in `src/analysis/baseline_sensitivity.py` for `policy_behavior_collapsed`

**Checkpoint**: The analyzer can tell whether BCO/FLC/MLEO behave equivalently or only appear similar through aggregation.

## Phase 5: User Story 3 - Explain Saturation and Masking (Priority: P3)

**Goal**: Diagnose whether saturation, timeout/finalization pressure, or aggregation masking is hiding distinctions in the committed outputs.

**Independent Test**: Given the committed campaign artifacts, the analyzer reports saturation signals, scenario output collapse, and accounting status deterministically.

- [ ] T016 [US3] Implement scenario sensitivity comparison in `src/analysis/baseline_sensitivity.py` for throughput, drop ratio, average delay, and completed/dropped totals
- [ ] T017 [US3] Implement saturation diagnosis in `src/analysis/baseline_sensitivity.py` using completed/dropped/total counts and delay patterns
- [ ] T018 [P] [US3] Add `tests/integration/test_baseline_sensitivity_flow.py` covering a complete analysis against `artifacts/campaigns/paper-baseline-reproduction`
- [ ] T019 [US3] Extend `tests/integration/test_baseline_sensitivity_flow.py` to verify accounting remains clean and existing artifacts are not modified
- [ ] T020 [US3] Implement report classification in `src/analysis/baseline_sensitivity.py` for `scenario_output_collapsed`, `saturation_dominant`, and `accounting_clean`

**Checkpoint**: The analyzer can explain whether saturation or masking is dominating the observed collapse.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Keep the analyzer deterministic, documented, and aligned with the paper-to-code mapping.

- [ ] T021 Update `docs/paper_notes/paper_to_code_mapping.md` with the sensitivity-analysis-to-artifact-inspection mapping
- [ ] T022 Update `docs/assumptions/hoodie_assumptions.md` only if the analysis introduces a new assumption about sensitivity thresholds or diagnostic interpretation
- [ ] T023 Verify `src/analysis/baseline_sensitivity.py` does not mutate input artifacts and preserves deterministic output ordering
- [ ] T024 Run unit and integration validation for the baseline sensitivity analysis feature

**Checkpoint**: Analysis reporting is complete, reproducible, and documented.

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) has no dependencies
- Foundational (Phase 2) depends on Setup and blocks all user stories
- User Story 1 (Phase 3) depends on Foundational
- User Story 2 (Phase 4) depends on Foundational and the trace/policy grouping helpers
- User Story 3 (Phase 5) depends on Foundational and the scenario/accounting helpers
- Polish (Phase 6) runs after all story phases

### User Story Dependencies

- **US1** can start after Foundational
- **US2** can start after Foundational and the shared policy grouping helpers
- **US3** can start after Foundational and the scenario/accounting helpers

### Parallel Opportunities

- `T002`, `T008`, `T014`, and `T018` can run in parallel with non-overlapping implementation tasks
- `T021` through `T024` can be scheduled after the feature logic stabilizes

## Implementation Strategy

### MVP First

1. Complete trace comparison and moderate versus paper_default identity checks
2. Add policy signature comparison and collapse detection
3. Add saturation and accounting diagnostics
4. Validate against the committed paper-baseline-reproduction artifacts

### Incremental Delivery

1. Build the artifact loader and report skeleton
2. Add trace-level analysis
3. Add policy-level analysis
4. Add saturation and masking diagnostics plus regression tests

### Parallel Team Strategy

1. One developer handles `baseline_sensitivity.py` artifact loading and report generation
2. One developer handles trace comparison and unit coverage
3. One developer handles policy/saturation diagnostics and integration coverage
4. One developer handles documentation and validation checks

