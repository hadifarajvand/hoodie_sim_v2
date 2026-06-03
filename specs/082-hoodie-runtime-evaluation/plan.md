# Plan — Feature 082 Proposed-vs-Original Policy-Divergence Repair

## Spec Kit Reference

Follow the GitHub Spec Kit workflow as the implementation process reference:

https://github.com/github/spec-kit

## Repair Objective

Repair Feature 082 so that `HOODIE_PROPOSED` and `ORIGINAL_HOODIE_BASELINE` are behaviorally distinct in generated runtime evaluation artifacts.

## Current State

Already repaired:

```text
HOODIE_PROPOSED != LOCAL_ONLY
ORIGINAL_HOODIE_BASELINE != CLOUD_ONLY
```

Still broken:

```text
HOODIE_PROPOSED == ORIGINAL_HOODIE_BASELINE
```

This is a hard blocker. The feature is not research-valid until the two core policies diverge in at least one core aggregate metric.

## Repair Phases

### Phase 1 — Confirm Current Failure

Read:

```text
artifacts/feature_082_full_runtime_eval/aggregate_by_policy.csv
artifacts/feature_082_full_runtime_eval/aggregate_by_policy.json
```

Confirm that `HOODIE_PROPOSED` and `ORIGINAL_HOODIE_BASELINE` are currently identical across all core aggregate metrics.

### Phase 2 — Inspect Policy Execution Paths

Inspect:

```text
src/analysis/hoodie_runtime_evaluation_runner/policies.py
src/analysis/hoodie_runtime_evaluation_runner/runner.py
src/analysis/hoodie_runtime_evaluation_runner/model.py
src/analysis/hoodie_runtime_evaluation_runner/scenarios.py
src/analysis/hoodie_runtime_evaluation_runner/metrics.py
src/analysis/hoodie_proposed_method/
```

Find whether both policies:

- call the same scoring helper
- use the same candidate ordering
- use the same action selection rule
- generate only different labels over the same behavior

### Phase 3 — Repair HOODIE_PROPOSED

The proposed adapter must:

- use Feature 080 proposed-method components
- expose Feature-080/proposed-specific decision traces
- use a proposed scoring path that can differ from baseline under mixed candidates
- not mutate Feature 080 internals
- remain base-paper only

### Phase 4 — Repair ORIGINAL_HOODIE_BASELINE

The original baseline adapter must:

- use a distinct baseline decision path
- avoid using the same proposed-method scoring path
- expose baseline-specific decision traces
- represent a paper-aligned baseline heuristic if full original-HOODIE runtime is unavailable
- document any limitation honestly

### Phase 5 — Add Divergence Tests

Add or update tests so validation fails if:

- `HOODIE_PROPOSED` and `ORIGINAL_HOODIE_BASELINE` choose the same action in every mixed-candidate scenario
- their traces use the same scoring label or same runtime path
- their aggregate artifacts are identical across all core metrics

### Phase 6 — Regenerate Artifacts

Run:

```bash
src/.venvmac/bin/python -m analysis.hoodie_runtime_evaluation_runner --write-artifacts artifacts/feature_082_full_runtime_eval
src/.venvmac/bin/python -m analysis.hoodie_runtime_evaluation_runner --validate-artifacts --artifact-dir artifacts/feature_082_full_runtime_eval
```

### Phase 7 — Report Proof

Update report and manifest to include explicit proof for:

```text
HOODIE_PROPOSED != LOCAL_ONLY
ORIGINAL_HOODIE_BASELINE != CLOUD_ONLY
HOODIE_PROPOSED != ORIGINAL_HOODIE_BASELINE
```

The third proof must include the exact metric or metrics where the two differ.

## Validation Commands

```bash
git diff --check
src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_hoodie_runtime_evaluation_*.py'
src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_hoodie_runtime_evaluation_*.py'
src/.venvmac/bin/python -m analysis.hoodie_runtime_evaluation_runner --write-artifacts artifacts/feature_082_full_runtime_eval
src/.venvmac/bin/python -m analysis.hoodie_runtime_evaluation_runner --validate-artifacts --artifact-dir artifacts/feature_082_full_runtime_eval
```

## Expected Outcome

The final aggregate artifact must prove:

```text
HOODIE_PROPOSED != ORIGINAL_HOODIE_BASELINE
```

in at least one core metric.

If not, the task fails.
