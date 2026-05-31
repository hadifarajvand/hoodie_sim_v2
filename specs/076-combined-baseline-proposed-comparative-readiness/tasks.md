# Feature 076 Tasks

## Status

Spec Kit preparation complete; implementation pending.

## Tasks

- [X] T001 Confirm dependency base from Feature 075 commit `b23b2fa5b1c8fc6d58f3eb533164f83c05c2ec61`.
- [X] T002 Create Feature 076 branch.
- [X] T003 Add Feature 076 specification.
- [X] T004 Add Feature 076 plan.
- [X] T005 Add Feature 076 data model.
- [ ] T006 Add Feature 076 report contract.
- [ ] T007 Add Feature 076 requirements checklist.
- [ ] T008 Implement read-only analysis package under `src/analysis/combined_baseline_proposed_comparative_readiness/`.
- [ ] T009 Implement scope guard.
- [ ] T010 Implement model entities: CombinedPolicyRow, CombinedPolicyAggregate, CombinedRegressionEvidence, CombinedComparativeReadinessReport.
- [ ] T011 Consume and normalize Feature 074 baseline rows.
- [ ] T012 Consume and normalize Feature 075 proposed-method rows.
- [ ] T013 Validate full 7 method by 7 scenario matrix, total 49 rows.
- [ ] T014 Compute per-policy and per-method aggregates.
- [ ] T015 Implement report rendering with claim boundary.
- [ ] T016 Add unit tests for model validation, missing coverage, duplicate rows, action-bound enforcement, compatibility rejection, aggregate correctness, and scope guard.
- [ ] T017 Add integration tests for consuming Feature 074 and Feature 075 reports into one combined matrix.
- [ ] T018 Run targeted regression slices for Features 068R through 075.
- [ ] T019 Run Feature 076 unit and integration tests.
- [ ] T020 Run git diff check and Feature 076 scope validator.
- [ ] T021 Commit and push only.

## Required Implementation Package

- `src/analysis/combined_baseline_proposed_comparative_readiness/__init__.py`
- `src/analysis/combined_baseline_proposed_comparative_readiness/__main__.py`
- `src/analysis/combined_baseline_proposed_comparative_readiness/config.py`
- `src/analysis/combined_baseline_proposed_comparative_readiness/model.py`
- `src/analysis/combined_baseline_proposed_comparative_readiness/report.py`
- `src/analysis/combined_baseline_proposed_comparative_readiness/runner.py`

## Required Tests

- `tests/unit/test_combined_baseline_proposed_comparative_readiness_model.py`
- `tests/unit/test_combined_baseline_proposed_comparative_readiness_report.py`
- `tests/unit/test_combined_baseline_proposed_comparative_readiness_scope_guard.py`
- `tests/integration/test_combined_baseline_proposed_comparative_readiness_report.py`

## Completion Criteria

- Report status is `combined_baseline_proposed_comparative_readiness_ready`.
- Report passed value is true.
- All seven policy/method IDs are present.
- All seven scenario IDs are present for each policy/method.
- Total row count is 49.
- Every row is action-bound.
- No row uses compatibility mode.
- Aggregates are computed from rows.
- Claim boundaries are explicit.
- No PR is opened.
- No merge is performed.
