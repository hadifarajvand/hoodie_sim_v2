# Completion Root-Cause Diagnosis Report

- feature_id: `045-completion-root-cause-diagnosis`
- final_verdict: `root_cause_identified_configuration_or_load_explanation`
- recommended_next_feature: `load/admission/action-exposure review`

## Diagnosis
{
  "dominant_root_causes": [
    "execution_progress_deadline_expires_first",
    "no_completion_problem_detected",
    "task_generation_admission_overload"
  ],
  "runtime_repair_verdict_guard": false,
  "summary": "Some tasks make measurable execution progress but the deadline drops them before completion can finish.",
  "trace_evidence": {
    "completed_count": 292,
    "dropped_count": 1312,
    "pending_at_horizon_count": 61,
    "trace_depth_ok": true
  }
}

## Dominant Root Causes
[
  {
    "confidence": "high",
    "detected": true,
    "evaluated": true,
    "evidence_count": 1312,
    "explanation": "Some tasks make measurable execution progress but the deadline drops them before completion can finish.",
    "representative_task_ids": [
      "environment_default_policy_probe:0:22",
      "environment_default_policy_probe:0:23",
      "environment_default_policy_probe:0:24",
      "environment_default_policy_probe:0:25",
      "environment_default_policy_probe:0:26"
    ],
    "required_next_action": "consider runtime repair only if progress is lost despite adequate budget",
    "root_cause_class": "execution_progress_deadline_expires_first",
    "supporting_event_types": [
      "execution_progress",
      "deadline_reached",
      "deadline_expired",
      "task_dropped"
    ]
  },
  {
    "confidence": "medium",
    "detected": true,
    "evaluated": true,
    "evidence_count": 292,
    "explanation": "Completions do occur under paper-default traces; the problem is weakness, not total absence.",
    "representative_task_ids": [
      "environment_default_policy_probe:0:1",
      "environment_default_policy_probe:0:2",
      "environment_default_policy_probe:0:3",
      "environment_default_policy_probe:0:4",
      "environment_default_policy_probe:0:5"
    ],
    "required_next_action": "no runtime repair needed for absence alone; continue with load/configuration review",
    "root_cause_class": "no_completion_problem_detected",
    "supporting_event_types": [
      "task_completed",
      "reward_emitted"
    ]
  },
  {
    "confidence": "low",
    "detected": true,
    "evaluated": true,
    "evidence_count": 61,
    "explanation": "Generation and admission progress faster than the system can retire work within the paper-default horizon.",
    "representative_task_ids": [
      "109",
      "110",
      "111",
      "109",
      "110"
    ],
    "required_next_action": "audit arrival/load configuration and admission pressure",
    "root_cause_class": "task_generation_admission_overload",
    "supporting_event_types": [
      "task_generated",
      "task_admitted",
      "pending_at_horizon"
    ]
  }
]

## Root Cause Evaluations
[
  {
    "confidence": "low",
    "detected": false,
    "evaluated": true,
    "evidence_count": 0,
    "explanation": "Dropped tasks spend measurable time waiting in private or shared queues before reaching terminal state.",
    "representative_task_ids": [],
    "required_next_action": "audit queue pressure and load balancing before considering runtime repair",
    "root_cause_class": "queue_pressure",
    "supporting_event_types": [
      "task_admitted",
      "execution_progress",
      "task_dropped"
    ]
  },
  {
    "confidence": "low",
    "detected": true,
    "evaluated": true,
    "evidence_count": 61,
    "explanation": "Generation and admission progress faster than the system can retire work within the paper-default horizon.",
    "representative_task_ids": [
      "109",
      "110",
      "111",
      "109",
      "110"
    ],
    "required_next_action": "audit arrival/load configuration and admission pressure",
    "root_cause_class": "task_generation_admission_overload",
    "supporting_event_types": [
      "task_generated",
      "task_admitted",
      "pending_at_horizon"
    ]
  },
  {
    "confidence": "high",
    "detected": false,
    "evaluated": true,
    "evidence_count": 611,
    "explanation": "Action usage is dominated by 'local' but this alone does not explain the completion pattern unless completion rates diverge materially.",
    "representative_task_ids": [
      "environment_default_policy_probe:0:22",
      "environment_default_policy_probe:0:23",
      "environment_default_policy_probe:0:24",
      "environment_default_policy_probe:0:25",
      "environment_default_policy_probe:0:26"
    ],
    "required_next_action": "adjust observation vectors or exploration if action exposure appears to suppress viable paths",
    "root_cause_class": "action_exposure_bias",
    "supporting_event_types": [
      "task_admitted",
      "execution_progress",
      "task_dropped"
    ]
  },
  {
    "confidence": "low",
    "detected": false,
    "evaluated": true,
    "evidence_count": 0,
    "explanation": "Local/private tasks pile up long enough to expire before completion on a meaningful subset of runs.",
    "representative_task_ids": [],
    "required_next_action": "audit local/private queue pressure and service rate assumptions",
    "root_cause_class": "local_private_queue_blockage",
    "supporting_event_types": [
      "task_admitted",
      "execution_started",
      "execution_progress",
      "task_dropped"
    ]
  },
  {
    "confidence": "low",
    "detected": false,
    "evaluated": true,
    "evidence_count": 0,
    "explanation": "Offloaded work accumulates in public/cloud queues long enough to miss the useful completion window.",
    "representative_task_ids": [],
    "required_next_action": "audit public/cloud queue sharing and service rates",
    "root_cause_class": "public_cloud_queue_blockage",
    "supporting_event_types": [
      "transmission_started",
      "transmission_completed",
      "execution_progress",
      "task_dropped"
    ]
  },
  {
    "confidence": "low",
    "detected": false,
    "evaluated": true,
    "evidence_count": 0,
    "explanation": "Transmission plus queue admission consumes the useful budget for a non-trivial subset of offloaded tasks.",
    "representative_task_ids": [],
    "required_next_action": "audit transmission-delay and admission timing assumptions",
    "root_cause_class": "transmission_delay_admission_mismatch",
    "supporting_event_types": [
      "transmission_started",
      "transmission_completed",
      "execution_started",
      "task_dropped"
    ]
  },
  {
    "confidence": "high",
    "detected": true,
    "evaluated": true,
    "evidence_count": 1312,
    "explanation": "Some tasks make measurable execution progress but the deadline drops them before completion can finish.",
    "representative_task_ids": [
      "environment_default_policy_probe:0:22",
      "environment_default_policy_probe:0:23",
      "environment_default_policy_probe:0:24",
      "environment_default_policy_probe:0:25",
      "environment_default_policy_probe:0:26"
    ],
    "required_next_action": "consider runtime repair only if progress is lost despite adequate budget",
    "root_cause_class": "execution_progress_deadline_expires_first",
    "supporting_event_types": [
      "execution_progress",
      "deadline_reached",
      "deadline_expired",
      "task_dropped"
    ]
  },
  {
    "confidence": "low",
    "detected": false,
    "evaluated": true,
    "evidence_count": 0,
    "explanation": "Completion exists but the reward/counter path fails to reflect it correctly.",
    "representative_task_ids": [],
    "required_next_action": "repair the runtime reward/counter path if this appears in the evidence",
    "root_cause_class": "completion_emitted_but_reward_or_counter_path_wrong",
    "supporting_event_types": [
      "task_completed",
      "reward_emitted"
    ]
  },
  {
    "confidence": "low",
    "detected": false,
    "evaluated": true,
    "evidence_count": 0,
    "explanation": "Deadline/drop/reward ordering violates the expected passive trace sequence.",
    "representative_task_ids": [],
    "required_next_action": "repair deadline/drop ordering in the runtime only if the ordering is actually violated",
    "root_cause_class": "deadline_drop_ordering_issue",
    "supporting_event_types": [
      "deadline_reached",
      "deadline_expired",
      "task_dropped",
      "reward_emitted"
    ]
  },
  {
    "confidence": "low",
    "detected": false,
    "evaluated": true,
    "evidence_count": 0,
    "explanation": "No evidence indicates that the unit conversion or cycles formula is drifting from the paper-default contract.",
    "representative_task_ids": [],
    "required_next_action": "audit the formula contract only if future evidence shows a mismatch",
    "root_cause_class": "formula_unit_mismatch",
    "supporting_event_types": [
      "task_generated",
      "execution_progress"
    ]
  },
  {
    "confidence": "medium",
    "detected": true,
    "evaluated": true,
    "evidence_count": 292,
    "explanation": "Completions do occur under paper-default traces; the problem is weakness, not total absence.",
    "representative_task_ids": [
      "environment_default_policy_probe:0:1",
      "environment_default_policy_probe:0:2",
      "environment_default_policy_probe:0:3",
      "environment_default_policy_probe:0:4",
      "environment_default_policy_probe:0:5"
    ],
    "required_next_action": "no runtime repair needed for absence alone; continue with load/configuration review",
    "root_cause_class": "no_completion_problem_detected",
    "supporting_event_types": [
      "task_completed",
      "reward_emitted"
    ]
  },
  {
    "confidence": "low",
    "detected": false,
    "evaluated": true,
    "evidence_count": 0,
    "explanation": "Trace depth is sufficient to distinguish terminal ordering, so inconclusive evidence is not the dominant explanation.",
    "representative_task_ids": [],
    "required_next_action": "increase trace depth only if future data lose lifecycle ordering evidence",
    "root_cause_class": "inconclusive_trace_evidence",
    "supporting_event_types": [
      "task_generated",
      "task_admitted"
    ]
  }
]

## Task Lifecycle Reconstruction Summary
{
  "completed_count": 292,
  "dropped_count": 1312,
  "median_queue_wait_time": 0.0,
  "pending_at_horizon_count": 61,
  "run_count": 15,
  "seed_counts": {
    "0": 5,
    "1": 5,
    "2": 5
  },
  "strategy_counts": {
    "environment_default_policy_probe": 3,
    "force_horizontal_legal_probe": 3,
    "force_local_legal_probe": 3,
    "force_vertical_legal_probe": 3,
    "mixed_legal_round_robin_probe": 3
  },
  "total_tasks": 1665
}

## Trace Input Sources
[
  {
    "path": "artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/lifecycle-trace-instrumentation-report.json",
    "role": "primary_input",
    "source_type": "feature_044_report",
    "verified": true
  },
  {
    "path": "src/analysis/passive_runtime_lifecycle_trace_instrumentation/runner.py",
    "role": "trace_replay_for_diagnosis",
    "source_type": "passive_trace_runner",
    "verified": true
  }
]
