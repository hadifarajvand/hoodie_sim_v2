# Gate 4B — Paper-Faithful 74D State / 22A Action Path

**Date:** 2026-06-28
**Classification:** small-feature
**Route:** OpenCode direct (no swarm needed, single-module focused work)

## Files Changed

| File | Change | Description |
|---|---|---|
| `src/analysis/full_training_reproduction_campaign/replay.py` | Modified | Added PAPER_STATE_DIM=74, PAPER_ACTION_COUNT=22, paper action mapping (local/edge/cloud), dimension-agnostic zero_state_row/build_state_window, ReplayTransition with state_dim/action_count fields and per-row dimension validation |
| `src/analysis/full_training_reproduction_campaign/trainer.py` | Modified | _initial_history uses config.state_dim; _state_tensor passes state_dim to build_state_window; ReplayTransition creation passes state_dim/action_count; build_state_vector calls condition on state_dim==3 |
| `tests/unit/test_full_training_reproduction_campaign_replay_paper_dimensions.py` | Created | 17 tests covering: 74D zero state row, 22-action mask, ReplayTransition acceptance/rejection, DDQNTrainer initial history dimensions, paper action index semantics |

## Implementation Summary

1. **replay.py**: Made replay infrastructure dimension-agnostic while preserving legacy 3D/3A defaults
   - Added `PAPER_STATE_DIM=74`, `PAPER_ACTION_COUNT=22`, paper action index mapping (0=local, 1-20=horizontal_edge, 21=cloud)
   - `zero_state_row(state_dim=...)` accepts configurable dimension
   - `build_state_window` auto-infers row dimension from history
   - `legal_action_mask_to_tuple(action_count=...)` supports both 3-key dict and paper mask list
   - `ReplayTransition` gains `state_dim` and `action_count` fields with validation:
     - State rows must match state_dim
     - Next_state rows must match state_dim
     - Action must be in `[0, action_count)`
     - Mask must have action_count entries

2. **trainer.py**: Wire config dimensions through training pipeline
   - `_initial_history` uses `config.state_dim` for paper-faithful zero rows
   - `_state_tensor` passes `state_dim` to `build_state_window`
   - Transition creation passes `state_dim`/`action_count` from config
   - `build_state_vector` legacy path gated on `state_dim==3`

3. **Gate 4A preserved**: All legacy 3D/3A behavior unchanged (defaults unchanged, existing tests pass)

## Validation Results

- **61 tests pass total across all Gate 4B and legacy test suites**
- Gate 4A baseline: 9 passed
- Paper state/action helpers: 4 passed
- Extended campaign config dimensions: 11 passed
- **New replay paper dimension tests: 17 passed** (covers all required acceptance criteria)
- Legacy replay contract: 3 passed
- Legacy campaign config: 6 passed
- Integration link rate wiring: 11 passed

## Remaining Blocker

`PaperHoodieDuelingNetwork.__init__` (Feature 039) enforces `action_count == 3`. This prevents DDQNTrainer instantiation with `state_dim=74, action_count=22` without mocking. Network must be updated separately to support 22-action output.

## Next Command

`pytest tests/unit/test_full_training_reproduction_campaign_replay_paper_dimensions.py -v`
