# Quickstart: Differential Environment Audit

## Purpose

Run the diagnostic audit over the fixed toy-case set and verify the comparison artifacts are deterministic and non-remediating.

## Validation Commands

Run the planned test suite with the approved environment:

```bash
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_differential_environment_audit \
  tests.integration.test_differential_environment_audit_flow
```

## Expected Outcomes

- The unit tests validate the toy-case schema and classification logic.
- The integration test validates deterministic report generation over the fixed toy-case set.
- The guard test confirms the audit only reads from the allowed public environment interface and does not import forbidden simulator paths.
- The generated JSON and Markdown reports are deterministic and include no-fix disclaimers.

## Output Paths

- `artifacts/analysis/differential-environment-audit/differential-audit.json`
- `artifacts/analysis/differential-environment-audit/differential-audit.md`

## Notes

- The audit is diagnostic only.
- Divergences and unsupported observations are classified, not repaired.

