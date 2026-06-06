# Report Schema Contract: Selected-Action Outcome Evidence Rerun

The report must be machine-readable and must include the following top-level fields:

```json
{
  "feature_id": "052-selected-action-outcome-evidence-rerun",
  "prerequisite_tags_verified": [],
  "prior_feature_gates_verified": [],
  "feature_051_trace_readiness_verified": false,
  "selected_action_family_evidence_summary": {},
  "selected_action_family_evidence_status": "",
  "selected_action_to_task_join_summary": {},
  "selected_action_to_task_join_status": "",
  "per_action_outcome_join_summary": {},
  "per_action_outcome_evidence_status": "",
  "per_action_outcome_matrix": [],
  "legal_but_unselected_consistency_summary": {},
  "exposure_matrix_internal_consistency_summary": {},
  "feature_049_unblock_assessment": {},
  "behavior_equivalence_passed": false,
  "behavior_equivalence_summary": {},
  "feature_049_can_be_rerun": false,
  "feature_049_remaining_blockers": [],
  "recommended_next_feature": "",
  "no_runtime_repair_performed": true,
  "no_training_started": true,
  "no_optimizer_step": true,
  "no_replay_training": true,
  "no_target_update_execution": true,
  "no_dependency_drift": true,
  "no_policy_drift": true,
  "no_reward_timing_change": true,
  "no_timeout_contract_drift": true,
  "no_capacity_contract_drift": true,
  "no_transmission_contract_drift": true,
  "no_action_legality_drift": true,
  "no_action_selection_drift": true,
  "no_curve_fitting": true,
  "no_simulator_output_tuning": true,
  "no_paper_reproduction_claim": true,
  "final_verdict": ""
}
```

Contract expectations:

- `feature_051_trace_readiness_verified` must be true only when Feature 051 rerun readiness is fully established.
- `selected_action_family_evidence_summary` must report the selected-action family counts, ratios, and consistency state derived from Feature 051 evidence.
- `selected_action_family_evidence_status` must be one of `available`, `partial`, or `unavailable` and must align with the summary copy when present.
- `selected_action_to_task_join_summary` must report the selected-action-to-task join counts, ratios, and missing counts.
- `selected_action_to_task_join_status` must be one of `available`, `partial`, or `unavailable` and must align with the summary copy when present.
- `per_action_outcome_join_summary` must report completion, drop, and pending counts and rates.
- `per_action_outcome_evidence_status` must be one of `available`, `partial`, or `unavailable` and must align with `per_action_outcome_join_summary.per_action_outcome_evidence_status` when present.
- `per_action_outcome_matrix` must preserve the evidence rows used to evaluate outcome rerun readiness.
- `legal_but_unselected_consistency_summary` must report the unselected-but-legal counts and their consistency verification.
- `exposure_matrix_internal_consistency_summary` must report whether selected-action counts and outcome counts remain internally consistent.
- `feature_049_unblock_assessment` must explain whether Feature 049 may be rerun.
- `behavior_equivalence_passed` must equal `behavior_equivalence_summary.passed`.
- `feature_049_can_be_rerun` must be true only when family evidence, task joins, per-action outcomes, legal-but-unselected consistency, exposure consistency, and behavior equivalence all pass.
- `feature_049_remaining_blockers` must be non-empty whenever `feature_049_can_be_rerun` is false.
- `recommended_next_feature` must point to Feature 053 only when Feature 049 is ready for rerun.

Contract failure conditions:

- The contract fails if `feature_051_trace_readiness_verified` is false.
- The contract fails if `selected_action_family_evidence_status` is missing.
- The contract fails if `selected_action_to_task_join_status` is missing.
- The contract fails if `per_action_outcome_evidence_status` is missing as a top-level field in the report body.
- The contract fails if `per_action_outcome_evidence_status` contradicts `per_action_outcome_join_summary.per_action_outcome_evidence_status`.
- The contract fails if `feature_049_can_be_rerun = true` while `per_action_outcome_evidence_status != available`.
- The contract fails if `final_verdict` claims readiness while `per_action_outcome_evidence_status` is partial or unavailable.
- The contract fails if `recommended_next_feature` routes to Feature 053 while `per_action_outcome_evidence_status` is not available.
- The contract fails if `behavior_equivalence_passed` contradicts `behavior_equivalence_summary.passed`.
- The contract fails if `feature_049_can_be_rerun = true` while any required consistency check fails.
- The contract fails if `feature_049_remaining_blockers` is empty while rerun readiness is false.
- The contract fails if `final_verdict` claims readiness while `feature_049_can_be_rerun = false`.

Allowed final verdict values:

- `selected_action_outcome_evidence_ready_for_feature_049_rerun`
- `selected_action_family_evidence_still_incomplete`
- `selected_action_to_task_join_still_incomplete`
- `per_action_outcome_join_still_incomplete`
- `exposure_matrix_internal_consistency_failed`
- `behavior_drift_detected`
- `prerequisite_blocked`
