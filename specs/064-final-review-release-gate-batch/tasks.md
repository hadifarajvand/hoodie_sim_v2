# Tasks: Feature 064 — Final Review and Release Gate Batch

## A. Prerequisite gates

- [X] T001 Verify `main` contains Feature 063 merge evidence.
- [X] T002 Verify Feature 063 report has `final_verdict = results_export_reproducibility_documentation_batch_passed`.
- [X] T003 Verify Feature 063 report has `remaining_blockers = []`.
- [X] T004 Verify all Feature 063 final export artifacts exist.

## B. Model and package

- [X] T005 Create `src/analysis/final_review_release_gate_batch/config.py`.
- [X] T006 Create `src/analysis/final_review_release_gate_batch/model.py`.
- [X] T007 Create `src/analysis/final_review_release_gate_batch/report.py`.
- [X] T008 Create `src/analysis/final_review_release_gate_batch/runner.py`.
- [X] T009 Create `src/analysis/final_review_release_gate_batch/__init__.py` and `__main__.py`.

## C. Batch item 1 — final repository state audit

- [X] T010 Generate `final-repository-state-audit.json`.
- [X] T011 Verify release evidence is source-backed and committed.
- [X] T012 Verify no final gate logic requires uncommitted local state.

## D. Batch item 2 — final artifact completeness gate

- [X] T013 Generate `final-artifact-completeness-gate.json`.
- [X] T014 Verify all required Feature 063 final exports exist.
- [X] T015 Verify all referenced source artifacts exist.

## E. Batch item 3 — final claim boundary review

- [X] T016 Generate `final-claim-boundary-review.json`.
- [X] T017 Verify no paper reproduction claim.
- [X] T018 Verify no unsupported superiority claim.
- [X] T019 Verify supported claims map to committed artifacts.

## F. Batch item 4 — release tag readiness package

- [X] T020 Generate `release-tag-readiness-package.md`.
- [X] T021 Recommend release tag name but do not create the tag.
- [X] T022 Include exact release prerequisites and post-merge tag command.

## G. Batch item 5 — final handoff and next-work recommendation

- [X] T023 Generate `final-handoff-and-next-work.md`.
- [X] T024 Summarize supported results, unsupported claims, known limitations, and recommended thesis/paper workflow.

## H. Safety gates

- [X] T025 Validate no training rerun or new experiment output.
- [X] T026 Validate no dependency, policy, environment, or reward-timing drift.
- [X] T027 Validate no prior Feature 037–063 artifacts are rewritten.
- [X] T028 Validate no release tag is created inside this feature.

## I. Tests

- [X] T029 Add `tests/unit/test_final_review_release_gate_batch_schema.py`.
- [X] T030 Add `tests/unit/test_final_review_release_gate_batch_metrics.py`.
- [X] T031 Add `tests/unit/test_final_review_release_gate_batch_behavior_equivalence.py`.
- [X] T032 Add `tests/integration/test_final_review_release_gate_batch.py`.
- [X] T033 Add `tests/integration/test_final_review_release_gate_batch_report.py`.
- [X] T034 Add `tests/integration/test_final_review_release_gate_batch_scope_guard.py`.

## J. Report generation and final gate

- [X] T035 Generate all Feature 064 batch artifacts.
- [X] T036 Final verdict must be `final_review_release_gate_batch_passed` only when all release gates pass and blockers are empty.
- [X] T037 Recommended next feature must be `Release tag creation or thesis/paper writing workflow` only on passing verdict.

## Validation Handoff and Remote Audit Packet

- [X] T038 Print exact test output or CI result URL.
- [X] T039 Print report proof fields.
- [X] T040 Print `git status --short`.
- [X] T041 Print `git diff --name-only main...HEAD`.
- [X] T042 Print `git diff --stat main...HEAD`.
- [X] T043 Print `git diff --cached --name-only`.
- [X] T044 If auto-push is used, print commit SHA, branch name, pushed remote ref, final verdict, recommended next feature, and final `git status --short`.
