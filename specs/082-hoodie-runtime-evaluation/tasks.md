# Tasks — Feature 082 Proposed-vs-Original Policy-Divergence Repair

## Spec Kit Reference

Use the GitHub Spec Kit workflow as process reference:

https://github.com/github/spec-kit

## Task Group A — Confirm Current Failure

- [ ] Read `artifacts/feature_082_full_runtime_eval/aggregate_by_policy.csv`.
- [ ] Read `artifacts/feature_082_full_runtime_eval/aggregate_by_policy.json`.
- [ ] Confirm `HOODIE_PROPOSED == ORIGINAL_HOODIE_BASELINE` across all core aggregate metrics.
- [ ] Mark the feature blocked if this equality remains after repair.

## Task Group B — Inspect Policy Paths

- [ ] Inspect `src/analysis/hoodie_runtime_evaluation_runner/policies.py`.
- [ ] Inspect `src/analysis/hoodie_runtime_evaluation_runner/runner.py`.
- [ ] Inspect `src/analysis/hoodie_runtime_evaluation_runner/model.py`.
- [ ] Inspect `src/analysis/hoodie_runtime_evaluation_runner/scenarios.py`.
- [ ] Inspect `src/analysis/hoodie_proposed_method/`.
- [ ] Identify shared scoring/helper/selection behavior between `HOODIE_PROPOSED` and `ORIGINAL_HOODIE_BASELINE`.

## Task Group C — Repair HOODIE_PROPOSED

- [ ] Use Feature 080 proposed-method components.
- [ ] Add proposed-method-specific trace labels.
- [ ] Ensure the proposed adapter has a distinct scoring path.
- [ ] Ensure it can select differently from `ORIGINAL_HOODIE_BASELINE` in mixed candidate scenarios.
- [ ] Keep the implementation base-paper only.

## Task Group D — Repair ORIGINAL_HOODIE_BASELINE

- [ ] Remove shared proposed-method scoring behavior.
- [ ] Implement a distinct paper-aligned baseline path.
- [ ] Add baseline-specific trace labels.
- [ ] If full original-HOODIE runtime is unavailable, document this limitation.
- [ ] Ensure it differs from `HOODIE_PROPOSED` in at least one core aggregate metric.

## Task Group E — Divergence Tests

- [ ] Unit test: `HOODIE_PROPOSED` and `ORIGINAL_HOODIE_BASELINE` have different decision traces under mixed candidates.
- [ ] Unit test: policies do not choose the same action for every mixed local/horizontal/vertical scenario.
- [ ] Integration test: artifacts prove `HOODIE_PROPOSED != ORIGINAL_HOODIE_BASELINE`.
- [ ] Artifact validation test: fail if all core aggregate metrics are equal between the two policies.
- [ ] Scope guard: no DCQ/thesis/custom queue redesign introduced.

## Task Group F — Artifact Regeneration

- [ ] Regenerate `raw_rows.json` and `raw_rows.csv`.
- [ ] Regenerate `aggregate_by_policy.json` and `aggregate_by_policy.csv`.
- [ ] Regenerate `ranking_by_metric.json` and `ranking_by_metric.csv`.
- [ ] Regenerate runtime evaluation report JSON/MD.
- [ ] Regenerate execution manifest.

## Task Group G — Report and Manifest

- [ ] Add proof `HOODIE_PROPOSED != LOCAL_ONLY`.
- [ ] Add proof `ORIGINAL_HOODIE_BASELINE != CLOUD_ONLY`.
- [ ] Add proof `HOODIE_PROPOSED != ORIGINAL_HOODIE_BASELINE`.
- [ ] Include exact differing metric(s) for proposed-vs-original.
- [ ] Include claim boundary.
- [ ] Include scope proof.
- [ ] Do not claim statistical superiority.

## Task Group H — Final Validation

- [ ] `git diff --check` passes.
- [ ] Unit tests pass.
- [ ] Integration tests pass.
- [ ] Artifact write command passes.
- [ ] Artifact validation command passes.
- [ ] Branch pushed.
- [ ] Final output includes aggregate proof that `HOODIE_PROPOSED` and `ORIGINAL_HOODIE_BASELINE` differ.
