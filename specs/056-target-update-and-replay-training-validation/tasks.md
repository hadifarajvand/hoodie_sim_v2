# Tasks: Feature 056 — Target Update and Replay Training Validation

## A. Prerequisite gates

- [X] T001 Verify `main` contains `055-paper-default-training-smoke-run-complete`.
- [X] T002 Verify branch is not `main` and is based on current `main`.
- [X] T003 Verify Feature 055 report is committed and has `final_verdict = paper_default_training_smoke_passed`.
- [X] T004 Verify Feature 055 report has `replay_inserted = true`, `optimizer_steps_executed = true`, and `remaining_blockers = []`.

## B. Model and schema

- [X] T005 Create `src/analysis/target_update_replay_training_validation/config.py`.
- [X] T006 Create `src/analysis/target_update_replay_training_validation/model.py` with the report dataclass and required fields.
- [X] T007 Create `src/analysis/target_update_replay_training_validation/report.py` for JSON and Markdown artifacts.
- [X] T008 Create `src/analysis/target_update_replay_training_validation/runner.py`.
- [X] T009 Create `src/analysis/target_update_replay_training_validation/__init__.py` and `__main__.py`.

## C. Replay validation

- [X] T010 Validate replay insertion from the Feature 055 smoke output.
- [X] T011 Validate replay sampling contract using controlled replay data.
- [X] T012 Validate replay sample fields include state, action, legal mask, next state, reward, terminal, reward availability, and pending-at-horizon information.
- [X] T013 Fail if replay sampling fabricates terminal rewards or ignores delayed-reward semantics.

## D. Optimizer and target-update validation

- [X] T014 Validate optimizer-step counter increments monotonically.
- [X] T015 Validate approved target-update unit is `optimizer_step`.
- [X] T016 Validate approved target-update frequency is `2000`.
- [X] T017 Validate no target sync occurs before threshold.
- [X] T018 Validate target sync occurs at the threshold.
- [X] T019 Validate target sync count and optimizer-step count are reported consistently.

## E. Checkpoint metadata and safety

- [X] T020 Validate checkpoint metadata contains target-update unit, optimizer-step count, replay size, config hash, trace bank IDs, and seed bundle.
- [X] T021 Validate no full campaign, baseline comparison, paper reproduction claim, policy drift, dependency drift, environment semantic change, or reward timing change.
- [X] T022 Validate no Feature 037–055 artifacts are rewritten.

## F. Tests

- [X] T023 Add `tests/unit/test_target_update_replay_validation_schema.py`.
- [X] T024 Add `tests/unit/test_target_update_replay_validation_metrics.py`.
- [X] T025 Add `tests/unit/test_target_update_replay_validation_behavior_equivalence.py`.
- [X] T026 Add `tests/integration/test_target_update_replay_validation.py`.
- [X] T027 Add `tests/integration/test_target_update_replay_validation_report.py`.
- [X] T028 Add `tests/integration/test_target_update_replay_validation_scope_guard.py`.

## G. Report generation and final gate

- [X] T029 Generate JSON and Markdown reports under `artifacts/analysis/target-update-replay-training-validation/`.
- [X] T030 Final verdict must be `target_update_replay_validation_passed` only when all validation gates pass and blockers are empty.
- [X] T031 Recommended next feature must be `Feature 057 — Paper-Default Pilot Training Run` only on passing verdict.
- [X] T032 Print dirty-path classification and use approved Feature 056 paths only.
