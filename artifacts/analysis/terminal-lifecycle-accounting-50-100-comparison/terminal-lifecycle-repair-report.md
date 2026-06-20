# Terminal Lifecycle Accounting and 50/100 Comparison Repair

- feature_id: `067-terminal-lifecycle-accounting-50-100-comparison`
- final_verdict: `terminal_lifecycle_50_100_comparison_ready`
- diagnostic_decision: `fix_completion_path_next`
- recommended_next_feature: `Completion-path repair`

## 1. Feature 066 Prerequisite Verification
{
  "feature_066_prerequisite_verified": true,
  "prerequisite_artifacts": {
    "feature_066_report": {
      "details": "Feature 066 repair report validated as prerequisite",
      "exists": true,
      "path": "artifacts/analysis/reward-emission-evaluation-metric-aggregation-repair/reward-emission-aggregation-repair-report.json",
      "verified": true
    }
  },
  "prerequisite_tags": [
    {
      "details": "current branch matches Feature 067",
      "name": "branch",
      "verified": true
    },
    {
      "details": "current branch is not main",
      "name": "not_main",
      "verified": true
    },
    {
      "details": "Feature 066 report validated",
      "name": "feature_066_report_valid",
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
      "name": "base_branch_diff_approved",
      "verified": true
    }
  ]
}

## 2. Terminal Event Classification Result
{
  "by_checkpoint": [
    {
      "event_type_counts": {
        "deadline_expired": 100,
        "deadline_reached": 100,
        "reward_emitted": 100,
        "task_dropped": 100
      },
      "lifecycle_only_event_count": 100,
      "pending_event_count": 0,
      "reward_event_count": 100,
      "terminal_outcome_event_count": 100,
      "training_budget": 50
    },
    {
      "event_type_counts": {
        "deadline_expired": 100,
        "deadline_reached": 100,
        "reward_emitted": 100,
        "task_dropped": 100
      },
      "lifecycle_only_event_count": 100,
      "pending_event_count": 0,
      "reward_event_count": 100,
      "terminal_outcome_event_count": 100,
      "training_budget": 100
    }
  ],
  "checkpoint_budgets": [
    50,
    100
  ],
  "overall": {
    "event_type_counts": {
      "deadline_expired": 200,
      "deadline_reached": 200,
      "reward_emitted": 200,
      "task_dropped": 200
    },
    "lifecycle_only_event_count": 200,
    "pending_event_count": 0,
    "reward_event_count": 200,
    "terminal_outcome_event_count": 200
  },
  "sample_events": []
}

## 3. Canonical Terminal Task Summary
{
  "by_checkpoint": [
    {
      "overall": {
        "canonical_completion_count": 0,
        "canonical_completion_ratio": 0.0,
        "canonical_deadline_violation_ratio": 1.0,
        "canonical_drop_count": 100,
        "canonical_drop_ratio": 1.0,
        "canonical_mean_completion_latency_slots": null,
        "canonical_mean_drop_latency_slots": 4.0,
        "canonical_mean_terminal_latency_slots": 4.0,
        "canonical_pending_count": 0,
        "canonical_pending_ratio": 0.0,
        "canonical_reward_per_decision": -1.0,
        "canonical_reward_per_task": -1.0,
        "canonical_task_count": 100,
        "canonical_task_reward_count": 100,
        "canonical_task_reward_total": -100.0,
        "canonical_tasks_per_decision": 1.0,
        "canonical_terminal_task_count": 100,
        "canonical_unknown_count": 0,
        "double_count_detected": false,
        "duplicate_reward_event_count": 0,
        "duplicate_terminal_event_count": 0,
        "raw_event_reward_count": 100,
        "raw_event_reward_total": -100.0,
        "raw_reward_emission_count": 100,
        "raw_terminal_event_count": 100,
        "raw_vs_canonical_reward_delta": 0.0
      },
      "training_budget": 50
    },
    {
      "overall": {
        "canonical_completion_count": 0,
        "canonical_completion_ratio": 0.0,
        "canonical_deadline_violation_ratio": 1.0,
        "canonical_drop_count": 100,
        "canonical_drop_ratio": 1.0,
        "canonical_mean_completion_latency_slots": null,
        "canonical_mean_drop_latency_slots": 4.0,
        "canonical_mean_terminal_latency_slots": 4.0,
        "canonical_pending_count": 0,
        "canonical_pending_ratio": 0.0,
        "canonical_reward_per_decision": -1.0,
        "canonical_reward_per_task": -1.0,
        "canonical_task_count": 100,
        "canonical_task_reward_count": 100,
        "canonical_task_reward_total": -100.0,
        "canonical_tasks_per_decision": 1.0,
        "canonical_terminal_task_count": 100,
        "canonical_unknown_count": 0,
        "double_count_detected": false,
        "duplicate_reward_event_count": 0,
        "duplicate_terminal_event_count": 0,
        "raw_event_reward_count": 100,
        "raw_event_reward_total": -100.0,
        "raw_reward_emission_count": 100,
        "raw_terminal_event_count": 100,
        "raw_vs_canonical_reward_delta": 0.0
      },
      "training_budget": 100
    }
  ],
  "checkpoint_budgets": [
    50,
    100
  ],
  "overall": {
    "canonical_completion_count": 0,
    "canonical_drop_count": 200,
    "canonical_pending_count": 0,
    "canonical_task_count": 200,
    "canonical_task_reward_count": 200,
    "canonical_task_reward_total": -200.0,
    "canonical_terminal_task_count": 200,
    "canonical_unknown_count": 0,
    "raw_reward_event_count": 200,
    "raw_terminal_event_count": 200,
    "raw_vs_canonical_reward_delta": 0.0
  },
  "sample_task_outcomes": []
}

## 4. Raw vs Canonical Terminal Reconciliation
{
  "by_checkpoint": [
    {
      "canonical_reward_event_count": 100,
      "canonical_task_reward_total": -100.0,
      "canonical_terminal_task_count": 100,
      "duplicate_terminal_event_count": 0,
      "raw_event_reward_total": -100.0,
      "raw_reward_event_count": 100,
      "raw_reward_event_recovery_blocked": false,
      "raw_terminal_event_count": 100,
      "raw_vs_canonical_reward_delta": 0.0,
      "reward_event_coverage_ratio": 1.0,
      "reward_reconciled": true,
      "terminal_event_coverage_ratio": 1.0,
      "terminal_event_recovery_blocked": false,
      "terminal_reconciled": true,
      "training_budget": 50
    },
    {
      "canonical_reward_event_count": 100,
      "canonical_task_reward_total": -100.0,
      "canonical_terminal_task_count": 100,
      "duplicate_terminal_event_count": 0,
      "raw_event_reward_total": -100.0,
      "raw_reward_event_count": 100,
      "raw_reward_event_recovery_blocked": false,
      "raw_terminal_event_count": 100,
      "raw_vs_canonical_reward_delta": 0.0,
      "reward_event_coverage_ratio": 1.0,
      "reward_reconciled": true,
      "terminal_event_coverage_ratio": 1.0,
      "terminal_event_recovery_blocked": false,
      "terminal_reconciled": true,
      "training_budget": 100
    }
  ],
  "checkpoint_budgets": [
    50,
    100
  ],
  "overall": {
    "canonical_reward_event_count": 200,
    "canonical_task_reward_total": -200.0,
    "canonical_terminal_task_count": 200,
    "duplicate_terminal_event_count": 0,
    "raw_event_reward_total": -200.0,
    "raw_reward_event_count": 200,
    "raw_reward_event_recovery_blocked": false,
    "raw_terminal_event_count": 200,
    "raw_vs_canonical_reward_delta": 0.0,
    "reward_event_coverage_ratio": 1.0,
    "reward_reconciled": true,
    "terminal_event_coverage_ratio": 1.0,
    "terminal_event_recovery_blocked": false,
    "terminal_reconciled": true
  }
}

## 5. Reward Reconciliation After Terminal Repair
{
  "by_checkpoint": [
    {
      "canonical_task_reward_count": 100,
      "canonical_task_reward_total": -100.0,
      "checkpoint_budget": 50,
      "raw_event_reward_count": 100,
      "raw_event_reward_total": -100.0,
      "raw_reward_event_recovery_blocked": false,
      "raw_vs_canonical_reward_delta": 0.0,
      "reward_reconciled": true,
      "reward_reconciliation_tolerance": 1e-09,
      "terminal_event_recovery_blocked": false,
      "training_budget": 50
    },
    {
      "canonical_task_reward_count": 100,
      "canonical_task_reward_total": -100.0,
      "checkpoint_budget": 100,
      "raw_event_reward_count": 100,
      "raw_event_reward_total": -100.0,
      "raw_reward_event_recovery_blocked": false,
      "raw_vs_canonical_reward_delta": 0.0,
      "reward_reconciled": true,
      "reward_reconciliation_tolerance": 1e-09,
      "terminal_event_recovery_blocked": false,
      "training_budget": 100
    }
  ],
  "checkpoint_budgets": [
    50,
    100
  ],
  "overall": {
    "canonical_task_reward_count": 200,
    "canonical_task_reward_total": -200.0,
    "raw_event_reward_count": 200,
    "raw_event_reward_total": -200.0,
    "raw_reward_event_recovery_blocked": false,
    "raw_vs_canonical_reward_delta": 0.0,
    "reward_reconciled": true,
    "reward_reconciliation_tolerance": 1e-09,
    "terminal_event_recovery_blocked": false
  }
}

## 6. Completion Path Audit
{
  "by_checkpoint": [
    {
      "completed_canonical_task_count": 0,
      "deadline_expired_event_count": 100,
      "deadline_reached_event_count": 100,
      "deadline_reached_then_task_dropped_duplicate_detected": true,
      "execution_completed_but_no_task_completed_detected": false,
      "execution_completed_event_count": 0,
      "pending_at_horizon_count": 0,
      "reward_emitted_event_count": 100,
      "reward_emitted_without_terminal_outcome_detected": false,
      "task_completed_but_no_reward_detected": false,
      "task_completed_event_count": 0,
      "task_dropped_event_count": 100,
      "terminal_outcome_without_reward_detected": false,
      "training_budget": 50
    },
    {
      "completed_canonical_task_count": 0,
      "deadline_expired_event_count": 100,
      "deadline_reached_event_count": 100,
      "deadline_reached_then_task_dropped_duplicate_detected": true,
      "execution_completed_but_no_task_completed_detected": false,
      "execution_completed_event_count": 0,
      "pending_at_horizon_count": 0,
      "reward_emitted_event_count": 100,
      "reward_emitted_without_terminal_outcome_detected": false,
      "task_completed_but_no_reward_detected": false,
      "task_completed_event_count": 0,
      "task_dropped_event_count": 100,
      "terminal_outcome_without_reward_detected": false,
      "training_budget": 100
    }
  ],
  "by_policy": {
    "candidate_policy_at_100": {
      "completed_canonical_task_count": 0,
      "deadline_expired_event_count": 100,
      "deadline_reached_event_count": 100,
      "deadline_reached_then_task_dropped_duplicate_detected": true,
      "execution_completed_but_no_task_completed_detected": false,
      "execution_completed_event_count": 0,
      "pending_at_horizon_count": 0,
      "reward_emitted_event_count": 100,
      "reward_emitted_without_terminal_outcome_detected": false,
      "task_completed_but_no_reward_detected": false,
      "task_completed_event_count": 0,
      "task_dropped_event_count": 100,
      "terminal_outcome_without_reward_detected": false
    },
    "candidate_policy_at_50": {
      "completed_canonical_task_count": 0,
      "deadline_expired_event_count": 100,
      "deadline_reached_event_count": 100,
      "deadline_reached_then_task_dropped_duplicate_detected": true,
      "execution_completed_but_no_task_completed_detected": false,
      "execution_completed_event_count": 0,
      "pending_at_horizon_count": 0,
      "reward_emitted_event_count": 100,
      "reward_emitted_without_terminal_outcome_detected": false,
      "task_completed_but_no_reward_detected": false,
      "task_completed_event_count": 0,
      "task_dropped_event_count": 100,
      "terminal_outcome_without_reward_detected": false
    },
    "fixed_horizontal_policy": {
      "completed_canonical_task_count": 0,
      "deadline_expired_event_count": 100,
      "deadline_reached_event_count": 100,
      "deadline_reached_then_task_dropped_duplicate_detected": true,
      "execution_completed_but_no_task_completed_detected": false,
      "execution_completed_event_count": 0,
      "pending_at_horizon_count": 0,
      "reward_emitted_event_count": 100,
      "reward_emitted_without_terminal_outcome_detected": false,
      "task_completed_but_no_reward_detected": false,
      "task_completed_event_count": 0,
      "task_dropped_event_count": 100,
      "terminal_outcome_without_reward_detected": false
    },
    "fixed_local_policy": {
      "completed_canonical_task_count": 0,
      "deadline_expired_event_count": 100,
      "deadline_reached_event_count": 100,
      "deadline_reached_then_task_dropped_duplicate_detected": true,
      "execution_completed_but_no_task_completed_detected": false,
      "execution_completed_event_count": 0,
      "pending_at_horizon_count": 0,
      "reward_emitted_event_count": 100,
      "reward_emitted_without_terminal_outcome_detected": false,
      "task_completed_but_no_reward_detected": false,
      "task_completed_event_count": 0,
      "task_dropped_event_count": 100,
      "terminal_outcome_without_reward_detected": false
    },
    "fixed_vertical_policy": {
      "completed_canonical_task_count": 0,
      "deadline_expired_event_count": 100,
      "deadline_reached_event_count": 100,
      "deadline_reached_then_task_dropped_duplicate_detected": true,
      "execution_completed_but_no_task_completed_detected": false,
      "execution_completed_event_count": 0,
      "pending_at_horizon_count": 0,
      "reward_emitted_event_count": 100,
      "reward_emitted_without_terminal_outcome_detected": false,
      "task_completed_but_no_reward_detected": false,
      "task_completed_event_count": 0,
      "task_dropped_event_count": 100,
      "terminal_outcome_without_reward_detected": false
    },
    "random_legal_policy": {
      "completed_canonical_task_count": 0,
      "deadline_expired_event_count": 100,
      "deadline_reached_event_count": 100,
      "deadline_reached_then_task_dropped_duplicate_detected": true,
      "execution_completed_but_no_task_completed_detected": false,
      "execution_completed_event_count": 0,
      "pending_at_horizon_count": 0,
      "reward_emitted_event_count": 100,
      "reward_emitted_without_terminal_outcome_detected": false,
      "task_completed_but_no_reward_detected": false,
      "task_completed_event_count": 0,
      "task_dropped_event_count": 100,
      "terminal_outcome_without_reward_detected": false
    }
  }
}

## 7. Policy-Effect Diagnostic Result
{
  "candidate_action_distribution_changed_by_budget": false,
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
  "evaluation_reward_static_after_terminal_repair": true,
  "evaluation_trace_bank_id": "eval-bank",
  "policy_affects_reward": "false",
  "policy_affects_terminal_outcomes": "false",
  "policy_results": {
    "candidate_policy_at_100": {
      "candidate_policy_vertical_share": 1.0,
      "canonical_terminal_task_summary": {
        "overall": {
          "canonical_completion_count": 0,
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 1.0,
          "canonical_drop_count": 100,
          "canonical_drop_ratio": 1.0,
          "canonical_mean_completion_latency_slots": null,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 0,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_per_decision": -1.0,
          "canonical_reward_per_task": -1.0,
          "canonical_task_count": 100,
          "canonical_task_reward_count": 100,
          "canonical_task_reward_total": -100.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 100,
          "canonical_unknown_count": 0,
          "double_count_detected": false,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "raw_event_reward_count": 100,
          "raw_event_reward_total": -100.0,
          "raw_reward_emission_count": 100,
          "raw_terminal_event_count": 100,
          "raw_vs_canonical_reward_delta": 0.0
        }
      },
      "checkpoint_budget": 100,
      "completion_path_audit": {
        "completed_canonical_task_count": 0,
        "deadline_expired_event_count": 100,
        "deadline_reached_event_count": 100,
        "deadline_reached_then_task_dropped_duplicate_detected": true,
        "execution_completed_but_no_task_completed_detected": false,
        "execution_completed_event_count": 0,
        "pending_at_horizon_count": 0,
        "reward_emitted_event_count": 100,
        "reward_emitted_without_terminal_outcome_detected": false,
        "task_completed_but_no_reward_detected": false,
        "task_completed_event_count": 0,
        "task_dropped_event_count": 100,
        "terminal_outcome_without_reward_detected": false
      },
      "decision_records_summary": {
        "decision_count": 100,
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
      "episode_length": 110,
      "episode_reward_totals": [
        -100.0
      ],
      "episode_summaries": [
        {
          "canonical_reward_total": -100.0,
          "completion_count": 0,
          "decision_count": 100,
          "drop_count": 100,
          "episode_id": 0,
          "pending_count": 0,
          "raw_reward_event_count": 100,
          "raw_reward_total": -100.0,
          "reward_recovered": true,
          "terminal_task_count": 100,
          "trace_id": "trace-0",
          "unknown_count": 0
        }
      ],
      "evaluation_action_by_episode_id": {
        "0": {
          "decision_count": 100
        }
      },
      "evaluation_action_by_trace_id": {
        "trace-0": {
          "decision_count": 100
        }
      },
      "evaluation_action_distribution": {
        "horizontal": 0,
        "local": 0,
        "vertical": 100
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
      "evaluation_decision_count": 100,
      "evaluation_episode_count": 100,
      "evaluation_legal_action_mask_distribution": {
        "local=1|horizontal=1|vertical=1": 100
      },
      "evaluation_reward_summary": {
        "canonical_task_count": 100,
        "completed_task_count": 0,
        "dropped_task_count": 100,
        "evaluation_episode_count": 100,
        "mean_reward": -100.0,
        "pending_at_horizon_count": 0,
        "reward_bearing_transition_count": 100,
        "terminal_transition_count": 100,
        "unknown_task_count": 0
      },
      "evaluation_trace_bank_id": "eval-bank",
      "paper_aligned_diagnostic_metrics": {
        "canonical_completion_ratio": 0.0,
        "canonical_deadline_violation_ratio": 1.0,
        "canonical_drop_ratio": 1.0,
        "canonical_mean_completion_latency_slots": null,
        "canonical_mean_drop_latency_slots": 4.0,
        "canonical_mean_terminal_latency_slots": 4.0,
        "canonical_pending_ratio": 0.0,
        "canonical_reward_per_decision": -1.0,
        "canonical_reward_per_task": -1.0,
        "canonical_tasks_per_decision": 1.0,
        "checkpoint_budget": 100,
        "raw_reward_event_coverage_ratio": 1.0,
        "reward_reconciliation_status": "passed",
        "terminal_event_coverage_ratio": 1.0
      },
      "policy_kind": "candidate",
      "policy_name": "candidate_policy_at_100",
      "raw_reward_event_count": 100,
      "raw_reward_event_recovery_blocked": false,
      "raw_reward_total": -100.0,
      "raw_terminal_event_count": 100,
      "raw_vs_canonical_terminal_reconciliation": {
        "canonical_reward_event_count": 100,
        "canonical_task_reward_total": -100.0,
        "canonical_terminal_task_count": 100,
        "duplicate_terminal_event_count": 0,
        "raw_event_reward_total": -100.0,
        "raw_reward_event_count": 100,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 100,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_event_coverage_ratio": 1.0,
        "reward_reconciled": true,
        "terminal_event_coverage_ratio": 1.0,
        "terminal_event_recovery_blocked": false,
        "terminal_reconciled": true
      },
      "reward_event_records": {
        "raw_reward_event_recovery_blocked": false,
        "record_count": 100,
        "reward_available_count": 100,
        "sample_records": [
          {
            "episode_id": 0,
            "raw_reward": -1.0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "reward_reconciliation_after_terminal_repair": {
        "canonical_task_reward_count": 100,
        "canonical_task_reward_total": -100.0,
        "checkpoint_budget": 100,
        "raw_event_reward_count": 100,
        "raw_event_reward_total": -100.0,
        "raw_reward_event_recovery_blocked": false,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_reconciled": true,
        "reward_reconciliation_tolerance": 1e-09,
        "terminal_event_recovery_blocked": false
      },
      "reward_reconciliation_tolerance": 1e-09,
      "same_evaluation_trace_bank": true,
      "task_records": {},
      "terminal_event_classification": {
        "overall": {
          "event_type_counts": {
            "deadline_expired": 100,
            "deadline_reached": 100,
            "reward_emitted": 100,
            "task_dropped": 100
          },
          "lifecycle_only_event_count": 100,
          "pending_event_count": 0,
          "reward_event_count": 100,
          "terminal_outcome_event_count": 100
        }
      },
      "terminal_event_records": {
        "record_count": 100,
        "recovered_from_finalized_tasks": true,
        "sample_records": [
          {
            "episode_id": 0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "terminal_event_recovery_blocked": false
    },
    "candidate_policy_at_50": {
      "candidate_policy_vertical_share": 0.9,
      "canonical_terminal_task_summary": {
        "overall": {
          "canonical_completion_count": 0,
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 1.0,
          "canonical_drop_count": 100,
          "canonical_drop_ratio": 1.0,
          "canonical_mean_completion_latency_slots": null,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 0,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_per_decision": -1.0,
          "canonical_reward_per_task": -1.0,
          "canonical_task_count": 100,
          "canonical_task_reward_count": 100,
          "canonical_task_reward_total": -100.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 100,
          "canonical_unknown_count": 0,
          "double_count_detected": false,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "raw_event_reward_count": 100,
          "raw_event_reward_total": -100.0,
          "raw_reward_emission_count": 100,
          "raw_terminal_event_count": 100,
          "raw_vs_canonical_reward_delta": 0.0
        }
      },
      "checkpoint_budget": 50,
      "completion_path_audit": {
        "completed_canonical_task_count": 0,
        "deadline_expired_event_count": 100,
        "deadline_reached_event_count": 100,
        "deadline_reached_then_task_dropped_duplicate_detected": true,
        "execution_completed_but_no_task_completed_detected": false,
        "execution_completed_event_count": 0,
        "pending_at_horizon_count": 0,
        "reward_emitted_event_count": 100,
        "reward_emitted_without_terminal_outcome_detected": false,
        "task_completed_but_no_reward_detected": false,
        "task_completed_event_count": 0,
        "task_dropped_event_count": 100,
        "terminal_outcome_without_reward_detected": false
      },
      "decision_records_summary": {
        "decision_count": 100,
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
      "episode_length": 110,
      "episode_reward_totals": [
        -100.0
      ],
      "episode_summaries": [
        {
          "canonical_reward_total": -100.0,
          "completion_count": 0,
          "decision_count": 100,
          "drop_count": 100,
          "episode_id": 0,
          "pending_count": 0,
          "raw_reward_event_count": 100,
          "raw_reward_total": -100.0,
          "reward_recovered": true,
          "terminal_task_count": 100,
          "trace_id": "trace-0",
          "unknown_count": 0
        }
      ],
      "evaluation_action_by_episode_id": {
        "0": {
          "decision_count": 100
        }
      },
      "evaluation_action_by_trace_id": {
        "trace-0": {
          "decision_count": 100
        }
      },
      "evaluation_action_distribution": {
        "horizontal": 5,
        "local": 5,
        "vertical": 90
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
      "evaluation_decision_count": 100,
      "evaluation_episode_count": 100,
      "evaluation_legal_action_mask_distribution": {
        "local=1|horizontal=1|vertical=1": 100
      },
      "evaluation_reward_summary": {
        "canonical_task_count": 100,
        "completed_task_count": 0,
        "dropped_task_count": 100,
        "evaluation_episode_count": 100,
        "mean_reward": -100.0,
        "pending_at_horizon_count": 0,
        "reward_bearing_transition_count": 100,
        "terminal_transition_count": 100,
        "unknown_task_count": 0
      },
      "evaluation_trace_bank_id": "eval-bank",
      "paper_aligned_diagnostic_metrics": {
        "canonical_completion_ratio": 0.0,
        "canonical_deadline_violation_ratio": 1.0,
        "canonical_drop_ratio": 1.0,
        "canonical_mean_completion_latency_slots": null,
        "canonical_mean_drop_latency_slots": 4.0,
        "canonical_mean_terminal_latency_slots": 4.0,
        "canonical_pending_ratio": 0.0,
        "canonical_reward_per_decision": -1.0,
        "canonical_reward_per_task": -1.0,
        "canonical_tasks_per_decision": 1.0,
        "checkpoint_budget": 50,
        "raw_reward_event_coverage_ratio": 1.0,
        "reward_reconciliation_status": "passed",
        "terminal_event_coverage_ratio": 1.0
      },
      "policy_kind": "candidate",
      "policy_name": "candidate_policy_at_50",
      "raw_reward_event_count": 100,
      "raw_reward_event_recovery_blocked": false,
      "raw_reward_total": -100.0,
      "raw_terminal_event_count": 100,
      "raw_vs_canonical_terminal_reconciliation": {
        "canonical_reward_event_count": 100,
        "canonical_task_reward_total": -100.0,
        "canonical_terminal_task_count": 100,
        "duplicate_terminal_event_count": 0,
        "raw_event_reward_total": -100.0,
        "raw_reward_event_count": 100,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 100,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_event_coverage_ratio": 1.0,
        "reward_reconciled": true,
        "terminal_event_coverage_ratio": 1.0,
        "terminal_event_recovery_blocked": false,
        "terminal_reconciled": true
      },
      "reward_event_records": {
        "raw_reward_event_recovery_blocked": false,
        "record_count": 100,
        "reward_available_count": 100,
        "sample_records": [
          {
            "episode_id": 0,
            "raw_reward": -1.0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "reward_reconciliation_after_terminal_repair": {
        "canonical_task_reward_count": 100,
        "canonical_task_reward_total": -100.0,
        "checkpoint_budget": 50,
        "raw_event_reward_count": 100,
        "raw_event_reward_total": -100.0,
        "raw_reward_event_recovery_blocked": false,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_reconciled": true,
        "reward_reconciliation_tolerance": 1e-09,
        "terminal_event_recovery_blocked": false
      },
      "reward_reconciliation_tolerance": 1e-09,
      "same_evaluation_trace_bank": true,
      "task_records": {},
      "terminal_event_classification": {
        "overall": {
          "event_type_counts": {
            "deadline_expired": 100,
            "deadline_reached": 100,
            "reward_emitted": 100,
            "task_dropped": 100
          },
          "lifecycle_only_event_count": 100,
          "pending_event_count": 0,
          "reward_event_count": 100,
          "terminal_outcome_event_count": 100
        }
      },
      "terminal_event_records": {
        "record_count": 100,
        "recovered_from_finalized_tasks": true,
        "sample_records": [
          {
            "episode_id": 0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "terminal_event_recovery_blocked": false
    },
    "fixed_horizontal_policy": {
      "candidate_policy_vertical_share": 1.0,
      "canonical_terminal_task_summary": {
        "overall": {
          "canonical_completion_count": 0,
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 1.0,
          "canonical_drop_count": 100,
          "canonical_drop_ratio": 1.0,
          "canonical_mean_completion_latency_slots": null,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 0,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_per_decision": -1.0,
          "canonical_reward_per_task": -1.0,
          "canonical_task_count": 100,
          "canonical_task_reward_count": 100,
          "canonical_task_reward_total": -100.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 100,
          "canonical_unknown_count": 0,
          "double_count_detected": false,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "raw_event_reward_count": 100,
          "raw_event_reward_total": -100.0,
          "raw_reward_emission_count": 100,
          "raw_terminal_event_count": 100,
          "raw_vs_canonical_reward_delta": 0.0
        }
      },
      "checkpoint_budget": 100,
      "completion_path_audit": {
        "completed_canonical_task_count": 0,
        "deadline_expired_event_count": 100,
        "deadline_reached_event_count": 100,
        "deadline_reached_then_task_dropped_duplicate_detected": true,
        "execution_completed_but_no_task_completed_detected": false,
        "execution_completed_event_count": 0,
        "pending_at_horizon_count": 0,
        "reward_emitted_event_count": 100,
        "reward_emitted_without_terminal_outcome_detected": false,
        "task_completed_but_no_reward_detected": false,
        "task_completed_event_count": 0,
        "task_dropped_event_count": 100,
        "terminal_outcome_without_reward_detected": false
      },
      "decision_records_summary": {
        "decision_count": 100,
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
      "episode_length": 110,
      "episode_reward_totals": [
        -100.0
      ],
      "episode_summaries": [
        {
          "canonical_reward_total": -100.0,
          "completion_count": 0,
          "decision_count": 100,
          "drop_count": 100,
          "episode_id": 0,
          "pending_count": 0,
          "raw_reward_event_count": 100,
          "raw_reward_total": -100.0,
          "reward_recovered": true,
          "terminal_task_count": 100,
          "trace_id": "trace-0",
          "unknown_count": 0
        }
      ],
      "evaluation_action_by_episode_id": {
        "0": {
          "decision_count": 100
        }
      },
      "evaluation_action_by_trace_id": {
        "trace-0": {
          "decision_count": 100
        }
      },
      "evaluation_action_distribution": {
        "horizontal": 0,
        "local": 0,
        "vertical": 100
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
      "evaluation_decision_count": 100,
      "evaluation_episode_count": 100,
      "evaluation_legal_action_mask_distribution": {
        "local=1|horizontal=1|vertical=1": 100
      },
      "evaluation_reward_summary": {
        "canonical_task_count": 100,
        "completed_task_count": 0,
        "dropped_task_count": 100,
        "evaluation_episode_count": 100,
        "mean_reward": -100.0,
        "pending_at_horizon_count": 0,
        "reward_bearing_transition_count": 100,
        "terminal_transition_count": 100,
        "unknown_task_count": 0
      },
      "evaluation_trace_bank_id": "eval-bank",
      "paper_aligned_diagnostic_metrics": {
        "canonical_completion_ratio": 0.0,
        "canonical_deadline_violation_ratio": 1.0,
        "canonical_drop_ratio": 1.0,
        "canonical_mean_completion_latency_slots": null,
        "canonical_mean_drop_latency_slots": 4.0,
        "canonical_mean_terminal_latency_slots": 4.0,
        "canonical_pending_ratio": 0.0,
        "canonical_reward_per_decision": -1.0,
        "canonical_reward_per_task": -1.0,
        "canonical_tasks_per_decision": 1.0,
        "checkpoint_budget": 100,
        "raw_reward_event_coverage_ratio": 1.0,
        "reward_reconciliation_status": "passed",
        "terminal_event_coverage_ratio": 1.0
      },
      "policy_kind": "candidate",
      "policy_name": "candidate_policy_at_100",
      "raw_reward_event_count": 100,
      "raw_reward_event_recovery_blocked": false,
      "raw_reward_total": -100.0,
      "raw_terminal_event_count": 100,
      "raw_vs_canonical_terminal_reconciliation": {
        "canonical_reward_event_count": 100,
        "canonical_task_reward_total": -100.0,
        "canonical_terminal_task_count": 100,
        "duplicate_terminal_event_count": 0,
        "raw_event_reward_total": -100.0,
        "raw_reward_event_count": 100,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 100,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_event_coverage_ratio": 1.0,
        "reward_reconciled": true,
        "terminal_event_coverage_ratio": 1.0,
        "terminal_event_recovery_blocked": false,
        "terminal_reconciled": true
      },
      "reward_event_records": {
        "raw_reward_event_recovery_blocked": false,
        "record_count": 100,
        "reward_available_count": 100,
        "sample_records": [
          {
            "episode_id": 0,
            "raw_reward": -1.0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "reward_reconciliation_after_terminal_repair": {
        "canonical_task_reward_count": 100,
        "canonical_task_reward_total": -100.0,
        "checkpoint_budget": 100,
        "raw_event_reward_count": 100,
        "raw_event_reward_total": -100.0,
        "raw_reward_event_recovery_blocked": false,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_reconciled": true,
        "reward_reconciliation_tolerance": 1e-09,
        "terminal_event_recovery_blocked": false
      },
      "reward_reconciliation_tolerance": 1e-09,
      "same_evaluation_trace_bank": true,
      "task_records": {},
      "terminal_event_classification": {
        "overall": {
          "event_type_counts": {
            "deadline_expired": 100,
            "deadline_reached": 100,
            "reward_emitted": 100,
            "task_dropped": 100
          },
          "lifecycle_only_event_count": 100,
          "pending_event_count": 0,
          "reward_event_count": 100,
          "terminal_outcome_event_count": 100
        }
      },
      "terminal_event_records": {
        "record_count": 100,
        "recovered_from_finalized_tasks": true,
        "sample_records": [
          {
            "episode_id": 0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "terminal_event_recovery_blocked": false
    },
    "fixed_local_policy": {
      "candidate_policy_vertical_share": 1.0,
      "canonical_terminal_task_summary": {
        "overall": {
          "canonical_completion_count": 0,
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 1.0,
          "canonical_drop_count": 100,
          "canonical_drop_ratio": 1.0,
          "canonical_mean_completion_latency_slots": null,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 0,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_per_decision": -1.0,
          "canonical_reward_per_task": -1.0,
          "canonical_task_count": 100,
          "canonical_task_reward_count": 100,
          "canonical_task_reward_total": -100.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 100,
          "canonical_unknown_count": 0,
          "double_count_detected": false,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "raw_event_reward_count": 100,
          "raw_event_reward_total": -100.0,
          "raw_reward_emission_count": 100,
          "raw_terminal_event_count": 100,
          "raw_vs_canonical_reward_delta": 0.0
        }
      },
      "checkpoint_budget": 100,
      "completion_path_audit": {
        "completed_canonical_task_count": 0,
        "deadline_expired_event_count": 100,
        "deadline_reached_event_count": 100,
        "deadline_reached_then_task_dropped_duplicate_detected": true,
        "execution_completed_but_no_task_completed_detected": false,
        "execution_completed_event_count": 0,
        "pending_at_horizon_count": 0,
        "reward_emitted_event_count": 100,
        "reward_emitted_without_terminal_outcome_detected": false,
        "task_completed_but_no_reward_detected": false,
        "task_completed_event_count": 0,
        "task_dropped_event_count": 100,
        "terminal_outcome_without_reward_detected": false
      },
      "decision_records_summary": {
        "decision_count": 100,
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
      "episode_length": 110,
      "episode_reward_totals": [
        -100.0
      ],
      "episode_summaries": [
        {
          "canonical_reward_total": -100.0,
          "completion_count": 0,
          "decision_count": 100,
          "drop_count": 100,
          "episode_id": 0,
          "pending_count": 0,
          "raw_reward_event_count": 100,
          "raw_reward_total": -100.0,
          "reward_recovered": true,
          "terminal_task_count": 100,
          "trace_id": "trace-0",
          "unknown_count": 0
        }
      ],
      "evaluation_action_by_episode_id": {
        "0": {
          "decision_count": 100
        }
      },
      "evaluation_action_by_trace_id": {
        "trace-0": {
          "decision_count": 100
        }
      },
      "evaluation_action_distribution": {
        "horizontal": 0,
        "local": 0,
        "vertical": 100
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
      "evaluation_decision_count": 100,
      "evaluation_episode_count": 100,
      "evaluation_legal_action_mask_distribution": {
        "local=1|horizontal=1|vertical=1": 100
      },
      "evaluation_reward_summary": {
        "canonical_task_count": 100,
        "completed_task_count": 0,
        "dropped_task_count": 100,
        "evaluation_episode_count": 100,
        "mean_reward": -100.0,
        "pending_at_horizon_count": 0,
        "reward_bearing_transition_count": 100,
        "terminal_transition_count": 100,
        "unknown_task_count": 0
      },
      "evaluation_trace_bank_id": "eval-bank",
      "paper_aligned_diagnostic_metrics": {
        "canonical_completion_ratio": 0.0,
        "canonical_deadline_violation_ratio": 1.0,
        "canonical_drop_ratio": 1.0,
        "canonical_mean_completion_latency_slots": null,
        "canonical_mean_drop_latency_slots": 4.0,
        "canonical_mean_terminal_latency_slots": 4.0,
        "canonical_pending_ratio": 0.0,
        "canonical_reward_per_decision": -1.0,
        "canonical_reward_per_task": -1.0,
        "canonical_tasks_per_decision": 1.0,
        "checkpoint_budget": 100,
        "raw_reward_event_coverage_ratio": 1.0,
        "reward_reconciliation_status": "passed",
        "terminal_event_coverage_ratio": 1.0
      },
      "policy_kind": "candidate",
      "policy_name": "candidate_policy_at_100",
      "raw_reward_event_count": 100,
      "raw_reward_event_recovery_blocked": false,
      "raw_reward_total": -100.0,
      "raw_terminal_event_count": 100,
      "raw_vs_canonical_terminal_reconciliation": {
        "canonical_reward_event_count": 100,
        "canonical_task_reward_total": -100.0,
        "canonical_terminal_task_count": 100,
        "duplicate_terminal_event_count": 0,
        "raw_event_reward_total": -100.0,
        "raw_reward_event_count": 100,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 100,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_event_coverage_ratio": 1.0,
        "reward_reconciled": true,
        "terminal_event_coverage_ratio": 1.0,
        "terminal_event_recovery_blocked": false,
        "terminal_reconciled": true
      },
      "reward_event_records": {
        "raw_reward_event_recovery_blocked": false,
        "record_count": 100,
        "reward_available_count": 100,
        "sample_records": [
          {
            "episode_id": 0,
            "raw_reward": -1.0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "reward_reconciliation_after_terminal_repair": {
        "canonical_task_reward_count": 100,
        "canonical_task_reward_total": -100.0,
        "checkpoint_budget": 100,
        "raw_event_reward_count": 100,
        "raw_event_reward_total": -100.0,
        "raw_reward_event_recovery_blocked": false,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_reconciled": true,
        "reward_reconciliation_tolerance": 1e-09,
        "terminal_event_recovery_blocked": false
      },
      "reward_reconciliation_tolerance": 1e-09,
      "same_evaluation_trace_bank": true,
      "task_records": {},
      "terminal_event_classification": {
        "overall": {
          "event_type_counts": {
            "deadline_expired": 100,
            "deadline_reached": 100,
            "reward_emitted": 100,
            "task_dropped": 100
          },
          "lifecycle_only_event_count": 100,
          "pending_event_count": 0,
          "reward_event_count": 100,
          "terminal_outcome_event_count": 100
        }
      },
      "terminal_event_records": {
        "record_count": 100,
        "recovered_from_finalized_tasks": true,
        "sample_records": [
          {
            "episode_id": 0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "terminal_event_recovery_blocked": false
    },
    "fixed_vertical_policy": {
      "candidate_policy_vertical_share": 1.0,
      "canonical_terminal_task_summary": {
        "overall": {
          "canonical_completion_count": 0,
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 1.0,
          "canonical_drop_count": 100,
          "canonical_drop_ratio": 1.0,
          "canonical_mean_completion_latency_slots": null,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 0,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_per_decision": -1.0,
          "canonical_reward_per_task": -1.0,
          "canonical_task_count": 100,
          "canonical_task_reward_count": 100,
          "canonical_task_reward_total": -100.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 100,
          "canonical_unknown_count": 0,
          "double_count_detected": false,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "raw_event_reward_count": 100,
          "raw_event_reward_total": -100.0,
          "raw_reward_emission_count": 100,
          "raw_terminal_event_count": 100,
          "raw_vs_canonical_reward_delta": 0.0
        }
      },
      "checkpoint_budget": 100,
      "completion_path_audit": {
        "completed_canonical_task_count": 0,
        "deadline_expired_event_count": 100,
        "deadline_reached_event_count": 100,
        "deadline_reached_then_task_dropped_duplicate_detected": true,
        "execution_completed_but_no_task_completed_detected": false,
        "execution_completed_event_count": 0,
        "pending_at_horizon_count": 0,
        "reward_emitted_event_count": 100,
        "reward_emitted_without_terminal_outcome_detected": false,
        "task_completed_but_no_reward_detected": false,
        "task_completed_event_count": 0,
        "task_dropped_event_count": 100,
        "terminal_outcome_without_reward_detected": false
      },
      "decision_records_summary": {
        "decision_count": 100,
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
      "episode_length": 110,
      "episode_reward_totals": [
        -100.0
      ],
      "episode_summaries": [
        {
          "canonical_reward_total": -100.0,
          "completion_count": 0,
          "decision_count": 100,
          "drop_count": 100,
          "episode_id": 0,
          "pending_count": 0,
          "raw_reward_event_count": 100,
          "raw_reward_total": -100.0,
          "reward_recovered": true,
          "terminal_task_count": 100,
          "trace_id": "trace-0",
          "unknown_count": 0
        }
      ],
      "evaluation_action_by_episode_id": {
        "0": {
          "decision_count": 100
        }
      },
      "evaluation_action_by_trace_id": {
        "trace-0": {
          "decision_count": 100
        }
      },
      "evaluation_action_distribution": {
        "horizontal": 0,
        "local": 0,
        "vertical": 100
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
      "evaluation_decision_count": 100,
      "evaluation_episode_count": 100,
      "evaluation_legal_action_mask_distribution": {
        "local=1|horizontal=1|vertical=1": 100
      },
      "evaluation_reward_summary": {
        "canonical_task_count": 100,
        "completed_task_count": 0,
        "dropped_task_count": 100,
        "evaluation_episode_count": 100,
        "mean_reward": -100.0,
        "pending_at_horizon_count": 0,
        "reward_bearing_transition_count": 100,
        "terminal_transition_count": 100,
        "unknown_task_count": 0
      },
      "evaluation_trace_bank_id": "eval-bank",
      "paper_aligned_diagnostic_metrics": {
        "canonical_completion_ratio": 0.0,
        "canonical_deadline_violation_ratio": 1.0,
        "canonical_drop_ratio": 1.0,
        "canonical_mean_completion_latency_slots": null,
        "canonical_mean_drop_latency_slots": 4.0,
        "canonical_mean_terminal_latency_slots": 4.0,
        "canonical_pending_ratio": 0.0,
        "canonical_reward_per_decision": -1.0,
        "canonical_reward_per_task": -1.0,
        "canonical_tasks_per_decision": 1.0,
        "checkpoint_budget": 100,
        "raw_reward_event_coverage_ratio": 1.0,
        "reward_reconciliation_status": "passed",
        "terminal_event_coverage_ratio": 1.0
      },
      "policy_kind": "candidate",
      "policy_name": "candidate_policy_at_100",
      "raw_reward_event_count": 100,
      "raw_reward_event_recovery_blocked": false,
      "raw_reward_total": -100.0,
      "raw_terminal_event_count": 100,
      "raw_vs_canonical_terminal_reconciliation": {
        "canonical_reward_event_count": 100,
        "canonical_task_reward_total": -100.0,
        "canonical_terminal_task_count": 100,
        "duplicate_terminal_event_count": 0,
        "raw_event_reward_total": -100.0,
        "raw_reward_event_count": 100,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 100,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_event_coverage_ratio": 1.0,
        "reward_reconciled": true,
        "terminal_event_coverage_ratio": 1.0,
        "terminal_event_recovery_blocked": false,
        "terminal_reconciled": true
      },
      "reward_event_records": {
        "raw_reward_event_recovery_blocked": false,
        "record_count": 100,
        "reward_available_count": 100,
        "sample_records": [
          {
            "episode_id": 0,
            "raw_reward": -1.0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "reward_reconciliation_after_terminal_repair": {
        "canonical_task_reward_count": 100,
        "canonical_task_reward_total": -100.0,
        "checkpoint_budget": 100,
        "raw_event_reward_count": 100,
        "raw_event_reward_total": -100.0,
        "raw_reward_event_recovery_blocked": false,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_reconciled": true,
        "reward_reconciliation_tolerance": 1e-09,
        "terminal_event_recovery_blocked": false
      },
      "reward_reconciliation_tolerance": 1e-09,
      "same_evaluation_trace_bank": true,
      "task_records": {},
      "terminal_event_classification": {
        "overall": {
          "event_type_counts": {
            "deadline_expired": 100,
            "deadline_reached": 100,
            "reward_emitted": 100,
            "task_dropped": 100
          },
          "lifecycle_only_event_count": 100,
          "pending_event_count": 0,
          "reward_event_count": 100,
          "terminal_outcome_event_count": 100
        }
      },
      "terminal_event_records": {
        "record_count": 100,
        "recovered_from_finalized_tasks": true,
        "sample_records": [
          {
            "episode_id": 0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "terminal_event_recovery_blocked": false
    },
    "random_legal_policy": {
      "candidate_policy_vertical_share": 1.0,
      "canonical_terminal_task_summary": {
        "overall": {
          "canonical_completion_count": 0,
          "canonical_completion_ratio": 0.0,
          "canonical_deadline_violation_ratio": 1.0,
          "canonical_drop_count": 100,
          "canonical_drop_ratio": 1.0,
          "canonical_mean_completion_latency_slots": null,
          "canonical_mean_drop_latency_slots": 4.0,
          "canonical_mean_terminal_latency_slots": 4.0,
          "canonical_pending_count": 0,
          "canonical_pending_ratio": 0.0,
          "canonical_reward_per_decision": -1.0,
          "canonical_reward_per_task": -1.0,
          "canonical_task_count": 100,
          "canonical_task_reward_count": 100,
          "canonical_task_reward_total": -100.0,
          "canonical_tasks_per_decision": 1.0,
          "canonical_terminal_task_count": 100,
          "canonical_unknown_count": 0,
          "double_count_detected": false,
          "duplicate_reward_event_count": 0,
          "duplicate_terminal_event_count": 0,
          "raw_event_reward_count": 100,
          "raw_event_reward_total": -100.0,
          "raw_reward_emission_count": 100,
          "raw_terminal_event_count": 100,
          "raw_vs_canonical_reward_delta": 0.0
        }
      },
      "checkpoint_budget": 100,
      "completion_path_audit": {
        "completed_canonical_task_count": 0,
        "deadline_expired_event_count": 100,
        "deadline_reached_event_count": 100,
        "deadline_reached_then_task_dropped_duplicate_detected": true,
        "execution_completed_but_no_task_completed_detected": false,
        "execution_completed_event_count": 0,
        "pending_at_horizon_count": 0,
        "reward_emitted_event_count": 100,
        "reward_emitted_without_terminal_outcome_detected": false,
        "task_completed_but_no_reward_detected": false,
        "task_completed_event_count": 0,
        "task_dropped_event_count": 100,
        "terminal_outcome_without_reward_detected": false
      },
      "decision_records_summary": {
        "decision_count": 100,
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
      "episode_length": 110,
      "episode_reward_totals": [
        -100.0
      ],
      "episode_summaries": [
        {
          "canonical_reward_total": -100.0,
          "completion_count": 0,
          "decision_count": 100,
          "drop_count": 100,
          "episode_id": 0,
          "pending_count": 0,
          "raw_reward_event_count": 100,
          "raw_reward_total": -100.0,
          "reward_recovered": true,
          "terminal_task_count": 100,
          "trace_id": "trace-0",
          "unknown_count": 0
        }
      ],
      "evaluation_action_by_episode_id": {
        "0": {
          "decision_count": 100
        }
      },
      "evaluation_action_by_trace_id": {
        "trace-0": {
          "decision_count": 100
        }
      },
      "evaluation_action_distribution": {
        "horizontal": 0,
        "local": 0,
        "vertical": 100
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
      "evaluation_decision_count": 100,
      "evaluation_episode_count": 100,
      "evaluation_legal_action_mask_distribution": {
        "local=1|horizontal=1|vertical=1": 100
      },
      "evaluation_reward_summary": {
        "canonical_task_count": 100,
        "completed_task_count": 0,
        "dropped_task_count": 100,
        "evaluation_episode_count": 100,
        "mean_reward": -100.0,
        "pending_at_horizon_count": 0,
        "reward_bearing_transition_count": 100,
        "terminal_transition_count": 100,
        "unknown_task_count": 0
      },
      "evaluation_trace_bank_id": "eval-bank",
      "paper_aligned_diagnostic_metrics": {
        "canonical_completion_ratio": 0.0,
        "canonical_deadline_violation_ratio": 1.0,
        "canonical_drop_ratio": 1.0,
        "canonical_mean_completion_latency_slots": null,
        "canonical_mean_drop_latency_slots": 4.0,
        "canonical_mean_terminal_latency_slots": 4.0,
        "canonical_pending_ratio": 0.0,
        "canonical_reward_per_decision": -1.0,
        "canonical_reward_per_task": -1.0,
        "canonical_tasks_per_decision": 1.0,
        "checkpoint_budget": 100,
        "raw_reward_event_coverage_ratio": 1.0,
        "reward_reconciliation_status": "passed",
        "terminal_event_coverage_ratio": 1.0
      },
      "policy_kind": "candidate",
      "policy_name": "candidate_policy_at_100",
      "raw_reward_event_count": 100,
      "raw_reward_event_recovery_blocked": false,
      "raw_reward_total": -100.0,
      "raw_terminal_event_count": 100,
      "raw_vs_canonical_terminal_reconciliation": {
        "canonical_reward_event_count": 100,
        "canonical_task_reward_total": -100.0,
        "canonical_terminal_task_count": 100,
        "duplicate_terminal_event_count": 0,
        "raw_event_reward_total": -100.0,
        "raw_reward_event_count": 100,
        "raw_reward_event_recovery_blocked": false,
        "raw_terminal_event_count": 100,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_event_coverage_ratio": 1.0,
        "reward_reconciled": true,
        "terminal_event_coverage_ratio": 1.0,
        "terminal_event_recovery_blocked": false,
        "terminal_reconciled": true
      },
      "reward_event_records": {
        "raw_reward_event_recovery_blocked": false,
        "record_count": 100,
        "reward_available_count": 100,
        "sample_records": [
          {
            "episode_id": 0,
            "raw_reward": -1.0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "reward_reconciliation_after_terminal_repair": {
        "canonical_task_reward_count": 100,
        "canonical_task_reward_total": -100.0,
        "checkpoint_budget": 100,
        "raw_event_reward_count": 100,
        "raw_event_reward_total": -100.0,
        "raw_reward_event_recovery_blocked": false,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_reconciled": true,
        "reward_reconciliation_tolerance": 1e-09,
        "terminal_event_recovery_blocked": false
      },
      "reward_reconciliation_tolerance": 1e-09,
      "same_evaluation_trace_bank": true,
      "task_records": {},
      "terminal_event_classification": {
        "overall": {
          "event_type_counts": {
            "deadline_expired": 100,
            "deadline_reached": 100,
            "reward_emitted": 100,
            "task_dropped": 100
          },
          "lifecycle_only_event_count": 100,
          "pending_event_count": 0,
          "reward_event_count": 100,
          "terminal_outcome_event_count": 100
        }
      },
      "terminal_event_records": {
        "record_count": 100,
        "recovered_from_finalized_tasks": true,
        "sample_records": [
          {
            "episode_id": 0,
            "task_id": 1,
            "trace_id": "trace-0"
          }
        ]
      },
      "terminal_event_recovery_blocked": false
    }
  },
  "raw_event_reward_static_across_budget": false
}

## 8. Why the Previous Outputs Looked Static
{
  "candidate_action_distribution_changed_by_budget": true,
  "candidate_completion_count_changed_by_budget": false,
  "candidate_drop_count_changed_by_budget": false,
  "candidate_mean_reward_changed_by_budget": false,
  "raw_terminal_events_are_lifecycle_mixed": true,
  "why_previous_outputs_looked_static": "The raw lifecycle stream contains both terminal-outcome events and lifecycle-only events. Once terminal outcomes are counted canonically, the remaining comparison is dominated by a drop-heavy trace bank and a candidate policy that stays vertically collapsed."
}

## 9. Whether Terminal and Reward Metrics Are Still Static
{
  "candidate_policy_vertical_collapse_in_evaluation": true,
  "candidate_policy_vertical_collapse_in_training_replay_window": true,
  "evaluation_action_distribution_static_across_budget": false,
  "evaluation_reward_static_after_terminal_repair": true
}

## 10. Whether Candidate Policy Collapses During Evaluation, Training, or Both
{
  "policy_affects_reward": "false",
  "policy_affects_terminal_outcomes": "false"
}

## 11. Whether Larger Training Is Still Blocked
{
  "remaining_blockers": []
}

## 12. Recommended Next Feature
Completion-path repair

## 13. Final Verdict
terminal_lifecycle_50_100_comparison_ready

## 50/100 Comparison
{
  "by_checkpoint": [],
  "checkpoint_budgets": [
    50,
    100
  ],
  "comparison": {}
}

## Paper-Aligned Metrics
{
  "by_checkpoint": [
    {
      "canonical_completion_ratio": 0.0,
      "canonical_deadline_violation_ratio": 1.0,
      "canonical_drop_ratio": 1.0,
      "canonical_mean_completion_latency_slots": null,
      "canonical_mean_drop_latency_slots": 4.0,
      "canonical_mean_terminal_latency_slots": 4.0,
      "canonical_pending_ratio": 0.0,
      "canonical_reward_per_decision": -1.0,
      "canonical_reward_per_task": -1.0,
      "canonical_tasks_per_decision": 1.0,
      "checkpoint_budget": 50,
      "raw_reward_event_coverage_ratio": 1.0,
      "reward_reconciliation_status": "passed",
      "terminal_event_coverage_ratio": 1.0,
      "training_budget": 50
    },
    {
      "canonical_completion_ratio": 0.0,
      "canonical_deadline_violation_ratio": 1.0,
      "canonical_drop_ratio": 1.0,
      "canonical_mean_completion_latency_slots": null,
      "canonical_mean_drop_latency_slots": 4.0,
      "canonical_mean_terminal_latency_slots": 4.0,
      "canonical_pending_ratio": 0.0,
      "canonical_reward_per_decision": -1.0,
      "canonical_reward_per_task": -1.0,
      "canonical_tasks_per_decision": 1.0,
      "checkpoint_budget": 100,
      "raw_reward_event_coverage_ratio": 1.0,
      "reward_reconciliation_status": "passed",
      "terminal_event_coverage_ratio": 1.0,
      "training_budget": 100
    }
  ],
  "checkpoint_budgets": [
    50,
    100
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
  "figure_directory": "artifacts/analysis/terminal-lifecycle-accounting-50-100-comparison/figures",
  "figure_files": [
    "figure_01_terminal_event_reconciliation_50_vs_100.png",
    "figure_02_completion_drop_pending_50_vs_100.png",
    "figure_03_reward_reconciliation_50_vs_100.png",
    "figure_04_policy_effect_50_vs_100.png",
    "figure_05_completion_path_event_counts.png"
  ],
  "figures_generated": true
}

## Checkpoint Summary
| budget | cumulative episodes | decisions | terminal tasks | completed | dropped | raw terminal | canonical terminal | terminal coverage | raw reward delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 50 | 100 | 100 | 0 | 100 | 100 | 100 | 1.000 | 0.000 |
| 100 | 100 | 100 | 100 | 0 | 100 | 100 | 100 | 1.000 | 0.000 |
