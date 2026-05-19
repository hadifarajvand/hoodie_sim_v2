# Data Model: Task Completion Lifecycle and Formula Audit

## Entities

### CompletionLifecycleAuditConfig

Represents the immutable audit settings for the feature.

- `feature_id`
- `episode_length`
- `timeout_slots`
- `slot_duration_seconds`
- `seeds`
- `strategies`
- `no_training`
- `no_runtime_mutation`

Validation rules:
- `feature_id` must be `043-task-completion-lifecycle-formula-audit`
- `episode_length` must be `110`
- `timeout_slots` must be `20`
- `slot_duration_seconds` must be `0.1`
- `seeds` must be `[0, 1, 2]`
- `no_training` and `no_runtime_mutation` must be `true`

### FormulaAuditCalculator

Calculates expected task cycles, compute slots, transmission slots, and total slot bounds for each audited path.

Fields:
- `task_size_mbit`
- `processing_density_gcycles_per_mbit`
- `local_cpu_capacity_gcycles_per_slot`
- `public_cpu_capacity_gcycles_per_slot`
- `cloud_cpu_capacity_gcycles_per_slot`
- `horizontal_rate_mbps`
- `vertical_rate_mbps`
- `slot_duration_seconds`
- `timeout_slots`

Derived values:
- expected task cycles
- expected compute slots by host type
- expected transmission slots by action type
- expected minimum total slots by action type

### LifecycleTraceCounters

Captures observed lifecycle results from the existing runtime outputs or passive analysis traces.

Fields:
- `observed_generated_task_count`
- `observed_admitted_task_count`
- `observed_transmission_started_count`
- `observed_transmission_completed_count`
- `observed_execution_started_count`
- `observed_execution_capacity_consumed_gcycles`
- `observed_execution_remaining_cycles_min`
- `observed_execution_remaining_cycles_max`
- `observed_execution_completed_count`
- `observed_completed_task_count`
- `observed_dropped_task_count`
- `observed_pending_at_horizon_count`
- `observed_reward_emitted_count`
- `observed_terminal_transition_count`
- `observed_completion_reward_count`
- `observed_drop_reward_count`
- `max_observed_task_age_slots`
- `max_observed_queue_wait_slots`
- `queue_head_blocked_count`
- `deadline_before_completion_count`
- `completion_before_deadline_count`
- `exact_deadline_completion_count`

Validation rules:
- completion and drop counts must be tracked separately
- pending-at-horizon must remain non-terminal
- reward emission must only be counted for completion or drop terminal events

### CompletionLifecycleAuditReport

Top-level report object written to JSON and Markdown artifacts.

Fields:
- `feature_id`
- `prerequisite_tags_verified`
- `prior_feature_gates_verified`
- `paper_default_runtime_verified`
- `formula_audit_summary`
- `hand_calculation_examples`
- `per_action_lifecycle_results`
- `lifecycle_breakpoint_summary`
- `completion_absence_diagnosis`
- `suspected_root_causes`
- `recommended_next_feature`
- `runtime_contracts_verified`
- `reward_timing_contract_verified`
- `pending_at_horizon_contract_verified`
- anti-training / no-drift / no-tuning / no-reproduction flags
- `final_verdict`

Validation rules:
- all anti-training and no-drift flags must be `true`
- `final_verdict` must be one of the approved diagnostic verdicts
- `recommended_next_feature` must be present whenever the result is inconclusive or a runtime bug is suspected

## Relationships

- `CompletionLifecycleAuditReport` contains one `CompletionLifecycleAuditConfig`
- `FormulaAuditCalculator` feeds `CompletionLifecycleAuditReport`
- `LifecycleTraceCounters` is produced per strategy/seed combination and then aggregated into the report

## State Transitions

- Audit config is immutable once created
- Lifecycle trace counters are collected from existing probe outputs
- The report transitions from draft analysis to finalized artifact after validation passes
