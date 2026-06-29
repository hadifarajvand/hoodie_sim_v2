# Phase 1 Master Plan: Paper-Faithful HOODIE Baseline Reproduction

**Status:** IN PROGRESS (Phase 1A ✅, Phase 1B ✅, Phase 1C–1G pending)
**Created:** 2026-06-29
**Last audited:** 2026-06-29

---

## Current Verified State

### Confirmed Locally
- Branch: `main`, HEAD: `aa9f11e` (includes both Phase 1A commit `d0fa548` and Phase 1B commit `aa9f11e`)
- Working tree: clean (no uncommitted changes)
- All Phase 1A+1B source files are committed to local `main`
- Tests: 37/37 pass in direct affected suites; 1 pre-existing failure in `test_paper_faithful_state_action_space_batch_schema.py`

### GitHub Sync Status
- **NOT VERIFIED** — Local changes may not yet be pushed to origin. The `qwdwqd` commit message and no dirty tree suggests the Phase 1B changes and subsequent commit were applied locally but push status is unconfirmed.
- **Action required:** Verify `git log origin/main..HEAD` before claiming GitHub parity.

### Phase 1A Completed
- `CampaignConfig.state_dim` and `action_count` hard locks removed; positive-value validation
- `CampaignConfig.build_network_config()` passes `action_count`
- `PaperHoodieNetworkConfig.standard()` accepts `action_count` parameter
- `PaperHoodieNetworkConfig.expected_output_shape` is dynamic
- 11 new tests in `test_campaign_config_extended_dimensions.py`
- Updated `test_paper_hoodie_network_config.py`

### Phase 1B Completed
- `CampaignConfig` exposes `horizontal_data_rate_mbps=30.0`, `vertical_data_rate_mbps=10.0`
- `CampaignConfig.build_link_rate_config()` creates `LinkRateConfig`
- `trainer.py:_build_environment()` passes `link_rate_config`
- `readiness.py:_environment()` passes `link_rate_config`
- 11 new tests in `test_campaign_link_rate_wiring.py`

---

## Critical Finding: state_dim=74 / action_count=22 Not Yet Active in Training Path

Although `CampaignConfig` now *accepts* `state_dim=74` and `action_count=22` without raising, the **actual training/replay state construction is still hard-coded to 3/3**:

| Component | Current Hard-Coding | Paper Target | Status |
|-----------|---------------------|--------------|--------|
| `replay.py:build_state_vector()` | returns `tuple[float, float, float]` (3-dim) | 74-dim state vector | **BLOCKED** |
| `replay.py:zero_state_row()` | returns `(0.0, 0.0, 0.0)` | 74-dim zero row | **BLOCKED** |
| `replay.py:build_state_window_tensor()` | shape `(10, 3)` | shape `(10, 74)` | **BLOCKED** |
| `replay.py:ReplayTransition.state` | `tuple[tuple[float, float, float], ...]` | 74-dim tuples | **BLOCKED** |
| `replay.py:legal_action_mask_to_tuple()` | 3-tuple `(local, horizontal, vertical)` | 22-action mask | **BLOCKED** |
| `replay.py:ACTION_INDEX_TO_SEMANTICS` | 3 entries | 22 entries | **BLOCKED** |
| `trainer.py:_initial_history()` | `deque[tuple[float, float, float]]` | 74-dim deque | **BLOCKED** |
| `trainer.py:_state_tensor()` | `torch.Tensor` from 3-dim history | 74-dim tensor | **BLOCKED** |

This is the single largest remaining work item for Phase 1.

---

## Audit Scores (0–10)

| Category | Score | Classification | Notes |
|----------|-------|----------------|-------|
| A. Git/local sync and artifact truth | 7 | PARTIAL | Local commits exist; push status unconfirmed |
| B. Phase 1A dimension unlock evidence | 10 | PASS | Config accepts 74/22, 11 tests pass |
| C. Phase 1B data-rate wiring evidence | 10 | PASS | Rates wired to trainer+readiness, 11 tests pass |
| D. paper_default config readiness | 3 | BLOCKED | No `paper_default.json` with 74/22 yet; CampaignConfig accepts values but replay.py doesn't use them |
| E. smoke campaign readiness | 2 | BLOCKED | Depends on D + active path wiring |
| F. Figure 7 topology readiness | 8 | PARTIAL | `TopologyGraph.from_approved_assumption_registry()` exists; topology_mode=paper_figure_7 enforced |
| G. state_dim=74 / action_count=22 active path | 2 | BLOCKED | Config accepts but replay.py/trainer.py still use 3/3 |
| H. transmission-delay active-path | 9 | PASS | `gym_adapter.py` correctly routes horizontal/vertical rates |
| I. metrics/KPI export readiness | 5 | PARTIAL | `CampaignReport` exists but no figure-specific KPI extraction |
| J. Figures 8–11 reproduction pathway | 2 | BLOCKED | No figure extraction pipeline; paper_figure_extraction.py exists but not wired to campaign |
| K. LSTM/Figure 11 dependency | 3 | BLOCKED | LSTM encoder exists in network; Figure 11 requires training convergence data |
| L. assumption-backed parameters | 7 | PARTIAL | Most parameters paper-backed; TargetUpdateContract explicitly tracks ambiguity |
| M. test coverage | 7 | PARTIAL | 22 tests for Phase 1A+1B; no tests for 74/22 active path |
| N. scope creep / forbidden edits | 10 | PASS | Only allowed files edited; no training runs, no Phase 2 leakage |

---

## Gates

### Gate 0 — Sync and Truth Baseline
**Status:** PARTIAL  
**Action:** Verify local changes are pushed to origin  
**Commands:**
```bash
git log origin/main..HEAD --oneline
git diff origin/main..HEAD --stat
```
**Stop condition:** `origin/main..HEAD` diff is empty (all local commits pushed)  
**Rollback:** `git reset --soft origin/main` if needed

### Gate 1 — Phase 1A/1B Closure Verification
**Status:** PASS ✅  
**Evidence:** 37/37 tests pass; no regressions; working tree clean  
**Validation:**
```bash
python -m pytest tests/unit/test_full_training_campaign_config.py tests/unit/test_paper_hoodie_network_config.py tests/unit/test_campaign_config_extended_dimensions.py tests/integration/test_campaign_link_rate_wiring.py -v
```

### Gate 2 — paper_default Config Creation
**Status:** BLOCKED  
**Scope:**
- Create ` CampaignConfig` instantiation with all paper parameters (state_dim=74, action_count=22, lr=7e-7, etc.)
- Create JSON config file if project uses config files
**Edit scope:** `src/analysis/full_training_reproduction_campaign/config.py` (additional defaults if needed), new config file  
**Stop condition:** Config with state_dim=74, action_count=22 instantiates without error  
**Validation:** `CampaignConfig(state_dim=74, action_count=22, horizontal_data_rate_mbps=30.0, vertical_data_rate_mbps=10.0)`

### Gate 3 — Smoke Campaign Path
**Status:** BLOCKED (depends on Gate 4)  
**Scope:**
- 3-episode / 50-slot smoke test that verifies: config parses, environment initializes, replay buffer + network allocate, one training step runs without NaN/Inf, one evaluation step runs
- No full training run required
**Edit scope:** `tests/integration/test_smoke_paper_default.py` (new)  
**Stop condition:** Smoke campaign completes 3 episodes with no exceptions or NaN

### Gate 4A — Simplified Campaign Pipeline Viability
**Status:** READY (prerequisite C-001 fix applied)
**Purpose:** Prove campaign orchestration pipeline runs end-to-end with 3D/3-action simplified path.
**Scope:** Existing `replay.py` and `trainer.py` with current 3D/3A configuration.
**Prerequisite:** C-001 fix in `gym_adapter.py:383` (isolated, valid)
**DISCLAIMER:** This gate does NOT claim paper-faithful state/action reproduction. It only validates the pipeline machinery.
**Edit scope:** None (uses existing code)
**Validation:**
```bash
python -m pytest tests/unit/test_slot_engine.py tests/unit/test_baseline_rebuild_sensitivity_audit.py -x --tb=short -q
```
**Stop condition:** Readiness probe + pilot training complete without error using 3D/3A config; pipeline artifacts generated

### Gate 4B — Paper-Faithful 74D/22A Active State/Action Path
**Status:** BLOCKED (largest remaining Phase 1 work)
**Purpose:** Wire 74-dimensional state vector and 22-action legal mask into campaign training path.
**This gate is REQUIRED before claiming Phase 1 paper-faithful baseline readiness.**

**Critical correction:** 74D/22A is NOT Phase 2 / DCQ-MADRL scope. It is the HOODIE paper baseline itself. DCQ-MADRL remains blocked until Phase 1 fully closes.

**Scope:**
- `replay.py:build_state_vector()` — must produce 74-dim state vector matching paper specification
- `replay.py:zero_state_row()` — must return 74-dim zero row
- `replay.py:build_state_window_tensor()` — must produce shape `(10, 74)`
- `replay.py:legal_action_mask_to_tuple()` — must produce 22-action mask
- `replay.py:ACTION_INDEX_TO_SEMANTICS` — must map 22 action indices
- `replay.py:ReplayTransition` — state/next_state must be 74-dim; action must be 0–21; mask must be 22 entries
- `replay.py:ReplayTransition.__post_init__()` — validate 74/22 dimensions
- `trainer.py:_initial_history()` — must use 74-dim deque when config.state_dim=74
- `trainer.py:_state_tensor()` — must produce correct 74-dim tensor
- `readiness.py` — must use 74D/22A state construction
- Paper state vector fields must be mapped from environment observations via `PaperStateBuilder` or `build_paper_state_snapshot`
**Existing implementations to wire in:**
- `src/agents/paper_state_builder.py` — produces 74-dim vector (31 size one-hot + 1 density + 1 private wait + 1 offload wait + 20 public queue + 20 load forecast)
- `src/environment/paper_action_space.py` — produces 22-action destination-specific space with topology legality
- `src/environment/paper_state.py` — PaperStateSnapshot with load history matrix (10×21)
**Edit scope:**
- `src/analysis/full_training_reproduction_campaign/replay.py` (major rewrite)
- `src/analysis/full_training_reproduction_campaign/trainer.py` (moderate update)
- `src/analysis/full_training_reproduction_campaign/readiness.py` (moderate update)
- `src/analysis/full_training_reproduction_campaign/__init__.py` (public API update)
- New tests: `test_paper_replay_transition_74d.py`, `test_paper_replay_transition_22a.py`, `test_trainer_initial_history_74d.py`, `test_campaign_74_22_active_path.py`
**Validation:**
```bash
python -m pytest tests/unit/test_paper_replay_transition_74d.py tests/unit/test_paper_replay_transition_22a.py -v
python -m pytest tests/unit/test_trainer_initial_history_74d.py -v
python -m pytest tests/unit/test_paper_action_space.py tests/unit/test_paper_state_vector.py -v
python -m pytest tests/unit/test_campaign_config_extended_dimensions.py -v
```
**Stop condition:** `build_state_vector()` returns 74-dim; `legal_action_mask_to_tuple()` returns 22-action mask; `ReplayTransition` validates and accepts 74/22 transitions; `DDQNTrainer._initial_history()` uses 74-dim rows when `config.state_dim=74`

### Gate 5 — Metrics and Artifact Export
**Status:** PARTIAL  
**Scope:**
- Verify `CampaignReport` includes link rate and dimension fields
- Verify artifact path produces JSON + Markdown  
**Edit scope:** Report and artifact generation (if gaps found)  
**Stop condition:** Campaign report includes state_dim, action_count, horizontal/vertical rates, transmission delay metadata

### Gate 6 — Figure Reproduction Readiness
**Status:** BLOCKED  
**Scope:**
- Wire `paper_figure_extraction.py` output to campaign results
- Create extraction templates for Figures 8–11
- Define KPI extraction from training logs
**Edit scope:** New analysis modules, figure extraction configs  
**Stop condition:** Campaign output contains machine-readable KPI payloads matching figure data points

### Gate 7 — LSTM/Figure 11 Decision
**Status:** BLOCKED  
**Scope:**
- LSTM encoder is defined in `network.py` but Figure 11 requires convergence + forecast visualization
- Decision needed: implement LSTM forecast extraction or defer Figure 11
**Edit scope:** TBD based on decision  
**Stop condition:** Decision recorded; if implementing, forecast extraction produces training curve + lookahead

### Gate 8 — Final Phase 1 Review and Phase 2 Unlock Decision
**Status:** BLOCKED  
**Scope:**
- All Gates 0–7 must pass
- No paper reproduction claim made (data supports mechanism verification only)
- Phase 2 (DCQ-MADRL) remains blocked until Phase 1 is fully closed
**Stop condition:** All gates pass; human approves Phase 1 closure

---

## Publication Boundary

**No paper reproduction claim is made.** Phase 1 verifies that the simulation infrastructure can faithfully represent the paper's parameters. It does NOT claim that training results match the paper's Figures 8–11. Any reproduction claim requires:
1. Full training convergence with paper parameters
2. Independent verification against paper data
3. Human approval

---

## What Remains Blocked Before Phase 2

1. **Gate 4B (state/action active path)** — the replay and training code must actually construct 74-dim state vectors and 22-action masks. This is Phase 1 paper-faithful HOODIE baseline, NOT Phase 2 / DCQ-MADRL.
2. **Gate 3 (smoke campaign)** — cannot test 74/22 path until Gate 4B
3. **Gate 6 (figure reproduction)** — requires training output
4. **Gate 7 (LSTM/Figure 11)** — requires convergence data
5. **Phase 2 / DCQ-MADRL** — blocked until Phase 1 is fully closed

**Note:** Gate 4A (simplified pipeline viability) is unblocked and can proceed independently of Gate 4B.

---

## Rollback Strategy

| Gate | Rollback |
|------|----------|
| 0 | `git reset --soft origin/main` |
| 1 | Already passed; no rollback needed |
| 2 | Delete paper_default config; revert to defaults |
| 3 | Delete smoke test file |
| 4A | Revert `gym_adapter.py` to pre-C-001 state (not recommended) |
| 4B | Revert `replay.py` and `trainer.py` to 3/3 hard-coding (or keep as configurable with 3 default) |
| 5–8 | Revert specific files per gate |

---

## Acceptance Criteria

Phase 1 is complete when:
1. All local changes are pushed to GitHub (Gate 0)
2. `CampaignConfig(state_dim=74, action_count=22)` instantiates and passes validation (Gate 2)
3. Simplified 3D/3A campaign pipeline runs without error (Gate 4A)
4. `build_state_vector()` returns a 74-dim tuple (Gate 4B)
5. `legal_action_mask_to_tuple()` returns a 22-element mask (Gate 4B)
6. A 3-episode smoke campaign runs to completion without error with 74D/22A config (Gate 3)
7. Campaign report includes all paper parameters (Gate 5)
8. No paper reproduction claim is made in any report or artifact
9. Phase 2 remains blocked
