# Quickstart: Mechanism Repair

## Purpose

Repair the confirmed Feature 018 timeout/drop divergence, validate it with regression tests, and regenerate the Feature 018 audit artifacts.

## Validation Commands

Run the targeted regression and audit tests with the approved interpreter:

```bash
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_mechanism_repair_timeout_drop \
  tests.unit.test_differential_environment_audit \
  tests.integration.test_differential_environment_audit_flow
```

After the repair, regenerate the Feature 018 differential audit artifacts:

```bash
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -c "from src.audits.differential_environment import DifferentialEnvironmentAudit; DifferentialEnvironmentAudit().run()"
```

## Expected Outputs

- `artifacts/analysis/mechanism-repair/repair-summary.json`
- `artifacts/analysis/mechanism-repair/repair-summary.md`
- `artifacts/analysis/differential-environment-audit/differential-audit.json`
- `artifacts/analysis/differential-environment-audit/differential-audit.md`

## Validation Notes

- The timeout/drop regression must fail before the patch and pass after it.
- Existing Feature 017 and Feature 018 targeted tests must remain passing.
- The regenerated Feature 018 audit must no longer report the repaired timeout/drop case as a divergence unless the behavior still genuinely differs from the reference contract.
