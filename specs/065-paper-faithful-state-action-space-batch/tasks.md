# Tasks: Feature 065 — Paper-Faithful State and Action Space Batch

## A. Prerequisite gates

- [X] T001 Verify Feature 064 is merged into `main`.
- [X] T002 Verify Feature 064 report has `final_verdict = final_review_release_gate_batch_passed`.
- [X] T003 Verify Feature 064 report has `remaining_blockers = []`.
- [X] T004 Verify recovered 20-node topology registry is present.

## B. Environment paper-contract modules

- [X] T005 Create `src/environment/paper_action_space.py`.
- [X] T006 Create `src/environment/paper_state.py`.
- [X] T007 Create `src/environment/paper_load_history.py`.
- [X] T008 Create `src/environment/paper_lstm_forecast.py`.

## C. Full paper state vector

- [X] T009 Implement paper state schema with task size, private/offloading waiting times, public queue vector, load history matrix, and destination metadata.
- [X] T010 Preserve old compact state as legacy-only if referenced.
- [X] T011 Add validation that paper state is not the old 3-dimensional compact state.

## D. Waiting-time fields

- [X] T012 Compute or explicitly approximate private queue waiting time.
- [X] T013 Compute or explicitly approximate offloading queue waiting time.
- [X] T014 Report waiting-time exactness and source.

## E. Public queue vector

- [X] T015 Implement public queue length vector.
- [X] T016 Preserve destination order.
- [X] T017 Validate the vector is not scalar-collapsed.

## F. Load history and LSTM forecast input

- [X] T018 Implement active queue count sampling per node.
- [X] T019 Implement `W × (N+1)` load-history matrix.
- [X] T020 Implement LSTM forecast input matrix derived from active queue counts.
- [X] T021 Validate shape, node order, and window size.

## G. Destination-specific action space

- [X] T022 Implement destination-specific action mapping.
- [X] T023 Implement local/self action.
- [X] T024 Implement exact Edge-Agent destination actions.
- [X] T025 Implement Cloud action.
- [X] T026 Document action count and whether a reserved invalid/noop action exists.

## H. Destination-specific legal masking

- [X] T027 Implement legal action mask of length `paper_action_count`.
- [X] T028 Mark self-horizontal destination illegal.
- [X] T029 Mark non-neighbor Edge Agents illegal.
- [X] T030 Mark topology neighbors legal.
- [X] T031 Mark Cloud legal unless disabled by config.
- [X] T032 Emit legal/illegal reasons.

## I. Analysis/report package

- [X] T033 Create `src/analysis/paper_faithful_state_action_space_batch/config.py`.
- [X] T034 Create `src/analysis/paper_faithful_state_action_space_batch/model.py`.
- [X] T035 Create `src/analysis/paper_faithful_state_action_space_batch/runner.py`.
- [X] T036 Create `src/analysis/paper_faithful_state_action_space_batch/report.py`.
- [X] T037 Create `__init__.py` and `__main__.py`.

## J. Required artifacts

- [X] T038 Generate `paper-state-contract.json`.
- [X] T039 Generate `paper-action-space-contract.json`.
- [X] T040 Generate `paper-legal-mask-contract.json`.
- [X] T041 Generate `paper-load-history-contract.json`.
- [X] T042 Generate `migration-readiness-for-feature-066.json`.
- [X] T043 Generate final JSON and Markdown reports.

## K. Tests

- [X] T044 Add `tests/unit/test_paper_faithful_state_action_space_batch_schema.py`.
- [X] T045 Add `tests/unit/test_paper_faithful_state_action_space_batch_metrics.py`.
- [X] T046 Add `tests/unit/test_paper_faithful_state_action_space_batch_behavior_equivalence.py`.
- [X] T047 Add `tests/unit/test_paper_state_vector.py`.
- [X] T048 Add `tests/unit/test_paper_action_space.py`.
- [X] T049 Add `tests/unit/test_paper_load_history.py`.
- [X] T050 Add `tests/integration/test_paper_faithful_state_action_space_batch.py`.
- [X] T051 Add `tests/integration/test_paper_faithful_state_action_space_batch_report.py`.
- [X] T052 Add `tests/integration/test_paper_faithful_state_action_space_batch_scope_guard.py`.

## L. Safety gates

- [X] T053 Verify no training rerun.
- [X] T054 Verify no evaluation campaign rerun.
- [X] T055 Verify no optimizer steps.
- [X] T056 Verify no prior Feature 037–064 artifacts are rewritten.
- [X] T057 Verify no dependency/policy/environment semantic drift outside approved files.
- [X] T058 Verify no paper reproduction or unsupported superiority claim.

## M. Final validation handoff

- [X] T059 Run all required tests.
- [X] T060 Run `python3 -m src.analysis.paper_faithful_state_action_space_batch`.
- [X] T061 Print report proof fields.
- [X] T062 Print `git status --short`.
- [X] T063 Print `git diff --name-only main...HEAD`.
- [X] T064 Print `git diff --stat main...HEAD`.
- [X] T065 Print `git diff --cached --name-only`.
- [X] T066 Auto-commit/push only if all guarded conditions pass.
