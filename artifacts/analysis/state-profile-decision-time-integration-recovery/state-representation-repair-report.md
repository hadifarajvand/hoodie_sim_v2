# State Profile Decision-Time Integration Recovery

- feature_id: `072-state-profile-decision-time-integration-recovery`
- final_verdict: `state_profile_decision_time_integration_blocked`
- diagnostic_decision: `blocked_due_to_state_profile_integration_failure`
- feature_071_prerequisite_verified: `True`
- decision_state_injection_passed: `True`
- replay_state_alignment_passed: `True`
- train_eval_state_profile_match: `True`

## 1. Feature 071 Prerequisite Verification
{
  "prerequisite_artifacts": {
    "feature_070_report": {
      "details": "Feature 071 report validated",
      "exists": true,
      "path": "artifacts/analysis/state-representation-deadline-queue-feasibility-repair/state-representation-repair-report.json",
      "verified": true
    },
    "feature_071_report": {
      "details": "Feature 071 report validated",
      "exists": true,
      "path": "artifacts/analysis/state-representation-deadline-queue-feasibility-repair/state-representation-repair-report.json",
      "verified": true
    }
  },
  "prerequisite_tags_verified": [
    {
      "details": "current branch matches Feature 072",
      "name": "branch",
      "verified": true
    },
    {
      "details": "Feature 071 report validated",
      "name": "feature_071_report_valid",
      "verified": true
    },
    {
      "details": "Feature 070 alias report validated",
      "name": "feature_070_report_valid",
      "verified": true
    },
    {
      "details": "working tree stays within the approved scope",
      "name": "working_tree_paths_approved",
      "verified": true
    },
    {
      "details": "staged paths stay within the approved scope",
      "name": "staged_paths_approved",
      "verified": true
    },
    {
      "details": "branch diff stays within the approved scope",
      "name": "base_branch_diff_approved",
      "verified": true
    }
  ],
  "scope_guard_summary": {
    "approved_prefixes": [
      "artifacts/analysis/state-profile-decision-time-integration-recovery/",
      "docs/architecture/euls_phase31_state_profile_decision_time_integration_recovery.md",
      "specs/072-state-profile-decision-time-integration-recovery/",
      "src/analysis/state_profile_decision_time_integration_recovery/",
      "tests/unit/test_state_profile_decision_time_integration_recovery",
      "tests/integration/test_state_profile_decision_time_integration_recovery",
      "src/analysis/full_training_reproduction_campaign/replay.py",
      "src/analysis/full_training_reproduction_campaign/trainer.py",
      "src/analysis/full_training_reproduction_campaign/config.py"
    ],
    "base_branch_head_diff_approved": true,
    "diff_paths": [],
    "forbidden_prefixes": [
      "src/environment/reward_timing.py",
      "src/dal/",
      "src/policies/",
      "src/environment/replay_hash.py",
      "requirements",
      "pyproject.toml",
      "poetry.lock",
      "uv.lock",
      "AGENTS.md",
      ".specify/feature.json",
      "artifacts/analysis/full-paper-default-training-campaign-execution/",
      "artifacts/analysis/unified-campaign-result-analysis-figures-findings/",
      "artifacts/analysis/staged-training-budget-learning-curve/",
      "artifacts/analysis/final-review-release-gate-batch/",
      "artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic/",
      "artifacts/analysis/reward-emission-evaluation-metric-aggregation-repair/",
      "artifacts/analysis/terminal-lifecycle-accounting-50-100-comparison/",
      "artifacts/analysis/completion-path-deadline-feasibility-repair/",
      "artifacts/analysis/deadline-timeout-feasible-workload-calibration/",
      "artifacts/analysis/calibration-metric-consistency-reconciliation-fix/",
      "artifacts/analysis/state-representation-deadline-queue-feasibility-repair/"
    ],
    "staged_paths": [],
    "staged_paths_approved": true,
    "working_tree_paths": [
      "src/analysis/full_training_reproduction_campaign/trainer.py"
    ],
    "working_tree_paths_approved": true
  }
}

## 2. Decision-Time State Injection Audit
{
  "current_feature_tail_matches": true,
  "decision_state_contains_current_task": true,
  "sample_records": [
    {
      "absolute_deadline_slot": 3,
      "arrival_slot": 0,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 0,
      "slot": 0,
      "source_agent_id": 1,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 1,
      "timeout_length": 3,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 3,
      "arrival_slot": 1,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 1,
      "slot": 1,
      "source_agent_id": 2,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 2,
      "timeout_length": 2,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 7,
      "arrival_slot": 2,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 2,
      "slot": 2,
      "source_agent_id": 3,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 3,
      "timeout_length": 5,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 8,
      "arrival_slot": 3,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 3,
      "slot": 3,
      "source_agent_id": 1,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 4,
      "timeout_length": 5,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 9,
      "arrival_slot": 4,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 4,
      "slot": 4,
      "source_agent_id": 2,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 5,
      "timeout_length": 5,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 7,
      "arrival_slot": 5,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 3,
      "slot": 5,
      "source_agent_id": 3,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 6,
      "timeout_length": 2,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 11,
      "arrival_slot": 6,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 4,
      "slot": 6,
      "source_agent_id": 1,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 7,
      "timeout_length": 5,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 10,
      "arrival_slot": 7,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 5,
      "slot": 7,
      "source_agent_id": 2,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 8,
      "timeout_length": 3,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 11,
      "arrival_slot": 8,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 6,
      "slot": 8,
      "source_agent_id": 3,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 9,
      "timeout_length": 3,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 13,
      "arrival_slot": 9,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 6,
      "slot": 9,
      "source_agent_id": 1,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 10,
      "timeout_length": 4,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 15,
      "arrival_slot": 10,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 5,
      "slot": 10,
      "source_agent_id": 2,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 11,
      "timeout_length": 5,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 13,
      "arrival_slot": 11,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 5,
      "slot": 11,
      "source_agent_id": 3,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 12,
      "timeout_length": 2,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 15,
      "arrival_slot": 12,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 5,
      "slot": 12,
      "source_agent_id": 1,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 13,
      "timeout_length": 3,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 15,
      "arrival_slot": 13,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 4,
      "slot": 13,
      "source_agent_id": 2,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 14,
      "timeout_length": 2,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 16,
      "arrival_slot": 14,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 5,
      "slot": 14,
      "source_agent_id": 3,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 15,
      "timeout_length": 2,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 17,
      "arrival_slot": 15,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 4,
      "slot": 15,
      "source_agent_id": 1,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 16,
      "timeout_length": 2,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 20,
      "arrival_slot": 16,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 5,
      "slot": 16,
      "source_agent_id": 2,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 17,
      "timeout_length": 4,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 22,
      "arrival_slot": 17,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 4,
      "slot": 17,
      "source_agent_id": 3,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 18,
      "timeout_length": 5,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 20,
      "arrival_slot": 18,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 3,
      "slot": 18,
      "source_agent_id": 1,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 19,
      "timeout_length": 2,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 23,
      "arrival_slot": 19,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 3,
      "slot": 19,
      "source_agent_id": 2,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 20,
      "timeout_length": 4,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 22,
      "arrival_slot": 20,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 4,
      "slot": 20,
      "source_agent_id": 3,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 21,
      "timeout_length": 2,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 25,
      "arrival_slot": 21,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 5,
      "slot": 21,
      "source_agent_id": 1,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 22,
      "timeout_length": 4,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 27,
      "arrival_slot": 22,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 4,
      "slot": 22,
      "source_agent_id": 2,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 23,
      "timeout_length": 5,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 28,
      "arrival_slot": 23,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 5,
      "slot": 23,
      "source_agent_id": 3,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 24,
      "timeout_length": 5,
      "trace_id": "hoodie-43"
    },
    {
      "absolute_deadline_slot": 28,
      "arrival_slot": 24,
      "current_feature_tail_matches": true,
      "decision_state_contains_current_task": true,
      "decision_window_length": 10,
      "episode_id": 0,
      "legal_action_mask": {
        "compute_local": true,
        "horizontal": true,
        "local": true,
        "offload_horizontal": true,
        "offload_vertical": true,
        "vertical": true
      },
      "queue_load": 5,
      "slot": 24,
      "source_agent_id": 1,
      "state_dim": 30,
      "state_has_inf": false,
      "state_has_nan": false,
      "task_id": 25,
      "timeout_length": 4,
      "trace_id": "hoodie-43"
    }
  ],
  "state_dim": 30,
  "state_has_inf": false,
  "state_has_nan": false,
  "state_representation_profile": "deadline_queue_feasibility_v1"
}

## 3. Train/Eval State Profile Consistency
{
  "decision_state_contains_current_task": true,
  "eval_state_dim": 30,
  "eval_state_representation_profile": "deadline_queue_feasibility_v1",
  "state_has_inf": false,
  "state_has_nan": false,
  "train_eval_state_dim_match": true,
  "train_eval_state_profile_match": true,
  "train_state_dim": 30,
  "train_state_representation_profile": "deadline_queue_feasibility_v1"
}

## 4. Replay State Alignment Audit
{
  "compared_transition_count": 25,
  "mismatch_count": 0,
  "replay_transition_state_matches_action_state": true,
  "sample_records": [
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 0,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 1,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 2,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 3,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 4,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 5,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 6,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 7,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 8,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 9,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 10,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 11,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 12,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 13,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 14,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 15,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 16,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 17,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 18,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 19,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 20,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 21,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 22,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 23,
      "replay_state_shape": [
        10,
        30
      ]
    },
    {
      "action_state_matches_replay_state": true,
      "action_state_shape": [
        10,
        30
      ],
      "index": 24,
      "replay_state_shape": [
        10,
        30
      ]
    }
  ]
}

## 5. State Sample Records After Decision Injection
[
  {
    "absolute_deadline_slot": 3,
    "arrival_slot": 0,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 0,
    "slot": 0,
    "source_agent_id": 1,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 1,
    "timeout_length": 3,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 3,
    "arrival_slot": 1,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 1,
    "slot": 1,
    "source_agent_id": 2,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 2,
    "timeout_length": 2,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 7,
    "arrival_slot": 2,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 2,
    "slot": 2,
    "source_agent_id": 3,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 3,
    "timeout_length": 5,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 8,
    "arrival_slot": 3,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 3,
    "slot": 3,
    "source_agent_id": 1,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 4,
    "timeout_length": 5,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 9,
    "arrival_slot": 4,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 4,
    "slot": 4,
    "source_agent_id": 2,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 5,
    "timeout_length": 5,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 7,
    "arrival_slot": 5,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 3,
    "slot": 5,
    "source_agent_id": 3,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 6,
    "timeout_length": 2,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 11,
    "arrival_slot": 6,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 4,
    "slot": 6,
    "source_agent_id": 1,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 7,
    "timeout_length": 5,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 10,
    "arrival_slot": 7,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 5,
    "slot": 7,
    "source_agent_id": 2,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 8,
    "timeout_length": 3,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 11,
    "arrival_slot": 8,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 6,
    "slot": 8,
    "source_agent_id": 3,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 9,
    "timeout_length": 3,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 13,
    "arrival_slot": 9,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 6,
    "slot": 9,
    "source_agent_id": 1,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 10,
    "timeout_length": 4,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 15,
    "arrival_slot": 10,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 5,
    "slot": 10,
    "source_agent_id": 2,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 11,
    "timeout_length": 5,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 13,
    "arrival_slot": 11,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 5,
    "slot": 11,
    "source_agent_id": 3,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 12,
    "timeout_length": 2,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 15,
    "arrival_slot": 12,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 5,
    "slot": 12,
    "source_agent_id": 1,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 13,
    "timeout_length": 3,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 15,
    "arrival_slot": 13,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 4,
    "slot": 13,
    "source_agent_id": 2,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 14,
    "timeout_length": 2,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 16,
    "arrival_slot": 14,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 5,
    "slot": 14,
    "source_agent_id": 3,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 15,
    "timeout_length": 2,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 17,
    "arrival_slot": 15,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 4,
    "slot": 15,
    "source_agent_id": 1,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 16,
    "timeout_length": 2,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 20,
    "arrival_slot": 16,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 5,
    "slot": 16,
    "source_agent_id": 2,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 17,
    "timeout_length": 4,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 22,
    "arrival_slot": 17,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 4,
    "slot": 17,
    "source_agent_id": 3,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 18,
    "timeout_length": 5,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 20,
    "arrival_slot": 18,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 3,
    "slot": 18,
    "source_agent_id": 1,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 19,
    "timeout_length": 2,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 23,
    "arrival_slot": 19,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 3,
    "slot": 19,
    "source_agent_id": 2,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 20,
    "timeout_length": 4,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 22,
    "arrival_slot": 20,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 4,
    "slot": 20,
    "source_agent_id": 3,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 21,
    "timeout_length": 2,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 25,
    "arrival_slot": 21,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 5,
    "slot": 21,
    "source_agent_id": 1,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 22,
    "timeout_length": 4,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 27,
    "arrival_slot": 22,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 4,
    "slot": 22,
    "source_agent_id": 2,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 23,
    "timeout_length": 5,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 28,
    "arrival_slot": 23,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 5,
    "slot": 23,
    "source_agent_id": 3,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 24,
    "timeout_length": 5,
    "trace_id": "hoodie-43"
  },
  {
    "absolute_deadline_slot": 28,
    "arrival_slot": 24,
    "current_feature_tail_matches": true,
    "decision_state_contains_current_task": true,
    "decision_window_length": 10,
    "episode_id": 0,
    "legal_action_mask": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "queue_load": 5,
    "slot": 24,
    "source_agent_id": 1,
    "state_dim": 30,
    "state_has_inf": false,
    "state_has_nan": false,
    "task_id": 25,
    "timeout_length": 4,
    "trace_id": "hoodie-43"
  }
]

## 6. Legacy vs Decision-Time State Comparison
{
  "comparison": {
    "action_collapse_reduced": false,
    "action_distribution_changed": true,
    "completion_ratio_changed": true,
    "reward_changed": true,
    "selected_action_feasibility_improved": true,
    "state_dim_increased": true
  },
  "legacy_candidate_100": {},
  "legacy_candidate_50": {},
  "legacy_state_dim": 3,
  "new_candidate_100": {
    "action_distribution": {
      "horizontal": 0,
      "local": 10412,
      "vertical": 0
    },
    "action_entropy": 0.0,
    "checkpoint_budget": 100,
    "completed_count": 2589,
    "completed_feasible_task_count": 35,
    "completed_feasible_task_count_definition": "completed tasks whose selected action was feasible under the same selected-action feasibility estimate",
    "completed_feasible_task_count_universe": "U_selected_action_tasks",
    "completed_infeasible_task_count": 2554,
    "completed_selected_action_feasible_count": 35,
    "completed_selected_action_feasible_count_universe": "U_selected_action_tasks",
    "completed_selected_action_infeasible_count": 2554,
    "completed_selected_action_infeasible_count_universe": "U_selected_action_tasks",
    "completion_ratio": 0.2464540694907187,
    "deadline_violation_ratio": 0.6626368396001904,
    "decision_count": 10412,
    "decision_count_universe": "U_full_decisions",
    "dominant_action_name": "local",
    "dominant_action_share": 1.0,
    "drop_ratio": 0.6626368396001904,
    "dropped_count": 6961,
    "dropped_feasible_task_count": 0,
    "dropped_infeasible_task_count": 6961,
    "dropped_selected_action_feasible_count": 0,
    "dropped_selected_action_feasible_count_universe": "U_selected_action_tasks",
    "dropped_selected_action_infeasible_count": 6961,
    "dropped_selected_action_infeasible_count_universe": "U_selected_action_tasks",
    "feasible_task_count": 35,
    "feasible_task_count_definition": "selected_action_feasible_task_count",
    "feasible_task_count_universe": "U_selected_action_tasks",
    "infeasible_task_count": 10470,
    "is_action_collapsed": true,
    "mean_completion_latency_slots": 10.092699884125144,
    "mean_drop_latency_slots": 16.995977589426808,
    "mean_reward": -3045.7,
    "mean_terminal_latency_slots": 15.124502617801047,
    "pending_count": 433,
    "policy_name": "candidate_policy_at_100",
    "raw_vs_canonical_reward_delta": 3000.0,
    "reward_per_decision": -29.251824817518248,
    "reward_per_task": -28.992860542598763,
    "reward_reconciled": false,
    "selected_action_feasible_ratio": 0.0033317467872441696,
    "selected_action_feasible_task_count": 35,
    "selected_action_feasible_task_count_universe": "U_selected_action_tasks",
    "selected_action_infeasible_task_count": 10470,
    "selected_action_infeasible_task_count_universe": "U_selected_action_tasks",
    "terminal_reconciled": false,
    "unique_task_count": 10505,
    "unique_task_count_universe": "U_unique_tasks"
  },
  "new_candidate_50": {
    "action_distribution": {
      "horizontal": 9306,
      "local": 0,
      "vertical": 1106
    },
    "action_entropy": 0.4884190075208499,
    "checkpoint_budget": 50,
    "completed_count": 1754,
    "completed_feasible_task_count": 14,
    "completed_feasible_task_count_definition": "completed tasks whose selected action was feasible under the same selected-action feasibility estimate",
    "completed_feasible_task_count_universe": "U_selected_action_tasks",
    "completed_infeasible_task_count": 1740,
    "completed_selected_action_feasible_count": 14,
    "completed_selected_action_feasible_count_universe": "U_selected_action_tasks",
    "completed_selected_action_infeasible_count": 1740,
    "completed_selected_action_infeasible_count_universe": "U_selected_action_tasks",
    "completion_ratio": 0.16696811042360782,
    "deadline_violation_ratio": 0.7393622084721562,
    "decision_count": 10412,
    "decision_count_universe": "U_full_decisions",
    "dominant_action_name": "horizontal",
    "dominant_action_share": 0.893776411832501,
    "drop_ratio": 0.7393622084721562,
    "dropped_count": 7767,
    "dropped_feasible_task_count": 0,
    "dropped_infeasible_task_count": 7767,
    "dropped_selected_action_feasible_count": 0,
    "dropped_selected_action_feasible_count_universe": "U_selected_action_tasks",
    "dropped_selected_action_infeasible_count": 7767,
    "dropped_selected_action_infeasible_count_universe": "U_selected_action_tasks",
    "feasible_task_count": 14,
    "feasible_task_count_definition": "selected_action_feasible_task_count",
    "feasible_task_count_universe": "U_selected_action_tasks",
    "infeasible_task_count": 10491,
    "is_action_collapsed": false,
    "mean_completion_latency_slots": 11.205245153933866,
    "mean_drop_latency_slots": 16.99909875112656,
    "mean_reward": -3303.34,
    "mean_terminal_latency_slots": 15.93172986030879,
    "pending_count": 536,
    "policy_name": "candidate_policy_at_50",
    "raw_vs_canonical_reward_delta": 3320.0,
    "reward_per_decision": -31.726277372262775,
    "reward_per_task": -31.44540694907187,
    "reward_reconciled": false,
    "selected_action_feasible_ratio": 0.0013326987148976678,
    "selected_action_feasible_task_count": 14,
    "selected_action_feasible_task_count_universe": "U_selected_action_tasks",
    "selected_action_infeasible_task_count": 10491,
    "selected_action_infeasible_task_count_universe": "U_selected_action_tasks",
    "terminal_reconciled": false,
    "unique_task_count": 10505,
    "unique_task_count_universe": "U_unique_tasks"
  },
  "new_state_dim": 30
}

## 7. Policy Effect After Decision-State Fix
{
  "any_fixed_policy_completes": true,
  "candidate_action_distribution_changed_by_budget": true,
  "candidate_policy_at_100": {
    "action_distribution": {
      "horizontal": 0,
      "local": 10412,
      "vertical": 0
    },
    "action_entropy": 0.0,
    "checkpoint_budget": 100,
    "completed_count": 2589,
    "completed_feasible_task_count": 35,
    "completed_feasible_task_count_definition": "completed tasks whose selected action was feasible under the same selected-action feasibility estimate",
    "completed_feasible_task_count_universe": "U_selected_action_tasks",
    "completed_infeasible_task_count": 2554,
    "completed_selected_action_feasible_count": 35,
    "completed_selected_action_feasible_count_universe": "U_selected_action_tasks",
    "completed_selected_action_infeasible_count": 2554,
    "completed_selected_action_infeasible_count_universe": "U_selected_action_tasks",
    "completion_ratio": 0.2464540694907187,
    "deadline_violation_ratio": 0.6626368396001904,
    "decision_count": 10412,
    "decision_count_universe": "U_full_decisions",
    "dominant_action_name": "local",
    "dominant_action_share": 1.0,
    "drop_ratio": 0.6626368396001904,
    "dropped_count": 6961,
    "dropped_feasible_task_count": 0,
    "dropped_infeasible_task_count": 6961,
    "dropped_selected_action_feasible_count": 0,
    "dropped_selected_action_feasible_count_universe": "U_selected_action_tasks",
    "dropped_selected_action_infeasible_count": 6961,
    "dropped_selected_action_infeasible_count_universe": "U_selected_action_tasks",
    "feasible_task_count": 35,
    "feasible_task_count_definition": "selected_action_feasible_task_count",
    "feasible_task_count_universe": "U_selected_action_tasks",
    "infeasible_task_count": 10470,
    "is_action_collapsed": true,
    "mean_completion_latency_slots": 10.092699884125144,
    "mean_drop_latency_slots": 16.995977589426808,
    "mean_reward": -3045.7,
    "mean_terminal_latency_slots": 15.124502617801047,
    "pending_count": 433,
    "policy_name": "candidate_policy_at_100",
    "raw_vs_canonical_reward_delta": 3000.0,
    "reward_per_decision": -29.251824817518248,
    "reward_per_task": -28.992860542598763,
    "reward_reconciled": false,
    "selected_action_feasible_ratio": 0.0033317467872441696,
    "selected_action_feasible_task_count": 35,
    "selected_action_feasible_task_count_universe": "U_selected_action_tasks",
    "selected_action_infeasible_task_count": 10470,
    "selected_action_infeasible_task_count_universe": "U_selected_action_tasks",
    "terminal_reconciled": false,
    "unique_task_count": 10505,
    "unique_task_count_universe": "U_unique_tasks"
  },
  "candidate_policy_at_50": {
    "action_distribution": {
      "horizontal": 9306,
      "local": 0,
      "vertical": 1106
    },
    "action_entropy": 0.4884190075208499,
    "checkpoint_budget": 50,
    "completed_count": 1754,
    "completed_feasible_task_count": 14,
    "completed_feasible_task_count_definition": "completed tasks whose selected action was feasible under the same selected-action feasibility estimate",
    "completed_feasible_task_count_universe": "U_selected_action_tasks",
    "completed_infeasible_task_count": 1740,
    "completed_selected_action_feasible_count": 14,
    "completed_selected_action_feasible_count_universe": "U_selected_action_tasks",
    "completed_selected_action_infeasible_count": 1740,
    "completed_selected_action_infeasible_count_universe": "U_selected_action_tasks",
    "completion_ratio": 0.16696811042360782,
    "deadline_violation_ratio": 0.7393622084721562,
    "decision_count": 10412,
    "decision_count_universe": "U_full_decisions",
    "dominant_action_name": "horizontal",
    "dominant_action_share": 0.893776411832501,
    "drop_ratio": 0.7393622084721562,
    "dropped_count": 7767,
    "dropped_feasible_task_count": 0,
    "dropped_infeasible_task_count": 7767,
    "dropped_selected_action_feasible_count": 0,
    "dropped_selected_action_feasible_count_universe": "U_selected_action_tasks",
    "dropped_selected_action_infeasible_count": 7767,
    "dropped_selected_action_infeasible_count_universe": "U_selected_action_tasks",
    "feasible_task_count": 14,
    "feasible_task_count_definition": "selected_action_feasible_task_count",
    "feasible_task_count_universe": "U_selected_action_tasks",
    "infeasible_task_count": 10491,
    "is_action_collapsed": false,
    "mean_completion_latency_slots": 11.205245153933866,
    "mean_drop_latency_slots": 16.99909875112656,
    "mean_reward": -3303.34,
    "mean_terminal_latency_slots": 15.93172986030879,
    "pending_count": 536,
    "policy_name": "candidate_policy_at_50",
    "raw_vs_canonical_reward_delta": 3320.0,
    "reward_per_decision": -31.726277372262775,
    "reward_per_task": -31.44540694907187,
    "reward_reconciled": false,
    "selected_action_feasible_ratio": 0.0013326987148976678,
    "selected_action_feasible_task_count": 14,
    "selected_action_feasible_task_count_universe": "U_selected_action_tasks",
    "selected_action_infeasible_task_count": 10491,
    "selected_action_infeasible_task_count_universe": "U_selected_action_tasks",
    "terminal_reconciled": false,
    "unique_task_count": 10505,
    "unique_task_count_universe": "U_unique_tasks"
  },
  "candidate_policy_vertical_collapse_in_evaluation": false,
  "candidate_policy_vertical_collapse_in_training_replay_window": false,
  "candidate_reward_variation": 257.6400000000003,
  "candidate_terminal_outcomes_changed_by_budget": true,
  "canonical_completion_rate_static_across_budget": false,
  "canonical_drop_rate_static_across_budget": false,
  "canonical_policy_effect_summary": {
    "canonical_completion_rate_static_across_budget": false,
    "canonical_drop_rate_static_across_budget": false,
    "canonical_task_reward_static_across_budget": false,
    "evaluation_action_distribution_static_across_budget": false,
    "policy_affects_reward": "true",
    "policy_affects_terminal_outcomes": "true",
    "raw_event_reward_static_across_budget": false
  },
  "canonical_task_reward_static_across_budget": false,
  "episode_length": 110,
  "evaluation_action_distribution_static_across_budget": false,
  "evaluation_episode_count": 100,
  "evaluation_reward_static_after_terminal_repair": false,
  "evaluation_trace_bank_id": "state-repair-eval-bank",
  "fixed_horizontal_policy": {
    "action_distribution": {
      "horizontal": 10412,
      "local": 0,
      "vertical": 0
    },
    "action_entropy": 0.0,
    "checkpoint_budget": null,
    "completed_count": 1743,
    "completed_feasible_task_count": 14,
    "completed_feasible_task_count_definition": "completed tasks whose selected action was feasible under the same selected-action feasibility estimate",
    "completed_feasible_task_count_universe": "U_selected_action_tasks",
    "completed_infeasible_task_count": 1729,
    "completed_selected_action_feasible_count": 14,
    "completed_selected_action_feasible_count_universe": "U_selected_action_tasks",
    "completed_selected_action_infeasible_count": 1729,
    "completed_selected_action_infeasible_count_universe": "U_selected_action_tasks",
    "completion_ratio": 0.16592099000475963,
    "deadline_violation_ratio": 0.7404093288910043,
    "decision_count": 10412,
    "decision_count_universe": "U_full_decisions",
    "dominant_action_name": "horizontal",
    "dominant_action_share": 1.0,
    "drop_ratio": 0.7404093288910043,
    "dropped_count": 7778,
    "dropped_feasible_task_count": 0,
    "dropped_infeasible_task_count": 7778,
    "dropped_selected_action_feasible_count": 0,
    "dropped_selected_action_feasible_count_universe": "U_selected_action_tasks",
    "dropped_selected_action_infeasible_count": 7778,
    "dropped_selected_action_infeasible_count_universe": "U_selected_action_tasks",
    "feasible_task_count": 14,
    "feasible_task_count_definition": "selected_action_feasible_task_count",
    "feasible_task_count_universe": "U_selected_action_tasks",
    "infeasible_task_count": 10491,
    "is_action_collapsed": true,
    "mean_completion_latency_slots": 11.348823866896156,
    "mean_drop_latency_slots": 16.998457186937515,
    "mean_reward": -3309.01,
    "mean_terminal_latency_slots": 15.96418443440815,
    "pending_count": 522,
    "policy_name": "fixed_horizontal_policy",
    "raw_vs_canonical_reward_delta": 3320.0,
    "reward_per_decision": -31.78073376872839,
    "reward_per_task": -31.499381247025227,
    "reward_reconciled": false,
    "selected_action_feasible_ratio": 0.0013326987148976678,
    "selected_action_feasible_task_count": 14,
    "selected_action_feasible_task_count_universe": "U_selected_action_tasks",
    "selected_action_infeasible_task_count": 10491,
    "selected_action_infeasible_task_count_universe": "U_selected_action_tasks",
    "terminal_reconciled": false,
    "unique_task_count": 10505,
    "unique_task_count_universe": "U_unique_tasks"
  },
  "fixed_local_policy": {
    "action_distribution": {
      "horizontal": 0,
      "local": 10412,
      "vertical": 0
    },
    "action_entropy": 0.0,
    "checkpoint_budget": null,
    "completed_count": 2589,
    "completed_feasible_task_count": 35,
    "completed_feasible_task_count_definition": "completed tasks whose selected action was feasible under the same selected-action feasibility estimate",
    "completed_feasible_task_count_universe": "U_selected_action_tasks",
    "completed_infeasible_task_count": 2554,
    "completed_selected_action_feasible_count": 35,
    "completed_selected_action_feasible_count_universe": "U_selected_action_tasks",
    "completed_selected_action_infeasible_count": 2554,
    "completed_selected_action_infeasible_count_universe": "U_selected_action_tasks",
    "completion_ratio": 0.2464540694907187,
    "deadline_violation_ratio": 0.6626368396001904,
    "decision_count": 10412,
    "decision_count_universe": "U_full_decisions",
    "dominant_action_name": "local",
    "dominant_action_share": 1.0,
    "drop_ratio": 0.6626368396001904,
    "dropped_count": 6961,
    "dropped_feasible_task_count": 0,
    "dropped_infeasible_task_count": 6961,
    "dropped_selected_action_feasible_count": 0,
    "dropped_selected_action_feasible_count_universe": "U_selected_action_tasks",
    "dropped_selected_action_infeasible_count": 6961,
    "dropped_selected_action_infeasible_count_universe": "U_selected_action_tasks",
    "feasible_task_count": 35,
    "feasible_task_count_definition": "selected_action_feasible_task_count",
    "feasible_task_count_universe": "U_selected_action_tasks",
    "infeasible_task_count": 10470,
    "is_action_collapsed": true,
    "mean_completion_latency_slots": 10.092699884125144,
    "mean_drop_latency_slots": 16.995977589426808,
    "mean_reward": -3045.7,
    "mean_terminal_latency_slots": 15.124502617801047,
    "pending_count": 433,
    "policy_name": "fixed_local_policy",
    "raw_vs_canonical_reward_delta": 3000.0,
    "reward_per_decision": -29.251824817518248,
    "reward_per_task": -28.992860542598763,
    "reward_reconciled": false,
    "selected_action_feasible_ratio": 0.0033317467872441696,
    "selected_action_feasible_task_count": 35,
    "selected_action_feasible_task_count_universe": "U_selected_action_tasks",
    "selected_action_infeasible_task_count": 10470,
    "selected_action_infeasible_task_count_universe": "U_selected_action_tasks",
    "terminal_reconciled": false,
    "unique_task_count": 10505,
    "unique_task_count_universe": "U_unique_tasks"
  },
  "fixed_vertical_policy": {
    "action_distribution": {
      "horizontal": 0,
      "local": 0,
      "vertical": 10412
    },
    "action_entropy": 0.0,
    "checkpoint_budget": null,
    "completed_count": 1413,
    "completed_feasible_task_count": 14,
    "completed_feasible_task_count_definition": "completed tasks whose selected action was feasible under the same selected-action feasibility estimate",
    "completed_feasible_task_count_universe": "U_selected_action_tasks",
    "completed_infeasible_task_count": 1399,
    "completed_selected_action_feasible_count": 14,
    "completed_selected_action_feasible_count_universe": "U_selected_action_tasks",
    "completed_selected_action_infeasible_count": 1399,
    "completed_selected_action_infeasible_count_universe": "U_selected_action_tasks",
    "completion_ratio": 0.13450737743931462,
    "deadline_violation_ratio": 0.7709662065683008,
    "decision_count": 10412,
    "decision_count_universe": "U_full_decisions",
    "dominant_action_name": "vertical",
    "dominant_action_share": 1.0,
    "drop_ratio": 0.7709662065683008,
    "dropped_count": 8099,
    "dropped_feasible_task_count": 0,
    "dropped_infeasible_task_count": 8099,
    "dropped_selected_action_feasible_count": 0,
    "dropped_selected_action_feasible_count_universe": "U_selected_action_tasks",
    "dropped_selected_action_infeasible_count": 8099,
    "dropped_selected_action_infeasible_count_universe": "U_selected_action_tasks",
    "feasible_task_count": 14,
    "feasible_task_count_definition": "selected_action_feasible_task_count",
    "feasible_task_count_universe": "U_selected_action_tasks",
    "infeasible_task_count": 10491,
    "is_action_collapsed": true,
    "mean_completion_latency_slots": 11.664543524416136,
    "mean_drop_latency_slots": 16.9983948635634,
    "mean_reward": -3404.42,
    "mean_terminal_latency_slots": 16.20605550883095,
    "pending_count": 445,
    "policy_name": "fixed_vertical_policy",
    "raw_vs_canonical_reward_delta": 3400.0,
    "reward_per_decision": -32.697080291970806,
    "reward_per_task": -32.40761542122799,
    "reward_reconciled": false,
    "selected_action_feasible_ratio": 0.0013326987148976678,
    "selected_action_feasible_task_count": 14,
    "selected_action_feasible_task_count_universe": "U_selected_action_tasks",
    "selected_action_infeasible_task_count": 10491,
    "selected_action_infeasible_task_count_universe": "U_selected_action_tasks",
    "terminal_reconciled": false,
    "unique_task_count": 10505,
    "unique_task_count_universe": "U_unique_tasks"
  },
  "policy_affects_reward": "true",
  "policy_affects_reward_boolean": true,
  "policy_affects_terminal_outcomes": "true",
  "policy_affects_terminal_outcomes_boolean": true,
  "policy_summaries": {
    "candidate_policy_at_100": {
      "action_distribution": {
        "horizontal": 0,
        "local": 10412,
        "vertical": 0
      },
      "action_entropy": 0.0,
      "checkpoint_budget": 100,
      "completed_count": 2589,
      "completed_feasible_task_count": 35,
      "completed_feasible_task_count_definition": "completed tasks whose selected action was feasible under the same selected-action feasibility estimate",
      "completed_feasible_task_count_universe": "U_selected_action_tasks",
      "completed_infeasible_task_count": 2554,
      "completed_selected_action_feasible_count": 35,
      "completed_selected_action_feasible_count_universe": "U_selected_action_tasks",
      "completed_selected_action_infeasible_count": 2554,
      "completed_selected_action_infeasible_count_universe": "U_selected_action_tasks",
      "completion_ratio": 0.2464540694907187,
      "deadline_violation_ratio": 0.6626368396001904,
      "decision_count": 10412,
      "decision_count_universe": "U_full_decisions",
      "dominant_action_name": "local",
      "dominant_action_share": 1.0,
      "drop_ratio": 0.6626368396001904,
      "dropped_count": 6961,
      "dropped_feasible_task_count": 0,
      "dropped_infeasible_task_count": 6961,
      "dropped_selected_action_feasible_count": 0,
      "dropped_selected_action_feasible_count_universe": "U_selected_action_tasks",
      "dropped_selected_action_infeasible_count": 6961,
      "dropped_selected_action_infeasible_count_universe": "U_selected_action_tasks",
      "feasible_task_count": 35,
      "feasible_task_count_definition": "selected_action_feasible_task_count",
      "feasible_task_count_universe": "U_selected_action_tasks",
      "infeasible_task_count": 10470,
      "is_action_collapsed": true,
      "mean_completion_latency_slots": 10.092699884125144,
      "mean_drop_latency_slots": 16.995977589426808,
      "mean_reward": -3045.7,
      "mean_terminal_latency_slots": 15.124502617801047,
      "pending_count": 433,
      "policy_name": "candidate_policy_at_100",
      "raw_vs_canonical_reward_delta": 3000.0,
      "reward_per_decision": -29.251824817518248,
      "reward_per_task": -28.992860542598763,
      "reward_reconciled": false,
      "selected_action_feasible_ratio": 0.0033317467872441696,
      "selected_action_feasible_task_count": 35,
      "selected_action_feasible_task_count_universe": "U_selected_action_tasks",
      "selected_action_infeasible_task_count": 10470,
      "selected_action_infeasible_task_count_universe": "U_selected_action_tasks",
      "terminal_reconciled": false,
      "unique_task_count": 10505,
      "unique_task_count_universe": "U_unique_tasks"
    },
    "candidate_policy_at_50": {
      "action_distribution": {
        "horizontal": 9306,
        "local": 0,
        "vertical": 1106
      },
      "action_entropy": 0.4884190075208499,
      "checkpoint_budget": 50,
      "completed_count": 1754,
      "completed_feasible_task_count": 14,
      "completed_feasible_task_count_definition": "completed tasks whose selected action was feasible under the same selected-action feasibility estimate",
      "completed_feasible_task_count_universe": "U_selected_action_tasks",
      "completed_infeasible_task_count": 1740,
      "completed_selected_action_feasible_count": 14,
      "completed_selected_action_feasible_count_universe": "U_selected_action_tasks",
      "completed_selected_action_infeasible_count": 1740,
      "completed_selected_action_infeasible_count_universe": "U_selected_action_tasks",
      "completion_ratio": 0.16696811042360782,
      "deadline_violation_ratio": 0.7393622084721562,
      "decision_count": 10412,
      "decision_count_universe": "U_full_decisions",
      "dominant_action_name": "horizontal",
      "dominant_action_share": 0.893776411832501,
      "drop_ratio": 0.7393622084721562,
      "dropped_count": 7767,
      "dropped_feasible_task_count": 0,
      "dropped_infeasible_task_count": 7767,
      "dropped_selected_action_feasible_count": 0,
      "dropped_selected_action_feasible_count_universe": "U_selected_action_tasks",
      "dropped_selected_action_infeasible_count": 7767,
      "dropped_selected_action_infeasible_count_universe": "U_selected_action_tasks",
      "feasible_task_count": 14,
      "feasible_task_count_definition": "selected_action_feasible_task_count",
      "feasible_task_count_universe": "U_selected_action_tasks",
      "infeasible_task_count": 10491,
      "is_action_collapsed": false,
      "mean_completion_latency_slots": 11.205245153933866,
      "mean_drop_latency_slots": 16.99909875112656,
      "mean_reward": -3303.34,
      "mean_terminal_latency_slots": 15.93172986030879,
      "pending_count": 536,
      "policy_name": "candidate_policy_at_50",
      "raw_vs_canonical_reward_delta": 3320.0,
      "reward_per_decision": -31.726277372262775,
      "reward_per_task": -31.44540694907187,
      "reward_reconciled": false,
      "selected_action_feasible_ratio": 0.0013326987148976678,
      "selected_action_feasible_task_count": 14,
      "selected_action_feasible_task_count_universe": "U_selected_action_tasks",
      "selected_action_infeasible_task_count": 10491,
      "selected_action_infeasible_task_count_universe": "U_selected_action_tasks",
      "terminal_reconciled": false,
      "unique_task_count": 10505,
      "unique_task_count_universe": "U_unique_tasks"
    },
    "fixed_horizontal_policy": {
      "action_distribution": {
        "horizontal": 10412,
        "local": 0,
        "vertical": 0
      },
      "action_entropy": 0.0,
      "checkpoint_budget": null,
      "completed_count": 1743,
      "completed_feasible_task_count": 14,
      "completed_feasible_task_count_definition": "completed tasks whose selected action was feasible under the same selected-action feasibility estimate",
      "completed_feasible_task_count_universe": "U_selected_action_tasks",
      "completed_infeasible_task_count": 1729,
      "completed_selected_action_feasible_count": 14,
      "completed_selected_action_feasible_count_universe": "U_selected_action_tasks",
      "completed_selected_action_infeasible_count": 1729,
      "completed_selected_action_infeasible_count_universe": "U_selected_action_tasks",
      "completion_ratio": 0.16592099000475963,
      "deadline_violation_ratio": 0.7404093288910043,
      "decision_count": 10412,
      "decision_count_universe": "U_full_decisions",
      "dominant_action_name": "horizontal",
      "dominant_action_share": 1.0,
      "drop_ratio": 0.7404093288910043,
      "dropped_count": 7778,
      "dropped_feasible_task_count": 0,
      "dropped_infeasible_task_count": 7778,
      "dropped_selected_action_feasible_count": 0,
      "dropped_selected_action_feasible_count_universe": "U_selected_action_tasks",
      "dropped_selected_action_infeasible_count": 7778,
      "dropped_selected_action_infeasible_count_universe": "U_selected_action_tasks",
      "feasible_task_count": 14,
      "feasible_task_count_definition": "selected_action_feasible_task_count",
      "feasible_task_count_universe": "U_selected_action_tasks",
      "infeasible_task_count": 10491,
      "is_action_collapsed": true,
      "mean_completion_latency_slots": 11.348823866896156,
      "mean_drop_latency_slots": 16.998457186937515,
      "mean_reward": -3309.01,
      "mean_terminal_latency_slots": 15.96418443440815,
      "pending_count": 522,
      "policy_name": "fixed_horizontal_policy",
      "raw_vs_canonical_reward_delta": 3320.0,
      "reward_per_decision": -31.78073376872839,
      "reward_per_task": -31.499381247025227,
      "reward_reconciled": false,
      "selected_action_feasible_ratio": 0.0013326987148976678,
      "selected_action_feasible_task_count": 14,
      "selected_action_feasible_task_count_universe": "U_selected_action_tasks",
      "selected_action_infeasible_task_count": 10491,
      "selected_action_infeasible_task_count_universe": "U_selected_action_tasks",
      "terminal_reconciled": false,
      "unique_task_count": 10505,
      "unique_task_count_universe": "U_unique_tasks"
    },
    "fixed_local_policy": {
      "action_distribution": {
        "horizontal": 0,
        "local": 10412,
        "vertical": 0
      },
      "action_entropy": 0.0,
      "checkpoint_budget": null,
      "completed_count": 2589,
      "completed_feasible_task_count": 35,
      "completed_feasible_task_count_definition": "completed tasks whose selected action was feasible under the same selected-action feasibility estimate",
      "completed_feasible_task_count_universe": "U_selected_action_tasks",
      "completed_infeasible_task_count": 2554,
      "completed_selected_action_feasible_count": 35,
      "completed_selected_action_feasible_count_universe": "U_selected_action_tasks",
      "completed_selected_action_infeasible_count": 2554,
      "completed_selected_action_infeasible_count_universe": "U_selected_action_tasks",
      "completion_ratio": 0.2464540694907187,
      "deadline_violation_ratio": 0.6626368396001904,
      "decision_count": 10412,
      "decision_count_universe": "U_full_decisions",
      "dominant_action_name": "local",
      "dominant_action_share": 1.0,
      "drop_ratio": 0.6626368396001904,
      "dropped_count": 6961,
      "dropped_feasible_task_count": 0,
      "dropped_infeasible_task_count": 6961,
      "dropped_selected_action_feasible_count": 0,
      "dropped_selected_action_feasible_count_universe": "U_selected_action_tasks",
      "dropped_selected_action_infeasible_count": 6961,
      "dropped_selected_action_infeasible_count_universe": "U_selected_action_tasks",
      "feasible_task_count": 35,
      "feasible_task_count_definition": "selected_action_feasible_task_count",
      "feasible_task_count_universe": "U_selected_action_tasks",
      "infeasible_task_count": 10470,
      "is_action_collapsed": true,
      "mean_completion_latency_slots": 10.092699884125144,
      "mean_drop_latency_slots": 16.995977589426808,
      "mean_reward": -3045.7,
      "mean_terminal_latency_slots": 15.124502617801047,
      "pending_count": 433,
      "policy_name": "fixed_local_policy",
      "raw_vs_canonical_reward_delta": 3000.0,
      "reward_per_decision": -29.251824817518248,
      "reward_per_task": -28.992860542598763,
      "reward_reconciled": false,
      "selected_action_feasible_ratio": 0.0033317467872441696,
      "selected_action_feasible_task_count": 35,
      "selected_action_feasible_task_count_universe": "U_selected_action_tasks",
      "selected_action_infeasible_task_count": 10470,
      "selected_action_infeasible_task_count_universe": "U_selected_action_tasks",
      "terminal_reconciled": false,
      "unique_task_count": 10505,
      "unique_task_count_universe": "U_unique_tasks"
    },
    "fixed_vertical_policy": {
      "action_distribution": {
        "horizontal": 0,
        "local": 0,
        "vertical": 10412
      },
      "action_entropy": 0.0,
      "checkpoint_budget": null,
      "completed_count": 1413,
      "completed_feasible_task_count": 14,
      "completed_feasible_task_count_definition": "completed tasks whose selected action was feasible under the same selected-action feasibility estimate",
      "completed_feasible_task_count_universe": "U_selected_action_tasks",
      "completed_infeasible_task_count": 1399,
      "completed_selected_action_feasible_count": 14,
      "completed_selected_action_feasible_count_universe": "U_selected_action_tasks",
      "completed_selected_action_infeasible_count": 1399,
      "completed_selected_action_infeasible_count_universe": "U_selected_action_tasks",
      "completion_ratio": 0.13450737743931462,
      "deadline_violation_ratio": 0.7709662065683008,
      "decision_count": 10412,
      "decision_count_universe": "U_full_decisions",
      "dominant_action_name": "vertical",
      "dominant_action_share": 1.0,
      "drop_ratio": 0.7709662065683008,
      "dropped_count": 8099,
      "dropped_feasible_task_count": 0,
      "dropped_infeasible_task_count": 8099,
      "dropped_selected_action_feasible_count": 0,
      "dropped_selected_action_feasible_count_universe": "U_selected_action_tasks",
      "dropped_selected_action_infeasible_count": 8099,
      "dropped_selected_action_infeasible_count_universe": "U_selected_action_tasks",
      "feasible_task_count": 14,
      "feasible_task_count_definition": "selected_action_feasible_task_count",
      "feasible_task_count_universe": "U_selected_action_tasks",
      "infeasible_task_count": 10491,
      "is_action_collapsed": true,
      "mean_completion_latency_slots": 11.664543524416136,
      "mean_drop_latency_slots": 16.9983948635634,
      "mean_reward": -3404.42,
      "mean_terminal_latency_slots": 16.20605550883095,
      "pending_count": 445,
      "policy_name": "fixed_vertical_policy",
      "raw_vs_canonical_reward_delta": 3400.0,
      "reward_per_decision": -32.697080291970806,
      "reward_per_task": -32.40761542122799,
      "reward_reconciled": false,
      "selected_action_feasible_ratio": 0.0013326987148976678,
      "selected_action_feasible_task_count": 14,
      "selected_action_feasible_task_count_universe": "U_selected_action_tasks",
      "selected_action_infeasible_task_count": 10491,
      "selected_action_infeasible_task_count_universe": "U_selected_action_tasks",
      "terminal_reconciled": false,
      "unique_task_count": 10505,
      "unique_task_count_universe": "U_unique_tasks"
    },
    "random_legal_policy": {
      "action_distribution": {
        "horizontal": 3495,
        "local": 3431,
        "vertical": 3486
      },
      "action_entropy": 1.5849144934148753,
      "checkpoint_budget": null,
      "completed_count": 2551,
      "completed_feasible_task_count": 21,
      "completed_feasible_task_count_definition": "completed tasks whose selected action was feasible under the same selected-action feasibility estimate",
      "completed_feasible_task_count_universe": "U_selected_action_tasks",
      "completed_infeasible_task_count": 2530,
      "completed_selected_action_feasible_count": 21,
      "completed_selected_action_feasible_count_universe": "U_selected_action_tasks",
      "completed_selected_action_infeasible_count": 2530,
      "completed_selected_action_infeasible_count_universe": "U_selected_action_tasks",
      "completion_ratio": 0.24283674440742503,
      "deadline_violation_ratio": 0.6664445502141837,
      "decision_count": 10412,
      "decision_count_universe": "U_full_decisions",
      "dominant_action_name": "horizontal",
      "dominant_action_share": 0.33567038033038804,
      "drop_ratio": 0.6664445502141837,
      "dropped_count": 7001,
      "dropped_feasible_task_count": 0,
      "dropped_infeasible_task_count": 7001,
      "dropped_selected_action_feasible_count": 0,
      "dropped_selected_action_feasible_count_universe": "U_selected_action_tasks",
      "dropped_selected_action_infeasible_count": 7001,
      "dropped_selected_action_infeasible_count_universe": "U_selected_action_tasks",
      "feasible_task_count": 21,
      "feasible_task_count_definition": "selected_action_feasible_task_count",
      "feasible_task_count_universe": "U_selected_action_tasks",
      "infeasible_task_count": 10484,
      "is_action_collapsed": false,
      "mean_completion_latency_slots": 10.112112896903175,
      "mean_drop_latency_slots": 16.99885730609913,
      "mean_reward": -3058.36,
      "mean_terminal_latency_slots": 15.15965242881072,
      "pending_count": 713,
      "policy_name": "random_legal_policy",
      "raw_vs_canonical_reward_delta": 3120.0,
      "reward_per_decision": -29.37341529004994,
      "reward_per_task": -29.11337458353165,
      "reward_reconciled": false,
      "selected_action_feasible_ratio": 0.001999048072346502,
      "selected_action_feasible_task_count": 21,
      "selected_action_feasible_task_count_universe": "U_selected_action_tasks",
      "selected_action_infeasible_task_count": 10484,
      "selected_action_infeasible_task_count_universe": "U_selected_action_tasks",
      "terminal_reconciled": false,
      "unique_task_count": 10505,
      "unique_task_count_universe": "U_unique_tasks"
    }
  },
  "random_legal_policy": {
    "action_distribution": {
      "horizontal": 3495,
      "local": 3431,
      "vertical": 3486
    },
    "action_entropy": 1.5849144934148753,
    "checkpoint_budget": null,
    "completed_count": 2551,
    "completed_feasible_task_count": 21,
    "completed_feasible_task_count_definition": "completed tasks whose selected action was feasible under the same selected-action feasibility estimate",
    "completed_feasible_task_count_universe": "U_selected_action_tasks",
    "completed_infeasible_task_count": 2530,
    "completed_selected_action_feasible_count": 21,
    "completed_selected_action_feasible_count_universe": "U_selected_action_tasks",
    "completed_selected_action_infeasible_count": 2530,
    "completed_selected_action_infeasible_count_universe": "U_selected_action_tasks",
    "completion_ratio": 0.24283674440742503,
    "deadline_violation_ratio": 0.6664445502141837,
    "decision_count": 10412,
    "decision_count_universe": "U_full_decisions",
    "dominant_action_name": "horizontal",
    "dominant_action_share": 0.33567038033038804,
    "drop_ratio": 0.6664445502141837,
    "dropped_count": 7001,
    "dropped_feasible_task_count": 0,
    "dropped_infeasible_task_count": 7001,
    "dropped_selected_action_feasible_count": 0,
    "dropped_selected_action_feasible_count_universe": "U_selected_action_tasks",
    "dropped_selected_action_infeasible_count": 7001,
    "dropped_selected_action_infeasible_count_universe": "U_selected_action_tasks",
    "feasible_task_count": 21,
    "feasible_task_count_definition": "selected_action_feasible_task_count",
    "feasible_task_count_universe": "U_selected_action_tasks",
    "infeasible_task_count": 10484,
    "is_action_collapsed": false,
    "mean_completion_latency_slots": 10.112112896903175,
    "mean_drop_latency_slots": 16.99885730609913,
    "mean_reward": -3058.36,
    "mean_terminal_latency_slots": 15.15965242881072,
    "pending_count": 713,
    "policy_name": "random_legal_policy",
    "raw_vs_canonical_reward_delta": 3120.0,
    "reward_per_decision": -29.37341529004994,
    "reward_per_task": -29.11337458353165,
    "reward_reconciled": false,
    "selected_action_feasible_ratio": 0.001999048072346502,
    "selected_action_feasible_task_count": 21,
    "selected_action_feasible_task_count_universe": "U_selected_action_tasks",
    "selected_action_infeasible_task_count": 10484,
    "selected_action_infeasible_task_count_universe": "U_selected_action_tasks",
    "terminal_reconciled": false,
    "unique_task_count": 10505,
    "unique_task_count_universe": "U_unique_tasks"
  },
  "raw_event_reward_static_across_budget": false
}

## 8. Reconciliation After Decision-State Fix
{
  "policies_with_reward_reconciled_false": [
    "candidate_policy_at_50",
    "candidate_policy_at_100",
    "fixed_local_policy",
    "fixed_horizontal_policy",
    "fixed_vertical_policy",
    "random_legal_policy"
  ],
  "policies_with_terminal_reconciled_false": [
    "candidate_policy_at_50",
    "candidate_policy_at_100",
    "fixed_local_policy",
    "fixed_horizontal_policy",
    "fixed_vertical_policy",
    "random_legal_policy"
  ],
  "raw_vs_canonical_reward_delta_max": 3400.0,
  "reward_reconciliation_passed": false,
  "terminal_reconciliation_passed": false
}

## 9. Diagnostic Decision
{
  "decision_reason": "The repaired decision-time state path failed one or more required consistency checks.",
  "evidence_notes": [
    "reward_reconciliation_failed",
    "terminal_reconciliation_failed"
  ],
  "recommended_next_action": "blocked_due_to_state_profile_integration_failure"
}

## 10. Claim Safety
{
  "baseline_superiority_claim_made": false,
  "claim_safety_passed": true,
  "paper_reproduction_claim_made": false,
  "performance_superiority_claim_made": false
}

## 11. Figure Manifest
{
  "figure_count": 5,
  "figure_directory": "artifacts/analysis/state-profile-decision-time-integration-recovery/figures",
  "figure_files": [
    "figure_01_decision_state_injection_before_after.png",
    "figure_02_action_distribution_after_decision_state_fix.png",
    "figure_03_action_collapse_after_decision_state_fix.png",
    "figure_04_selected_action_feasibility_after_decision_state_fix.png",
    "figure_05_completion_drop_after_decision_state_fix.png"
  ],
  "figures_generated": true
}

## 12. Final Verdict
state_profile_decision_time_integration_blocked
