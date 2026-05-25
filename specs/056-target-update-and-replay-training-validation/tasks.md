# Tasks: Feature 056 — Target Update and Replay Training Validation

## A. Prerequisite gates

- [ ] T001 Verify `main` contains `055-paper-default-training-smoke-run-complete`.
- [ ] T002 Verify branch is not `main` and is based on current `main`.
- [ ] T003 Verify Feature 055 report is committed and has `final_verdict = paper_default_training_smoke_passed`.
- [ ] T004 Verify Feature 055 report has `replay_inserted = true`, `optimizer_steps_executed = true`, and `remaining_blockers = []`.

## B. Model and schema

- [ ] T005 Create `src/analysis/target_update_replay_training_validation/config.py`.
- [ ] T006 Create `src/analysis/target_update_replay_training_validation/model.py` with the report dataclass and required fields.
- [ ] T007 Create `src/analysis/target_update_replay_training_validation/report.py` for JSON and Markdown artifacts.
- [ ] T008 Create `src/analysis/target_update_replay_training_validation/runner.py`.
- [ ] T009 Create `src/analysis/target_update_replay_training_validation/__init__.py` and `__main__.py`.

## C. Replay validation

- [ ] T010 Validate replay insertion from the Feature 055 smoke output.
- [ ] T011 Validate replay sampling contract using controlled replay data.
- [ ] T012 Validate replay sample fields include state, action, legal mask, next state, reward, terminal, reward availability, and pending-at-horizon information.
- [ ] T013 Fail if replay sampling fabricates terminal rewards or ignores delayed-reward semantics.

## D. Optimizer and target-update validation

- [ ] T014 Validate optimizer-step counter increments monotonically.
- [ ] T015 Validate approved target-update unit is `optimizer_step`.
- [ ] T016 Validate approved target-update frequency is `2000`.
- [ ] T017 Validate no target sync occurs before threshold.
- [ ] T018 Validate target sync occurs at the threshold.
- [ ] T019 Validate target sync count and optimizer-step count are reported consistently.

## E. Checkpoint metadata and safety

- [ ] T020 Validate checkpoint metadata contains target-update unit, optimizer-step count, replay size, config hash, trace bank IDs, and seed bundle.
- [ ] T021 Validate no full campaign, baseline comparison, paper reproduction claim, policy drift, dependency drift, environment semantic change, or reward timing change.
- [ ] T022 Validate no Feature 037–055 artifacts are rewritten.

## F. Tests

- [ ] T023 Add `tests/unit/test_target_update_replay_validation_schema.py`.
- [ ] T024 Add `tests/unit/test_target_update_replay_validation_metrics.py`.
- [ ] T025 Add `tests/unit/test_target_update_replay_validation_behavior_equivalence.py`.
- [ ] T026 Add `tests/integration/test_target_update_replay_validation.py`.
- [ ] T027 Add `tests/integration/test_target_update_replay_validation_report.py`.
- [ ] T028 Add `tests/integration/test_target_update_replay_validation_scope_guard.py`.

## G. Report generation and final gate

- [ ] T029 Generate JSON and Markdown reports under `artifacts/analysis/target-update-replay-training-validation/`.
- [ ] T030 Final verdict must be `target_update_replay_validation_passed` only when all validation gates pass and blockers are empty.
- [ ] T031 Recommended next feature must be `Feature 057 — Paper-Default Pilot Training Run` only on passing verdict.
- [ ] T032 Print dirty-path classification and use approved Feature 056 paths only.
