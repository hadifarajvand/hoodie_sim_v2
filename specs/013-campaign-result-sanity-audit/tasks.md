# Tasks: Campaign Result Sanity Audit

**Input**: Design documents from `/specs/013-campaign-result-sanity-audit/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the audit feature skeleton and keep scope read-only.

- [x] T001 Create `src/analysis/campaign_audit.py` with the audit entry points and report data structures described in the plan
- [x] T002 Create `tests/unit/test_campaign_audit_config.py` covering read-only artifact discovery, deterministic ordering, and missing-artifact handling for audit inputs

**Checkpoint**: The audit feature has a defined source file and a focused unit test surface.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the shared artifact inventory and reconciliation logic that all audit stories depend on.

- [x] T003 Implement artifact inventory loading in `src/analysis/campaign_audit.py` for campaign, matrix, bundle, and trace directories
- [x] T004 Implement deterministic artifact ordering and stable path normalization in `src/analysis/campaign_audit.py`
- [x] T005 Implement baseline accounting reconciliation helpers in `src/analysis/campaign_audit.py` for campaign totals versus per-run matrix records
- [x] T006 Implement summary extraction helpers in `src/analysis/campaign_audit.py` for campaign-summary and matrix-summary inputs

**Checkpoint**: Audit inputs can be loaded and reconciled without changing any artifact files.

## Phase 3: User Story 1 - Inspect Campaign Artifacts (Priority: P1)

**Goal**: Inspect completed campaign artifacts and report what exists, what is missing, and whether the artifact set looks structurally complete.

**Independent Test**: Given a completed campaign artifact directory, the audit returns a deterministic inventory report without mutating any files.

- [x] T007 [US1] Implement campaign artifact inventory reporting in `src/analysis/campaign_audit.py`
- [x] T008 [P] [US1] Add `tests/unit/test_campaign_audit_report.py` covering inventory output, missing-artifact reporting, and stable report ordering
- [x] T009 [US1] Implement human-readable audit summary generation in `src/analysis/campaign_audit.py`
- [x] T010 [US1] Implement machine-readable audit summary generation in `src/analysis/campaign_audit.py`

**Checkpoint**: The audit can enumerate the campaign artifact set and emit a deterministic report.

## Phase 4: User Story 2 - Explain Anomalies (Priority: P2)

**Goal**: Explain unusual drop ratios, weak policy differentiation, and weak scenario differentiation using only the existing artifacts.

**Independent Test**: Given the baseline campaign artifacts, the audit flags and categorizes the anomaly signals without rerunning the campaign.

- [x] T011 [US2] Implement high drop-ratio detection in `src/analysis/campaign_audit.py`
- [x] T012 [US2] Implement scenario differentiation analysis in `src/analysis/campaign_audit.py`
- [x] T013 [US2] Implement policy differentiation analysis in `src/analysis/campaign_audit.py`
- [x] T014 [P] [US2] Add `tests/unit/test_campaign_audit_report.py` coverage for anomaly categorization and deterministic anomaly ordering
- [x] T015 [US2] Extend `tests/unit/test_campaign_audit_report.py` to verify the audit explains near-identical baseline outcomes without asserting a single speculative root cause

**Checkpoint**: The audit explains the suspicious aggregate patterns seen in the campaign outputs.

## Phase 5: User Story 3 - Check Accounting Consistency (Priority: P3)

**Goal**: Detect missing finalization and accounting inconsistencies between campaign totals and the underlying matrix records.

**Independent Test**: Given campaign summaries and per-run outputs, the audit reports reconciliation success or inconsistency deterministically.

- [x] T016 [US3] Implement finalized-task accounting checks in `src/analysis/campaign_audit.py`
- [x] T017 [US3] Implement consistency status generation in `src/analysis/campaign_audit.py` for total tasks, completed tasks, dropped tasks, and run counts
- [x] T018 [P] [US3] Add `tests/integration/test_campaign_result_sanity_audit.py` covering a complete audit against existing campaign artifacts
- [x] T019 [US3] Extend `tests/integration/test_campaign_result_sanity_audit.py` to verify missing-finalization or reconciliation mismatches are surfaced explicitly

**Checkpoint**: The audit can prove whether the summarized totals reconcile with the underlying campaign records.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Keep the audit deterministic, documented, and aligned with the paper-to-code mapping.

- [x] T020 Update `docs/paper_notes/paper_to_code_mapping.md` with the audit-to-artifact inspection mapping
- [x] T021 Update `docs/assumptions/hoodie_assumptions.md` only if the audit introduces a new assumption about anomaly thresholds or reconciliation rules
- [x] T022 Verify `src/analysis/campaign_audit.py` does not mutate input artifacts and preserves deterministic output ordering
- [x] T023 Run unit and integration validation for the campaign audit feature

**Checkpoint**: Audit reporting is complete, reproducible, and documented.

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) has no dependencies
- Foundational (Phase 2) depends on Setup and blocks all user stories
- User Story 1 (Phase 3) depends on Foundational
- User Story 2 (Phase 4) depends on Foundational and the audit inventory/reporting helpers
- User Story 3 (Phase 5) depends on Foundational and the accounting reconciliation helpers
- Polish (Phase 6) runs after all story phases

### User Story Dependencies

- **US1** can start after Foundational
- **US2** can start after Foundational and the shared report inventory
- **US3** can start after Foundational and the reconciliation helpers

### Parallel Opportunities

- `T002`, `T008`, `T014`, and `T018` can run in parallel with non-overlapping implementation tasks
- `T020` through `T023` can be scheduled after the feature logic stabilizes

## Implementation Strategy

### MVP First

1. Complete the shared audit inventory and deterministic report structure
2. Add the anomaly categorization for drop ratio, scenario separation, and policy separation
3. Add accounting reconciliation for finalized-task totals
4. Validate against existing campaign artifacts

### Incremental Delivery

1. Build the audit inventory and human-readable report
2. Add machine-readable report output
3. Add anomaly detection categories
4. Add accounting consistency checks and regression tests

### Parallel Team Strategy

1. One developer handles `campaign_audit.py` inventory and report generation
2. One developer handles anomaly detection logic and unit coverage
3. One developer handles accounting reconciliation and integration coverage
4. One developer handles documentation and validation checks
