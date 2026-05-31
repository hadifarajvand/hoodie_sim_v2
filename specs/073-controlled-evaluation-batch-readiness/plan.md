# Implementation Plan: Feature 073

**Feature**: Controlled Evaluation Batch Readiness  
**Status**: Spec Kit created; implementation pending  
**Depends On**: Feature 072 golden trace validation

## Summary

Feature 073 turns the deterministic semantic trace layer from Feature 072 into a controlled batch evaluation readiness layer. It must not become training, campaign generation, or final evaluation reporting.

The goal is to prove the repo can execute a small deterministic batch of paper-mode scenarios and compute defensible metrics.

## Implementation Boundary

Allowed paths:

- `specs/073-controlled-evaluation-batch-readiness/**`
- `src/analysis/controlled_evaluation_batch_readiness/**`
- `tests/unit/test_controlled_evaluation_batch_readiness_*.py`
- `tests/integration/test_controlled_evaluation_batch_readiness_*.py`

Forbidden paths:

- `src/training/**`
- `src/agents/**`
- `artifacts/**`
- `resources/**`
- dependency files
- lock files
- generated campaign outputs
- Feature 074+ files
- runtime helper rewrites
- policy rewrites

## Execution Order

1. Verify Feature 072 report passes.
2. Build controlled scenario data models.
3. Build deterministic scenario fixtures.
4. Compute per-scenario metrics.
5. Compute aggregate batch metrics.
6. Implement report and renderer.
7. Implement scope validator.
8. Add tests for metrics, scenario coverage, prior regressions, and claim boundary.
9. Run Feature 068R through Feature 073 targeted validations.
10. Commit and push only.

## Required Scenarios

- Light load with no deadline pressure.
- Tight deadline pressure.
- Legal horizontal offload.
- Illegal horizontal destination attempt.
- Cloud vertical fallback.
- Timeout/drop case.
- Mixed local, horizontal, and cloud candidates.

## Required Metrics

- Completed count.
- Timeout drop count.
- Unavailable drop count.
- Deadline violation count.
- Illegal action rejection count.
- Average delay.
- Average reward.
- Paper-mode success count.
- Compatibility mode usage flag.

## Validation Gates

- Feature 068R targeted regression.
- Feature 069 targeted regression.
- Feature 070 targeted regression.
- Feature 071 targeted regression.
- Feature 072 targeted regression.
- Feature 073 unit tests.
- Feature 073 integration tests.
- `git diff --check`.
- Feature 073 scope validator.

## Claim Boundary

Feature 073 may claim controlled evaluation batch readiness. It must not claim final evaluation, training correctness, performance superiority, or full paper reproduction.
