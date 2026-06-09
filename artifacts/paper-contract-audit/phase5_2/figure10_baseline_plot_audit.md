# Figure 10 Baseline Plot Audit

This plot is generated from the baseline validation run only. It is not the full official HOODIE Figure 10 reproduction because HOODIE is unavailable/not trained in this run.

What this adds:
- Baseline-only plotting support from the existing 200-episode validation outputs.
- Delay and drop-ratio figures for `RO`, `FLC`, `VO`, `HO`, `BCO`, and `MLEO`.
- A combined baseline-only diagnostic figure.

What it does not do:
- It does not rerun simulation.
- It does not train HOODIE.
- It does not plot HOODIE.
- It does not claim paper-faithful final reproduction.

Source inputs:
- `artifacts/figure10_validation/runs/baseline-200-seed42/figure10_policy_metrics_summary.json`
- `artifacts/figure10_validation/runs/baseline-200-seed42/figure10_policy_readiness.json`
- `artifacts/figure10_validation/runs/baseline-200-seed42/figure10_validation_manifest.json`
- `artifacts/figure10_validation/runs/baseline-200-seed42/figure10_run_config_snapshot.json`

Warnings:
- Runtime parameter diagnostics still exist.
- The plot is diagnostic-only, not a final official reproduction.

