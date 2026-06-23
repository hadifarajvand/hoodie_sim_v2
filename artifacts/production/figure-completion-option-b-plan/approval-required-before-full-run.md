# Approval Required Before Full Run

**Status:** BLOCKED — All full training/evaluation runs require explicit user approval  
**Plan Date:** 2026-06-23  
**Type:** Safety gate documentation

---

## What Is Blocked

The following commands will **not execute** without explicit approval:

- ✗ `APPROVE_OPTION_B_FIG8_SWEEP=1 python -m src.analysis.figure_8_sweep.run_all_lshape_configs`
- ✗ `APPROVE_OPTION_B_FIG9_EVAL=1 python -m src.analysis.figure_9_sensitivity.run_all_system_param_evals`
- ✗ `APPROVE_OPTION_B_FIG11_ABLATION=1 python -m src.analysis.figure_11_ablation.run_fig11_no_lstm_ablation_full`

The environment variable `APPROVE_OPTION_B_*=1` must be set and explicitly verified by user action.

---

## What Is Allowed

The following commands execute without approval (lightweight):

- ✓ Smoke tests (<5 min each)
- ✓ Dry-run config validation (no training)
- ✓ Planning document review
- ✓ Execution command inspection

---

## Approval Checklist

Before any full run, user must confirm:

### Plan Understanding
- [ ] I have read option-b-run-matrix.md
- [ ] I understand Figure 8 requires 5 full training runs (5.4 hours)
- [ ] I understand Figure 9 requires 6 evaluation-only configs (0.6 hours)
- [ ] I understand Figure 10 requires no new work
- [ ] I understand Figure 11 requires 1 full training run (1.077 hours)
- [ ] Total estimated time is 7.1 hours

### Runtime Acceptance
- [ ] 7.1 hours wall time is acceptable for my use case
- [ ] Worst-case 8.5 hours is acceptable
- [ ] I can allocate a full work day for execution
- [ ] I understand smoke tests should run first (<15 min)

### Safety Gates Confirmation
- [ ] No reward logic will be changed
- [ ] No environment topology will be changed
- [ ] No metric definitions will be changed
- [ ] No proposed method implementation will occur
- [ ] Only hyperparameters (Fig 8) and environment params (Fig 9) and architecture (Fig 11) will vary
- [ ] All reconciliation profiles remain identical to baseline

### Code Changes Acceptance
- [ ] Figure 8: No code changes (configs only)
- [ ] Figure 9: No code changes (evaluation script only)
- [ ] Figure 10: No code changes (no runs)
- [ ] Figure 11: Only add feedforward-only agent class (~50 lines)
  - [ ] I accept this minor agent code addition
  - [ ] I have reviewed distributed_agent_no_lstm.py before running

### Data Integrity
- [ ] I understand all results will have reconciliation delta=0.0
- [ ] I understand all results will be traced to source configs
- [ ] I accept no synthetic data will be created
- [ ] I accept no oracle extrapolation will occur

### Paper Readiness
- [ ] I accept Figure 8 will still be marked as REAL_PARTIAL (sweep shows robustness but not published as main result)
- [ ] I accept Figure 9 will still be marked as REAL_PARTIAL (9a real; 9b–9e now have evaluation data)
- [ ] I accept Figure 10 will remain REAL_FULL (unchanged)
- [ ] I accept Figure 11 will be updated to show with-LSTM vs without-LSTM comparison

---

## How to Approve

### Option 1: Explicit Command Approval (Recommended)

For each full run, provide explicit approval:

```bash
# For Figure 8 sweep
APPROVE_OPTION_B_FIG8_SWEEP=1 bash <command>

# For Figure 9 evals
APPROVE_OPTION_B_FIG9_EVAL=1 bash <command>

# For Figure 11 ablation
APPROVE_OPTION_B_FIG11_ABLATION=1 bash <command>
```

### Option 2: Blanket Approval (Less Safe)

To approve entire Option B at once:

```bash
export APPROVE_OPTION_B_FULL_RUN=1
bash artifacts/production/figure-completion-option-b-plan/run-all-full-jobs.sh
```

**Warning:** This skips per-run approval. Only recommended if smoke tests all pass.

### Option 3: Approval via Git Tag

To create an auditable approval record:

```bash
# Create approval tag
git tag -a option-b-approved-2026-06-23 -m "User explicitly approved Option B execution"
git push origin option-b-approved-2026-06-23

# Check approval in execution script
if git rev-parse option-b-approved-2026-06-23 &>/dev/null; then
  APPROVED=true
fi
```

---

## Pre-Approval Verification

Before submitting approval, verify:

### 1. Plan Documentation is Complete
```bash
ls -lh artifacts/production/figure-completion-option-b-plan/ | grep -E '\.md|\.json'
# Should show:
# - option-b-run-matrix.md/json
# - figure-8-lshape-sweep-plan.md
# - figure-9-evaluation-sweep-plan.md
# - figure-11-no-lstm-ablation-plan.md
# - execution-commands.md
# - runtime-estimate.md
# - approval-required-before-full-run.md
# - claim-safety.json
```

### 2. No Code Changes Yet
```bash
git status --short | grep -E '^ M src/' && echo "ERROR: Code modified" || echo "OK: No code changes yet"
```

### 3. Baseline Data Exists
```bash
ls -lh artifacts/production/true-per-EA-distributed-baseline/distributed-candidate-metrics.json
ls -lh artifacts/production/true-per-EA-distributed-baseline/baseline-and-oracle-metrics.json
# Both files should exist and be non-empty
```

### 4. Smoke Tests Pass
```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2
HOODIE_SMOKE_EPISODE_LIMIT=50 python -m src.analysis.figure_8_sweep.run_fig8_lr_1e6_gamma099_smoke
# Should complete in <5 minutes with 0.0 delta reconciliation
```

---

## What Approval Authorizes

**Explicit approval authorizes:**
1. Creating 6 new full 5000-episode training runs (Figures 8 & 11)
2. Creating 6 evaluation-only configs (Figure 9)
3. Using ~7.1 wall hours of compute
4. Writing results to artifacts/production/figure-completion-option-b-plan/
5. Creating one new agent class (DistributedDDQNAgent_NoLSTM)

**Explicit approval DOES NOT authorize:**
- ✗ Changing any existing configs
- ✗ Modifying trainer logic
- ✗ Changing reward functions
- ✗ Altering environment topology
- ✗ Modifying metric definitions
- ✗ Implementing the proposed method
- ✗ Force-pushing to main or publishing
- ✗ Running additional sweeps beyond Option B scope

---

## Withdrawal of Approval

Approval can be withdrawn at any time:

```bash
# Before any full run starts:
unset APPROVE_OPTION_B_FIG8_SWEEP
unset APPROVE_OPTION_B_FIG9_EVAL
unset APPROVE_OPTION_B_FIG11_ABLATION
unset APPROVE_OPTION_B_FULL_RUN

# Or delete approval tag
git tag -d option-b-approved-2026-06-23
```

If runs are already in progress:
- Let them finish (safe to do; no code changes)
- Results are valid even if approval withdrawn
- Just don't commit if approval withdrawn before completion

---

## Escalation Path

If you have concerns:

1. **Review the plans:** Read all figure-specific plan documents
2. **Run smoke tests:** Verify they work without full commitment
3. **Ask questions:** Inspect execution-commands.md for exact commands being run
4. **Modify if needed:** Edit option-b-run-matrix.json before approval
5. **Escalate:** If significant changes needed, return to feasibility analysis

---

## Record Keeping

Once approved and completed, create audit trail:

```bash
# Save plan summary
cp artifacts/production/figure-completion-option-b-plan/* \
   artifacts/production/paper-output-report/

# Create execution record
cat > artifacts/production/figure-completion-option-b-plan/EXECUTION_RECORD.md <<EOF
# Execution Record

**Date:** $(date)
**Plan:** Option B Figure Completion
**Status:** APPROVED AND EXECUTED
**Total Wall Time:** [actual time]
**Results Location:** artifacts/production/figure-completion-option-b-plan/

## Figures Completed
- Figure 8: Added L-shaped sweep (5 new runs)
- Figure 9: Added system sensitivity eval (6 configs)
- Figure 10: No changes (already complete)
- Figure 11: Added no-LSTM ablation (1 run)

## Safety Verification
- All reconciliation deltas: 0.0 ✓
- No code changes to trainers ✓
- No reward logic changes ✓
- No topology changes ✓
- All configs use existing harness ✓

EOF

# Commit record
git add artifacts/production/figure-completion-option-b-plan/EXECUTION_RECORD.md
git commit -m "docs: record option b execution completion"
```

---

## Denial of Approval

If approval is denied:

1. **Plan is still valid** — saved in git for future use
2. **Smoke tests can still run** — they're lightweight and approved by default
3. **Can modify plan** — edit option-b-run-matrix.json and resubmit
4. **Can reduce scope** — approve only Fig 11 ablation (1 run instead of 12)
5. **Can delay** — approval is not time-limited; plan remains ready

---

## Safety Gates Locked

**All safety gates are LOCKED until explicit approval.**

Lock status:
- 🔒 Figure 8 sweep execution lock: LOCKED
- 🔒 Figure 9 evaluation lock: LOCKED
- 🔒 Figure 11 ablation lock: LOCKED
- 🔒 Code change lock: LOCKED
- 🔒 Reward/environment change lock: LOCKED

To unlock:
```bash
export APPROVE_OPTION_B_FIG8_SWEEP=1      # Unlocks Fig 8
export APPROVE_OPTION_B_FIG9_EVAL=1       # Unlocks Fig 9
export APPROVE_OPTION_B_FIG11_ABLATION=1  # Unlocks Fig 11
export APPROVE_OPTION_B_FULL_RUN=1        # Unlocks all at once
```

---

## Approval Timestamp

Once approved, approval is timestamped:

```bash
# Create timestamped approval record
echo "Approval granted: $(date -u +%Y-%m-%dT%H:%M:%SZ)" > \
  artifacts/production/figure-completion-option-b-plan/APPROVAL_TIMESTAMP.txt
```

---

## Summary

**Status:** 🔒 **AWAITING APPROVAL**

Approval checklist must be complete. All documentation is ready. Smoke tests are available. Once approved, execution can begin.

**To proceed:** Check all boxes in the approval checklist above, then provide explicit approval command with `APPROVE_OPTION_B_*=1` environment variables.
