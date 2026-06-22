# Full HOODIE Paper Campaign — Execution Runbook (config only)

> **This branch does NOT run the campaign.** Execution requires the explicit flag
> `--execute-full-campaign` AND the env confirmation `HOODIE_EXECUTE_FULL_CAMPAIGN=1`,
> which is intentionally never set here. N_E=5000 is not run.

## 1. Exact commands
- Dry-run / config validation: `python -m src.analysis.full_paper_campaign_config.runner --dry-run --json`
- Full campaign (gated, do not run without approval): `python -m src.analysis.full_paper_campaign_config.runner --execute-full-campaign --json`

## 2. Estimated wall time
- Training: 2.4 h (range 2.22–3.61 h)
- Evaluation: 0.61 h
- **Total wall: 3.01 h (range 2.83–4.22 h)** on single CPU core (no GPU; small model, GPU yields little benefit)

## 3. Estimated storage
- ~503.5 MB checkpoints (20 ckpts) + ~23.3 MB replay + ~200.0 MB artifacts ≈ **~726.9 MB total**

## 4. Checkpoint interval & resume
- Checkpoint every 250 episodes (see checkpoint-resume-plan.md).
- Resume: re-invoke the execute command; the runner loads the latest checkpoint and continues to N_E=5000 (epsilon is episode-indexed, so resume is exact).

## 5. Monitoring
- `tail -f artifacts/production/full-paper-campaign-run/progress.jsonl` (see monitoring-plan.md).

## 6. Artifact directory
- `artifacts/production/full-paper-campaign-run/` (see expected-artifact-manifest.json).

## 7. Abort conditions
- See abort-conditions.md (NaN loss, reconciliation regression, delta!=0, coverage<1, disk full, runaway wall time).

## 8. Post-run verification
- `python -m src.analysis.paper_faithful_simulation_production.runner --json`  # paper-compatible metric schema check
- Confirm reward_reconciled / terminal_reconciled true, raw_vs_canonical_delta=0, coverage=1.0 in final metrics.

## 9. Known limitations
- Shared-parameter trainer approximation, not the paper's per-EA distributed model fleet (see remaining-approximations.md).
- Running 5000 tests the shared-parameter implementation ceiling only.

## 10. Warning
- No paper-reproduction, exact-numerical-reproduction, or baseline-superiority claims are made or implied.