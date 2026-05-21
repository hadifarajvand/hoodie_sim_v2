# Data Model: Completion Root-Cause Diagnosis

## TaskLifecycleReconstruction

Represents the recovered lifecycle for one task under diagnosis.

Fields:
- `task_id`
- `generated_slot`
- `admitted_slot`
- `selected_action`
- `destination`
- `queue_type`
- `host_node_id`
- `transmission_started_at`
- `transmission_completed_at`
- `execution_started_at`
- `execution_progress_slots`
- `execution_completed_at`
- `deadline_reached_at`
- `deadline_expired_at`
- `task_completed_at`
- `task_dropped_at`
- `reward_emitted_at`
- `terminal_outcome`
- `remaining_cycles_by_slot`
- `task_age_by_slot`
- `queue_wait_time_slots`
- `completed_before_deadline`
- `deadline_or_drop_before_completion`
- `reward_after_terminal_outcome`

Validation rules:
- Lifecycle timestamps must be derived from passive trace evidence only.
- If evidence is missing, the corresponding field must remain unknown rather than inferred.

## RootCauseEvaluation

Represents one candidate explanation for weak or absent completions.

Fields:
- `root_cause_class`
- `evaluated`
- `detected`
- `evidence_count`
- `supporting_event_types`
- `representative_task_ids`
- `explanation`
- `confidence`
- `required_next_action`

Validation rules:
- `confidence` must be one of `low`, `medium`, `high`.
- `detected` can be true for more than one class in the same run.
- A `root_cause_identified_runtime_repair_required` outcome is valid only when at least one runtime-fault class is detected, such as completion/counter-path mismatch, deadline/drop ordering failure, formula unit mismatch, proven capacity or accounting inconsistency, or a proven drop despite sufficient remaining budget under current queues, transmission, and deadline constraints.
- If completions exist and formula, reward, and deadline ordering remain consistent, the report must prefer configuration/load or policy/action-exposure explanations unless a runtime-fault classifier is explicitly detected.
- If execution progress is visible before deadline expiry but the other paths remain valid, the report must treat that evidence as deadline/load pressure unless additional evidence proves a runtime fault.

## DiagnosisReport

Represents the passive analysis artifact produced by the feature.

Fields:
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

Validation rules:
- The report must be generated from paper-default `T = 110` traces.
- The report must preserve the diagnostic distinction between runtime bugs, load/configuration causes, action exposure issues, formula mismatches, and inconclusive evidence.
- The report must never imply repair was performed.
- The report's final verdict must be consistent with the detected root-cause classes and may only recommend runtime repair when a runtime-fault classifier is detected.

## FeatureRoutingOutcome

Represents the follow-up recommendation produced by the diagnosis.

Allowed values:
- `Feature 046 - Runtime Repair for Completion Lifecycle`
- observation vector follow-up
- exploration schedule follow-up
- loss-sequence follow-up
- load/configuration audit follow-up

Validation rules:
- Runtime-proven failures must route to Feature 046.
- Load or action exposure explanations must not route to runtime repair.
- Execution-progress-before-deadline-loss must route to deadline/load pressure unless additional runtime-fault evidence is present.
