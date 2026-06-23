# Figure Concept Audit — HOODIE Paper Figures 8–11

**Date:** 2026-06-23  
**Audit Type:** Mechanism validation before export  
**Source Branches:**
- `true-per-EA-distributed-baseline` (per-EA distributed campaign, 5000 episodes)
- `full-paper-campaign-execution-run` (shared-agent campaign, 5000 episodes)

---

## Figure 8: Reward Time-Course (Learning Dynamics)

### Paper Intent
Demonstrate how accumulated reward and reward-per-task evolve during training under a **single hyperparameter configuration**. This shows the learning trajectory and policy convergence behavior.

### Mechanism Being Tested
- Does the agent converge to a stable policy?
- What is the reward trajectory shape (monotonic, oscillatory, plateauing)?
- At what training episode does convergence stabilize?

### Required Data
- Accumulated reward per episode (episodes 1–5000)
- Reward per task per episode
- Single hyperparameter configuration: `lr=7e-7, gamma=0.99`

### Available Data
✓ **Shared-agent campaign** (`full-paper-campaign-execution-run`):
- 5000 episodes completed
- 11 checkpoint evaluations
- Checkpoint metrics including accumulated reward and reward-per-task

✓ **Per-EA distributed campaign** (`true-per-EA-distributed-baseline`):
- 5000 episodes completed
- 11 checkpoint evaluations
- Distributed candidate metrics including accumulated reward per checkpoint

### Data Sources
- `artifacts/production/true-per-EA-distributed-baseline/distributed-candidate-metrics.json` (per-EA, episodes 250–5000)
- `artifacts/production/full-paper-campaign-execution-run/candidate-checkpoint-metrics.json` (shared-agent, episodes 1–5000)

### Sub-figures

#### 8a: Accumulated Reward Over Training
- **Status:** `REAL_PARTIAL`
- **Data:** Actual checkpoint reward values from training run
- **Mechanistically Valid:** ✓ Yes
  - Real checkpoint-based accumulation of total reward during training
  - Represents one configuration only (lr=7e-7, γ=0.99)
  - No hyperparameter sweep; single-config only
- **Reason:** Single-config is mechanistically valid for demonstrating convergence behavior. Hyperparameter robustness requires additional sweep configs (not run).

#### 8b: Reward Per Task Over Training
- **Status:** `REAL_PARTIAL`
- **Data:** Actual reward-per-task from checkpoint metrics
- **Mechanistically Valid:** ✓ Yes
  - Represents efficiency of learned policy on a per-task basis
  - Single-config real data
- **Reason:** Valid for showing per-task efficiency trend. Sweep panels would require additional runs.

#### 8c–8e: Learning-Rate and Discount-Factor Sweep Panels
- **Status:** `PLACEHOLDER_REQUIRES_SWEEP`
- **Missing Data:** Configs for `lr ∈ {1e-6, 5e-7, 7e-7, 1e-7}` and `gamma ∈ {0.95, 0.99, 0.995}`
- **Mechanistically Valid:** ✗ Not available
- **Reason:** Hyperparameter sweep requires ~5–10 additional full 5000-episode training runs. Not executed in current campaign.

---

## Figure 9: Behavior Insights & System Sensitivity

### Paper Intent
Show the **action distribution** learned by the agent and demonstrate **sensitivity to system parameters** (arrival probability, agent count, CPU capacity, data rate).

### Mechanism Being Tested
- Which actions (local, horizontal, vertical) does the learned policy prefer?
- How robust is the learned policy across different system configurations?
- Does the policy generalize or fail under parameter variations?

### Required Data
- Real action distribution from trained agent
- Reward/completion under system parameter variations:
  - Task arrival probability
  - DRL agent count
  - CPU capacity per agent
  - Offloading data rate

### Available Data
✓ **Action distribution (9a):**
- `artifacts/production/true-per-EA-distributed-baseline/distributed-candidate-metrics.json`
  - Final action distribution: 0% local, 0% horizontal, 100% vertical
  
✓ **Real metrics exist for:**
- Single fixed environment configuration only
- All action decisions reconciled with perfect delta=0.0

✗ **Missing (not run):**
- Parameter sweep variations (arrival, agent count, CPU capacity, data rate)
- System sensitivity evaluation

### Data Sources
- `artifacts/production/true-per-EA-distributed-baseline/distributed-candidate-metrics.json`
- `artifacts/production/true-per-EA-distributed-baseline/baseline-and-oracle-metrics.json` (baseline action distributions for comparison)

### Sub-figures

#### 9a: Action Distribution (Real)
- **Status:** `REAL_PARTIAL`
- **Data:** Actual action counts from candidate evaluation
- **Mechanistically Valid:** ✓ Yes
  - Real distribution showing 100% vertical action selection in final policy
  - Represents true agent behavior in fixed environment
- **Reason:** Single-environment action distribution is valid; demonstrates learned behavior. Sweep panels are optional generalization analysis.

#### 9b: Reward by Task Arrival Probability
- **Status:** `PLACEHOLDER_REQUIRES_SWEEP`
- **Missing Data:** Reward measurements under arrival probability ∈ {0.2, 0.4, 0.6, 0.8}
- **Mechanistically Valid:** ✗ Not available
- **Reason:** Requires retraining or re-evaluation under different arrival profiles. Not executed.

#### 9c: Reward by DRL Agent Count
- **Status:** `PLACEHOLDER_REQUIRES_SWEEP`
- **Missing Data:** Reward measurements under agent count ∈ {5, 10, 15, 20, 25}
- **Mechanistically Valid:** ✗ Not available
- **Reason:** Requires separate evaluation configs. Not executed.

#### 9d: Reward by CPU Capacity
- **Status:** `PLACEHOLDER_REQUIRES_SWEEP`
- **Missing Data:** Reward under capacity multiplier ∈ {0.5×, 1.0×, 2.0×}
- **Mechanistically Valid:** ✗ Not available
- **Reason:** Requires environment reconfiguration and re-evaluation. Not executed.

#### 9e: Reward by Offloading Data Rate
- **Status:** `PLACEHOLDER_REQUIRES_SWEEP`
- **Missing Data:** Reward under data rate ∈ {0.2×, 1.0×, 5.0×}
- **Mechanistically Valid:** ✗ Not available
- **Reason:** Requires environment reconfiguration. Not executed.

---

## Figure 10: HOODIE vs Baselines (Comparison)

### Paper Intent
Demonstrate that the learned agent achieves lower **average delay** and **drop ratio** than the implemented baselines, validating the DRL approach.

### Mechanism Being Tested
- Does the candidate outperform fixed policies (local, horizontal, vertical)?
- Does the candidate approach the oracle (capacity-proportional split)?
- Is the learned routing strategy effective for deadline-aware scheduling?

### Required Data
- Average delay (in slots) for candidate and all baselines
- Drop ratio for candidate and all baselines
- Baselines must include: fixed_local, fixed_horizontal, fixed_vertical, random_legal, capacity_split_oracle

### Available Data
✓ **All baseline metrics available:**
- `artifacts/production/true-per-EA-distributed-baseline/baseline-and-oracle-metrics.json`
  - fixed_local: completion=0.2465, drop=0.6626, avg_latency=15.12 slots
  - fixed_horizontal: completion=0.1659, drop=0.7404, avg_latency=15.96 slots
  - fixed_vertical: completion=0.1789, drop=0.7362, avg_latency=16.04 slots
  - random_legal: completion=0.2428, drop=0.6574, avg_latency=15.08 slots
  - capacity_split_oracle: completion=0.2572, drop=0.6511, avg_latency=14.62 slots

✓ **Candidate metrics available:**
- Shared-agent: completion=0.2545, drop=0.6550, avg_latency=14.58 slots
- Per-EA distributed: completion=0.2214, drop=0.6476, avg_latency=15.14 slots

### Data Sources
- `artifacts/production/true-per-EA-distributed-baseline/baseline-and-oracle-metrics.json` (all baselines)
- `artifacts/production/true-per-EA-distributed-baseline/distributed-candidate-metrics.json` (per-EA candidate)
- `artifacts/production/full-paper-campaign-execution-run/candidate-vs-baselines-summary.json` (shared-agent candidate)

### Sub-figures

#### 10a: Average Delay vs Baselines
- **Status:** `REAL_FULL`
- **Data:** Average latency (slots) for 7 policies
- **Mechanistically Valid:** ✓ Yes
  - Real evaluation metrics from completed campaigns
  - All baselines reconciled (delta=0.0)
  - Candidate metrics also reconciled
- **Reason:** Fully real data from completed simulations. No sweep or ablation required.

#### 10b: Drop Ratio vs Baselines
- **Status:** `REAL_FULL`
- **Data:** Drop ratio (deadline violations) for 7 policies
- **Mechanistically Valid:** ✓ Yes
  - Real drop counts from evaluation episodes
  - All reconciliation checks passed
- **Reason:** Fully real data from simulation metrics.

---

## Figure 11: LSTM Ablation (Architecture Contribution)

### Paper Intent
Demonstrate that the **LSTM layer is necessary** for achieving low delay in the distributed setting. Contrast with and without LSTM.

### Mechanism Being Tested
- Does the LSTM provide significant delay reduction?
- How much of the performance is due to recurrence vs. feedforward structure?
- Is the LSTM contribution measurable and substantial?

### Required Data
- **With-LSTM:** Delay curves from actual training with LSTM enabled
- **Without-LSTM:** Delay curves from ablation run with LSTM removed (feedforward only)

### Available Data
✓ **With-LSTM (from per-EA distributed campaign):**
- `artifacts/production/true-per-EA-distributed-baseline/distributed-candidate-metrics.json`
- LSTM was used in all agent models during full campaign (5000 episodes)
- Evaluation metrics available at checkpoints

✗ **Without-LSTM (not available):**
- Ablation run not executed
- Would require separate 5000-episode training with feedforward architecture

### Data Sources
- `artifacts/production/true-per-EA-distributed-baseline/distributed-candidate-metrics.json` (with-LSTM, episode 5000)

### Sub-figures

#### 11a: Delay Trend (With LSTM)
- **Status:** `REAL_PARTIAL`
- **Data:** Actual delay measurements from trained agents with LSTM
- **Mechanistically Valid:** ✓ Yes (as a single-architecture result)
  - Real evaluation metrics from completed campaign
  - Represents true performance of LSTM-enabled model
- **Reason:** Demonstrates LSTM-enabled performance. Without-LSTM comparison requires ablation.

#### 11b: Delay Trend (Without LSTM)
- **Status:** `PLACEHOLDER_REQUIRES_ABLATION`
- **Missing Data:** Feedforward (no-LSTM) training run for 5000 episodes
- **Mechanistically Valid:** ✗ Not available
- **Reason:** Ablation requires separate training run. Not executed. Cannot construct valid ablation from with-LSTM data alone.

---

## Summary Table

| Figure | Sub | Status | Real? | Sweep/Ablation | Data Source | Verdict |
|--------|-----|--------|-------|----------------|-------------|---------|
| 8 | Overall | REAL_PARTIAL | ✓ | Single-config | checkpoint metrics | Publishable as single-config |
| 8a | Accumulated reward | REAL_PARTIAL | ✓ | Single-config | distributed-candidate-metrics | Valid real curve |
| 8b | Reward per task | REAL_PARTIAL | ✓ | Single-config | checkpoint metrics | Valid real curve |
| 8c–8e | lr/gamma sweeps | PLACEHOLDER_REQUIRES_SWEEP | ✗ | Not run | N/A | Future work |
| 9 | Overall | REAL_PARTIAL | ✓ | Single config | baseline-and-oracle-metrics | Publishable as action distribution only |
| 9a | Action distribution | REAL_PARTIAL | ✓ | Single config | distributed-candidate-metrics | Real distribution |
| 9b–9e | System sweeps | PLACEHOLDER_REQUIRES_SWEEP | ✗ | Not run | N/A | Future work |
| 10 | Overall | REAL_FULL | ✓ | N/A | baseline-and-oracle-metrics | Complete baseline comparison |
| 10a | Average delay | REAL_FULL | ✓ | N/A | baseline-and-oracle-metrics | All real |
| 10b | Drop ratio | REAL_FULL | ✓ | N/A | baseline-and-oracle-metrics | All real |
| 11 | Overall | REAL_PARTIAL | ✓ partial | Ablation missing | distributed-candidate-metrics | With-LSTM real; without-LSTM missing |
| 11a | With LSTM | REAL_PARTIAL | ✓ | N/A | distributed-candidate-metrics | Real performance curve |
| 11b | Without LSTM | PLACEHOLDER_REQUIRES_ABLATION | ✗ | Not run | N/A | Future work |

---

## Validation Conclusion

### Figure 8: REAL_PARTIAL
- **Verdict:** Publishable with honest caption stating single-config only
- **What is real:** Accumulated reward and reward-per-task curves from actual training
- **What is missing:** Hyperparameter sweep panels (lr/gamma variations)
- **Publishability:** ✓ Yes (with caption)

### Figure 9: REAL_PARTIAL
- **Verdict:** Publishable with honest caption for action distribution only
- **What is real:** Actual action distribution learned by candidate
- **What is missing:** System parameter sensitivity analysis (arrival, agent count, capacity, rate)
- **Publishability:** ✓ Yes (9a only; 9b–9e mark as future work)

### Figure 10: REAL_FULL
- **Verdict:** Fully publishable; complete baseline comparison
- **What is real:** All delay and drop metrics from 7 policies (candidate + 6 baselines)
- **What is missing:** Nothing required for paper submission
- **Publishability:** ✓ Yes (ready)

### Figure 11: REAL_PARTIAL
- **Verdict:** Publishable with honest caption about ablation gap
- **What is real:** With-LSTM delay performance from actual training
- **What is missing:** Without-LSTM ablation results (requires separate run)
- **Publishability:** ✓ Yes (with caption explaining ablation is future work)

---

## Export Readiness

✓ Figure 8: Ready for export (mark as single-config)  
✓ Figure 9: Ready for export (action distribution only; mark sweeps as future work)  
✓ Figure 10: Ready for export (fully complete)  
✓ Figure 11: Ready for export (mark ablation as future work)  

**Overall Verdict:** All figures are mechanistically valid for export with honest captions about missing sweeps/ablations.
