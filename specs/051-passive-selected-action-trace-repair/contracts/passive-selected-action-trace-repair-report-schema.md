# Report Schema Contract: Passive Selected-Action Trace Repair

The report must be machine-readable and must include the following top-level fields:

```json
{
  "feature_id": "051-passive-selected-action-trace-repair",
  "prerequisite_tags_verified": [],
  "prior_feature_gates_verified": [],
  "selected_action_trace_schema": {},
  "selected_action_trace_emission_summary": {},
  "decision_opportunity_count": 0,
  "selected_action_trace_record_count": 0,
  "selected_action_family_trace_record_count": 0,
  "selected_action_to_task_join_key_count": 0,
  "terminal_outcome_join_key_count": 0,
  "selected_action_trace_coverage_ratio": 0.0,
  "selected_action_family_coverage_ratio": 0.0,
  "selected_action_to_task_join_coverage_ratio": 0.0,
  "terminal_outcome_join_key_coverage_ratio": 0.0,
  "missing_selected_action_trace_count": 0,
  "missing_selected_action_family_count": 0,
  "missing_selected_action_to_task_join_key_count": 0,
  "missing_terminal_outcome_join_key_count": 0,
  "selected_action_family_trace_summary": {},
  "selected_action_family_evidence_status": "",
  "selected_action_to_task_join_summary": {},
  "selected_action_to_task_join_status": "",
  "terminal_outcome_join_key_summary": {},
  "terminal_outcome_join_status": "",
  "per_action_outcome_join_readiness": "",
  "behavior_equivalence_passed": false,
  "behavior_equivalence_summary": {},
  "evidence_readiness_for_feature_050_rerun": false,
  "remaining_blockers": [],
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

- `selected_action_trace_schema` must describe the passive fields needed for selected-action repair.
- `selected_action_trace_emission_summary` must describe whether each required trace field is actually emitted.
- If `selected_action_trace_emission_summary` reports that selected-action fields are emitted, the contract also requires populated runtime evidence counts, coverage ratios, and missing-count metrics proving that the trace records exist.
- `selected_action_family_trace_summary` must describe whether the trace can support local, horizontal, vertical, or unknown family derivation.
- `selected_action_family_evidence_status` must be one of `available`, `partial`, or `unavailable` and must match `selected_action_family_trace_summary.selected_action_family_evidence_status` when that summary field is present.
- `selected_action_family_evidence_status` is `available` only when `selected_action_family_trace_record_count == decision_opportunity_count` and `decision_opportunity_count > 0`.
- `selected_action_family_evidence_status` is `partial` when `0 < selected_action_family_trace_record_count < decision_opportunity_count`.
- `selected_action_family_evidence_status` is `unavailable` when `selected_action_family_trace_record_count == 0` or `decision_opportunity_count` is missing, zero, or otherwise not explained by the report.
- `selected_action_to_task_join_summary` must explain how selected actions are linked to task identity.
- `selected_action_to_task_join_status` must be one of `available`, `partial`, or `unavailable` and must match `selected_action_to_task_join_summary.selected_action_to_task_join_status` when that summary field is present.
- `selected_action_to_task_join_status` is `available` only when `selected_action_to_task_join_key_count == decision_opportunity_count` and every join key deterministically maps a selected action to `task_id`.
- `selected_action_to_task_join_status` is `partial` when some but not all selected actions have valid task join keys.
- `selected_action_to_task_join_status` is `unavailable` when no valid selected-action-to-task join keys exist.
- `terminal_outcome_join_key_summary` must explain how task outcomes can be linked back to selected actions.
- `terminal_outcome_join_status` must be one of `available`, `partial`, or `unavailable` and must match `terminal_outcome_join_key_summary.terminal_outcome_join_status` when that summary field is present.
- `terminal_outcome_join_status` is `available` only when `terminal_outcome_join_key_count == decision_opportunity_count` and each key deterministically supports the selected action -> task_id -> terminal lifecycle outcome path.
- `terminal_outcome_join_status` is `partial` when some but not all selected actions have terminal outcome join keys.
- `terminal_outcome_join_status` is `unavailable` when no valid terminal outcome join keys exist.
- `per_action_outcome_join_readiness` must be one of `ready`, `partial`, or `unavailable` and must align with the overall Feature 050 rerun readiness logic.
- `per_action_outcome_join_readiness` is `ready` only when `selected_action_family_evidence_status = available`, `selected_action_to_task_join_status = available`, `terminal_outcome_join_status = available`, and terminal lifecycle events can be joined through the emitted keys.
- `per_action_outcome_join_readiness` is `partial` when joins exist but are incomplete.
- `per_action_outcome_join_readiness` is `unavailable` when selected-action family evidence or join keys are unavailable.
- `behavior_equivalence_passed` must be exposed as a top-level report field and must equal `behavior_equivalence_summary.passed`.
- `behavior_equivalence_summary` must explain whether passive trace repair changed selected action sequence, rewards, or terminal outcomes.
- `evidence_readiness_for_feature_050_rerun` must be `true` only when `decision_opportunity_count > 0`, `selected_action_family_evidence_status = available`, `selected_action_to_task_join_status = available`, `terminal_outcome_join_status = available`, `per_action_outcome_join_readiness = ready`, `behavior_equivalence_summary.passed = true`, `no_action_selection_drift = true`, and `no_action_legality_drift = true`.
- `remaining_blockers` must be non-empty whenever `evidence_readiness_for_feature_050_rerun` is `false`.
- `recommended_next_feature` must point to Feature 052 only when the passive trace is ready for the Feature 050 rerun path.

Contract failure conditions:

- The contract fails if `decision_opportunity_count` is missing.
- The contract fails if any count, coverage ratio, or missing-count field is missing when selected-action trace emission is claimed.
- The contract fails if `selected_action_family_evidence_status` is missing.
- The contract fails if `selected_action_to_task_join_status` is missing.
- The contract fails if `terminal_outcome_join_status` is missing.
- The contract fails if `per_action_outcome_join_readiness` is missing.
- The contract fails if `behavior_equivalence_passed` is missing.
- The contract fails if any top-level status contradicts its summary copy.
- The contract fails if `behavior_equivalence_passed` contradicts `behavior_equivalence_summary.passed`.
- The contract fails if `selected_action_trace_emission_summary.selected_action_emitted_at_decision_point = true` but `selected_action_trace_record_count = 0`.
- The contract fails if `selected_action_trace_emission_summary.selected_action_to_task_join_key_emitted = true` but `selected_action_to_task_join_key_count = 0`.
- The contract fails if `selected_action_trace_emission_summary.terminal_outcome_join_key_emitted = true` but `terminal_outcome_join_key_count = 0`.
- The contract fails if required schema fields are listed but no runtime trace record contains them.
- The contract fails if `evidence_readiness_for_feature_050_rerun = true` while any required status is `partial` or `unavailable`.
- The contract fails if `evidence_readiness_for_feature_050_rerun = true` while `per_action_outcome_join_readiness != ready`.
- The contract fails if `evidence_readiness_for_feature_050_rerun = true` while `behavior_equivalence_summary.passed = false`.
- The contract fails if `final_verdict` claims readiness while `evidence_readiness_for_feature_050_rerun = false`.
- The contract fails if `remaining_blockers` is empty while readiness is false.

Allowed final verdict values:

- `passive_selected_action_trace_ready_for_feature_050_rerun`
- `selected_action_family_trace_incomplete`
- `selected_action_to_task_join_incomplete`
- `terminal_outcome_join_key_incomplete`
- `behavior_drift_detected`
- `prerequisite_blocked`
