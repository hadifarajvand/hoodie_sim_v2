# Quickstart: Paper HOODIE Network Implementation

This feature is architecture-only. It does not train a model, sample replay, or run campaigns.

## Validate the architecture contract

If torch is unavailable in the approved interpreter, implementation remains dependency-blocked and must stop without editing dependency files.

## Expected architecture checks

- Q-network hidden layers are `[1024, 1024, 1024]`
- LSTM lookback window is `10`
- LSTM num layers is `1`
- LSTM hidden size is `20`
- Action count is `3`
- Online and target networks share the same forward API shape

## Validate the report artifacts

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_paper_hoodie_network_config \
  tests.unit.test_paper_hoodie_network_shapes \
  tests.integration.test_paper_hoodie_network_report \
  tests.integration.test_paper_hoodie_network_scope_guard
```

## Expected report artifacts

- `artifacts/analysis/paper-hoodie-network-implementation/network-implementation-report.json`
- `artifacts/analysis/paper-hoodie-network-implementation/network-implementation-report.md`

## What the report must say

- `dependency_status` is `blocked_missing_existing_torch` if torch is not available
- no training started
- no optimizer step
- no replay execution
- Feature 038 readiness gate still blocks training
