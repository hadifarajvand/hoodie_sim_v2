# Implementation Plan: Feature 072

**Feature**: End-to-End HOODIE Golden Trace Validation  
**Status**: Spec Kit created; implementation pending  
**Depends On**: Feature 071 runtime semantics alignment

## Summary

Feature 072 validates deterministic end-to-end semantic traces after Feature 070 recovered paper evidence and Feature 071 aligned runtime helper semantics.

The feature must prove that topology legality, deadline strictness, terminal state assignment, and reward emission work together in deterministic scenarios.

## Implementation Boundary

Allowed paths:

- `specs/072-end-to-end-hoodie-golden-trace-validation/**`
- `src/analysis/end_to_end_hoodie_golden_trace_validation/**`
- `tests/unit/test_end_to_end_hoodie_golden_trace_validation_*.py`
- `tests/integration/test_end_to_end_hoodie_golden_trace_validation_*.py`

Forbidden paths:

- `src/training/**`
- `src/agents/**`
- `artifacts/**`
- `resources/**`
- dependency files
- lock files
- generated campaign outputs
- Feature 073+ files
- runtime helper rewrites unless a later repair explicitly requires them

## Execution Order

1. Verify Feature 071 branch and report state.
2. Create golden trace data models.
3. Implement deterministic scenario builder functions.
4. Implement topology legality scenarios using Feature 070 Figure 7 neighbor map.
5. Implement deadline and reward scenarios using Feature 071 helpers.
6. Implement report and renderer.
7. Implement scope validator.
8. Add unit and integration tests.
9. Run Feature 068R, 069, 070, 071, and 072 targeted validations.
10. Commit and push only.

## Scenario Requirements

- Local success before deadline.
- Local timeout at deadline.
- Horizontal legal neighbor using Figure 7.
- Horizontal non-neighbor rejection.
- Horizontal self-destination rejection.
- Cloud vertical success.
- Success reward equals `-Phi`.
- Drop reward equals `-C`.
- Inactive task no-reward sentinel.
- Pending task cannot emit reward.
- Compatibility mode is not default.

## Do Not Proceed Gates

Stop if:

- Feature 071 report does not pass.
- Feature 071 default mode is not paper.
- Feature 070 topology evidence is unavailable.
- The implementation would require training or campaign generation.
- The implementation would rewrite runtime helpers instead of consuming them.

## Validation Gates

- Feature 068R targeted regression.
- Feature 069 targeted regression.
- Feature 070 targeted regression.
- Feature 071 targeted regression.
- Feature 072 unit tests.
- Feature 072 integration tests.
- `git diff --check`.
- Feature 072 scope validator.

## Claim Boundary

Feature 072 may claim deterministic end-to-end semantic trace validation. It must not claim full HOODIE reproduction, training correctness, or performance evaluation readiness.
