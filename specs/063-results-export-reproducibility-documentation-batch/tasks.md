# Tasks: Feature 063 — Results Export, Reproducibility, and Final Documentation Batch

## A. Prerequisite gates

- [X] T001 Verify `main` contains Feature 062 merge evidence.
- [X] T002 Verify Feature 062 report has `final_verdict = multi_seed_campaign_ablation_batch_passed`.
- [X] T003 Verify Feature 062 report has `remaining_blockers = []`.
- [X] T004 Verify Feature 062 multi-seed, aggregation, and ablation artifacts exist.

## B. Model and package

- [X] T005 Create `src/analysis/results_export_reproducibility_documentation_batch/config.py`.
- [X] T006 Create `src/analysis/results_export_reproducibility_documentation_batch/model.py`.
- [X] T007 Create `src/analysis/results_export_reproducibility_documentation_batch/report.py`.
- [X] T008 Create `src/analysis/results_export_reproducibility_documentation_batch/runner.py`.
- [X] T009 Create `src/analysis/results_export_reproducibility_documentation_batch/__init__.py` and `__main__.py`.

## C. Batch item 1 — final experiment integrity audit

- [X] T010 Map every exported claim to a source artifact.
- [X] T011 Mark unsupported claims as unsupported rather than silently claiming them.
- [X] T012 Generate `final-experiment-integrity-audit.json`.

## D. Batch item 2 — paper/thesis results table export

- [X] T013 Generate `results-table-export.csv`.
- [X] T014 Generate `results-table-export.md`.
- [X] T015 Ensure exported values are controlled experiment data, not paper reproduction claims.

## E. Batch item 3 — reproducibility package

- [X] T016 Generate `reproducibility-package.md`.
- [X] T017 Include exact commands, branch/tag assumptions, artifact list, seed set, trace-bank IDs, and known limitations.

## F. Batch item 4 — final mechanism documentation

- [X] T018 Generate `final-mechanism-documentation.md`.
- [X] T019 Document HOODIE-style faithful components, implemented simplifications, and non-claims.

## G. Batch item 5 — final artifact index and handoff report

- [X] T020 Generate `final-artifact-index.json`.
- [X] T021 Generate final batch JSON and Markdown reports.
- [X] T022 Validate all exported artifacts exist and are internally consistent.

## H. Safety gates

- [X] T023 Validate no dependency, policy, environment, or reward-timing drift.
- [X] T024 Validate no prior Feature 037–062 artifacts are rewritten.
- [X] T025 Validate no paper reproduction or unsupported superiority claim is made.
- [X] T026 Validate no rerun of training campaigns or uncontrolled outputs occurs.

## I. Tests

- [X] T027 Add `tests/unit/test_results_export_reproducibility_documentation_batch_schema.py`.
- [X] T028 Add `tests/unit/test_results_export_reproducibility_documentation_batch_metrics.py`.
- [X] T029 Add `tests/unit/test_results_export_reproducibility_documentation_batch_behavior_equivalence.py`.
- [X] T030 Add `tests/integration/test_results_export_reproducibility_documentation_batch.py`.
- [X] T031 Add `tests/integration/test_results_export_reproducibility_documentation_batch_report.py`.
- [X] T032 Add `tests/integration/test_results_export_reproducibility_documentation_batch_scope_guard.py`.

## J. Report generation and final gate

- [X] T033 Generate all Feature 063 batch artifacts.
- [X] T034 Final verdict must be `results_export_reproducibility_documentation_batch_passed` only when all batch gates pass and blockers are empty.
- [X] T035 Recommended next feature must be `Feature 064 — Final Review and Release Gate` only on passing verdict.

## Validation Handoff and Remote Audit Packet

- [X] T036 Print exact test output or CI result URL.
- [X] T037 Print report proof fields.
- [X] T038 Print `git status --short`.
- [X] T039 Print `git diff --name-only main...HEAD`.
- [X] T040 Print `git diff --stat main...HEAD`.
- [X] T041 Print `git diff --cached --name-only`.
- [X] T042 If auto-push is used, print commit SHA, branch name, pushed remote ref, final verdict, recommended next feature, and final `git status --short`.
