# Implementation Plan: Feature 070

**Feature**: Topology, Timeout/Drop, and Reward Fidelity  
**Status**: Spec Kit handoff; implementation blocked until this Spec Kit is merged  
**Depends On**: Feature 069 merged into `main`

## Summary

Feature 070 resolves the three blockers recorded by Feature 069: structured topology evidence, timeout/drop accounting, and reward equation fidelity. These three areas are related and may be implemented in one feature, but the implementation must remain phased, contract-bound, and test-driven.

## Implementation Boundary

Expected future implementation areas may include:

- `src/analysis/topology_timeout_reward_fidelity/` for read-only evidence models and report generation.
- Targeted topology helper modules only if existing structured evidence is insufficient and the Spec Kit requires a reusable contract.
- Targeted timeout/drop accounting helpers only if they do not rewrite unrelated simulator lifecycle behavior.
- Targeted reward-equation helpers only if the recovered equation is explicitly sourced and tested.
- Targeted unit and integration tests.

Forbidden unless a later Spec Kit update approves them:

- DRL training changes.
- Campaign artifact regeneration.
- Dependency or lock-file changes.
- Feature 071 or later work.
- Baseline-policy rewrites unrelated to these three blockers.

## Phased Execution Order

1. Confirm Feature 069 is present in `main`.
2. Read Feature 069 report implementation and blocker list.
3. Read the paper mechanism registry and paper-to-code mapping.
4. Build tests for topology evidence first.
5. Build tests for timeout/drop terminal accounting second.
6. Build tests for reward equation and terminal reward fidelity third.
7. Implement the smallest source changes needed for each contract.
8. Produce an integrated Feature 070 report.
9. Run Feature 068R + Feature 069 regression gates.
10. Run targeted Feature 070 validations.
11. Run scope audit.

## Validation Gates

- Feature 068R regression gate.
- Feature 069 mechanism report gate.
- Structured topology contract gate.
- Neighbor legality gate.
- Timeout/drop terminal accounting gate.
- Reward equation source gate.
- Terminal reward emission gate.
- Integrated report schema gate.
- Scope audit gate.

## Do Not Proceed Gates

Do not start implementation if:

- Feature 069 is not present in `main`.
- The branch is stale relative to `origin/main`.
- The paper evidence for a claimed equation or topology edge is missing.
- The implementation would invent topology, timeout/drop, or reward semantics.
- The implementation would require campaign output regeneration.

## Complexity Control

This feature is deliberately larger than previous features because it combines three blockers. That is acceptable only if each blocker remains independently testable and independently reportable.

## Claim Boundary

The feature may claim resolved evidence only for blockers actually closed by tests and structured source evidence. Any unresolved item must remain in the report as a blocker or assumption-backed item.
