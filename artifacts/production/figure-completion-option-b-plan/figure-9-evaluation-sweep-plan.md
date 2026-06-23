# Figure 9: System Parameter Sensitivity Evaluation Plan

**Date:** 2026-06-23  
**Figure:** Figure 9 — Behavior Insights & System Parameter Robustness  
**Purpose:** Evaluate learned policy performance across system parameter variations  
**Critical:** Evaluation-only; NO new training required  
**Mode:** Planning only — no execution yet

---

## Key Principle: Evaluation-Only, No Retraining

The trained per-EA-distributed-baseline agent (5000 episodes, 20 agents, LSTM-enabled) will be **fixed** across all system parameter evaluations. We do not train new agents; we test the existing agent's robustness.

### Why Evaluation-Only?

**Full approach (not taken):** Retrain for each system parameter variation.
- Cost: 20+ full training runs
- Benefit: See how system parameters affect learning trajectory
- Issue: Creates dependency between agent training and environment config

**Evaluation-only approach (CHOSEN):** Use one trained agent, evaluate under different parameters.
- Cost: 6 evaluation configs (0.6 hours total)
- Benefit: Isolates policy robustness from training dynamics
- Interpretation: "Does our single learned policy generalize to different system regimes?"

---

## Existing Trained Agent

**Source:** per-EA-distributed-baseline  
**Training:** 5000 episodes, 20 agents, LSTM-enabled  
**Config:** lr=7e-7, gamma=0.99  
**Status:** ✓ Already complete and reconciled (delta=0.0)  
**Policy checkpoint:** Use weights at episode 5000 (final trained policy)

---

## Evaluation Config Specifications

### Config 1: Low Task Arrival Probability (0.2)

```
config_id: fig9_arrival_prob_02
parameter: arrival_probability
value: 0.2
episodes: 100 (evaluation only)
metric_mode: policy_fixed_no_training
agent_policy_source: per-EA-distributed-baseline @ episode 5000
seed: 7 (deterministic)
metrics_captured: [reward, completion_ratio, drop_ratio, latency]
description: Scarce task arrivals (only 20% of slot periods)
```

**Interpretation:** 
- Baseline was trained with arrival_probability=0.5 (or close to it)
- At 0.2, tasks are rare → lower load → policy should have fewer decisions
- Expected: Higher completion (easier problem) or similar drop ratio (policy still effective)

**Estimated time:** 0.1 h

---

### Config 2: Medium Task Arrival Probability (0.5) — Baseline

```
config_id: fig9_arrival_prob_05
parameter: arrival_probability
value: 0.5
episodes: 100 (evaluation only)
metric_mode: policy_fixed_no_training
agent_policy_source: per-EA-distributed-baseline @ episode 5000
seed: 7 (deterministic)
metrics_captured: [reward, completion_ratio, drop_ratio, latency]
description: Standard task arrival rate (baseline training config)
```

**Interpretation:**
- This matches the training environment
- Expected: Consistent with baseline performance metrics

**Estimated time:** 0.1 h

---

### Config 3: High Task Arrival Probability (0.8)

```
config_id: fig9_arrival_prob_08
parameter: arrival_probability
value: 0.8
episodes: 100 (evaluation only)
metric_mode: policy_fixed_no_training
agent_policy_source: per-EA-distributed-baseline @ episode 5000
seed: 7 (deterministic)
metrics_captured: [reward, completion_ratio, drop_ratio, latency]
description: High task arrival (80% of slot periods; congested)
```

**Interpretation:**
- Policy trained at 0.5 now faces higher load (0.8)
- Expected: More failures/drops if policy does not generalize; still good if robust

**Estimated time:** 0.1 h

---

### Config 4: Low DRL Agent Count (10 agents)

```
config_id: fig9_agent_count_10
parameter: num_agents_drl
value: 10
episodes: 100 (evaluation only)
metric_mode: policy_fixed_no_training
agent_policy_source: per-EA-distributed-baseline @ episode 5000
seed: 7 (deterministic)
metrics_captured: [reward, completion_ratio, drop_ratio, latency]
description: Reduced number of DRL agents (half of baseline 20)
```

**Interpretation:**
- Baseline trained with 20 agents
- At 10 agents, fewer decision-makers → more load per agent
- Expected: Worse performance (fewer resources) but policy still works if robust

**Estimated time:** 0.1 h

---

### Config 5: Baseline DRL Agent Count (20 agents)

```
config_id: fig9_agent_count_20
parameter: num_agents_drl
value: 20
episodes: 100 (evaluation only)
metric_mode: policy_fixed_no_training
agent_policy_source: per-EA-distributed-baseline @ episode 5000
seed: 7 (deterministic)
metrics_captured: [reward, completion_ratio, drop_ratio, latency]
description: Standard agent count (baseline training config)
```

**Interpretation:**
- Matches training condition
- Expected: Consistent baseline performance

**Estimated time:** 0.1 h

---

### Config 6: High DRL Agent Count (30 agents)

```
config_id: fig9_agent_count_30
parameter: num_agents_drl
value: 30
episodes: 100 (evaluation only)
metric_mode: policy_fixed_no_training
agent_policy_source: per-EA-distributed-baseline @ episode 5000
seed: 7 (deterministic)
metrics_captured: [reward, completion_ratio, drop_ratio, latency]
description: Increased number of DRL agents (50% more than baseline 20)
```

**Interpretation:**
- More agents → distributed decision-making
- Expected: Better performance (more resources) if cooperation scales

**Estimated time:** 0.1 h

---

## Summary Table

| Config ID | Parameter | Value | Type | Time | Expected Behavior |
|-----------|-----------|-------|------|------|-------------------|
| fig9_arrival_prob_02 | arrival_probability | 0.2 | low | 0.1 h | Rare arrivals; easier problem |
| fig9_arrival_prob_05 | arrival_probability | 0.5 | baseline | 0.1 h | Standard load |
| fig9_arrival_prob_08 | arrival_probability | 0.8 | high | 0.1 h | High load; test robustness |
| fig9_agent_count_10 | num_agents_drl | 10 | low | 0.1 h | Reduced capacity; harder |
| fig9_agent_count_20 | num_agents_drl | 20 | baseline | 0.1 h | Standard team |
| fig9_agent_count_30 | num_agents_drl | 30 | high | 0.1 h | Increased capacity; easier |

**Total new evaluations:** 6  
**Total time:** 0.6 hours (6 × 0.1 h per evaluation)

---

## Why NOT Full Multi-Dimensional Sweep?

**Original plan (not taken):** Test all combinations of arrival × agent_count
- 3 arrival values × 3 agent counts = 9 configs
- Time: 0.9 hours

**Chosen plan:** Separate 1D slices
- 3 arrival values (fixed agent_count=20) + 3 agent counts (fixed arrival=0.5) − 1 overlap = 5 + 1 = 6 configs
- Time: 0.6 hours
- Benefit: Clearer interpretation (main effects visible)
- Cost: Miss interaction effects (arrival × agent_count)

For Figure 9 robustness, main effects are more important than interactions.

---

## Existing Data Reusability: Controlled-Mechanistic-Sweeps

**Found:** artifacts/analysis/controlled-mechanistic-sweeps/

**Reviewed:** Contains sweep definitions for arrival_probability, timeout, cpu_capacity, link_rate, topology_density.

**Key difference:**
- controlled-mechanistic-sweeps uses **random fixed-seed agents (seed=7)**, not our trained policy
- We need **our specific trained per-EA-distributed agent** evaluated under parameter variations
- Therefore: **Cannot directly reuse controlled-mechanistic-sweeps data**

**Action:** Create new evaluation configs from scratch, using our trained agent.

---

## Evaluation Procedure

For each config:

1. **Load trained policy**
   ```python
   agent = load_per_ea_distributed_baseline_agent(checkpoint_episode=5000)
   ```

2. **Configure environment parameter**
   ```python
   env.set_arrival_probability(config['value'])  # or set_num_agents_drl
   ```

3. **Run 100 evaluation episodes (no training)**
   ```python
   for episode in range(100):
       state = env.reset(seed=7)
       done = False
       while not done:
           action = agent.select_action(state, training=False)  # Inference only
           state, reward, done = env.step(action)
   ```

4. **Capture metrics**
   ```python
   metrics = {
       'reward': total_reward_per_episode,
       'completion_ratio': completed_tasks / total_tasks,
       'drop_ratio': dropped_tasks / total_tasks,
       'latency': average_latency_slots
   }
   ```

5. **Save results**
   ```json
   {
       "config_id": "fig9_arrival_prob_02",
       "metrics": metrics,
       "episodes_evaluated": 100,
       "checkpoint_used": 5000
   }
   ```

---

## Output Expectations

### Per-Config Output
Each evaluation produces:
- `evaluation_results_<config_id>.json` with aggregated metrics
- `evaluation_episodes_<config_id>.json` with per-episode data

### Figure 9 Panel Data

**9a: Action Distribution (Already Real)**
- Pie/bar chart showing % vertical, % horizontal, % local
- Data: Final policy action distribution from baseline

**9b: Reward vs Arrival Probability**
- X-axis: Arrival probability {0.2, 0.5, 0.8}
- Y-axis: Average reward per episode
- 1 curve (single trained agent under 3 arrival conditions)

**9c: Reward vs Agent Count**
- X-axis: Agent count {10, 20, 30}
- Y-axis: Average reward per episode
- 1 curve (single trained agent under 3 team sizes)

---

## Smoke Test (Lightweight)

Before committing to 0.6 hours, run a smoke test:

```bash
# Smoke test: 10 evaluation episodes only (instead of 100)
# Estimated time: < 2 minutes
HOODIE_SMOKE_EVAL_LIMIT=10 python -m src.analysis.figure_9_sensitivity.eval_fig9_arrival_prob_02_smoke
```

**Success criteria:**
- ✓ No crashes
- ✓ Metrics are captured
- ✓ Agent policy loads successfully
- ✓ Environment parameter changes work

If smoke test passes, proceed with full 6-config evaluation.

---

## Code Changes Required

**None.** All evaluations use existing agent and environment code. Only environment parameters change.

---

## Safety Assertions

- ✓ No agent retraining
- ✓ No reward logic changes
- ✓ No environment topology changes
- ✓ No metric definition changes
- ✓ No proposed method implementation
- ✓ Fixed policy (no learning during evaluation)
- ✓ Deterministic seed for reproducibility

---

## Approval Required

Full execution blocked until user approves Option B run.

**To approve and run:**
```bash
git checkout figure-completion-option-b-plan
APPROVE_OPTION_B_FIG9_EVAL=1 python -m src.analysis.figure_9_sensitivity.run_all_system_param_evals
```

---

## Next Steps

1. ✓ Plan created
2. ⏳ User review
3. ⏳ User approval
4. ⏳ Smoke test (if approved)
5. ⏳ Full evaluation run (if smoke passes)
6. ⏳ Results aggregation into Figure 9 panels
