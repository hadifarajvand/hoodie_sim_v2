# Feature 078 Quickstart

## Pull Latest Main

```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2
git fetch origin --prune
git checkout main
git pull --ff-only origin main
git status --short --branch
git rev-parse HEAD
```

## Future Implementation Flow

1. Confirm Feature 076 and Feature 077 are present on `main`.
2. Create the execution package under `src/analysis/campaign_execution_engine/`.
3. Create the unit and integration tests for Feature 078.
4. Build the campaign grid from the Feature 077 contract.
5. Execute all configured grid cells.
6. Emit raw result rows only.
7. Validate row count as `441 * seed_count`.
8. Validate each row against the metric contract.
9. Validate no statistical summary or method ranking is produced.
10. Run regressions.
11. Commit and push.

## Required Python

Use only:

```bash
src/.venvmac/bin/python
```

Do not use system `python3`.

## Expected Future Commands

```bash
src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_campaign_execution_engine_*.py'
src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_campaign_execution_engine_*.py'
src/.venvmac/bin/python -m src.analysis.campaign_execution_engine
```

## Success State

- campaign execution report exists in memory or approved output path.
- raw row count equals `441 * seed_count`.
- every row is action-bound.
- compatibility mode is false for every row.
- no ranking or statistical conclusion is produced.
