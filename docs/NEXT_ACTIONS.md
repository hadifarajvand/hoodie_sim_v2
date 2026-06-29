# Next Actions

## Immediate — Gate 4A (Simplified Pipeline Viability)

1. Commit C-001 fix: `git add src/environment/gym_adapter.py && git commit -m "fix: add missing compute_config argument to advance_shared_runtime call in _maybe_finalize_head"`
2. Run Gate 4A validation: `pytest tests/unit/test_slot_engine.py tests/unit/test_baseline_rebuild_sensitivity_audit.py -x --tb=short -q`
3. Gate 4A does NOT claim paper-faithful state/action reproduction

## Next — Gate 4B (Paper-Faithful 74D/22A Active Path)

1. Wire `PaperStateBuilder` (74-dim) into `replay.py:build_state_vector()`
2. Wire `paper_action_space.py` (22 actions) into `replay.py:ACTION_INDEX_TO_SEMANTICS` and `legal_action_mask_to_tuple()`
3. Update `ReplayTransition` validation for 74D state / 22-action mask
4. Update `trainer.py:_initial_history()` for 74-dim rows
5. Write tests: `test_paper_replay_transition_74d.py`, `test_paper_replay_transition_22a.py`, `test_trainer_initial_history_74d.py`
6. Gate 4B is required before claiming Phase 1 paper-faithful baseline readiness

## Blocked — Phase 2 / DCQ-MADRL

Phase 2 remains blocked until all Phase 1 gates (0–8) pass, including Gate 4B.
74D/22A is HOODIE paper baseline scope, NOT DCQ-MADRL scope.
