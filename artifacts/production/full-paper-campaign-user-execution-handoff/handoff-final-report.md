# Full Paper Campaign — User Execution Handoff Report

- **Verdict:** `full_campaign_user_execution_handoff_ready`
- **Next step:** `user_runs_full_campaign_command`
- Executed 5000: False | Execution path wired: True
- Execution requires: --execute-full-campaign, HOODIE_EXECUTE_FULL_CAMPAIGN=1
- Config guards pass: True | Execution guard correct: True
- Output artifacts: `artifacts/production/full-paper-campaign-execution-run/`

## Full execution command
```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2
PY=/Users/hadi/Documents/GitHub/hoodie_sim_v2/.venvmac/bin/python

git fetch origin
git checkout full-paper-campaign-user-execution-handoff
git reset --hard origin/full-paper-campaign-user-execution-handoff

HOODIE_EXECUTE_FULL_CAMPAIGN=1 $PY -m src.analysis.full_paper_campaign_config.runner --execute-full-campaign --json
```

## Dry-run command
```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2
PY=/Users/hadi/Documents/GitHub/hoodie_sim_v2/.venvmac/bin/python

$PY -m src.analysis.full_paper_campaign_config.runner --dry-run --json
```

## Claim safety
- No paper-reproduction / exact-numerical / performance / baseline-superiority claims are made.