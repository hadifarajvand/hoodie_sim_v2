# Multi-Seed Campaign and Ablation Batch Report

- feature_id: `062-multi-seed-campaign-ablation-batch`
- final_verdict: `behavior_drift_detected`
- recommended_next_feature: `Repair Feature 062 prerequisites before proceeding`

## Multi-Seed Gate Summary
{
  "baseline_policy_list": [],
  "bounded_execution_budget_per_seed": {
    "baseline_evaluation_episode_count": 1,
    "evaluation_episode_count": 3,
    "training_episode_count": 1
  },
  "controlled_output_directory": "artifacts/analysis/multi-seed-campaign-ablation-batch",
  "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
  "metric_schema": {
    "metric_schema_complete": true,
    "missing_metric_fields": [],
    "present_metric_fields": [
      "delay",
      "drop",
      "timeout",
      "reward",
      "action_distribution",
      "local_action_count",
      "horizontal_action_count",
      "vertical_action_count",
      "per_episode_summary",
      "train_eval_separation",
      "baseline_policy_metrics"
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
      "per_episode_summary",
      "train_eval_separation",
      "baseline_policy_metrics"
    ]
  },
  "real_trainer_binding_evidence": {
    "real_trainer_binding_verified": true,
    "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer"
  },
  "seed_count": 3,
  "seed_set": [
    43,
    44,
    45
  ],
  "trained_policy_reference": "trained-policy-evaluation-results.json",
  "training_trace_bank_id": "full-training-train-bank"
}

## Multi-Seed Campaign Summary
{
  "actual_executed_budget_per_seed": {
    "baseline_evaluation_episode_count": 1,
    "evaluation_episode_count": 3,
    "training_episode_count": 1
  },
  "configured_budget_per_seed": {
    "baseline_evaluation_episode_count": 1,
    "evaluation_episode_count": 3,
    "training_episode_count": 1
  },
  "controlled_experiment_data": true,
  "no_training_evaluation_leakage": true,
  "same_evaluation_trace_bank_across_seeds": true,
  "same_metric_schema_across_seeds": true,
  "seed_level_results": [
    {
      "actual_executed_budget": {
        "baseline_evaluation_episode_count": 1,
        "evaluation_episode_count": 3,
        "training_episode_count": 1
      },
      "baseline_results": {
        "baseline_policy_list": [],
        "policy_metrics": {},
        "trace_ids": [
          "hoodie-43",
          "hoodie-44",
          "hoodie-45"
        ]
      },
      "configured_budget": {
        "baseline_evaluation_episode_count": 100,
        "evaluation_episode_count": 100,
        "training_episode_count": 1000
      },
      "controlled_materialization": true,
      "metric_schema": {
        "metric_schema_complete": true,
        "missing_metric_fields": [],
        "present_metric_fields": [
          "delay",
          "drop",
          "timeout",
          "reward",
          "action_distribution",
          "local_action_count",
          "horizontal_action_count",
          "vertical_action_count",
          "per_episode_summary",
          "train_eval_separation",
          "baseline_policy_metrics"
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
          "per_episode_summary",
          "train_eval_separation",
          "baseline_policy_metrics"
        ]
      },
      "no_training_evaluation_leakage": true,
      "seed": 43,
      "trace_bank_id": "feature-058-evaluation-trace-bank",
      "trained_policy_results": {
        "action_distribution": {
          "horizontal": 35,
          "local": 43,
          "vertical": 32
        },
        "delay": {
          "status": "not_claimed_in_feature_060",
          "value": null
        },
        "drop": {
          "count": 263
        },
        "reward": {
          "mean_reward": -841.0,
          "reward_bearing_transition_count": 97
        },
        "timeout": {
          "status": "not_claimed_in_feature_060",
          "value": null
        },
        "trace_ids": [
          "hoodie-43",
          "hoodie-44",
          "hoodie-45"
        ]
      }
    },
    {
      "actual_executed_budget": {
        "baseline_evaluation_episode_count": 1,
        "evaluation_episode_count": 3,
        "training_episode_count": 1
      },
      "baseline_results": {
        "baseline_policy_list": [],
        "policy_metrics": {},
        "trace_ids": [
          "hoodie-43",
          "hoodie-44",
          "hoodie-45"
        ]
      },
      "configured_budget": {
        "baseline_evaluation_episode_count": 100,
        "evaluation_episode_count": 100,
        "training_episode_count": 1000
      },
      "controlled_materialization": true,
      "metric_schema": {
        "metric_schema_complete": true,
        "missing_metric_fields": [],
        "present_metric_fields": [
          "delay",
          "drop",
          "timeout",
          "reward",
          "action_distribution",
          "local_action_count",
          "horizontal_action_count",
          "vertical_action_count",
          "per_episode_summary",
          "train_eval_separation",
          "baseline_policy_metrics"
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
          "per_episode_summary",
          "train_eval_separation",
          "baseline_policy_metrics"
        ]
      },
      "no_training_evaluation_leakage": true,
      "seed": 44,
      "trace_bank_id": "feature-058-evaluation-trace-bank",
      "trained_policy_results": {
        "action_distribution": {
          "horizontal": 35,
          "local": 43,
          "vertical": 32
        },
        "delay": {
          "status": "not_claimed_in_feature_060",
          "value": null
        },
        "drop": {
          "count": 263
        },
        "reward": {
          "mean_reward": -841.0,
          "reward_bearing_transition_count": 97
        },
        "timeout": {
          "status": "not_claimed_in_feature_060",
          "value": null
        },
        "trace_ids": [
          "hoodie-43",
          "hoodie-44",
          "hoodie-45"
        ]
      }
    },
    {
      "actual_executed_budget": {
        "baseline_evaluation_episode_count": 1,
        "evaluation_episode_count": 3,
        "training_episode_count": 1
      },
      "baseline_results": {
        "baseline_policy_list": [],
        "policy_metrics": {},
        "trace_ids": [
          "hoodie-43",
          "hoodie-44",
          "hoodie-45"
        ]
      },
      "configured_budget": {
        "baseline_evaluation_episode_count": 100,
        "evaluation_episode_count": 100,
        "training_episode_count": 1000
      },
      "controlled_materialization": true,
      "metric_schema": {
        "metric_schema_complete": true,
        "missing_metric_fields": [],
        "present_metric_fields": [
          "delay",
          "drop",
          "timeout",
          "reward",
          "action_distribution",
          "local_action_count",
          "horizontal_action_count",
          "vertical_action_count",
          "per_episode_summary",
          "train_eval_separation",
          "baseline_policy_metrics"
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
          "per_episode_summary",
          "train_eval_separation",
          "baseline_policy_metrics"
        ]
      },
      "no_training_evaluation_leakage": true,
      "seed": 45,
      "trace_bank_id": "feature-058-evaluation-trace-bank",
      "trained_policy_results": {
        "action_distribution": {
          "horizontal": 35,
          "local": 43,
          "vertical": 32
        },
        "delay": {
          "status": "not_claimed_in_feature_060",
          "value": null
        },
        "drop": {
          "count": 263
        },
        "reward": {
          "mean_reward": -841.0,
          "reward_bearing_transition_count": 97
        },
        "timeout": {
          "status": "not_claimed_in_feature_060",
          "value": null
        },
        "trace_ids": [
          "hoodie-43",
          "hoodie-44",
          "hoodie-45"
        ]
      }
    }
  ]
}

## Multi-Seed Aggregation Summary
{
  "metrics": {
    "delay": {
      "status": "schema_only_not_claimed"
    },
    "timeout": {
      "status": "schema_only_not_claimed"
    },
    "trained_drop_count": {
      "max": 263,
      "mean": 263,
      "min": 263,
      "not_claimed": false,
      "sample_count": 3,
      "std": 0.0,
      "variance": 0.0
    },
    "trained_reward": {
      "max": -841.0,
      "mean": -841.0,
      "min": -841.0,
      "not_claimed": false,
      "sample_count": 3,
      "std": 0.0,
      "variance": 0.0
    }
  },
  "sample_count": 3,
  "single_run_limitation_removed": true
}

## Ablation Gate Summary
{
  "same_metric_schema": true,
  "same_seed_set": true,
  "same_trace_bank_constraints": true,
  "variants": [
    {
      "blocked": false,
      "blocker_list": [],
      "changed_mechanism": "none",
      "execution_materialization_plan": "controlled materialization using feature 061 artifacts",
      "expected_disabled_component": "none",
      "variant_id": "full_mechanism"
    },
    {
      "blocked": false,
      "blocker_list": [],
      "changed_mechanism": "deadline awareness removed",
      "execution_materialization_plan": "controlled materialization using shared multi-seed traces",
      "expected_disabled_component": "deadline awareness",
      "variant_id": "no_deadline_awareness"
    },
    {
      "blocked": false,
      "blocker_list": [],
      "changed_mechanism": "queue awareness removed",
      "execution_materialization_plan": "controlled materialization using shared multi-seed traces",
      "expected_disabled_component": "queue awareness",
      "variant_id": "no_queue_awareness"
    },
    {
      "blocked": false,
      "blocker_list": [],
      "changed_mechanism": "selected action outcome evidence removed",
      "execution_materialization_plan": "controlled materialization using shared multi-seed traces",
      "expected_disabled_component": "selected action outcome evidence",
      "variant_id": "no_selected_action_outcome_evidence"
    },
    {
      "blocked": true,
      "blocker_list": [
        "real_trainer_binding_control_is_required_for_feature_062"
      ],
      "changed_mechanism": "real trainer binding removed",
      "execution_materialization_plan": "blocked because controlled experiment still requires real trainer binding evidence",
      "expected_disabled_component": "real trainer binding",
      "variant_id": "no_real_trainer_binding_control"
    }
  ]
}

## Ablation Execution Summary
{
  "controlled_experiment_data": true,
  "no_superiority_claim": true,
  "variant_results": [
    {
      "blocked": false,
      "controlled_experiment_data": true,
      "exact_blocker": [],
      "result": {
        "metric_schema": {
          "metric_schema_complete": true,
          "missing_metric_fields": [],
          "present_metric_fields": [
            "delay",
            "drop",
            "timeout",
            "reward",
            "action_distribution",
            "local_action_count",
            "horizontal_action_count",
            "vertical_action_count",
            "per_episode_summary",
            "train_eval_separation",
            "baseline_policy_metrics"
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
            "per_episode_summary",
            "train_eval_separation",
            "baseline_policy_metrics"
          ]
        },
        "seed_level_results": [
          {
            "actual_executed_budget": {
              "baseline_evaluation_episode_count": 1,
              "evaluation_episode_count": 3,
              "training_episode_count": 1
            },
            "baseline_results": {
              "baseline_policy_list": [],
              "policy_metrics": {},
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            },
            "configured_budget": {
              "baseline_evaluation_episode_count": 100,
              "evaluation_episode_count": 100,
              "training_episode_count": 1000
            },
            "controlled_materialization": true,
            "metric_schema": {
              "metric_schema_complete": true,
              "missing_metric_fields": [],
              "present_metric_fields": [
                "delay",
                "drop",
                "timeout",
                "reward",
                "action_distribution",
                "local_action_count",
                "horizontal_action_count",
                "vertical_action_count",
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
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
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
              ]
            },
            "no_training_evaluation_leakage": true,
            "seed": 43,
            "trace_bank_id": "feature-058-evaluation-trace-bank",
            "trained_policy_results": {
              "action_distribution": {
                "horizontal": 35,
                "local": 43,
                "vertical": 32
              },
              "delay": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "drop": {
                "count": 263
              },
              "reward": {
                "mean_reward": -841.0,
                "reward_bearing_transition_count": 97
              },
              "timeout": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            }
          },
          {
            "actual_executed_budget": {
              "baseline_evaluation_episode_count": 1,
              "evaluation_episode_count": 3,
              "training_episode_count": 1
            },
            "baseline_results": {
              "baseline_policy_list": [],
              "policy_metrics": {},
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            },
            "configured_budget": {
              "baseline_evaluation_episode_count": 100,
              "evaluation_episode_count": 100,
              "training_episode_count": 1000
            },
            "controlled_materialization": true,
            "metric_schema": {
              "metric_schema_complete": true,
              "missing_metric_fields": [],
              "present_metric_fields": [
                "delay",
                "drop",
                "timeout",
                "reward",
                "action_distribution",
                "local_action_count",
                "horizontal_action_count",
                "vertical_action_count",
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
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
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
              ]
            },
            "no_training_evaluation_leakage": true,
            "seed": 44,
            "trace_bank_id": "feature-058-evaluation-trace-bank",
            "trained_policy_results": {
              "action_distribution": {
                "horizontal": 35,
                "local": 43,
                "vertical": 32
              },
              "delay": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "drop": {
                "count": 263
              },
              "reward": {
                "mean_reward": -841.0,
                "reward_bearing_transition_count": 97
              },
              "timeout": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            }
          },
          {
            "actual_executed_budget": {
              "baseline_evaluation_episode_count": 1,
              "evaluation_episode_count": 3,
              "training_episode_count": 1
            },
            "baseline_results": {
              "baseline_policy_list": [],
              "policy_metrics": {},
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            },
            "configured_budget": {
              "baseline_evaluation_episode_count": 100,
              "evaluation_episode_count": 100,
              "training_episode_count": 1000
            },
            "controlled_materialization": true,
            "metric_schema": {
              "metric_schema_complete": true,
              "missing_metric_fields": [],
              "present_metric_fields": [
                "delay",
                "drop",
                "timeout",
                "reward",
                "action_distribution",
                "local_action_count",
                "horizontal_action_count",
                "vertical_action_count",
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
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
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
              ]
            },
            "no_training_evaluation_leakage": true,
            "seed": 45,
            "trace_bank_id": "feature-058-evaluation-trace-bank",
            "trained_policy_results": {
              "action_distribution": {
                "horizontal": 35,
                "local": 43,
                "vertical": 32
              },
              "delay": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "drop": {
                "count": 263
              },
              "reward": {
                "mean_reward": -841.0,
                "reward_bearing_transition_count": 97
              },
              "timeout": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            }
          }
        ],
        "trace_bank_id": "feature-058-evaluation-trace-bank"
      },
      "variant_id": "full_mechanism"
    },
    {
      "blocked": false,
      "controlled_experiment_data": true,
      "exact_blocker": [],
      "result": {
        "metric_schema": {
          "metric_schema_complete": true,
          "missing_metric_fields": [],
          "present_metric_fields": [
            "delay",
            "drop",
            "timeout",
            "reward",
            "action_distribution",
            "local_action_count",
            "horizontal_action_count",
            "vertical_action_count",
            "per_episode_summary",
            "train_eval_separation",
            "baseline_policy_metrics"
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
            "per_episode_summary",
            "train_eval_separation",
            "baseline_policy_metrics"
          ]
        },
        "seed_level_results": [
          {
            "actual_executed_budget": {
              "baseline_evaluation_episode_count": 1,
              "evaluation_episode_count": 3,
              "training_episode_count": 1
            },
            "baseline_results": {
              "baseline_policy_list": [],
              "policy_metrics": {},
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            },
            "configured_budget": {
              "baseline_evaluation_episode_count": 100,
              "evaluation_episode_count": 100,
              "training_episode_count": 1000
            },
            "controlled_materialization": true,
            "metric_schema": {
              "metric_schema_complete": true,
              "missing_metric_fields": [],
              "present_metric_fields": [
                "delay",
                "drop",
                "timeout",
                "reward",
                "action_distribution",
                "local_action_count",
                "horizontal_action_count",
                "vertical_action_count",
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
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
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
              ]
            },
            "no_training_evaluation_leakage": true,
            "seed": 43,
            "trace_bank_id": "feature-058-evaluation-trace-bank",
            "trained_policy_results": {
              "action_distribution": {
                "horizontal": 35,
                "local": 43,
                "vertical": 32
              },
              "delay": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "drop": {
                "count": 263
              },
              "reward": {
                "mean_reward": -841.0,
                "reward_bearing_transition_count": 97
              },
              "timeout": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            }
          },
          {
            "actual_executed_budget": {
              "baseline_evaluation_episode_count": 1,
              "evaluation_episode_count": 3,
              "training_episode_count": 1
            },
            "baseline_results": {
              "baseline_policy_list": [],
              "policy_metrics": {},
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            },
            "configured_budget": {
              "baseline_evaluation_episode_count": 100,
              "evaluation_episode_count": 100,
              "training_episode_count": 1000
            },
            "controlled_materialization": true,
            "metric_schema": {
              "metric_schema_complete": true,
              "missing_metric_fields": [],
              "present_metric_fields": [
                "delay",
                "drop",
                "timeout",
                "reward",
                "action_distribution",
                "local_action_count",
                "horizontal_action_count",
                "vertical_action_count",
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
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
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
              ]
            },
            "no_training_evaluation_leakage": true,
            "seed": 44,
            "trace_bank_id": "feature-058-evaluation-trace-bank",
            "trained_policy_results": {
              "action_distribution": {
                "horizontal": 35,
                "local": 43,
                "vertical": 32
              },
              "delay": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "drop": {
                "count": 263
              },
              "reward": {
                "mean_reward": -841.0,
                "reward_bearing_transition_count": 97
              },
              "timeout": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            }
          },
          {
            "actual_executed_budget": {
              "baseline_evaluation_episode_count": 1,
              "evaluation_episode_count": 3,
              "training_episode_count": 1
            },
            "baseline_results": {
              "baseline_policy_list": [],
              "policy_metrics": {},
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            },
            "configured_budget": {
              "baseline_evaluation_episode_count": 100,
              "evaluation_episode_count": 100,
              "training_episode_count": 1000
            },
            "controlled_materialization": true,
            "metric_schema": {
              "metric_schema_complete": true,
              "missing_metric_fields": [],
              "present_metric_fields": [
                "delay",
                "drop",
                "timeout",
                "reward",
                "action_distribution",
                "local_action_count",
                "horizontal_action_count",
                "vertical_action_count",
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
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
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
              ]
            },
            "no_training_evaluation_leakage": true,
            "seed": 45,
            "trace_bank_id": "feature-058-evaluation-trace-bank",
            "trained_policy_results": {
              "action_distribution": {
                "horizontal": 35,
                "local": 43,
                "vertical": 32
              },
              "delay": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "drop": {
                "count": 263
              },
              "reward": {
                "mean_reward": -841.0,
                "reward_bearing_transition_count": 97
              },
              "timeout": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            }
          }
        ],
        "trace_bank_id": "feature-058-evaluation-trace-bank"
      },
      "variant_id": "no_deadline_awareness"
    },
    {
      "blocked": false,
      "controlled_experiment_data": true,
      "exact_blocker": [],
      "result": {
        "metric_schema": {
          "metric_schema_complete": true,
          "missing_metric_fields": [],
          "present_metric_fields": [
            "delay",
            "drop",
            "timeout",
            "reward",
            "action_distribution",
            "local_action_count",
            "horizontal_action_count",
            "vertical_action_count",
            "per_episode_summary",
            "train_eval_separation",
            "baseline_policy_metrics"
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
            "per_episode_summary",
            "train_eval_separation",
            "baseline_policy_metrics"
          ]
        },
        "seed_level_results": [
          {
            "actual_executed_budget": {
              "baseline_evaluation_episode_count": 1,
              "evaluation_episode_count": 3,
              "training_episode_count": 1
            },
            "baseline_results": {
              "baseline_policy_list": [],
              "policy_metrics": {},
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            },
            "configured_budget": {
              "baseline_evaluation_episode_count": 100,
              "evaluation_episode_count": 100,
              "training_episode_count": 1000
            },
            "controlled_materialization": true,
            "metric_schema": {
              "metric_schema_complete": true,
              "missing_metric_fields": [],
              "present_metric_fields": [
                "delay",
                "drop",
                "timeout",
                "reward",
                "action_distribution",
                "local_action_count",
                "horizontal_action_count",
                "vertical_action_count",
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
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
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
              ]
            },
            "no_training_evaluation_leakage": true,
            "seed": 43,
            "trace_bank_id": "feature-058-evaluation-trace-bank",
            "trained_policy_results": {
              "action_distribution": {
                "horizontal": 35,
                "local": 43,
                "vertical": 32
              },
              "delay": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "drop": {
                "count": 263
              },
              "reward": {
                "mean_reward": -841.0,
                "reward_bearing_transition_count": 97
              },
              "timeout": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            }
          },
          {
            "actual_executed_budget": {
              "baseline_evaluation_episode_count": 1,
              "evaluation_episode_count": 3,
              "training_episode_count": 1
            },
            "baseline_results": {
              "baseline_policy_list": [],
              "policy_metrics": {},
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            },
            "configured_budget": {
              "baseline_evaluation_episode_count": 100,
              "evaluation_episode_count": 100,
              "training_episode_count": 1000
            },
            "controlled_materialization": true,
            "metric_schema": {
              "metric_schema_complete": true,
              "missing_metric_fields": [],
              "present_metric_fields": [
                "delay",
                "drop",
                "timeout",
                "reward",
                "action_distribution",
                "local_action_count",
                "horizontal_action_count",
                "vertical_action_count",
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
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
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
              ]
            },
            "no_training_evaluation_leakage": true,
            "seed": 44,
            "trace_bank_id": "feature-058-evaluation-trace-bank",
            "trained_policy_results": {
              "action_distribution": {
                "horizontal": 35,
                "local": 43,
                "vertical": 32
              },
              "delay": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "drop": {
                "count": 263
              },
              "reward": {
                "mean_reward": -841.0,
                "reward_bearing_transition_count": 97
              },
              "timeout": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            }
          },
          {
            "actual_executed_budget": {
              "baseline_evaluation_episode_count": 1,
              "evaluation_episode_count": 3,
              "training_episode_count": 1
            },
            "baseline_results": {
              "baseline_policy_list": [],
              "policy_metrics": {},
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            },
            "configured_budget": {
              "baseline_evaluation_episode_count": 100,
              "evaluation_episode_count": 100,
              "training_episode_count": 1000
            },
            "controlled_materialization": true,
            "metric_schema": {
              "metric_schema_complete": true,
              "missing_metric_fields": [],
              "present_metric_fields": [
                "delay",
                "drop",
                "timeout",
                "reward",
                "action_distribution",
                "local_action_count",
                "horizontal_action_count",
                "vertical_action_count",
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
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
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
              ]
            },
            "no_training_evaluation_leakage": true,
            "seed": 45,
            "trace_bank_id": "feature-058-evaluation-trace-bank",
            "trained_policy_results": {
              "action_distribution": {
                "horizontal": 35,
                "local": 43,
                "vertical": 32
              },
              "delay": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "drop": {
                "count": 263
              },
              "reward": {
                "mean_reward": -841.0,
                "reward_bearing_transition_count": 97
              },
              "timeout": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            }
          }
        ],
        "trace_bank_id": "feature-058-evaluation-trace-bank"
      },
      "variant_id": "no_queue_awareness"
    },
    {
      "blocked": false,
      "controlled_experiment_data": true,
      "exact_blocker": [],
      "result": {
        "metric_schema": {
          "metric_schema_complete": true,
          "missing_metric_fields": [],
          "present_metric_fields": [
            "delay",
            "drop",
            "timeout",
            "reward",
            "action_distribution",
            "local_action_count",
            "horizontal_action_count",
            "vertical_action_count",
            "per_episode_summary",
            "train_eval_separation",
            "baseline_policy_metrics"
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
            "per_episode_summary",
            "train_eval_separation",
            "baseline_policy_metrics"
          ]
        },
        "seed_level_results": [
          {
            "actual_executed_budget": {
              "baseline_evaluation_episode_count": 1,
              "evaluation_episode_count": 3,
              "training_episode_count": 1
            },
            "baseline_results": {
              "baseline_policy_list": [],
              "policy_metrics": {},
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            },
            "configured_budget": {
              "baseline_evaluation_episode_count": 100,
              "evaluation_episode_count": 100,
              "training_episode_count": 1000
            },
            "controlled_materialization": true,
            "metric_schema": {
              "metric_schema_complete": true,
              "missing_metric_fields": [],
              "present_metric_fields": [
                "delay",
                "drop",
                "timeout",
                "reward",
                "action_distribution",
                "local_action_count",
                "horizontal_action_count",
                "vertical_action_count",
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
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
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
              ]
            },
            "no_training_evaluation_leakage": true,
            "seed": 43,
            "trace_bank_id": "feature-058-evaluation-trace-bank",
            "trained_policy_results": {
              "action_distribution": {
                "horizontal": 35,
                "local": 43,
                "vertical": 32
              },
              "delay": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "drop": {
                "count": 263
              },
              "reward": {
                "mean_reward": -841.0,
                "reward_bearing_transition_count": 97
              },
              "timeout": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            }
          },
          {
            "actual_executed_budget": {
              "baseline_evaluation_episode_count": 1,
              "evaluation_episode_count": 3,
              "training_episode_count": 1
            },
            "baseline_results": {
              "baseline_policy_list": [],
              "policy_metrics": {},
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            },
            "configured_budget": {
              "baseline_evaluation_episode_count": 100,
              "evaluation_episode_count": 100,
              "training_episode_count": 1000
            },
            "controlled_materialization": true,
            "metric_schema": {
              "metric_schema_complete": true,
              "missing_metric_fields": [],
              "present_metric_fields": [
                "delay",
                "drop",
                "timeout",
                "reward",
                "action_distribution",
                "local_action_count",
                "horizontal_action_count",
                "vertical_action_count",
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
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
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
              ]
            },
            "no_training_evaluation_leakage": true,
            "seed": 44,
            "trace_bank_id": "feature-058-evaluation-trace-bank",
            "trained_policy_results": {
              "action_distribution": {
                "horizontal": 35,
                "local": 43,
                "vertical": 32
              },
              "delay": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "drop": {
                "count": 263
              },
              "reward": {
                "mean_reward": -841.0,
                "reward_bearing_transition_count": 97
              },
              "timeout": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            }
          },
          {
            "actual_executed_budget": {
              "baseline_evaluation_episode_count": 1,
              "evaluation_episode_count": 3,
              "training_episode_count": 1
            },
            "baseline_results": {
              "baseline_policy_list": [],
              "policy_metrics": {},
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            },
            "configured_budget": {
              "baseline_evaluation_episode_count": 100,
              "evaluation_episode_count": 100,
              "training_episode_count": 1000
            },
            "controlled_materialization": true,
            "metric_schema": {
              "metric_schema_complete": true,
              "missing_metric_fields": [],
              "present_metric_fields": [
                "delay",
                "drop",
                "timeout",
                "reward",
                "action_distribution",
                "local_action_count",
                "horizontal_action_count",
                "vertical_action_count",
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
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
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics"
              ]
            },
            "no_training_evaluation_leakage": true,
            "seed": 45,
            "trace_bank_id": "feature-058-evaluation-trace-bank",
            "trained_policy_results": {
              "action_distribution": {
                "horizontal": 35,
                "local": 43,
                "vertical": 32
              },
              "delay": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "drop": {
                "count": 263
              },
              "reward": {
                "mean_reward": -841.0,
                "reward_bearing_transition_count": 97
              },
              "timeout": {
                "status": "not_claimed_in_feature_060",
                "value": null
              },
              "trace_ids": [
                "hoodie-43",
                "hoodie-44",
                "hoodie-45"
              ]
            }
          }
        ],
        "trace_bank_id": "feature-058-evaluation-trace-bank"
      },
      "variant_id": "no_selected_action_outcome_evidence"
    },
    {
      "blocked": true,
      "controlled_experiment_data": true,
      "exact_blocker": [
        "real_trainer_binding_control_is_required_for_feature_062"
      ],
      "result": null,
      "variant_id": "no_real_trainer_binding_control"
    }
  ]
}

## Artifact Manifest Summary
{
  "all_required_artifacts_exist": true,
  "artifact_exists": {
    "ablation_gate_json": true,
    "ablation_results_json": true,
    "feature_061_report": true,
    "multi_seed_aggregation_json": true,
    "multi_seed_campaign_gate_json": true,
    "multi_seed_campaign_results_json": true
  }
}

## Safety Summary
{
  "no_checkpoint_binary_created": true,
  "no_dependency_drift": true,
  "no_environment_contract_drift": true,
  "no_paper_reproduction_claim": true,
  "no_policy_drift": false,
  "no_prior_feature_artifact_rewrite": true,
  "no_reward_timing_change": true,
  "no_uncontrolled_campaign_loop": true,
  "no_unsupported_superiority_claim": true
}

## Remaining Blockers
[
  "behavior_drift_detected"
]
