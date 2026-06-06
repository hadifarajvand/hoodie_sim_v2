# Feature Specification: Runtime Paper-Faithful Semantics Alignment

**Feature Branch**: `071-runtime-paper-faithful-semantics-alignment`  
**Created**: 2026-05-31  
**Status**: Spec Kit created; implementation pending  
**Input**: Feature 071 converts Feature 070's recovered paper evidence and documented runtime compatibility divergence into explicit runtime behavior.

## Dependency

Feature 071 depends on Feature 070 branch `070-topology-timeout-reward-fidelity-implementation` at commit `3851cd3be63de09189d4ed45c038b34c9ca57aee` or newer.

Feature 070 is accepted for review at evidence level:

- `passed=True`
- `status=blocker_resolution_readiness_with_runtime_divergence`
- topology evidence recovered from Figure 7
- timeout/drop equation evidence recovered
- reward Eq. (20)-(23) recovered
- runtime divergence still visible
- no full paper reproduction claim

Feature 071 must not rewrite Feature 070 history. It must use Feature 070 as evidence input and then align runtime helper semantics.

## Goal

Align the runtime deadline, timeout/drop, terminal-state, and reward helper behavior with the recovered HOODIE paper equations while preserving legacy behavior only as an explicit compatibility mode.

## User Stories

### US1 - Paper-mode deadline strictness
As a researcher, I need paper mode to implement the recovered strict deadline rule so completion at the deadline is treated consistently with the paper success condition.

### US2 - Compatibility mode is explicit
As a maintainer, I need legacy completion-at-deadline behavior to exist only behind an explicit compatibility mode, not as the default paper path.

### US3 - Terminal-state accounting
As a researcher, I need terminal task states to be explicit before reward is emitted.

### US4 - Runtime reward equation alignment
As a researcher, I need runtime reward helpers to implement HOODIE Eq. (20)-(23), including `Phi_priv`, `Phi_pub`, success reward, thrown/drop penalty, and inactive-task no-reward behavior.

### US5 - Regression preservation
As a reviewer, I need Feature 068R, Feature 069, and Feature 070 targeted slices to remain green after runtime alignment.

## Paper-Backed Runtime Contracts

### Deadline contract

- `absolute_deadline_slot = arrival_slot + phi_n(t) - 1`
- paper success requires strict completion before the deadline:
  - `completion_slot < absolute_deadline_slot`
- in paper mode, `completion_slot == absolute_deadline_slot` is timeout/drop.
- in compatibility mode, legacy behavior may allow equality only if explicitly requested.

### Timeout/drop contract

Terminal states must be explicit:

- `completed_private`
- `completed_public`
- `completed_cloud`
- `dropped_timeout`
- `dropped_unavailable`
- `pending`

A completed task must not carry a drop reason. A dropped task must carry terminal evidence and a drop reason.

### Reward contract

Feature 071 must implement the recovered HOODIE reward equations:

- Eq. (20): inactive task -> NaN / explicit no-reward sentinel; success -> `-Phi_n(t)`; thrown/drop -> `-C`
- Eq. (21): `Phi_n(t)` selects private or public delay according to `d_n^(1)`
- Eq. (22): `Phi_priv_n(t) = psi_priv_n(t) - t + 1`
- Eq. (23): `Phi_pub_n(t) = sum_{k,t'} d_{n,k}^{(2)}(t) * (psi_pub_{n,k}(t') - t + 1)`

## Acceptance Criteria

- Paper mode computes strict deadline success.
- Compatibility mode preserves legacy equality behavior explicitly.
- Runtime helper defaults use paper mode for Feature 071 validation.
- Terminal-state consistency is enforced.
- Reward helpers implement Eq. (20)-(23) with concrete tests.
- Inactive task reward behavior is explicit and tested.
- Reward emission happens after terminal evidence.
- Feature 068R regression slice remains green.
- Feature 069 regression slice remains green.
- Feature 070 regression slice remains green.
- No full paper reproduction claim is made.

## Out of Scope

- DRL training.
- Campaign generation or artifact regeneration.
- Feature 072 golden trace validation.
- Dependency or lock-file changes.
- Baseline policy rewrites.
- Broad environment lifecycle rewrites unrelated to deadline, terminal state, or reward semantics.

## Claim Boundary

Feature 071 may claim runtime paper-faithful semantics alignment for deadline, timeout/drop, terminal-state, and reward helper behavior after targeted tests pass. It may not claim complete HOODIE paper reproduction or full evaluation reproduction.
