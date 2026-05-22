# Exposure-Matrix Review Report

- feature_id: `047-exposure-matrix-review`
- final_verdict: `exposure_matrix_incomplete_requires_legality_evidence`
- recommended_next_feature: `legality evidence expansion before Feature 048`

## Matrix Completeness
{
  "evidence_coverage_ratio": 0.0,
  "reason": "legal action evidence unavailable in committed artifacts",
  "sample_usage_policy": "representative examples only; no aggregate derivation from lifecycle_trace_sample",
  "status": "incomplete"
}

## Illegal Action Summary
{
  "evidence_status": "unavailable",
  "selected_illegal_action_count": null,
  "selected_illegal_action_examples": [],
  "selected_illegal_action_rate": null,
  "selected_illegal_horizontal_count": null,
  "selected_illegal_local_count": null,
  "selected_illegal_vertical_count": null
}

## Exposure Bias Summary
{
  "action_exposure_measurable": false,
  "legal_action_evidence_status": "unavailable_in_committed_artifacts",
  "load_dominant": true,
  "load_pressure_reference": {
    "completed_task_count": 292,
    "dropped_task_count": 1312,
    "generated_task_count": 1665
  },
  "offload_underexposure_measurable": false
}

## Load vs Exposure Summary
{
  "action_exposure_evidence_status": "unavailable_in_committed_artifacts",
  "load_pressure_explains_completion_weakness": true,
  "load_pressure_summary": {
    "completed_task_count": 292,
    "dropped_task_count": 1312,
    "evidence_population": "feature_045_full_reconstruction_summary",
    "generated_task_count": 1665,
    "pending_at_horizon_count": 61
  },
  "offload_path_pressure_evidence_status": "unavailable_in_committed_artifacts",
  "queue_pressure_evidence_status": "unavailable_in_committed_artifacts",
  "selected_illegal_action_count": null
}

## Dominant Exposure Findings
[
  {
    "confidence": "high",
    "details": {
      "completed_task_count": 292,
      "dropped_task_count": 1312,
      "generated_task_count": 1665
    },
    "evidence_population": "feature_045_full_reconstruction_summary",
    "rank": 1,
    "source": "load_pressure"
  },
  {
    "confidence": "high",
    "details": "aggregate admission serialization evidence unavailable in committed artifacts",
    "evidence_population": "unavailable_in_committed_artifacts",
    "rank": 2,
    "source": "admission_serialization"
  },
  {
    "confidence": "unknown",
    "details": "legal-vs-selected exposure evidence unavailable in committed artifacts",
    "evidence_population": "unavailable_in_committed_artifacts",
    "rank": 3,
    "source": "action_exposure_unavailable"
  },
  {
    "confidence": "unknown",
    "details": "queue pressure aggregate evidence unavailable in committed artifacts",
    "evidence_population": "unavailable_in_committed_artifacts",
    "rank": 4,
    "source": "queue_pressure_unavailable"
  },
  {
    "confidence": "unknown",
    "details": "offload path aggregate evidence unavailable in committed artifacts",
    "evidence_population": "unavailable_in_committed_artifacts",
    "rank": 5,
    "source": "offload_path_pressure_unavailable"
  }
]