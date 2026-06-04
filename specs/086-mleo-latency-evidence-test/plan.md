# Implementation Plan: Feature 086 MLEO Latency Evidence Test

## Branch

`086-mleo-latency-evidence-test`

Base branch: `085-hoodie-paper-baseline-fidelity-audit`

Base SHA at creation: `abc7539b064912e8db5749945f009e2ea4705d15`

## Problem

Feature 085 repaired the active baseline label to `MLEO` and regenerated artifacts. The remaining review risk is that `HOODIE` and `MLEO` tie exactly across all aggregate metrics. That does not automatically mean the implementation is wrong, but it must be explained with numeric evidence.

## Implementation Steps

### Phase 1 — Inspect Existing MLEO Implementation

1. Inspect `src/policies/mleo.py`.
2. Inspect `src/analysis/hoodie_runtime_evaluation_runner/policies.py`.
3. Inspect tests in `tests/unit/test_hoodie_runtime_evaluation_runner_policies.py` and related policy tests.
4. Confirm where candidate latency details are exposed: `last_candidates`, adapter trace detail, or runtime row metadata.

### Phase 2 — Add Numeric MLEO Unit Tests

Add tests that construct a controlled context where:

- local has the smallest queue but not the smallest total latency;
- horizontal or vertical has the smallest total latency;
- MLEO must select the minimum-total-delay candidate;
- candidate `total_delay` values are asserted explicitly.

The test must fail for a pure queue-length-only implementation.

### Phase 3 — Add Tie Evidence

If the aggregate benchmark still ties `HOODIE` and `MLEO`, add evidence explaining the tie.

Preferred evidence:

- Count selected actions by policy and scenario.
- Compare `HOODIE` and `MLEO` selected action traces over the deterministic benchmark.
- Add a report field such as `hoodie_mleo_tie_evidence` explaining whether selected actions are identical in every row or whether metric equality arises after different actions.

### Phase 4 — Update Docs and Gates

Update Feature 086 docs and mark tasks complete only after code/test evidence exists.

## Codex Implementation Prompt

```text
You are working in repository `/Users/hadi/Documents/GitHub/hoodie_sim_v2` on branch `086-mleo-latency-evidence-test`.

Goal: Add numeric evidence tests proving that MLEO is a real minimum latency estimation baseline and not a renamed minimum-queue policy. Do not introduce any thesis method, DCQ method, custom queue redesign, or new proposed method.

Context:
- Feature 085 repaired the paper baseline set to HOODIE, RO, FLC, VO, HO, BCO, MLEO.
- Feature 085 artifacts show HOODIE and MLEO tied exactly across aggregate metrics.
- That tie may be valid, but it must be supported by evidence.
- The main implementation under review is `MinimumLatencyEstimateOffloadingPolicy` in `src/policies/mleo.py` and the runtime adapter in `src/analysis/hoodie_runtime_evaluation_runner/policies.py`.

Required changes:

1. Add numeric MLEO policy tests.
   - Create or update an appropriate unit test file, preferably `tests/unit/test_hoodie_runtime_evaluation_runner_policies.py` or a focused `tests/unit/test_mleo_latency_evidence.py`.
   - Construct a deterministic context with at least three candidates: local, horizontal, vertical.
   - Ensure the smallest queue-length candidate is NOT the smallest total-latency candidate.
   - Assert that MLEO selects the candidate with the smallest `total_delay`, not the smallest queue length.
   - Assert candidate total delay values explicitly by inspecting `last_candidates` or adapter trace details.
   - The test must fail if MLEO is implemented as queue-length-only behavior.

2. Add tie evidence for HOODIE vs MLEO.
   - Inspect generated Feature 085 raw rows and/or runtime traces.
   - Determine whether HOODIE and MLEO select identical actions across deterministic scenarios or whether they differ but aggregate metrics tie.
   - Add a report field, artifact, or test assertion documenting the tie reason.
   - Preferred output: update `artifacts/feature_085_full_audit/feature_085_audit_report.json` and `.md` or generate a small Feature 086 artifact directory such as `artifacts/feature_086_mleo_latency_evidence/`.
   - Do not overclaim full paper reproduction.

3. Add/adjust tests for tie evidence.
   - Add a test that reads the generated evidence and fails if the HOODIE/MLEO tie is undocumented.
   - If HOODIE and MLEO selected actions are identical in all benchmark rows, assert that explicitly and include counts by scenario.
   - If they differ, assert the metric tie explanation and include counts.

4. Documentation.
   - Update `specs/086-mleo-latency-evidence-test/tasks.md` with completed tasks.
   - Update `specs/086-mleo-latency-evidence-test/quickstart.md` with exact validation commands.
   - Update `specs/086-mleo-latency-evidence-test/contracts/validation-rules.md` if the implemented evidence format differs from this plan.

Validation commands:
- `git diff --check`
- `src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_hoodie_runtime_evaluation_*.py'`
- `src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_*mleo*.py'`
- `src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_hoodie_runtime_evaluation_*.py'`
- `src/.venvmac/bin/python -m analysis.hoodie_runtime_evaluation_runner --validate-artifacts --artifact-dir artifacts/feature_085_full_audit`

Commit message:
`Implement Feature 086 MLEO latency evidence test`

Final response must include:
- branch name
- final commit SHA
- files changed
- exact tests run and results
- whether MLEO passed the non-queue-only numeric test
- HOODIE/MLEO tie explanation
- remaining limitations
```
