# Figure 9 Smoke Test Results

**Status:** ⚠️ NOT EXECUTED — Execution module does not exist

---

## What Was Planned

Figure 9 smoke test (10-evaluation quick validation):
- Config: `fig9_arrival_prob_02` (low arrival probability variant)
- Agent policy: Fixed per-EA-distributed-baseline (trained at 5000 episodes)
- Evaluation episodes: 10 (vs 100 for full evaluation)
- Expected duration: <2 minutes
- Expected reconciliation delta: N/A (evaluation only, no training)
- Purpose: Validate evaluation-only inference loop works

---

## Why It Didn't Execute

The execution module `src/analysis.figure_9_sensitivity` does not exist.

### What Needs to Exist

File: `src/analysis/figure_9_sensitivity/__init__.py`

Required functions:

```python
def eval_fig9_arrival_prob_02_smoke(
    agent_checkpoint: str,
    output_dir: str,
    log_level: str = "info"
) -> dict:
    """Run 10-evaluation smoke test for low arrival probability."""
    # Load trained agent from per-EA-distributed-baseline
    # Set arrival_probability = 0.2
    # Run 10 evaluation episodes (no training)
    # Check HOODIE_SMOKE_EVAL_LIMIT for episode count
    # Return evaluation metrics

def run_all_system_param_evals(
    agent_source: str,
    agent_checkpoint: int,
    configs: list[str],
    output_dir: str,
    eval_episodes: int = 100,
    log_level: str = "info",
    seed: int = 7
) -> dict:
    """Run all 6 system parameter evaluation configs."""
    # Load trained agent once
    # For each config: vary environment parameter
    # Run evaluation episodes without training
    # Aggregate results
```

---

## Key Differences from Figure 8

**Figure 8 (training):**
- Trains new agents from random initialization
- Checkpoints and saves weights
- Produces reward learning curves
- Reconciliation delta = 0.0

**Figure 9 (evaluation):**
- Uses pre-trained agent from per-EA-distributed-baseline
- No weight updates; fixed policy
- Evaluates robustness under parameter variations
- Reconciliation delta = N/A (not trained)

---

## Expected Results (If Test Had Executed)

### Metrics (Per Evaluation)
- `reward`: Average per-episode reward
- `completion_ratio`: Percentage of tasks completed
- `drop_ratio`: Percentage of tasks dropped
- `latency_slots`: Average slots to completion

### Output Files
- `smoke_eval_results.json`: Summary of smoke evaluation
- `smoke_eval_metrics.json`: Per-episode breakdown

### Why No Reconciliation Delta
- Figure 9 doesn't train new agents
- It uses a fixed policy trained at 5000 episodes in per-EA-distributed-baseline
- Evaluation is deterministic given seed
- No "delta" metric needed; results are by definition correct

---

## Full Run Configuration (After Smoke Approval)

Once smoke passes, the full Figure 9 evaluation would run:

| Config | Parameter | Value | Purpose | Episodes |
|--------|-----------|-------|---------|----------|
| fig9_arrival_prob_02 | arrival_probability | 0.2 | Low task arrival | 100 |
| fig9_arrival_prob_05 | arrival_probability | 0.5 | Medium (baseline) | 100 |
| fig9_arrival_prob_08 | arrival_probability | 0.8 | High arrival | 100 |
| fig9_agent_count_10 | num_agents_drl | 10 | Small team | 100 |
| fig9_agent_count_20 | num_agents_drl | 20 | Standard team | 100 |
| fig9_agent_count_30 | num_agents_drl | 30 | Large team | 100 |
| **Total** | — | — | System sensitivity | 0.6 h |

---

## Why Evaluation-Only (No New Training)

- **Rationale:** The per-EA-distributed baseline is already trained and stable (5000 episodes)
- **Question:** How does this policy perform under different environment configurations?
- **Method:** Fix the policy, vary the environment, measure robustness
- **Cost:** 6 × 100 episodes ≈ 0.6 hours (vs 6 × 5000 = 30 hours if we retrained each)

---

## Implementation Blockers

- [ ] Module `src/analysis/figure_9_sensitivity` must be created
- [ ] It must load per-EA-distributed-baseline trained agent
- [ ] It must evaluate at checkpoint 5000
- [ ] It must support `HOODIE_SMOKE_EVAL_LIMIT` env var
- [ ] It must respect `APPROVE_OPTION_B_FIG9_EVAL` approval gate
- [ ] Metrics must be recorded per evaluation config

---

## Safety Constraints (Must Be Enforced)

- ✓ No new training (fixed policy)
- ✓ No reward function modifications
- ✓ No environment topology changes
- ✓ No metric definition changes
- ✓ Only environment parameters vary (arrival_probability, num_agents_drl)

---

## Approval Gate

Before any Figure 9 evaluations execute, this must be set:

```bash
export APPROVE_OPTION_B_FIG9_EVAL=1
```

---

## Can Existing Data Be Reused?

**Partially, but with caveats:**

The repo contains `artifacts/analysis/controlled-mechanistic-sweeps/` with system parameter sweep data. However:

- ✗ It was run with a **random fixed-seed agent** (not our trained policy)
- ✗ It doesn't represent the learned behavior of our specific trained agent
- ✗ It's not directly comparable to baseline results

**Decision:** Run new evaluations using our trained baseline agent. Cost is only 0.6 hours (evaluation-only), worth it for data integrity.

---

## Next Steps

1. Create `src/analysis/figure_9_sensitivity/__init__.py`
2. Implement evaluation loader and functions
3. Run smoke test: `APPROVE_OPTION_B_FIG9_EVAL=1 python -m src.analysis.figure_9_sensitivity.eval_fig9_arrival_prob_02_smoke`
4. Once smoke passes, run all 6 evaluation configs
5. Aggregate results into updated Figure 9 panels (9b–9e)

---

**Status:** Awaiting module creation and user approval.
