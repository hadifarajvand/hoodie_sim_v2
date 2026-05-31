# Implementation Plan: Feature 074

**Feature**: Baseline Policy Comparative Evaluation Readiness  
**Status**: Spec Kit created; implementation pending  
**Depends On**: Feature 073 controlled evaluation batch readiness

## Summary

Feature 074 turns Feature 073's controlled batch metrics into a comparative readiness layer across baseline policies. It must remain read-only and must not become training, campaign evaluation, or a performance-superiority claim.

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
3. Build comparative data models.
4. Build deterministic per-policy scenario evaluation wrappers.
5. Compute per-policy, per-scenario metrics.
6. Compute aggregate per-policy metrics.
7. Implement report and renderer.
8. Implement scope validator.
9. Add tests for registry coverage, metric comparability, policy inclusion, claim boundary, and prior regressions.
10. Run Feature 068R through Feature 074 targeted validations.
11. Commit and push only.

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

Feature 074 may claim comparative evaluation readiness. It must not claim final evaluation, policy superiority, statistical significance, training correctness, or full paper reproduction.
