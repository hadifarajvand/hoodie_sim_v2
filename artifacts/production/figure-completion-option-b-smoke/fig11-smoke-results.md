# Figure 11 Smoke Test Results

**Status:** ⚠️ NOT EXECUTED — Execution module and agent class do not exist

---

## What Was Planned

Figure 11 smoke test (50-episode quick validation):
- Config: No-LSTM ablation variant
- Network architecture: Feedforward only (3×1024 dense, no LSTM layer)
- All other hyperparameters: Identical to baseline (lr=7e-7, gamma=0.99)
- Episode limit: 50 (vs 5000 for full)
- Expected duration: <5 minutes
- Expected reconciliation delta: 0.0
- Purpose: Validate feedforward-only agent initializes and trains

---

## Why It Didn't Execute

Two prerequisites are missing:

1. ❌ Execution module `src/analysis.figure_11_ablation` does not exist
2. ❌ Agent class `src.agents.distributed_agent_no_lstm` does not exist

### What Needs to Exist: Execution Module

File: `src/analysis/figure_11_ablation/__init__.py`

Required functions:

```python
def run_fig11_no_lstm_ablation_smoke(
    output_dir: str,
    log_level: str = "info"
) -> dict:
    """Run 50-episode smoke test for no-LSTM ablation."""
    # Initialize DistributedDDQNAgent_NoLSTM
    # Check HOODIE_SMOKE_EPISODE_LIMIT for episode count
    # Run 50 episodes of training
    # Return metrics with reconciliation delta

def run_fig11_no_lstm_ablation_full(
    output_dir: str,
    episodes: int = 5000,
    checkpoints: list[int] = None,
    eval_episodes: int = 100,
    log_level: str = "info",
    save_checkpoints: bool = True
) -> dict:
    """Run 5000-episode training for no-LSTM ablation."""
    # Initialize DistributedDDQNAgent_NoLSTM
    # Train for 5000 episodes with checkpoints at specified points
    # Return all checkpoint metrics
```

### What Needs to Exist: Agent Class

File: `src/agents/distributed_agent_no_lstm.py`

This file should contain:

```python
class DistributedDDQNAgent_NoLSTM:
    """Distributed DDQN agent WITHOUT LSTM layer.
    
    Architecture:
    - Input: state representation (same as baseline)
    - Layer 1: Dense(1024, ReLU)
    - Layer 2: Dense(1024, ReLU)
    - Layer 3: Dense(1024, ReLU)
    - Output: Q-values (no LSTM)
    
    All other properties identical to DistributedDDQNAgent:
    - 20 agents total
    - Per-agent networks and optimizers
    - Per-agent replay buffers
    - Per-agent epsilon schedules
    - Target network sync every 2000 episodes
    - Dueling DQN + Double DQN techniques
    """
```

---

## Key Difference from Baseline

| Component | With LSTM (Baseline) | Without LSTM (Ablation) |
|-----------|----------------------|------------------------|
| Network layers | Dense + LSTM + Dense | Dense + Dense + Dense |
| Sequence modeling | Yes (LSTM) | No (feedforward) |
| Memory across episodes | Yes | No |
| Parameter count | ~X | ~0.9X (fewer LSTM params) |
| Convergence speed | ? | ? (ablation will show) |
| Final performance | Baseline | Ablation comparison |

---

## Why This Ablation Matters

**Research question:** Does the LSTM layer significantly help distributed DDQN?

**How to answer:** Train the same agent with/without LSTM, same hyperparams, compare results.

**Expected outcomes (scenarios):**

1. **LSTM is critical:** Without-LSTM converges slower, final performance much worse
   - Conclusion: LSTM is important for credit assignment
2. **LSTM is helpful but not critical:** Performance drops slightly but agent still learns
   - Conclusion: LSTM is beneficial but not essential
3. **LSTM is neutral:** With/without LSTM give similar results
   - Conclusion: LSTM overhead not justified for this domain

---

## Expected Results (If Test Had Executed)

### Metrics
- Learning curve: Reward vs episode (same scale as with-LSTM baseline)
- Checkpoints: 11 (at 250, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000)
- Per-checkpoint metrics:
  - `reward_per_checkpoint`: Average reward at checkpoint
  - `completion_ratio`: Percentage of tasks completed
  - `drop_ratio`: Percentage of tasks dropped
  - `latency_slots`: Average slots to completion

### Reconciliation
- `delta`: 0.0 (expected; same harness and reconciliation profile)
- `terminal_coverage`: 1.0 (expected; all tasks evaluated)

### Output Files
- `smoke_metrics.json`: Summary of smoke run
- `smoke_checkpoint_metrics.json`: Per-checkpoint breakdown
- `smoke_reconciliation_status.json`: Reconciliation verification

---

## Validation Criteria (Not Checked Yet)

- [ ] Agent initializes without LSTM layer
- [ ] Training loop executes without crash
- [ ] Reconciliation delta = 0.0
- [ ] Terminal coverage = 1.0
- [ ] Reward values in expected range (no NaN/Inf)
- [ ] Checkpoints save and load correctly
- [ ] Network has no LSTM operations (verifiable in graph)

---

## Full Run Configuration (After Smoke Approval)

Once smoke passes, the full Figure 11 ablation would run:

| Variant | Architecture | Hyperparams | Episodes | Time |
|---------|---|---|---|---|
| With LSTM (baseline) | Dense + LSTM + Dense | lr=7e-7, gamma=0.99 | 5000 | 1.077 h |
| Without LSTM (ablation) | Dense + Dense + Dense | lr=7e-7, gamma=0.99 | 5000 | 1.077 h |
| **Comparison** | — | Identical except architecture | — | **~2.2 h total** |

---

## Implementation Blockers

- [ ] Agent class `DistributedDDQNAgent_NoLSTM` must be created (~50 lines)
- [ ] Module `src/analysis/figure_11_ablation` must be created
- [ ] Agent initialization must use correct network definition
- [ ] It must respect `HOODIE_SMOKE_EPISODE_LIMIT` env var
- [ ] It must respect `APPROVE_OPTION_B_FIG11_ABLATION` approval gate
- [ ] Checkpoints must save at specified episodes
- [ ] Metrics must be recorded and traced to source config

---

## Safety Constraints (Must Be Enforced)

- ✓ No reward function modifications
- ✓ No environment topology changes
- ✓ No metric definition changes
- ✓ All hyperparameters locked to baseline (lr, gamma, batch size, etc.)
- ✓ Only network architecture changes (remove LSTM)
- ✓ Same reconciliation profiles as baseline

---

## Approval Gate

Before full Figure 11 ablation runs, this must be set:

```bash
export APPROVE_OPTION_B_FIG11_ABLATION=1
```

---

## Next Steps

1. Create `src/agents/distributed_agent_no_lstm.py` (~50 lines)
   - Copy DistributedDDQNAgent
   - Remove LSTM from network initialization
   - Everything else identical
2. Create `src/analysis/figure_11_ablation/__init__.py`
   - Implement smoke and full run functions
3. Run smoke test: `APPROVE_OPTION_B_FIG11_ABLATION=1 python -m src.analysis.figure_11_ablation.run_fig11_no_lstm_ablation_smoke`
4. Once smoke passes, run full ablation
5. Generate comparison figure (with vs without LSTM)

---

**Status:** Awaiting agent class and module creation, plus user approval.
