# Data Model: Load, Admission, and Action-Exposure Review

## Entities

### LoadPressureMetrics
- **Purpose**: Summarize the overall amount of work created, admitted, completed, dropped, and left pending.
- **Attributes**:
  - `generated_task_count`
  - `admitted_task_count`
  - `terminal_task_count`
  - `completed_task_count`
  - `dropped_task_count`
  - `pending_at_horizon_count`
  - `generated_per_slot`
  - `admitted_per_slot`
  - `terminal_per_slot`
  - `completion_rate`
  - `drop_rate`
  - `pending_rate`
- **Validation**:
  - Counts must be non-negative integers.
  - Rates must be between 0 and 1 when defined.

### AdmissionSerializationMetrics
- **Purpose**: Quantify same-slot arrival and serialized admission delay.
- **Attributes**:
  - `same_slot_generated_count`
  - `same_slot_admitted_count`
  - `serialized_admission_backlog_count`
  - `max_serialization_lag_slots`
  - `mean_serialization_lag_slots`
  - `tasks_delayed_by_serialization`
  - `tasks_expired_after_serialization_delay`
- **Validation**:
  - Serialization lag must be non-negative.
  - Tasks delayed by serialization must be a subset of admitted tasks with measurable delay.

### ActionExposureMetrics
- **Purpose**: Compare legal action availability against selected action distribution and outcomes.
- **Attributes**:
  - `legal_local_count`
  - `legal_horizontal_count`
  - `legal_vertical_count`
  - `selected_local_count`
  - `selected_horizontal_count`
  - `selected_vertical_count`
  - `exposure_ratio_by_action`
  - `selection_ratio_by_action`
  - `legal_but_unselected_by_action`
  - `action_entropy`
  - `per_action_completion_rate`
  - `per_action_drop_rate`
  - `per_action_pending_rate`
- **Validation**:
  - Action counts must be non-negative.
  - Exposure and selection ratios must sum consistently for the evaluated action set.

### QueuePressureMetrics
- **Purpose**: Describe pressure across queue families.
- **Attributes**:
  - `private_queue_admission_count`
  - `public_queue_admission_count`
  - `cloud_queue_admission_count`
  - `private_queue_terminal_count`
  - `public_queue_terminal_count`
  - `cloud_queue_terminal_count`
  - `per_queue_completion_rate`
  - `per_queue_drop_rate`
  - `queue_wait_time_mean`
  - `queue_wait_time_max`
  - `queue_pressure_index`
- **Validation**:
  - Queue wait times must be non-negative.
  - Queue pressure index must be derived from observed queue delay and terminal outcomes.

### OffloadPathPressureMetrics
- **Purpose**: Capture transmission and offload execution delays.
- **Attributes**:
  - `transmission_started_count`
  - `transmission_completed_count`
  - `transmission_delay_slots_mean`
  - `transmission_delay_slots_max`
  - `transmission_to_admission_lag`
  - `execution_start_after_transmission_lag`
  - `offloaded_completed_count`
  - `offloaded_dropped_count`
  - `offloaded_pending_count`
- **Validation**:
  - Transmission delay and lag values must be non-negative.
  - Offloaded terminal counts must not exceed offloaded admissions.

### BudgetComparisonMetrics
- **Purpose**: Compare representative tasks against expected budget and observed terminal behavior.
- **Attributes**:
  - `representative_task_ids`
  - `expected_min_compute_slots`
  - `expected_transmission_slots`
  - `observed_queue_wait_slots`
  - `observed_execution_progress_slots`
  - `observed_task_age_at_drop_or_completion`
  - `deadline_margin_at_completion`
  - `deadline_overrun_at_drop`
- **Validation**:
  - Observed time values must be non-negative.
  - Task IDs must refer to reconstructed lifecycle evidence.

### LoadAdmissionActionExposureReport
- **Purpose**: Final artifact that aggregates the metrics above and routes the next feature.
- **Attributes**:
  - `feature_id`
  - `prerequisite_tags_verified`
  - `prior_feature_gates_verified`
  - `trace_input_sources`
  - `paper_default_runtime_verified`
  - `load_pressure_summary`
  - `admission_serialization_summary`
  - `action_exposure_summary`
  - `queue_pressure_summary`
  - `offload_path_pressure_summary`
  - `budget_comparison_summary`
  - `per_strategy_summary`
  - `per_action_summary`
  - `per_queue_summary`
  - `dominant_pressure_sources`
  - `diagnosis`
  - `recommended_next_feature`
  - scope guard booleans
  - `final_verdict`
- **Validation**:
  - All prerequisite and prior-feature gates must be verified.
  - `recommended_next_feature` must be consistent with `final_verdict`.
  - Scope guard booleans must remain true.

## Relationships

- A single report aggregates metrics across multiple strategies and seeds.
- Each strategy summary derives from multiple runs.
- Each action summary is derived from selected and legal action evidence across lifecycle reconstructions.
- Each queue summary aggregates task-level queue pressure evidence.

## State and Lifecycle Notes

- Pending-at-horizon tasks remain non-terminal and are counted separately from completed or dropped tasks.
- Legal-but-unselected actions are tracked as exposure evidence even when they produce no terminal events.
- Admission serialization is represented by same-slot generation followed by delayed admission.
