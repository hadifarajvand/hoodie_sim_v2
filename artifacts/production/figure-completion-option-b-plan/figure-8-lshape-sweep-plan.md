# Figure 8: L-Shaped Hyperparameter Sweep Plan

**Date:** 2026-06-23  
**Figure:** Figure 8 — Reward Time-Course During Training  
**Purpose:** Demonstrate hyperparameter robustness (learning rate + discount factor sensitivity)  
**Mode:** Planning only — no execution yet

---

## Existing Baseline

**Source:** `per-EA-distributed-baseline`  
**Config:** lr=7e-7, gamma=0.99  
**Runtime:** 1.077 wall hours  
**Checkpoints:** 11 evaluations (episodes 250, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000)  
**Output:** Accumulated reward and reward-per-task curves  
**Status:** ✓ Already complete  

---

## Sweep Strategy: L-Shape (5 New Runs)

### Why L-Shaped?

**Option 1: Full Factorial Sweep**
- Learning rates: {1e-6, 5e-7, 7e-7, 1e-7} = 4 values
- Discount factors: {0.95, 0.99, 0.995} = 3 values
- Total configs: 4 × 3 = **12 configs**
- Time: **13 hours**

**Option 2: L-Shaped Sweep (CHOSEN)**
- LR sweep at fixed gamma=0.99: {1e-6, 5e-7, 7e-7, 1e-7} = 4 configs
- Gamma sweep at fixed lr=7e-7: {0.95, 0.99, 0.995} = 3 configs
- Minus overlap (7e-7, 0.99 already done): = 4 + 3 − 1 = **6 configs**
- But we already have baseline, so **5 new configs**
- Time: **5.4 hours**

**Reduction:** ~58% fewer runs while capturing main effects

**Trade-off:** We lose interaction terms (e.g., high-lr + high-gamma), but main effects are more important for learning curves.

---

## Run Specifications

### Run 1: fig8_lr_1e6_gamma099 (High Learning Rate)

```
config_id: fig8_lr_1e6_gamma099
learning_rate: 1e-6
gamma: 0.99
episodes: 5000
num_agents: 20
episode_length: 110
evaluation_episode_count: 100
batch_size: 64
replay_memory_capacity_per_agent: 10000
target_update_frequency_episodes: 2000
epsilon_start: 1.0
epsilon_final: 0.0
epsilon_decay_episodes: 2500
state_representation_profile: deadline_queue_feasibility_v1
reconciliation_profile: horizon_aware_recovered_reward_event
credit_assignment: per_task_delayed_reward
techniques: [LSTM, Dueling DQN, Double DQN]
per_agent_enabled: true
proposed_method: none (paper-faithful baseline only)
```

**Rationale:** 10× baseline LR. Tests whether faster learning speeds up convergence or causes instability.  
**Expected behavior:** May show faster initial convergence but potential oscillation.  
**Estimated time:** 1.077 h

---

### Run 2: fig8_lr_5e7_gamma099 (Mid-Low Learning Rate)

```
config_id: fig8_lr_5e7_gamma099
learning_rate: 5e-7
gamma: 0.99
episodes: 5000
num_agents: 20
episode_length: 110
evaluation_episode_count: 100
batch_size: 64
replay_memory_capacity_per_agent: 10000
target_update_frequency_episodes: 2000
epsilon_start: 1.0
epsilon_final: 0.0
epsilon_decay_episodes: 2500
state_representation_profile: deadline_queue_feasibility_v1
reconciliation_profile: horizon_aware_recovered_reward_event
credit_assignment: per_task_delayed_reward
techniques: [LSTM, Dueling DQN, Double DQN]
per_agent_enabled: true
proposed_method: none (paper-faithful baseline only)
```

**Rationale:** 0.7× baseline LR. Tests slightly conservative learning.  
**Expected behavior:** Similar to baseline, possibly slightly slower convergence.  
**Estimated time:** 1.077 h

---

### Run 3: fig8_lr_1e7_gamma099 (Low Learning Rate)

```
config_id: fig8_lr_1e7_gamma099
learning_rate: 1e-7
gamma: 0.99
episodes: 5000
num_agents: 20
episode_length: 110
evaluation_episode_count: 100
batch_size: 64
replay_memory_capacity_per_agent: 10000
target_update_frequency_episodes: 2000
epsilon_start: 1.0
epsilon_final: 0.0
epsilon_decay_episodes: 2500
state_representation_profile: deadline_queue_feasibility_v1
reconciliation_profile: horizon_aware_recovered_reward_event
credit_assignment: per_task_delayed_reward
techniques: [LSTM, Dueling DQN, Double DQN]
per_agent_enabled: true
proposed_method: none (paper-faithful baseline only)
```

**Rationale:** 0.14× baseline LR. Tests conservative learning (low stability risk).  
**Expected behavior:** Very slow convergence, potential underfitting.  
**Estimated time:** 1.077 h

---

### Run 4: fig8_lr_7e7_gamma095 (Low Discount Factor)

```
config_id: fig8_lr_7e7_gamma095
learning_rate: 7e-7
gamma: 0.95
episodes: 5000
num_agents: 20
episode_length: 110
evaluation_episode_count: 100
batch_size: 64
replay_memory_capacity_per_agent: 10000
target_update_frequency_episodes: 2000
epsilon_start: 1.0
epsilon_final: 0.0
epsilon_decay_episodes: 2500
state_representation_profile: deadline_queue_feasibility_v1
reconciliation_profile: horizon_aware_recovered_reward_event
credit_assignment: per_task_delayed_reward
techniques: [LSTM, Dueling DQN, Double DQN]
per_agent_enabled: true
proposed_method: none (paper-faithful baseline only)
```

**Rationale:** gamma−0.04 from baseline. Tests myopic discounting (favor immediate rewards).  
**Expected behavior:** May show faster initial learning but plateau sooner (values future less).  
**Estimated time:** 1.077 h

---

### Run 5: fig8_lr_7e7_gamma0995 (High Discount Factor)

```
config_id: fig8_lr_7e7_gamma0995
learning_rate: 7e-7
gamma: 0.995
episodes: 5000
num_agents: 20
episode_length: 110
evaluation_episode_count: 100
batch_size: 64
replay_memory_capacity_per_agent: 10000
target_update_frequency_episodes: 2000
epsilon_start: 1.0
epsilon_final: 0.0
epsilon_decay_episodes: 2500
state_representation_profile: deadline_queue_feasibility_v1
reconciliation_profile: horizon_aware_recovered_reward_event
credit_assignment: per_task_delayed_reward
techniques: [LSTM, Dueling DQN, Double DQN]
per_agent_enabled: true
proposed_method: none (paper-faithful baseline only)
```

**Rationale:** gamma+0.005 from baseline. Tests stronger long-term value emphasis.  
**Expected behavior:** May show more stable asymptotic behavior, slightly slower convergence.  
**Estimated time:** 1.077 h

---

## Summary

| Run ID | LR | Gamma | Type | Time |
|--------|-------|-------|------|------|
| (baseline: fig8_lr_7e7_gamma099) | 7e-7 | 0.99 | existing | 1.077 h |
| fig8_lr_1e6_gamma099 | 1e-6 | 0.99 | new | 1.077 h |
| fig8_lr_5e7_gamma099 | 5e-7 | 0.99 | new | 1.077 h |
| fig8_lr_1e7_gamma099 | 1e-7 | 0.99 | new | 1.077 h |
| fig8_lr_7e7_gamma095 | 7e-7 | 0.95 | new | 1.077 h |
| fig8_lr_7e7_gamma0995 | 7e-7 | 0.995 | new | 1.077 h |

**Total new runs:** 5  
**Total time:** 5.4 hours

---

## Output Expectations

### Per-Run Outputs
Each run will produce:
- `checkpoint_metrics.json` with 11 evaluations
- `reconciliation_status.json` showing delta and terminal_coverage
- `final-run-report.md` with summary stats

### Figure 8 Panel Data
**8a: Accumulated Reward Over Training**
- X-axis: Episodes (250–5000)
- Y-axis: Accumulated total reward
- 6 curves (baseline + 5 new)

**8b: Reward Per Task Over Training**
- X-axis: Episodes
- Y-axis: Reward per completed task
- 6 curves

### Sensitivity Analysis
- **LR sensitivity:** Compare 3 LR curves at fixed gamma=0.99
- **Gamma sensitivity:** Compare 3 gamma curves at fixed lr=7e-7
- **Interpretation:** How robust is convergence to these hyperparams?

---

## Smoke Test (Lightweight)

Before committing to 5.4 hours, run a smoke test for one config:

```bash
# Smoke test: 50 episodes only (instead of 5000)
# Estimated time: < 5 minutes
HOODIE_SMOKE_EPISODE_LIMIT=50 python -m src.analysis.figure_8_sweep.run_fig8_lr_1e6_gamma099_smoke
```

**Success criteria:**
- ✓ No crashes
- ✓ Metrics are captured at checkpoints
- ✓ Reconciliation runs successfully
- ✓ Output structure matches baseline

If smoke test passes, proceed with full 5-run sweep.

---

## Code Changes Required

**None.** All configs use existing trainer and agent code. Only hyperparameter values change.

---

## Safety Assertions

- ✓ No reward logic changes
- ✓ No environment topology changes
- ✓ No metric definition changes
- ✓ No proposed method implementation
- ✓ All runs use per-agent training (consistent with baseline)
- ✓ All runs use LSTM, Dueling DQN, Double DQN (consistent)
- ✓ All runs use same reconciliation profile

---

## Approval Required

Full execution blocked until user approves Option B run.

**To approve and run:**
```bash
git checkout figure-completion-option-b-plan
APPROVE_OPTION_B_FIG8_SWEEP=1 python -m src.analysis.figure_8_sweep.run_all_lshape_configs
```

---

## Next Steps

1. ✓ Plan created
2. ⏳ User review
3. ⏳ User approval
4. ⏳ Smoke test (if approved)
5. ⏳ Full run (if smoke passes)
6. ⏳ Results aggregation into Figure 8 panels
