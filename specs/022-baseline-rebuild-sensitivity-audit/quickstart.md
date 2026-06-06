# Quickstart: Baseline Rebuild Sensitivity Audit

## Purpose

Run the Feature 022 sensitivity audit after Feature 021 has produced a baseline fairness rebuild result.

## Required Inputs

- Feature 018 differential audit artifact
- Feature 019 mechanism repair summary artifact
- Feature 020 controlled mechanistic sweeps artifact
- Feature 021 baseline fairness rebuild artifact

## Expected Outputs

- `artifacts/analysis/baseline-rebuild-sensitivity-audit/baseline-rebuild-sensitivity-audit.json`
- `artifacts/analysis/baseline-rebuild-sensitivity-audit/baseline-rebuild-sensitivity-audit.md`
- Optional deterministic CSV summary if already conventional in the repository

## Validation Guidance

- Use the approved project interpreter at `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`
- Run the unit and integration tests associated with the sensitivity audit
- Confirm the report records whether the Feature 021 conclusion is robust, fragile, worsened, or inconclusive

## Validation Command

```bash
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_baseline_rebuild_sensitivity_audit \
  tests.integration.test_baseline_rebuild_sensitivity_audit_flow \
  tests.integration.test_baseline_rebuild_sensitivity_audit_scope_guard \
  tests.integration.test_baseline_rebuild_sensitivity_audit_final_diff
```

## Scope Reminder

- No policy redesign
- No training foundation work
- No metric formula changes
- No paper-validity claim
