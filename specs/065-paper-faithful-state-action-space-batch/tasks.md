# Tasks: Feature 065 — Paper-Faithful State and Action Space Batch

## A. Prerequisite gates

- [ ] T001 Verify Feature 064 is merged into `main`.
- [ ] T002 Verify Feature 064 report has `final_verdict = final_review_release_gate_batch_passed`.
- [ ] T003 Verify Feature 064 report has `remaining_blockers = []`.
- [ ] T004 Verify recovered 20-node topology registry is present.

## B. Environment paper-contract modules

- [ ] T005 Create `src/environment/paper_action_space.py`.
- [ ] T006 Create `src/environment/paper_state.py`.
- [ ] T007 Create `src/environment/paper_load_history.py`.
- [ ] T008 Create `src/environment/paper_lstm_forecast.py`.

## C. Full paper state vector

- [ ] T009 Implement paper state schema with task size, private/offloading waiting times, public queue vector, load history matrix, and destination metadata.
- [ ] T010 Preserve old compact state as legacy-only if referenced.
- [ ] T011 Add validation that paper state is not the old 3-dimensional compact state.

## D. Waiting-time fields

- [ ] T012 Compute or explicitly approximate private queue waiting time.
- [ ] T013 Compute or explicitly approximate offloading queue waiting time.
- [ ] T014 Report waiting-time exactness and source.

## E. Public queue vector

- [ ] T015 Implement public queue length vector.
- [ ] T016 Preserve destination order.
- [ ] T017 Validate the vector is not scalar-collapsed.

## F. Load history and LSTM forecast input

- [ ] T018 Implement active queue count sampling per node.
- [ ] T019 Implement `W × (N+1)` load-history matrix.
- [ ] T020 Implement LSTM forecast input matrix derived from active queue counts.
- [ ] T021 Validate shape, node order, and window size.

## G. Destination-specific action space

- [ ] T022 Implement destination-specific action mapping.
- [ ] T023 Implement local/self action.
- [ ] T024 Implement exact Edge-Agent destination actions.
- [ ] T025 Implement Cloud action.
- [ ] T026 Document action count and whether a reserved invalid/noop action exists.

## H. Destination-specific legal masking

- [ ] T027 Implement legal action mask of length `paper_action_count`.
- [ ] T028 Mark self-horizontal destination illegal.
- [ ] T029 Mark non-neighbor Edge Agents illegal.
- [ ] T030 Mark topology neighbors legal.
- [ ] T031 Mark Cloud legal unless disabled by config.
- [ ] T032 Emit legal/illegal reasons.

## I. Analysis/report package

- [ ] T033 Create `src/analysis/paper_faithful_state_action_space_batch/config.py`.
- [ ] T034 Create `src/analysis/paper_faithful_state_action_space_batch/model.py`.
- [ ] T035 Create `src/analysis/paper_faithful_state_action_space_batch/runner.py`.
- [ ] T036 Create `src/analysis/paper_faithful_state_action_space_batch/report.py`.
- [ ] T037 Create `__init__.py` and `__main__.py`.

## J. Required artifacts

- [ ] T038 Generate `paper-state-contract.json`.
- [ ] T039 Generate `paper-action-space-contract.json`.
- [ ] T040 Generate `paper-legal-mask-contract.json`.
- [ ] T041 Generate `paper-load-history-contract.json`.
- [ ] T042 Generate `migration-readiness-for-feature-066.json`.
- [ ] T043 Generate final JSON and Markdown reports.

## K. Tests

- [ ] T044 Add `tests/unit/test_paper_faithful_state_action_space_batch_schema.py`.
- [ ] T045 Add `tests/unit/test_paper_faithful_state_action_space_batch_metrics.py`.
- [ ] T046 Add `tests/unit/test_paper_faithful_state_action_space_batch_behavior_equivalence.py`.
- [ ] T047 Add `tests/unit/test_paper_state_vector.py`.
- [ ] T048 Add `tests/unit/test_paper_action_space.py`.
- [ ] T049 Add `tests/unit/test_paper_load_history.py`.
- [ ] T050 Add `tests/integration/test_paper_faithful_state_action_space_batch.py`.
- [ ] T051 Add `tests/integration/test_paper_faithful_state_action_space_batch_report.py`.
- [ ] T052 Add `tests/integration/test_paper_faithful_state_action_space_batch_scope_guard.py`.

## L. Safety gates

- [ ] T053 Verify no training rerun.
- [ ] T054 Verify no evaluation campaign rerun.
- [ ] T055 Verify no optimizer steps.
- [ ] T056 Verify no prior Feature 037–064 artifacts are rewritten.
- [ ] T057 Verify no dependency/policy/environment semantic drift outside approved files.
- [ ] T058 Verify no paper reproduction or unsupported superiority claim.

## M. Final validation handoff

- [ ] T059 Run all required tests.
- [ ] T060 Run `python3 -m src.analysis.paper_faithful_state_action_space_batch`.
- [ ] T061 Print report proof fields.
- [ ] T062 Print `git status --short`.
- [ ] T063 Print `git diff --name-only main...HEAD`.
- [ ] T064 Print `git diff --stat main...HEAD`.
- [ ] T065 Print `git diff --cached --name-only`.
- [ ] T066 Auto-commit/push only if all guarded conditions pass.
