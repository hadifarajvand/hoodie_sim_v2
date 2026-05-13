# Quickstart: Training Foundation Contract

This feature is contract-only. It does not train a model or change runtime semantics.

## Validate the spec artifacts

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_training_foundation_contract \
  tests.integration.test_training_foundation_contract_report \
  tests.integration.test_training_readiness_gate \
  tests.integration.test_training_foundation_scope_guard
```

## Validate the readiness gate against existing evidence

The readiness gate must consume existing Feature 037 trace evidence or a lightweight audit over `HoodieGymEnvironment` traces. It must not alter episode length, extend horizons, or add drain behavior.

## Expected report artifacts

- `artifacts/analysis/training-foundation-contract/training-foundation-contract-report.json`
- `artifacts/analysis/training-foundation-contract/training-foundation-contract-report.md`

## What the report must say

- Training is blocked until terminal/reward-bearing exposure is sufficient and approved.
- Feature 037 sparse-terminal traces are a blocker, not paper reproduction evidence.
- No training, neural-network, optimizer, replay-execution, or runtime-contract changes were introduced.

