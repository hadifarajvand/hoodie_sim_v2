# Quickstart: Baseline Fairness Rebuild

## Purpose

Rerun a small baseline fairness matrix after the mechanism credibility gates have passed and summarize whether collapse is reduced, unchanged, worsened, or inconclusive.

## Expected Artifacts

- `artifacts/analysis/baseline-fairness-rebuild/baseline-fairness-rebuild.json`
- `artifacts/analysis/baseline-fairness-rebuild/baseline-fairness-rebuild.md`
- Optional CSV summary only if it is already conventional and deterministic for this analysis class

## Validation Commands

The planned implementation should be verified with the approved interpreter and the feature’s unit/integration tests.

```bash
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_baseline_fairness_rebuild \
  tests.integration.test_baseline_fairness_rebuild_flow
```

## Report Expectations

- The JSON report must include metadata, source gate status, baseline policies included, scenarios/traces used, fairness controls, reused metrics, collapse indicators, anti-collapse assessment, unchanged-collapse explanation, limitations, disclaimers, and reproducibility details.
- The Markdown report must present the same information in a readable summary.
- The report must include no-training, no-policy-redesign, and no-paper-validity disclaimers.
- Persistent collapse must remain a valid outcome and may be reported as evidence for further mechanism investigation or policy-definition audit.

## Constraints

- No policy redesign.
- No new baselines.
- No HOODIE DRL training.
- No simulator or environment changes.
- No metric formula changes.
- No campaign-scale paper reproduction.
- No plotting unless already conventional and explicitly approved.
