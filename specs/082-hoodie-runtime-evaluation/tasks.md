# Tasks — Feature 082 Proposed-vs-Original Policy-Divergence Repair

## Spec Kit Reference

Use the GitHub Spec Kit workflow as process reference:

https://github.com/github/spec-kit

## Task Group A — Confirm Current Failure

- [X] Read `artifacts/feature_082_full_runtime_eval/aggregate_by_policy.csv`.
- [X] Read `artifacts/feature_082_full_runtime_eval/aggregate_by_policy.json`.
- [X] Confirm `HOODIE_PROPOSED == ORIGINAL_HOODIE_BASELINE` across all core aggregate metrics.
- [X] Mark the feature blocked if this equality remains after repair.

## Task Group B — Inspect Policy Paths

- [X] Inspect `src/analysis/hoodie_runtime_evaluation_runner/policies.py`.
- [X] Inspect `src/analysis/hoodie_runtime_evaluation_runner/runner.py`.
- [X] Inspect `src/analysis/hoodie_runtime_evaluation_runner/model.py`.
- [X] Inspect `src/analysis/hoodie_runtime_evaluation_runner/scenarios.py`.
- [X] Inspect `src/analysis/hoodie_proposed_method/`.
- [X] Identify shared scoring/helper/selection behavior between `HOODIE_PROPOSED` and `ORIGINAL_HOODIE_BASELINE`.

## Task Group C — Repair HOODIE_PROPOSED

- [X] Use Feature 080 proposed-method components.
- [X] Add proposed-method-specific trace labels.
- [X] Ensure the proposed adapter has a distinct scoring path.
- [X] Ensure it can select differently from `ORIGINAL_HOODIE_BASELINE` in mixed candidate scenarios.
- [X] Keep the implementation base-paper only.

## Task Group D — Repair ORIGINAL_HOODIE_BASELINE

- [X] Remove shared proposed-method scoring behavior.
- [X] Implement a distinct paper-aligned baseline path.
- [X] Add baseline-specific trace labels.
- [X] If full original-HOODIE runtime is unavailable, document this limitation.
- [X] Ensure it differs from `HOODIE_PROPOSED` in at least one core aggregate metric.

## Task Group E — Divergence Tests

- [X] Unit test: `HOODIE_PROPOSED` and `ORIGINAL_HOODIE_BASELINE` have different decision traces under mixed candidates.
- [X] Unit test: policies do not choose the same action for every mixed local/horizontal/vertical scenario.
- [X] Integration test: artifacts prove `HOODIE_PROPOSED != ORIGINAL_HOODIE_BASELINE`.
- [X] Artifact validation test: fail if all core aggregate metrics are equal between the two policies.
- [X] Scope guard: no DCQ/thesis/custom queue redesign introduced.

## Task Group F — Artifact Regeneration

- [X] Regenerate `raw_rows.json` and `raw_rows.csv`.
- [X] Regenerate `aggregate_by_policy.json` and `aggregate_by_policy.csv`.
- [X] Regenerate `ranking_by_metric.json` and `ranking_by_metric.csv`.
- [X] Regenerate runtime evaluation report JSON/MD.
- [X] Regenerate execution manifest.

## Task Group G — Report and Manifest

- [X] Add proof `HOODIE_PROPOSED != LOCAL_ONLY`.
- [X] Add proof `ORIGINAL_HOODIE_BASELINE != CLOUD_ONLY`.
- [X] Add proof `HOODIE_PROPOSED != ORIGINAL_HOODIE_BASELINE`.
- [X] Include exact differing metric(s) for proposed-vs-original.
- [X] Include claim boundary.
- [X] Include scope proof.
- [X] Do not claim statistical superiority.

## Task Group H — Final Validation

- [X] `git diff --check` passes.
- [X] Unit tests pass.
- [X] Integration tests pass.
- [X] Artifact write command passes.
- [X] Artifact validation command passes.
- [X] Branch pushed.
- [X] Final output includes aggregate proof that `HOODIE_PROPOSED` and `ORIGINAL_HOODIE_BASELINE` differ.
