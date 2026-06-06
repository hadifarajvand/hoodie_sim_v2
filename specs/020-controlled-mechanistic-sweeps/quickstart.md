# Quickstart: Controlled Mechanistic Sweeps

## Purpose

Run tiny deterministic sweeps over a controlled set of mechanism parameters and produce a diagnostic-only summary.

## Expected Artifacts

- `artifacts/analysis/controlled-mechanistic-sweeps/controlled-mechanistic-sweeps.json`
- `artifacts/analysis/controlled-mechanistic-sweeps/controlled-mechanistic-sweeps.md`

## Validation Commands

The planned implementation should be verified with the approved interpreter and the feature’s unit/integration tests.

```bash
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_controlled_mechanistic_sweeps \
  tests.integration.test_controlled_mechanistic_sweeps_flow
```

## Report Expectations

- The JSON report must include metadata, sweep definitions, fixed inputs, observations, monotonic checks, warnings, instrumentation gaps, limitations, and reproducibility details.
- The Markdown report must present the same information in a readable summary.
- The report must include a no-campaign-rerun disclaimer and a no-paper-validity disclaimer.
- Unsupported or unobservable sweep dimensions must be labeled inconclusive or instrumentation_gap rather than silently repaired.

## Constraints

- No baseline campaign reruns.
- No plotting.
- No simulator or environment changes.
- No policy changes.
- No metric formula changes.
- No dependency changes.
