# Remaining Gaps & Future Work

**Date:** 2026-06-23  
**Status:** Baseline simulations complete; optional work pending user decision

---

## Overview

The baseline campaigns (shared-agent and per-EA distributed) are complete with full 5000-episode training, reconciliation, and primary figures. The following work items remain optional and require explicit user approval.

---

## 1. Paper Figure Gaps

### Figure 8: Hyperparameter Sweep (lr/γ sensitivity)

**Current:** Single-config curves (lr=7e-7, γ=0.99)  
**Missing:** Multi-config sweep showing sensitivity to learning rate and discount factor

**Why:** Reviewers often ask "how robust is your training to hyperparameter choices?" Sweep curves demonstrate that the learned behavior is not a fluke of one configuration.

**Effort:** 5–10 additional full 5000-episode training runs
- lr values: [1e-6, 5e-7, 7e-7, 1e-7] (4 configs)
- γ values: [0.95, 0.99, 0.995] (3 configs)
- Total: ~12 combos, but prunable to ~5–10 most informative

**Wall time:** ~50–100 wall hours

**Output:** 2D heatmap or multi-line plot showing accumulated reward and reward/task across lr/γ pairs

**Priority:** Optional; can mark sweep panels as "future work" in manuscript

---

### Figure 9: System Parameter Sweeps (environment sensitivity)

**Current:** Real action distribution from single fixed environment

**Missing:** Sensitivity curves across system configurations:
- Task arrival probability (distribution of incoming tasks)
- DRL agent count (size of distributed system)
- CPU capacity per agent (resource availability)
- Offloading data rate (bandwidth cost)

**Why:** Demonstrates that learned routing is robust across different deployment scenarios.

**Effort:** 20–40 additional training runs
- Arrival probability: [0.2, 0.4, 0.6, 0.8] (4 configs)
- Agent count: [5, 10, 15, 20, 25] (5 configs)
- CPU capacity: [0.5×, 1.0×, 2.0×] (3 configs)
- Offloading rate: [0.2×, 1.0×, 5.0×] (3 configs)
- Cartesian product: ~15–20 distinct runs (not all combos needed)

**Wall time:** ~200–400 wall hours

**Output:** 4–5 sensitivity curves or heatmaps

**Priority:** Optional; important for generalization claims but significant effort

---

### Figure 11: LSTM Ablation (architecture contribution)

**Current:** With-LSTM delay curves from distributed full campaign

**Missing:** Without-LSTM (feedforward) variant showing recurrence contribution

**Why:** Shows that LSTM is necessary and beneficial for delay reduction, not just coincidental.

**Effort:** 1 additional full 5000-episode training run
- Remove LSTM layer, keep 3×1024 dense
- Same training procedure, 5000 episodes
- Same evaluation

**Wall time:** ~4–8 wall hours

**Output:** Side-by-side delay curves (with/without LSTM)

**Priority:** Optional; lighter effort than sweeps; useful for ablation completeness

---

## 2. Diagnostic Work (Not Required for Paper)

### Per-EA Q-Value Analysis
- Deep-dive into per-agent value function distributions
- Temporal evolution of Q-values during training
- Convergence rate per agent
- Divergence between agents

**Effort:** Low (post-hoc analysis of checkpoints)  
**Wall time:** 2–4 hours  
**Output:** Optional diagnostic figures and statistics  
**Priority:** Very optional; nice to have for appendix only

---

### Per-EA Action Preference Heatmap
- Matrix showing which agent preferred which action at each checkpoint
- Visualizes per-agent differentiation and evolution

**Effort:** Very low (post-hoc analysis)  
**Wall time:** 1 hour  
**Output:** Heatmap figure  
**Priority:** Very optional; appendix material

---

## 3. Proposed Method (NOT STARTED)

**Status:** Out of scope for baseline report  
**Implementation:** Pending user approval  
**Scope:** Separate branch (do not mix with baseline)

**Expected work items:**
- Implement deadline-aware routing logic
- Add reward shaping for deadline incentives
- Integrate EDF/LSTF queue discipline (optional)
- Train 5000-episode campaign with proposed method
- Evaluate against same baselines
- Generate comparison figures (proposed vs baselines)

**Estimated effort:** 20–40 wall hours for implementation + 8–16 hours for training/evaluation

**Approval required before starting:** Yes, explicit user decision needed

---

## 4. Optional Improvements to Baselines

### Per-EA Hyperparameter Tuning
If per-EA distributed underperformance is surprising, could try:
- Tuning lr per agent
- Adjusting target_sync_frequency per agent
- Larger replay buffer sizes

**Effort:** 5–10 additional runs  
**Priority:** Optional; only if reviewer/user questions why per-EA underperformed

---

## Summary of Effort

| Work Item | Type | Runs | Wall Hours | Priority |
|-----------|------|------|-----------|----------|
| Fig 8 lr/γ sweep | Hyperparameter | 10 | 50–100 | Optional |
| Fig 9 system sweeps | System configs | 40 | 200–400 | Optional |
| Fig 11 LSTM ablation | Architecture | 1 | 4–8 | Optional |
| Q-value diagnostics | Analysis | 0 | 2–4 | Very optional |
| Action preference heatmap | Analysis | 0 | 1 | Very optional |
| Per-EA tuning | Tuning | 10 | 50–100 | Optional (if needed) |
| **Proposed method** | **Implementation** | **~5** | **20–40** | **Requires approval** |

---

## Timeline Recommendation

### Immediate (Now)
- ✓ Baseline campaigns complete
- ✓ Figures 1–11 generated (partial for 8, 9, 11)
- ✓ Claim safety verified
- ✗ Proposed method: NOT started

### Phase 1 (If Approved)
- Run lightweight optional work (LSTM ablation, diagnostics) — 1–2 days
- User reviews manuscript draft with partial figures

### Phase 2 (If Approved)
- Run parameter sweeps if reviewer feedback requests — 7–14 days
- Generate additional figures

### Phase 3 (If Approved)
- Begin proposed method on separate branch
- 3–5 days for implementation + 1–2 days for training/evaluation

---

## Recommendation for Manuscript Submission

**For Figures 8, 9, 11:**
- Include single-config real data (actual curves)
- Mark sweep/ablation panels with caption: "(requires additional hyperparameter sweep; future work)"
- Honest and transparent about what was/wasn't done

**For Figure 10:**
- Submit as complete (both delay and drop ratio vs baselines)

**For Baselines:**
- Present both shared-agent and per-EA distributed results
- Discuss why per-EA underperformed shared (honest analysis in discussion)
- No superiority claims anywhere

**For Proposed Method:**
- Only include after it's completed, trained, and evaluated
- Do not mix proposed-method results with baseline artifact

---

## Decision Points for User

1. **Before manuscript submission:**
   - Accept partial figures (8, 9, 11 single-config only)?
   - Or delay submission to run sweeps/ablations?

2. **Before next phase:**
   - Approve per-EA hyperparameter tuning (if curiosity about underperformance)?
   - Approve proposed-method implementation?

3. **Timeline:**
   - Baseline ready for review now
   - Optional work can be added incrementally
   - Proposed method is fully separate

