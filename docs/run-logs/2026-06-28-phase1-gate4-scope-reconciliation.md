# Phase 1 Gate 4 Scope Reconciliation

**Date:** 2026-06-29
**Status:** RESOLVED — plan corrected
**Trigger:** Review approved Gate 4 continuation but incorrectly redefined it as 3D/3-action simplified campaign, contradicting the paper-faithful HOODIE baseline objective.

---

## Problem Statement

The prior review (`gate4-review-2026-06-29`) concluded that Gate 4 could proceed using the existing simplified campaign path (state_dim=3, action_count=3). This is **incorrect** for Phase 1 paper-faithful baseline reproduction because:

1. The HOODIE paper requires **state_dim=74** (31 task-size one-hot + 1 density + 1 private wait + 1 offload wait + 20 public queue lengths + 20 load forecast values).
2. The HOODIE paper requires **action_count=22** (1 local + 20 horizontal destinations + 1 cloud).
3. These dimensions are **NOT** Phase 2 / DCQ-MADRL scope — they are the HOODIE baseline itself.
4. DCQ-MADRL remains blocked until paper-faithful baseline reproduction is complete.

---

## Evidence From Codebase

### Already Exists (Paper-Faithful Components)

| Component | File | Status |
|-----------|------|--------|
| 74D state builder | `src/agents/paper_state_builder.py` | ✅ Implemented, produces 74-dim vector for N=20 |
| 22-action space | `src/environment/paper_action_space.py` | ✅ Implemented, produces 22-action mask with topology legality |
| 74D state snapshot | `src/environment/paper_state.py` | ✅ Implemented, load history + waiting times + queue vector |
| Tests for 74D state | `tests/unit/test_paper_state_vector.py` | ✅ Pass (2 tests) |
| Tests for 22 actions | `tests/unit/test_paper_action_space.py` | ✅ Pass (2 tests) |
| HoodieModel 74D path | `src/agents/hoodie_model.py:61-93` | ✅ Dynamic init from observation |
| Topology (Figure 7) | `src/environment/topology.py` | ✅ `from_approved_assumption_registry()` |

### NOT Yet Wired to Campaign

| Component | File | Current | Required |
|-----------|------|---------|----------|
| `build_state_vector()` | `replay.py:38` | Returns `tuple[float, float, float]` (3D) | Must return 74-dim vector |
| `zero_state_row()` | `replay.py:22` | Returns `(0.0, 0.0, 0.0)` | Must return 74-dim zero row |
| `build_state_window_tensor()` | `replay.py:34-35` | Shape `(10, 3)` | Shape `(10, 74)` |
| `ReplayTransition.state` | `replay.py:72` | `tuple[tuple[float, float, float], ...]` | 74-dim tuples |
| `legal_action_mask_to_tuple()` | `replay.py:52` | 3-tuple | 22-tuple |
| `ACTION_INDEX_TO_SEMANTICS` | `replay.py:9-13` | 3 entries | 22 entries |
| `ReplayTransition` validation | `replay.py:93-96` | Validates 3 actions / 3 mask | Must validate 22 |
| `trainer._initial_history()` | `trainer.py:191-193` | 3-dim deque | 74-dim deque |

---

## Decision: Split Gate 4 into 4A and 4B

### Gate 4A — Simplified Campaign Pipeline Viability

**Purpose:** Prove the campaign orchestration pipeline runs end-to-end with 3D/3-action.
**Allowed scope:** Existing `replay.py` and `trainer.py` with current 3D/3A path.
**Acceptance criteria:**
- Readiness probe completes 3 episodes without error
- Pilot training completes with finite loss
- Replay buffer stores and samples transitions correctly
- Campaign report generates JSON + Markdown artifacts
- **EXPLICIT DISCLAIMER:** This gate does NOT claim paper-faithful state/action reproduction

**Prerequisite fixes:**
- C-001 `gym_adapter.py:383` fix is an **isolated prerequisite** — env.step() must work for any campaign path
- C-001 is valid and does not need rollback

**Validation:**
```bash
pytest tests/unit/test_slot_engine.py tests/unit/test_baseline_rebuild_sensitivity_audit.py -x --tb=short -q
```

### Gate 4B — Paper-Faithful Active State/Action Path

**Purpose:** Wire the paper-faithful 74D/22A state vector and action mask into the campaign training path.
**Required for:** Phase 1 paper-faithful HOODIE baseline reproduction.
**Status:** BLOCKED (not started)

**Implementation scope (ordered):**

1. **replay.py — Action semantics expansion**
   - `ACTION_INDEX_TO_SEMANTICS`: Expand from 3 entries to 22 entries matching `paper_action_space.py` destination indexing
   - `SEMANTICS_TO_ACTION_INDEX`: Inverse map of the above
   - `legal_action_mask_to_tuple()`: Accept 22-action mask dict, return 22-tuple
   - `ReplayTransition.__post_init__()`: Validate 22-action indices and 22-entry masks
   - Keep backward-compat: `STATE_DIM` constant becomes configurable or 74-by-default

2. **replay.py — State vector expansion**
   - `build_state_vector()`: Wire to `PaperStateBuilder` or `build_paper_state_snapshot()`, return 74-dim tuple
   - `zero_state_row()`: Return 74-dim zero tuple
   - `build_state_window_tensor()`: Produce shape `(10, 74)`
   - `ReplayTransition.state/next_state`: Typed as 74-dim tuples, validated for length

3. **trainer.py — History shape update**
   - `_initial_history()`: Use 74-dim zero rows
   - `_state_tensor()`: Pass 74-dim window through network
   - Ensure `CampaignConfig.state_dim=74` flows through to network construction

4. **readiness.py — Probe uses 74D/22A**
   - Import and use `build_paper_state_snapshot` / `build_legal_action_mask` from environment
   - History deque initialized with 74-dim rows
   - Action selection uses 22-action space indices

5. **New tests**
   - `test_paper_replay_transition_74d.py`: ReplayTransition accepts/rejects 74D state
   - `test_paper_replay_transition_22a.py`: ReplayTransition validates 22-action mask
   - `test_trainer_initial_history_74d.py`: Trainer produces 74-dim history
   - `test_campaign_74_22_active_path.py`: Full smoke with 74D/22A config

**Dependency graph:**
```
paper_action_space.py (exists) ──> replay.py:ACTION_INDEX_TO_SEMANTICS
paper_state_builder.py (exists) ──> replay.py:build_state_vector
paper_state.py (exists) ──> replay.py:build_state_vector
replay.py ──> trainer.py:_initial_history / _state_tensor
replay.py ──> readiness.py:run
trainer.py ──> config.py:CampaignConfig (state_dim=74 already accepted)
```

**Impact radius:**
- `src/analysis/full_training_reproduction_campaign/replay.py` — major rewrite
- `src/analysis/full_training_reproduction_campaign/trainer.py` — moderate update
- `src/analysis/full_training_reproduction_campaign/readiness.py` — moderate update
- `src/analysis/full_training_reproduction_campaign/__init__.py` — public API update
- `tests/unit/` — new test files, 4-5 files
- **No changes needed to:** `paper_state_builder.py`, `paper_action_space.py`, `paper_state.py`, `topology.py`, `gym_adapter.py`, `hoodie_model.py`

**Acceptance criteria:**
- `build_state_vector()` returns 74-dim tuple
- `legal_action_mask_to_tuple()` returns 22-element tuple
- `ReplayTransition` validates and accepts 74/22 transitions
- `DDQNTrainer._initial_history()` uses 74-dim rows when `config.state_dim=74`
- All existing 3D/3A tests continue to pass (backward-compatible or versioned)
- Phase 2 / DCQ-MADRL remains blocked

**Validation:**
```bash
pytest tests/unit/test_paper_replay_transition_74d.py -v
pytest tests/unit/test_paper_replay_transition_22a.py -v
pytest tests/unit/test_trainer_initial_history_74d.py -v
pytest tests/unit/test_paper_action_space.py tests/unit/test_paper_state_vector.py -v
pytest tests/unit/test_campaign_config_extended_dimensions.py -v
```

---

## Phase 2 / DCQ-MADRL Status

**STILL BLOCKED.** Phase 2 cannot start until:
1. Gate 4B passes (74D/22A active path)
2. Gate 3 passes (smoke campaign with paper-faithful config)
3. Gate 5 passes (metrics/artifact export)
4. Gate 6 passes (figure reproduction readiness)
5. Gate 7 passes (LSTM/Figure 11 decision)
6. Gate 8 passes (final review + human approval)

74D/22A is NOT a DCQ-MADRL concern. It is the HOODIE paper baseline.

---

## C-001 Status

**C-001 is an isolated prerequisite fix.** It fixes `advance_shared_runtime()` call in `gym_adapter.py:383` which was missing the `compute_config` argument. This fix is required by both Gate 4A and Gate 4B because any campaign execution path calls `env.step()` which calls `_maybe_finalize_head()`. No rollback needed.
