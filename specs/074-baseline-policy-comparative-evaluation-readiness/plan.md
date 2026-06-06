# Implementation Plan: Feature 074

**Feature**: Baseline Policy Comparative Evaluation Readiness  
**Status**: Implemented; action-bound comparative metrics repair required  
**Depends On**: Feature 073 controlled evaluation batch readiness

## Summary

Feature 074 turns Feature 073's controlled batch metrics into a comparative readiness layer across baseline policies. It must remain read-only and must not become training, campaign evaluation, or a performance-superiority claim.

The initial Feature 074 implementation proved registry coverage, full policy/scenario matrix coverage, decision-trace presence, aggregate schema, scope safety, and claim boundaries. The remaining gap is that per-policy metrics can still be identical because Feature 073 scenario metrics are copied as the metric substrate without binding the selected policy action to the controlled outcome.

This repair must make the comparison action-bound:

`policy.choose_action(context) -> selected action -> legality/topology/deadline/reward -> per-policy scenario metrics`

## Implementation Boundary

Allowed paths:

- `specs/074-baseline-policy-comparative-evaluation-readiness/**`
- `src/analysis/baseline_policy_comparative_evaluation_readiness/**`
- `tests/unit/test_baseline_policy_comparative_evaluation_readiness_*.py`
- `tests/integration/test_baseline_policy_comparative_evaluation_readiness_*.py`

Forbidden paths:

- `src/training/**`
- `src/agents/**`
- `artifacts/**`
- `resources/**`
- dependency files
- lock files
- generated campaign outputs
- Feature 075+ files
- runtime helper rewrites
- policy rewrites

## Execution Order

1. Verify Feature 073 report passes.
2. Verify baseline policy registry coverage.
3. Preserve the existing comparative data models and extend them for selected action/outcome binding.
4. Build deterministic per-policy scenario evaluation wrappers.
5. For each policy/scenario row, call the policy and capture the selected action.
6. Map the selected action to an action-aware controlled outcome using Feature 071 helpers and Feature 073 scenario fixtures.
7. Compute per-policy, per-scenario metrics from that action-aware outcome.
8. Compute aggregate per-policy metrics from the scenario rows.
9. Implement report and renderer evidence for action binding.
10. Implement or update scope validator if needed.
11. Add tests for registry coverage, metric comparability, policy inclusion, action binding, no metric substrate passthrough, claim boundary, and prior regressions.
12. Run Feature 068R through Feature 074 targeted validations.
13. Commit and push only.

## Required Policy Coverage

- FLC
- VO
- HO
- RO
- BCO
- MLEO

If any required policy is absent, the report must fail readiness.

## Required Comparative Scenarios

Use Feature 073 controlled scenarios as the base scenario set. Do not invent a separate scenario universe unless required by policy-decision trace adaptation.

## Action-Bound Metric Rules

- A selected local action must produce local/private metrics.
- A selected vertical/cloud action must produce cloud/vertical metrics.
- A selected horizontal action must be checked against Feature 070 Figure 7 topology before public outcome metrics are assigned.
- A selected illegal/unavailable action must produce dropped-unavailable metrics and increment illegal-action rejection.
- Timeout/drop outcomes must use Feature 071 paper-mode deadline semantics.
- Compatibility mode must remain false in the default comparison.
- Metrics must not be copied unchanged from Feature 073 unless the selected action maps to the same controlled path and this mapping is recorded.

## Validation Gates

- Feature 068R targeted regression.
- Feature 069 targeted regression.
- Feature 070 targeted regression.
- Feature 071 targeted regression.
- Feature 072 targeted regression.
- Feature 073 targeted regression.
- Feature 074 unit tests.
- Feature 074 integration tests.
- `git diff --check`.
- Feature 074 scope validator.

## Claim Boundary

Feature 074 may claim comparative evaluation readiness only when policy-selected actions are bound to controlled outcome metrics. It must not claim final evaluation, policy superiority, statistical significance, training correctness, or full paper reproduction.
