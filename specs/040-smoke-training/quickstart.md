# Quickstart: Smoke Training

## Purpose

Run a tiny deterministic smoke validation that proves the Feature 039 network surface, delayed reward handling, and optimizer wiring can execute without runtime failure.

## Prerequisites

- Use the approved interpreter: `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`
- Ensure the active feature pointer resolves to `specs/040-smoke-training`
- Do not add or change dependency files

## Validation Command

Run the full validation gate:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_smoke_training_contract \
  tests.integration.test_smoke_training_report \
  tests.integration.test_smoke_training_determinism \
  tests.integration.test_smoke_training_scope_guard \
  tests.unit.test_paper_hoodie_network_config \
  tests.unit.test_paper_hoodie_network_shapes \
  tests.integration.test_paper_hoodie_network_report \
  tests.unit.test_training_foundation_contract \
  tests.integration.test_training_foundation_contract_report \
  tests.integration.test_training_readiness_gate
```

## Expected Smoke Artifacts

- `artifacts/analysis/smoke-training/smoke-training-report.json`
- `artifacts/analysis/smoke-training/smoke-training-report.md`

## Smoke Contract Expectations

- Exactly one optimizer step
- Finite smoke loss
- At least one online-network parameter changes
- Deterministic repeatability with the same seed bundle
- Target network instantiated but not updated
- No paper reproduction claim
- No performance metrics

## Notes

- Fixture transitions are validation artifacts only and are not simulator evidence.
- Pending-at-horizon transitions must remain non-terminal.
- The Feature 038 readiness block remains active.
