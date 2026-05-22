# Contract: Completion Root-Cause Report Schema

## Required top-level fields

- `feature_id`
- `prerequisite_tags_verified`
- `prior_feature_gates_verified`
- `trace_input_sources`
- `paper_default_runtime_verified`
- `task_lifecycle_reconstruction_summary`
- `root_cause_evaluations`
- `dominant_root_causes`
- `per_action_root_cause_summary`
- `per_queue_root_cause_summary`
- `formula_consistency_summary`
- `deadline_ordering_summary`
- `reward_counter_path_summary`
- `diagnosis`
- `recommended_next_feature`
- `no_runtime_repair_performed`
- `no_training_started`
- `no_optimizer_step`
- `no_replay_training`
- `no_target_update_execution`
- `no_dependency_drift`
- `no_environment_contract_drift`
- `no_policy_drift`
- `no_reward_timing_change`
- `no_timeout_contract_drift`
- `no_capacity_contract_drift`
- `no_transmission_contract_drift`
- `no_action_legality_drift`
- `no_curve_fitting`
- `no_simulator_output_tuning`
- `no_paper_reproduction_claim`
- `final_verdict`

## Root cause evaluation contract

Each `root_cause_evaluations` entry must include:
- `root_cause_class`
- `evaluated`
- `detected`
- `evidence_count`
- `supporting_event_types`
- `representative_task_ids`
- `explanation`
- `confidence`
- `required_next_action`

## Allowed final verdicts

- `root_cause_identified_runtime_repair_required`
- `root_cause_identified_configuration_or_load_explanation`
- `root_cause_identified_policy_or_action_exposure_issue`
- `root_cause_identified_formula_unit_mismatch`
- `no_completion_problem_detected`
- `inconclusive_requires_additional_trace_depth`
- `prerequisite_blocked`

## Verdict discipline

- `runtime_repair_verdict_guard`:
  - `root_cause_identified_runtime_repair_required` is valid only when a runtime-fault class is detected with `evidence_count > 0` and confidence `medium` or `high`.
  - Runtime-fault classes are limited to:
    - `completion_emitted_but_reward_or_counter_path_wrong`
    - `deadline_drop_ordering_issue`
    - `formula_unit_mismatch`
    - `proven_capacity_accounting_inconsistency`
    - `proven_sufficient_budget_drop_violation`
- `runtime_fault_classifier_threshold`:
  - The report must not emit the runtime-repair verdict if no runtime-fault classifier meets the guard above.
- `non_runtime_verdict_rule`:
  - If `completed_count > 0`
  - and `formula_unit_mismatch` detected is false
  - and `deadline_drop_ordering_issue` detected is false
  - and `completion_emitted_but_reward_or_counter_path_wrong` detected is false
  - and `reward_after_terminal_outcome` is true
  - and deadline/drop ordering is supported
  - then `root_cause_identified_runtime_repair_required` is not allowed.
- `execution_progress_deadline_expires_first_interpretation`:
  - `execution_progress_deadline_expires_first` may be detected.
  - It does not alone prove runtime repair.
  - It must route to configuration/load/action-exposure diagnosis unless there is proven sufficient-budget violation evidence.
- `final_verdict_recommended_next_feature_consistency`:
  - `final_verdict` and `recommended_next_feature` must not contradict the detected root causes.
  - `recommended_next_feature = runtime repair` is invalid when `final_verdict` is configuration/load or policy/action-exposure.
  - `execution_progress_deadline_expires_first` must not be the sole trigger for a runtime-repair recommendation.
- Acceptable runtime-fault classes are:
  - `completion_emitted_but_reward_or_counter_path_wrong`
  - `deadline_drop_ordering_issue`
  - `formula_unit_mismatch`
  - a proven capacity or accounting inconsistency
  - a proven task drop despite sufficient remaining budget under the current queues, transmission, and deadline constraints
- If completions exist and formula, reward, and deadline ordering remain consistent, the report must not use the runtime-repair verdict unless one of the runtime-fault classes above is explicitly detected.
- If `execution_progress_deadline_expires_first` is detected without a separate runtime fault, the report must use `root_cause_identified_configuration_or_load_explanation` or `root_cause_identified_policy_or_action_exposure_issue`, not runtime repair.
