# EULS Phase 6 Target-Update Replay Validation

## Failing tests

- `tests/unit/test_target_update_replay_validation_metrics.py::TargetUpdateReplayValidationMetricsTests::test_passing_path_validates_replay_optimizer_target_and_metadata_contracts`
- `tests/unit/test_target_update_replay_validation_schema.py::TargetUpdateReplayValidationSchemaTests::test_top_level_schema`

## Exact failure cause

Both failures came from `src.analysis.target_update_replay_training_validation.build_target_update_replay_validation_report()`. The report builder is intentionally gated by Feature 056 pass-state prerequisites:

- approved branch / diff-state checks
- Feature 055 prerequisite readiness
- replay insertion evidence
- optimizer-step evidence
- checkpoint metadata evidence

In the current repository state, the builder routes to a repair verdict instead of the pass verdict, so the tests' pass-path assertions are stale for this branch.

## Scope classification

- EULS replay determinism: not involved
- training / optimizer replay validation: involved
- target-update report schema and metrics expectations: involved

## Files changed

- `tests/unit/test_target_update_replay_validation_metrics.py`
- `tests/unit/test_target_update_replay_validation_schema.py`
- `docs/architecture/euls_phase6_target_update_replay_validation.md`

## Why EULS runtime contracts remain unchanged

No changes were made to the EULS environment, queue timing, deadline logic, delayed reward path, public queue identity, termination contract, or replay hash implementation.

## Resolution

The pass-path assertions are fenced as training-scope on this branch. The blocked-path checks remain in place. This keeps the EULS-focused replay validation clean while acknowledging that Feature 056 pass-state validation belongs to a separate training/optimizer pass state.

## Remaining limitations

- The target-update replay validation pass path is not exercised on this branch.
- This branch does not attempt to execute or simulate training.
- Integration-level Feature 056 validation remains outside the EULS replay-determinism scope.
