# Tasks: Feature 064 - Final Review and Release Gate Batch

## Phase 1: Setup

- [ ] T001 Create the feature contract docs in `specs/064-final-review-release-gate-batch/`
- [ ] T002 Create the architecture note at `docs/architecture/euls_phase23_final_review_release_gate_batch.md`
- [ ] T003 Create the analysis package skeleton in `src/analysis/final_review_release_gate_batch/`

## Phase 2: Diagnostics Core

- [ ] T004 Implement the feature config and artifact-path contract in `src/analysis/final_review_release_gate_batch/config.py`
- [ ] T005 Implement the review and report dataclasses in `src/analysis/final_review_release_gate_batch/model.py`
- [ ] T006 Implement JSON and Markdown writers in `src/analysis/final_review_release_gate_batch/report.py`
- [ ] T007 Implement matplotlib-only diagnostic figures in `src/analysis/final_review_release_gate_batch/figures.py`
- [ ] T008 Implement read-only evidence loading and gate synthesis in `src/analysis/final_review_release_gate_batch/runner.py`

## Phase 3: Tests

- [ ] T009 Add schema and diagnostics tests in `tests/unit/test_final_review_release_gate_batch_schema.py`
- [ ] T010 Add claim-safety tests in `tests/unit/test_final_review_release_gate_batch_claim_safety.py`
- [ ] T011 Add integration coverage for the gate command in `tests/integration/test_final_review_release_gate_batch.py`
- [ ] T012 Add report and scope-guard coverage in the remaining integration tests

## Phase 4: Validation

- [ ] T013 Run `py_compile`, the gate command, and the focused pytest selection
- [ ] T014 Verify `git diff --name-only 063-staged-training-budget-learning-curve...HEAD`, `git diff --stat`, `git diff --check`, and `git status --short --untracked-files=no`
