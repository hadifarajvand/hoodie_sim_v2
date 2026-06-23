# Figure 11: No-LSTM Ablation Study Plan

**Date:** 2026-06-23  
**Figure:** Figure 11 — LSTM Architecture Contribution to Latency Reduction  
**Purpose:** Quantify the performance impact of removing the LSTM layer  
**Comparison:** With-LSTM (baseline) vs Without-LSTM (new ablation)  
**Mode:** Planning only — no execution yet

---

## Existing Baseline (With LSTM)

**Source:** per-EA-distributed-baseline  
**Architecture:** 3×1024 dense layers + 256-unit LSTM layer per agent  
**Training:** 5000 episodes  
**Number of agents:** 20 (distributed, per-agent networks)  
**Hyperparameters:** lr=7e-7, gamma=0.99  
**Checkpoints:** 11 evaluations (episodes 250, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000)  
**Status:** ✓ Already complete and reconciled (delta=0.0)  
**Key metric for ablation:** `avg_latency_slots` at each checkpoint

---

## New Ablation Config (Without LSTM)

### Specification

```
config_id: fig11_no_lstm_ablation
architecture: feedforward_3layer_1024_no_lstm
description: 3×1024 dense (fully connected) without LSTM; matches with-LSTM on all other dimensions
training_mode: full_5000_episodes
episodes: 5000
num_agents: 20
episode_length: 110
evaluation_episode_count: 100
learning_rate: 7e-7 (IDENTICAL to with-LSTM baseline)
gamma: 0.99 (IDENTICAL to with-LSTM baseline)
batch_size: 64 (IDENTICAL)
replay_memory_capacity_per_agent: 10000 (IDENTICAL)
target_update_frequency_episodes: 2000 (IDENTICAL)
epsilon_start: 1.0 (IDENTICAL)
epsilon_final: 0.0 (IDENTICAL)
epsilon_decay_episodes: 2500 (IDENTICAL)
state_representation_profile: deadline_queue_feasibility_v1 (IDENTICAL)
reconciliation_profile: horizon_aware_recovered_reward_event (IDENTICAL)
credit_assignment: per_task_delayed_reward (IDENTICAL)
techniques: [Dueling DQN, Double DQN] (IDENTICAL but NO LSTM)
per_agent_training: true (IDENTICAL)
proposed_method: none (paper-faithful baseline only) (IDENTICAL)
```

**Only change:** Remove LSTM layer from agent network architecture.

**Estimated time:** 1.077 hours (same as with-LSTM baseline)

---

## Network Architecture Details

### With-LSTM (Baseline)

```
Per-agent network:
├── Input (state_dim)
├── Dense(1024, ReLU)
├── Dense(1024, ReLU)
├── Dense(1024, ReLU)
├── LSTM(256, stateful=True)  ← Recurrent processing
├── Dense(action_dim)
└── Output (Q-values)
```

**Key feature:** Recurrent LSTM layer processes temporal sequences, maintaining hidden state across time steps.

### Without-LSTM (Ablation)

```
Per-agent network:
├── Input (state_dim)
├── Dense(1024, ReLU)
├── Dense(1024, ReLU)
├── Dense(1024, ReLU)
├── Dense(action_dim)         ← Direct output (no recurrence)
└── Output (Q-values)
```

**Key change:** No LSTM; purely feedforward. Network sees only current state, not history.

**Why feedforward only?** Isolates LSTM contribution. Without this ablation, we can't tell if performance is due to recurrence or just having large dense layers.

---

## Comparison Strategy

### Checkpoint Schedule (Aligned with Baseline)

Run both with-LSTM and without-LSTM for the same checkpoint schedule:

| Checkpoint | Episodes | Evaluation | Metrics |
|-----------|----------|-----------|---------|
| 1 | 250 | 100 | reward, completion, drop, latency |
| 2 | 500 | 100 | same |
| 3 | 1000 | 100 | same |
| 4 | 1500 | 100 | same |
| 5 | 2000 | 100 | same |
| 6 | 2500 | 100 | same |
| 7 | 3000 | 100 | same |
| 8 | 3500 | 100 | same |
| 9 | 4000 | 100 | same |
| 10 | 4500 | 100 | same |
| 11 | 5000 | 100 | same |

**Why same checkpoints?** Ensures fair comparison. Both agents trained for same total episodes.

---

## Expected Outcomes

### Scenario 1: LSTM Provides Significant Benefit
- With-LSTM curve is consistently lower (better latency)
- Without-LSTM shows slower convergence or plateau
- **Interpretation:** LSTM's recurrence is valuable for latency reduction

### Scenario 2: LSTM Provides Marginal Benefit
- Both curves overlap or very close
- Without-LSTM converges at similar speed
- **Interpretation:** Dense layers alone sufficient; LSTM overhead not justified

### Scenario 3: LSTM Harmful (Unlikely)
- Without-LSTM is better
- **Interpretation:** LSTM causes overfitting or instability in this domain

### Most Likely: Scenario 1 or 2
- Figure 11 is honest regardless
- Caption will state: "With-LSTM achieved [X] slots delay; without-LSTM achieved [Y] slots delay"

---

## Safety: Identical Everything Except Architecture

### Locked Parameters (Identical to Baseline)

| Parameter | Value | Reason |
|-----------|-------|--------|
| lr | 7e-7 | Fair comparison |
| gamma | 0.99 | Fair comparison |
| batch_size | 64 | Fair comparison |
| replay_buffer_size | 10000 | Fair comparison |
| epsilon_schedule | 1.0 → 0.0 over 2500 eps | Fair comparison |
| num_agents | 20 | Fair comparison |
| total_episodes | 5000 | Fair comparison |
| reward_definition | Same | Fair comparison |
| environment_config | Same | Fair comparison |
| evaluation_episodes | 100 per checkpoint | Fair comparison |

**Only variable:** Network architecture (with vs without LSTM)

---

## Training Procedure

### Setup
1. Create new agent class: `DistributedDDQNAgent_NoLSTM`
2. Initialize 20 agents with feedforward-only networks
3. Load same initial weights (from random seed 42) as with-LSTM baseline

### Training Loop
```python
for episode in range(5000):
    state = env.reset()
    agent.reset_hidden_state() if hasattr(agent, 'reset_hidden_state') else None
    done = False
    
    while not done:
        action = agent.select_action(state, training=True)
        next_state, reward, done = env.step(action)
        agent.store_transition(state, action, reward, next_state, done)
        agent.learn()
        state = next_state
    
    # Checkpoint at fixed intervals
    if episode in {250, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000}:
        metrics = evaluate_agent(agent, num_episodes=100)
        save_metrics(metrics, episode)
```

### Evaluation at Each Checkpoint
- Run 100 episodes with agent in inference mode (no training)
- Capture: total_reward, completion_ratio, drop_ratio, avg_latency_slots
- Save to JSON with checkpoint index

---

## Output Expectations

### Per-Ablation Outputs
- `ablation_checkpoint_metrics_no_lstm.json` with 11 evaluations
- `reconciliation_status_no_lstm.json` showing delta and terminal_coverage
- `final-ablation-report.md` with summary

### Figure 11 Panel Data

**11a: Delay Trend (With LSTM) — Already Exists**
- X-axis: Episodes (250–5000)
- Y-axis: Average latency (slots)
- Data source: per-EA-distributed-baseline

**11b: Delay Trend (Without LSTM) — New from Ablation**
- X-axis: Episodes (250–5000)
- Y-axis: Average latency (slots)
- Data source: fig11_no_lstm_ablation

**Combined comparison plot:**
- Both curves on same axes
- Shows latency evolution with and without LSTM
- Allows visual assessment of LSTM contribution

---

## Smoke Test (Lightweight)

Before committing to 1.077 hours, run a smoke test:

```bash
# Smoke test: 50 episodes only (instead of 5000)
# Estimated time: < 5 minutes
HOODIE_SMOKE_EPISODE_LIMIT=50 python -m src.analysis.figure_11_ablation.run_fig11_no_lstm_ablation_smoke
```

**Success criteria:**
- ✓ No crashes
- ✓ Feedforward network initializes correctly
- ✓ Training loop executes without errors
- ✓ Metrics are captured at checkpoints
- ✓ Reconciliation runs successfully
- ✓ Output structure matches baseline

If smoke test passes, proceed with full 5000-episode ablation.

---

## Code Changes Required

**Minimal:** Add feedforward-only agent class.

**What needs to be added:**
- New agent class: `DistributedDDQNAgent_NoLSTM`
- Same as `DistributedDDQNAgent` but with network architecture:
  ```python
  # Instead of Dense → LSTM → Dense
  # Use: Dense → Dense → Dense
  ```

**What stays unchanged:**
- Training loop
- Reward definition
- Reconciliation logic
- Evaluation procedure
- Metric definitions

**Implementation estimate:** < 50 lines of code (copy existing agent, modify network instantiation)

---

## Safety Assertions

- ✓ No reward logic changes
- ✓ No environment topology changes
- ✓ No metric definition changes
- ✓ No proposed method implementation
- ✓ All hyperparameters identical except architecture
- ✓ Same per-agent training setup
- ✓ Same reconciliation profile
- ✓ Same credit assignment
- ✓ Only LSTM removed; all other techniques (Dueling DQN, Double DQN) retained

---

## Approval Required

Full execution blocked until user approves Option B run.

**To approve and run:**
```bash
git checkout figure-completion-option-b-plan
APPROVE_OPTION_B_FIG11_ABLATION=1 python -m src.analysis.figure_11_ablation.run_no_lstm_ablation_full
```

---

## Next Steps

1. ✓ Plan created
2. ⏳ User review
3. ⏳ User approval
4. ⏳ Code implementation (add NoLSTM agent class)
5. ⏳ Smoke test (if approved)
6. ⏳ Full ablation run (if smoke passes)
7. ⏳ Results aggregation into Figure 11 comparison panel
