# Evaluation Trace Bank Baseline Harness Report

- feature_id: `058-evaluation-trace-bank-baseline-harness`
- final_verdict: `evaluation_trace_bank_baseline_harness_ready`
- recommended_next_feature: `Feature 059 — Full Paper-Default Training Campaign Gate`
- feature_057_pilot_verified: `True`

## Evaluation Trace Bank Summary
{
  "bank_generation_repeatable": true,
  "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
  "evaluation_trace_count": 12,
  "repeatability_evidence": {
    "method": "canonical sha256 over deterministic seed bundle and trace hashes",
    "same_seed_rebuild_signature": "d32ae09c1f6830361dd3cab2622dc2102b5191061e0de6cf14795619ac3ac14e"
  },
  "seed_bundle": {
    "baseline_policy_seed": 6101,
    "evaluation_trace_generation_seed": 43,
    "trace_identity_seed": 5843,
    "training_trace_generation_seed": 41
  },
  "trace_bank_signature": "d32ae09c1f6830361dd3cab2622dc2102b5191061e0de6cf14795619ac3ac14e",
  "trace_hashes": [
    "4d4c6f50a6a039fdbbd911ddfbfa11ef23f7f770c28bc4fd45620dcdf59b6879",
    "e005ecc446a771ea90e50e6e80ec4cbcaaab9f4ddbd2e0bbe2aae695271dc593",
    "02e59ac37e1d9cc99a56cb7ed0001951bd34b2a6b9332b329fa400b3cc6681e3",
    "446aa6d04d6df16f5c2d9ec4641d73523e148a539676cc60d8ab8642c3505fd8",
    "4ef715dfb23d232bdc79207c2b397b1f131639d228e09a5a9301cce11d053d59",
    "c3608ae4095307e5952fe07d22e85d08bd027400b6dc82284b54ce4ea79295a2",
    "604e7bf78e14668a8120958ac9035959d3d158d54694fa4ffce11d3cb6d2ced9",
    "d5a3efb8a17662d2b8675abbf5b214d5e39a6c54f9ef7f31f07ed2f4e1678003",
    "db39fb0427db6a7c371b15ce3fe19cce86dda47897ae1c1c4b570676fa42425a",
    "37ecc9df299de37e47e3bfe23a2b7f9fa71425cd4e1ee39fdcd1ff694af0c6a4",
    "ea921168759c8c25caad14d266b4e98295408f503d6e1577f003e802b0866dab",
    "a7b6088f92fbb903b2c48bf0729feb5ee1e4e90e50b2fe95414f77f3b0faf2a4"
  ],
  "trace_identities": [
    "feature-058-evaluation-trace-bank-trace-000-0d3321f39732",
    "feature-058-evaluation-trace-bank-trace-001-27a429c2b824",
    "feature-058-evaluation-trace-bank-trace-002-42c25a458cde",
    "feature-058-evaluation-trace-bank-trace-003-de82e91aec97",
    "feature-058-evaluation-trace-bank-trace-004-8050118c871c",
    "feature-058-evaluation-trace-bank-trace-005-1bb74efa7a79",
    "feature-058-evaluation-trace-bank-trace-006-618201f56169",
    "feature-058-evaluation-trace-bank-trace-007-247fdb56879b",
    "feature-058-evaluation-trace-bank-trace-008-c270890f4ea0",
    "feature-058-evaluation-trace-bank-trace-009-d60c2618cbed",
    "feature-058-evaluation-trace-bank-trace-010-135fe5d45383",
    "feature-058-evaluation-trace-bank-trace-011-a095006b8c3c"
  ],
  "traces": [
    {
      "arrival_slot": 1,
      "deadline_bucket": "short",
      "episode_id": 0,
      "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
      "legal_action_mask": {
        "horizontal": true,
        "local": true,
        "vertical": true
      },
      "trace_hash": "4d4c6f50a6a039fdbbd911ddfbfa11ef23f7f770c28bc4fd45620dcdf59b6879",
      "trace_id": "feature-058-evaluation-trace-bank-trace-000-0d3321f39732",
      "trace_index": 0,
      "workload_bucket": "low"
    },
    {
      "arrival_slot": 4,
      "deadline_bucket": "short",
      "episode_id": 0,
      "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
      "legal_action_mask": {
        "horizontal": true,
        "local": true,
        "vertical": true
      },
      "trace_hash": "e005ecc446a771ea90e50e6e80ec4cbcaaab9f4ddbd2e0bbe2aae695271dc593",
      "trace_id": "feature-058-evaluation-trace-bank-trace-001-27a429c2b824",
      "trace_index": 1,
      "workload_bucket": "low"
    },
    {
      "arrival_slot": 7,
      "deadline_bucket": "short",
      "episode_id": 0,
      "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
      "legal_action_mask": {
        "horizontal": true,
        "local": true,
        "vertical": true
      },
      "trace_hash": "02e59ac37e1d9cc99a56cb7ed0001951bd34b2a6b9332b329fa400b3cc6681e3",
      "trace_id": "feature-058-evaluation-trace-bank-trace-002-42c25a458cde",
      "trace_index": 2,
      "workload_bucket": "high"
    },
    {
      "arrival_slot": 10,
      "deadline_bucket": "nominal",
      "episode_id": 0,
      "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
      "legal_action_mask": {
        "horizontal": true,
        "local": true,
        "vertical": true
      },
      "trace_hash": "446aa6d04d6df16f5c2d9ec4641d73523e148a539676cc60d8ab8642c3505fd8",
      "trace_id": "feature-058-evaluation-trace-bank-trace-003-de82e91aec97",
      "trace_index": 3,
      "workload_bucket": "medium"
    },
    {
      "arrival_slot": 13,
      "deadline_bucket": "short",
      "episode_id": 1,
      "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
      "legal_action_mask": {
        "horizontal": true,
        "local": true,
        "vertical": true
      },
      "trace_hash": "4ef715dfb23d232bdc79207c2b397b1f131639d228e09a5a9301cce11d053d59",
      "trace_id": "feature-058-evaluation-trace-bank-trace-004-8050118c871c",
      "trace_index": 4,
      "workload_bucket": "medium"
    },
    {
      "arrival_slot": 16,
      "deadline_bucket": "nominal",
      "episode_id": 1,
      "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
      "legal_action_mask": {
        "horizontal": true,
        "local": true,
        "vertical": true
      },
      "trace_hash": "c3608ae4095307e5952fe07d22e85d08bd027400b6dc82284b54ce4ea79295a2",
      "trace_id": "feature-058-evaluation-trace-bank-trace-005-1bb74efa7a79",
      "trace_index": 5,
      "workload_bucket": "medium"
    },
    {
      "arrival_slot": 19,
      "deadline_bucket": "short",
      "episode_id": 1,
      "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
      "legal_action_mask": {
        "horizontal": true,
        "local": true,
        "vertical": true
      },
      "trace_hash": "604e7bf78e14668a8120958ac9035959d3d158d54694fa4ffce11d3cb6d2ced9",
      "trace_id": "feature-058-evaluation-trace-bank-trace-006-618201f56169",
      "trace_index": 6,
      "workload_bucket": "high"
    },
    {
      "arrival_slot": 22,
      "deadline_bucket": "long",
      "episode_id": 1,
      "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
      "legal_action_mask": {
        "horizontal": true,
        "local": true,
        "vertical": true
      },
      "trace_hash": "d5a3efb8a17662d2b8675abbf5b214d5e39a6c54f9ef7f31f07ed2f4e1678003",
      "trace_id": "feature-058-evaluation-trace-bank-trace-007-247fdb56879b",
      "trace_index": 7,
      "workload_bucket": "low"
    },
    {
      "arrival_slot": 25,
      "deadline_bucket": "nominal",
      "episode_id": 2,
      "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
      "legal_action_mask": {
        "horizontal": true,
        "local": true,
        "vertical": true
      },
      "trace_hash": "db39fb0427db6a7c371b15ce3fe19cce86dda47897ae1c1c4b570676fa42425a",
      "trace_id": "feature-058-evaluation-trace-bank-trace-008-c270890f4ea0",
      "trace_index": 8,
      "workload_bucket": "high"
    },
    {
      "arrival_slot": 28,
      "deadline_bucket": "long",
      "episode_id": 2,
      "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
      "legal_action_mask": {
        "horizontal": true,
        "local": true,
        "vertical": true
      },
      "trace_hash": "37ecc9df299de37e47e3bfe23a2b7f9fa71425cd4e1ee39fdcd1ff694af0c6a4",
      "trace_id": "feature-058-evaluation-trace-bank-trace-009-d60c2618cbed",
      "trace_index": 9,
      "workload_bucket": "medium"
    },
    {
      "arrival_slot": 31,
      "deadline_bucket": "short",
      "episode_id": 2,
      "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
      "legal_action_mask": {
        "horizontal": true,
        "local": true,
        "vertical": true
      },
      "trace_hash": "ea921168759c8c25caad14d266b4e98295408f503d6e1577f003e802b0866dab",
      "trace_id": "feature-058-evaluation-trace-bank-trace-010-135fe5d45383",
      "trace_index": 10,
      "workload_bucket": "medium"
    },
    {
      "arrival_slot": 34,
      "deadline_bucket": "short",
      "episode_id": 2,
      "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
      "legal_action_mask": {
        "horizontal": true,
        "local": true,
        "vertical": true
      },
      "trace_hash": "a7b6088f92fbb903b2c48bf0729feb5ee1e4e90e50b2fe95414f77f3b0faf2a4",
      "trace_id": "feature-058-evaluation-trace-bank-trace-011-a095006b8c3c",
      "trace_index": 11,
      "workload_bucket": "high"
    }
  ]
}

## Train/Eval Separation Summary
{
  "evaluation_on_training_traces": false,
  "evaluation_trace_bank_exists": true,
  "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
  "evaluation_trace_ids": [
    "feature-058-evaluation-trace-bank-trace-000-0d3321f39732",
    "feature-058-evaluation-trace-bank-trace-001-27a429c2b824",
    "feature-058-evaluation-trace-bank-trace-002-42c25a458cde",
    "feature-058-evaluation-trace-bank-trace-003-de82e91aec97",
    "feature-058-evaluation-trace-bank-trace-004-8050118c871c",
    "feature-058-evaluation-trace-bank-trace-005-1bb74efa7a79",
    "feature-058-evaluation-trace-bank-trace-006-618201f56169",
    "feature-058-evaluation-trace-bank-trace-007-247fdb56879b",
    "feature-058-evaluation-trace-bank-trace-008-c270890f4ea0",
    "feature-058-evaluation-trace-bank-trace-009-d60c2618cbed",
    "feature-058-evaluation-trace-bank-trace-010-135fe5d45383",
    "feature-058-evaluation-trace-bank-trace-011-a095006b8c3c"
  ],
  "overlap_trace_ids": [],
  "train_eval_trace_banks_disjoint": true,
  "training_trace_bank_exists": true,
  "training_trace_bank_id": "full-training-train-bank",
  "training_trace_ids": [
    "full-training-train-bank-trace-000",
    "full-training-train-bank-trace-001",
    "full-training-train-bank-trace-002",
    "full-training-train-bank-trace-003",
    "full-training-train-bank-trace-004",
    "full-training-train-bank-trace-005",
    "full-training-train-bank-trace-006",
    "full-training-train-bank-trace-007",
    "full-training-train-bank-trace-008",
    "full-training-train-bank-trace-009",
    "full-training-train-bank-trace-010",
    "full-training-train-bank-trace-011"
  ]
}

## Baseline Policy Registry Summary
{
  "action_contract_compatible": true,
  "baseline_policy_count": 3,
  "no_learned_policy_checkpoint_dependency": true,
  "policies": [
    {
      "action_contract_compatible": true,
      "kind": "deterministic-fixed-action",
      "learned_policy_checkpoint_dependency": false,
      "name": "local-only",
      "selected_action": "local"
    },
    {
      "action_contract_compatible": true,
      "kind": "deterministic-random-legal-action",
      "learned_policy_checkpoint_dependency": false,
      "name": "random-legal",
      "selected_action": "seeded legal action per trace"
    },
    {
      "action_contract_compatible": true,
      "kind": "deterministic-fixed-action",
      "learned_policy_checkpoint_dependency": false,
      "name": "fixed-horizontal",
      "selected_action": "horizontal"
    }
  ],
  "registered_policy_names": [
    "local-only",
    "random-legal",
    "fixed-horizontal"
  ]
}

## Baseline Evaluation Harness Summary
{
  "evaluated_policy_count": 3,
  "evaluation_trace_count": 12,
  "no_checkpoint_binary": true,
  "no_optimizer_steps": true,
  "no_replay_mutation": true,
  "no_training_execution": true,
  "per_policy_metric_shells": {
    "fixed-horizontal": {
      "action_distribution": {
        "horizontal": 12,
        "local": 0,
        "vertical": 0
      },
      "delay": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "drop": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "horizontal_action_count": 12,
      "local_action_count": 0,
      "per_episode_summary": [
        {
          "episode_id": 0,
          "metric_shell_only": true,
          "performance_claim": false
        },
        {
          "episode_id": 1,
          "metric_shell_only": true,
          "performance_claim": false
        },
        {
          "episode_id": 2,
          "metric_shell_only": true,
          "performance_claim": false
        }
      ],
      "reward": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "selected_actions": [
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-000-0d3321f39732"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-001-27a429c2b824"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-002-42c25a458cde"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-003-de82e91aec97"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-004-8050118c871c"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-005-1bb74efa7a79"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-006-618201f56169"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-007-247fdb56879b"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-008-c270890f4ea0"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-009-d60c2618cbed"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-010-135fe5d45383"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-011-a095006b8c3c"
        }
      ],
      "timeout": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "vertical_action_count": 0
    },
    "local-only": {
      "action_distribution": {
        "horizontal": 0,
        "local": 12,
        "vertical": 0
      },
      "delay": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "drop": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "horizontal_action_count": 0,
      "local_action_count": 12,
      "per_episode_summary": [
        {
          "episode_id": 0,
          "metric_shell_only": true,
          "performance_claim": false
        },
        {
          "episode_id": 1,
          "metric_shell_only": true,
          "performance_claim": false
        },
        {
          "episode_id": 2,
          "metric_shell_only": true,
          "performance_claim": false
        }
      ],
      "reward": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "selected_actions": [
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-000-0d3321f39732"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-001-27a429c2b824"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-002-42c25a458cde"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-003-de82e91aec97"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-004-8050118c871c"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-005-1bb74efa7a79"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-006-618201f56169"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-007-247fdb56879b"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-008-c270890f4ea0"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-009-d60c2618cbed"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-010-135fe5d45383"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-011-a095006b8c3c"
        }
      ],
      "timeout": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "vertical_action_count": 0
    },
    "random-legal": {
      "action_distribution": {
        "horizontal": 3,
        "local": 3,
        "vertical": 6
      },
      "delay": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "drop": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "horizontal_action_count": 3,
      "local_action_count": 3,
      "per_episode_summary": [
        {
          "episode_id": 0,
          "metric_shell_only": true,
          "performance_claim": false
        },
        {
          "episode_id": 1,
          "metric_shell_only": true,
          "performance_claim": false
        },
        {
          "episode_id": 2,
          "metric_shell_only": true,
          "performance_claim": false
        }
      ],
      "reward": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "selected_actions": [
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-000-0d3321f39732"
        },
        {
          "legal": true,
          "selected_action": "vertical",
          "trace_id": "feature-058-evaluation-trace-bank-trace-001-27a429c2b824"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-002-42c25a458cde"
        },
        {
          "legal": true,
          "selected_action": "vertical",
          "trace_id": "feature-058-evaluation-trace-bank-trace-003-de82e91aec97"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-004-8050118c871c"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-005-1bb74efa7a79"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-006-618201f56169"
        },
        {
          "legal": true,
          "selected_action": "vertical",
          "trace_id": "feature-058-evaluation-trace-bank-trace-007-247fdb56879b"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-008-c270890f4ea0"
        },
        {
          "legal": true,
          "selected_action": "vertical",
          "trace_id": "feature-058-evaluation-trace-bank-trace-009-d60c2618cbed"
        },
        {
          "legal": true,
          "selected_action": "vertical",
          "trace_id": "feature-058-evaluation-trace-bank-trace-010-135fe5d45383"
        },
        {
          "legal": true,
          "selected_action": "vertical",
          "trace_id": "feature-058-evaluation-trace-bank-trace-011-a095006b8c3c"
        }
      ],
      "timeout": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "vertical_action_count": 6
    }
  },
  "registered_policy_count": 3
}

## Metric Schema Summary
{
  "metric_schema_complete": true,
  "metric_values_are_shells_only": true,
  "missing_metric_fields": [],
  "performance_claim": false,
  "present_metric_fields": [
    "action_distribution",
    "delay",
    "drop",
    "horizontal_action_count",
    "local_action_count",
    "per_episode_summary",
    "reward",
    "timeout",
    "vertical_action_count"
  ],
  "required_metric_fields": [
    "delay",
    "drop",
    "timeout",
    "reward",
    "action_distribution",
    "local_action_count",
    "horizontal_action_count",
    "vertical_action_count",
    "per_episode_summary"
  ]
}

## Determinism Summary
{
  "first_run_signature": "7e2072d65b6524f142a7acc352dc6f52ec0bf81762f203f2a279589aa79bc0c5",
  "harness_outputs_repeatable": true,
  "repeatability_proven": true,
  "second_run_signature": "7e2072d65b6524f142a7acc352dc6f52ec0bf81762f203f2a279589aa79bc0c5",
  "trace_bank_repeatable": true
}

## Behavior Safety Summary
{
  "no_checkpoint_binary_written": true,
  "no_dependency_drift": true,
  "no_environment_contract_drift": true,
  "no_full_campaign": true,
  "no_optimizer_execution": true,
  "no_paper_reproduction_claim": true,
  "no_performance_claim": true,
  "no_policy_drift": true,
  "no_prior_artifact_rewrite": true,
  "no_replay_mutation": true,
  "no_reward_timing_change": true,
  "no_training_execution": true
}

## Remaining Blockers
[]