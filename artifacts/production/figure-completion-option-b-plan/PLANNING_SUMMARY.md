# Option B Planning Complete — Summary

**Date:** 2026-06-23  
**Status:** ✓ Planning complete, ready for approval  
**Approval Status:** 🔒 BLOCKED — Awaiting explicit user approval  

---

## What Has Been Created

A complete, pragmatic plan for completing HOODIE paper Figures 8, 9, 10, and 11 with minimum compute overhead.

### Documents Created (9 files, 2601 lines)

| Document | Lines | Purpose |
|----------|-------|---------|
| option-b-run-matrix.md | 208 | High-level overview of all runs and timing |
| option-b-run-matrix.json | 203 | Structured matrix for programmatic access |
| figure-8-lshape-sweep-plan.md | 295 | Detailed spec for 5 learning-rate/gamma runs |
| figure-9-evaluation-sweep-plan.md | 350 | Detailed spec for 6 system-parameter evals (no training) |
| figure-11-no-lstm-ablation-plan.md | 300 | Detailed spec for 1 feedforward-only ablation run |
| execution-commands.md | 406 | Exact bash commands for all smoke and full runs |
| runtime-estimate.md | 307 | Detailed timing analysis and scenarios |
| approval-required-before-full-run.md | 311 | Approval checklist and safety gates |
| claim-safety.json | 221 | Formal safety claims and verification checklist |

**Total planning investment:** ~3000 lines of documentation  
**Investment as code:** ~50 lines (new DistributedDDQNAgent_NoLSTM class)

---

## What Option B Proposes

### Figure 8: Learning Dynamics
- **Current:** 1 baseline config (lr=7e-7, gamma=0.99)
- **Add:** 5 new configs (L-shaped sweep)
- **Time:** 5.4 hours (5 × 1.077 h per run)
- **New training:** 5 full 5000-episode runs
- **Status on completion:** REAL_PARTIAL → more robust demonstration of convergence across hyperparameter space

### Figure 9: Behavior & Robustness
- **Current:** Action distribution 9a (real)
- **Add:** 6 evaluation configs (arrival probability + agent count)
- **Time:** 0.6 hours (6 × 0.1 h per eval)
- **New training:** None (uses trained baseline agent; evaluation-only)
- **Status on completion:** REAL_PARTIAL → evaluates learned policy robustness

### Figure 10: Baseline Comparison
- **Current:** All 7 policies complete
- **Add:** Nothing
- **Time:** 0.0 hours
- **Status:** REAL_FULL → no changes needed

### Figure 11: LSTM Ablation
- **Current:** With-LSTM performance (real)
- **Add:** Without-LSTM ablation (feedforward-only)
- **Time:** 1.077 hours (1 × 1.077 h)
- **New training:** 1 full 5000-episode run (new agent class)
- **Status on completion:** REAL_PARTIAL → quantifies LSTM contribution

---

## Total Investment

| Metric | Value | Notes |
|--------|-------|-------|
| New training runs | 6 | Figures 8 (5) + 11 (1) |
| New evaluation configs | 6 | Figure 9 only (no training) |
| Wall time estimate | 7.1 hours | Worst case: 8.5 hours; best case: 5.6 hours |
| Worst case (with overhead) | ~1 wall day | Can complete in single work day |
| Code additions | ~50 lines | Only new feedforward agent class |
| Code modifications | 0 | No changes to trainers/environment/reward |

---

## Safety Gates (All Active)

✓ **Training execution:** LOCKED until `APPROVE_OPTION_B_FIG8_SWEEP=1` and `APPROVE_OPTION_B_FIG11_ABLATION=1`  
✓ **Evaluation execution:** LOCKED until `APPROVE_OPTION_B_FIG9_EVAL=1`  
✓ **Code changes:** LOCKED except new agent class file  
✓ **Semantics protection:** All reward/environment/metric definitions locked to baseline  

---

## What Cannot Happen (Protected)

- ✗ Proposed method implementation
- ✗ Reward function changes
- ✗ Environment topology changes
- ✗ Metric definition changes
- ✗ Trainer logic modifications
- ✗ New sweeps beyond Option B scope

---

## What Will Happen (If Approved)

1. **Smoke tests** (<15 min)
   - 50-episode test for Fig 8 config
   - 10-eval test for Fig 9 config
   - 50-episode test for Fig 11 config
   - Verify all work, delta=0.0, no crashes

2. **Full runs** (~7.1 hours)
   - Figure 8: 5 full training runs (5.4 h)
   - Figure 9: 6 evaluation-only runs (0.6 h)
   - Figure 11: 1 full training run (1.077 h)

3. **Results aggregation**
   - Collect all checkpoint metrics
   - Verify all reconciliation deltas=0.0
   - Generate updated Figure 8, 9, 11 panels

4. **Commit & push**
   - Save all results to git
   - Create audit trail
   - Ready for paper submission

---

## How to Proceed

### Option A: Approve Everything (Simple)
```bash
export APPROVE_OPTION_B_FULL_RUN=1
bash artifacts/production/figure-completion-option-b-plan/run-all-smoke-tests.sh
# (If smoke passes)
bash artifacts/production/figure-completion-option-b-plan/run-all-full-jobs.sh
```

### Option B: Approve Selectively (Conservative)
```bash
# Just Fig 8 sweep
export APPROVE_OPTION_B_FIG8_SWEEP=1
python -m src.analysis.figure_8_sweep.run_all_lshape_configs ...

# Just Fig 11 ablation
export APPROVE_OPTION_B_FIG11_ABLATION=1
python -m src.analysis.figure_11_ablation.run_fig11_no_lstm_ablation_full ...

# Just Fig 9 evaluation
export APPROVE_OPTION_B_FIG9_EVAL=1
python -m src.analysis.figure_9_sensitivity.run_all_system_param_evals ...
```

### Option C: Deny and Modify (Flexible)
1. Edit `option-b-run-matrix.json`
2. Reduce scope (e.g., skip Fig 8 sweep)
3. Resubmit modified plan
4. Plan stays valid; no wasted effort

---

## Readiness Assessment

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Plan documents complete | ✓ | 9 files created, 2601 lines |
| Baseline data available | ✓ | per-EA-distributed-baseline exists and complete |
| Smoke tests ready | ✓ | Commands in execution-commands.md |
| Safety gates active | ✓ | All claim-safety gates locked |
| Code protected | ✓ | No modifications to trainers/harness |
| Approval process defined | ✓ | approval-required-before-full-run.md |
| Runtime estimated | ✓ | 7.1 hours ± variance documented |

**Verdict:** ✓ **READY FOR APPROVAL**

---

## Next Action

**User must explicitly approve one or more figures:**

Check approval-required-before-full-run.md, verify the checklist, then:

```bash
# Set approval environment variable
export APPROVE_OPTION_B_FIG8_SWEEP=1      # To run Fig 8 sweep
export APPROVE_OPTION_B_FIG9_EVAL=1       # To run Fig 9 evals
export APPROVE_OPTION_B_FIG11_ABLATION=1  # To run Fig 11 ablation
export APPROVE_OPTION_B_FULL_RUN=1        # To run all three

# Then run smoke tests first
APPROVE_OPTION_B_FULL_RUN=1 \
  python -m src.analysis.figure_8_sweep.run_fig8_lr_1e6_gamma099_smoke

# Once smoke passes, run full execution
APPROVE_OPTION_B_FULL_RUN=1 \
  python -m src.analysis.figure_8_sweep.run_all_lshape_configs ...
```

---

## Files Ready for Review

All planning documents are in:

```
artifacts/production/figure-completion-option-b-plan/
├── option-b-run-matrix.md              ← Start here (overview)
├── option-b-run-matrix.json            ← Machine-readable
├── figure-8-lshape-sweep-plan.md       ← Details for Fig 8
├── figure-9-evaluation-sweep-plan.md   ← Details for Fig 9
├── figure-11-no-lstm-ablation-plan.md  ← Details for Fig 11
├── execution-commands.md               ← Exact bash commands
├── runtime-estimate.md                 ← Timing analysis
├── approval-required-before-full-run.md ← Approval checklist
└── claim-safety.json                   ← Safety verification
```

---

## Questions for User

Before approval, consider:

1. **Timing:** Is 7.1 hours acceptable? (Worst case 8.5 h)
2. **Scope:** Is Option B (6 new training + 6 evals) the right scope?
3. **Figures:** Are all 4 figures ready once completed?
4. **Alternatives:** Would you prefer Option A (minimal) or Option C (full sweeps)?

---

**Status:** 🔒 Locked, awaiting explicit user approval  
**Ready for:** Smoke tests, full execution, or modifications  
**Plan is:** Durable, recoverable, and reversible (no destructive ops)

---

*All planning work is committed to `figure-completion-option-b-plan` branch. Main branch untouched. Results (when created) will be in dedicated folder. Easy to rollback or retry.*
