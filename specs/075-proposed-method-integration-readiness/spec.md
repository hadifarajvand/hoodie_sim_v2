# Feature Specification: Proposed Method Integration Readiness

**Feature Branch**: `075-proposed-integration-readiness`  
**Created**: 2026-05-31  
**Status**: Spec Kit created; implementation pending

## Dependency

Feature 075 depends on Feature 074 branch `074-baseline-policy-comparative-evaluation-readiness` at commit `b9d847d5f0777e17d223b7f78ff738bff79e8b0e` or newer.

Feature 074 provides action-bound baseline comparative readiness. Feature 075 must add the proposed method as a contract-compatible, action-bound, traceable policy candidate without training or final evaluation claims.

## Goal

Create a read-only proposed-method integration readiness layer that proves the proposed deadline-aware method can enter the same action-bound comparison contract used by Feature 074.

Feature 075 answers this question:

Can the proposed deadline-aware method produce traceable candidate rankings, selected actions, legality checks, terminal outcomes, rewards, and metrics over the controlled scenario set without training or overclaiming?

## Proposed Method Scope

The proposed method is a deterministic readiness policy, not a trained DRL agent in this feature.

Working name:

- `PROPOSED_DCQ`

Policy family:

- `proposed_deadline_queueing`

Decision evidence must include:

- candidate actions
- candidate legality
- deadline slack or timeout-risk evidence
- estimated delay evidence
- queue/load evidence or explicit unavailable marker
- reward-risk evidence
- selected action
- selection rationale

## Required Scenario Set

Feature 075 must evaluate the proposed method over the same controlled scenarios used by Feature 073 and Feature 074:

1. `light_load_no_deadline_pressure`
2. `tight_deadline_pressure`
3. `legal_horizontal_offload`
4. `illegal_horizontal_destination_attempt`
5. `cloud_vertical_fallback`
6. `timeout_drop_case`
7. `mixed_local_horizontal_cloud_candidates`

## Required Output Contract

For every scenario, the proposed method must output:

- `selected_action_id`
- `selected_action_family`
- `candidate_ranking_trace_present`
- `deadline_slack_evidence_present`
- `queue_or_load_evidence_present`
- `topology_legality_enforced`
- `action_bound_terminal_status`
- `action_bound_reward_value`
- `action_bound_metrics_derived`
- `compatibility_mode_used`

## Acceptance Criteria

- Create a read-only analysis package under `src/analysis/proposed_method_integration_readiness/`.
- Do not modify baseline policies, runtime helpers, agents, training code, dependency files, or generated artifacts.
- Evaluate `PROPOSED_DCQ` over all required controlled scenarios.
- Produce candidate ranking and selection evidence for every scenario.
- Enforce Feature 070 Figure 7 topology legality for horizontal candidates.
- Use Feature 071 paper-mode terminal and reward helpers.
- Consume Feature 073 controlled scenario fixtures.
- Remain contract-compatible with Feature 074 action-bound comparison rows.
- Preserve Feature 068R through Feature 074 targeted regression evidence.
- Block readiness if selected action cannot be mapped to an action-bound controlled outcome.
- Block readiness if compatibility mode is used in default proposed-method evaluation.
- No PR is opened and no merge is performed.
- No training claim is made.
- No final evaluation claim is made.
- No performance superiority claim is made.
- No full paper reproduction claim is made.

## Out of Scope

- DRL training.
- Neural network implementation.
- Proposed method final evaluation.
- Baseline policy rewrites.
- Runtime helper rewrites.
- Large stochastic campaigns.
- Plot generation.
- Generated artifacts committed to git.
- Dependency or lock-file changes.
- Feature 076+ files.

## Claim Boundary

Feature 075 may claim proposed method integration readiness only. It must not claim final proposed-method evaluation, policy superiority, statistical significance, training correctness, or full HOODIE reproduction.
