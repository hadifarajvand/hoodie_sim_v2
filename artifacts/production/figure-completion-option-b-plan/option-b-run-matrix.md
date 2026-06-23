# Option B Figure Completion Run Matrix

**Date:** 2026-06-23  
**Status:** Planning only — no execution yet  
**Approval Status:** PENDING_FULL_RUN_APPROVAL

---

## Overview

Option B is the **pragmatic approach** to completing Figures 8, 9, 10, and 11 for the HOODIE paper.

| Component | Status | Action | Time |
|-----------|--------|--------|------|
| Figure 8 | PARTIAL | Add 5 training runs (L-shaped hyperparameter sweep) | 5.4 h |
| Figure 9 | PARTIAL | Add 6 evaluation configs (no retraining) | 0.6 h |
| Figure 10 | COMPLETE | No changes | 0.0 h |
| Figure 11 | PARTIAL | Add 1 training run (no-LSTM ablation) | 1.1 h |
| **TOTAL** | — | **6 training + 6 evaluations** | **7.1 h** |

---

## Figure 8: Learning-Rate and Discount-Factor L-Shaped Sweep

### Goal
Demonstrate hyperparameter robustness without full factorial sweep.

### Existing Baseline
- **Config:** lr=7e-7, gamma=0.99
- **Status:** ✓ Already complete (per-EA-distributed-baseline)
- **Runtime:** 1.077 hours
- **Checkpoints:** 11 (episodes 250–5000)

### New Configs (5 runs)

| Run ID | Learning Rate | Gamma | Purpose | Episodes |
|--------|---------------|-------|---------|----------|
| fig8_lr_1e6_gamma099 | 1e-6 | 0.99 | High LR (10× baseline) | 5000 |
| fig8_lr_5e7_gamma099 | 5e-7 | 0.99 | Mid-low LR (0.7× baseline) | 5000 |
| fig8_lr_1e7_gamma099 | 1e-7 | 0.99 | Low LR (0.14× baseline) | 5000 |
| fig8_lr_7e7_gamma095 | 7e-7 | 0.95 | Low gamma (−0.04 from baseline) | 5000 |
| fig8_lr_7e7_gamma0995 | 7e-7 | 0.995 | High gamma (+0.005 from baseline) | 5000 |

**Total new configs:** 5  
**Estimated time:** 5.4 hours (5 × 1.077 h/run)  
**Expected output:** Reward curves showing sensitivity to lr and gamma

### L-Shape Rationale
- **Why L-shaped (not full factorial)?**
  - Full factorial: 4 lr × 3 gamma = 12 configs
  - L-shaped: 3 lr at fixed gamma + 3 gamma at fixed lr − 1 overlap = 5 configs
  - Reduces compute by ~58% while capturing main effects
  
- **Why these values?**
  - LR: 10×, 0.7×, 0.14× baseline (covers wide range)
  - Gamma: 0.95–0.995 (reasonable RL discount range)
  - Baseline 7e-7, 0.99 sits roughly in the middle

---

## Figure 9: System Parameter Sensitivity (Evaluation-Only)

### Goal
Test learned policy robustness across environment parameter variations without retraining.

### Key Point
**No new training runs.** Use the trained per-EA-distributed baseline agent and evaluate it under different environment configs.

### Existing Data
- **Trained policy:** per-EA-distributed-baseline (5000 episodes, 20 agents, LSTM-enabled)
- **Status:** ✓ Already complete and reconciled

### New Evaluation Configs (6 runs)

| Config ID | Parameter | Value | Episodes | Type | Purpose |
|-----------|-----------|-------|----------|------|---------|
| fig9_arrival_prob_02 | arrival_probability | 0.2 | 100 | eval | Low task arrival (scarce tasks) |
| fig9_arrival_prob_05 | arrival_probability | 0.5 | 100 | eval | Medium arrival (baseline) |
| fig9_arrival_prob_08 | arrival_probability | 0.8 | 100 | eval | High arrival (congested) |
| fig9_agent_count_10 | num_agents_drl | 10 | 100 | eval | Reduced team size |
| fig9_agent_count_20 | num_agents_drl | 20 | 100 | eval | Baseline team size |
| fig9_agent_count_30 | num_agents_drl | 30 | 100 | eval | Expanded team size |

**Total new evaluation configs:** 6  
**Estimated time:** 0.6 hours (6 × 0.1 h/config)  
**Expected output:** Reward, completion, drop-ratio, latency under parameter variations

### Evaluation-Only Process
1. Load trained policy from per-EA-distributed-baseline (5000-episode checkpoint)
2. For each config:
   - Set environment parameter (arrival_probability or num_agents_drl)
   - Run 100 evaluation episodes (no training)
   - Capture metrics: reward, completion_ratio, drop_ratio, latency
3. Aggregate results into sensitivity curves

### Can Existing Data Be Reused?
**Partial.** The controlled-mechanistic-sweeps artifact (artifacts/analysis/controlled-mechanistic-sweeps/) has some parameter sweep definitions, but:
- It was run with **random fixed_seed agent (seed=7)**, not the trained per-EA-distributed policy
- We need re-evaluation with **our specific trained policy** to get meaningful sensitivity
- **Decision:** Prepare new evaluation configs; do not rely on controlled-mechanistic-sweeps data

---

## Figure 10: HOODIE vs Baselines (No Changes)

### Status
✓ **COMPLETE**

### Existing Data
All 7 policies with complete metrics:
- **Candidates:** shared-agent (25.45% completion, 14.58 slots delay), per-EA distributed (22.14% completion, 15.14 slots)
- **Baselines:** fixed-local, fixed-horizontal, fixed-vertical, random-legal
- **Oracle:** capacity-split (25.72% completion, 14.62 slots)

### Reconciliation
- All policies: delta=0.0, terminal_coverage=100%

### Action
- No new training runs
- No config changes
- No evaluation runs
- **Time:** 0.0 hours

---

## Figure 11: LSTM Ablation Study

### Goal
Quantify the contribution of the LSTM layer to latency reduction.

### Existing Baseline (With LSTM)
- **Config:** per-EA-distributed-baseline
- **Architecture:** 3×1024 dense + 256 LSTM per agent
- **Status:** ✓ Already complete (5000 episodes)
- **Checkpoints:** 11 (episodes 250–5000)
- **Metrics:** avg_latency_slots at each checkpoint

### New Config (Without LSTM)

| Run ID | Architecture | Episodes | LR | Gamma | Purpose |
|--------|--------------|----------|----|----|---------|
| fig11_no_lstm_ablation | 3×1024 dense (feedforward only) | 5000 | 7e-7 | 0.99 | Ablation: isolate LSTM contribution |

**Total new configs:** 1  
**Estimated time:** 1.077 hours  
**Expected output:** Latency curves showing with-LSTM vs without-LSTM comparison

### Ablation Procedure
1. Create new agent architecture: remove LSTM layer, keep 3×1024 dense layers
2. Train for 5000 episodes with identical config as baseline (lr, gamma, replay, epsilon schedule)
3. Capture same 11 checkpoint evaluations (episodes 250–5000)
4. Compute latency metrics at each checkpoint
5. Plot alongside with-LSTM curve from baseline

### Why Full 5000 Episodes?
- Must match the baseline's training depth
- Checkpoints must align (250, 500, ..., 5000)
- Ablation is only meaningful with identical training conditions

---

## Safety Gates

All safety gates are **ACTIVE** and **LOCKED** until explicit approval.

### Gate 1: Training Execution Lock
- **Status:** LOCKED
- **Unlocks when:** User explicitly approves "run Option B" or specific run
- **Blocks:** Fig 8 full runs, Fig 11 ablation run

### Gate 2: Long Experiment Lock
- **Status:** LOCKED
- **Definition:** Any job > 1 hour
- **Unlocks when:** User approves specific long job

### Gate 3: Code Change Lock
- **Status:** LOCKED
- **Protected:** Reward logic, environment topology, metric definitions, proposed method implementation
- **Enforcement:** All configs use existing code; no architectural changes

### Gate 4: Semantics Lock
- **Status:** LOCKED
- **Protected:** All training parameters stay identical across variants (only hyperparams for Fig 8, only env params for Fig 9, only arch for Fig 11)

---

## Next Steps

1. **Review this plan** — Verify configs match your intent
2. **Approve Option B** — Explicitly authorize full runs
3. **Run smoke/dry checks** (lightweight, < 5 min each):
   - Fig 8 smoke: 50 episodes for one config
   - Fig 9 smoke: 10 evaluation episodes for one config
   - Fig 11 smoke: 50 episodes
4. **Execute full runs** — Once smoke passes and approval confirmed
5. **Collect results** — Aggregate metrics into figures

---

## Approval Checklist

- [ ] Plan reviewed
- [ ] Run matrix acceptable
- [ ] Time estimates reasonable
- [ ] Safety gates understood
- [ ] Ready to proceed with Option B

**Status:** Awaiting approval before execution.
