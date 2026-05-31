# Feature Specification: Controlled Evaluation Batch Readiness

**Feature Branch**: `073-controlled-evaluation-batch-readiness`  
**Created**: 2026-05-31  
**Status**: Spec Kit created; implementation pending

## Dependency

Feature 073 depends on Feature 072 branch `072-golden-trace-validation` at commit `66f140c020ddf7f362d331523148782d923f2bdf` or newer.

Feature 072 provides deterministic end-to-end semantic trace validation. Feature 073 must build a controlled evaluation batch layer on top of that validated semantic path.

## Goal

Create a deterministic controlled evaluation batch readiness layer that can execute a small suite of paper-semantic scenarios and produce metrics without claiming training, campaign reproduction, or final performance results.

Feature 073 answers this question:

Can the repository run controlled multi-scenario evaluations with paper-mode semantics, prior feature regressions, and defensible metrics?

## Required Evaluation Scenarios

Feature 073 must include at least these controlled scenarios:

1. `light_load_no_deadline_pressure`
2. `tight_deadline_pressure`
3. `legal_horizontal_offload`
4. `illegal_horizontal_destination_attempt`
5. `cloud_vertical_fallback`
6. `timeout_drop_case`
7. `mixed_local_horizontal_cloud_candidates`

## Required Metrics

Every scenario and batch report must expose:

- `completed_count`
- `dropped_timeout_count`
- `dropped_unavailable_count`
- `deadline_violation_count`
- `illegal_action_rejection_count`
- `average_delay`
- `average_reward`
- `paper_mode_success_count`
- `compatibility_mode_used`

`compatibility_mode_used` must be `False` for the default controlled evaluation batch.

## Acceptance Criteria

- Create a read-only analysis package under `src/analysis/controlled_evaluation_batch_readiness/`.
- Create deterministic controlled scenarios.
- Use Feature 071 paper-mode helpers for deadline and reward semantics.
- Use Feature 070 Figure 7 topology for horizontal legality.
- Use Feature 072 golden trace report as a prerequisite gate.
- Produce per-scenario and aggregate metrics.
- Preserve Feature 068R, 069, 070, 071, and 072 targeted regression evidence.
- No PR is opened and no merge is performed.
- No full paper reproduction claim is made.

## Out of Scope

- DRL training.
- Neural network changes.
- Policy rewrites.
- Large simulation campaigns.
- Plot generation.
- Generated artifacts committed to git.
- Dependency or lock-file changes.
- Feature 074+ files.

## Claim Boundary

Feature 073 may claim controlled evaluation batch readiness only. It must not claim final evaluation results, baseline superiority, full HOODIE reproduction, or campaign-level validity.
