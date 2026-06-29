# Gate 4C — Paper-Faithful Network Output Dimension Unlock

**Date:** 2026-06-28  
**Classification:** small-feature  
**Route:** OpenCode direct (no swarm needed, focused implementation)

## Files Changed

| File | Change | Description |
|------|--------|-------------|
| `src/analysis/paper_hoodie_network_implementation/network.py` | Modified | Relaxed `action_count` guard from `!= 3` to `not in (3, 22)` to allow paper-faithful 22-action networks |
| `src/analysis/full_training_reproduction_campaign/trainer.py` | Modified | Updated `CampaignPolicy` to accept `action_count` parameter, use it for mask creation, and select appropriate semantics mapping (legacy 3-action vs paper 22-action) |
| `tests/unit/test_gate4c_paper_network_dimension_unlock.py` | Created | 11 tests covering: network accepts 22 actions, output shape `[..., 22]`, still accepts 3 actions, rejects invalid counts, DDQNTrainer instantiates with 74/22 config, policy mask shape matches Q-values, semantic mapping correct |

## Implementation Summary

1. **network.py**: Changed the validation in `PaperHoodieDuelingNetwork.__init__` from `if config.action_count != 3:` to `if config.action_count not in (3, 22):` with an appropriate error message. The network architecture already supported variable action counts via `self.advantage_head = nn.Linear(body_input_dim, self.action_count)`.

2. **trainer.py**: 
   - Modified `CampaignPolicy.__init__` to accept an `action_count` parameter (default 3 for backward compatibility)
   - Updated `choose_action_index` to pass `action_count` to `legal_action_mask_to_tuple`
   - Updated `choose_action` to use `ACTION_INDEX_TO_SEMANTICS_PAPER` when `action_count != 3` (i.e., for 22-action paper-faithful mode)
   - Updated `DDQNTrainer.__init__` to pass `self.config.action_count` when constructing the `CampaignPolicy`

3. **Test Coverage**: Created comprehensive test suite verifying:
   - Network instantiation and output shape for both 3 and 22 actions
   - Proper rejection of invalid action counts (0, 1, 2, 4, 5, etc.)
   - DDQNTrainer can now instantiate with `CampaignConfig(state_dim=74, action_count=22)` without mocking
   - `CampaignPolicy` mask shape matches Q-values output shape
   - Correct semantic mapping: action 0 → "local", actions 1-20 → "horizontal_X", action 21 → "cloud"
   - Legacy 3-action behavior preserved for backward compatibility

## Validation Results

- **All Gate 4B tests pass**: 17/17 replay paper-dimension tests ✅
- **Gate 4A baseline preserved**: 9/9 slot engine and sensitivity audit tests ✅
- **Paper helper tests pass**: 4/4 state/vector and action space tests ✅
- **Extended config tests pass**: 11/11 campaign config and network config tests ✅
- **Integration tests pass**: 11/11 link rate wiring tests ✅
- **New Gate 4C tests pass**: 11/11 tests for 22-action network unlock ✅
- **Total**: 63 tests passed, 0 failed

## Remaining Blocker

None — Gate 4C is now complete. The paper-faithful 74D/22A path is fully functional from configuration through network inference to policy action selection.

## Next Command

```
pytest tests/unit/test_gate4c_paper_network_dimension_unlock.py -v
```