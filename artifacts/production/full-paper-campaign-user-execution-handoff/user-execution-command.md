# Full Paper Campaign — User Execution Command

> Execution requires BOTH the explicit flag AND the env confirmation. Without both, the
> runner refuses and prints the disabled message. The agent will NOT run this for you.

## Run the full campaign (manual)
```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2
PY=/Users/hadi/Documents/GitHub/hoodie_sim_v2/.venvmac/bin/python

git fetch origin
git checkout full-paper-campaign-user-execution-handoff
git reset --hard origin/full-paper-campaign-user-execution-handoff

HOODIE_EXECUTE_FULL_CAMPAIGN=1 $PY -m src.analysis.full_paper_campaign_config.runner --execute-full-campaign --json
```

## Dry-run / config validation (safe, no training)
```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2
PY=/Users/hadi/Documents/GitHub/hoodie_sim_v2/.venvmac/bin/python

$PY -m src.analysis.full_paper_campaign_config.runner --dry-run --json
```

## What it will do
- Train N_E=5000 episodes (T=110), checkpoint every 250 episodes (20 checkpoints).
- Evaluate candidate at [250, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000] vs fixed_local/horizontal/vertical, random_legal, capacity_proportional_split.
- Estimated wall time: ~3.01 h (range 2.83–4.22 h) on single CPU core (no GPU; small model, GPU yields little benefit).
- Estimated storage: ~726.9 MB (checkpoints gitignored).
- Writes artifacts under `artifacts/production/full-paper-campaign-execution-run/`.

## Abort behavior
- Aborts safely on: NaN/Inf loss, raw-vs-canonical delta != 0, terminal coverage < 1.0,
  reconciliation failure, checkpoint write failure, disk full, wall time > 2x upper estimate,
  metric-schema break, or unexpected exception. On abort it still writes abort-status.json,
  monitoring-log-summary.json, and a partial run manifest.