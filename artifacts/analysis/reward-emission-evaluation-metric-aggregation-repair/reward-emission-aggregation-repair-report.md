# Reward Emission and Evaluation Metric Aggregation Repair

- feature_id: `066-reward-emission-evaluation-metric-aggregation-repair`
- final_verdict: `reward_emission_aggregation_repair_ready`
- recommended_next_feature: `State-reward alignment repair`
- diagnostic_decision: `fix_state_representation_next`

## 1. Feature 065 Prerequisite Verification
{
  "feature_065_prerequisite_verified": true,
  "prerequisite_artifacts": {
    "feature_065_report": {
      "details": "Feature 065 diagnostic report validated as prerequisite",
      "exists": true,
      "path": "artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic/evaluation-instrumentation-diagnostic-report.json",
      "verified": true
    }
  },
  "prerequisite_tags_verified": [
    {
      "details": "current branch matches Feature 066",
      "name": "branch",
      "verified": true
    },
    {
      "details": "current branch is not main",
      "name": "not_main",
      "verified": true
    },
    {
      "details": "Feature 065 report validated",
      "name": "feature_065_report_valid",
      "verified": true
    },
    {
      "details": "working tree paths stay inside the approved scope",
      "name": "working_tree_paths_approved",
      "verified": true
    },
    {
      "details": "staged paths stay inside the approved scope",
      "name": "staged_paths_approved",
      "verified": true
    },
    {
      "details": "base-branch diff stays inside the approved scope",
      "name": "base_branch_head_diff_approved",
      "verified": true
    }
  ]
}

## 2. Evaluation Action Logging Repair Result
{
  "by_checkpoint": [
    {
      "decision_count": 3,
      "evaluation_action_distribution_source": "evaluation_episodes",
      "sample_records": [
        {
          "episode_id": 0,
          "selected_action": "vertical",
          "task_id": 1,
          "trace_id": "trace-0"
        }
      ],
      "training_budget": 100
    },
    {
      "decision_count": 3,
      "evaluation_action_distribution_source": "evaluation_episodes",
      "sample_records": [
        {
          "episode_id": 0,
          "selected_action": "vertical",
          "task_id": 1,
          "trace_id": "trace-0"
        }
      ],
      "training_budget": 150
    },
    {
      "decision_count": 3,
      "evaluation_action_distribution_source": "evaluation_episodes",
      "sample_records": [
        {
          "episode_id": 0,
          "selected_action": "vertical",
          "task_id": 1,
          "trace_id": "trace-0"
        }
      ],
      "training_budget": 200
    },
    {
      "decision_count": 3,
      "evaluation_action_distribution_source": "evaluation_episodes",
      "sample_records": [
        {
          "episode_id": 0,
          "selected_action": "vertical",
          "task_id": 1,
          "trace_id": "trace-0"
        }
      ],
      "training_budget": 500
    }
  ],
  "evaluation_action_distribution_source": "evaluation_episodes",
  "record_count": 12,
  "sample_records": [
    {
      "episode_id": 0,
      "selected_action": "vertical",
      "task_id": 1,
      "trace_id": "trace-0"
    },
    {
      "episode_id": 0,
      "selected_action": "vertical",
      "task_id": 1,
      "trace_id": "trace-0"
    },
    {
      "episode_id": 0,
      "selected_action": "vertical",
      "task_id": 1,
      "trace_id": "trace-0"
    },
    {
      "episode_id": 0,
      "selected_action": "vertical",
      "task_id": 1,
      "trace_id": "trace-0"
    }
  ]
}

## 3. Replay Rolling-Window Interpretation Repair Result
{
  "checkpoint_budgets": [
    100,
    150,
    200,
    500
  ],
  "replay_window_capacity": 10000,
  "replay_window_warning": true,
  "training_mode": "cumulative_staged_diagnostic_repair"
}

## 4. Per-Action Outcome Attribution Result
{
  "horizontal": {
    "canonical_completion_ratio": 0.0,
    "canonical_deadline_violation_ratio": 0.0,
    "canonical_drop_ratio": 0.0,
    "canonical_pending_ratio": 1.0,
    "canonical_reward_count": 0,
    "canonical_reward_total": 0.0,
    "canonical_task_count": 1,
    "canonical_task_mean_reward": 0.0,
    "canonical_terminal_task_count": 0,
    "completed_count": 0,
    "completion_reward_count": 0,
    "decision_count": 1,
    "double_count_detected": false,
    "drop_penalty_count": 0,
    "dropped_count": 0,
    "duplicate_reward_event_count": 0,
    "duplicate_terminal_event_count": 0,
    "mean_completion_latency_slots": null,
    "mean_drop_latency_slots": null,
    "mean_reward": 0.0,
    "mean_terminal_latency_slots": null,
    "pending_at_horizon_count": 1,
    "raw_event_reward_count": 0,
    "raw_event_reward_total": 0.0,
    "raw_reward_emission_count": 0,
    "raw_terminal_event_count": 0,
    "raw_vs_canonical_reward_delta": 0.0,
    "reward_bearing_transition_count": 0,
    "terminal_transition_count": 0,
    "total_reward": 0.0,
    "unknown_count": 0
  },
  "local": {
    "canonical_completion_ratio": 0.0,
    "canonical_deadline_violation_ratio": 0.0,
    "canonical_drop_ratio": 0.0,
    "canonical_pending_ratio": 0.0,
    "canonical_reward_count": 0,
    "canonical_reward_total": 0.0,
    "canonical_task_count": 0,
    "canonical_task_mean_reward": 0.0,
    "canonical_terminal_task_count": 0,
    "completed_count": 0,
    "completion_reward_count": 0,
    "decision_count": 0,
    "double_count_detected": false,
    "drop_penalty_count": 0,
    "dropped_count": 0,
    "duplicate_reward_event_count": 0,
    "duplicate_terminal_event_count": 0,
    "mean_completion_latency_slots": null,
    "mean_drop_latency_slots": null,
    "mean_reward": 0.0,
    "mean_terminal_latency_slots": null,
    "pending_at_horizon_count": 0,
    "raw_event_reward_count": 0,
    "raw_event_reward_total": 0.0,
    "raw_reward_emission_count": 0,
    "raw_terminal_event_count": 0,
    "raw_vs_canonical_reward_delta": 0.0,
    "reward_bearing_transition_count": 0,
    "terminal_transition_count": 0,
    "total_reward": 0.0,
    "unknown_count": 0
  },
  "vertical": {
    "canonical_completion_ratio": 0.5,
    "canonical_deadline_violation_ratio": 0.5,
    "canonical_drop_ratio": 0.5,
    "canonical_pending_ratio": 0.0,
    "canonical_reward_count": 2,
    "canonical_reward_total": -44.0,
    "canonical_task_count": 2,
    "canonical_task_mean_reward": -22.0,
    "canonical_terminal_task_count": 2,
    "completed_count": 1,
    "completion_reward_count": 1,
    "decision_count": 2,
    "double_count_detected": true,
    "drop_penalty_count": 1,
    "dropped_count": 1,
    "duplicate_reward_event_count": 0,
    "duplicate_terminal_event_count": 1,
    "mean_completion_latency_slots": 4.0,
    "mean_drop_latency_slots": 4.0,
    "mean_reward": -22.0,
    "mean_terminal_latency_slots": 4.0,
    "pending_at_horizon_count": 0,
    "raw_event_reward_count": 2,
    "raw_event_reward_total": -44.0,
    "raw_reward_emission_count": 2,
    "raw_terminal_event_count": 3,
    "raw_vs_canonical_reward_delta": 0.0,
    "reward_bearing_transition_count": 2,
    "terminal_transition_count": 2,
    "total_reward": -44.0,
    "unknown_count": 0
  }
}

## 5. Reward Decomposition Result
{
  "canonical_task_mean_reward_by_action": {
    "horizontal": 0.0,
    "local": 0.0,
    "vertical": -22.0
  },
  "canonical_task_reward_count_by_action": {
    "horizontal": 0,
    "local": 0,
    "vertical": 2
  },
  "canonical_task_reward_total_by_action": {
    "horizontal": 0.0,
    "local": 0.0,
    "vertical": -44.0
  },
  "completion_reward_count_by_action": {
    "horizontal": 0,
    "local": 0,
    "vertical": 1
  },
  "drop_penalty_count_by_action": {
    "horizontal": 0,
    "local": 0,
    "vertical": 1
  },
  "nan_reward_count": 0,
  "raw_event_reward_count_by_action": {
    "horizontal": 0,
    "local": 0,
    "vertical": 2
  },
  "raw_event_reward_total_by_action": {
    "horizontal": 0.0,
    "local": 0.0,
    "vertical": -44.0
  },
  "raw_vs_canonical_reward_delta_by_action": {
    "horizontal": 0.0,
    "local": 0.0,
    "vertical": 0.0
  },
  "raw_vs_canonical_reward_delta_total": 0.0,
  "reward_available_count": 2,
  "reward_by_action": {
    "horizontal": 0.0,
    "local": 0.0,
    "vertical": -44.0
  },
  "reward_by_action_and_terminal_outcome": {
    "horizontal": {
      "completed": {
        "canonical_task_mean_reward": 0.0,
        "canonical_task_reward_count": 0,
        "canonical_task_reward_total": 0.0,
        "count": 0,
        "mean_reward": 0.0,
        "raw_event_reward_count": 0,
        "raw_event_reward_total": 0.0,
        "raw_vs_canonical_reward_delta": 0.0,
        "total_reward": 0.0
      },
      "dropped": {
        "canonical_task_mean_reward": 0.0,
        "canonical_task_reward_count": 0,
        "canonical_task_reward_total": 0.0,
        "count": 0,
        "mean_reward": 0.0,
        "raw_event_reward_count": 0,
        "raw_event_reward_total": 0.0,
        "raw_vs_canonical_reward_delta": 0.0,
        "total_reward": 0.0
      }
    },
    "local": {
      "completed": {
        "canonical_task_mean_reward": 0.0,
        "canonical_task_reward_count": 0,
        "canonical_task_reward_total": 0.0,
        "count": 0,
        "mean_reward": 0.0,
        "raw_event_reward_count": 0,
        "raw_event_reward_total": 0.0,
        "raw_vs_canonical_reward_delta": 0.0,
        "total_reward": 0.0
      },
      "dropped": {
        "canonical_task_mean_reward": 0.0,
        "canonical_task_reward_count": 0,
        "canonical_task_reward_total": 0.0,
        "count": 0,
        "mean_reward": 0.0,
        "raw_event_reward_count": 0,
        "raw_event_reward_total": 0.0,
        "raw_vs_canonical_reward_delta": 0.0,
        "total_reward": 0.0
      }
    },
    "vertical": {
      "completed": {
        "canonical_task_mean_reward": -4.0,
        "canonical_task_reward_count": 1,
        "canonical_task_reward_total": -4.0,
        "count": 1,
        "mean_reward": -4.0,
        "raw_event_reward_count": 1,
        "raw_event_reward_total": -4.0,
        "raw_vs_canonical_reward_delta": 0.0,
        "total_reward": -4.0
      },
      "dropped": {
        "canonical_task_mean_reward": -40.0,
        "canonical_task_reward_count": 1,
        "canonical_task_reward_total": -40.0,
        "count": 1,
        "mean_reward": -40.0,
        "raw_event_reward_count": 1,
        "raw_event_reward_total": -40.0,
        "raw_vs_canonical_reward_delta": 0.0,
        "total_reward": -40.0
      }
    }
  },
  "reward_by_terminal_outcome": {
    "completed": -4.0,
    "dropped": -40.0
  },
  "zero_reward_count": 0
}

## 6. State Feature Coverage Audit Result
{
  "status": "not captured in this repair"
}

## 7. Policy-Effect Diagnostic Result
{
  "candidate_action_distribution_changed_by_budget": true,
  "candidate_policy_vertical_collapse_in_evaluation": true,
  "candidate_policy_vertical_collapse_in_training_replay_window": true,
  "candidate_reward_variation": 0.0,
  "candidate_terminal_outcomes_changed_by_budget": false,
  "canonical_completion_rate_static_across_budget": true,
  "canonical_drop_rate_static_across_budget": true,
  "canonical_policy_effect_summary": {},
  "canonical_task_reward_static_across_budget": true,
  "episode_length": 110,
  "evaluation_action_distribution_static_across_budget": false,
  "evaluation_episode_count": 100,
  "evaluation_metric_static_because_environment_dynamics": "uncertain",
  "evaluation_metric_static_because_policy_same": "false",
  "evaluation_metric_static_because_reward_aggregation": "true",
  "evaluation_reward_static_after_instrumentation": true,
  "evaluation_trace_bank_id": "eval-bank",
  "policy_affects_reward": "false",
  "policy_affects_terminal_outcomes": "false",
  "policy_results": {
    "candidate_policy_at_100": {
      "action_distribution": {
        "horizontal": 1,
        "local": 1,
        "vertical": 1
      },
      "candidate_policy_vertical_share": 0.3333333333333333,
      "canonical_reward_decomposition": {
        "canonical_task_mean_reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -22.0
        },
        "canonical_task_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "canonical_task_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "completion_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "drop_penalty_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "nan_reward_count": 0,
        "raw_event_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "raw_event_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "raw_vs_canonical_reward_delta_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": 0.0
        },
        "raw_vs_canonical_reward_delta_total": 0.0,
        "reward_available_count": 2,
        "reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "reward_by_action_and_terminal_outcome": {
          "horizontal": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "local": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "vertical": {
            "completed": {
              "canonical_task_mean_reward": -4.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -4.0,
              "count": 1,
              "mean_reward": -4.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -4.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -4.0
            },
            "dropped": {
              "canonical_task_mean_reward": -40.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -40.0,
              "count": 1,
              "mean_reward": -40.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -40.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -40.0
            }
          }
        },
        "reward_by_terminal_outcome": {
          "completed": -4.0,
          "dropped": -40.0
        },
        "zero_reward_count": 0
      },
      "canonical_task_outcome_summary": {
        "by_action": {
          "horizontal": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 1.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 1,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 1,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "local": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 0,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 0,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "vertical": {
            "canonical_completion_ratio": 0.5,
            "canonical_deadline_violation_ratio": 0.5,
            "canonical_drop_ratio": 0.5,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 2,
            "canonical_reward_total": -44.0,
            "canonical_task_count": 2,
            "canonical_task_mean_reward": -22.0,
            "canonical_terminal_task_count": 2,
            "completed_count": 1,
            "completion_reward_count": 1,
            "decision_count": 2,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_completion_latency_slots": 4.0,
            "mean_drop_latency_slots": 4.0,
            "mean_reward": -22.0,
            "mean_terminal_latency_slots": 4.0,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          }
        },
        "checkpoint_budget": 100,
        "overall": {
          "canonical_completion_count": 1,
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_count": 1,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 1,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_count": 2,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_task_count": 3,
          "canonical_task_mean_reward": -22.0,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 2,
          "canonical_unknown_count": 0,
          "completed_count": 1,
          "completion_reward_count": 1,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_reward": 0.0,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        },
        "reward_coverage": {
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "reward_available_count": 2
        }
      },
      "canonical_task_reconciliation": {
        "by_action": {
          "horizontal": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 1.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 1,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 1,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "local": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 0,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 0,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "vertical": {
            "canonical_completion_ratio": 0.5,
            "canonical_deadline_violation_ratio": 0.5,
            "canonical_drop_ratio": 0.5,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 2,
            "canonical_reward_total": -44.0,
            "canonical_task_count": 2,
            "canonical_task_mean_reward": -22.0,
            "canonical_terminal_task_count": 2,
            "completed_count": 1,
            "completion_reward_count": 1,
            "decision_count": 2,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_completion_latency_slots": 4.0,
            "mean_drop_latency_slots": 4.0,
            "mean_reward": -22.0,
            "mean_terminal_latency_slots": 4.0,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          }
        },
        "checkpoint_budget": 100,
        "overall": {
          "canonical_completion_count": 1,
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_count": 1,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 1,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_count": 2,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_task_count": 3,
          "canonical_task_mean_reward": -22.0,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 2,
          "canonical_unknown_count": 0,
          "completed_count": 1,
          "completion_reward_count": 1,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_reward": 0.0,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        },
        "reward_coverage": {
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "reward_available_count": 2
        }
      },
      "canonical_task_reward_count": 2,
      "canonical_task_reward_total": -44.0,
      "checkpoint_budget": 100,
      "completed_count": 1,
      "completed_task_count": 1,
      "completion_ratio": 0.3333333333333333,
      "deadline_violation_ratio": 0.3333333333333333,
      "decision_records_summary": {
        "decision_count": 3,
        "evaluation_action_distribution_source": "evaluation_episodes",
        "sample_records": [
          {
            "episode_id": 0,
            "selected_action": "vertical",
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "drop_ratio": 0.3333333333333333,
      "dropped_count": 1,
      "dropped_task_count": 1,
      "episode_length": 110,
      "episode_reward_totals": [
        -44.0
      ],
      "episode_summaries": [
        {
          "canonical_reward_total": -44.0,
          "completion_count": 1,
          "decision_count": 3,
          "drop_count": 1,
          "episode_id": 0,
          "pending_count": 1,
          "raw_reward_event_count": 2,
          "raw_reward_total": -44.0,
          "reward_recovered": true,
          "terminal_task_count": 2,
          "trace_id": "trace-0",
          "unknown_count": 0
        }
      ],
      "evaluation_action_by_episode_id": {
        "0": {
          "decision_count": 3
        }
      },
      "evaluation_action_by_trace_id": {
        "trace-0": {
          "decision_count": 3
        }
      },
      "evaluation_action_distribution": {
        "horizontal": 1,
        "local": 1,
        "vertical": 1
      },
      "evaluation_action_distribution_source": "evaluation_episodes",
      "evaluation_action_sequence_sample": [
        {
          "episode_id": 0,
          "selected_action": "vertical",
          "task_id": 1,
          "trace_id": "trace-0"
        }
      ],
      "evaluation_decision_count": 3,
      "evaluation_episode_count": 100,
      "evaluation_legal_action_mask_distribution": {
        "local=1|horizontal=1|vertical=1": 3
      },
      "evaluation_reward_summary": {
        "candidate_reproduction_supported": true,
        "canonical_task_count": 3,
        "canonical_task_reward_count": 2,
        "canonical_task_reward_total": -44.0,
        "completed_task_count": 1,
        "dropped_task_count": 1,
        "evaluation_episode_count": 100,
        "evaluation_on_training_traces": false,
        "mean_reward": -44.0,
        "pending_at_horizon_count": 1,
        "raw_event_reward_count": 2,
        "raw_event_reward_total": -44.0,
        "raw_reward_emission_count": 2,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 3,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_available_count": 2,
        "reward_bearing_transition_count": 2,
        "same_evaluation_trace_bank": true,
        "terminal_event_recovery_blocked": false,
        "terminal_transition_count": 2,
        "trace_bank_disjoint": true,
        "trace_bank_ids": {
          "evaluation": "eval-bank",
          "training": "train-bank"
        },
        "trace_ids": [
          "trace-0"
        ],
        "unknown_task_count": 0
      },
      "evaluation_trace_bank_id": "eval-bank",
      "mean_latency_slots": 4.0,
      "paper_aligned_diagnostic_metrics": {
        "canonical_completion_ratio": 0.3333333333333333,
        "canonical_deadline_violation_ratio": 0.3333333333333333,
        "canonical_drop_ratio": 0.3333333333333333,
        "canonical_mean_completion_latency_slots": 4.0,
        "canonical_mean_drop_latency_slots": 4.0,
        "canonical_mean_terminal_latency_slots": 4.0,
        "canonical_pending_ratio": 0.3333333333333333,
        "canonical_reward_per_decision": -14.666666666666666,
        "canonical_reward_per_task": -14.666666666666666,
        "canonical_tasks_per_decision": 1.0,
        "raw_reward_event_coverage_ratio": 1.0,
        "reward_reconciliation_status": "passed",
        "terminal_event_coverage_ratio": 1.5,
        "training_budget": 100
      },
      "pending_at_horizon_count": 1,
      "pending_task_count": 1,
      "per_action_outcome_summary": {
        "horizontal": {
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 0.0,
          "canonical_drop_ratio": 0.0,
          "canonical_pending_ratio": 1.0,
          "canonical_reward_count": 0,
          "canonical_reward_total": 0.0,
          "canonical_task_count": 1,
          "canonical_task_mean_reward": 0.0,
          "canonical_terminal_task_count": 0,
          "completed_count": 0,
          "completion_reward_count": 0,
          "decision_count": 1,
          "double_count_detected": false,
          "drop_penalty_count": 0,
          "dropped_count": 0,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "mean_completion_latency_slots": null,
          "mean_drop_latency_slots": null,
          "mean_reward": 0.0,
          "mean_terminal_latency_slots": null,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 0,
          "raw_event_reward_total": 0.0,
          "raw_reward_emission_count": 0,
          "raw_terminal_event_count": 0,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 0,
          "terminal_transition_count": 0,
          "total_reward": 0.0,
          "unknown_count": 0
        },
        "local": {
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 0.0,
          "canonical_drop_ratio": 0.0,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_count": 0,
          "canonical_reward_total": 0.0,
          "canonical_task_count": 0,
          "canonical_task_mean_reward": 0.0,
          "canonical_terminal_task_count": 0,
          "completed_count": 0,
          "completion_reward_count": 0,
          "decision_count": 0,
          "double_count_detected": false,
          "drop_penalty_count": 0,
          "dropped_count": 0,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "mean_completion_latency_slots": null,
          "mean_drop_latency_slots": null,
          "mean_reward": 0.0,
          "mean_terminal_latency_slots": null,
          "pending_at_horizon_count": 0,
          "raw_event_reward_count": 0,
          "raw_event_reward_total": 0.0,
          "raw_reward_emission_count": 0,
          "raw_terminal_event_count": 0,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 0,
          "terminal_transition_count": 0,
          "total_reward": 0.0,
          "unknown_count": 0
        },
        "vertical": {
          "canonical_completion_ratio": 0.5,
          "canonical_deadline_violation_ratio": 0.5,
          "canonical_drop_ratio": 0.5,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_count": 2,
          "canonical_reward_total": -44.0,
          "canonical_task_count": 2,
          "canonical_task_mean_reward": -22.0,
          "canonical_terminal_task_count": 2,
          "completed_count": 1,
          "completion_reward_count": 1,
          "decision_count": 2,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_completion_latency_slots": 4.0,
          "mean_drop_latency_slots": 4.0,
          "mean_reward": -22.0,
          "mean_terminal_latency_slots": 4.0,
          "pending_at_horizon_count": 0,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        }
      },
      "policy_kind": "candidate",
      "policy_name": "candidate_policy_at_100",
      "raw_event_reward_count": 2,
      "raw_event_reward_total": -44.0,
      "raw_lifecycle_terminal_event_count": 3,
      "raw_reward_event_count": 2,
      "raw_reward_event_recovery_blocked": false,
      "raw_reward_total": -44.0,
      "raw_terminal_event_count": 3,
      "raw_vs_canonical_reward_reconciliation": {
        "canonical_task_count": 3,
        "canonical_task_reward_count": 2,
        "canonical_task_reward_total": -44.0,
        "canonical_terminal_task_count": 2,
        "checkpoint_budget": 100,
        "duplicate_reward_event_count": 0,
        "duplicate_terminal_event_count": 1,
        "raw_event_reward_count": 2,
        "raw_event_reward_total": -44.0,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 3,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_reconciled": true,
        "terminal_event_recovery_blocked": false
      },
      "reconciliation": {
        "canonical_reward_decomposition": {
          "canonical_task_mean_reward_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -22.0
          },
          "canonical_task_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 2
          },
          "canonical_task_reward_total_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "completion_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 1
          },
          "drop_penalty_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 1
          },
          "nan_reward_count": 0,
          "raw_event_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 2
          },
          "raw_event_reward_total_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "raw_vs_canonical_reward_delta_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": 0.0
          },
          "raw_vs_canonical_reward_delta_total": 0.0,
          "reward_available_count": 2,
          "reward_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "reward_by_action_and_terminal_outcome": {
            "horizontal": {
              "completed": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              },
              "dropped": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              }
            },
            "local": {
              "completed": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              },
              "dropped": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              }
            },
            "vertical": {
              "completed": {
                "canonical_task_mean_reward": -4.0,
                "canonical_task_reward_count": 1,
                "canonical_task_reward_total": -4.0,
                "count": 1,
                "mean_reward": -4.0,
                "raw_event_reward_count": 1,
                "raw_event_reward_total": -4.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": -4.0
              },
              "dropped": {
                "canonical_task_mean_reward": -40.0,
                "canonical_task_reward_count": 1,
                "canonical_task_reward_total": -40.0,
                "count": 1,
                "mean_reward": -40.0,
                "raw_event_reward_count": 1,
                "raw_event_reward_total": -40.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": -40.0
              }
            }
          },
          "reward_by_terminal_outcome": {
            "completed": -4.0,
            "dropped": -40.0
          },
          "zero_reward_count": 0
        },
        "canonical_task_outcome_sample": [
          {
            "arrival_slot": 0,
            "canonical_join_key": "trace-1:0:1",
            "canonical_reward": -40.0,
            "canonical_terminal_outcome": "dropped",
            "completion_or_drop_slot": 3,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "episode_id": 0,
            "first_decision_slot": 0,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -40.0,
            "raw_terminal_event_count": 2,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 1,
            "terminal_slot": 3,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 1,
            "canonical_join_key": "trace-1:0:2",
            "canonical_reward": -4.0,
            "canonical_terminal_outcome": "completed",
            "completion_or_drop_slot": 4,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 1,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -4.0,
            "raw_terminal_event_count": 1,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 2,
            "terminal_slot": 4,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 2,
            "canonical_join_key": "trace-1:0:3",
            "canonical_reward": 0.0,
            "canonical_terminal_outcome": "pending_at_horizon",
            "completion_or_drop_slot": null,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 2,
            "latency_slots": null,
            "raw_reward_event_count": 0,
            "raw_reward_total": 0.0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "horizontal",
            "task_id": 3,
            "terminal_slot": 5,
            "trace_id": "trace-1"
          }
        ],
        "canonical_task_outcome_summary": {
          "by_action": {
            "horizontal": {
              "canonical_completion_ratio": 0.0,
              "canonical_deadline_violation_ratio": 0.0,
              "canonical_drop_ratio": 0.0,
              "canonical_pending_ratio": 1.0,
              "canonical_reward_count": 0,
              "canonical_reward_total": 0.0,
              "canonical_task_count": 1,
              "canonical_task_mean_reward": 0.0,
              "canonical_terminal_task_count": 0,
              "completed_count": 0,
              "completion_reward_count": 0,
              "decision_count": 1,
              "double_count_detected": false,
              "drop_penalty_count": 0,
              "dropped_count": 0,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 0,
              "mean_completion_latency_slots": null,
              "mean_drop_latency_slots": null,
              "mean_reward": 0.0,
              "mean_terminal_latency_slots": null,
              "pending_at_horizon_count": 1,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_reward_emission_count": 0,
              "raw_terminal_event_count": 0,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 0,
              "terminal_transition_count": 0,
              "total_reward": 0.0,
              "unknown_count": 0
            },
            "local": {
              "canonical_completion_ratio": 0.0,
              "canonical_deadline_violation_ratio": 0.0,
              "canonical_drop_ratio": 0.0,
              "canonical_pending_ratio": 0.0,
              "canonical_reward_count": 0,
              "canonical_reward_total": 0.0,
              "canonical_task_count": 0,
              "canonical_task_mean_reward": 0.0,
              "canonical_terminal_task_count": 0,
              "completed_count": 0,
              "completion_reward_count": 0,
              "decision_count": 0,
              "double_count_detected": false,
              "drop_penalty_count": 0,
              "dropped_count": 0,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 0,
              "mean_completion_latency_slots": null,
              "mean_drop_latency_slots": null,
              "mean_reward": 0.0,
              "mean_terminal_latency_slots": null,
              "pending_at_horizon_count": 0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_reward_emission_count": 0,
              "raw_terminal_event_count": 0,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 0,
              "terminal_transition_count": 0,
              "total_reward": 0.0,
              "unknown_count": 0
            },
            "vertical": {
              "canonical_completion_ratio": 0.5,
              "canonical_deadline_violation_ratio": 0.5,
              "canonical_drop_ratio": 0.5,
              "canonical_pending_ratio": 0.0,
              "canonical_reward_count": 2,
              "canonical_reward_total": -44.0,
              "canonical_task_count": 2,
              "canonical_task_mean_reward": -22.0,
              "canonical_terminal_task_count": 2,
              "completed_count": 1,
              "completion_reward_count": 1,
              "decision_count": 2,
              "double_count_detected": true,
              "drop_penalty_count": 1,
              "dropped_count": 1,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 1,
              "mean_completion_latency_slots": 4.0,
              "mean_drop_latency_slots": 4.0,
              "mean_reward": -22.0,
              "mean_terminal_latency_slots": 4.0,
              "pending_at_horizon_count": 0,
              "raw_event_reward_count": 2,
              "raw_event_reward_total": -44.0,
              "raw_reward_emission_count": 2,
              "raw_terminal_event_count": 3,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 2,
              "terminal_transition_count": 2,
              "total_reward": -44.0,
              "unknown_count": 0
            }
          },
          "checkpoint_budget": 100,
          "overall": {
            "canonical_completion_count": 1,
            "canonical_completion_ratio": 0.3333333333333333,
            "canonical_deadline_violation_ratio": 0.3333333333333333,
            "canonical_drop_count": 1,
            "canonical_drop_ratio": 0.3333333333333333,
            "canonical_mean_completion_latency_slots": 4.0,
            "canonical_mean_drop_latency_slots": 4.0,
            "canonical_mean_terminal_latency_slots": 4.0,
            "canonical_pending_count": 1,
            "canonical_pending_ratio": 0.3333333333333333,
            "canonical_reward_count": 2,
            "canonical_reward_per_decision": -14.666666666666666,
            "canonical_reward_per_task": -14.666666666666666,
            "canonical_task_count": 3,
            "canonical_task_mean_reward": -22.0,
            "canonical_task_reward_count": 2,
            "canonical_task_reward_total": -44.0,
            "canonical_tasks_per_decision": 1.0,
            "canonical_terminal_task_count": 2,
            "canonical_unknown_count": 0,
            "completed_count": 1,
            "completion_reward_count": 1,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_reward": 0.0,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_reward_event_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          },
          "reward_coverage": {
            "raw_reward_event_count": 2,
            "raw_terminal_event_count": 3,
            "reward_available_count": 2
          }
        },
        "canonical_task_outcomes": [
          {
            "arrival_slot": 0,
            "canonical_join_key": "trace-1:0:1",
            "canonical_reward": -40.0,
            "canonical_terminal_outcome": "dropped",
            "completion_or_drop_slot": 3,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "episode_id": 0,
            "first_decision_slot": 0,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -40.0,
            "raw_terminal_event_count": 2,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 1,
            "terminal_slot": 3,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 1,
            "canonical_join_key": "trace-1:0:2",
            "canonical_reward": -4.0,
            "canonical_terminal_outcome": "completed",
            "completion_or_drop_slot": 4,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 1,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -4.0,
            "raw_terminal_event_count": 1,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 2,
            "terminal_slot": 4,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 2,
            "canonical_join_key": "trace-1:0:3",
            "canonical_reward": 0.0,
            "canonical_terminal_outcome": "pending_at_horizon",
            "completion_or_drop_slot": null,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 2,
            "latency_slots": null,
            "raw_reward_event_count": 0,
            "raw_reward_total": 0.0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "horizontal",
            "task_id": 3,
            "terminal_slot": 5,
            "trace_id": "trace-1"
          }
        ],
        "checkpoint_budget": 100,
        "decision_count": 3,
        "paper_aligned_diagnostic_metrics": {
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_tasks_per_decision": 1.0,
          "raw_reward_event_coverage_ratio": 1.0,
          "reward_reconciliation_status": "passed",
          "terminal_event_coverage_ratio": 1.5,
          "training_budget": 100
        },
        "raw_vs_canonical_reward_reconciliation": {
          "canonical_task_count": 3,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_terminal_task_count": 2,
          "checkpoint_budget": 100,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_event_recovery_blocked": false,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_reconciled": true,
          "terminal_event_recovery_blocked": false
        }
      },
      "reward_decomposition": {
        "canonical_task_mean_reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -22.0
        },
        "canonical_task_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "canonical_task_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "completion_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "drop_penalty_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "nan_reward_count": 0,
        "raw_event_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "raw_event_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "raw_vs_canonical_reward_delta_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": 0.0
        },
        "raw_vs_canonical_reward_delta_total": 0.0,
        "reward_available_count": 2,
        "reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "reward_by_action_and_terminal_outcome": {
          "horizontal": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "local": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "vertical": {
            "completed": {
              "canonical_task_mean_reward": -4.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -4.0,
              "count": 1,
              "mean_reward": -4.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -4.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -4.0
            },
            "dropped": {
              "canonical_task_mean_reward": -40.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -40.0,
              "count": 1,
              "mean_reward": -40.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -40.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -40.0
            }
          }
        },
        "reward_by_terminal_outcome": {
          "completed": -4.0,
          "dropped": -40.0
        },
        "zero_reward_count": 0
      },
      "reward_event_records": {
        "raw_reward_event_recovery_blocked": false,
        "record_count": 2,
        "reward_available_count": 2,
        "sample_records": [
          {
            "episode_id": 0,
            "raw_reward": -40.0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "reward_reconciled": true,
      "reward_reconciliation_status": "passed",
      "reward_reconciliation_tolerance": 1e-09,
      "same_evaluation_trace_bank": true,
      "terminal_event_records": {
        "record_count": 3,
        "recovered_from_finalized_tasks": true,
        "sample_records": [
          {
            "episode_id": 0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "terminal_event_recovery_blocked": false,
      "unknown_count": 0
    },
    "candidate_policy_at_150": {
      "action_distribution": {
        "horizontal": 1,
        "local": 1,
        "vertical": 1
      },
      "candidate_policy_vertical_share": 0.3333333333333333,
      "canonical_reward_decomposition": {
        "canonical_task_mean_reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -22.0
        },
        "canonical_task_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "canonical_task_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "completion_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "drop_penalty_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "nan_reward_count": 0,
        "raw_event_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "raw_event_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "raw_vs_canonical_reward_delta_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": 0.0
        },
        "raw_vs_canonical_reward_delta_total": 0.0,
        "reward_available_count": 2,
        "reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "reward_by_action_and_terminal_outcome": {
          "horizontal": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "local": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "vertical": {
            "completed": {
              "canonical_task_mean_reward": -4.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -4.0,
              "count": 1,
              "mean_reward": -4.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -4.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -4.0
            },
            "dropped": {
              "canonical_task_mean_reward": -40.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -40.0,
              "count": 1,
              "mean_reward": -40.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -40.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -40.0
            }
          }
        },
        "reward_by_terminal_outcome": {
          "completed": -4.0,
          "dropped": -40.0
        },
        "zero_reward_count": 0
      },
      "canonical_task_outcome_summary": {
        "by_action": {
          "horizontal": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 1.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 1,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 1,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "local": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 0,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 0,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "vertical": {
            "canonical_completion_ratio": 0.5,
            "canonical_deadline_violation_ratio": 0.5,
            "canonical_drop_ratio": 0.5,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 2,
            "canonical_reward_total": -44.0,
            "canonical_task_count": 2,
            "canonical_task_mean_reward": -22.0,
            "canonical_terminal_task_count": 2,
            "completed_count": 1,
            "completion_reward_count": 1,
            "decision_count": 2,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_completion_latency_slots": 4.0,
            "mean_drop_latency_slots": 4.0,
            "mean_reward": -22.0,
            "mean_terminal_latency_slots": 4.0,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          }
        },
        "checkpoint_budget": 150,
        "overall": {
          "canonical_completion_count": 1,
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_count": 1,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 1,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_count": 2,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_task_count": 3,
          "canonical_task_mean_reward": -22.0,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 2,
          "canonical_unknown_count": 0,
          "completed_count": 1,
          "completion_reward_count": 1,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_reward": 0.0,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        },
        "reward_coverage": {
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "reward_available_count": 2
        }
      },
      "canonical_task_reconciliation": {
        "by_action": {
          "horizontal": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 1.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 1,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 1,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "local": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 0,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 0,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "vertical": {
            "canonical_completion_ratio": 0.5,
            "canonical_deadline_violation_ratio": 0.5,
            "canonical_drop_ratio": 0.5,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 2,
            "canonical_reward_total": -44.0,
            "canonical_task_count": 2,
            "canonical_task_mean_reward": -22.0,
            "canonical_terminal_task_count": 2,
            "completed_count": 1,
            "completion_reward_count": 1,
            "decision_count": 2,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_completion_latency_slots": 4.0,
            "mean_drop_latency_slots": 4.0,
            "mean_reward": -22.0,
            "mean_terminal_latency_slots": 4.0,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          }
        },
        "checkpoint_budget": 150,
        "overall": {
          "canonical_completion_count": 1,
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_count": 1,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 1,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_count": 2,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_task_count": 3,
          "canonical_task_mean_reward": -22.0,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 2,
          "canonical_unknown_count": 0,
          "completed_count": 1,
          "completion_reward_count": 1,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_reward": 0.0,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        },
        "reward_coverage": {
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "reward_available_count": 2
        }
      },
      "canonical_task_reward_count": 2,
      "canonical_task_reward_total": -44.0,
      "checkpoint_budget": 150,
      "completed_count": 1,
      "completed_task_count": 1,
      "completion_ratio": 0.3333333333333333,
      "deadline_violation_ratio": 0.3333333333333333,
      "decision_records_summary": {
        "decision_count": 3,
        "evaluation_action_distribution_source": "evaluation_episodes",
        "sample_records": [
          {
            "episode_id": 0,
            "selected_action": "vertical",
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "drop_ratio": 0.3333333333333333,
      "dropped_count": 1,
      "dropped_task_count": 1,
      "episode_length": 110,
      "episode_reward_totals": [
        -44.0
      ],
      "episode_summaries": [
        {
          "canonical_reward_total": -44.0,
          "completion_count": 1,
          "decision_count": 3,
          "drop_count": 1,
          "episode_id": 0,
          "pending_count": 1,
          "raw_reward_event_count": 2,
          "raw_reward_total": -44.0,
          "reward_recovered": true,
          "terminal_task_count": 2,
          "trace_id": "trace-0",
          "unknown_count": 0
        }
      ],
      "evaluation_action_by_episode_id": {
        "0": {
          "decision_count": 3
        }
      },
      "evaluation_action_by_trace_id": {
        "trace-0": {
          "decision_count": 3
        }
      },
      "evaluation_action_distribution": {
        "horizontal": 1,
        "local": 1,
        "vertical": 1
      },
      "evaluation_action_distribution_source": "evaluation_episodes",
      "evaluation_action_sequence_sample": [
        {
          "episode_id": 0,
          "selected_action": "vertical",
          "task_id": 1,
          "trace_id": "trace-0"
        }
      ],
      "evaluation_decision_count": 3,
      "evaluation_episode_count": 100,
      "evaluation_legal_action_mask_distribution": {
        "local=1|horizontal=1|vertical=1": 3
      },
      "evaluation_reward_summary": {
        "candidate_reproduction_supported": true,
        "canonical_task_count": 3,
        "canonical_task_reward_count": 2,
        "canonical_task_reward_total": -44.0,
        "completed_task_count": 1,
        "dropped_task_count": 1,
        "evaluation_episode_count": 100,
        "evaluation_on_training_traces": false,
        "mean_reward": -44.0,
        "pending_at_horizon_count": 1,
        "raw_event_reward_count": 2,
        "raw_event_reward_total": -44.0,
        "raw_reward_emission_count": 2,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 3,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_available_count": 2,
        "reward_bearing_transition_count": 2,
        "same_evaluation_trace_bank": true,
        "terminal_event_recovery_blocked": false,
        "terminal_transition_count": 2,
        "trace_bank_disjoint": true,
        "trace_bank_ids": {
          "evaluation": "eval-bank",
          "training": "train-bank"
        },
        "trace_ids": [
          "trace-0"
        ],
        "unknown_task_count": 0
      },
      "evaluation_trace_bank_id": "eval-bank",
      "mean_latency_slots": 4.0,
      "paper_aligned_diagnostic_metrics": {
        "canonical_completion_ratio": 0.3333333333333333,
        "canonical_deadline_violation_ratio": 0.3333333333333333,
        "canonical_drop_ratio": 0.3333333333333333,
        "canonical_mean_completion_latency_slots": 4.0,
        "canonical_mean_drop_latency_slots": 4.0,
        "canonical_mean_terminal_latency_slots": 4.0,
        "canonical_pending_ratio": 0.3333333333333333,
        "canonical_reward_per_decision": -14.666666666666666,
        "canonical_reward_per_task": -14.666666666666666,
        "canonical_tasks_per_decision": 1.0,
        "raw_reward_event_coverage_ratio": 1.0,
        "reward_reconciliation_status": "passed",
        "terminal_event_coverage_ratio": 1.5,
        "training_budget": 150
      },
      "pending_at_horizon_count": 1,
      "pending_task_count": 1,
      "per_action_outcome_summary": {
        "horizontal": {
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 0.0,
          "canonical_drop_ratio": 0.0,
          "canonical_pending_ratio": 1.0,
          "canonical_reward_count": 0,
          "canonical_reward_total": 0.0,
          "canonical_task_count": 1,
          "canonical_task_mean_reward": 0.0,
          "canonical_terminal_task_count": 0,
          "completed_count": 0,
          "completion_reward_count": 0,
          "decision_count": 1,
          "double_count_detected": false,
          "drop_penalty_count": 0,
          "dropped_count": 0,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "mean_completion_latency_slots": null,
          "mean_drop_latency_slots": null,
          "mean_reward": 0.0,
          "mean_terminal_latency_slots": null,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 0,
          "raw_event_reward_total": 0.0,
          "raw_reward_emission_count": 0,
          "raw_terminal_event_count": 0,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 0,
          "terminal_transition_count": 0,
          "total_reward": 0.0,
          "unknown_count": 0
        },
        "local": {
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 0.0,
          "canonical_drop_ratio": 0.0,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_count": 0,
          "canonical_reward_total": 0.0,
          "canonical_task_count": 0,
          "canonical_task_mean_reward": 0.0,
          "canonical_terminal_task_count": 0,
          "completed_count": 0,
          "completion_reward_count": 0,
          "decision_count": 0,
          "double_count_detected": false,
          "drop_penalty_count": 0,
          "dropped_count": 0,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "mean_completion_latency_slots": null,
          "mean_drop_latency_slots": null,
          "mean_reward": 0.0,
          "mean_terminal_latency_slots": null,
          "pending_at_horizon_count": 0,
          "raw_event_reward_count": 0,
          "raw_event_reward_total": 0.0,
          "raw_reward_emission_count": 0,
          "raw_terminal_event_count": 0,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 0,
          "terminal_transition_count": 0,
          "total_reward": 0.0,
          "unknown_count": 0
        },
        "vertical": {
          "canonical_completion_ratio": 0.5,
          "canonical_deadline_violation_ratio": 0.5,
          "canonical_drop_ratio": 0.5,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_count": 2,
          "canonical_reward_total": -44.0,
          "canonical_task_count": 2,
          "canonical_task_mean_reward": -22.0,
          "canonical_terminal_task_count": 2,
          "completed_count": 1,
          "completion_reward_count": 1,
          "decision_count": 2,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_completion_latency_slots": 4.0,
          "mean_drop_latency_slots": 4.0,
          "mean_reward": -22.0,
          "mean_terminal_latency_slots": 4.0,
          "pending_at_horizon_count": 0,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        }
      },
      "policy_kind": "candidate",
      "policy_name": "candidate_policy_at_150",
      "raw_event_reward_count": 2,
      "raw_event_reward_total": -44.0,
      "raw_lifecycle_terminal_event_count": 3,
      "raw_reward_event_count": 2,
      "raw_reward_event_recovery_blocked": false,
      "raw_reward_total": -44.0,
      "raw_terminal_event_count": 3,
      "raw_vs_canonical_reward_reconciliation": {
        "canonical_task_count": 3,
        "canonical_task_reward_count": 2,
        "canonical_task_reward_total": -44.0,
        "canonical_terminal_task_count": 2,
        "checkpoint_budget": 150,
        "duplicate_reward_event_count": 0,
        "duplicate_terminal_event_count": 1,
        "raw_event_reward_count": 2,
        "raw_event_reward_total": -44.0,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 3,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_reconciled": true,
        "terminal_event_recovery_blocked": false
      },
      "reconciliation": {
        "canonical_reward_decomposition": {
          "canonical_task_mean_reward_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -22.0
          },
          "canonical_task_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 2
          },
          "canonical_task_reward_total_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "completion_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 1
          },
          "drop_penalty_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 1
          },
          "nan_reward_count": 0,
          "raw_event_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 2
          },
          "raw_event_reward_total_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "raw_vs_canonical_reward_delta_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": 0.0
          },
          "raw_vs_canonical_reward_delta_total": 0.0,
          "reward_available_count": 2,
          "reward_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "reward_by_action_and_terminal_outcome": {
            "horizontal": {
              "completed": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              },
              "dropped": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              }
            },
            "local": {
              "completed": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              },
              "dropped": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              }
            },
            "vertical": {
              "completed": {
                "canonical_task_mean_reward": -4.0,
                "canonical_task_reward_count": 1,
                "canonical_task_reward_total": -4.0,
                "count": 1,
                "mean_reward": -4.0,
                "raw_event_reward_count": 1,
                "raw_event_reward_total": -4.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": -4.0
              },
              "dropped": {
                "canonical_task_mean_reward": -40.0,
                "canonical_task_reward_count": 1,
                "canonical_task_reward_total": -40.0,
                "count": 1,
                "mean_reward": -40.0,
                "raw_event_reward_count": 1,
                "raw_event_reward_total": -40.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": -40.0
              }
            }
          },
          "reward_by_terminal_outcome": {
            "completed": -4.0,
            "dropped": -40.0
          },
          "zero_reward_count": 0
        },
        "canonical_task_outcome_sample": [
          {
            "arrival_slot": 0,
            "canonical_join_key": "trace-1:0:1",
            "canonical_reward": -40.0,
            "canonical_terminal_outcome": "dropped",
            "completion_or_drop_slot": 3,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "episode_id": 0,
            "first_decision_slot": 0,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -40.0,
            "raw_terminal_event_count": 2,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 1,
            "terminal_slot": 3,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 1,
            "canonical_join_key": "trace-1:0:2",
            "canonical_reward": -4.0,
            "canonical_terminal_outcome": "completed",
            "completion_or_drop_slot": 4,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 1,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -4.0,
            "raw_terminal_event_count": 1,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 2,
            "terminal_slot": 4,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 2,
            "canonical_join_key": "trace-1:0:3",
            "canonical_reward": 0.0,
            "canonical_terminal_outcome": "pending_at_horizon",
            "completion_or_drop_slot": null,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 2,
            "latency_slots": null,
            "raw_reward_event_count": 0,
            "raw_reward_total": 0.0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "horizontal",
            "task_id": 3,
            "terminal_slot": 5,
            "trace_id": "trace-1"
          }
        ],
        "canonical_task_outcome_summary": {
          "by_action": {
            "horizontal": {
              "canonical_completion_ratio": 0.0,
              "canonical_deadline_violation_ratio": 0.0,
              "canonical_drop_ratio": 0.0,
              "canonical_pending_ratio": 1.0,
              "canonical_reward_count": 0,
              "canonical_reward_total": 0.0,
              "canonical_task_count": 1,
              "canonical_task_mean_reward": 0.0,
              "canonical_terminal_task_count": 0,
              "completed_count": 0,
              "completion_reward_count": 0,
              "decision_count": 1,
              "double_count_detected": false,
              "drop_penalty_count": 0,
              "dropped_count": 0,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 0,
              "mean_completion_latency_slots": null,
              "mean_drop_latency_slots": null,
              "mean_reward": 0.0,
              "mean_terminal_latency_slots": null,
              "pending_at_horizon_count": 1,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_reward_emission_count": 0,
              "raw_terminal_event_count": 0,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 0,
              "terminal_transition_count": 0,
              "total_reward": 0.0,
              "unknown_count": 0
            },
            "local": {
              "canonical_completion_ratio": 0.0,
              "canonical_deadline_violation_ratio": 0.0,
              "canonical_drop_ratio": 0.0,
              "canonical_pending_ratio": 0.0,
              "canonical_reward_count": 0,
              "canonical_reward_total": 0.0,
              "canonical_task_count": 0,
              "canonical_task_mean_reward": 0.0,
              "canonical_terminal_task_count": 0,
              "completed_count": 0,
              "completion_reward_count": 0,
              "decision_count": 0,
              "double_count_detected": false,
              "drop_penalty_count": 0,
              "dropped_count": 0,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 0,
              "mean_completion_latency_slots": null,
              "mean_drop_latency_slots": null,
              "mean_reward": 0.0,
              "mean_terminal_latency_slots": null,
              "pending_at_horizon_count": 0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_reward_emission_count": 0,
              "raw_terminal_event_count": 0,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 0,
              "terminal_transition_count": 0,
              "total_reward": 0.0,
              "unknown_count": 0
            },
            "vertical": {
              "canonical_completion_ratio": 0.5,
              "canonical_deadline_violation_ratio": 0.5,
              "canonical_drop_ratio": 0.5,
              "canonical_pending_ratio": 0.0,
              "canonical_reward_count": 2,
              "canonical_reward_total": -44.0,
              "canonical_task_count": 2,
              "canonical_task_mean_reward": -22.0,
              "canonical_terminal_task_count": 2,
              "completed_count": 1,
              "completion_reward_count": 1,
              "decision_count": 2,
              "double_count_detected": true,
              "drop_penalty_count": 1,
              "dropped_count": 1,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 1,
              "mean_completion_latency_slots": 4.0,
              "mean_drop_latency_slots": 4.0,
              "mean_reward": -22.0,
              "mean_terminal_latency_slots": 4.0,
              "pending_at_horizon_count": 0,
              "raw_event_reward_count": 2,
              "raw_event_reward_total": -44.0,
              "raw_reward_emission_count": 2,
              "raw_terminal_event_count": 3,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 2,
              "terminal_transition_count": 2,
              "total_reward": -44.0,
              "unknown_count": 0
            }
          },
          "checkpoint_budget": 150,
          "overall": {
            "canonical_completion_count": 1,
            "canonical_completion_ratio": 0.3333333333333333,
            "canonical_deadline_violation_ratio": 0.3333333333333333,
            "canonical_drop_count": 1,
            "canonical_drop_ratio": 0.3333333333333333,
            "canonical_mean_completion_latency_slots": 4.0,
            "canonical_mean_drop_latency_slots": 4.0,
            "canonical_mean_terminal_latency_slots": 4.0,
            "canonical_pending_count": 1,
            "canonical_pending_ratio": 0.3333333333333333,
            "canonical_reward_count": 2,
            "canonical_reward_per_decision": -14.666666666666666,
            "canonical_reward_per_task": -14.666666666666666,
            "canonical_task_count": 3,
            "canonical_task_mean_reward": -22.0,
            "canonical_task_reward_count": 2,
            "canonical_task_reward_total": -44.0,
            "canonical_tasks_per_decision": 1.0,
            "canonical_terminal_task_count": 2,
            "canonical_unknown_count": 0,
            "completed_count": 1,
            "completion_reward_count": 1,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_reward": 0.0,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_reward_event_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          },
          "reward_coverage": {
            "raw_reward_event_count": 2,
            "raw_terminal_event_count": 3,
            "reward_available_count": 2
          }
        },
        "canonical_task_outcomes": [
          {
            "arrival_slot": 0,
            "canonical_join_key": "trace-1:0:1",
            "canonical_reward": -40.0,
            "canonical_terminal_outcome": "dropped",
            "completion_or_drop_slot": 3,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "episode_id": 0,
            "first_decision_slot": 0,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -40.0,
            "raw_terminal_event_count": 2,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 1,
            "terminal_slot": 3,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 1,
            "canonical_join_key": "trace-1:0:2",
            "canonical_reward": -4.0,
            "canonical_terminal_outcome": "completed",
            "completion_or_drop_slot": 4,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 1,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -4.0,
            "raw_terminal_event_count": 1,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 2,
            "terminal_slot": 4,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 2,
            "canonical_join_key": "trace-1:0:3",
            "canonical_reward": 0.0,
            "canonical_terminal_outcome": "pending_at_horizon",
            "completion_or_drop_slot": null,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 2,
            "latency_slots": null,
            "raw_reward_event_count": 0,
            "raw_reward_total": 0.0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "horizontal",
            "task_id": 3,
            "terminal_slot": 5,
            "trace_id": "trace-1"
          }
        ],
        "checkpoint_budget": 150,
        "decision_count": 3,
        "paper_aligned_diagnostic_metrics": {
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_tasks_per_decision": 1.0,
          "raw_reward_event_coverage_ratio": 1.0,
          "reward_reconciliation_status": "passed",
          "terminal_event_coverage_ratio": 1.5,
          "training_budget": 150
        },
        "raw_vs_canonical_reward_reconciliation": {
          "canonical_task_count": 3,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_terminal_task_count": 2,
          "checkpoint_budget": 150,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_event_recovery_blocked": false,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_reconciled": true,
          "terminal_event_recovery_blocked": false
        }
      },
      "reward_decomposition": {
        "canonical_task_mean_reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -22.0
        },
        "canonical_task_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "canonical_task_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "completion_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "drop_penalty_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "nan_reward_count": 0,
        "raw_event_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "raw_event_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "raw_vs_canonical_reward_delta_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": 0.0
        },
        "raw_vs_canonical_reward_delta_total": 0.0,
        "reward_available_count": 2,
        "reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "reward_by_action_and_terminal_outcome": {
          "horizontal": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "local": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "vertical": {
            "completed": {
              "canonical_task_mean_reward": -4.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -4.0,
              "count": 1,
              "mean_reward": -4.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -4.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -4.0
            },
            "dropped": {
              "canonical_task_mean_reward": -40.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -40.0,
              "count": 1,
              "mean_reward": -40.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -40.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -40.0
            }
          }
        },
        "reward_by_terminal_outcome": {
          "completed": -4.0,
          "dropped": -40.0
        },
        "zero_reward_count": 0
      },
      "reward_event_records": {
        "raw_reward_event_recovery_blocked": false,
        "record_count": 2,
        "reward_available_count": 2,
        "sample_records": [
          {
            "episode_id": 0,
            "raw_reward": -40.0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "reward_reconciled": true,
      "reward_reconciliation_status": "passed",
      "reward_reconciliation_tolerance": 1e-09,
      "same_evaluation_trace_bank": true,
      "terminal_event_records": {
        "record_count": 3,
        "recovered_from_finalized_tasks": true,
        "sample_records": [
          {
            "episode_id": 0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "terminal_event_recovery_blocked": false,
      "unknown_count": 0
    },
    "candidate_policy_at_200": {
      "action_distribution": {
        "horizontal": 1,
        "local": 1,
        "vertical": 1
      },
      "candidate_policy_vertical_share": 0.3333333333333333,
      "canonical_reward_decomposition": {
        "canonical_task_mean_reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -22.0
        },
        "canonical_task_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "canonical_task_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "completion_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "drop_penalty_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "nan_reward_count": 0,
        "raw_event_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "raw_event_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "raw_vs_canonical_reward_delta_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": 0.0
        },
        "raw_vs_canonical_reward_delta_total": 0.0,
        "reward_available_count": 2,
        "reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "reward_by_action_and_terminal_outcome": {
          "horizontal": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "local": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "vertical": {
            "completed": {
              "canonical_task_mean_reward": -4.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -4.0,
              "count": 1,
              "mean_reward": -4.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -4.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -4.0
            },
            "dropped": {
              "canonical_task_mean_reward": -40.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -40.0,
              "count": 1,
              "mean_reward": -40.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -40.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -40.0
            }
          }
        },
        "reward_by_terminal_outcome": {
          "completed": -4.0,
          "dropped": -40.0
        },
        "zero_reward_count": 0
      },
      "canonical_task_outcome_summary": {
        "by_action": {
          "horizontal": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 1.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 1,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 1,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "local": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 0,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 0,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "vertical": {
            "canonical_completion_ratio": 0.5,
            "canonical_deadline_violation_ratio": 0.5,
            "canonical_drop_ratio": 0.5,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 2,
            "canonical_reward_total": -44.0,
            "canonical_task_count": 2,
            "canonical_task_mean_reward": -22.0,
            "canonical_terminal_task_count": 2,
            "completed_count": 1,
            "completion_reward_count": 1,
            "decision_count": 2,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_completion_latency_slots": 4.0,
            "mean_drop_latency_slots": 4.0,
            "mean_reward": -22.0,
            "mean_terminal_latency_slots": 4.0,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          }
        },
        "checkpoint_budget": 200,
        "overall": {
          "canonical_completion_count": 1,
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_count": 1,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 1,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_count": 2,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_task_count": 3,
          "canonical_task_mean_reward": -22.0,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 2,
          "canonical_unknown_count": 0,
          "completed_count": 1,
          "completion_reward_count": 1,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_reward": 0.0,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        },
        "reward_coverage": {
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "reward_available_count": 2
        }
      },
      "canonical_task_reconciliation": {
        "by_action": {
          "horizontal": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 1.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 1,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 1,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "local": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 0,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 0,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "vertical": {
            "canonical_completion_ratio": 0.5,
            "canonical_deadline_violation_ratio": 0.5,
            "canonical_drop_ratio": 0.5,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 2,
            "canonical_reward_total": -44.0,
            "canonical_task_count": 2,
            "canonical_task_mean_reward": -22.0,
            "canonical_terminal_task_count": 2,
            "completed_count": 1,
            "completion_reward_count": 1,
            "decision_count": 2,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_completion_latency_slots": 4.0,
            "mean_drop_latency_slots": 4.0,
            "mean_reward": -22.0,
            "mean_terminal_latency_slots": 4.0,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          }
        },
        "checkpoint_budget": 200,
        "overall": {
          "canonical_completion_count": 1,
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_count": 1,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 1,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_count": 2,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_task_count": 3,
          "canonical_task_mean_reward": -22.0,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 2,
          "canonical_unknown_count": 0,
          "completed_count": 1,
          "completion_reward_count": 1,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_reward": 0.0,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        },
        "reward_coverage": {
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "reward_available_count": 2
        }
      },
      "canonical_task_reward_count": 2,
      "canonical_task_reward_total": -44.0,
      "checkpoint_budget": 200,
      "completed_count": 1,
      "completed_task_count": 1,
      "completion_ratio": 0.3333333333333333,
      "deadline_violation_ratio": 0.3333333333333333,
      "decision_records_summary": {
        "decision_count": 3,
        "evaluation_action_distribution_source": "evaluation_episodes",
        "sample_records": [
          {
            "episode_id": 0,
            "selected_action": "vertical",
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "drop_ratio": 0.3333333333333333,
      "dropped_count": 1,
      "dropped_task_count": 1,
      "episode_length": 110,
      "episode_reward_totals": [
        -44.0
      ],
      "episode_summaries": [
        {
          "canonical_reward_total": -44.0,
          "completion_count": 1,
          "decision_count": 3,
          "drop_count": 1,
          "episode_id": 0,
          "pending_count": 1,
          "raw_reward_event_count": 2,
          "raw_reward_total": -44.0,
          "reward_recovered": true,
          "terminal_task_count": 2,
          "trace_id": "trace-0",
          "unknown_count": 0
        }
      ],
      "evaluation_action_by_episode_id": {
        "0": {
          "decision_count": 3
        }
      },
      "evaluation_action_by_trace_id": {
        "trace-0": {
          "decision_count": 3
        }
      },
      "evaluation_action_distribution": {
        "horizontal": 1,
        "local": 1,
        "vertical": 1
      },
      "evaluation_action_distribution_source": "evaluation_episodes",
      "evaluation_action_sequence_sample": [
        {
          "episode_id": 0,
          "selected_action": "vertical",
          "task_id": 1,
          "trace_id": "trace-0"
        }
      ],
      "evaluation_decision_count": 3,
      "evaluation_episode_count": 100,
      "evaluation_legal_action_mask_distribution": {
        "local=1|horizontal=1|vertical=1": 3
      },
      "evaluation_reward_summary": {
        "candidate_reproduction_supported": true,
        "canonical_task_count": 3,
        "canonical_task_reward_count": 2,
        "canonical_task_reward_total": -44.0,
        "completed_task_count": 1,
        "dropped_task_count": 1,
        "evaluation_episode_count": 100,
        "evaluation_on_training_traces": false,
        "mean_reward": -44.0,
        "pending_at_horizon_count": 1,
        "raw_event_reward_count": 2,
        "raw_event_reward_total": -44.0,
        "raw_reward_emission_count": 2,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 3,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_available_count": 2,
        "reward_bearing_transition_count": 2,
        "same_evaluation_trace_bank": true,
        "terminal_event_recovery_blocked": false,
        "terminal_transition_count": 2,
        "trace_bank_disjoint": true,
        "trace_bank_ids": {
          "evaluation": "eval-bank",
          "training": "train-bank"
        },
        "trace_ids": [
          "trace-0"
        ],
        "unknown_task_count": 0
      },
      "evaluation_trace_bank_id": "eval-bank",
      "mean_latency_slots": 4.0,
      "paper_aligned_diagnostic_metrics": {
        "canonical_completion_ratio": 0.3333333333333333,
        "canonical_deadline_violation_ratio": 0.3333333333333333,
        "canonical_drop_ratio": 0.3333333333333333,
        "canonical_mean_completion_latency_slots": 4.0,
        "canonical_mean_drop_latency_slots": 4.0,
        "canonical_mean_terminal_latency_slots": 4.0,
        "canonical_pending_ratio": 0.3333333333333333,
        "canonical_reward_per_decision": -14.666666666666666,
        "canonical_reward_per_task": -14.666666666666666,
        "canonical_tasks_per_decision": 1.0,
        "raw_reward_event_coverage_ratio": 1.0,
        "reward_reconciliation_status": "passed",
        "terminal_event_coverage_ratio": 1.5,
        "training_budget": 200
      },
      "pending_at_horizon_count": 1,
      "pending_task_count": 1,
      "per_action_outcome_summary": {
        "horizontal": {
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 0.0,
          "canonical_drop_ratio": 0.0,
          "canonical_pending_ratio": 1.0,
          "canonical_reward_count": 0,
          "canonical_reward_total": 0.0,
          "canonical_task_count": 1,
          "canonical_task_mean_reward": 0.0,
          "canonical_terminal_task_count": 0,
          "completed_count": 0,
          "completion_reward_count": 0,
          "decision_count": 1,
          "double_count_detected": false,
          "drop_penalty_count": 0,
          "dropped_count": 0,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "mean_completion_latency_slots": null,
          "mean_drop_latency_slots": null,
          "mean_reward": 0.0,
          "mean_terminal_latency_slots": null,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 0,
          "raw_event_reward_total": 0.0,
          "raw_reward_emission_count": 0,
          "raw_terminal_event_count": 0,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 0,
          "terminal_transition_count": 0,
          "total_reward": 0.0,
          "unknown_count": 0
        },
        "local": {
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 0.0,
          "canonical_drop_ratio": 0.0,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_count": 0,
          "canonical_reward_total": 0.0,
          "canonical_task_count": 0,
          "canonical_task_mean_reward": 0.0,
          "canonical_terminal_task_count": 0,
          "completed_count": 0,
          "completion_reward_count": 0,
          "decision_count": 0,
          "double_count_detected": false,
          "drop_penalty_count": 0,
          "dropped_count": 0,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "mean_completion_latency_slots": null,
          "mean_drop_latency_slots": null,
          "mean_reward": 0.0,
          "mean_terminal_latency_slots": null,
          "pending_at_horizon_count": 0,
          "raw_event_reward_count": 0,
          "raw_event_reward_total": 0.0,
          "raw_reward_emission_count": 0,
          "raw_terminal_event_count": 0,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 0,
          "terminal_transition_count": 0,
          "total_reward": 0.0,
          "unknown_count": 0
        },
        "vertical": {
          "canonical_completion_ratio": 0.5,
          "canonical_deadline_violation_ratio": 0.5,
          "canonical_drop_ratio": 0.5,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_count": 2,
          "canonical_reward_total": -44.0,
          "canonical_task_count": 2,
          "canonical_task_mean_reward": -22.0,
          "canonical_terminal_task_count": 2,
          "completed_count": 1,
          "completion_reward_count": 1,
          "decision_count": 2,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_completion_latency_slots": 4.0,
          "mean_drop_latency_slots": 4.0,
          "mean_reward": -22.0,
          "mean_terminal_latency_slots": 4.0,
          "pending_at_horizon_count": 0,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        }
      },
      "policy_kind": "candidate",
      "policy_name": "candidate_policy_at_200",
      "raw_event_reward_count": 2,
      "raw_event_reward_total": -44.0,
      "raw_lifecycle_terminal_event_count": 3,
      "raw_reward_event_count": 2,
      "raw_reward_event_recovery_blocked": false,
      "raw_reward_total": -44.0,
      "raw_terminal_event_count": 3,
      "raw_vs_canonical_reward_reconciliation": {
        "canonical_task_count": 3,
        "canonical_task_reward_count": 2,
        "canonical_task_reward_total": -44.0,
        "canonical_terminal_task_count": 2,
        "checkpoint_budget": 200,
        "duplicate_reward_event_count": 0,
        "duplicate_terminal_event_count": 1,
        "raw_event_reward_count": 2,
        "raw_event_reward_total": -44.0,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 3,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_reconciled": true,
        "terminal_event_recovery_blocked": false
      },
      "reconciliation": {
        "canonical_reward_decomposition": {
          "canonical_task_mean_reward_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -22.0
          },
          "canonical_task_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 2
          },
          "canonical_task_reward_total_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "completion_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 1
          },
          "drop_penalty_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 1
          },
          "nan_reward_count": 0,
          "raw_event_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 2
          },
          "raw_event_reward_total_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "raw_vs_canonical_reward_delta_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": 0.0
          },
          "raw_vs_canonical_reward_delta_total": 0.0,
          "reward_available_count": 2,
          "reward_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "reward_by_action_and_terminal_outcome": {
            "horizontal": {
              "completed": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              },
              "dropped": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              }
            },
            "local": {
              "completed": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              },
              "dropped": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              }
            },
            "vertical": {
              "completed": {
                "canonical_task_mean_reward": -4.0,
                "canonical_task_reward_count": 1,
                "canonical_task_reward_total": -4.0,
                "count": 1,
                "mean_reward": -4.0,
                "raw_event_reward_count": 1,
                "raw_event_reward_total": -4.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": -4.0
              },
              "dropped": {
                "canonical_task_mean_reward": -40.0,
                "canonical_task_reward_count": 1,
                "canonical_task_reward_total": -40.0,
                "count": 1,
                "mean_reward": -40.0,
                "raw_event_reward_count": 1,
                "raw_event_reward_total": -40.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": -40.0
              }
            }
          },
          "reward_by_terminal_outcome": {
            "completed": -4.0,
            "dropped": -40.0
          },
          "zero_reward_count": 0
        },
        "canonical_task_outcome_sample": [
          {
            "arrival_slot": 0,
            "canonical_join_key": "trace-1:0:1",
            "canonical_reward": -40.0,
            "canonical_terminal_outcome": "dropped",
            "completion_or_drop_slot": 3,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "episode_id": 0,
            "first_decision_slot": 0,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -40.0,
            "raw_terminal_event_count": 2,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 1,
            "terminal_slot": 3,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 1,
            "canonical_join_key": "trace-1:0:2",
            "canonical_reward": -4.0,
            "canonical_terminal_outcome": "completed",
            "completion_or_drop_slot": 4,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 1,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -4.0,
            "raw_terminal_event_count": 1,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 2,
            "terminal_slot": 4,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 2,
            "canonical_join_key": "trace-1:0:3",
            "canonical_reward": 0.0,
            "canonical_terminal_outcome": "pending_at_horizon",
            "completion_or_drop_slot": null,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 2,
            "latency_slots": null,
            "raw_reward_event_count": 0,
            "raw_reward_total": 0.0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "horizontal",
            "task_id": 3,
            "terminal_slot": 5,
            "trace_id": "trace-1"
          }
        ],
        "canonical_task_outcome_summary": {
          "by_action": {
            "horizontal": {
              "canonical_completion_ratio": 0.0,
              "canonical_deadline_violation_ratio": 0.0,
              "canonical_drop_ratio": 0.0,
              "canonical_pending_ratio": 1.0,
              "canonical_reward_count": 0,
              "canonical_reward_total": 0.0,
              "canonical_task_count": 1,
              "canonical_task_mean_reward": 0.0,
              "canonical_terminal_task_count": 0,
              "completed_count": 0,
              "completion_reward_count": 0,
              "decision_count": 1,
              "double_count_detected": false,
              "drop_penalty_count": 0,
              "dropped_count": 0,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 0,
              "mean_completion_latency_slots": null,
              "mean_drop_latency_slots": null,
              "mean_reward": 0.0,
              "mean_terminal_latency_slots": null,
              "pending_at_horizon_count": 1,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_reward_emission_count": 0,
              "raw_terminal_event_count": 0,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 0,
              "terminal_transition_count": 0,
              "total_reward": 0.0,
              "unknown_count": 0
            },
            "local": {
              "canonical_completion_ratio": 0.0,
              "canonical_deadline_violation_ratio": 0.0,
              "canonical_drop_ratio": 0.0,
              "canonical_pending_ratio": 0.0,
              "canonical_reward_count": 0,
              "canonical_reward_total": 0.0,
              "canonical_task_count": 0,
              "canonical_task_mean_reward": 0.0,
              "canonical_terminal_task_count": 0,
              "completed_count": 0,
              "completion_reward_count": 0,
              "decision_count": 0,
              "double_count_detected": false,
              "drop_penalty_count": 0,
              "dropped_count": 0,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 0,
              "mean_completion_latency_slots": null,
              "mean_drop_latency_slots": null,
              "mean_reward": 0.0,
              "mean_terminal_latency_slots": null,
              "pending_at_horizon_count": 0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_reward_emission_count": 0,
              "raw_terminal_event_count": 0,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 0,
              "terminal_transition_count": 0,
              "total_reward": 0.0,
              "unknown_count": 0
            },
            "vertical": {
              "canonical_completion_ratio": 0.5,
              "canonical_deadline_violation_ratio": 0.5,
              "canonical_drop_ratio": 0.5,
              "canonical_pending_ratio": 0.0,
              "canonical_reward_count": 2,
              "canonical_reward_total": -44.0,
              "canonical_task_count": 2,
              "canonical_task_mean_reward": -22.0,
              "canonical_terminal_task_count": 2,
              "completed_count": 1,
              "completion_reward_count": 1,
              "decision_count": 2,
              "double_count_detected": true,
              "drop_penalty_count": 1,
              "dropped_count": 1,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 1,
              "mean_completion_latency_slots": 4.0,
              "mean_drop_latency_slots": 4.0,
              "mean_reward": -22.0,
              "mean_terminal_latency_slots": 4.0,
              "pending_at_horizon_count": 0,
              "raw_event_reward_count": 2,
              "raw_event_reward_total": -44.0,
              "raw_reward_emission_count": 2,
              "raw_terminal_event_count": 3,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 2,
              "terminal_transition_count": 2,
              "total_reward": -44.0,
              "unknown_count": 0
            }
          },
          "checkpoint_budget": 200,
          "overall": {
            "canonical_completion_count": 1,
            "canonical_completion_ratio": 0.3333333333333333,
            "canonical_deadline_violation_ratio": 0.3333333333333333,
            "canonical_drop_count": 1,
            "canonical_drop_ratio": 0.3333333333333333,
            "canonical_mean_completion_latency_slots": 4.0,
            "canonical_mean_drop_latency_slots": 4.0,
            "canonical_mean_terminal_latency_slots": 4.0,
            "canonical_pending_count": 1,
            "canonical_pending_ratio": 0.3333333333333333,
            "canonical_reward_count": 2,
            "canonical_reward_per_decision": -14.666666666666666,
            "canonical_reward_per_task": -14.666666666666666,
            "canonical_task_count": 3,
            "canonical_task_mean_reward": -22.0,
            "canonical_task_reward_count": 2,
            "canonical_task_reward_total": -44.0,
            "canonical_tasks_per_decision": 1.0,
            "canonical_terminal_task_count": 2,
            "canonical_unknown_count": 0,
            "completed_count": 1,
            "completion_reward_count": 1,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_reward": 0.0,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_reward_event_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          },
          "reward_coverage": {
            "raw_reward_event_count": 2,
            "raw_terminal_event_count": 3,
            "reward_available_count": 2
          }
        },
        "canonical_task_outcomes": [
          {
            "arrival_slot": 0,
            "canonical_join_key": "trace-1:0:1",
            "canonical_reward": -40.0,
            "canonical_terminal_outcome": "dropped",
            "completion_or_drop_slot": 3,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "episode_id": 0,
            "first_decision_slot": 0,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -40.0,
            "raw_terminal_event_count": 2,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 1,
            "terminal_slot": 3,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 1,
            "canonical_join_key": "trace-1:0:2",
            "canonical_reward": -4.0,
            "canonical_terminal_outcome": "completed",
            "completion_or_drop_slot": 4,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 1,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -4.0,
            "raw_terminal_event_count": 1,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 2,
            "terminal_slot": 4,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 2,
            "canonical_join_key": "trace-1:0:3",
            "canonical_reward": 0.0,
            "canonical_terminal_outcome": "pending_at_horizon",
            "completion_or_drop_slot": null,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 2,
            "latency_slots": null,
            "raw_reward_event_count": 0,
            "raw_reward_total": 0.0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "horizontal",
            "task_id": 3,
            "terminal_slot": 5,
            "trace_id": "trace-1"
          }
        ],
        "checkpoint_budget": 200,
        "decision_count": 3,
        "paper_aligned_diagnostic_metrics": {
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_tasks_per_decision": 1.0,
          "raw_reward_event_coverage_ratio": 1.0,
          "reward_reconciliation_status": "passed",
          "terminal_event_coverage_ratio": 1.5,
          "training_budget": 200
        },
        "raw_vs_canonical_reward_reconciliation": {
          "canonical_task_count": 3,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_terminal_task_count": 2,
          "checkpoint_budget": 200,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_event_recovery_blocked": false,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_reconciled": true,
          "terminal_event_recovery_blocked": false
        }
      },
      "reward_decomposition": {
        "canonical_task_mean_reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -22.0
        },
        "canonical_task_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "canonical_task_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "completion_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "drop_penalty_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "nan_reward_count": 0,
        "raw_event_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "raw_event_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "raw_vs_canonical_reward_delta_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": 0.0
        },
        "raw_vs_canonical_reward_delta_total": 0.0,
        "reward_available_count": 2,
        "reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "reward_by_action_and_terminal_outcome": {
          "horizontal": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "local": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "vertical": {
            "completed": {
              "canonical_task_mean_reward": -4.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -4.0,
              "count": 1,
              "mean_reward": -4.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -4.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -4.0
            },
            "dropped": {
              "canonical_task_mean_reward": -40.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -40.0,
              "count": 1,
              "mean_reward": -40.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -40.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -40.0
            }
          }
        },
        "reward_by_terminal_outcome": {
          "completed": -4.0,
          "dropped": -40.0
        },
        "zero_reward_count": 0
      },
      "reward_event_records": {
        "raw_reward_event_recovery_blocked": false,
        "record_count": 2,
        "reward_available_count": 2,
        "sample_records": [
          {
            "episode_id": 0,
            "raw_reward": -40.0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "reward_reconciled": true,
      "reward_reconciliation_status": "passed",
      "reward_reconciliation_tolerance": 1e-09,
      "same_evaluation_trace_bank": true,
      "terminal_event_records": {
        "record_count": 3,
        "recovered_from_finalized_tasks": true,
        "sample_records": [
          {
            "episode_id": 0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "terminal_event_recovery_blocked": false,
      "unknown_count": 0
    },
    "candidate_policy_at_500": {
      "action_distribution": {
        "horizontal": 1,
        "local": 1,
        "vertical": 1
      },
      "candidate_policy_vertical_share": 0.3333333333333333,
      "canonical_reward_decomposition": {
        "canonical_task_mean_reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -22.0
        },
        "canonical_task_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "canonical_task_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "completion_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "drop_penalty_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "nan_reward_count": 0,
        "raw_event_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "raw_event_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "raw_vs_canonical_reward_delta_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": 0.0
        },
        "raw_vs_canonical_reward_delta_total": 0.0,
        "reward_available_count": 2,
        "reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "reward_by_action_and_terminal_outcome": {
          "horizontal": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "local": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "vertical": {
            "completed": {
              "canonical_task_mean_reward": -4.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -4.0,
              "count": 1,
              "mean_reward": -4.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -4.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -4.0
            },
            "dropped": {
              "canonical_task_mean_reward": -40.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -40.0,
              "count": 1,
              "mean_reward": -40.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -40.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -40.0
            }
          }
        },
        "reward_by_terminal_outcome": {
          "completed": -4.0,
          "dropped": -40.0
        },
        "zero_reward_count": 0
      },
      "canonical_task_outcome_summary": {
        "by_action": {
          "horizontal": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 1.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 1,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 1,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "local": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 0,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 0,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "vertical": {
            "canonical_completion_ratio": 0.5,
            "canonical_deadline_violation_ratio": 0.5,
            "canonical_drop_ratio": 0.5,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 2,
            "canonical_reward_total": -44.0,
            "canonical_task_count": 2,
            "canonical_task_mean_reward": -22.0,
            "canonical_terminal_task_count": 2,
            "completed_count": 1,
            "completion_reward_count": 1,
            "decision_count": 2,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_completion_latency_slots": 4.0,
            "mean_drop_latency_slots": 4.0,
            "mean_reward": -22.0,
            "mean_terminal_latency_slots": 4.0,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          }
        },
        "checkpoint_budget": 500,
        "overall": {
          "canonical_completion_count": 1,
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_count": 1,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 1,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_count": 2,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_task_count": 3,
          "canonical_task_mean_reward": -22.0,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 2,
          "canonical_unknown_count": 0,
          "completed_count": 1,
          "completion_reward_count": 1,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_reward": 0.0,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        },
        "reward_coverage": {
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "reward_available_count": 2
        }
      },
      "canonical_task_reconciliation": {
        "by_action": {
          "horizontal": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 1.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 1,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 1,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "local": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 0,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 0,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "vertical": {
            "canonical_completion_ratio": 0.5,
            "canonical_deadline_violation_ratio": 0.5,
            "canonical_drop_ratio": 0.5,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 2,
            "canonical_reward_total": -44.0,
            "canonical_task_count": 2,
            "canonical_task_mean_reward": -22.0,
            "canonical_terminal_task_count": 2,
            "completed_count": 1,
            "completion_reward_count": 1,
            "decision_count": 2,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_completion_latency_slots": 4.0,
            "mean_drop_latency_slots": 4.0,
            "mean_reward": -22.0,
            "mean_terminal_latency_slots": 4.0,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          }
        },
        "checkpoint_budget": 500,
        "overall": {
          "canonical_completion_count": 1,
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_count": 1,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 1,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_count": 2,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_task_count": 3,
          "canonical_task_mean_reward": -22.0,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 2,
          "canonical_unknown_count": 0,
          "completed_count": 1,
          "completion_reward_count": 1,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_reward": 0.0,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        },
        "reward_coverage": {
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "reward_available_count": 2
        }
      },
      "canonical_task_reward_count": 2,
      "canonical_task_reward_total": -44.0,
      "checkpoint_budget": 500,
      "completed_count": 1,
      "completed_task_count": 1,
      "completion_ratio": 0.3333333333333333,
      "deadline_violation_ratio": 0.3333333333333333,
      "decision_records_summary": {
        "decision_count": 3,
        "evaluation_action_distribution_source": "evaluation_episodes",
        "sample_records": [
          {
            "episode_id": 0,
            "selected_action": "vertical",
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "drop_ratio": 0.3333333333333333,
      "dropped_count": 1,
      "dropped_task_count": 1,
      "episode_length": 110,
      "episode_reward_totals": [
        -44.0
      ],
      "episode_summaries": [
        {
          "canonical_reward_total": -44.0,
          "completion_count": 1,
          "decision_count": 3,
          "drop_count": 1,
          "episode_id": 0,
          "pending_count": 1,
          "raw_reward_event_count": 2,
          "raw_reward_total": -44.0,
          "reward_recovered": true,
          "terminal_task_count": 2,
          "trace_id": "trace-0",
          "unknown_count": 0
        }
      ],
      "evaluation_action_by_episode_id": {
        "0": {
          "decision_count": 3
        }
      },
      "evaluation_action_by_trace_id": {
        "trace-0": {
          "decision_count": 3
        }
      },
      "evaluation_action_distribution": {
        "horizontal": 1,
        "local": 1,
        "vertical": 1
      },
      "evaluation_action_distribution_source": "evaluation_episodes",
      "evaluation_action_sequence_sample": [
        {
          "episode_id": 0,
          "selected_action": "vertical",
          "task_id": 1,
          "trace_id": "trace-0"
        }
      ],
      "evaluation_decision_count": 3,
      "evaluation_episode_count": 100,
      "evaluation_legal_action_mask_distribution": {
        "local=1|horizontal=1|vertical=1": 3
      },
      "evaluation_reward_summary": {
        "candidate_reproduction_supported": true,
        "canonical_task_count": 3,
        "canonical_task_reward_count": 2,
        "canonical_task_reward_total": -44.0,
        "completed_task_count": 1,
        "dropped_task_count": 1,
        "evaluation_episode_count": 100,
        "evaluation_on_training_traces": false,
        "mean_reward": -44.0,
        "pending_at_horizon_count": 1,
        "raw_event_reward_count": 2,
        "raw_event_reward_total": -44.0,
        "raw_reward_emission_count": 2,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 3,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_available_count": 2,
        "reward_bearing_transition_count": 2,
        "same_evaluation_trace_bank": true,
        "terminal_event_recovery_blocked": false,
        "terminal_transition_count": 2,
        "trace_bank_disjoint": true,
        "trace_bank_ids": {
          "evaluation": "eval-bank",
          "training": "train-bank"
        },
        "trace_ids": [
          "trace-0"
        ],
        "unknown_task_count": 0
      },
      "evaluation_trace_bank_id": "eval-bank",
      "mean_latency_slots": 4.0,
      "paper_aligned_diagnostic_metrics": {
        "canonical_completion_ratio": 0.3333333333333333,
        "canonical_deadline_violation_ratio": 0.3333333333333333,
        "canonical_drop_ratio": 0.3333333333333333,
        "canonical_mean_completion_latency_slots": 4.0,
        "canonical_mean_drop_latency_slots": 4.0,
        "canonical_mean_terminal_latency_slots": 4.0,
        "canonical_pending_ratio": 0.3333333333333333,
        "canonical_reward_per_decision": -14.666666666666666,
        "canonical_reward_per_task": -14.666666666666666,
        "canonical_tasks_per_decision": 1.0,
        "raw_reward_event_coverage_ratio": 1.0,
        "reward_reconciliation_status": "passed",
        "terminal_event_coverage_ratio": 1.5,
        "training_budget": 500
      },
      "pending_at_horizon_count": 1,
      "pending_task_count": 1,
      "per_action_outcome_summary": {
        "horizontal": {
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 0.0,
          "canonical_drop_ratio": 0.0,
          "canonical_pending_ratio": 1.0,
          "canonical_reward_count": 0,
          "canonical_reward_total": 0.0,
          "canonical_task_count": 1,
          "canonical_task_mean_reward": 0.0,
          "canonical_terminal_task_count": 0,
          "completed_count": 0,
          "completion_reward_count": 0,
          "decision_count": 1,
          "double_count_detected": false,
          "drop_penalty_count": 0,
          "dropped_count": 0,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "mean_completion_latency_slots": null,
          "mean_drop_latency_slots": null,
          "mean_reward": 0.0,
          "mean_terminal_latency_slots": null,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 0,
          "raw_event_reward_total": 0.0,
          "raw_reward_emission_count": 0,
          "raw_terminal_event_count": 0,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 0,
          "terminal_transition_count": 0,
          "total_reward": 0.0,
          "unknown_count": 0
        },
        "local": {
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 0.0,
          "canonical_drop_ratio": 0.0,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_count": 0,
          "canonical_reward_total": 0.0,
          "canonical_task_count": 0,
          "canonical_task_mean_reward": 0.0,
          "canonical_terminal_task_count": 0,
          "completed_count": 0,
          "completion_reward_count": 0,
          "decision_count": 0,
          "double_count_detected": false,
          "drop_penalty_count": 0,
          "dropped_count": 0,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "mean_completion_latency_slots": null,
          "mean_drop_latency_slots": null,
          "mean_reward": 0.0,
          "mean_terminal_latency_slots": null,
          "pending_at_horizon_count": 0,
          "raw_event_reward_count": 0,
          "raw_event_reward_total": 0.0,
          "raw_reward_emission_count": 0,
          "raw_terminal_event_count": 0,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 0,
          "terminal_transition_count": 0,
          "total_reward": 0.0,
          "unknown_count": 0
        },
        "vertical": {
          "canonical_completion_ratio": 0.5,
          "canonical_deadline_violation_ratio": 0.5,
          "canonical_drop_ratio": 0.5,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_count": 2,
          "canonical_reward_total": -44.0,
          "canonical_task_count": 2,
          "canonical_task_mean_reward": -22.0,
          "canonical_terminal_task_count": 2,
          "completed_count": 1,
          "completion_reward_count": 1,
          "decision_count": 2,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_completion_latency_slots": 4.0,
          "mean_drop_latency_slots": 4.0,
          "mean_reward": -22.0,
          "mean_terminal_latency_slots": 4.0,
          "pending_at_horizon_count": 0,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        }
      },
      "policy_kind": "candidate",
      "policy_name": "candidate_policy_at_500",
      "raw_event_reward_count": 2,
      "raw_event_reward_total": -44.0,
      "raw_lifecycle_terminal_event_count": 3,
      "raw_reward_event_count": 2,
      "raw_reward_event_recovery_blocked": false,
      "raw_reward_total": -44.0,
      "raw_terminal_event_count": 3,
      "raw_vs_canonical_reward_reconciliation": {
        "canonical_task_count": 3,
        "canonical_task_reward_count": 2,
        "canonical_task_reward_total": -44.0,
        "canonical_terminal_task_count": 2,
        "checkpoint_budget": 500,
        "duplicate_reward_event_count": 0,
        "duplicate_terminal_event_count": 1,
        "raw_event_reward_count": 2,
        "raw_event_reward_total": -44.0,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 3,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_reconciled": true,
        "terminal_event_recovery_blocked": false
      },
      "reconciliation": {
        "canonical_reward_decomposition": {
          "canonical_task_mean_reward_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -22.0
          },
          "canonical_task_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 2
          },
          "canonical_task_reward_total_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "completion_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 1
          },
          "drop_penalty_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 1
          },
          "nan_reward_count": 0,
          "raw_event_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 2
          },
          "raw_event_reward_total_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "raw_vs_canonical_reward_delta_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": 0.0
          },
          "raw_vs_canonical_reward_delta_total": 0.0,
          "reward_available_count": 2,
          "reward_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "reward_by_action_and_terminal_outcome": {
            "horizontal": {
              "completed": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              },
              "dropped": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              }
            },
            "local": {
              "completed": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              },
              "dropped": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              }
            },
            "vertical": {
              "completed": {
                "canonical_task_mean_reward": -4.0,
                "canonical_task_reward_count": 1,
                "canonical_task_reward_total": -4.0,
                "count": 1,
                "mean_reward": -4.0,
                "raw_event_reward_count": 1,
                "raw_event_reward_total": -4.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": -4.0
              },
              "dropped": {
                "canonical_task_mean_reward": -40.0,
                "canonical_task_reward_count": 1,
                "canonical_task_reward_total": -40.0,
                "count": 1,
                "mean_reward": -40.0,
                "raw_event_reward_count": 1,
                "raw_event_reward_total": -40.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": -40.0
              }
            }
          },
          "reward_by_terminal_outcome": {
            "completed": -4.0,
            "dropped": -40.0
          },
          "zero_reward_count": 0
        },
        "canonical_task_outcome_sample": [
          {
            "arrival_slot": 0,
            "canonical_join_key": "trace-1:0:1",
            "canonical_reward": -40.0,
            "canonical_terminal_outcome": "dropped",
            "completion_or_drop_slot": 3,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "episode_id": 0,
            "first_decision_slot": 0,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -40.0,
            "raw_terminal_event_count": 2,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 1,
            "terminal_slot": 3,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 1,
            "canonical_join_key": "trace-1:0:2",
            "canonical_reward": -4.0,
            "canonical_terminal_outcome": "completed",
            "completion_or_drop_slot": 4,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 1,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -4.0,
            "raw_terminal_event_count": 1,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 2,
            "terminal_slot": 4,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 2,
            "canonical_join_key": "trace-1:0:3",
            "canonical_reward": 0.0,
            "canonical_terminal_outcome": "pending_at_horizon",
            "completion_or_drop_slot": null,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 2,
            "latency_slots": null,
            "raw_reward_event_count": 0,
            "raw_reward_total": 0.0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "horizontal",
            "task_id": 3,
            "terminal_slot": 5,
            "trace_id": "trace-1"
          }
        ],
        "canonical_task_outcome_summary": {
          "by_action": {
            "horizontal": {
              "canonical_completion_ratio": 0.0,
              "canonical_deadline_violation_ratio": 0.0,
              "canonical_drop_ratio": 0.0,
              "canonical_pending_ratio": 1.0,
              "canonical_reward_count": 0,
              "canonical_reward_total": 0.0,
              "canonical_task_count": 1,
              "canonical_task_mean_reward": 0.0,
              "canonical_terminal_task_count": 0,
              "completed_count": 0,
              "completion_reward_count": 0,
              "decision_count": 1,
              "double_count_detected": false,
              "drop_penalty_count": 0,
              "dropped_count": 0,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 0,
              "mean_completion_latency_slots": null,
              "mean_drop_latency_slots": null,
              "mean_reward": 0.0,
              "mean_terminal_latency_slots": null,
              "pending_at_horizon_count": 1,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_reward_emission_count": 0,
              "raw_terminal_event_count": 0,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 0,
              "terminal_transition_count": 0,
              "total_reward": 0.0,
              "unknown_count": 0
            },
            "local": {
              "canonical_completion_ratio": 0.0,
              "canonical_deadline_violation_ratio": 0.0,
              "canonical_drop_ratio": 0.0,
              "canonical_pending_ratio": 0.0,
              "canonical_reward_count": 0,
              "canonical_reward_total": 0.0,
              "canonical_task_count": 0,
              "canonical_task_mean_reward": 0.0,
              "canonical_terminal_task_count": 0,
              "completed_count": 0,
              "completion_reward_count": 0,
              "decision_count": 0,
              "double_count_detected": false,
              "drop_penalty_count": 0,
              "dropped_count": 0,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 0,
              "mean_completion_latency_slots": null,
              "mean_drop_latency_slots": null,
              "mean_reward": 0.0,
              "mean_terminal_latency_slots": null,
              "pending_at_horizon_count": 0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_reward_emission_count": 0,
              "raw_terminal_event_count": 0,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 0,
              "terminal_transition_count": 0,
              "total_reward": 0.0,
              "unknown_count": 0
            },
            "vertical": {
              "canonical_completion_ratio": 0.5,
              "canonical_deadline_violation_ratio": 0.5,
              "canonical_drop_ratio": 0.5,
              "canonical_pending_ratio": 0.0,
              "canonical_reward_count": 2,
              "canonical_reward_total": -44.0,
              "canonical_task_count": 2,
              "canonical_task_mean_reward": -22.0,
              "canonical_terminal_task_count": 2,
              "completed_count": 1,
              "completion_reward_count": 1,
              "decision_count": 2,
              "double_count_detected": true,
              "drop_penalty_count": 1,
              "dropped_count": 1,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 1,
              "mean_completion_latency_slots": 4.0,
              "mean_drop_latency_slots": 4.0,
              "mean_reward": -22.0,
              "mean_terminal_latency_slots": 4.0,
              "pending_at_horizon_count": 0,
              "raw_event_reward_count": 2,
              "raw_event_reward_total": -44.0,
              "raw_reward_emission_count": 2,
              "raw_terminal_event_count": 3,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 2,
              "terminal_transition_count": 2,
              "total_reward": -44.0,
              "unknown_count": 0
            }
          },
          "checkpoint_budget": 500,
          "overall": {
            "canonical_completion_count": 1,
            "canonical_completion_ratio": 0.3333333333333333,
            "canonical_deadline_violation_ratio": 0.3333333333333333,
            "canonical_drop_count": 1,
            "canonical_drop_ratio": 0.3333333333333333,
            "canonical_mean_completion_latency_slots": 4.0,
            "canonical_mean_drop_latency_slots": 4.0,
            "canonical_mean_terminal_latency_slots": 4.0,
            "canonical_pending_count": 1,
            "canonical_pending_ratio": 0.3333333333333333,
            "canonical_reward_count": 2,
            "canonical_reward_per_decision": -14.666666666666666,
            "canonical_reward_per_task": -14.666666666666666,
            "canonical_task_count": 3,
            "canonical_task_mean_reward": -22.0,
            "canonical_task_reward_count": 2,
            "canonical_task_reward_total": -44.0,
            "canonical_tasks_per_decision": 1.0,
            "canonical_terminal_task_count": 2,
            "canonical_unknown_count": 0,
            "completed_count": 1,
            "completion_reward_count": 1,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_reward": 0.0,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_reward_event_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          },
          "reward_coverage": {
            "raw_reward_event_count": 2,
            "raw_terminal_event_count": 3,
            "reward_available_count": 2
          }
        },
        "canonical_task_outcomes": [
          {
            "arrival_slot": 0,
            "canonical_join_key": "trace-1:0:1",
            "canonical_reward": -40.0,
            "canonical_terminal_outcome": "dropped",
            "completion_or_drop_slot": 3,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "episode_id": 0,
            "first_decision_slot": 0,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -40.0,
            "raw_terminal_event_count": 2,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 1,
            "terminal_slot": 3,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 1,
            "canonical_join_key": "trace-1:0:2",
            "canonical_reward": -4.0,
            "canonical_terminal_outcome": "completed",
            "completion_or_drop_slot": 4,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 1,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -4.0,
            "raw_terminal_event_count": 1,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 2,
            "terminal_slot": 4,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 2,
            "canonical_join_key": "trace-1:0:3",
            "canonical_reward": 0.0,
            "canonical_terminal_outcome": "pending_at_horizon",
            "completion_or_drop_slot": null,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 2,
            "latency_slots": null,
            "raw_reward_event_count": 0,
            "raw_reward_total": 0.0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "horizontal",
            "task_id": 3,
            "terminal_slot": 5,
            "trace_id": "trace-1"
          }
        ],
        "checkpoint_budget": 500,
        "decision_count": 3,
        "paper_aligned_diagnostic_metrics": {
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_tasks_per_decision": 1.0,
          "raw_reward_event_coverage_ratio": 1.0,
          "reward_reconciliation_status": "passed",
          "terminal_event_coverage_ratio": 1.5,
          "training_budget": 500
        },
        "raw_vs_canonical_reward_reconciliation": {
          "canonical_task_count": 3,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_terminal_task_count": 2,
          "checkpoint_budget": 500,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_event_recovery_blocked": false,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_reconciled": true,
          "terminal_event_recovery_blocked": false
        }
      },
      "reward_decomposition": {
        "canonical_task_mean_reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -22.0
        },
        "canonical_task_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "canonical_task_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "completion_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "drop_penalty_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "nan_reward_count": 0,
        "raw_event_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "raw_event_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "raw_vs_canonical_reward_delta_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": 0.0
        },
        "raw_vs_canonical_reward_delta_total": 0.0,
        "reward_available_count": 2,
        "reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "reward_by_action_and_terminal_outcome": {
          "horizontal": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "local": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "vertical": {
            "completed": {
              "canonical_task_mean_reward": -4.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -4.0,
              "count": 1,
              "mean_reward": -4.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -4.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -4.0
            },
            "dropped": {
              "canonical_task_mean_reward": -40.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -40.0,
              "count": 1,
              "mean_reward": -40.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -40.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -40.0
            }
          }
        },
        "reward_by_terminal_outcome": {
          "completed": -4.0,
          "dropped": -40.0
        },
        "zero_reward_count": 0
      },
      "reward_event_records": {
        "raw_reward_event_recovery_blocked": false,
        "record_count": 2,
        "reward_available_count": 2,
        "sample_records": [
          {
            "episode_id": 0,
            "raw_reward": -40.0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "reward_reconciled": true,
      "reward_reconciliation_status": "passed",
      "reward_reconciliation_tolerance": 1e-09,
      "same_evaluation_trace_bank": true,
      "terminal_event_records": {
        "record_count": 3,
        "recovered_from_finalized_tasks": true,
        "sample_records": [
          {
            "episode_id": 0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "terminal_event_recovery_blocked": false,
      "unknown_count": 0
    },
    "fixed_horizontal_policy": {
      "action_distribution": {
        "horizontal": 1,
        "local": 1,
        "vertical": 1
      },
      "candidate_policy_vertical_share": 0.3333333333333333,
      "canonical_reward_decomposition": {
        "canonical_task_mean_reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -22.0
        },
        "canonical_task_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "canonical_task_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "completion_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "drop_penalty_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "nan_reward_count": 0,
        "raw_event_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "raw_event_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "raw_vs_canonical_reward_delta_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": 0.0
        },
        "raw_vs_canonical_reward_delta_total": 0.0,
        "reward_available_count": 2,
        "reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "reward_by_action_and_terminal_outcome": {
          "horizontal": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "local": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "vertical": {
            "completed": {
              "canonical_task_mean_reward": -4.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -4.0,
              "count": 1,
              "mean_reward": -4.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -4.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -4.0
            },
            "dropped": {
              "canonical_task_mean_reward": -40.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -40.0,
              "count": 1,
              "mean_reward": -40.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -40.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -40.0
            }
          }
        },
        "reward_by_terminal_outcome": {
          "completed": -4.0,
          "dropped": -40.0
        },
        "zero_reward_count": 0
      },
      "canonical_task_outcome_summary": {
        "by_action": {
          "horizontal": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 1.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 1,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 1,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "local": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 0,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 0,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "vertical": {
            "canonical_completion_ratio": 0.5,
            "canonical_deadline_violation_ratio": 0.5,
            "canonical_drop_ratio": 0.5,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 2,
            "canonical_reward_total": -44.0,
            "canonical_task_count": 2,
            "canonical_task_mean_reward": -22.0,
            "canonical_terminal_task_count": 2,
            "completed_count": 1,
            "completion_reward_count": 1,
            "decision_count": 2,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_completion_latency_slots": 4.0,
            "mean_drop_latency_slots": 4.0,
            "mean_reward": -22.0,
            "mean_terminal_latency_slots": 4.0,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          }
        },
        "checkpoint_budget": 100,
        "overall": {
          "canonical_completion_count": 1,
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_count": 1,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 1,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_count": 2,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_task_count": 3,
          "canonical_task_mean_reward": -22.0,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 2,
          "canonical_unknown_count": 0,
          "completed_count": 1,
          "completion_reward_count": 1,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_reward": 0.0,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        },
        "reward_coverage": {
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "reward_available_count": 2
        }
      },
      "canonical_task_reconciliation": {
        "by_action": {
          "horizontal": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 1.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 1,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 1,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "local": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 0,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 0,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "vertical": {
            "canonical_completion_ratio": 0.5,
            "canonical_deadline_violation_ratio": 0.5,
            "canonical_drop_ratio": 0.5,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 2,
            "canonical_reward_total": -44.0,
            "canonical_task_count": 2,
            "canonical_task_mean_reward": -22.0,
            "canonical_terminal_task_count": 2,
            "completed_count": 1,
            "completion_reward_count": 1,
            "decision_count": 2,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_completion_latency_slots": 4.0,
            "mean_drop_latency_slots": 4.0,
            "mean_reward": -22.0,
            "mean_terminal_latency_slots": 4.0,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          }
        },
        "checkpoint_budget": 100,
        "overall": {
          "canonical_completion_count": 1,
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_count": 1,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 1,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_count": 2,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_task_count": 3,
          "canonical_task_mean_reward": -22.0,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 2,
          "canonical_unknown_count": 0,
          "completed_count": 1,
          "completion_reward_count": 1,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_reward": 0.0,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        },
        "reward_coverage": {
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "reward_available_count": 2
        }
      },
      "canonical_task_reward_count": 2,
      "canonical_task_reward_total": -44.0,
      "checkpoint_budget": 100,
      "completed_count": 1,
      "completed_task_count": 1,
      "completion_ratio": 0.3333333333333333,
      "deadline_violation_ratio": 0.3333333333333333,
      "decision_records_summary": {
        "decision_count": 3,
        "evaluation_action_distribution_source": "evaluation_episodes",
        "sample_records": [
          {
            "episode_id": 0,
            "selected_action": "vertical",
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "drop_ratio": 0.3333333333333333,
      "dropped_count": 1,
      "dropped_task_count": 1,
      "episode_length": 110,
      "episode_reward_totals": [
        -44.0
      ],
      "episode_summaries": [
        {
          "canonical_reward_total": -44.0,
          "completion_count": 1,
          "decision_count": 3,
          "drop_count": 1,
          "episode_id": 0,
          "pending_count": 1,
          "raw_reward_event_count": 2,
          "raw_reward_total": -44.0,
          "reward_recovered": true,
          "terminal_task_count": 2,
          "trace_id": "trace-0",
          "unknown_count": 0
        }
      ],
      "evaluation_action_by_episode_id": {
        "0": {
          "decision_count": 3
        }
      },
      "evaluation_action_by_trace_id": {
        "trace-0": {
          "decision_count": 3
        }
      },
      "evaluation_action_distribution": {
        "horizontal": 1,
        "local": 1,
        "vertical": 1
      },
      "evaluation_action_distribution_source": "evaluation_episodes",
      "evaluation_action_sequence_sample": [
        {
          "episode_id": 0,
          "selected_action": "vertical",
          "task_id": 1,
          "trace_id": "trace-0"
        }
      ],
      "evaluation_decision_count": 3,
      "evaluation_episode_count": 100,
      "evaluation_legal_action_mask_distribution": {
        "local=1|horizontal=1|vertical=1": 3
      },
      "evaluation_reward_summary": {
        "candidate_reproduction_supported": true,
        "canonical_task_count": 3,
        "canonical_task_reward_count": 2,
        "canonical_task_reward_total": -44.0,
        "completed_task_count": 1,
        "dropped_task_count": 1,
        "evaluation_episode_count": 100,
        "evaluation_on_training_traces": false,
        "mean_reward": -44.0,
        "pending_at_horizon_count": 1,
        "raw_event_reward_count": 2,
        "raw_event_reward_total": -44.0,
        "raw_reward_emission_count": 2,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 3,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_available_count": 2,
        "reward_bearing_transition_count": 2,
        "same_evaluation_trace_bank": true,
        "terminal_event_recovery_blocked": false,
        "terminal_transition_count": 2,
        "trace_bank_disjoint": true,
        "trace_bank_ids": {
          "evaluation": "eval-bank",
          "training": "train-bank"
        },
        "trace_ids": [
          "trace-0"
        ],
        "unknown_task_count": 0
      },
      "evaluation_trace_bank_id": "eval-bank",
      "mean_latency_slots": 4.0,
      "paper_aligned_diagnostic_metrics": {
        "canonical_completion_ratio": 0.3333333333333333,
        "canonical_deadline_violation_ratio": 0.3333333333333333,
        "canonical_drop_ratio": 0.3333333333333333,
        "canonical_mean_completion_latency_slots": 4.0,
        "canonical_mean_drop_latency_slots": 4.0,
        "canonical_mean_terminal_latency_slots": 4.0,
        "canonical_pending_ratio": 0.3333333333333333,
        "canonical_reward_per_decision": -14.666666666666666,
        "canonical_reward_per_task": -14.666666666666666,
        "canonical_tasks_per_decision": 1.0,
        "raw_reward_event_coverage_ratio": 1.0,
        "reward_reconciliation_status": "passed",
        "terminal_event_coverage_ratio": 1.5,
        "training_budget": 100
      },
      "pending_at_horizon_count": 1,
      "pending_task_count": 1,
      "per_action_outcome_summary": {
        "horizontal": {
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 0.0,
          "canonical_drop_ratio": 0.0,
          "canonical_pending_ratio": 1.0,
          "canonical_reward_count": 0,
          "canonical_reward_total": 0.0,
          "canonical_task_count": 1,
          "canonical_task_mean_reward": 0.0,
          "canonical_terminal_task_count": 0,
          "completed_count": 0,
          "completion_reward_count": 0,
          "decision_count": 1,
          "double_count_detected": false,
          "drop_penalty_count": 0,
          "dropped_count": 0,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "mean_completion_latency_slots": null,
          "mean_drop_latency_slots": null,
          "mean_reward": 0.0,
          "mean_terminal_latency_slots": null,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 0,
          "raw_event_reward_total": 0.0,
          "raw_reward_emission_count": 0,
          "raw_terminal_event_count": 0,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 0,
          "terminal_transition_count": 0,
          "total_reward": 0.0,
          "unknown_count": 0
        },
        "local": {
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 0.0,
          "canonical_drop_ratio": 0.0,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_count": 0,
          "canonical_reward_total": 0.0,
          "canonical_task_count": 0,
          "canonical_task_mean_reward": 0.0,
          "canonical_terminal_task_count": 0,
          "completed_count": 0,
          "completion_reward_count": 0,
          "decision_count": 0,
          "double_count_detected": false,
          "drop_penalty_count": 0,
          "dropped_count": 0,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "mean_completion_latency_slots": null,
          "mean_drop_latency_slots": null,
          "mean_reward": 0.0,
          "mean_terminal_latency_slots": null,
          "pending_at_horizon_count": 0,
          "raw_event_reward_count": 0,
          "raw_event_reward_total": 0.0,
          "raw_reward_emission_count": 0,
          "raw_terminal_event_count": 0,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 0,
          "terminal_transition_count": 0,
          "total_reward": 0.0,
          "unknown_count": 0
        },
        "vertical": {
          "canonical_completion_ratio": 0.5,
          "canonical_deadline_violation_ratio": 0.5,
          "canonical_drop_ratio": 0.5,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_count": 2,
          "canonical_reward_total": -44.0,
          "canonical_task_count": 2,
          "canonical_task_mean_reward": -22.0,
          "canonical_terminal_task_count": 2,
          "completed_count": 1,
          "completion_reward_count": 1,
          "decision_count": 2,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_completion_latency_slots": 4.0,
          "mean_drop_latency_slots": 4.0,
          "mean_reward": -22.0,
          "mean_terminal_latency_slots": 4.0,
          "pending_at_horizon_count": 0,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        }
      },
      "policy_kind": "candidate",
      "policy_name": "candidate_policy_at_100",
      "raw_event_reward_count": 2,
      "raw_event_reward_total": -44.0,
      "raw_lifecycle_terminal_event_count": 3,
      "raw_reward_event_count": 2,
      "raw_reward_event_recovery_blocked": false,
      "raw_reward_total": -44.0,
      "raw_terminal_event_count": 3,
      "raw_vs_canonical_reward_reconciliation": {
        "canonical_task_count": 3,
        "canonical_task_reward_count": 2,
        "canonical_task_reward_total": -44.0,
        "canonical_terminal_task_count": 2,
        "checkpoint_budget": 100,
        "duplicate_reward_event_count": 0,
        "duplicate_terminal_event_count": 1,
        "raw_event_reward_count": 2,
        "raw_event_reward_total": -44.0,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 3,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_reconciled": true,
        "terminal_event_recovery_blocked": false
      },
      "reconciliation": {
        "canonical_reward_decomposition": {
          "canonical_task_mean_reward_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -22.0
          },
          "canonical_task_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 2
          },
          "canonical_task_reward_total_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "completion_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 1
          },
          "drop_penalty_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 1
          },
          "nan_reward_count": 0,
          "raw_event_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 2
          },
          "raw_event_reward_total_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "raw_vs_canonical_reward_delta_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": 0.0
          },
          "raw_vs_canonical_reward_delta_total": 0.0,
          "reward_available_count": 2,
          "reward_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "reward_by_action_and_terminal_outcome": {
            "horizontal": {
              "completed": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              },
              "dropped": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              }
            },
            "local": {
              "completed": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              },
              "dropped": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              }
            },
            "vertical": {
              "completed": {
                "canonical_task_mean_reward": -4.0,
                "canonical_task_reward_count": 1,
                "canonical_task_reward_total": -4.0,
                "count": 1,
                "mean_reward": -4.0,
                "raw_event_reward_count": 1,
                "raw_event_reward_total": -4.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": -4.0
              },
              "dropped": {
                "canonical_task_mean_reward": -40.0,
                "canonical_task_reward_count": 1,
                "canonical_task_reward_total": -40.0,
                "count": 1,
                "mean_reward": -40.0,
                "raw_event_reward_count": 1,
                "raw_event_reward_total": -40.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": -40.0
              }
            }
          },
          "reward_by_terminal_outcome": {
            "completed": -4.0,
            "dropped": -40.0
          },
          "zero_reward_count": 0
        },
        "canonical_task_outcome_sample": [
          {
            "arrival_slot": 0,
            "canonical_join_key": "trace-1:0:1",
            "canonical_reward": -40.0,
            "canonical_terminal_outcome": "dropped",
            "completion_or_drop_slot": 3,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "episode_id": 0,
            "first_decision_slot": 0,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -40.0,
            "raw_terminal_event_count": 2,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 1,
            "terminal_slot": 3,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 1,
            "canonical_join_key": "trace-1:0:2",
            "canonical_reward": -4.0,
            "canonical_terminal_outcome": "completed",
            "completion_or_drop_slot": 4,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 1,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -4.0,
            "raw_terminal_event_count": 1,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 2,
            "terminal_slot": 4,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 2,
            "canonical_join_key": "trace-1:0:3",
            "canonical_reward": 0.0,
            "canonical_terminal_outcome": "pending_at_horizon",
            "completion_or_drop_slot": null,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 2,
            "latency_slots": null,
            "raw_reward_event_count": 0,
            "raw_reward_total": 0.0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "horizontal",
            "task_id": 3,
            "terminal_slot": 5,
            "trace_id": "trace-1"
          }
        ],
        "canonical_task_outcome_summary": {
          "by_action": {
            "horizontal": {
              "canonical_completion_ratio": 0.0,
              "canonical_deadline_violation_ratio": 0.0,
              "canonical_drop_ratio": 0.0,
              "canonical_pending_ratio": 1.0,
              "canonical_reward_count": 0,
              "canonical_reward_total": 0.0,
              "canonical_task_count": 1,
              "canonical_task_mean_reward": 0.0,
              "canonical_terminal_task_count": 0,
              "completed_count": 0,
              "completion_reward_count": 0,
              "decision_count": 1,
              "double_count_detected": false,
              "drop_penalty_count": 0,
              "dropped_count": 0,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 0,
              "mean_completion_latency_slots": null,
              "mean_drop_latency_slots": null,
              "mean_reward": 0.0,
              "mean_terminal_latency_slots": null,
              "pending_at_horizon_count": 1,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_reward_emission_count": 0,
              "raw_terminal_event_count": 0,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 0,
              "terminal_transition_count": 0,
              "total_reward": 0.0,
              "unknown_count": 0
            },
            "local": {
              "canonical_completion_ratio": 0.0,
              "canonical_deadline_violation_ratio": 0.0,
              "canonical_drop_ratio": 0.0,
              "canonical_pending_ratio": 0.0,
              "canonical_reward_count": 0,
              "canonical_reward_total": 0.0,
              "canonical_task_count": 0,
              "canonical_task_mean_reward": 0.0,
              "canonical_terminal_task_count": 0,
              "completed_count": 0,
              "completion_reward_count": 0,
              "decision_count": 0,
              "double_count_detected": false,
              "drop_penalty_count": 0,
              "dropped_count": 0,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 0,
              "mean_completion_latency_slots": null,
              "mean_drop_latency_slots": null,
              "mean_reward": 0.0,
              "mean_terminal_latency_slots": null,
              "pending_at_horizon_count": 0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_reward_emission_count": 0,
              "raw_terminal_event_count": 0,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 0,
              "terminal_transition_count": 0,
              "total_reward": 0.0,
              "unknown_count": 0
            },
            "vertical": {
              "canonical_completion_ratio": 0.5,
              "canonical_deadline_violation_ratio": 0.5,
              "canonical_drop_ratio": 0.5,
              "canonical_pending_ratio": 0.0,
              "canonical_reward_count": 2,
              "canonical_reward_total": -44.0,
              "canonical_task_count": 2,
              "canonical_task_mean_reward": -22.0,
              "canonical_terminal_task_count": 2,
              "completed_count": 1,
              "completion_reward_count": 1,
              "decision_count": 2,
              "double_count_detected": true,
              "drop_penalty_count": 1,
              "dropped_count": 1,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 1,
              "mean_completion_latency_slots": 4.0,
              "mean_drop_latency_slots": 4.0,
              "mean_reward": -22.0,
              "mean_terminal_latency_slots": 4.0,
              "pending_at_horizon_count": 0,
              "raw_event_reward_count": 2,
              "raw_event_reward_total": -44.0,
              "raw_reward_emission_count": 2,
              "raw_terminal_event_count": 3,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 2,
              "terminal_transition_count": 2,
              "total_reward": -44.0,
              "unknown_count": 0
            }
          },
          "checkpoint_budget": 100,
          "overall": {
            "canonical_completion_count": 1,
            "canonical_completion_ratio": 0.3333333333333333,
            "canonical_deadline_violation_ratio": 0.3333333333333333,
            "canonical_drop_count": 1,
            "canonical_drop_ratio": 0.3333333333333333,
            "canonical_mean_completion_latency_slots": 4.0,
            "canonical_mean_drop_latency_slots": 4.0,
            "canonical_mean_terminal_latency_slots": 4.0,
            "canonical_pending_count": 1,
            "canonical_pending_ratio": 0.3333333333333333,
            "canonical_reward_count": 2,
            "canonical_reward_per_decision": -14.666666666666666,
            "canonical_reward_per_task": -14.666666666666666,
            "canonical_task_count": 3,
            "canonical_task_mean_reward": -22.0,
            "canonical_task_reward_count": 2,
            "canonical_task_reward_total": -44.0,
            "canonical_tasks_per_decision": 1.0,
            "canonical_terminal_task_count": 2,
            "canonical_unknown_count": 0,
            "completed_count": 1,
            "completion_reward_count": 1,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_reward": 0.0,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_reward_event_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          },
          "reward_coverage": {
            "raw_reward_event_count": 2,
            "raw_terminal_event_count": 3,
            "reward_available_count": 2
          }
        },
        "canonical_task_outcomes": [
          {
            "arrival_slot": 0,
            "canonical_join_key": "trace-1:0:1",
            "canonical_reward": -40.0,
            "canonical_terminal_outcome": "dropped",
            "completion_or_drop_slot": 3,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "episode_id": 0,
            "first_decision_slot": 0,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -40.0,
            "raw_terminal_event_count": 2,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 1,
            "terminal_slot": 3,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 1,
            "canonical_join_key": "trace-1:0:2",
            "canonical_reward": -4.0,
            "canonical_terminal_outcome": "completed",
            "completion_or_drop_slot": 4,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 1,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -4.0,
            "raw_terminal_event_count": 1,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 2,
            "terminal_slot": 4,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 2,
            "canonical_join_key": "trace-1:0:3",
            "canonical_reward": 0.0,
            "canonical_terminal_outcome": "pending_at_horizon",
            "completion_or_drop_slot": null,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 2,
            "latency_slots": null,
            "raw_reward_event_count": 0,
            "raw_reward_total": 0.0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "horizontal",
            "task_id": 3,
            "terminal_slot": 5,
            "trace_id": "trace-1"
          }
        ],
        "checkpoint_budget": 100,
        "decision_count": 3,
        "paper_aligned_diagnostic_metrics": {
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_tasks_per_decision": 1.0,
          "raw_reward_event_coverage_ratio": 1.0,
          "reward_reconciliation_status": "passed",
          "terminal_event_coverage_ratio": 1.5,
          "training_budget": 100
        },
        "raw_vs_canonical_reward_reconciliation": {
          "canonical_task_count": 3,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_terminal_task_count": 2,
          "checkpoint_budget": 100,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_event_recovery_blocked": false,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_reconciled": true,
          "terminal_event_recovery_blocked": false
        }
      },
      "reward_decomposition": {
        "canonical_task_mean_reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -22.0
        },
        "canonical_task_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "canonical_task_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "completion_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "drop_penalty_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "nan_reward_count": 0,
        "raw_event_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "raw_event_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "raw_vs_canonical_reward_delta_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": 0.0
        },
        "raw_vs_canonical_reward_delta_total": 0.0,
        "reward_available_count": 2,
        "reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "reward_by_action_and_terminal_outcome": {
          "horizontal": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "local": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "vertical": {
            "completed": {
              "canonical_task_mean_reward": -4.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -4.0,
              "count": 1,
              "mean_reward": -4.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -4.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -4.0
            },
            "dropped": {
              "canonical_task_mean_reward": -40.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -40.0,
              "count": 1,
              "mean_reward": -40.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -40.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -40.0
            }
          }
        },
        "reward_by_terminal_outcome": {
          "completed": -4.0,
          "dropped": -40.0
        },
        "zero_reward_count": 0
      },
      "reward_event_records": {
        "raw_reward_event_recovery_blocked": false,
        "record_count": 2,
        "reward_available_count": 2,
        "sample_records": [
          {
            "episode_id": 0,
            "raw_reward": -40.0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "reward_reconciled": true,
      "reward_reconciliation_status": "passed",
      "reward_reconciliation_tolerance": 1e-09,
      "same_evaluation_trace_bank": true,
      "terminal_event_records": {
        "record_count": 3,
        "recovered_from_finalized_tasks": true,
        "sample_records": [
          {
            "episode_id": 0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "terminal_event_recovery_blocked": false,
      "unknown_count": 0
    },
    "fixed_local_policy": {
      "action_distribution": {
        "horizontal": 1,
        "local": 1,
        "vertical": 1
      },
      "candidate_policy_vertical_share": 0.3333333333333333,
      "canonical_reward_decomposition": {
        "canonical_task_mean_reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -22.0
        },
        "canonical_task_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "canonical_task_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "completion_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "drop_penalty_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "nan_reward_count": 0,
        "raw_event_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "raw_event_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "raw_vs_canonical_reward_delta_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": 0.0
        },
        "raw_vs_canonical_reward_delta_total": 0.0,
        "reward_available_count": 2,
        "reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "reward_by_action_and_terminal_outcome": {
          "horizontal": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "local": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "vertical": {
            "completed": {
              "canonical_task_mean_reward": -4.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -4.0,
              "count": 1,
              "mean_reward": -4.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -4.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -4.0
            },
            "dropped": {
              "canonical_task_mean_reward": -40.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -40.0,
              "count": 1,
              "mean_reward": -40.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -40.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -40.0
            }
          }
        },
        "reward_by_terminal_outcome": {
          "completed": -4.0,
          "dropped": -40.0
        },
        "zero_reward_count": 0
      },
      "canonical_task_outcome_summary": {
        "by_action": {
          "horizontal": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 1.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 1,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 1,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "local": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 0,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 0,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "vertical": {
            "canonical_completion_ratio": 0.5,
            "canonical_deadline_violation_ratio": 0.5,
            "canonical_drop_ratio": 0.5,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 2,
            "canonical_reward_total": -44.0,
            "canonical_task_count": 2,
            "canonical_task_mean_reward": -22.0,
            "canonical_terminal_task_count": 2,
            "completed_count": 1,
            "completion_reward_count": 1,
            "decision_count": 2,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_completion_latency_slots": 4.0,
            "mean_drop_latency_slots": 4.0,
            "mean_reward": -22.0,
            "mean_terminal_latency_slots": 4.0,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          }
        },
        "checkpoint_budget": 100,
        "overall": {
          "canonical_completion_count": 1,
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_count": 1,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 1,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_count": 2,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_task_count": 3,
          "canonical_task_mean_reward": -22.0,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 2,
          "canonical_unknown_count": 0,
          "completed_count": 1,
          "completion_reward_count": 1,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_reward": 0.0,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        },
        "reward_coverage": {
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "reward_available_count": 2
        }
      },
      "canonical_task_reconciliation": {
        "by_action": {
          "horizontal": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 1.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 1,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 1,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "local": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 0,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 0,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "vertical": {
            "canonical_completion_ratio": 0.5,
            "canonical_deadline_violation_ratio": 0.5,
            "canonical_drop_ratio": 0.5,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 2,
            "canonical_reward_total": -44.0,
            "canonical_task_count": 2,
            "canonical_task_mean_reward": -22.0,
            "canonical_terminal_task_count": 2,
            "completed_count": 1,
            "completion_reward_count": 1,
            "decision_count": 2,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_completion_latency_slots": 4.0,
            "mean_drop_latency_slots": 4.0,
            "mean_reward": -22.0,
            "mean_terminal_latency_slots": 4.0,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          }
        },
        "checkpoint_budget": 100,
        "overall": {
          "canonical_completion_count": 1,
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_count": 1,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 1,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_count": 2,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_task_count": 3,
          "canonical_task_mean_reward": -22.0,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 2,
          "canonical_unknown_count": 0,
          "completed_count": 1,
          "completion_reward_count": 1,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_reward": 0.0,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        },
        "reward_coverage": {
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "reward_available_count": 2
        }
      },
      "canonical_task_reward_count": 2,
      "canonical_task_reward_total": -44.0,
      "checkpoint_budget": 100,
      "completed_count": 1,
      "completed_task_count": 1,
      "completion_ratio": 0.3333333333333333,
      "deadline_violation_ratio": 0.3333333333333333,
      "decision_records_summary": {
        "decision_count": 3,
        "evaluation_action_distribution_source": "evaluation_episodes",
        "sample_records": [
          {
            "episode_id": 0,
            "selected_action": "vertical",
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "drop_ratio": 0.3333333333333333,
      "dropped_count": 1,
      "dropped_task_count": 1,
      "episode_length": 110,
      "episode_reward_totals": [
        -44.0
      ],
      "episode_summaries": [
        {
          "canonical_reward_total": -44.0,
          "completion_count": 1,
          "decision_count": 3,
          "drop_count": 1,
          "episode_id": 0,
          "pending_count": 1,
          "raw_reward_event_count": 2,
          "raw_reward_total": -44.0,
          "reward_recovered": true,
          "terminal_task_count": 2,
          "trace_id": "trace-0",
          "unknown_count": 0
        }
      ],
      "evaluation_action_by_episode_id": {
        "0": {
          "decision_count": 3
        }
      },
      "evaluation_action_by_trace_id": {
        "trace-0": {
          "decision_count": 3
        }
      },
      "evaluation_action_distribution": {
        "horizontal": 1,
        "local": 1,
        "vertical": 1
      },
      "evaluation_action_distribution_source": "evaluation_episodes",
      "evaluation_action_sequence_sample": [
        {
          "episode_id": 0,
          "selected_action": "vertical",
          "task_id": 1,
          "trace_id": "trace-0"
        }
      ],
      "evaluation_decision_count": 3,
      "evaluation_episode_count": 100,
      "evaluation_legal_action_mask_distribution": {
        "local=1|horizontal=1|vertical=1": 3
      },
      "evaluation_reward_summary": {
        "candidate_reproduction_supported": true,
        "canonical_task_count": 3,
        "canonical_task_reward_count": 2,
        "canonical_task_reward_total": -44.0,
        "completed_task_count": 1,
        "dropped_task_count": 1,
        "evaluation_episode_count": 100,
        "evaluation_on_training_traces": false,
        "mean_reward": -44.0,
        "pending_at_horizon_count": 1,
        "raw_event_reward_count": 2,
        "raw_event_reward_total": -44.0,
        "raw_reward_emission_count": 2,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 3,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_available_count": 2,
        "reward_bearing_transition_count": 2,
        "same_evaluation_trace_bank": true,
        "terminal_event_recovery_blocked": false,
        "terminal_transition_count": 2,
        "trace_bank_disjoint": true,
        "trace_bank_ids": {
          "evaluation": "eval-bank",
          "training": "train-bank"
        },
        "trace_ids": [
          "trace-0"
        ],
        "unknown_task_count": 0
      },
      "evaluation_trace_bank_id": "eval-bank",
      "mean_latency_slots": 4.0,
      "paper_aligned_diagnostic_metrics": {
        "canonical_completion_ratio": 0.3333333333333333,
        "canonical_deadline_violation_ratio": 0.3333333333333333,
        "canonical_drop_ratio": 0.3333333333333333,
        "canonical_mean_completion_latency_slots": 4.0,
        "canonical_mean_drop_latency_slots": 4.0,
        "canonical_mean_terminal_latency_slots": 4.0,
        "canonical_pending_ratio": 0.3333333333333333,
        "canonical_reward_per_decision": -14.666666666666666,
        "canonical_reward_per_task": -14.666666666666666,
        "canonical_tasks_per_decision": 1.0,
        "raw_reward_event_coverage_ratio": 1.0,
        "reward_reconciliation_status": "passed",
        "terminal_event_coverage_ratio": 1.5,
        "training_budget": 100
      },
      "pending_at_horizon_count": 1,
      "pending_task_count": 1,
      "per_action_outcome_summary": {
        "horizontal": {
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 0.0,
          "canonical_drop_ratio": 0.0,
          "canonical_pending_ratio": 1.0,
          "canonical_reward_count": 0,
          "canonical_reward_total": 0.0,
          "canonical_task_count": 1,
          "canonical_task_mean_reward": 0.0,
          "canonical_terminal_task_count": 0,
          "completed_count": 0,
          "completion_reward_count": 0,
          "decision_count": 1,
          "double_count_detected": false,
          "drop_penalty_count": 0,
          "dropped_count": 0,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "mean_completion_latency_slots": null,
          "mean_drop_latency_slots": null,
          "mean_reward": 0.0,
          "mean_terminal_latency_slots": null,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 0,
          "raw_event_reward_total": 0.0,
          "raw_reward_emission_count": 0,
          "raw_terminal_event_count": 0,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 0,
          "terminal_transition_count": 0,
          "total_reward": 0.0,
          "unknown_count": 0
        },
        "local": {
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 0.0,
          "canonical_drop_ratio": 0.0,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_count": 0,
          "canonical_reward_total": 0.0,
          "canonical_task_count": 0,
          "canonical_task_mean_reward": 0.0,
          "canonical_terminal_task_count": 0,
          "completed_count": 0,
          "completion_reward_count": 0,
          "decision_count": 0,
          "double_count_detected": false,
          "drop_penalty_count": 0,
          "dropped_count": 0,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "mean_completion_latency_slots": null,
          "mean_drop_latency_slots": null,
          "mean_reward": 0.0,
          "mean_terminal_latency_slots": null,
          "pending_at_horizon_count": 0,
          "raw_event_reward_count": 0,
          "raw_event_reward_total": 0.0,
          "raw_reward_emission_count": 0,
          "raw_terminal_event_count": 0,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 0,
          "terminal_transition_count": 0,
          "total_reward": 0.0,
          "unknown_count": 0
        },
        "vertical": {
          "canonical_completion_ratio": 0.5,
          "canonical_deadline_violation_ratio": 0.5,
          "canonical_drop_ratio": 0.5,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_count": 2,
          "canonical_reward_total": -44.0,
          "canonical_task_count": 2,
          "canonical_task_mean_reward": -22.0,
          "canonical_terminal_task_count": 2,
          "completed_count": 1,
          "completion_reward_count": 1,
          "decision_count": 2,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_completion_latency_slots": 4.0,
          "mean_drop_latency_slots": 4.0,
          "mean_reward": -22.0,
          "mean_terminal_latency_slots": 4.0,
          "pending_at_horizon_count": 0,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        }
      },
      "policy_kind": "candidate",
      "policy_name": "candidate_policy_at_100",
      "raw_event_reward_count": 2,
      "raw_event_reward_total": -44.0,
      "raw_lifecycle_terminal_event_count": 3,
      "raw_reward_event_count": 2,
      "raw_reward_event_recovery_blocked": false,
      "raw_reward_total": -44.0,
      "raw_terminal_event_count": 3,
      "raw_vs_canonical_reward_reconciliation": {
        "canonical_task_count": 3,
        "canonical_task_reward_count": 2,
        "canonical_task_reward_total": -44.0,
        "canonical_terminal_task_count": 2,
        "checkpoint_budget": 100,
        "duplicate_reward_event_count": 0,
        "duplicate_terminal_event_count": 1,
        "raw_event_reward_count": 2,
        "raw_event_reward_total": -44.0,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 3,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_reconciled": true,
        "terminal_event_recovery_blocked": false
      },
      "reconciliation": {
        "canonical_reward_decomposition": {
          "canonical_task_mean_reward_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -22.0
          },
          "canonical_task_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 2
          },
          "canonical_task_reward_total_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "completion_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 1
          },
          "drop_penalty_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 1
          },
          "nan_reward_count": 0,
          "raw_event_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 2
          },
          "raw_event_reward_total_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "raw_vs_canonical_reward_delta_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": 0.0
          },
          "raw_vs_canonical_reward_delta_total": 0.0,
          "reward_available_count": 2,
          "reward_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "reward_by_action_and_terminal_outcome": {
            "horizontal": {
              "completed": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              },
              "dropped": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              }
            },
            "local": {
              "completed": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              },
              "dropped": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              }
            },
            "vertical": {
              "completed": {
                "canonical_task_mean_reward": -4.0,
                "canonical_task_reward_count": 1,
                "canonical_task_reward_total": -4.0,
                "count": 1,
                "mean_reward": -4.0,
                "raw_event_reward_count": 1,
                "raw_event_reward_total": -4.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": -4.0
              },
              "dropped": {
                "canonical_task_mean_reward": -40.0,
                "canonical_task_reward_count": 1,
                "canonical_task_reward_total": -40.0,
                "count": 1,
                "mean_reward": -40.0,
                "raw_event_reward_count": 1,
                "raw_event_reward_total": -40.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": -40.0
              }
            }
          },
          "reward_by_terminal_outcome": {
            "completed": -4.0,
            "dropped": -40.0
          },
          "zero_reward_count": 0
        },
        "canonical_task_outcome_sample": [
          {
            "arrival_slot": 0,
            "canonical_join_key": "trace-1:0:1",
            "canonical_reward": -40.0,
            "canonical_terminal_outcome": "dropped",
            "completion_or_drop_slot": 3,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "episode_id": 0,
            "first_decision_slot": 0,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -40.0,
            "raw_terminal_event_count": 2,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 1,
            "terminal_slot": 3,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 1,
            "canonical_join_key": "trace-1:0:2",
            "canonical_reward": -4.0,
            "canonical_terminal_outcome": "completed",
            "completion_or_drop_slot": 4,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 1,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -4.0,
            "raw_terminal_event_count": 1,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 2,
            "terminal_slot": 4,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 2,
            "canonical_join_key": "trace-1:0:3",
            "canonical_reward": 0.0,
            "canonical_terminal_outcome": "pending_at_horizon",
            "completion_or_drop_slot": null,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 2,
            "latency_slots": null,
            "raw_reward_event_count": 0,
            "raw_reward_total": 0.0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "horizontal",
            "task_id": 3,
            "terminal_slot": 5,
            "trace_id": "trace-1"
          }
        ],
        "canonical_task_outcome_summary": {
          "by_action": {
            "horizontal": {
              "canonical_completion_ratio": 0.0,
              "canonical_deadline_violation_ratio": 0.0,
              "canonical_drop_ratio": 0.0,
              "canonical_pending_ratio": 1.0,
              "canonical_reward_count": 0,
              "canonical_reward_total": 0.0,
              "canonical_task_count": 1,
              "canonical_task_mean_reward": 0.0,
              "canonical_terminal_task_count": 0,
              "completed_count": 0,
              "completion_reward_count": 0,
              "decision_count": 1,
              "double_count_detected": false,
              "drop_penalty_count": 0,
              "dropped_count": 0,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 0,
              "mean_completion_latency_slots": null,
              "mean_drop_latency_slots": null,
              "mean_reward": 0.0,
              "mean_terminal_latency_slots": null,
              "pending_at_horizon_count": 1,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_reward_emission_count": 0,
              "raw_terminal_event_count": 0,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 0,
              "terminal_transition_count": 0,
              "total_reward": 0.0,
              "unknown_count": 0
            },
            "local": {
              "canonical_completion_ratio": 0.0,
              "canonical_deadline_violation_ratio": 0.0,
              "canonical_drop_ratio": 0.0,
              "canonical_pending_ratio": 0.0,
              "canonical_reward_count": 0,
              "canonical_reward_total": 0.0,
              "canonical_task_count": 0,
              "canonical_task_mean_reward": 0.0,
              "canonical_terminal_task_count": 0,
              "completed_count": 0,
              "completion_reward_count": 0,
              "decision_count": 0,
              "double_count_detected": false,
              "drop_penalty_count": 0,
              "dropped_count": 0,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 0,
              "mean_completion_latency_slots": null,
              "mean_drop_latency_slots": null,
              "mean_reward": 0.0,
              "mean_terminal_latency_slots": null,
              "pending_at_horizon_count": 0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_reward_emission_count": 0,
              "raw_terminal_event_count": 0,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 0,
              "terminal_transition_count": 0,
              "total_reward": 0.0,
              "unknown_count": 0
            },
            "vertical": {
              "canonical_completion_ratio": 0.5,
              "canonical_deadline_violation_ratio": 0.5,
              "canonical_drop_ratio": 0.5,
              "canonical_pending_ratio": 0.0,
              "canonical_reward_count": 2,
              "canonical_reward_total": -44.0,
              "canonical_task_count": 2,
              "canonical_task_mean_reward": -22.0,
              "canonical_terminal_task_count": 2,
              "completed_count": 1,
              "completion_reward_count": 1,
              "decision_count": 2,
              "double_count_detected": true,
              "drop_penalty_count": 1,
              "dropped_count": 1,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 1,
              "mean_completion_latency_slots": 4.0,
              "mean_drop_latency_slots": 4.0,
              "mean_reward": -22.0,
              "mean_terminal_latency_slots": 4.0,
              "pending_at_horizon_count": 0,
              "raw_event_reward_count": 2,
              "raw_event_reward_total": -44.0,
              "raw_reward_emission_count": 2,
              "raw_terminal_event_count": 3,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 2,
              "terminal_transition_count": 2,
              "total_reward": -44.0,
              "unknown_count": 0
            }
          },
          "checkpoint_budget": 100,
          "overall": {
            "canonical_completion_count": 1,
            "canonical_completion_ratio": 0.3333333333333333,
            "canonical_deadline_violation_ratio": 0.3333333333333333,
            "canonical_drop_count": 1,
            "canonical_drop_ratio": 0.3333333333333333,
            "canonical_mean_completion_latency_slots": 4.0,
            "canonical_mean_drop_latency_slots": 4.0,
            "canonical_mean_terminal_latency_slots": 4.0,
            "canonical_pending_count": 1,
            "canonical_pending_ratio": 0.3333333333333333,
            "canonical_reward_count": 2,
            "canonical_reward_per_decision": -14.666666666666666,
            "canonical_reward_per_task": -14.666666666666666,
            "canonical_task_count": 3,
            "canonical_task_mean_reward": -22.0,
            "canonical_task_reward_count": 2,
            "canonical_task_reward_total": -44.0,
            "canonical_tasks_per_decision": 1.0,
            "canonical_terminal_task_count": 2,
            "canonical_unknown_count": 0,
            "completed_count": 1,
            "completion_reward_count": 1,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_reward": 0.0,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_reward_event_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          },
          "reward_coverage": {
            "raw_reward_event_count": 2,
            "raw_terminal_event_count": 3,
            "reward_available_count": 2
          }
        },
        "canonical_task_outcomes": [
          {
            "arrival_slot": 0,
            "canonical_join_key": "trace-1:0:1",
            "canonical_reward": -40.0,
            "canonical_terminal_outcome": "dropped",
            "completion_or_drop_slot": 3,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "episode_id": 0,
            "first_decision_slot": 0,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -40.0,
            "raw_terminal_event_count": 2,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 1,
            "terminal_slot": 3,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 1,
            "canonical_join_key": "trace-1:0:2",
            "canonical_reward": -4.0,
            "canonical_terminal_outcome": "completed",
            "completion_or_drop_slot": 4,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 1,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -4.0,
            "raw_terminal_event_count": 1,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 2,
            "terminal_slot": 4,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 2,
            "canonical_join_key": "trace-1:0:3",
            "canonical_reward": 0.0,
            "canonical_terminal_outcome": "pending_at_horizon",
            "completion_or_drop_slot": null,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 2,
            "latency_slots": null,
            "raw_reward_event_count": 0,
            "raw_reward_total": 0.0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "horizontal",
            "task_id": 3,
            "terminal_slot": 5,
            "trace_id": "trace-1"
          }
        ],
        "checkpoint_budget": 100,
        "decision_count": 3,
        "paper_aligned_diagnostic_metrics": {
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_tasks_per_decision": 1.0,
          "raw_reward_event_coverage_ratio": 1.0,
          "reward_reconciliation_status": "passed",
          "terminal_event_coverage_ratio": 1.5,
          "training_budget": 100
        },
        "raw_vs_canonical_reward_reconciliation": {
          "canonical_task_count": 3,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_terminal_task_count": 2,
          "checkpoint_budget": 100,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_event_recovery_blocked": false,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_reconciled": true,
          "terminal_event_recovery_blocked": false
        }
      },
      "reward_decomposition": {
        "canonical_task_mean_reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -22.0
        },
        "canonical_task_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "canonical_task_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "completion_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "drop_penalty_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "nan_reward_count": 0,
        "raw_event_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "raw_event_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "raw_vs_canonical_reward_delta_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": 0.0
        },
        "raw_vs_canonical_reward_delta_total": 0.0,
        "reward_available_count": 2,
        "reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "reward_by_action_and_terminal_outcome": {
          "horizontal": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "local": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "vertical": {
            "completed": {
              "canonical_task_mean_reward": -4.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -4.0,
              "count": 1,
              "mean_reward": -4.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -4.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -4.0
            },
            "dropped": {
              "canonical_task_mean_reward": -40.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -40.0,
              "count": 1,
              "mean_reward": -40.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -40.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -40.0
            }
          }
        },
        "reward_by_terminal_outcome": {
          "completed": -4.0,
          "dropped": -40.0
        },
        "zero_reward_count": 0
      },
      "reward_event_records": {
        "raw_reward_event_recovery_blocked": false,
        "record_count": 2,
        "reward_available_count": 2,
        "sample_records": [
          {
            "episode_id": 0,
            "raw_reward": -40.0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "reward_reconciled": true,
      "reward_reconciliation_status": "passed",
      "reward_reconciliation_tolerance": 1e-09,
      "same_evaluation_trace_bank": true,
      "terminal_event_records": {
        "record_count": 3,
        "recovered_from_finalized_tasks": true,
        "sample_records": [
          {
            "episode_id": 0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "terminal_event_recovery_blocked": false,
      "unknown_count": 0
    },
    "fixed_vertical_policy": {
      "action_distribution": {
        "horizontal": 1,
        "local": 1,
        "vertical": 1
      },
      "candidate_policy_vertical_share": 0.3333333333333333,
      "canonical_reward_decomposition": {
        "canonical_task_mean_reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -22.0
        },
        "canonical_task_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "canonical_task_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "completion_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "drop_penalty_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "nan_reward_count": 0,
        "raw_event_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "raw_event_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "raw_vs_canonical_reward_delta_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": 0.0
        },
        "raw_vs_canonical_reward_delta_total": 0.0,
        "reward_available_count": 2,
        "reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "reward_by_action_and_terminal_outcome": {
          "horizontal": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "local": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "vertical": {
            "completed": {
              "canonical_task_mean_reward": -4.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -4.0,
              "count": 1,
              "mean_reward": -4.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -4.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -4.0
            },
            "dropped": {
              "canonical_task_mean_reward": -40.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -40.0,
              "count": 1,
              "mean_reward": -40.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -40.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -40.0
            }
          }
        },
        "reward_by_terminal_outcome": {
          "completed": -4.0,
          "dropped": -40.0
        },
        "zero_reward_count": 0
      },
      "canonical_task_outcome_summary": {
        "by_action": {
          "horizontal": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 1.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 1,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 1,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "local": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 0,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 0,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "vertical": {
            "canonical_completion_ratio": 0.5,
            "canonical_deadline_violation_ratio": 0.5,
            "canonical_drop_ratio": 0.5,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 2,
            "canonical_reward_total": -44.0,
            "canonical_task_count": 2,
            "canonical_task_mean_reward": -22.0,
            "canonical_terminal_task_count": 2,
            "completed_count": 1,
            "completion_reward_count": 1,
            "decision_count": 2,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_completion_latency_slots": 4.0,
            "mean_drop_latency_slots": 4.0,
            "mean_reward": -22.0,
            "mean_terminal_latency_slots": 4.0,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          }
        },
        "checkpoint_budget": 100,
        "overall": {
          "canonical_completion_count": 1,
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_count": 1,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 1,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_count": 2,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_task_count": 3,
          "canonical_task_mean_reward": -22.0,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 2,
          "canonical_unknown_count": 0,
          "completed_count": 1,
          "completion_reward_count": 1,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_reward": 0.0,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        },
        "reward_coverage": {
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "reward_available_count": 2
        }
      },
      "canonical_task_reconciliation": {
        "by_action": {
          "horizontal": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 1.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 1,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 1,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "local": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 0,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 0,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "vertical": {
            "canonical_completion_ratio": 0.5,
            "canonical_deadline_violation_ratio": 0.5,
            "canonical_drop_ratio": 0.5,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 2,
            "canonical_reward_total": -44.0,
            "canonical_task_count": 2,
            "canonical_task_mean_reward": -22.0,
            "canonical_terminal_task_count": 2,
            "completed_count": 1,
            "completion_reward_count": 1,
            "decision_count": 2,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_completion_latency_slots": 4.0,
            "mean_drop_latency_slots": 4.0,
            "mean_reward": -22.0,
            "mean_terminal_latency_slots": 4.0,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          }
        },
        "checkpoint_budget": 100,
        "overall": {
          "canonical_completion_count": 1,
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_count": 1,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 1,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_count": 2,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_task_count": 3,
          "canonical_task_mean_reward": -22.0,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 2,
          "canonical_unknown_count": 0,
          "completed_count": 1,
          "completion_reward_count": 1,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_reward": 0.0,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        },
        "reward_coverage": {
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "reward_available_count": 2
        }
      },
      "canonical_task_reward_count": 2,
      "canonical_task_reward_total": -44.0,
      "checkpoint_budget": 100,
      "completed_count": 1,
      "completed_task_count": 1,
      "completion_ratio": 0.3333333333333333,
      "deadline_violation_ratio": 0.3333333333333333,
      "decision_records_summary": {
        "decision_count": 3,
        "evaluation_action_distribution_source": "evaluation_episodes",
        "sample_records": [
          {
            "episode_id": 0,
            "selected_action": "vertical",
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "drop_ratio": 0.3333333333333333,
      "dropped_count": 1,
      "dropped_task_count": 1,
      "episode_length": 110,
      "episode_reward_totals": [
        -44.0
      ],
      "episode_summaries": [
        {
          "canonical_reward_total": -44.0,
          "completion_count": 1,
          "decision_count": 3,
          "drop_count": 1,
          "episode_id": 0,
          "pending_count": 1,
          "raw_reward_event_count": 2,
          "raw_reward_total": -44.0,
          "reward_recovered": true,
          "terminal_task_count": 2,
          "trace_id": "trace-0",
          "unknown_count": 0
        }
      ],
      "evaluation_action_by_episode_id": {
        "0": {
          "decision_count": 3
        }
      },
      "evaluation_action_by_trace_id": {
        "trace-0": {
          "decision_count": 3
        }
      },
      "evaluation_action_distribution": {
        "horizontal": 1,
        "local": 1,
        "vertical": 1
      },
      "evaluation_action_distribution_source": "evaluation_episodes",
      "evaluation_action_sequence_sample": [
        {
          "episode_id": 0,
          "selected_action": "vertical",
          "task_id": 1,
          "trace_id": "trace-0"
        }
      ],
      "evaluation_decision_count": 3,
      "evaluation_episode_count": 100,
      "evaluation_legal_action_mask_distribution": {
        "local=1|horizontal=1|vertical=1": 3
      },
      "evaluation_reward_summary": {
        "candidate_reproduction_supported": true,
        "canonical_task_count": 3,
        "canonical_task_reward_count": 2,
        "canonical_task_reward_total": -44.0,
        "completed_task_count": 1,
        "dropped_task_count": 1,
        "evaluation_episode_count": 100,
        "evaluation_on_training_traces": false,
        "mean_reward": -44.0,
        "pending_at_horizon_count": 1,
        "raw_event_reward_count": 2,
        "raw_event_reward_total": -44.0,
        "raw_reward_emission_count": 2,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 3,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_available_count": 2,
        "reward_bearing_transition_count": 2,
        "same_evaluation_trace_bank": true,
        "terminal_event_recovery_blocked": false,
        "terminal_transition_count": 2,
        "trace_bank_disjoint": true,
        "trace_bank_ids": {
          "evaluation": "eval-bank",
          "training": "train-bank"
        },
        "trace_ids": [
          "trace-0"
        ],
        "unknown_task_count": 0
      },
      "evaluation_trace_bank_id": "eval-bank",
      "mean_latency_slots": 4.0,
      "paper_aligned_diagnostic_metrics": {
        "canonical_completion_ratio": 0.3333333333333333,
        "canonical_deadline_violation_ratio": 0.3333333333333333,
        "canonical_drop_ratio": 0.3333333333333333,
        "canonical_mean_completion_latency_slots": 4.0,
        "canonical_mean_drop_latency_slots": 4.0,
        "canonical_mean_terminal_latency_slots": 4.0,
        "canonical_pending_ratio": 0.3333333333333333,
        "canonical_reward_per_decision": -14.666666666666666,
        "canonical_reward_per_task": -14.666666666666666,
        "canonical_tasks_per_decision": 1.0,
        "raw_reward_event_coverage_ratio": 1.0,
        "reward_reconciliation_status": "passed",
        "terminal_event_coverage_ratio": 1.5,
        "training_budget": 100
      },
      "pending_at_horizon_count": 1,
      "pending_task_count": 1,
      "per_action_outcome_summary": {
        "horizontal": {
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 0.0,
          "canonical_drop_ratio": 0.0,
          "canonical_pending_ratio": 1.0,
          "canonical_reward_count": 0,
          "canonical_reward_total": 0.0,
          "canonical_task_count": 1,
          "canonical_task_mean_reward": 0.0,
          "canonical_terminal_task_count": 0,
          "completed_count": 0,
          "completion_reward_count": 0,
          "decision_count": 1,
          "double_count_detected": false,
          "drop_penalty_count": 0,
          "dropped_count": 0,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "mean_completion_latency_slots": null,
          "mean_drop_latency_slots": null,
          "mean_reward": 0.0,
          "mean_terminal_latency_slots": null,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 0,
          "raw_event_reward_total": 0.0,
          "raw_reward_emission_count": 0,
          "raw_terminal_event_count": 0,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 0,
          "terminal_transition_count": 0,
          "total_reward": 0.0,
          "unknown_count": 0
        },
        "local": {
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 0.0,
          "canonical_drop_ratio": 0.0,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_count": 0,
          "canonical_reward_total": 0.0,
          "canonical_task_count": 0,
          "canonical_task_mean_reward": 0.0,
          "canonical_terminal_task_count": 0,
          "completed_count": 0,
          "completion_reward_count": 0,
          "decision_count": 0,
          "double_count_detected": false,
          "drop_penalty_count": 0,
          "dropped_count": 0,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "mean_completion_latency_slots": null,
          "mean_drop_latency_slots": null,
          "mean_reward": 0.0,
          "mean_terminal_latency_slots": null,
          "pending_at_horizon_count": 0,
          "raw_event_reward_count": 0,
          "raw_event_reward_total": 0.0,
          "raw_reward_emission_count": 0,
          "raw_terminal_event_count": 0,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 0,
          "terminal_transition_count": 0,
          "total_reward": 0.0,
          "unknown_count": 0
        },
        "vertical": {
          "canonical_completion_ratio": 0.5,
          "canonical_deadline_violation_ratio": 0.5,
          "canonical_drop_ratio": 0.5,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_count": 2,
          "canonical_reward_total": -44.0,
          "canonical_task_count": 2,
          "canonical_task_mean_reward": -22.0,
          "canonical_terminal_task_count": 2,
          "completed_count": 1,
          "completion_reward_count": 1,
          "decision_count": 2,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_completion_latency_slots": 4.0,
          "mean_drop_latency_slots": 4.0,
          "mean_reward": -22.0,
          "mean_terminal_latency_slots": 4.0,
          "pending_at_horizon_count": 0,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        }
      },
      "policy_kind": "candidate",
      "policy_name": "candidate_policy_at_100",
      "raw_event_reward_count": 2,
      "raw_event_reward_total": -44.0,
      "raw_lifecycle_terminal_event_count": 3,
      "raw_reward_event_count": 2,
      "raw_reward_event_recovery_blocked": false,
      "raw_reward_total": -44.0,
      "raw_terminal_event_count": 3,
      "raw_vs_canonical_reward_reconciliation": {
        "canonical_task_count": 3,
        "canonical_task_reward_count": 2,
        "canonical_task_reward_total": -44.0,
        "canonical_terminal_task_count": 2,
        "checkpoint_budget": 100,
        "duplicate_reward_event_count": 0,
        "duplicate_terminal_event_count": 1,
        "raw_event_reward_count": 2,
        "raw_event_reward_total": -44.0,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 3,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_reconciled": true,
        "terminal_event_recovery_blocked": false
      },
      "reconciliation": {
        "canonical_reward_decomposition": {
          "canonical_task_mean_reward_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -22.0
          },
          "canonical_task_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 2
          },
          "canonical_task_reward_total_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "completion_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 1
          },
          "drop_penalty_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 1
          },
          "nan_reward_count": 0,
          "raw_event_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 2
          },
          "raw_event_reward_total_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "raw_vs_canonical_reward_delta_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": 0.0
          },
          "raw_vs_canonical_reward_delta_total": 0.0,
          "reward_available_count": 2,
          "reward_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "reward_by_action_and_terminal_outcome": {
            "horizontal": {
              "completed": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              },
              "dropped": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              }
            },
            "local": {
              "completed": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              },
              "dropped": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              }
            },
            "vertical": {
              "completed": {
                "canonical_task_mean_reward": -4.0,
                "canonical_task_reward_count": 1,
                "canonical_task_reward_total": -4.0,
                "count": 1,
                "mean_reward": -4.0,
                "raw_event_reward_count": 1,
                "raw_event_reward_total": -4.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": -4.0
              },
              "dropped": {
                "canonical_task_mean_reward": -40.0,
                "canonical_task_reward_count": 1,
                "canonical_task_reward_total": -40.0,
                "count": 1,
                "mean_reward": -40.0,
                "raw_event_reward_count": 1,
                "raw_event_reward_total": -40.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": -40.0
              }
            }
          },
          "reward_by_terminal_outcome": {
            "completed": -4.0,
            "dropped": -40.0
          },
          "zero_reward_count": 0
        },
        "canonical_task_outcome_sample": [
          {
            "arrival_slot": 0,
            "canonical_join_key": "trace-1:0:1",
            "canonical_reward": -40.0,
            "canonical_terminal_outcome": "dropped",
            "completion_or_drop_slot": 3,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "episode_id": 0,
            "first_decision_slot": 0,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -40.0,
            "raw_terminal_event_count": 2,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 1,
            "terminal_slot": 3,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 1,
            "canonical_join_key": "trace-1:0:2",
            "canonical_reward": -4.0,
            "canonical_terminal_outcome": "completed",
            "completion_or_drop_slot": 4,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 1,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -4.0,
            "raw_terminal_event_count": 1,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 2,
            "terminal_slot": 4,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 2,
            "canonical_join_key": "trace-1:0:3",
            "canonical_reward": 0.0,
            "canonical_terminal_outcome": "pending_at_horizon",
            "completion_or_drop_slot": null,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 2,
            "latency_slots": null,
            "raw_reward_event_count": 0,
            "raw_reward_total": 0.0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "horizontal",
            "task_id": 3,
            "terminal_slot": 5,
            "trace_id": "trace-1"
          }
        ],
        "canonical_task_outcome_summary": {
          "by_action": {
            "horizontal": {
              "canonical_completion_ratio": 0.0,
              "canonical_deadline_violation_ratio": 0.0,
              "canonical_drop_ratio": 0.0,
              "canonical_pending_ratio": 1.0,
              "canonical_reward_count": 0,
              "canonical_reward_total": 0.0,
              "canonical_task_count": 1,
              "canonical_task_mean_reward": 0.0,
              "canonical_terminal_task_count": 0,
              "completed_count": 0,
              "completion_reward_count": 0,
              "decision_count": 1,
              "double_count_detected": false,
              "drop_penalty_count": 0,
              "dropped_count": 0,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 0,
              "mean_completion_latency_slots": null,
              "mean_drop_latency_slots": null,
              "mean_reward": 0.0,
              "mean_terminal_latency_slots": null,
              "pending_at_horizon_count": 1,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_reward_emission_count": 0,
              "raw_terminal_event_count": 0,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 0,
              "terminal_transition_count": 0,
              "total_reward": 0.0,
              "unknown_count": 0
            },
            "local": {
              "canonical_completion_ratio": 0.0,
              "canonical_deadline_violation_ratio": 0.0,
              "canonical_drop_ratio": 0.0,
              "canonical_pending_ratio": 0.0,
              "canonical_reward_count": 0,
              "canonical_reward_total": 0.0,
              "canonical_task_count": 0,
              "canonical_task_mean_reward": 0.0,
              "canonical_terminal_task_count": 0,
              "completed_count": 0,
              "completion_reward_count": 0,
              "decision_count": 0,
              "double_count_detected": false,
              "drop_penalty_count": 0,
              "dropped_count": 0,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 0,
              "mean_completion_latency_slots": null,
              "mean_drop_latency_slots": null,
              "mean_reward": 0.0,
              "mean_terminal_latency_slots": null,
              "pending_at_horizon_count": 0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_reward_emission_count": 0,
              "raw_terminal_event_count": 0,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 0,
              "terminal_transition_count": 0,
              "total_reward": 0.0,
              "unknown_count": 0
            },
            "vertical": {
              "canonical_completion_ratio": 0.5,
              "canonical_deadline_violation_ratio": 0.5,
              "canonical_drop_ratio": 0.5,
              "canonical_pending_ratio": 0.0,
              "canonical_reward_count": 2,
              "canonical_reward_total": -44.0,
              "canonical_task_count": 2,
              "canonical_task_mean_reward": -22.0,
              "canonical_terminal_task_count": 2,
              "completed_count": 1,
              "completion_reward_count": 1,
              "decision_count": 2,
              "double_count_detected": true,
              "drop_penalty_count": 1,
              "dropped_count": 1,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 1,
              "mean_completion_latency_slots": 4.0,
              "mean_drop_latency_slots": 4.0,
              "mean_reward": -22.0,
              "mean_terminal_latency_slots": 4.0,
              "pending_at_horizon_count": 0,
              "raw_event_reward_count": 2,
              "raw_event_reward_total": -44.0,
              "raw_reward_emission_count": 2,
              "raw_terminal_event_count": 3,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 2,
              "terminal_transition_count": 2,
              "total_reward": -44.0,
              "unknown_count": 0
            }
          },
          "checkpoint_budget": 100,
          "overall": {
            "canonical_completion_count": 1,
            "canonical_completion_ratio": 0.3333333333333333,
            "canonical_deadline_violation_ratio": 0.3333333333333333,
            "canonical_drop_count": 1,
            "canonical_drop_ratio": 0.3333333333333333,
            "canonical_mean_completion_latency_slots": 4.0,
            "canonical_mean_drop_latency_slots": 4.0,
            "canonical_mean_terminal_latency_slots": 4.0,
            "canonical_pending_count": 1,
            "canonical_pending_ratio": 0.3333333333333333,
            "canonical_reward_count": 2,
            "canonical_reward_per_decision": -14.666666666666666,
            "canonical_reward_per_task": -14.666666666666666,
            "canonical_task_count": 3,
            "canonical_task_mean_reward": -22.0,
            "canonical_task_reward_count": 2,
            "canonical_task_reward_total": -44.0,
            "canonical_tasks_per_decision": 1.0,
            "canonical_terminal_task_count": 2,
            "canonical_unknown_count": 0,
            "completed_count": 1,
            "completion_reward_count": 1,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_reward": 0.0,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_reward_event_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          },
          "reward_coverage": {
            "raw_reward_event_count": 2,
            "raw_terminal_event_count": 3,
            "reward_available_count": 2
          }
        },
        "canonical_task_outcomes": [
          {
            "arrival_slot": 0,
            "canonical_join_key": "trace-1:0:1",
            "canonical_reward": -40.0,
            "canonical_terminal_outcome": "dropped",
            "completion_or_drop_slot": 3,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "episode_id": 0,
            "first_decision_slot": 0,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -40.0,
            "raw_terminal_event_count": 2,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 1,
            "terminal_slot": 3,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 1,
            "canonical_join_key": "trace-1:0:2",
            "canonical_reward": -4.0,
            "canonical_terminal_outcome": "completed",
            "completion_or_drop_slot": 4,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 1,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -4.0,
            "raw_terminal_event_count": 1,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 2,
            "terminal_slot": 4,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 2,
            "canonical_join_key": "trace-1:0:3",
            "canonical_reward": 0.0,
            "canonical_terminal_outcome": "pending_at_horizon",
            "completion_or_drop_slot": null,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 2,
            "latency_slots": null,
            "raw_reward_event_count": 0,
            "raw_reward_total": 0.0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "horizontal",
            "task_id": 3,
            "terminal_slot": 5,
            "trace_id": "trace-1"
          }
        ],
        "checkpoint_budget": 100,
        "decision_count": 3,
        "paper_aligned_diagnostic_metrics": {
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_tasks_per_decision": 1.0,
          "raw_reward_event_coverage_ratio": 1.0,
          "reward_reconciliation_status": "passed",
          "terminal_event_coverage_ratio": 1.5,
          "training_budget": 100
        },
        "raw_vs_canonical_reward_reconciliation": {
          "canonical_task_count": 3,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_terminal_task_count": 2,
          "checkpoint_budget": 100,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_event_recovery_blocked": false,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_reconciled": true,
          "terminal_event_recovery_blocked": false
        }
      },
      "reward_decomposition": {
        "canonical_task_mean_reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -22.0
        },
        "canonical_task_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "canonical_task_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "completion_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "drop_penalty_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "nan_reward_count": 0,
        "raw_event_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "raw_event_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "raw_vs_canonical_reward_delta_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": 0.0
        },
        "raw_vs_canonical_reward_delta_total": 0.0,
        "reward_available_count": 2,
        "reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "reward_by_action_and_terminal_outcome": {
          "horizontal": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "local": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "vertical": {
            "completed": {
              "canonical_task_mean_reward": -4.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -4.0,
              "count": 1,
              "mean_reward": -4.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -4.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -4.0
            },
            "dropped": {
              "canonical_task_mean_reward": -40.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -40.0,
              "count": 1,
              "mean_reward": -40.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -40.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -40.0
            }
          }
        },
        "reward_by_terminal_outcome": {
          "completed": -4.0,
          "dropped": -40.0
        },
        "zero_reward_count": 0
      },
      "reward_event_records": {
        "raw_reward_event_recovery_blocked": false,
        "record_count": 2,
        "reward_available_count": 2,
        "sample_records": [
          {
            "episode_id": 0,
            "raw_reward": -40.0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "reward_reconciled": true,
      "reward_reconciliation_status": "passed",
      "reward_reconciliation_tolerance": 1e-09,
      "same_evaluation_trace_bank": true,
      "terminal_event_records": {
        "record_count": 3,
        "recovered_from_finalized_tasks": true,
        "sample_records": [
          {
            "episode_id": 0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "terminal_event_recovery_blocked": false,
      "unknown_count": 0
    },
    "random_legal_policy": {
      "action_distribution": {
        "horizontal": 1,
        "local": 1,
        "vertical": 1
      },
      "candidate_policy_vertical_share": 0.3333333333333333,
      "canonical_reward_decomposition": {
        "canonical_task_mean_reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -22.0
        },
        "canonical_task_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "canonical_task_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "completion_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "drop_penalty_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "nan_reward_count": 0,
        "raw_event_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "raw_event_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "raw_vs_canonical_reward_delta_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": 0.0
        },
        "raw_vs_canonical_reward_delta_total": 0.0,
        "reward_available_count": 2,
        "reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "reward_by_action_and_terminal_outcome": {
          "horizontal": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "local": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "vertical": {
            "completed": {
              "canonical_task_mean_reward": -4.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -4.0,
              "count": 1,
              "mean_reward": -4.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -4.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -4.0
            },
            "dropped": {
              "canonical_task_mean_reward": -40.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -40.0,
              "count": 1,
              "mean_reward": -40.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -40.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -40.0
            }
          }
        },
        "reward_by_terminal_outcome": {
          "completed": -4.0,
          "dropped": -40.0
        },
        "zero_reward_count": 0
      },
      "canonical_task_outcome_summary": {
        "by_action": {
          "horizontal": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 1.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 1,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 1,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "local": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 0,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 0,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "vertical": {
            "canonical_completion_ratio": 0.5,
            "canonical_deadline_violation_ratio": 0.5,
            "canonical_drop_ratio": 0.5,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 2,
            "canonical_reward_total": -44.0,
            "canonical_task_count": 2,
            "canonical_task_mean_reward": -22.0,
            "canonical_terminal_task_count": 2,
            "completed_count": 1,
            "completion_reward_count": 1,
            "decision_count": 2,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_completion_latency_slots": 4.0,
            "mean_drop_latency_slots": 4.0,
            "mean_reward": -22.0,
            "mean_terminal_latency_slots": 4.0,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          }
        },
        "checkpoint_budget": 100,
        "overall": {
          "canonical_completion_count": 1,
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_count": 1,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 1,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_count": 2,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_task_count": 3,
          "canonical_task_mean_reward": -22.0,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 2,
          "canonical_unknown_count": 0,
          "completed_count": 1,
          "completion_reward_count": 1,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_reward": 0.0,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        },
        "reward_coverage": {
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "reward_available_count": 2
        }
      },
      "canonical_task_reconciliation": {
        "by_action": {
          "horizontal": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 1.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 1,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 1,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "local": {
            "canonical_completion_ratio": 0.0,
            "canonical_deadline_violation_ratio": 0.0,
            "canonical_drop_ratio": 0.0,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 0,
            "canonical_reward_total": 0.0,
            "canonical_task_count": 0,
            "canonical_task_mean_reward": 0.0,
            "canonical_terminal_task_count": 0,
            "completed_count": 0,
            "completion_reward_count": 0,
            "decision_count": 0,
            "double_count_detected": false,
            "drop_penalty_count": 0,
            "dropped_count": 0,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "mean_completion_latency_slots": null,
            "mean_drop_latency_slots": null,
            "mean_reward": 0.0,
            "mean_terminal_latency_slots": null,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 0,
            "raw_event_reward_total": 0.0,
            "raw_reward_emission_count": 0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 0,
            "terminal_transition_count": 0,
            "total_reward": 0.0,
            "unknown_count": 0
          },
          "vertical": {
            "canonical_completion_ratio": 0.5,
            "canonical_deadline_violation_ratio": 0.5,
            "canonical_drop_ratio": 0.5,
            "canonical_pending_ratio": 0.0,
            "canonical_reward_count": 2,
            "canonical_reward_total": -44.0,
            "canonical_task_count": 2,
            "canonical_task_mean_reward": -22.0,
            "canonical_terminal_task_count": 2,
            "completed_count": 1,
            "completion_reward_count": 1,
            "decision_count": 2,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_completion_latency_slots": 4.0,
            "mean_drop_latency_slots": 4.0,
            "mean_reward": -22.0,
            "mean_terminal_latency_slots": 4.0,
            "pending_at_horizon_count": 0,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          }
        },
        "checkpoint_budget": 100,
        "overall": {
          "canonical_completion_count": 1,
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_count": 1,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 1,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_count": 2,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_task_count": 3,
          "canonical_task_mean_reward": -22.0,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 2,
          "canonical_unknown_count": 0,
          "completed_count": 1,
          "completion_reward_count": 1,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_reward": 0.0,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        },
        "reward_coverage": {
          "raw_reward_event_count": 2,
          "raw_terminal_event_count": 3,
          "reward_available_count": 2
        }
      },
      "canonical_task_reward_count": 2,
      "canonical_task_reward_total": -44.0,
      "checkpoint_budget": 100,
      "completed_count": 1,
      "completed_task_count": 1,
      "completion_ratio": 0.3333333333333333,
      "deadline_violation_ratio": 0.3333333333333333,
      "decision_records_summary": {
        "decision_count": 3,
        "evaluation_action_distribution_source": "evaluation_episodes",
        "sample_records": [
          {
            "episode_id": 0,
            "selected_action": "vertical",
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "drop_ratio": 0.3333333333333333,
      "dropped_count": 1,
      "dropped_task_count": 1,
      "episode_length": 110,
      "episode_reward_totals": [
        -44.0
      ],
      "episode_summaries": [
        {
          "canonical_reward_total": -44.0,
          "completion_count": 1,
          "decision_count": 3,
          "drop_count": 1,
          "episode_id": 0,
          "pending_count": 1,
          "raw_reward_event_count": 2,
          "raw_reward_total": -44.0,
          "reward_recovered": true,
          "terminal_task_count": 2,
          "trace_id": "trace-0",
          "unknown_count": 0
        }
      ],
      "evaluation_action_by_episode_id": {
        "0": {
          "decision_count": 3
        }
      },
      "evaluation_action_by_trace_id": {
        "trace-0": {
          "decision_count": 3
        }
      },
      "evaluation_action_distribution": {
        "horizontal": 1,
        "local": 1,
        "vertical": 1
      },
      "evaluation_action_distribution_source": "evaluation_episodes",
      "evaluation_action_sequence_sample": [
        {
          "episode_id": 0,
          "selected_action": "vertical",
          "task_id": 1,
          "trace_id": "trace-0"
        }
      ],
      "evaluation_decision_count": 3,
      "evaluation_episode_count": 100,
      "evaluation_legal_action_mask_distribution": {
        "local=1|horizontal=1|vertical=1": 3
      },
      "evaluation_reward_summary": {
        "candidate_reproduction_supported": true,
        "canonical_task_count": 3,
        "canonical_task_reward_count": 2,
        "canonical_task_reward_total": -44.0,
        "completed_task_count": 1,
        "dropped_task_count": 1,
        "evaluation_episode_count": 100,
        "evaluation_on_training_traces": false,
        "mean_reward": -44.0,
        "pending_at_horizon_count": 1,
        "raw_event_reward_count": 2,
        "raw_event_reward_total": -44.0,
        "raw_reward_emission_count": 2,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 3,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_available_count": 2,
        "reward_bearing_transition_count": 2,
        "same_evaluation_trace_bank": true,
        "terminal_event_recovery_blocked": false,
        "terminal_transition_count": 2,
        "trace_bank_disjoint": true,
        "trace_bank_ids": {
          "evaluation": "eval-bank",
          "training": "train-bank"
        },
        "trace_ids": [
          "trace-0"
        ],
        "unknown_task_count": 0
      },
      "evaluation_trace_bank_id": "eval-bank",
      "mean_latency_slots": 4.0,
      "paper_aligned_diagnostic_metrics": {
        "canonical_completion_ratio": 0.3333333333333333,
        "canonical_deadline_violation_ratio": 0.3333333333333333,
        "canonical_drop_ratio": 0.3333333333333333,
        "canonical_mean_completion_latency_slots": 4.0,
        "canonical_mean_drop_latency_slots": 4.0,
        "canonical_mean_terminal_latency_slots": 4.0,
        "canonical_pending_ratio": 0.3333333333333333,
        "canonical_reward_per_decision": -14.666666666666666,
        "canonical_reward_per_task": -14.666666666666666,
        "canonical_tasks_per_decision": 1.0,
        "raw_reward_event_coverage_ratio": 1.0,
        "reward_reconciliation_status": "passed",
        "terminal_event_coverage_ratio": 1.5,
        "training_budget": 100
      },
      "pending_at_horizon_count": 1,
      "pending_task_count": 1,
      "per_action_outcome_summary": {
        "horizontal": {
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 0.0,
          "canonical_drop_ratio": 0.0,
          "canonical_pending_ratio": 1.0,
          "canonical_reward_count": 0,
          "canonical_reward_total": 0.0,
          "canonical_task_count": 1,
          "canonical_task_mean_reward": 0.0,
          "canonical_terminal_task_count": 0,
          "completed_count": 0,
          "completion_reward_count": 0,
          "decision_count": 1,
          "double_count_detected": false,
          "drop_penalty_count": 0,
          "dropped_count": 0,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "mean_completion_latency_slots": null,
          "mean_drop_latency_slots": null,
          "mean_reward": 0.0,
          "mean_terminal_latency_slots": null,
          "pending_at_horizon_count": 1,
          "raw_event_reward_count": 0,
          "raw_event_reward_total": 0.0,
          "raw_reward_emission_count": 0,
          "raw_terminal_event_count": 0,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 0,
          "terminal_transition_count": 0,
          "total_reward": 0.0,
          "unknown_count": 0
        },
        "local": {
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 0.0,
          "canonical_drop_ratio": 0.0,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_count": 0,
          "canonical_reward_total": 0.0,
          "canonical_task_count": 0,
          "canonical_task_mean_reward": 0.0,
          "canonical_terminal_task_count": 0,
          "completed_count": 0,
          "completion_reward_count": 0,
          "decision_count": 0,
          "double_count_detected": false,
          "drop_penalty_count": 0,
          "dropped_count": 0,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "mean_completion_latency_slots": null,
          "mean_drop_latency_slots": null,
          "mean_reward": 0.0,
          "mean_terminal_latency_slots": null,
          "pending_at_horizon_count": 0,
          "raw_event_reward_count": 0,
          "raw_event_reward_total": 0.0,
          "raw_reward_emission_count": 0,
          "raw_terminal_event_count": 0,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 0,
          "terminal_transition_count": 0,
          "total_reward": 0.0,
          "unknown_count": 0
        },
        "vertical": {
          "canonical_completion_ratio": 0.5,
          "canonical_deadline_violation_ratio": 0.5,
          "canonical_drop_ratio": 0.5,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_count": 2,
          "canonical_reward_total": -44.0,
          "canonical_task_count": 2,
          "canonical_task_mean_reward": -22.0,
          "canonical_terminal_task_count": 2,
          "completed_count": 1,
          "completion_reward_count": 1,
          "decision_count": 2,
          "double_count_detected": true,
          "drop_penalty_count": 1,
          "dropped_count": 1,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "mean_completion_latency_slots": 4.0,
          "mean_drop_latency_slots": 4.0,
          "mean_reward": -22.0,
          "mean_terminal_latency_slots": 4.0,
          "pending_at_horizon_count": 0,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_emission_count": 2,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_bearing_transition_count": 2,
          "terminal_transition_count": 2,
          "total_reward": -44.0,
          "unknown_count": 0
        }
      },
      "policy_kind": "candidate",
      "policy_name": "candidate_policy_at_100",
      "raw_event_reward_count": 2,
      "raw_event_reward_total": -44.0,
      "raw_lifecycle_terminal_event_count": 3,
      "raw_reward_event_count": 2,
      "raw_reward_event_recovery_blocked": false,
      "raw_reward_total": -44.0,
      "raw_terminal_event_count": 3,
      "raw_vs_canonical_reward_reconciliation": {
        "canonical_task_count": 3,
        "canonical_task_reward_count": 2,
        "canonical_task_reward_total": -44.0,
        "canonical_terminal_task_count": 2,
        "checkpoint_budget": 100,
        "duplicate_reward_event_count": 0,
        "duplicate_terminal_event_count": 1,
        "raw_event_reward_count": 2,
        "raw_event_reward_total": -44.0,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 3,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_reconciled": true,
        "terminal_event_recovery_blocked": false
      },
      "reconciliation": {
        "canonical_reward_decomposition": {
          "canonical_task_mean_reward_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -22.0
          },
          "canonical_task_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 2
          },
          "canonical_task_reward_total_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "completion_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 1
          },
          "drop_penalty_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 1
          },
          "nan_reward_count": 0,
          "raw_event_reward_count_by_action": {
            "horizontal": 0,
            "local": 0,
            "vertical": 2
          },
          "raw_event_reward_total_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "raw_vs_canonical_reward_delta_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": 0.0
          },
          "raw_vs_canonical_reward_delta_total": 0.0,
          "reward_available_count": 2,
          "reward_by_action": {
            "horizontal": 0.0,
            "local": 0.0,
            "vertical": -44.0
          },
          "reward_by_action_and_terminal_outcome": {
            "horizontal": {
              "completed": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              },
              "dropped": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              }
            },
            "local": {
              "completed": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              },
              "dropped": {
                "canonical_task_mean_reward": 0.0,
                "canonical_task_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "count": 0,
                "mean_reward": 0.0,
                "raw_event_reward_count": 0,
                "raw_event_reward_total": 0.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": 0.0
              }
            },
            "vertical": {
              "completed": {
                "canonical_task_mean_reward": -4.0,
                "canonical_task_reward_count": 1,
                "canonical_task_reward_total": -4.0,
                "count": 1,
                "mean_reward": -4.0,
                "raw_event_reward_count": 1,
                "raw_event_reward_total": -4.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": -4.0
              },
              "dropped": {
                "canonical_task_mean_reward": -40.0,
                "canonical_task_reward_count": 1,
                "canonical_task_reward_total": -40.0,
                "count": 1,
                "mean_reward": -40.0,
                "raw_event_reward_count": 1,
                "raw_event_reward_total": -40.0,
                "raw_vs_canonical_reward_delta": 0.0,
                "total_reward": -40.0
              }
            }
          },
          "reward_by_terminal_outcome": {
            "completed": -4.0,
            "dropped": -40.0
          },
          "zero_reward_count": 0
        },
        "canonical_task_outcome_sample": [
          {
            "arrival_slot": 0,
            "canonical_join_key": "trace-1:0:1",
            "canonical_reward": -40.0,
            "canonical_terminal_outcome": "dropped",
            "completion_or_drop_slot": 3,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "episode_id": 0,
            "first_decision_slot": 0,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -40.0,
            "raw_terminal_event_count": 2,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 1,
            "terminal_slot": 3,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 1,
            "canonical_join_key": "trace-1:0:2",
            "canonical_reward": -4.0,
            "canonical_terminal_outcome": "completed",
            "completion_or_drop_slot": 4,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 1,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -4.0,
            "raw_terminal_event_count": 1,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 2,
            "terminal_slot": 4,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 2,
            "canonical_join_key": "trace-1:0:3",
            "canonical_reward": 0.0,
            "canonical_terminal_outcome": "pending_at_horizon",
            "completion_or_drop_slot": null,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 2,
            "latency_slots": null,
            "raw_reward_event_count": 0,
            "raw_reward_total": 0.0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "horizontal",
            "task_id": 3,
            "terminal_slot": 5,
            "trace_id": "trace-1"
          }
        ],
        "canonical_task_outcome_summary": {
          "by_action": {
            "horizontal": {
              "canonical_completion_ratio": 0.0,
              "canonical_deadline_violation_ratio": 0.0,
              "canonical_drop_ratio": 0.0,
              "canonical_pending_ratio": 1.0,
              "canonical_reward_count": 0,
              "canonical_reward_total": 0.0,
              "canonical_task_count": 1,
              "canonical_task_mean_reward": 0.0,
              "canonical_terminal_task_count": 0,
              "completed_count": 0,
              "completion_reward_count": 0,
              "decision_count": 1,
              "double_count_detected": false,
              "drop_penalty_count": 0,
              "dropped_count": 0,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 0,
              "mean_completion_latency_slots": null,
              "mean_drop_latency_slots": null,
              "mean_reward": 0.0,
              "mean_terminal_latency_slots": null,
              "pending_at_horizon_count": 1,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_reward_emission_count": 0,
              "raw_terminal_event_count": 0,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 0,
              "terminal_transition_count": 0,
              "total_reward": 0.0,
              "unknown_count": 0
            },
            "local": {
              "canonical_completion_ratio": 0.0,
              "canonical_deadline_violation_ratio": 0.0,
              "canonical_drop_ratio": 0.0,
              "canonical_pending_ratio": 0.0,
              "canonical_reward_count": 0,
              "canonical_reward_total": 0.0,
              "canonical_task_count": 0,
              "canonical_task_mean_reward": 0.0,
              "canonical_terminal_task_count": 0,
              "completed_count": 0,
              "completion_reward_count": 0,
              "decision_count": 0,
              "double_count_detected": false,
              "drop_penalty_count": 0,
              "dropped_count": 0,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 0,
              "mean_completion_latency_slots": null,
              "mean_drop_latency_slots": null,
              "mean_reward": 0.0,
              "mean_terminal_latency_slots": null,
              "pending_at_horizon_count": 0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_reward_emission_count": 0,
              "raw_terminal_event_count": 0,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 0,
              "terminal_transition_count": 0,
              "total_reward": 0.0,
              "unknown_count": 0
            },
            "vertical": {
              "canonical_completion_ratio": 0.5,
              "canonical_deadline_violation_ratio": 0.5,
              "canonical_drop_ratio": 0.5,
              "canonical_pending_ratio": 0.0,
              "canonical_reward_count": 2,
              "canonical_reward_total": -44.0,
              "canonical_task_count": 2,
              "canonical_task_mean_reward": -22.0,
              "canonical_terminal_task_count": 2,
              "completed_count": 1,
              "completion_reward_count": 1,
              "decision_count": 2,
              "double_count_detected": true,
              "drop_penalty_count": 1,
              "dropped_count": 1,
              "duplicate_reward_event_count": 0,
              "duplicate_terminal_event_count": 1,
              "mean_completion_latency_slots": 4.0,
              "mean_drop_latency_slots": 4.0,
              "mean_reward": -22.0,
              "mean_terminal_latency_slots": 4.0,
              "pending_at_horizon_count": 0,
              "raw_event_reward_count": 2,
              "raw_event_reward_total": -44.0,
              "raw_reward_emission_count": 2,
              "raw_terminal_event_count": 3,
              "raw_vs_canonical_reward_delta": 0.0,
              "reward_bearing_transition_count": 2,
              "terminal_transition_count": 2,
              "total_reward": -44.0,
              "unknown_count": 0
            }
          },
          "checkpoint_budget": 100,
          "overall": {
            "canonical_completion_count": 1,
            "canonical_completion_ratio": 0.3333333333333333,
            "canonical_deadline_violation_ratio": 0.3333333333333333,
            "canonical_drop_count": 1,
            "canonical_drop_ratio": 0.3333333333333333,
            "canonical_mean_completion_latency_slots": 4.0,
            "canonical_mean_drop_latency_slots": 4.0,
            "canonical_mean_terminal_latency_slots": 4.0,
            "canonical_pending_count": 1,
            "canonical_pending_ratio": 0.3333333333333333,
            "canonical_reward_count": 2,
            "canonical_reward_per_decision": -14.666666666666666,
            "canonical_reward_per_task": -14.666666666666666,
            "canonical_task_count": 3,
            "canonical_task_mean_reward": -22.0,
            "canonical_task_reward_count": 2,
            "canonical_task_reward_total": -44.0,
            "canonical_tasks_per_decision": 1.0,
            "canonical_terminal_task_count": 2,
            "canonical_unknown_count": 0,
            "completed_count": 1,
            "completion_reward_count": 1,
            "double_count_detected": true,
            "drop_penalty_count": 1,
            "dropped_count": 1,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "mean_reward": 0.0,
            "pending_at_horizon_count": 1,
            "raw_event_reward_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_reward_emission_count": 2,
            "raw_reward_event_count": 2,
            "raw_terminal_event_count": 3,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_bearing_transition_count": 2,
            "terminal_transition_count": 2,
            "total_reward": -44.0,
            "unknown_count": 0
          },
          "reward_coverage": {
            "raw_reward_event_count": 2,
            "raw_terminal_event_count": 3,
            "reward_available_count": 2
          }
        },
        "canonical_task_outcomes": [
          {
            "arrival_slot": 0,
            "canonical_join_key": "trace-1:0:1",
            "canonical_reward": -40.0,
            "canonical_terminal_outcome": "dropped",
            "completion_or_drop_slot": 3,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 1,
            "episode_id": 0,
            "first_decision_slot": 0,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -40.0,
            "raw_terminal_event_count": 2,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 1,
            "terminal_slot": 3,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 1,
            "canonical_join_key": "trace-1:0:2",
            "canonical_reward": -4.0,
            "canonical_terminal_outcome": "completed",
            "completion_or_drop_slot": 4,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 1,
            "latency_slots": 4,
            "raw_reward_event_count": 1,
            "raw_reward_total": -4.0,
            "raw_terminal_event_count": 1,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "vertical",
            "task_id": 2,
            "terminal_slot": 4,
            "trace_id": "trace-1"
          },
          {
            "arrival_slot": 2,
            "canonical_join_key": "trace-1:0:3",
            "canonical_reward": 0.0,
            "canonical_terminal_outcome": "pending_at_horizon",
            "completion_or_drop_slot": null,
            "duplicate_reward_event_count": 0,
            "duplicate_terminal_event_count": 0,
            "episode_id": 0,
            "first_decision_slot": 2,
            "latency_slots": null,
            "raw_reward_event_count": 0,
            "raw_reward_total": 0.0,
            "raw_terminal_event_count": 0,
            "raw_vs_canonical_reward_delta": 0.0,
            "reconciled": true,
            "selected_action": "horizontal",
            "task_id": 3,
            "terminal_slot": 5,
            "trace_id": "trace-1"
          }
        ],
        "checkpoint_budget": 100,
        "decision_count": 3,
        "paper_aligned_diagnostic_metrics": {
          "canonical_completion_ratio": 0.3333333333333333,
          "canonical_deadline_violation_ratio": 0.3333333333333333,
          "canonical_drop_ratio": 0.3333333333333333,
          "canonical_mean_completion_latency_slots": 4.0,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_ratio": 0.3333333333333333,
          "canonical_reward_per_decision": -14.666666666666666,
          "canonical_reward_per_task": -14.666666666666666,
          "canonical_tasks_per_decision": 1.0,
          "raw_reward_event_coverage_ratio": 1.0,
          "reward_reconciliation_status": "passed",
          "terminal_event_coverage_ratio": 1.5,
          "training_budget": 100
        },
        "raw_vs_canonical_reward_reconciliation": {
          "canonical_task_count": 3,
          "canonical_task_reward_count": 2,
          "canonical_task_reward_total": -44.0,
          "canonical_terminal_task_count": 2,
          "checkpoint_budget": 100,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 1,
          "raw_event_reward_count": 2,
          "raw_event_reward_total": -44.0,
          "raw_reward_event_recovery_blocked": false,
          "raw_terminal_event_count": 3,
          "raw_vs_canonical_reward_delta": 0.0,
          "reward_reconciled": true,
          "terminal_event_recovery_blocked": false
        }
      },
      "reward_decomposition": {
        "canonical_task_mean_reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -22.0
        },
        "canonical_task_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "canonical_task_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "completion_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "drop_penalty_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 1
        },
        "nan_reward_count": 0,
        "raw_event_reward_count_by_action": {
          "horizontal": 0,
          "local": 0,
          "vertical": 2
        },
        "raw_event_reward_total_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "raw_vs_canonical_reward_delta_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": 0.0
        },
        "raw_vs_canonical_reward_delta_total": 0.0,
        "reward_available_count": 2,
        "reward_by_action": {
          "horizontal": 0.0,
          "local": 0.0,
          "vertical": -44.0
        },
        "reward_by_action_and_terminal_outcome": {
          "horizontal": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "local": {
            "completed": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            },
            "dropped": {
              "canonical_task_mean_reward": 0.0,
              "canonical_task_reward_count": 0,
              "canonical_task_reward_total": 0.0,
              "count": 0,
              "mean_reward": 0.0,
              "raw_event_reward_count": 0,
              "raw_event_reward_total": 0.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": 0.0
            }
          },
          "vertical": {
            "completed": {
              "canonical_task_mean_reward": -4.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -4.0,
              "count": 1,
              "mean_reward": -4.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -4.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -4.0
            },
            "dropped": {
              "canonical_task_mean_reward": -40.0,
              "canonical_task_reward_count": 1,
              "canonical_task_reward_total": -40.0,
              "count": 1,
              "mean_reward": -40.0,
              "raw_event_reward_count": 1,
              "raw_event_reward_total": -40.0,
              "raw_vs_canonical_reward_delta": 0.0,
              "total_reward": -40.0
            }
          }
        },
        "reward_by_terminal_outcome": {
          "completed": -4.0,
          "dropped": -40.0
        },
        "zero_reward_count": 0
      },
      "reward_event_records": {
        "raw_reward_event_recovery_blocked": false,
        "record_count": 2,
        "reward_available_count": 2,
        "sample_records": [
          {
            "episode_id": 0,
            "raw_reward": -40.0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "reward_reconciled": true,
      "reward_reconciliation_status": "passed",
      "reward_reconciliation_tolerance": 1e-09,
      "same_evaluation_trace_bank": true,
      "terminal_event_records": {
        "record_count": 3,
        "recovered_from_finalized_tasks": true,
        "sample_records": [
          {
            "episode_id": 0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "terminal_event_recovery_blocked": false,
      "unknown_count": 0
    }
  },
  "raw_event_reward_static_across_budget": false
}

## 8. Why Previous Outputs Were Static
{
  "aggregation_explanation": "Canonical task rewards are now reconciled against raw event rewards instead of replacing them.",
  "event_recovery_explanation": "Trace-enabled evaluation exposes reward_emitted lifecycle events and terminal finalized-task records.",
  "policy_behavior_explanation": "Candidate policy action distributions are still inspected separately from reward aggregation.",
  "why_previous_outputs_were_identical_or_static": "The fixed evaluator now separates event-level reward emission from canonical task-level reward, so the previous flat output was an aggregation artifact rather than a missing metric surface."
}

## 9. Whether Evaluation Reward Is Genuinely Static After Instrumentation
{
  "canonical_completion_rate_static_across_budget": true,
  "canonical_drop_rate_static_across_budget": true,
  "canonical_task_reward_static_across_budget": true,
  "evaluation_action_distribution_static_across_budget": false,
  "evaluation_reward_static_after_instrumentation": true,
  "raw_event_reward_static_across_budget": false
}

## 10. Whether Candidate Policy Collapses During Evaluation, Training, or Both
{
  "candidate_policy_vertical_collapse_in_evaluation": true,
  "candidate_policy_vertical_collapse_in_training_replay_window": true,
  "policy_affects_reward": "false",
  "policy_affects_terminal_outcomes": "false"
}

## 11. Whether Larger Training Is Still Blocked
{
  "remaining_blockers": []
}

## 12. Recommended Next Feature
State-reward alignment repair

## 13. Final Verdict
reward_emission_aggregation_repair_ready

## Checkpoint Metrics
| budget | cumulative episodes | eval decisions | optimizer steps | replay size | raw reward events | canonical reward tasks | reward reconciled |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 100 | 100 | 3 | 101 | 10000 | 2 | 2 | True |
| 150 | 150 | 3 | 102 | 10000 | 2 | 2 | True |
| 200 | 200 | 3 | 103 | 10000 | 2 | 2 | True |
| 500 | 500 | 3 | 104 | 10000 | 2 | 2 | True |

## Raw vs Canonical Reward Reconciliation
{
  "by_checkpoint": [
    {
      "canonical_task_count": 3,
      "canonical_task_reward_count": 2,
      "canonical_task_reward_total": -44.0,
      "canonical_terminal_task_count": 2,
      "checkpoint_budget": 100,
      "duplicate_reward_event_count": 0,
      "duplicate_terminal_event_count": 1,
      "raw_event_reward_count": 2,
      "raw_event_reward_total": -44.0,
      "raw_reward_event_recovery_blocked": false,
      "raw_terminal_event_count": 3,
      "raw_vs_canonical_reward_delta": 0.0,
      "reward_reconciled": true,
      "terminal_event_recovery_blocked": false
    },
    {
      "canonical_task_count": 3,
      "canonical_task_reward_count": 2,
      "canonical_task_reward_total": -44.0,
      "canonical_terminal_task_count": 2,
      "checkpoint_budget": 150,
      "duplicate_reward_event_count": 0,
      "duplicate_terminal_event_count": 1,
      "raw_event_reward_count": 2,
      "raw_event_reward_total": -44.0,
      "raw_reward_event_recovery_blocked": false,
      "raw_terminal_event_count": 3,
      "raw_vs_canonical_reward_delta": 0.0,
      "reward_reconciled": true,
      "terminal_event_recovery_blocked": false
    },
    {
      "canonical_task_count": 3,
      "canonical_task_reward_count": 2,
      "canonical_task_reward_total": -44.0,
      "canonical_terminal_task_count": 2,
      "checkpoint_budget": 200,
      "duplicate_reward_event_count": 0,
      "duplicate_terminal_event_count": 1,
      "raw_event_reward_count": 2,
      "raw_event_reward_total": -44.0,
      "raw_reward_event_recovery_blocked": false,
      "raw_terminal_event_count": 3,
      "raw_vs_canonical_reward_delta": 0.0,
      "reward_reconciled": true,
      "terminal_event_recovery_blocked": false
    },
    {
      "canonical_task_count": 3,
      "canonical_task_reward_count": 2,
      "canonical_task_reward_total": -44.0,
      "canonical_terminal_task_count": 2,
      "checkpoint_budget": 500,
      "duplicate_reward_event_count": 0,
      "duplicate_terminal_event_count": 1,
      "raw_event_reward_count": 2,
      "raw_event_reward_total": -44.0,
      "raw_reward_event_recovery_blocked": false,
      "raw_terminal_event_count": 3,
      "raw_vs_canonical_reward_delta": 0.0,
      "reward_reconciled": true,
      "terminal_event_recovery_blocked": false
    }
  ],
  "checkpoint_budgets": [
    100,
    150,
    200,
    500
  ],
  "raw_reward_event_recovery_blocked": false,
  "raw_vs_canonical_reward_delta_total": 0.0,
  "reward_reconciled": true,
  "terminal_event_recovery_blocked": false
}

## Paper-Aligned Diagnostic Metrics
{
  "by_checkpoint": [
    {
      "canonical_completion_ratio": 0.3333333333333333,
      "canonical_deadline_violation_ratio": 0.3333333333333333,
      "canonical_drop_ratio": 0.3333333333333333,
      "canonical_mean_completion_latency_slots": 4.0,
      "canonical_mean_drop_latency_slots": 4.0,
      "canonical_mean_terminal_latency_slots": 4.0,
      "canonical_pending_ratio": 0.3333333333333333,
      "canonical_reward_per_decision": -14.666666666666666,
      "canonical_reward_per_task": -14.666666666666666,
      "canonical_tasks_per_decision": 1.0,
      "raw_reward_event_coverage_ratio": 1.0,
      "reward_reconciliation_status": "passed",
      "terminal_event_coverage_ratio": 1.5,
      "training_budget": 100
    },
    {
      "canonical_completion_ratio": 0.3333333333333333,
      "canonical_deadline_violation_ratio": 0.3333333333333333,
      "canonical_drop_ratio": 0.3333333333333333,
      "canonical_mean_completion_latency_slots": 4.0,
      "canonical_mean_drop_latency_slots": 4.0,
      "canonical_mean_terminal_latency_slots": 4.0,
      "canonical_pending_ratio": 0.3333333333333333,
      "canonical_reward_per_decision": -14.666666666666666,
      "canonical_reward_per_task": -14.666666666666666,
      "canonical_tasks_per_decision": 1.0,
      "raw_reward_event_coverage_ratio": 1.0,
      "reward_reconciliation_status": "passed",
      "terminal_event_coverage_ratio": 1.5,
      "training_budget": 150
    },
    {
      "canonical_completion_ratio": 0.3333333333333333,
      "canonical_deadline_violation_ratio": 0.3333333333333333,
      "canonical_drop_ratio": 0.3333333333333333,
      "canonical_mean_completion_latency_slots": 4.0,
      "canonical_mean_drop_latency_slots": 4.0,
      "canonical_mean_terminal_latency_slots": 4.0,
      "canonical_pending_ratio": 0.3333333333333333,
      "canonical_reward_per_decision": -14.666666666666666,
      "canonical_reward_per_task": -14.666666666666666,
      "canonical_tasks_per_decision": 1.0,
      "raw_reward_event_coverage_ratio": 1.0,
      "reward_reconciliation_status": "passed",
      "terminal_event_coverage_ratio": 1.5,
      "training_budget": 200
    },
    {
      "canonical_completion_ratio": 0.3333333333333333,
      "canonical_deadline_violation_ratio": 0.3333333333333333,
      "canonical_drop_ratio": 0.3333333333333333,
      "canonical_mean_completion_latency_slots": 4.0,
      "canonical_mean_drop_latency_slots": 4.0,
      "canonical_mean_terminal_latency_slots": 4.0,
      "canonical_pending_ratio": 0.3333333333333333,
      "canonical_reward_per_decision": -14.666666666666666,
      "canonical_reward_per_task": -14.666666666666666,
      "canonical_tasks_per_decision": 1.0,
      "raw_reward_event_coverage_ratio": 1.0,
      "reward_reconciliation_status": "passed",
      "terminal_event_coverage_ratio": 1.5,
      "training_budget": 500
    }
  ],
  "checkpoint_budgets": [
    100,
    150,
    200,
    500
  ]
}

## Claim Safety
{
  "baseline_superiority_claim_made": false,
  "claim_safety_passed": true,
  "paper_reproduction_claim_made": false,
  "performance_superiority_claim_made": false
}

## Figure Manifest
{
  "figure_count": 5,
  "figure_directory": "artifacts/analysis/reward-emission-evaluation-metric-aggregation-repair/figures",
  "figure_files": [
    "figure_01_raw_vs_canonical_reward_reconciliation.png",
    "figure_02_reward_event_coverage_by_budget.png",
    "figure_03_terminal_event_coverage_by_budget.png",
    "figure_04_completion_drop_pending_ratios_by_budget.png",
    "figure_05_policy_effect_after_repair.png"
  ],
  "figures_generated": true
}
