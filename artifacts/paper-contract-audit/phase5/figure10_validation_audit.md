# Figure 10 Validation Audit

## Scope

This phase adds an official validation workflow for Figure 10 data only.
It does not generate plots and it does not claim paper-faithful reproduction.

## What the workflow now computes

- Average computation delay from lifecycle completion data.
- Drop ratio from lifecycle task counts.
- Per-policy and per-regime raw metric tables.
- Policy readiness summaries.
- HOODIE checkpoint availability status.
- MLEO candidate-trace readiness status.
- Delayed-reward trace readiness status.

## Data sources

- `config/paper_table4_contract.json`
- `hyperparameters/hyperparameters.json`
- `task_lifecycle.csv`
- `episode_metrics.csv`
- `action_trace.csv`
- `pending_transition_trace.csv`
- `delayed_reward_event_trace.csv`
- `mleo_candidate_latency_trace.csv`

## What is derived from lifecycle traces

- `average_computation_delay`
- `drop_ratio`
- `completed_tasks`
- `dropped_tasks`
- `pending_tasks`

The delay denominator is completed tasks only.
The drop-ratio denominator is total tasks.
Pending tasks are reported explicitly and are not hidden.

## MLEO readiness

MLEO is considered ready only when `mleo_candidate_latency_trace.csv` exists and the validation report classifies it as `paper_candidate_trace_ready`.

## Delayed reward readiness

Delayed reward readiness requires both pending-transition and delayed-reward event traces.
The workflow checks that reward events are paired to the original transition and that replay insertion status is explicit.

## Why there are no plots

This phase is a validation workflow, not a figure-generation workflow.
It produces machine-readable CSV/JSON outputs only.

## Why HOODIE without checkpoint blocks the official Figure 10 claim

HOODIE is the trained DRL policy in inference mode.
If no trained checkpoint is supplied, the workflow marks HOODIE as `unavailable_not_trained` and does not pretend that an untrained agent is official HOODIE.

## What remains before plotting Figure 10

- Supply a real trained HOODIE checkpoint.
- Resolve any runtime parameter contract mismatches.
- Re-run the validation workflow in non-test mode for 200 episodes.
- Only then should plotting be attempted.

## Reproduction

```bash
./.venvmac/bin/python scripts/run_figure10_validation.py \
  --output-dir artifacts/figure10_validation/runs/<run_id> \
  --episodes 200 \
  --policies HOODIE,RO,FLC,VO,HO,BCO,MLEO
```

