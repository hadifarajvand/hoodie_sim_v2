# Load Admission Action Exposure Review

- feature_id: `046-load-admission-action-exposure-review`
- final_verdict: `mixed_load_action_pressure_explains_completion_weakness`
- recommended_next_feature: `Feature 047 — Paper HOODIE Observation Vector`

## Diagnosis
{
  "evidence_strength": "medium",
  "summary": "Passive evidence suggests load and serialization dominate, with action exposure and offload pressure still visible."
}

## Load Pressure
{
  "admitted_per_slot": 0.045454545454545456,
  "admitted_task_count": 5,
  "completed_task_count": 5,
  "completion_rate": 1.0,
  "drop_rate": 0.0,
  "dropped_task_count": 0,
  "generated_per_slot": 0.045454545454545456,
  "generated_task_count": 5,
  "pending_at_horizon_count": 0,
  "pending_rate": 0.0,
  "terminal_per_slot": 0.045454545454545456,
  "terminal_task_count": 5
}

## Admission Serialization
{
  "max_serialization_lag_slots": 0,
  "mean_serialization_lag_slots": 0.0,
  "same_slot_admitted_count": 5,
  "same_slot_generated_count": 1,
  "serialized_admission_backlog_count": 0,
  "tasks_delayed_by_serialization": [],
  "tasks_expired_after_serialization_delay": []
}

## Action Exposure
{
  "action_entropy": -0.0,
  "exposure_ratio_by_action": {
    "horizontal": 0.0,
    "local": 1.0,
    "vertical": 0.0
  },
  "legal_but_unselected_by_action": {
    "horizontal": 0,
    "local": 0,
    "vertical": 0
  },
  "legal_horizontal_count": 0,
  "legal_local_count": 5,
  "legal_vertical_count": 0,
  "per_action_completion_rate": {
    "horizontal": 0.0,
    "local": 1.0,
    "vertical": 0.0
  },
  "per_action_drop_rate": {
    "horizontal": 0.0,
    "local": 0.0,
    "vertical": 0.0
  },
  "per_action_pending_rate": {
    "horizontal": 0.0,
    "local": 0.0,
    "vertical": 0.0
  },
  "selected_horizontal_count": 0,
  "selected_local_count": 5,
  "selected_vertical_count": 0,
  "selection_ratio_by_action": {
    "horizontal": 0.0,
    "local": 1.0,
    "vertical": 0.0
  }
}

## Queue Pressure
{
  "cloud_queue_admission_count": 0,
  "cloud_queue_terminal_count": 0,
  "per_queue_completion_rate": {
    "cloud": 0.0,
    "private": 0.0,
    "public": 0.0
  },
  "per_queue_drop_rate": {
    "cloud": 0.0,
    "private": 0.0,
    "public": 0.0
  },
  "private_queue_admission_count": 0,
  "private_queue_terminal_count": 0,
  "public_queue_admission_count": 0,
  "public_queue_terminal_count": 0,
  "queue_pressure_index": 0.0,
  "queue_wait_time_max": 0,
  "queue_wait_time_mean": 0.0
}

## Offload Path Pressure
{
  "execution_start_after_transmission_lag": 0.0,
  "offloaded_completed_count": 0,
  "offloaded_dropped_count": 0,
  "offloaded_pending_count": 0,
  "transmission_completed_count": 0,
  "transmission_delay_slots_max": 0,
  "transmission_delay_slots_mean": 0.0,
  "transmission_started_count": 0,
  "transmission_to_admission_lag": 0.0
}

## Budget Comparison
{
  "deadline_margin_at_completion": 0.0,
  "deadline_overrun_at_drop": 0.0,
  "expected_min_compute_slots": 2.0,
  "expected_transmission_slots": 1.0,
  "observed_execution_progress_slots": 2.0,
  "observed_queue_wait_slots": 0.0,
  "observed_task_age_at_drop_or_completion": 3.0,
  "representative_task_ids": [
    "environment_default_policy_probe:0:1",
    "environment_default_policy_probe:0:2",
    "environment_default_policy_probe:0:3",
    "environment_default_policy_probe:0:4",
    "environment_default_policy_probe:0:5"
  ]
}