# Paper Figure Status Matrix

**Date:** 2026-06-23  
**Baseline:** True per-EA distributed full 5000-episode campaign

---

## Summary

| Figure | Title | Status | Completion | Notes |
|--------|-------|--------|------------|-------|
| **8** | Accumulated Reward & Reward-per-Task | PARTIAL | 50% | Real single-config data; sweep curves missing |
| **9** | Action Distribution & Parameter Sensitivity | PARTIAL | 20% | Real action distribution; parameter sweeps missing |
| **10** | Delay & Drop Ratio Comparison | COMPLETE | 100% | Both panels produced from run data |
| **11** | LSTM Ablation (Delay) | PARTIAL | 50% | With-LSTM real; without-LSTM missing |

---

## Figure 8: Accumulated Reward & Reward-per-Task Over Training

**Purpose:** Show learning progress of the per-EA distributed agent across training episodes.

### Sub-figure 8a: Accumulated Reward Over Training Episodes
- **Status:** ✓ PRODUCED
- **Data source:** Distributed candidate full campaign (250, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000)
- **Configuration:** Single fixed config (lr=7e-7, γ=0.99, batch=64, replay=10000)
- **Y-axis:** Accumulated total reward across evaluation episode
- **X-axis:** Training episode count
- **Generated:** From `distributed-candidate-metrics.json` final episode results

### Sub-figure 8b: Reward-per-Task Over Training Episodes
- **Status:** ✓ PRODUCED
- **Data source:** Same as 8a
- **Y-axis:** Average reward per task completed/dropped
- **X-axis:** Training episode count
- **Generated:** From `reward_per_task` field in metrics

### Sub-figure 8c–8e (placeholder): Parameter Sweep Panels
- **Status:** ✗ MISSING
- **Required:** Learning rate and discount factor (γ) sensitivity
- **Panel 8c:** Reward by learning rate (e.g., [1e-6, 5e-7, 7e-7, 1e-7])
- **Panel 8d:** Reward by discount factor (e.g., [0.95, 0.99, 0.995])
- **Panel 8e:** Combined 2D heatmap (lr vs γ)
- **Effort:** Requires ~5–10 additional full 5000-episode training runs with different hyperparameter pairs

### Overall Status
**PARTIAL** — Single-config curves complete; sweep panels require additional training.

---

## Figure 9: Action Distribution & System Parameter Sensitivity

**Purpose:** Show how the agent's routing behavior varies with system configurations.

### Sub-figure 9a: Action Distribution (Real)
- **Status:** ✓ PRODUCED
- **Data source:** Distributed candidate final evaluation
- **Chart type:** Stacked bar chart
- **Categories:** Local, Horizontal, Vertical
- **X-axis:** Training checkpoints (250, 500, 1000, ..., 5000)
- **Y-axis:** Proportion of actions (0–1)
- **Observation:** Evolved from mixed (smoke) to vertical-dominant (final)
- **Generated:** From `distributed-candidate-metrics.json` aggregated per checkpoint

### Sub-figure 9b (placeholder): Reward by Task Arrival Probability
- **Status:** ✗ MISSING
- **Required:** System parameter sweep on task arrival rate
- **X-axis:** Arrival probability values (e.g., [0.2, 0.4, 0.6, 0.8])
- **Y-axis:** Agent reward or completion ratio
- **Effort:** Requires ~5–10 additional training runs with different arrival distributions

### Sub-figure 9c (placeholder): Reward by DRL Agent Count
- **Status:** ✗ MISSING
- **Required:** Sweep on number of edge agents (N_a)
- **X-axis:** Number of agents (e.g., [5, 10, 15, 20, 25])
- **Y-axis:** Reward/completion
- **Effort:** Requires ~5–10 additional training runs with different topology sizes

### Sub-figure 9d (placeholder): Reward by CPU Capacity
- **Status:** ✗ MISSING
- **Required:** Sweep on available CPU capacity per agent
- **X-axis:** CPU capacity (normalized or absolute)
- **Y-axis:** Reward/completion
- **Effort:** Requires ~5 additional training runs with different capacity levels

### Sub-figure 9e (placeholder): Reward by Offloading Data Rate
- **Status:** ✗ MISSING
- **Required:** Sweep on offloading bandwidth/cost
- **X-axis:** Data rate or cost multiplier
- **Y-axis:** Reward/completion
- **Effort:** Requires ~5 additional training runs with different offloading rates

### Overall Status
**PARTIAL** — Real action distribution data exists; all parameter sensitivity curves missing.

---

## Figure 10: Delay & Drop Ratio Comparison (vs Baselines)

**Purpose:** Compare per-EA distributed agent performance against baseline policies.

### Sub-figure 10a: Average Latency (Delay) vs Baselines
- **Status:** ✓ PRODUCED
- **Data source:** Distributed candidate final checkpoint (5000) vs all baseline policies
- **Chart type:** Bar chart or line plot
- **X-axis:** Policy (shared-agent, distributed, fixed_local, fixed_horizontal, fixed_vertical, random_legal, capacity_split)
- **Y-axis:** Average latency in time slots
- **Results:**
  - Shared-agent: 14.58 slots
  - Distributed: 15.14 slots
  - Fixed_local: 15.12 slots
  - Capacity_split: 15.02 slots
  - Random_legal: 15.16 slots
- **Generated:** From baseline-and-oracle-metrics.json final rows

### Sub-figure 10b: Drop Ratio vs Baselines
- **Status:** ✓ PRODUCED
- **Data source:** Same baseline policies
- **Chart type:** Bar chart
- **X-axis:** Policy
- **Y-axis:** Drop ratio (0–1)
- **Results:**
  - Shared-agent: 0.655
  - Distributed: 0.648
  - Fixed_local: 0.663
  - Capacity_split: 0.651
  - Random_legal: 0.666
- **Generated:** From baseline-and-oracle-metrics.json final rows

### Overall Status
**COMPLETE** — Both panels produced from run data; no additional work required.

---

## Figure 11: LSTM Ablation (Delay with/without Recurrence)

**Purpose:** Isolate the contribution of the LSTM layer to delay reduction.

### Sub-figure 11a: Delay with LSTM (Recurrent Agent)
- **Status:** ✓ PRODUCED
- **Data source:** Distributed candidate full campaign
- **Architecture:** LSTM 1×20 hidden + 3×1024 dense layers
- **Chart type:** Line plot over training checkpoints
- **X-axis:** Training episodes (250, 500, 1000, ..., 5000)
- **Y-axis:** Average latency in slots
- **Results:** Improves from ~16 slots (early) to 15.14 slots (final)
- **Generated:** From distributed-candidate-metrics.json checkpoint-by-checkpoint

### Sub-figure 11b (placeholder): Delay without LSTM (Feedforward Agent)
- **Status:** ✗ MISSING
- **Required:** Same 5000-episode training without LSTM (pure feedforward network)
- **Architecture:** 3×1024 dense layers only (no recurrence)
- **Purpose:** Show difference in convergence and final performance
- **Expected:** Typically slower convergence and higher latency, but exact magnitude unknown
- **Effort:** Requires one additional full 5000-episode training run with the LSTM layer removed

### Overall Status
**PARTIAL** — With-LSTM real data exists; without-LSTM ablation requires retraining.

---

## Summary by Effort

| Gap | Type | Effort | Priority |
|-----|------|--------|----------|
| Fig 8 sweep (lr/γ) | Hyperparameter sweep | 5–10 runs | Optional; provides robustness data |
| Fig 9 sweeps (system params) | System configuration sweep | 20–40 runs | Optional; provides sensitivity data |
| Fig 11 ablation (no LSTM) | Architecture ablation | 1 run | Optional; provides ablation insight |

**Total optional effort:** ~26–51 additional full 5000-episode training campaigns (if all sweeps run).

---

## Recommendation

- **Figures 8, 9, 11:** Mark as "Partial – Single Configuration" in the manuscript
  - Real curves are provided for the primary configuration
  - Sweep and ablation panels can be marked as future work or requested in reviews
- **Figure 10:** Fully complete; ready for publication as-is
- **Decision:** User approval required before running optional parameter sweeps or ablations

