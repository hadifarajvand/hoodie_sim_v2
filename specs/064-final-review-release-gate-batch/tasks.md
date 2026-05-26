# Tasks: Feature 064 — Final Review and Release Gate Batch

## A. Prerequisite gates

- [ ] T001 Verify `main` contains Feature 063 merge evidence.
- [ ] T002 Verify Feature 063 report has `final_verdict = results_export_reproducibility_documentation_batch_passed`.
- [ ] T003 Verify Feature 063 report has `remaining_blockers = []`.
- [ ] T004 Verify all Feature 063 final export artifacts exist.

## B. Model and package

- [ ] T005 Create `src/analysis/final_review_release_gate_batch/config.py`.
- [ ] T006 Create `src/analysis/final_review_release_gate_batch/model.py`.
- [ ] T007 Create `src/analysis/final_review_release_gate_batch/report.py`.
- [ ] T008 Create `src/analysis/final_review_release_gate_batch/runner.py`.
- [ ] T009 Create `src/analysis/final_review_release_gate_batch/__init__.py` and `__main__.py`.

## C. Batch item 1 — final repository state audit

- [ ] T010 Generate `final-repository-state-audit.json`.
- [ ] T011 Verify release evidence is source-backed and committed.
- [ ] T012 Verify no final gate logic requires uncommitted local state.

## D. Batch item 2 — final artifact completeness gate

- [ ] T013 Generate `final-artifact-completeness-gate.json`.
- [ ] T014 Verify all required Feature 063 final exports exist.
- [ ] T015 Verify all referenced source artifacts exist.

## E. Batch item 3 — final claim boundary review

- [ ] T016 Generate `final-claim-boundary-review.json`.
- [ ] T017 Verify no paper reproduction claim.
- [ ] T018 Verify no unsupported superiority claim.
- [ ] T019 Verify supported claims map to committed artifacts.

## F. Batch item 4 — release tag readiness package

- [ ] T020 Generate `release-tag-readiness-package.md`.
- [ ] T021 Recommend release tag name but do not create the tag.
- [ ] T022 Include exact release prerequisites and post-merge tag command.

## G. Batch item 5 — final handoff and next-work recommendation

- [ ] T023 Generate `final-handoff-and-next-work.md`.
- [ ] T024 Summarize supported results, unsupported claims, known limitations, and recommended thesis/paper workflow.

## H. Safety gates

- [ ] T025 Validate no training rerun or new experiment output.
- [ ] T026 Validate no dependency, policy, environment, or reward-timing drift.
- [ ] T027 Validate no prior Feature 037–063 artifacts are rewritten.
- [ ] T028 Validate no release tag is created inside this feature.

## I. Tests

- [ ] T029 Add `tests/unit/test_final_review_release_gate_batch_schema.py`.
- [ ] T030 Add `tests/unit/test_final_review_release_gate_batch_metrics.py`.
- [ ] T031 Add `tests/unit/test_final_review_release_gate_batch_behavior_equivalence.py`.
- [ ] T032 Add `tests/integration/test_final_review_release_gate_batch.py`.
- [ ] T033 Add `tests/integration/test_final_review_release_gate_batch_report.py`.
- [ ] T034 Add `tests/integration/test_final_review_release_gate_batch_scope_guard.py`.

## J. Report generation and final gate

- [ ] T035 Generate all Feature 064 batch artifacts.
- [ ] T036 Final verdict must be `final_review_release_gate_batch_passed` only when all release gates pass and blockers are empty.
- [ ] T037 Recommended next feature must be `Release tag creation or thesis/paper writing workflow` only on passing verdict.

## Validation Handoff and Remote Audit Packet

- [ ] T038 Print exact test output or CI result URL.
- [ ] T039 Print report proof fields.
- [ ] T040 Print `git status --short`.
- [ ] T041 Print `git diff --name-only main...HEAD`.
- [ ] T042 Print `git diff --stat main...HEAD`.
- [ ] T043 Print `git diff --cached --name-only`.
- [ ] T044 If auto-push is used, print commit SHA, branch name, pushed remote ref, final verdict, recommended next feature, and final `git status --short`.
