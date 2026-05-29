# Feature Specification: Paper Baseline Policy Fidelity Batch

**Feature Branch**: `068-paper-baseline-policy-fidelity-batch`
**Created**: 2026-05-29
**Status**: Draft

## Summary

Define Feature 068 for paper baseline policy fidelity. This feature covers RO, FLC, VO, HO, BCO, and MLEO baseline behavior through the shared policy interface. MLEO must become delay-estimate based across legal candidate actions instead of relying on placeholder hints.

## Scope

In scope:

- Baseline policy fidelity for RO, FLC, VO, HO, BCO, and MLEO.
- Policy registry coverage.
- Legal-action-mask compliance.
- MLEO delay candidate ranking.
- Unit and integration tests for baseline behavior.

Out of scope:

- Simulator lifecycle changes.
- Training changes.
- Neural network changes.
- Campaign artifact regeneration.
- Dependency changes.

## Requirements

- FR-001: All six paper baselines must resolve from the policy registry.
- FR-002: All baselines must use the shared policy context and legal action mask.
- FR-003: FLC must prefer legal local computation.
- FR-004: VO must prefer legal vertical offload.
- FR-005: HO must prefer legal horizontal offload.
- FR-006: RO must choose only from legal actions with controlled seeding.
- FR-007: BCO must use a documented balancing rule.
- FR-008: MLEO must rank legal candidate actions by estimated total delay.
- FR-009: MLEO must exclude illegal candidates before ranking.
- FR-010: Missing estimate inputs must follow documented fallback behavior.
- FR-011: Tests must prove registry coverage, legality, MLEO ranking, fallback behavior, and baseline differentiation.

## Success Criteria

- SC-001: Required baselines resolve successfully.
- SC-002: Baselines never select illegal actions in targeted tests.
- SC-003: MLEO selects the legal minimum-delay candidate in controlled tests.
- SC-004: Controlled observations produce distinguishable behavior for FLC, HO, VO, and MLEO.
- SC-005: No simulator, training, artifact, or dependency files are changed.
