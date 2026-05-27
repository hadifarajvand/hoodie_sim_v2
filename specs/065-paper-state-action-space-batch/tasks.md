# Tasks: Feature 065 — Paper-Faithful State and Action Space Batch

## A. Prerequisite gates

- [ ] T001 Verify `main` contains Feature 064 merge evidence.
- [ ] T002 Verify Feature 064 report has `final_verdict = final_review_release_gate_batch_passed`.
- [ ] T003 Verify Feature 064 report has `remaining_blockers = []`.
- [ ] T004 Verify the current simplified state/action defects are detected before repair.

## B. Model and package

- [ ] T005 Create `src/analysis/paper_state_action_space_batch/config.py`.
- [ ] T006 Create `src/analysis/paper_state_action_space_batch/model.py`.
- [ ] T007 Create `src/analysis/paper_state_action_space_batch/report.py`.
- [ ] T008 Create `src/analysis/paper_state_action_space_batch/runner.py`.
- [ ] T009 Create `src/analysis/paper_state_action_space_batch/__init__.py` and `__main__.py`.

## C. Full paper state vector

- [ ] T010 Define structured paper state component schema.
- [ ] T011 Include task size, processing density/cycles, arrival slot, and deadline/timeout residual.
- [ ] T012 Include private queue waiting time and offloading queue waiting time.
- [ ] T013 Include public queue vector and load-history matrix.
- [ ] T014 Add deterministic tensor/flattening adapter and expose resulting `state_dim`.
- [ ] T015 Generate `paper-state-vector-contract.json`.

## D. Private/offloading waiting times

- [ ] T016 Compute private queue waiting time from actual private queue state.
- [ ] T017 Compute offloading queue waiting time from actual offloading queue state.
- [ ] T018 Record queue depth and zero-empty behavior.
- [ ] T019 Ensure values are not derived from global history length guesses.

## E. Public queue length vector

- [ ] T020 Define destination node order as Edge Agents plus Cloud.
- [ ] T021 Compute public queue lengths per exact destination.
- [ ] T022 Include Cloud public queue length.
- [ ] T023 Validate vector length is `N + 1`.

## F. Load-history matrix

- [ ] T024 Maintain node active queue counts per slot.
- [ ] T025 Expose matrix shape `[W, N+1]`.
- [ ] T026 Define deterministic left-padding/initialization behavior.
- [ ] T027 Generate `paper-load-history-contract.json`.

## G. LSTM forecast input

- [ ] T028 Build LSTM forecast tensor from node active queue load history.
- [ ] T029 Expose `forecast_input_shape = [lookback_w, edge_agent_count + 1]`.
- [ ] T030 Preserve compatibility path for `PaperHoodieDuelingNetwork`.
- [ ] T031 Generate `paper-lstm-forecast-input-contract.json`.

## H. Destination-specific action space

- [ ] T032 Define action registry with local/self, exact horizontal destinations, and Cloud.
- [ ] T033 Prevent generic horizontal action from silently selecting first neighbor in paper-faithful mode.
- [ ] T034 Include action index, family, source node, destination node, destination kind, and legality source.
- [ ] T035 Generate `paper-action-space-contract.json`.

## I. Legal destination mask

- [ ] T036 Permit local/self action for each Edge Agent.
- [ ] T037 Permit only topology-backed horizontal destination actions.
- [ ] T038 Permit Cloud vertical action.
- [ ] T039 Reject non-neighbor Edge Agent destinations.
- [ ] T040 Align mask one-to-one with action registry indices.
- [ ] T041 Generate `legal-destination-mask-contract.json`.

## J. Safety gates

- [ ] T042 Validate no training campaign rerun.
- [ ] T043 Validate no reward timing semantic change.
- [ ] T044 Validate no prior Feature 037–064 artifacts are rewritten.
- [ ] T045 Validate no paper reproduction or superiority claim is made.

## K. Tests

- [ ] T046 Add `tests/unit/test_paper_state_action_space_batch_schema.py`.
- [ ] T047 Add `tests/unit/test_paper_state_action_space_batch_metrics.py`.
- [ ] T048 Add `tests/unit/test_paper_state_action_space_batch_behavior_equivalence.py`.
- [ ] T049 Add `tests/integration/test_paper_state_action_space_batch.py`.
- [ ] T050 Add `tests/integration/test_paper_state_action_space_batch_report.py`.
- [ ] T051 Add `tests/integration/test_paper_state_action_space_batch_scope_guard.py`.

## L. Report generation and final gate

- [ ] T052 Generate all Feature 065 artifacts.
- [ ] T053 Final verdict must be `paper_state_action_space_batch_passed` only when all gates pass and blockers are empty.
- [ ] T054 Recommended next feature must be `Feature 066 — Distributed Multi-Agent HOODIE Training Batch` only on passing verdict.

## Validation Handoff and Remote Audit Packet

- [ ] T055 Print exact test output or CI result URL.
- [ ] T056 Print report proof fields.
- [ ] T057 Print `git status --short`.
- [ ] T058 Print `git diff --name-only main...HEAD`.
- [ ] T059 Print `git diff --stat main...HEAD`.
- [ ] T060 Print `git diff --cached --name-only`.
- [ ] T061 If auto-push is used, print commit SHA, branch name, pushed remote ref, final verdict, recommended next feature, and final `git status --short`.
