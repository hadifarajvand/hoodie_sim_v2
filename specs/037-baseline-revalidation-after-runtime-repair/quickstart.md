# Quickstart: Baseline Revalidation After Runtime Repair

## Approved Interpreter

Use the approved environment only:

```bash
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python
```

## Revalidation Scope

- FLC
- VO
- HO
- RO
- BCO
- MLEO
- ADAPTIVE

## Expected Inputs

- Repaired runtime contracts from Features 032–036
- Deterministic seeds: `0`, `1`, `2` minimum; `0` through `4` preferred when runtime cost allows
- Paper-default scenario unless an existing smaller smoke matrix is already used by the runner

## Validation Command

Use the approved interpreter to run the targeted baseline revalidation tests and report checks:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_baseline_registry_revalidation \
  tests.integration.test_baseline_revalidation_after_runtime_repair \
  tests.integration.test_baseline_revalidation_report \
  tests.integration.test_baseline_revalidation_scope_guard \
  tests.integration.test_execution_time_flow \
  tests.integration.test_transmission_delay_runtime_wiring \
  tests.integration.test_public_cloud_capacity_sharing_flow \
  tests.integration.test_mechanism_repair_timeout_drop
```

If the repository already has a smaller smoke matrix runner for deterministic validation, the report must explicitly label the result as smoke revalidation.

## Expected Outcomes

- All seven baseline policies run through the same `HoodieGymEnvironment` path.
- No policy bypasses the legal action mask.
- Fixed-seed deterministic baselines produce identical artifacts.
- RO remains reproducible with the same seed.
- The revalidation report records the required fields and refuses any paper-reproduction claim.

## Report Artifacts

Generate:

- `artifacts/analysis/baseline-revalidation-after-runtime-repair/baseline-revalidation-report.json`
- `artifacts/analysis/baseline-revalidation-after-runtime-repair/baseline-revalidation-report.md`

Optional when supported:

- `artifacts/evaluation/baseline-revalidation-after-runtime-repair/`

The report must distinguish:
- prerequisite runtime tags verified
- policies revalidated
- seeds used
- runtime contracts verified
- legal-action verification
- deterministic reproducibility verification
- metric schema verification
- baseline result summary
- no curve fitting
- no paper reproduction claim
