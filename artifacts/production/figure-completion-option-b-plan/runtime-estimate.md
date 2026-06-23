# Option B Runtime Estimate

**Analysis Date:** 2026-06-23  
**Baseline Metric:** 1.077 hours per 5000-episode full training run  
**Status:** Planning only — actual runtimes may vary

---

## Baseline Calibration

**Historical data:** per-EA-distributed-baseline full campaign  
- Episodes: 5000
- Agents: 20 (distributed)
- Wall time: 3875.7 seconds = 1.077 hours
- System: MacOS, 8-core CPU (estimated)

---

## Figure 8: L-Shaped Hyperparameter Sweep

| Config | Type | Episodes | Per-Run Time | Notes |
|--------|------|----------|--------------|-------|
| fig8_lr_1e6_gamma099 | training | 5000 | 1.077 h | High LR; may converge faster or oscillate |
| fig8_lr_5e7_gamma099 | training | 5000 | 1.077 h | Mid-low LR; similar to baseline |
| fig8_lr_1e7_gamma099 | training | 5000 | 1.077 h | Low LR; may be slower |
| fig8_lr_7e7_gamma095 | training | 5000 | 1.077 h | Low gamma; myopic discounting |
| fig8_lr_7e7_gamma0995 | training | 5000 | 1.077 h | High gamma; long-term focus |
| **SUBTOTAL** | — | — | **5.4 hours** | 5 × 1.077 h |

**Variance estimate:** ±20% depending on machine load and network dynamics
- Worst case: 6.5 hours (if machine slow or network contention)
- Best case: 4.3 hours (if machine fast or early convergence)

**Sequential execution:** 5.4 hours total  
**Parallel execution (if 5 GPUs available):** ~1.2 hours (min time for longest run) + overhead

---

## Figure 9: System Parameter Sensitivity Evaluation

| Config | Type | Episodes | Per-Config Time | Notes |
|--------|------|----------|-----------------|-------|
| fig9_arrival_prob_02 | eval | 100 | 0.1 h | Low arrival probability (0.2) |
| fig9_arrival_prob_05 | eval | 100 | 0.1 h | Medium arrival probability (0.5) |
| fig9_arrival_prob_08 | eval | 100 | 0.1 h | High arrival probability (0.8) |
| fig9_agent_count_10 | eval | 100 | 0.1 h | Reduced agent team (10) |
| fig9_agent_count_20 | eval | 100 | 0.1 h | Baseline agent team (20) |
| fig9_agent_count_30 | eval | 100 | 0.1 h | Expanded agent team (30) |
| **SUBTOTAL** | — | — | **0.6 hours** | 6 × 0.1 h |

**Why so fast?** Evaluation-only (no training). Trained policy runs 100 episodes per config.

**Estimation basis:**
- One 5000-episode training: 1.077 hours
- One 100-episode evaluation: ~0.1 hours (18× smaller, ~0.06 hours raw + overhead)

**Variance estimate:** ±10% (low variance; evaluation is lightweight)
- Worst case: 0.7 hours
- Best case: 0.5 hours

**Sequential execution:** 0.6 hours total  
**Parallel execution (if 6 cores available):** ~0.15 hours (min time for one eval) + overhead

---

## Figure 10: Baseline Comparison

| Item | Status | Time | Notes |
|------|--------|------|-------|
| All 7 policies | COMPLETE | 0.0 h | No new work required |
| Reconciliation | VERIFIED | 0.0 h | Already delta=0.0 |
| **SUBTOTAL** | — | **0.0 hours** | No changes |

---

## Figure 11: No-LSTM Ablation

| Item | Type | Episodes | Time | Notes |
|------|------|----------|------|-------|
| fig11_no_lstm_ablation | training | 5000 | 1.077 h | Feedforward-only, identical hyperparams |
| **SUBTOTAL** | — | — | **1.077 hours** | 1 × 1.077 h |

**Variance estimate:** ±20% (same as Fig 8 training)
- Worst case: 1.3 hours
- Best case: 0.85 hours

**Sequential execution:** 1.077 hours total  
**Parallel execution (single run):** ~1.077 hours (no parallelization benefit)

---

## Total Runtime Summary

### Conservative Estimate (With Variance)

| Component | Nominal | Worst Case | Best Case |
|-----------|---------|-----------|-----------|
| Figure 8 sweep | 5.4 h | 6.5 h | 4.3 h |
| Figure 9 evals | 0.6 h | 0.7 h | 0.5 h |
| Figure 10 | 0.0 h | 0.0 h | 0.0 h |
| Figure 11 ablation | 1.077 h | 1.3 h | 0.85 h |
| **TOTAL** | **7.1 h** | **8.5 h** | **5.65 h** |

### Execution Scenarios

#### Scenario A: Sequential Execution (Recommended)
- Run Fig 8 sweep (5.4 h)
- Run Fig 9 evals (0.6 h)
- Run Fig 11 ablation (1.077 h)
- **Total wall time:** 7.1 hours (~1 wall day)

**Pros:**
- Simple to monitor
- Clear bottleneck identification
- Easy to debug if something fails

**Cons:**
- Takes longest total time
- Low machine utilization

#### Scenario B: Partially Parallel
- Run Fig 8 sweep (5 runs in parallel, if 5 GPUs): ~1.2 h
- While Fig 8 running, run Fig 9 evals in parallel: ~0.15 h (overlaps)
- Run Fig 11 ablation sequentially: ~1.077 h
- **Total wall time:** ~2.4 hours (~1/3 of sequential)

**Pros:**
- Much faster overall
- Better resource utilization

**Cons:**
- Requires multiple GPUs
- More complex to monitor
- Harder to debug race conditions

#### Scenario C: Full Parallelization
- All 5 Fig 8 + 6 Fig 9 + 1 Fig 11 = 12 jobs in parallel
- **Total wall time:** ~1.2 hours (largest job)

**Pros:**
- Fastest possible

**Cons:**
- Requires 12 GPUs
- Very hard to debug
- Likely overkill for this analysis

**Recommendation:** **Scenario A (sequential)**. Simple, clear, 7 hours is acceptable, and no parallelization infrastructure needed.

---

## Overhead Factors

### Per-Run Overhead
- Agent initialization: ~30 sec per run
- Checkpoint save/load: ~10 sec per checkpoint
- Metric aggregation: ~30 sec per run
- File I/O: ~30 sec per run

**Total overhead per 5000-episode run:** ~2 minutes  
**Already included in 1.077 h baseline**

### Evaluation Overhead
- Policy loading: ~10 sec
- Environment setup: ~5 sec per episode batch
- Metric aggregation: ~10 sec
- File I/O: ~5 sec

**Total overhead per 100-episode eval:** ~30 sec  
**Already estimated in 0.1 h per config**

---

## Machine Assumptions

**Baseline calibration machine:**
- CPU: 8-core (Apple Silicon or Intel equivalent)
- RAM: 8–16 GB
- GPU: None (CPU-only training)
- I/O: SSD

**If running on slower machine:**
- Add 20–50% to all estimates

**If running on faster machine:**
- Subtract 10–30% from all estimates

---

## Smoke Test Time Estimates

| Test | Episodes/Configs | Expected Time | Purpose |
|------|------------------|----------------|---------|
| Fig 8 smoke | 50 episodes | <5 min | Verify training loop works |
| Fig 9 smoke | 10 eval episodes | <2 min | Verify evaluation works |
| Fig 11 smoke | 50 episodes | <5 min | Verify no-LSTM agent initializes |
| All smoke tests | — | <15 min | Before committing to full runs |

**Recommendation:** Run all smoke tests before any full runs.

---

## Checkpoint Save/Load Overhead

Figure 8 and 11 save checkpoints at 11 points each:

```
Episodes: 250, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000
```

**Per-checkpoint cost:**
- Save agent weights: ~5 sec
- Save metrics to JSON: ~2 sec
- Evaluate on 100 episodes: ~30 sec
- **Total per checkpoint:** ~37 sec

**Per run (11 checkpoints):**
- Checkpoint overhead: 11 × 37 sec = 407 sec ≈ 6.8 min

**Included in 1.077 h baseline:** Yes

---

## Network I/O (If Using Remote Storage)

If results are saved to network storage:

**Add 10–30% overhead** for remote writes:
- Figure 8 sweep: +0.5–1.6 hours
- Figure 9 evals: +0.06–0.2 hours
- Figure 11 ablation: +0.1–0.3 hours

**Assumption:** All storage is local SSD (no remote overhead)

---

## Contingency Plan

### If Running Behind Schedule

**Option 1: Reduce Fig 8 sweep**
- Skip gamma=0.995 config (one of five)
- Saves 1.077 hours
- Still captures most sensitivity

**Option 2: Reduce Fig 9 evals**
- Keep only arrival_probability sweep (3 configs, 0.3 h)
- Drop agent_count sweep
- Saves 0.3 hours

**Option 3: Skip Fig 11 ablation (not recommended)**
- Saves 1.077 hours
- But loses important LSTM ablation result

### If Need Results Faster

Run Scenario B (partially parallel) with 2–3 GPUs:
- Figure 8: Run 2–3 configs in parallel (reduces sweep time to 3–5 h)
- Figure 9: Run 2–3 evals in parallel (reduces eval time to 0.2–0.3 h)
- Figure 11: Run sequentially (1.077 h)
- **Total:** ~5–6 hours instead of 7

---

## Expected Completion Timeline

### Sequential Execution (Recommended)

| Phase | Start | Duration | End |
|-------|-------|----------|-----|
| Smoke tests | 0:00 | 0:15 | 0:15 |
| Fig 8 sweep | 0:15 | 5:24 | 5:39 |
| Fig 9 evals | 5:39 | 0:36 | 6:15 |
| Fig 11 ablation | 6:15 | 1:05 | 7:20 |
| Results aggregation | 7:20 | 0:15 | 7:35 |

**Estimated completion:** 7.5 hours from start

### Recommended Execution Time

- **Start:** Morning (8:00 AM)
- **Smoke tests:** 8:00–8:15 AM (15 min)
- **Fig 8 sweep:** 8:15 AM–1:39 PM (5.4 h)
- **Fig 9 evals:** 1:39–2:15 PM (0.6 h)
- **Fig 11 ablation:** 2:15–3:20 PM (1.077 h)
- **Results ready:** ~3:30 PM same day

---

## Summary

**Option B is designed for pragmatic completion in <8 wall hours.**

| Metric | Value |
|--------|-------|
| Total training runs | 6 (all 5000 episodes) |
| Total evaluation configs | 6 (all 100 episodes) |
| Nominal wall time | 7.1 hours |
| 90% confidence interval | 5.6–8.5 hours |
| Worst-case assumption | Slow machine, network overhead |
| Smoke test time | <15 minutes |
| Can complete in one day? | Yes (sequential) |
| Ready for submission after? | Yes (figures complete) |

---

**Status:** Plan is feasible within stated time bounds.
