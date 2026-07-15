# Load Admission Action Exposure Review

- feature_id: `046-load-admission-action-exposure-review`
- final_verdict: `diagnosis_inconclusive_requires_deeper_exposure_matrix`
- recommended_next_feature: `exposure-matrix review`

## Evidence Populations
{
  "action_exposure": "unavailable_in_committed_artifacts",
  "admission_serialization": "unavailable_in_committed_artifacts",
  "budget_comparison": "representative_trace_sample",
  "dominant_pressure_sources": "feature_045_full_reconstruction_summary",
  "final_verdict": "unavailable_in_committed_artifacts",
  "load_pressure": "feature_045_full_reconstruction_summary",
  "offload_path_pressure": "unavailable_in_committed_artifacts",
  "per_action": "unavailable_in_committed_artifacts",
  "per_queue": "unavailable_in_committed_artifacts",
  "per_strategy": "unavailable_in_committed_artifacts",
  "queue_pressure": "unavailable_in_committed_artifacts"
}

## Diagnosis
{
  "dominant_root_causes": [
    {
      "confidence": "high",
      "rank": 1,
      "source": "load_pressure"
    },
    {
      "confidence": "high",
      "rank": 2,
      "source": "admission_serialization"
    },
    {
      "confidence": "unavailable",
      "rank": 3,
      "source": "action_exposure"
    },
    {
      "confidence": "unavailable",
      "rank": 4,
      "source": "queue_pressure"
    },
    {
      "confidence": "unavailable",
      "rank": 5,
      "source": "offload_path_pressure"
    }
  ],
  "load_pressure_summary_reference": {
    "completed_task_count": 284,
    "dropped_task_count": 1328,
    "generated_task_count": 1665
  },
  "runtime_repair_verdict_guard": false,
  "summary": "Committed Feature 045 aggregate evidence supports a load/admission explanation, but action, queue, and offload exposure metrics are unavailable in the committed full-population artifacts."
}

## Load Pressure
{
  "admitted_per_slot": 15.136363636363637,
  "admitted_task_count": 1665,
  "completed_task_count": 284,
  "completion_rate": 0.1761786600496278,
  "drop_rate": 0.8238213399503722,
  "dropped_task_count": 1328,
  "evidence_population": "feature_045_full_reconstruction_summary",
  "generated_per_slot": 15.136363636363637,
  "generated_task_count": 1665,
  "pending_at_horizon_count": 53,
  "pending_rate": 0.03183183183183183,
  "terminal_per_slot": 14.654545454545454,
  "terminal_task_count": 1612
}

## Admission Serialization
{
  "evidence_population": "unavailable_in_committed_artifacts",
  "max_serialization_lag_slots": null,
  "mean_serialization_lag_slots": null,
  "note": "Admission serialization aggregate evidence is unavailable in committed artifacts.",
  "same_slot_admitted_count": null,
  "same_slot_generated_count": null,
  "serialized_admission_backlog_count": null,
  "tasks_delayed_by_serialization": [],
  "tasks_expired_after_serialization_delay": []
}

## Action Exposure
{
  "action_entropy": null,
  "evidence_population": "unavailable_in_committed_artifacts",
  "exposure_ratio_by_action": {
    "horizontal": null,
    "local": null,
    "vertical": null
  },
  "legal_but_unselected_by_action": {
    "horizontal": null,
    "local": null,
    "vertical": null
  },
  "legal_horizontal_count": null,
  "legal_local_count": null,
  "legal_vertical_count": null,
  "note": "No full-population legal-mask evidence was committed.",
  "per_action_completion_rate": {
    "horizontal": null,
    "local": null,
    "vertical": null
  },
  "per_action_drop_rate": {
    "horizontal": null,
    "local": null,
    "vertical": null
  },
  "per_action_pending_rate": {
    "horizontal": null,
    "local": null,
    "vertical": null
  },
  "selected_horizontal_count": null,
  "selected_local_count": null,
  "selected_vertical_count": null,
  "selection_ratio_by_action": {
    "horizontal": null,
    "local": null,
    "vertical": null
  }
}

## Queue Pressure
{
  "cloud_queue_admission_count": null,
  "cloud_queue_terminal_count": null,
  "evidence_population": "unavailable_in_committed_artifacts",
  "note": "Queue metrics unavailable in committed full-population artifacts.",
  "per_queue_completion_rate": {
    "cloud": null,
    "private": null,
    "public": null
  },
  "per_queue_drop_rate": {
    "cloud": null,
    "private": null,
    "public": null
  },
  "private_queue_admission_count": null,
  "private_queue_terminal_count": null,
  "public_queue_admission_count": null,
  "public_queue_terminal_count": null,
  "queue_pressure_index": null,
  "queue_wait_time_max": null,
  "queue_wait_time_mean": null
}

## Offload Path Pressure
{
  "evidence_population": "unavailable_in_committed_artifacts",
  "execution_start_after_transmission_lag": null,
  "note": "Offload metrics unavailable in committed full-population artifacts.",
  "offloaded_completed_count": null,
  "offloaded_dropped_count": null,
  "offloaded_pending_count": null,
  "transmission_completed_count": null,
  "transmission_delay_slots_max": null,
  "transmission_delay_slots_mean": null,
  "transmission_started_count": null,
  "transmission_to_admission_lag": null
}

## Budget Comparison
{
  "deadline_margin_at_completion": null,
  "deadline_overrun_at_drop": null,
  "evidence_population": "representative_trace_sample",
  "expected_min_compute_slots": null,
  "expected_transmission_slots": null,
  "observed_execution_progress_slots": null,
  "observed_queue_wait_slots": null,
  "observed_task_age_at_drop_or_completion": null,
  "representative_examples": [
    {
      "completed_before_deadline": true,
      "destination": "self",
      "queue_wait_time_slots": 0,
      "run_id": "environment_default_policy_probe:0",
      "selected_action": "local",
      "size_mbits": 2.0,
      "strategy": "environment_default_policy_probe",
      "task_age_by_slot": {
        "0": 0,
        "1": 1
      },
      "task_id": 1,
      "terminal_outcome": "completed"
    },
    {
      "completed_before_deadline": true,
      "destination": "self",
      "queue_wait_time_slots": 0,
      "run_id": "environment_default_policy_probe:0",
      "selected_action": "local",
      "size_mbits": 2.1,
      "strategy": "environment_default_policy_probe",
      "task_age_by_slot": {
        "1": 1,
        "2": 2
      },
      "task_id": 2,
      "terminal_outcome": "completed"
    },
    {
      "completed_before_deadline": true,
      "destination": "self",
      "queue_wait_time_slots": 0,
      "run_id": "environment_default_policy_probe:0",
      "selected_action": "local",
      "size_mbits": 2.2,
      "strategy": "environment_default_policy_probe",
      "task_age_by_slot": {
        "2": 2,
        "3": 3
      },
      "task_id": 3,
      "terminal_outcome": "completed"
    },
    {
      "completed_before_deadline": true,
      "destination": "self",
      "queue_wait_time_slots": 0,
      "run_id": "environment_default_policy_probe:0",
      "selected_action": "local",
      "size_mbits": 2.3,
      "strategy": "environment_default_policy_probe",
      "task_age_by_slot": {
        "3": 3,
        "4": 4
      },
      "task_id": 4,
      "terminal_outcome": "completed"
    },
    {
      "completed_before_deadline": true,
      "destination": "self",
      "queue_wait_time_slots": 0,
      "run_id": "environment_default_policy_probe:0",
      "selected_action": "local",
      "size_mbits": 2.4,
      "strategy": "environment_default_policy_probe",
      "task_age_by_slot": {
        "4": 4,
        "5": 5
      },
      "task_id": 5,
      "terminal_outcome": "completed"
    }
  ],
  "representative_task_ids": [
    "environment_default_policy_probe:0:1",
    "environment_default_policy_probe:0:2",
    "environment_default_policy_probe:0:3",
    "environment_default_policy_probe:0:4",
    "environment_default_policy_probe:0:5"
  ]
}