# Feature Specification: End-to-End HOODIE Golden Trace Validation

**Feature Branch**: `072-golden-trace-validation`  
**Created**: 2026-05-31  
**Status**: Spec Kit created; implementation pending

## Dependency

Feature 072 depends on Feature 071 branch `071-runtime-paper-faithful-semantics-alignment` at commit `4a3b33388074e60aa4462ce4fb71e282cfccc81c` or newer.

Feature 071 provides paper-mode runtime helpers, explicit compatibility mode, paper-faithful deadline behavior, and reward Eq. (20)-(23) helper behavior.

## Goal

Validate deterministic end-to-end semantic traces:

`task arrival -> action selection -> topology legality -> deadline computation -> terminal state -> reward emission -> expected-vs-actual comparison`

Feature 072 is a deterministic trace validation layer. It is not a training feature, not a campaign feature, and not a full paper reproduction claim.

## Required Scenarios

1. `local_success_before_deadline`
2. `local_timeout_at_deadline`
3. `horizontal_legal_neighbor_figure7`
4. `horizontal_non_neighbor_rejected`
5. `horizontal_self_destination_rejected`
6. `cloud_vertical_success`
7. `success_reward_negative_phi`
8. `drop_reward_negative_c`
9. `inactive_task_no_reward_sentinel`
10. `pending_task_cannot_emit_reward`
11. `compatibility_mode_not_default`

## Rules

- Every scenario must include inputs, expected outputs, actual outputs, and comparison result.
- Every trace must record semantic steps executed.
- Deadline and reward logic must call Feature 071 helpers.
- Horizontal legality must use Feature 070 Figure 7 neighbor map.
- Compatibility behavior must be explicit and not the default.
- A trace must fail if an expected semantic step is missing.

## Acceptance Criteria

- Create a read-only analysis package under `src/analysis/end_to_end_hoodie_golden_trace_validation/`.
- Validate topology, deadline, terminal state, reward, paper-mode default, and compatibility boundary.
- Preserve Feature 068R, 069, 070, and 071 targeted regression gates.
- Feature 072 targeted tests pass.
- Scope validator accepts only approved Feature 072 paths.
- No PR is opened and no merge is performed.
- No full paper reproduction claim is made.

## Out of Scope

- Training.
- Policy rewrite.
- Campaign generation.
- Generated artifacts committed to git.
- Dependency or lock-file changes.
- Feature 073+ files.
- Broad simulator rewrite.

## Claim Boundary

Feature 072 may claim deterministic end-to-end semantic trace validation only. It must not claim full paper reproduction, training correctness, performance reproduction, or campaign evaluation readiness.
