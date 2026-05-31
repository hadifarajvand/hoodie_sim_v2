# Feature Specification: Baseline Policy Comparative Evaluation Readiness

**Feature Branch**: `074-baseline-policy-comparative-evaluation-readiness`  
**Created**: 2026-05-31  
**Status**: Spec Kit created; implementation pending

## Dependency

Feature 074 depends on Feature 073 branch `073-controlled-evaluation-batch-readiness` at commit `d7ec5c4e69ea0faf3220e40a00f1bff1ada05c6d` or newer.

Feature 073 provides controlled evaluation batch readiness with deterministic paper-mode metrics, Figure 7 topology consumption, Feature 071 runtime helper consumption, Feature 072 golden trace prerequisite evidence, and no final evaluation claim.

## Goal

Create a read-only comparative evaluation readiness layer that runs the controlled Feature 073 scenarios across the paper baseline policies and reports comparable metrics per policy.

Feature 074 answers this question:

Can the repository compare baseline policy behavior over the controlled paper-semantic batch without training, campaign generation, or performance-superiority claims?

## Baseline Policy Set

The comparative layer must use the existing policy registry and baseline policy implementations. The expected baseline policy families are:

- FLC
- VO
- HO
- RO
- BCO
- MLEO

The implementation must not rewrite baseline policies. If a policy is unavailable in the registry, the report must block readiness rather than silently omit it.

## Required Comparative Scenarios

Feature 074 must compare policies over the controlled scenarios from Feature 073:

1. `light_load_no_deadline_pressure`
2. `tight_deadline_pressure`
3. `legal_horizontal_offload`
4. `illegal_horizontal_destination_attempt`
5. `cloud_vertical_fallback`
6. `timeout_drop_case`
7. `mixed_local_horizontal_cloud_candidates`

## Required Metrics

Per policy and per scenario:

- `completed_count`
- `dropped_timeout_count`
- `dropped_unavailable_count`
- `deadline_violation_count`
- `illegal_action_rejection_count`
- `average_delay`
- `average_reward`
- `paper_mode_success_count`
- `compatibility_mode_used`
- `policy_action_family`
- `policy_decision_trace_present`

Aggregate per policy:

- scenario count
- total completed count
- total timeout drops
- total unavailable drops
- total deadline violations
- total illegal action rejections
- mean delay
- mean reward
- compatibility mode usage flag

## Acceptance Criteria

- Create a read-only analysis package under `src/analysis/baseline_policy_comparative_evaluation_readiness/`.
- Consume Feature 073 controlled batch scenarios and metrics.
- Consume the existing policy registry and baseline policy implementations.
- Compare all required baseline policies over all required controlled scenarios.
- Produce per-policy and aggregate comparison metrics.
- Preserve Feature 068R, 069, 070, 071, 072, and 073 targeted regression evidence.
- Block readiness if any required baseline policy is missing.
- Block readiness if compatibility mode is used in default comparative evaluation.
- No PR is opened and no merge is performed.
- No final evaluation claim is made.
- No performance superiority claim is made.
- No full paper reproduction claim is made.

## Out of Scope

- DRL training.
- Neural network updates.
- Policy rewrites.
- New proposed method integration.
- Large stochastic campaigns.
- Plot generation.
- Generated artifacts committed to git.
- Dependency or lock-file changes.
- Feature 075+ files.

## Claim Boundary

Feature 074 may claim baseline policy comparative evaluation readiness only. It must not claim final evaluation results, statistical significance, training correctness, policy superiority, or full HOODIE reproduction.
