# Tasks: Feature 063 — Results Export, Reproducibility, and Final Documentation Batch

## A. Prerequisite gates

- [ ] T001 Verify `main` contains Feature 062 merge evidence.
- [ ] T002 Verify Feature 062 report has `final_verdict = multi_seed_campaign_ablation_batch_passed`.
- [ ] T003 Verify Feature 062 report has `remaining_blockers = []`.
- [ ] T004 Verify Feature 062 multi-seed, aggregation, and ablation artifacts exist.

## B. Model and package

- [ ] T005 Create `src/analysis/results_export_reproducibility_documentation_batch/config.py`.
- [ ] T006 Create `src/analysis/results_export_reproducibility_documentation_batch/model.py`.
- [ ] T007 Create `src/analysis/results_export_reproducibility_documentation_batch/report.py`.
- [ ] T008 Create `src/analysis/results_export_reproducibility_documentation_batch/runner.py`.
- [ ] T009 Create `src/analysis/results_export_reproducibility_documentation_batch/__init__.py` and `__main__.py`.

## C. Batch item 1 — final experiment integrity audit

- [ ] T010 Map every exported claim to a source artifact.
- [ ] T011 Mark unsupported claims as unsupported rather than silently claiming them.
- [ ] T012 Generate `final-experiment-integrity-audit.json`.

## D. Batch item 2 — paper/thesis results table export

- [ ] T013 Generate `results-table-export.csv`.
- [ ] T014 Generate `results-table-export.md`.
- [ ] T015 Ensure exported values are controlled experiment data, not paper reproduction claims.

## E. Batch item 3 — reproducibility package

- [ ] T016 Generate `reproducibility-package.md`.
- [ ] T017 Include exact commands, branch/tag assumptions, artifact list, seed set, trace-bank IDs, and known limitations.

## F. Batch item 4 — final mechanism documentation

- [ ] T018 Generate `final-mechanism-documentation.md`.
- [ ] T019 Document HOODIE-style faithful components, implemented simplifications, and non-claims.

## G. Batch item 5 — final artifact index and handoff report

- [ ] T020 Generate `final-artifact-index.json`.
- [ ] T021 Generate final batch JSON and Markdown reports.
- [ ] T022 Validate all exported artifacts exist and are internally consistent.

## H. Safety gates

- [ ] T023 Validate no dependency, policy, environment, or reward-timing drift.
- [ ] T024 Validate no prior Feature 037–062 artifacts are rewritten.
- [ ] T025 Validate no paper reproduction or unsupported superiority claim is made.
- [ ] T026 Validate no rerun of training campaigns or uncontrolled outputs occurs.

## I. Tests

- [ ] T027 Add `tests/unit/test_results_export_reproducibility_documentation_batch_schema.py`.
- [ ] T028 Add `tests/unit/test_results_export_reproducibility_documentation_batch_metrics.py`.
- [ ] T029 Add `tests/unit/test_results_export_reproducibility_documentation_batch_behavior_equivalence.py`.
- [ ] T030 Add `tests/integration/test_results_export_reproducibility_documentation_batch.py`.
- [ ] T031 Add `tests/integration/test_results_export_reproducibility_documentation_batch_report.py`.
- [ ] T032 Add `tests/integration/test_results_export_reproducibility_documentation_batch_scope_guard.py`.

## J. Report generation and final gate

- [ ] T033 Generate all Feature 063 batch artifacts.
- [ ] T034 Final verdict must be `results_export_reproducibility_documentation_batch_passed` only when all batch gates pass and blockers are empty.
- [ ] T035 Recommended next feature must be `Feature 064 — Final Review and Release Gate` only on passing verdict.

## Validation Handoff and Remote Audit Packet

- [ ] T036 Print exact test output or CI result URL.
- [ ] T037 Print report proof fields.
- [ ] T038 Print `git status --short`.
- [ ] T039 Print `git diff --name-only main...HEAD`.
- [ ] T040 Print `git diff --stat main...HEAD`.
- [ ] T041 Print `git diff --cached --name-only`.
- [ ] T042 If auto-push is used, print commit SHA, branch name, pushed remote ref, final verdict, recommended next feature, and final `git status --short`.
