# Report Schema Contract: Selected-Action Family and Per-Action Outcome Evidence Expansion

The report must be machine-readable and must include the following top-level fields:

```json
{
  "feature_id": "050-selected-action-family-per-action-outcome-evidence",
  "prerequisite_tags_verified": [],
  "prior_feature_gates_verified": [],
  "selected_action_family_evidence_status": "",
  "selected_action_to_task_join_status": "",
  "per_action_outcome_evidence_status": "",
  "behavior_equivalence_passed": false,
  "feature_049_can_be_rerun": false,
  "feature_049_remaining_blockers": [],
  "feature_049_unblock_assessment": {},
  "selected_action_family_evidence_summary": {},
  "per_strategy_seed_selected_action_family_matrix": [],
  "selected_action_to_task_join_summary": {},
  "per_action_outcome_join_summary": {},
  "per_action_outcome_matrix": {},
  "legal_but_unselected_consistency_summary": {},
  "exposure_matrix_internal_consistency_summary": {},
  "behavior_equivalence_summary": {},
  "evidence_population_summary": {},
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
  "final_verdict": "",
  "recommended_next_feature": ""
}
```

Contract expectations:

- `selected_action_family_evidence_status`, `selected_action_to_task_join_status`, `per_action_outcome_evidence_status`, `behavior_equivalence_passed`, `feature_049_can_be_rerun`, and `feature_049_remaining_blockers` must appear both at the top level and inside `feature_049_unblock_assessment`.
- `selected_action_family_evidence_summary` must distinguish available from unavailable family evidence and never use placeholder zeros to mask missing rows.
- `selected_action_family_evidence_status`, `selected_action_to_task_join_status`, and `per_action_outcome_evidence_status` must each use the allowed values `available`, `partial`, and `unavailable`.
- `per_strategy_seed_selected_action_family_matrix` must preserve traceability by strategy, seed, slot, agent_id, task_id, and selected action metadata.
- `selected_action_to_task_join_summary` must explain how selected actions are joined to task identifiers and what prevents a join from being completed.
- `per_action_outcome_join_summary` must explain how selected actions are joined to terminal lifecycle outcomes.
- `per_action_outcome_matrix` must report completion, drop, and pending counts/rates only when the corresponding evidence is available.
- `legal_but_unselected_consistency_summary` must document whether legal counts and selected-family counts reconcile.
- `exposure_matrix_internal_consistency_summary` must explain whether the evidence is sufficient to unblock Feature 049 rerun readiness.
- `feature_049_unblock_assessment` must contain `feature_049_can_be_rerun`, `feature_049_remaining_blockers`, `selected_action_family_evidence_status`, `selected_action_to_task_join_status`, `per_action_outcome_evidence_status`, `exposure_matrix_internal_consistency_verified`, `behavior_equivalence_passed`, and `recommended_next_feature`.
- `behavior_equivalence_passed` must exactly equal `behavior_equivalence_summary.passed` at the top level and inside `feature_049_unblock_assessment`.
- `feature_049_can_be_rerun` may be true only when selected-action family evidence, selected-action-to-task joins, per-action outcome evidence, `exposure_matrix_internal_consistency_verified`, `behavior_equivalence_passed`, `no_action_selection_drift`, and `no_action_legality_drift` are all satisfied.
- `feature_049_remaining_blockers` must be non-empty whenever `feature_049_can_be_rerun` is false.
- `behavior_equivalence_summary` must use unique check names and report whether passive capture changed the selected action sequence or terminal outcomes.
- `recommended_next_feature` must not point to training when an evidence gap remains.
- The report must fail validation if top-level `behavior_equivalence_passed` is missing, nested `behavior_equivalence_passed` is missing, top-level and nested values contradict, `behavior_equivalence_passed` contradicts `behavior_equivalence_summary.passed`, `feature_049_can_be_rerun = true` while `behavior_equivalence_passed = false`, `final_verdict` claims readiness while `behavior_equivalence_passed = false`, or `feature_049_remaining_blockers` omits `behavior_equivalence_failed` when `behavior_equivalence_passed = false`.

Allowed final verdict values:

- `selected_action_outcome_evidence_ready_for_feature_049_rerun`
- `selected_action_family_evidence_incomplete`
- `per_action_outcome_join_incomplete`
- `exposure_matrix_internal_consistency_failed`
- `behavior_drift_detected`
- `prerequisite_blocked`
