# Figure 10 Baseline Validation Runbook Audit

## What this adds

- A print-only runbook for baseline-only Figure 10 validation.
- A print-only reminder for the full HOODIE validation command.
- A tiny smoke command.
- Post-run inspection commands.
- Git hygiene commands.

## What this does not do

- It does not run the 200-episode validation.
- It does not generate plots.
- It does not fake readiness.
- It does not evaluate HOODIE without a trained checkpoint.
- It does not commit or push anything.

## Baseline-only command

The baseline-only command intentionally excludes `HOODIE`:

```bash
./.venvmac/bin/python scripts/run_figure10_validation.py \
  --output-dir artifacts/figure10_validation/runs/baseline-200-seed42 \
  --episodes 200 \
  --policies RO,FLC,VO,HO,BCO,MLEO \
  --seed 42
```

## Full command

The full Figure 10 command includes `HOODIE` and requires `--hoodie-checkpoint-dir`.

## Current status

- `baseline_validation_ready` is a future run result, not something this runbook claims.
- `figure10_data_ready` remains dependent on a trained HOODIE checkpoint and clean readiness checks.
- Generated outputs under `artifacts/figure10_validation/runs/` remain ignored by git.

