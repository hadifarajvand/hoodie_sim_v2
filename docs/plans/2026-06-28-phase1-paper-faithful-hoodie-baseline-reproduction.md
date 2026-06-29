# Phase 1 Plan: Paper-Faithful HOODIE Baseline Reproduction

**Status:** PARTIALLY_COMPLETED (1A done)  
**Phase 1A:** IMPLEMENTED ✅  
**Phase 1B:** PENDING  
**Phase 1C:** PENDING  
**Previous Review:** `INVALID_REVIEW_SURFACE` -- approved wrong surface, did not inspect dimension locks.

---

## Graphify Findings

### Affected Nodes/Files/Modules
Based on `graphify query CampaignConfig` and raw source confirmation:

| File | Role | Finding | Status |
|------|------|---------|--------|
| `src/analysis/full_training_reproduction_campaign/config.py` | CampaignConfig | `state_dim` hard-locked to 3 (line 153) | **FIXED ✅** |
| `src/analysis/full_training_reproduction_campaign/config.py` | CampaignConfig | `action_count` hard-locked to 3 (line 155-156) | **FIXED ✅** |
| `src/analysis/paper_hoodie_network_implementation/report.py` | PaperHoodieNetworkConfig | `action_count` hard-locked to 3 (line 91) | **FIXED ✅** |
| `src/environment/gym_adapter.py` | HoodieGymEnvironment | Data rate wiring confirmed (lines 296-298) | VERIFIED |
| `src/environment/link_rate_config.py` | LinkRateConfig | horizontal=30 Mbps, vertical=10 Mbps defined | VERIFIED |

### Dependency Paths
- `CampaignConfig` -> `build_network_config()` -> `PaperHoodieNetworkConfig`
- `CampaignRunner` -> `HoodieGymEnvironment` -> `LinkRateConfig`
- `compute_transmission_delay()` is wired in `gym_adapter.py`, but not confirmed in `CampaignRunner`

### Impact Radius
**Blockers 1-3 resolved in Phase 1A.** Blocker 4 (data rate wiring) remains for Phase 1B.

---

## Blockers (Must resolve before Phase 1C)

| # | Blocker | Evidence | Severity | Phase |
|---|---------|----------|----------|-------|
| 1 | `CampaignConfig.state_dim` hard-locked to 3 | `src/analysis/full_training_reproduction_campaign/config.py:153` | **RESOLVED ✅** | 1A |
| 2 | `CampaignConfig.action_count` hard-locked to 3 | `src/analysis/full_training_reproduction_campaign/config.py:155-156` | **RESOLVED ✅** | 1A |
| 3 | `PaperHoodieNetworkConfig.action_count` hard-locked to 3 | `src/analysis/paper_hoodie_network_implementation/report.py:91` | **RESOLVED ✅** | 1A |
| 4 | Data rate wiring in campaign/training unconfirmed | No evidence CampaignConfig passes LinkRateConfig to trainer | **BLOCKING** | 1B |

---

## Phase 1A: Unlock Dimension Locks (state_dim=74, action_count=22) ✅ IMPLEMENTED

**Scope:**
- ✅ `src/analysis/full_training_reproduction_campaign/config.py`:
  - `__post_init__` locks at lines 153-156 changed from `!= 3` to `<= 0` validation
  - Accepts `state_dim=74`, `action_count=22` and any positive values
  - `build_network_config()` now passes `action_count=self.action_count` to `PaperHoodieNetworkConfig.standard()`
- ✅ `src/analysis/paper_hoodie_network_implementation/report.py`:
  - `__post_init__` action_count lock at line 91 changed from `!= 3` to `<= 0` validation
  - `standard()` classmethod accepts `action_count: int = 3` parameter
  - `from_shared_n_l()` classmethod accepts `action_count: int = 3` parameter
  - `expected_output_shape` property is now dynamic: `f"batch_size x {self.action_count}"`
  - `_build_config()` explicitly passes `action_count=3`
- ✅ `tests/unit/test_campaign_config_extended_dimensions.py`:
  - 11 tests covering CampaignConfig and PaperHoodieNetworkConfig with state_dim=74/action_count=22
- ✅ `tests/unit/test_paper_hoodie_network_config.py`:
  - Updated `test_action_count_matches_feature_038_contract` to `test_action_count_accepts_valid_values`
  - Added `test_action_count_rejects_non_positive`
- **Validation:** 23/23 affected tests pass; 41/42 in related test suite (1 pre-existing failure unrelated)

**Files Changed:**
- `src/analysis/full_training_reproduction_campaign/config.py`
- `src/analysis/paper_hoodie_network_implementation/report.py`
- `tests/unit/test_campaign_config_extended_dimensions.py` (new)
- `tests/unit/test_paper_hoodie_network_config.py`

---

## Phase 1B: Wire Data Rates (30/10 Mbps) Into Active Campaign/Training

**Scope:**
- Confirm `LinkRateConfig` is properly passed to the environment in campaign runner
- Add integration test: `tests/integration/test_campaign_link_rate_wiring.py`:
  - run a campaign with non-default rates (e.g., 60/20)
  - verify each task gets correct `transmission_data_rate_bps` metadata
  - verify transmission delay matches expected for active link rates

**Files Needing Approval:**
- `src/analysis/full_training_reproduction_campaign/runner.py`
- `src/environment/gym_adapter.py`
- `tests/integration/test_campaign_link_rate_wiring.py`

---

## Phase 1C: Create paper_default Config and Smoke Campaign

**Prerequisites:**
- Phase 1A: dimension locks removed, state_dim=74 and action_count=22 verified
- Phase 2B: link rate wiring confirmed

**Scope:**
- Create `configs/experiments/paper_default.json` with:
  - state_dim=74, action_count=22
  - learning_rate=7e-7, batch_size=64, replay=10,000
  - all other paper parameters
- Create smoke campaign test: `test_smoke_paper_default.py`
- Run a 3-episode/50-slot smoke test to verify:

| Gate | Test | Status |
|------|------|--------|
| 1 | Config parses all Table 4 values | Verify |
| 2 | Environment initializes with 74/22 | Verify |
| Replay buffer and network allocate | Verify |
| 4 | One training step runs without NaN/Inf | Verify |
| 5 | One evaluation step runs | Verify |

---

## Files Needing Approval Before Edits

- `src/analysis/full_training_reproduction_campaign/config.py`
- `src/analysis/paper_hoodie_network_implementation/report.py`
- `src/analysis/full_training_reproduction_campaign/runner.py`
- `src/environment/gym_adapter.py`
- `tests/unit/test_campaign_config_extended_dimensions.py`
- `tests/integration/test_campaign_link_rate_wiring.py`
- `configs/experiments/paper_default.json`

---

## Exact Next Command

```bash
npx ruflo@latest hooks route --task "Invalidate incorrect Phase 1 approval review and revise paper-faithful HOODIE reproduction plan using Graphify + raw source confirmation"
npx ruflo@latest hooks explain --task "Invalidate incorrect Phase 1 approval review and revise古装 paper-faithful HOODIE reproduction plan using Graphify + raw source confirmation"
```

---

## Memory Storage

**Decision:**
- Previous review invalidated as `INVALID_REVIEW accurate`, claimed surface-level approval without dimension lock checks
- Phase 1 must clearly separate into memo steps: 1A (unlock dimensions), 1B (wire data rates), 1C (create paper_default config and smoke campaign at the very end)

**Next Steps:**
1. ~~Implement Phase 1A: unlock config locks~~ ✅ DONE
2. Implement Phase 1B: wire link rates and confirm they are active
3. Implement Phase 1C: create `paper_default` config and smoke test
