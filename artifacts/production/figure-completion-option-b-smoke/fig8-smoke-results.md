# Figure 8 Smoke Test Results

**Status:** ⚠️ NOT EXECUTED — Execution module does not exist

---

## What Was Planned

Figure 8 smoke test (50-episode quick validation):
- Config: `fig8_lr_1e6_gamma099` (high learning rate variant)
- Episode limit: 50 (vs 5000 for full)
- Expected duration: <5 minutes
- Expected reconciliation delta: 0.0
- Purpose: Validate hyperparameter sweep training loop works

---

## Why It Didn't Execute

The execution module `src/analysis/figure_8_sweep` does not exist.

### What Needs to Exist

File: `src/analysis/figure_8_sweep/__init__.py`

Required functions:

```python
def run_fig8_lr_1e6_gamma099_smoke(
    output_dir: str,
    log_level: str = "info"
) -> dict:
    """Run 50-episode smoke test for high-LR config."""
    # Execute fig8_lr_1e6_gamma099 config
    # Check HOODIE_SMOKE_EPISODE_LIMIT for episode count
    # Return metrics with reconciliation delta

def run_all_lshape_configs(
    configs: list[str],
    output_dir: str,
    log_level: str = "info",
    save_checkpoints: bool = True
) -> dict:
    """Run all 5 L-shaped hyperparameter configs (5000 episodes each)."""
    # Execute each config in sequence or parallel
    # Checkpoints at: 250, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000
    # Return aggregated metrics for all runs
```

---

## Expected Results (If Test Had Executed)

### Metrics
- Learning curve: Reward vs episode
- Checkpoints: 11 (at 250, 500, ..., 5000 episodes)
- Per-checkpoint metrics:
  - `reward_per_checkpoint`: Average reward at checkpoint
  - `completion_ratio`: Percentage of tasks completed
  - `drop_ratio`: Percentage of tasks dropped
  - `latency_slots`: Average slots to completion

### Reconciliation
- `delta`: 0.0 (expected; matching baseline)
- `terminal_coverage`: 1.0 (expected; all tasks evaluated)

### Output Files
- `smoke_metrics.json`: Summary of smoke run
- `smoke_checkpoint_metrics.json`: Per-checkpoint breakdown
- `smoke_reconciliation_status.json`: Reconciliation verification

---

## Validation Criteria (Not Checked Yet)

- [ ] No training crashes on early episodes
- [ ] Reconciliation delta = 0.0
- [ ] Terminal coverage = 1.0
- [ ] Reward changes gradually (no NaN/Inf)
- [ ] Checkpoints save and load correctly
- [ ] Metrics align with baseline harness expectations

---

## Full Run Configuration (After Smoke Approval)

Once smoke passes, the full Figure 8 sweep would run:

| Config | LR | Gamma | Expected Time | Purpose |
|--------|----|----|------|---------|
| fig8_lr_1e6_gamma099 | 1e-6 | 0.99 | 1.1 h | High LR (10× baseline) |
| fig8_lr_5e7_gamma099 | 5e-7 | 0.99 | 1.1 h | Mid-low LR (0.7× baseline) |
| fig8_lr_1e7_gamma099 | 1e-7 | 0.99 | 1.1 h | Low LR (0.14× baseline) |
| fig8_lr_7e7_gamma095 | 7e-7 | 0.95 | 1.1 h | Low gamma (−0.04) |
| fig8_lr_7e7_gamma0995 | 7e-7 | 0.995 | 1.1 h | High gamma (+0.005) |
| **Total** | — | — | **5.4 h** | L-shaped sweep |

---

## Implementation Blockers

- [ ] Module `src/analysis/figure_8_sweep` must be created
- [ ] It must reference per-EA-distributed-baseline policy
- [ ] It must respect `HOODIE_SMOKE_EPISODE_LIMIT` env var
- [ ] It must respect `APPROVE_OPTION_B_FIG8_SWEEP` approval gate
- [ ] Checkpoints must save at specified episodes
- [ ] Metrics must be recorded and traced to source config

---

## Safety Constraints (Must Be Enforced)

- ✓ No reward function modifications
- ✓ No environment topology changes
- ✓ No metric definition changes
- ✓ All reconciliation profiles locked to baseline
- ✓ All state representation profiles locked to baseline
- ✓ Only hyperparameters (lr, gamma) vary

---

## Approval Gate

Before full Figure 8 runs execute, this must be set:

```bash
export APPROVE_OPTION_B_FIG8_SWEEP=1
```

---

## Next Steps

1. Create `src/analysis/figure_8_sweep/__init__.py`
2. Implement smoke test function
3. Run smoke test: `APPROVE_OPTION_B_FIG8_SWEEP=1 python -m src.analysis.figure_8_sweep.run_fig8_lr_1e6_gamma099_smoke`
4. Once smoke passes, run full sweep
5. Aggregate results into updated Figure 8 panel

---

**Status:** Awaiting module creation and user approval.
