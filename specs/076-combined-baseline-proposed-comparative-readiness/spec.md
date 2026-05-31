# Feature Specification: Combined Baseline + Proposed Comparative Readiness

**Feature Branch**: `076-combined-baseline-proposed-comparative-readiness`  
**Created**: 2026-05-31  
**Status**: Spec Kit created; implementation pending

## Dependency

Feature 076 depends on Feature 075 branch `075-proposed-integration-readiness` at commit `b23b2fa5b1c8fc6d58f3eb533164f83c05c2ec61` or newer.

Feature 074 provides action-bound baseline comparative readiness. Feature 075 provides action-bound proposed-method integration readiness. Feature 076 must combine both layers into one readiness report without claiming final evaluation, statistical significance, superiority, training correctness, or full paper reproduction.

## Goal

Create a read-only combined comparative readiness layer that places baseline policy rows and the proposed method rows into one contract-compatible comparison matrix.

Feature 076 answers this question:

Can the repository present the baseline policies and the proposed method in one action-bound, paper-mode, controlled-scenario comparison structure without overclaiming final results?

## Required Policies / Methods

The combined matrix must include:

- FLC
- VO
- HO
- RO
- BCO
- MLEO
- PROPOSED_DCQ

## Required Scenario Set

Feature 076 must use the same controlled scenario set from Features 073, 074, and 075:

1. `light_load_no_deadline_pressure`
2. `tight_deadline_pressure`
3. `legal_horizontal_offload`
4. `illegal_horizontal_destination_attempt`
5. `cloud_vertical_fallback`
6. `timeout_drop_case`
7. `mixed_local_horizontal_cloud_candidates`

## Required Comparison Contract

Every policy/method and scenario row must expose:

- `policy_id`
- `policy_family`
- `scenario_id`
- `selected_action_id`
- `selected_action_family`
- `action_legality`
- `action_bound_terminal_status`
- `action_bound_reward_value`
- `action_bound_metrics_derived`
- `candidate_or_decision_trace_present`
- `compatibility_mode_used`
- controlled metrics

## Acceptance Criteria

- Create a read-only analysis package under `src/analysis/combined_baseline_proposed_comparative_readiness/`.
- Consume Feature 074 baseline action-bound comparison rows.
- Consume Feature 075 proposed-method action-bound rows.
- Normalize both sources into one combined comparison schema.
- Produce per-policy/method aggregate metrics.
- Preserve Feature 068R through Feature 075 targeted regression evidence.
- Block readiness if any required policy/method or scenario row is missing.
- Block readiness if compatibility mode is used by default.
- Block readiness if any row lacks action-bound metrics.
- No PR is opened and no merge is performed.
- No final evaluation claim is made.
- No policy superiority claim is made.
- No statistical significance claim is made.
- No training claim is made.
- No full paper reproduction claim is made.

## Out of Scope

- Training.
- New policy implementation.
- Proposed method redesign.
- Baseline policy rewrites.
- Runtime helper rewrites.
- Statistical testing.
- Ranking/winner declaration.
- Plot generation.
- Generated artifacts committed to git.
- Dependency or lock-file changes.
- Feature 077+ files.

## Claim Boundary

Feature 076 may claim combined baseline + proposed comparative readiness only. It must not claim final evaluation, superiority, statistical significance, training correctness, or full paper reproduction.
