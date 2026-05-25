# Target Update and Replay Training Validation Report

- feature_id: `056-target-update-and-replay-training-validation`
- final_verdict: `target_update_replay_validation_passed`
- recommended_next_feature: `Feature 057 — Paper-Default Pilot Training Run`
- feature_055_smoke_verified: `True`
- replay_insertion_validated: `True`
- replay_sampling_validated: `True`
- optimizer_step_counter_validated: `True`
- target_update_contract_validated: `True`
- target_sync_schedule_validated: `True`
- target_sync_before_threshold_blocked: `True`
- target_sync_at_threshold_validated: `True`
- checkpoint_metadata_validated: `True`

## Replay Summary
{
  "delayed_reward_semantics_preserved": true,
  "pending_at_horizon_true_count": 0,
  "replay_inserted": true,
  "replay_size": 110,
  "reward_available_true_count": 0,
  "sample_transitions": [
    {
      "action": 2,
      "agent_id": 3,
      "arrival_slot": 5,
      "completion_or_drop_slot": null,
      "episode_id": 0,
      "legal_action_mask": [
        true,
        true,
        true
      ],
      "next_state": [
        [
          0.0,
          0.0,
          0.0
        ],
        [
          0.0,
          0.0,
          0.0
        ],
        [
          0.0,
          0.0,
          0.0
        ],
        [
          0.0,
          0.0,
          0.0
        ],
        [
          0.009174311926605505,
          0.31,
          0.8
        ],
        [
          0.01834862385321101,
          0.8,
          0.6
        ],
        [
          0.027522935779816515,
          0.83,
          0.2
        ],
        [
          0.03669724770642202,
          0.94,
          0.2
        ],
        [
          0.045871559633027525,
          0.29,
          0.4
        ],
        [
          0.05504587155963303,
          0.31,
          0.6
        ]
      ],
      "pending_at_horizon": false,
      "reward": 0.0,
      "reward_available": false,
      "source_type": "environment_rollout",
      "state": [
        [
          0.0,
          0.0,
          0.0
        ],
        [
          0.0,
          0.0,
          0.0
        ],
        [
          0.0,
          0.0,
          0.0
        ],
        [
          0.0,
          0.0,
          0.0
        ],
        [
          0.0,
          0.0,
          0.0
        ],
        [
          0.009174311926605505,
          0.31,
          0.8
        ],
        [
          0.01834862385321101,
          0.8,
          0.6
        ],
        [
          0.027522935779816515,
          0.83,
          0.2
        ],
        [
          0.03669724770642202,
          0.94,
          0.2
        ],
        [
          0.045871559633027525,
          0.29,
          0.4
        ]
      ],
      "step_id": 5,
      "terminal": false,
      "terminal_reason": null
    },
    {
      "action": 2,
      "agent_id": 3,
      "arrival_slot": 8,
      "completion_or_drop_slot": null,
      "episode_id": 0,
      "legal_action_mask": [
        true,
        true,
        true
      ],
      "next_state": [
        [
          0.0,
          0.0,
          0.0
        ],
        [
          0.009174311926605505,
          0.31,
          0.8
        ],
        [
          0.01834862385321101,
          0.8,
          0.6
        ],
        [
          0.027522935779816515,
          0.83,
          0.2
        ],
        [
          0.03669724770642202,
          0.94,
          0.2
        ],
        [
          0.045871559633027525,
          0.29,
          0.4
        ],
        [
          0.05504587155963303,
          0.31,
          0.6
        ],
        [
          0.06422018348623854,
          0.25,
          1.0
        ],
        [
          0.07339449541284404,
          0.65,
          0.6
        ],
        [
          0.08256880733944955,
          0.19,
          0.6
        ]
      ],
      "pending_at_horizon": false,
      "reward": 0.0,
      "reward_available": false,
      "source_type": "environment_rollout",
      "state": [
        [
          0.0,
          0.0,
          0.0
        ],
        [
          0.0,
          0.0,
          0.0
        ],
        [
          0.009174311926605505,
          0.31,
          0.8
        ],
        [
          0.01834862385321101,
          0.8,
          0.6
        ],
        [
          0.027522935779816515,
          0.83,
          0.2
        ],
        [
          0.03669724770642202,
          0.94,
          0.2
        ],
        [
          0.045871559633027525,
          0.29,
          0.4
        ],
        [
          0.05504587155963303,
          0.31,
          0.6
        ],
        [
          0.06422018348623854,
          0.25,
          1.0
        ],
        [
          0.07339449541284404,
          0.65,
          0.6
        ]
      ],
      "step_id": 8,
      "terminal": false,
      "terminal_reason": null
    },
    {
      "action": 2,
      "agent_id": 3,
      "arrival_slot": 32,
      "completion_or_drop_slot": null,
      "episode_id": 0,
      "legal_action_mask": [
        true,
        true,
        true
      ],
      "next_state": [
        [
          0.22018348623853212,
          0.32,
          0.4
        ],
        [
          0.22935779816513763,
          0.15,
          0.2
        ],
        [
          0.23853211009174313,
          0.62,
          0.2
        ],
        [
          0.24770642201834864,
          0.86,
          0.2
        ],
        [
          0.25688073394495414,
          0.38,
          0.8
        ],
        [
          0.26605504587155965,
          0.68,
          0.8
        ],
        [
          0.27522935779816515,
          0.2,
          0.6
        ],
        [
          0.28440366972477066,
          0.97,
          0.4
        ],
        [
          0.29357798165137616,
          0.58,
          0.6
        ],
        [
          0.30275229357798167,
          0.47,
          0.8
        ]
      ],
      "pending_at_horizon": false,
      "reward": 0.0,
      "reward_available": false,
      "source_type": "environment_rollout",
      "state": [
        [
          0.21100917431192662,
          0.93,
          0.8
        ],
        [
          0.22018348623853212,
          0.32,
          0.4
        ],
        [
          0.22935779816513763,
          0.15,
          0.2
        ],
        [
          0.23853211009174313,
          0.62,
          0.2
        ],
        [
          0.24770642201834864,
          0.86,
          0.2
        ],
        [
          0.25688073394495414,
          0.38,
          0.8
        ],
        [
          0.26605504587155965,
          0.68,
          0.8
        ],
        [
          0.27522935779816515,
          0.2,
          0.6
        ],
        [
          0.28440366972477066,
          0.97,
          0.4
        ],
        [
          0.29357798165137616,
          0.58,
          0.6
        ]
      ],
      "step_id": 32,
      "terminal": false,
      "terminal_reason": null
    },
    {
      "action": 2,
      "agent_id": 2,
      "arrival_slot": 43,
      "completion_or_drop_slot": null,
      "episode_id": 0,
      "legal_action_mask": [
        true,
        true,
        true
      ],
      "next_state": [
        [
          0.3211009174311927,
          0.37,
          0.2
        ],
        [
          0.3302752293577982,
          0.33,
          0.8
        ],
        [
          0.3394495412844037,
          0.18,
          0.4
        ],
        [
          0.3486238532110092,
          0.73,
          0.6
        ],
        [
          0.3577981651376147,
          0.39,
          0.8
        ],
        [
          0.3669724770642202,
          0.67,
          1.0
        ],
        [
          0.3761467889908257,
          0.8,
          0.8
        ],
        [
          0.3853211009174312,
          0.55,
          0.6
        ],
        [
          0.3944954128440367,
          0.13,
          0.4
        ],
        [
          0.4036697247706422,
          0.91,
          0.4
        ]
      ],
      "pending_at_horizon": false,
      "reward": 0.0,
      "reward_available": false,
      "source_type": "environment_rollout",
      "state": [
        [
          0.3119266055045872,
          0.37,
          1.0
        ],
        [
          0.3211009174311927,
          0.37,
          0.2
        ],
        [
          0.3302752293577982,
          0.33,
          0.8
        ],
        [
          0.3394495412844037,
          0.18,
          0.4
        ],
        [
          0.3486238532110092,
          0.73,
          0.6
        ],
        [
          0.3577981651376147,
          0.39,
          0.8
        ],
        [
          0.3669724770642202,
          0.67,
          1.0
        ],
        [
          0.3761467889908257,
          0.8,
          0.8
        ],
        [
          0.3853211009174312,
          0.55,
          0.6
        ],
        [
          0.3944954128440367,
          0.13,
          0.4
        ]
      ],
      "step_id": 43,
      "terminal": false,
      "terminal_reason": null
    },
    {
      "action": 2,
      "agent_id": 1,
      "arrival_slot": 45,
      "completion_or_drop_slot": null,
      "episode_id": 0,
      "legal_action_mask": [
        true,
        true,
        true
      ],
      "next_state": [
        [
          0.3394495412844037,
          0.18,
          0.4
        ],
        [
          0.3486238532110092,
          0.73,
          0.6
        ],
        [
          0.3577981651376147,
          0.39,
          0.8
        ],
        [
          0.3669724770642202,
          0.67,
          1.0
        ],
        [
          0.3761467889908257,
          0.8,
          0.8
        ],
        [
          0.3853211009174312,
          0.55,
          0.6
        ],
        [
          0.3944954128440367,
          0.13,
          0.4
        ],
        [
          0.4036697247706422,
          0.91,
          0.4
        ],
        [
          0.41284403669724773,
          0.62,
          0.2
        ],
        [
          0.42201834862385323,
          0.75,
          1.0
        ]
      ],
      "pending_at_horizon": false,
      "reward": 0.0,
      "reward_available": false,
      "source_type": "environment_rollout",
      "state": [
        [
          0.3302752293577982,
          0.33,
          0.8
        ],
        [
          0.3394495412844037,
          0.18,
          0.4
        ],
        [
          0.3486238532110092,
          0.73,
          0.6
        ],
        [
          0.3577981651376147,
          0.39,
          0.8
        ],
        [
          0.3669724770642202,
          0.67,
          1.0
        ],
        [
          0.3761467889908257,
          0.8,
          0.8
        ],
        [
          0.3853211009174312,
          0.55,
          0.6
        ],
        [
          0.3944954128440367,
          0.13,
          0.4
        ],
        [
          0.4036697247706422,
          0.91,
          0.4
        ],
        [
          0.41284403669724773,
          0.62,
          0.2
        ]
      ],
      "step_id": 45,
      "terminal": false,
      "terminal_reason": null
    },
    {
      "action": 2,
      "agent_id": 2,
      "arrival_slot": 49,
      "completion_or_drop_slot": null,
      "episode_id": 0,
      "legal_action_mask": [
        true,
        true,
        true
      ],
      "next_state": [
        [
          0.3761467889908257,
          0.8,
          0.8
        ],
        [
          0.3853211009174312,
          0.55,
          0.6
        ],
        [
          0.3944954128440367,
          0.13,
          0.4
        ],
        [
          0.4036697247706422,
          0.91,
          0.4
        ],
        [
          0.41284403669724773,
          0.62,
          0.2
        ],
        [
          0.42201834862385323,
          0.75,
          1.0
        ],
        [
          0.43119266055045874,
          0.37,
          0.8
        ],
        [
          0.44036697247706424,
          0.46,
          0.4
        ],
        [
          0.44954128440366975,
          0.58,
          1.0
        ],
        [
          0.45871559633027525,
          0.25,
          0.6
        ]
      ],
      "pending_at_horizon": false,
      "reward": 0.0,
      "reward_available": false,
      "source_type": "environment_rollout",
      "state": [
        [
          0.3669724770642202,
          0.67,
          1.0
        ],
        [
          0.3761467889908257,
          0.8,
          0.8
        ],
        [
          0.3853211009174312,
          0.55,
          0.6
        ],
        [
          0.3944954128440367,
          0.13,
          0.4
        ],
        [
          0.4036697247706422,
          0.91,
          0.4
        ],
        [
          0.41284403669724773,
          0.62,
          0.2
        ],
        [
          0.42201834862385323,
          0.75,
          1.0
        ],
        [
          0.43119266055045874,
          0.37,
          0.8
        ],
        [
          0.44036697247706424,
          0.46,
          0.4
        ],
        [
          0.44954128440366975,
          0.58,
          1.0
        ]
      ],
      "step_id": 49,
      "terminal": false,
      "terminal_reason": null
    },
    {
      "action": 2,
      "agent_id": 3,
      "arrival_slot": 50,
      "completion_or_drop_slot": null,
      "episode_id": 0,
      "legal_action_mask": [
        true,
        true,
        true
      ],
      "next_state": [
        [
          0.3853211009174312,
          0.55,
          0.6
        ],
        [
          0.3944954128440367,
          0.13,
          0.4
        ],
        [
          0.4036697247706422,
          0.91,
          0.4
        ],
        [
          0.41284403669724773,
          0.62,
          0.2
        ],
        [
          0.42201834862385323,
          0.75,
          1.0
        ],
        [
          0.43119266055045874,
          0.37,
          0.8
        ],
        [
          0.44036697247706424,
          0.46,
          0.4
        ],
        [
          0.44954128440366975,
          0.58,
          1.0
        ],
        [
          0.45871559633027525,
          0.25,
          0.6
        ],
        [
          0.46788990825688076,
          0.48,
          0.8
        ]
      ],
      "pending_at_horizon": false,
      "reward": 0.0,
      "reward_available": false,
      "source_type": "environment_rollout",
      "state": [
        [
          0.3761467889908257,
          0.8,
          0.8
        ],
        [
          0.3853211009174312,
          0.55,
          0.6
        ],
        [
          0.3944954128440367,
          0.13,
          0.4
        ],
        [
          0.4036697247706422,
          0.91,
          0.4
        ],
        [
          0.41284403669724773,
          0.62,
          0.2
        ],
        [
          0.42201834862385323,
          0.75,
          1.0
        ],
        [
          0.43119266055045874,
          0.37,
          0.8
        ],
        [
          0.44036697247706424,
          0.46,
          0.4
        ],
        [
          0.44954128440366975,
          0.58,
          1.0
        ],
        [
          0.45871559633027525,
          0.25,
          0.6
        ]
      ],
      "step_id": 50,
      "terminal": false,
      "terminal_reason": null
    },
    {
      "action": 2,
      "agent_id": 3,
      "arrival_slot": 53,
      "completion_or_drop_slot": null,
      "episode_id": 0,
      "legal_action_mask": [
        true,
        true,
        true
      ],
      "next_state": [
        [
          0.41284403669724773,
          0.62,
          0.2
        ],
        [
          0.42201834862385323,
          0.75,
          1.0
        ],
        [
          0.43119266055045874,
          0.37,
          0.8
        ],
        [
          0.44036697247706424,
          0.46,
          0.4
        ],
        [
          0.44954128440366975,
          0.58,
          1.0
        ],
        [
          0.45871559633027525,
          0.25,
          0.6
        ],
        [
          0.46788990825688076,
          0.48,
          0.8
        ],
        [
          0.47706422018348627,
          0.98,
          0.4
        ],
        [
          0.48623853211009177,
          0.74,
          0.8
        ],
        [
          0.4954128440366973,
          0.39,
          0.8
        ]
      ],
      "pending_at_horizon": false,
      "reward": 0.0,
      "reward_available": false,
      "source_type": "environment_rollout",
      "state": [
        [
          0.4036697247706422,
          0.91,
          0.4
        ],
        [
          0.41284403669724773,
          0.62,
          0.2
        ],
        [
          0.42201834862385323,
          0.75,
          1.0
        ],
        [
          0.43119266055045874,
          0.37,
          0.8
        ],
        [
          0.44036697247706424,
          0.46,
          0.4
        ],
        [
          0.44954128440366975,
          0.58,
          1.0
        ],
        [
          0.45871559633027525,
          0.25,
          0.6
        ],
        [
          0.46788990825688076,
          0.48,
          0.8
        ],
        [
          0.47706422018348627,
          0.98,
          0.4
        ],
        [
          0.48623853211009177,
          0.74,
          0.8
        ]
      ],
      "step_id": 53,
      "terminal": false,
      "terminal_reason": null
    },
    {
      "action": 2,
      "agent_id": 2,
      "arrival_slot": 55,
      "completion_or_drop_slot": null,
      "episode_id": 0,
      "legal_action_mask": [
        true,
        true,
        true
      ],
      "next_state": [
        [
          0.43119266055045874,
          0.37,
          0.8
        ],
        [
          0.44036697247706424,
          0.46,
          0.4
        ],
        [
          0.44954128440366975,
          0.58,
          1.0
        ],
        [
          0.45871559633027525,
          0.25,
          0.6
        ],
        [
          0.46788990825688076,
          0.48,
          0.8
        ],
        [
          0.47706422018348627,
          0.98,
          0.4
        ],
        [
          0.48623853211009177,
          0.74,
          0.8
        ],
        [
          0.4954128440366973,
          0.39,
          0.8
        ],
        [
          0.5045871559633027,
          0.7,
          0.6
        ],
        [
          0.5137614678899083,
          0.41,
          0.8
        ]
      ],
      "pending_at_horizon": false,
      "reward": 0.0,
      "reward_available": false,
      "source_type": "environment_rollout",
      "state": [
        [
          0.42201834862385323,
          0.75,
          1.0
        ],
        [
          0.43119266055045874,
          0.37,
          0.8
        ],
        [
          0.44036697247706424,
          0.46,
          0.4
        ],
        [
          0.44954128440366975,
          0.58,
          1.0
        ],
        [
          0.45871559633027525,
          0.25,
          0.6
        ],
        [
          0.46788990825688076,
          0.48,
          0.8
        ],
        [
          0.47706422018348627,
          0.98,
          0.4
        ],
        [
          0.48623853211009177,
          0.74,
          0.8
        ],
        [
          0.4954128440366973,
          0.39,
          0.8
        ],
        [
          0.5045871559633027,
          0.7,
          0.6
        ]
      ],
      "step_id": 55,
      "terminal": false,
      "terminal_reason": null
    },
    {
      "action": 2,
      "agent_id": 2,
      "arrival_slot": 58,
      "completion_or_drop_slot": null,
      "episode_id": 0,
      "legal_action_mask": [
        true,
        true,
        true
      ],
      "next_state": [
        [
          0.45871559633027525,
          0.25,
          0.6
        ],
        [
          0.46788990825688076,
          0.48,
          0.8
        ],
        [
          0.47706422018348627,
          0.98,
          0.4
        ],
        [
          0.48623853211009177,
          0.74,
          0.8
        ],
        [
          0.4954128440366973,
          0.39,
          0.8
        ],
        [
          0.5045871559633027,
          0.7,
          0.6
        ],
        [
          0.5137614678899083,
          0.41,
          0.8
        ],
        [
          0.5229357798165137,
          0.82,
          0.8
        ],
        [
          0.5321100917431193,
          0.88,
          1.0
        ],
        [
          0.5412844036697247,
          0.9,
          0.4
        ]
      ],
      "pending_at_horizon": false,
      "reward": 0.0,
      "reward_available": false,
      "source_type": "environment_rollout",
      "state": [
        [
          0.44954128440366975,
          0.58,
          1.0
        ],
        [
          0.45871559633027525,
          0.25,
          0.6
        ],
        [
          0.46788990825688076,
          0.48,
          0.8
        ],
        [
          0.47706422018348627,
          0.98,
          0.4
        ],
        [
          0.48623853211009177,
          0.74,
          0.8
        ],
        [
          0.4954128440366973,
          0.39,
          0.8
        ],
        [
          0.5045871559633027,
          0.7,
          0.6
        ],
        [
          0.5137614678899083,
          0.41,
          0.8
        ],
        [
          0.5229357798165137,
          0.82,
          0.8
        ],
        [
          0.5321100917431193,
          0.88,
          1.0
        ]
      ],
      "step_id": 58,
      "terminal": false,
      "terminal_reason": null
    },
    {
      "action": 2,
      "agent_id": 3,
      "arrival_slot": 65,
      "completion_or_drop_slot": null,
      "episode_id": 0,
      "legal_action_mask": [
        true,
        true,
        true
      ],
      "next_state": [
        [
          0.5229357798165137,
          0.82,
          0.8
        ],
        [
          0.5321100917431193,
          0.88,
          1.0
        ],
        [
          0.5412844036697247,
          0.9,
          0.4
        ],
        [
          0.5504587155963303,
          0.73,
          0.6
        ],
        [
          0.5596330275229358,
          0.84,
          0.4
        ],
        [
          0.5688073394495413,
          0.12,
          0.4
        ],
        [
          0.5779816513761468,
          0.88,
          1.0
        ],
        [
          0.5871559633027523,
          0.29,
          0.2
        ],
        [
          0.5963302752293578,
          0.13,
          0.4
        ],
        [
          0.6055045871559633,
          0.89,
          0.2
        ]
      ],
      "pending_at_horizon": false,
      "reward": 0.0,
      "reward_available": false,
      "source_type": "environment_rollout",
      "state": [
        [
          0.5137614678899083,
          0.41,
          0.8
        ],
        [
          0.5229357798165137,
          0.82,
          0.8
        ],
        [
          0.5321100917431193,
          0.88,
          1.0
        ],
        [
          0.5412844036697247,
          0.9,
          0.4
        ],
        [
          0.5504587155963303,
          0.73,
          0.6
        ],
        [
          0.5596330275229358,
          0.84,
          0.4
        ],
        [
          0.5688073394495413,
          0.12,
          0.4
        ],
        [
          0.5779816513761468,
          0.88,
          1.0
        ],
        [
          0.5871559633027523,
          0.29,
          0.2
        ],
        [
          0.5963302752293578,
          0.13,
          0.4
        ]
      ],
      "step_id": 65,
      "terminal": false,
      "terminal_reason": null
    },
    {
      "action": 2,
      "agent_id": 2,
      "arrival_slot": 70,
      "completion_or_drop_slot": null,
      "episode_id": 0,
      "legal_action_mask": [
        true,
        true,
        true
      ],
      "next_state": [
        [
          0.5688073394495413,
          0.12,
          0.4
        ],
        [
          0.5779816513761468,
          0.88,
          1.0
        ],
        [
          0.5871559633027523,
          0.29,
          0.2
        ],
        [
          0.5963302752293578,
          0.13,
          0.4
        ],
        [
          0.6055045871559633,
          0.89,
          0.2
        ],
        [
          0.6146788990825688,
          0.59,
          0.4
        ],
        [
          0.6238532110091743,
          0.77,
          0.6
        ],
        [
          0.6330275229357798,
          0.72,
          0.2
        ],
        [
          0.6422018348623854,
          0.34,
          0.6
        ],
        [
          0.6513761467889908,
          0.45,
          0.8
        ]
      ],
      "pending_at_horizon": false,
      "reward": 0.0,
      "reward_available": false,
      "source_type": "environment_rollout",
      "state": [
        [
          0.5596330275229358,
          0.84,
          0.4
        ],
        [
          0.5688073394495413,
          0.12,
          0.4
        ],
        [
          0.5779816513761468,
          0.88,
          1.0
        ],
        [
          0.5871559633027523,
          0.29,
          0.2
        ],
        [
          0.5963302752293578,
          0.13,
          0.4
        ],
        [
          0.6055045871559633,
          0.89,
          0.2
        ],
        [
          0.6146788990825688,
          0.59,
          0.4
        ],
        [
          0.6238532110091743,
          0.77,
          0.6
        ],
        [
          0.6330275229357798,
          0.72,
          0.2
        ],
        [
          0.6422018348623854,
          0.34,
          0.6
        ]
      ],
      "step_id": 70,
      "terminal": false,
      "terminal_reason": null
    },
    {
      "action": 2,
      "agent_id": 2,
      "arrival_slot": 73,
      "completion_or_drop_slot": null,
      "episode_id": 0,
      "legal_action_mask": [
        true,
        true,
        true
      ],
      "next_state": [
        [
          0.5963302752293578,
          0.13,
          0.4
        ],
        [
          0.6055045871559633,
          0.89,
          0.2
        ],
        [
          0.6146788990825688,
          0.59,
          0.4
        ],
        [
          0.6238532110091743,
          0.77,
          0.6
        ],
        [
          0.6330275229357798,
          0.72,
          0.2
        ],
        [
          0.6422018348623854,
          0.34,
          0.6
        ],
        [
          0.6513761467889908,
          0.45,
          0.8
        ],
        [
          0.6605504587155964,
          0.94,
          0.8
        ],
        [
          0.6697247706422018,
          0.49,
          0.2
        ],
        [
          0.6788990825688074,
          0.59,
          0.2
        ]
      ],
      "pending_at_horizon": false,
      "reward": 0.0,
      "reward_available": false,
      "source_type": "environment_rollout",
      "state": [
        [
          0.5871559633027523,
          0.29,
          0.2
        ],
        [
          0.5963302752293578,
          0.13,
          0.4
        ],
        [
          0.6055045871559633,
          0.89,
          0.2
        ],
        [
          0.6146788990825688,
          0.59,
          0.4
        ],
        [
          0.6238532110091743,
          0.77,
          0.6
        ],
        [
          0.6330275229357798,
          0.72,
          0.2
        ],
        [
          0.6422018348623854,
          0.34,
          0.6
        ],
        [
          0.6513761467889908,
          0.45,
          0.8
        ],
        [
          0.6605504587155964,
          0.94,
          0.8
        ],
        [
          0.6697247706422018,
          0.49,
          0.2
        ]
      ],
      "step_id": 73,
      "terminal": false,
      "terminal_reason": null
    },
    {
      "action": 2,
      "agent_id": 1,
      "arrival_slot": 78,
      "completion_or_drop_slot": null,
      "episode_id": 0,
      "legal_action_mask": [
        true,
        true,
        true
      ],
      "next_state": [
        [
          0.6422018348623854,
          0.34,
          0.6
        ],
        [
          0.6513761467889908,
          0.45,
          0.8
        ],
        [
          0.6605504587155964,
          0.94,
          0.8
        ],
        [
          0.6697247706422018,
          0.49,
          0.2
        ],
        [
          0.6788990825688074,
          0.59,
          0.2
        ],
        [
          0.6880733944954128,
          0.95,
          0.8
        ],
        [
          0.6972477064220184,
          0.75,
          0.4
        ],
        [
          0.7064220183486238,
          0.19,
          0.6
        ],
        [
          0.7155963302752294,
          0.54,
          0.4
        ],
        [
          0.7247706422018348,
          0.32,
          0.6
        ]
      ],
      "pending_at_horizon": false,
      "reward": 0.0,
      "reward_available": false,
      "source_type": "environment_rollout",
      "state": [
        [
          0.6330275229357798,
          0.72,
          0.2
        ],
        [
          0.6422018348623854,
          0.34,
          0.6
        ],
        [
          0.6513761467889908,
          0.45,
          0.8
        ],
        [
          0.6605504587155964,
          0.94,
          0.8
        ],
        [
          0.6697247706422018,
          0.49,
          0.2
        ],
        [
          0.6788990825688074,
          0.59,
          0.2
        ],
        [
          0.6880733944954128,
          0.95,
          0.8
        ],
        [
          0.6972477064220184,
          0.75,
          0.4
        ],
        [
          0.7064220183486238,
          0.19,
          0.6
        ],
        [
          0.7155963302752294,
          0.54,
          0.4
        ]
      ],
      "step_id": 78,
      "terminal": false,
      "terminal_reason": null
    },
    {
      "action": 2,
      "agent_id": 1,
      "arrival_slot": 84,
      "completion_or_drop_slot": null,
      "episode_id": 0,
      "legal_action_mask": [
        true,
        true,
        true
      ],
      "next_state": [
        [
          0.6972477064220184,
          0.75,
          0.4
        ],
        [
          0.7064220183486238,
          0.19,
          0.6
        ],
        [
          0.7155963302752294,
          0.54,
          0.4
        ],
        [
          0.7247706422018348,
          0.32,
          0.6
        ],
        [
          0.7339449541284404,
          0.21,
          0.2
        ],
        [
          0.7431192660550459,
          0.5,
          0.6
        ],
        [
          0.7522935779816514,
          0.51,
          0.2
        ],
        [
          0.7614678899082569,
          0.16,
          0.8
        ],
        [
          0.7706422018348624,
          0.12,
          0.4
        ],
        [
          0.7798165137614679,
          0.77,
          0.6
        ]
      ],
      "pending_at_horizon": false,
      "reward": 0.0,
      "reward_available": false,
      "source_type": "environment_rollout",
      "state": [
        [
          0.6880733944954128,
          0.95,
          0.8
        ],
        [
          0.6972477064220184,
          0.75,
          0.4
        ],
        [
          0.7064220183486238,
          0.19,
          0.6
        ],
        [
          0.7155963302752294,
          0.54,
          0.4
        ],
        [
          0.7247706422018348,
          0.32,
          0.6
        ],
        [
          0.7339449541284404,
          0.21,
          0.2
        ],
        [
          0.7431192660550459,
          0.5,
          0.6
        ],
        [
          0.7522935779816514,
          0.51,
          0.2
        ],
        [
          0.7614678899082569,
          0.16,
          0.8
        ],
        [
          0.7706422018348624,
          0.12,
          0.4
        ]
      ],
      "step_id": 84,
      "terminal": false,
      "terminal_reason": null
    },
    {
      "action": 2,
      "agent_id": 3,
      "arrival_slot": 101,
      "completion_or_drop_slot": null,
      "episode_id": 0,
      "legal_action_mask": [
        true,
        true,
        true
      ],
      "next_state": [
        [
          0.8532110091743119,
          0.18,
          0.6
        ],
        [
          0.8623853211009175,
          0.29,
          0.8
        ],
        [
          0.8715596330275229,
          0.57,
          0.4
        ],
        [
          0.8807339449541285,
          0.63,
          1.0
        ],
        [
          0.8899082568807339,
          0.63,
          0.4
        ],
        [
          0.8990825688073395,
          0.35,
          0.2
        ],
        [
          0.908256880733945,
          0.88,
          0.6
        ],
        [
          0.9174311926605505,
          0.32,
          0.8
        ],
        [
          0.926605504587156,
          0.98,
          0.2
        ],
        [
          0.9357798165137615,
          0.89,
          0.2
        ]
      ],
      "pending_at_horizon": false,
      "reward": 0.0,
      "reward_available": false,
      "source_type": "environment_rollout",
      "state": [
        [
          0.8440366972477065,
          0.44,
          0.6
        ],
        [
          0.8532110091743119,
          0.18,
          0.6
        ],
        [
          0.8623853211009175,
          0.29,
          0.8
        ],
        [
          0.8715596330275229,
          0.57,
          0.4
        ],
        [
          0.8807339449541285,
          0.63,
          1.0
        ],
        [
          0.8899082568807339,
          0.63,
          0.4
        ],
        [
          0.8990825688073395,
          0.35,
          0.2
        ],
        [
          0.908256880733945,
          0.88,
          0.6
        ],
        [
          0.9174311926605505,
          0.32,
          0.8
        ],
        [
          0.926605504587156,
          0.98,
          0.2
        ]
      ],
      "step_id": 101,
      "terminal": false,
      "terminal_reason": null
    }
  ],
  "sampled_batch_size": 16,
  "sampled_field_coverage": {
    "action": true,
    "legal_action_mask": true,
    "next_state": true,
    "pending_at_horizon": true,
    "reward": true,
    "reward_available": true,
    "state": true,
    "terminal": true
  },
  "sampled_transition_count": 16
}

## Optimizer Step Summary
{
  "optimizer_step_count": 47,
  "optimizer_step_monotonic": true,
  "optimizer_step_sequence": [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    47
  ],
  "optimizer_steps_executed": true,
  "target_sync_count": 0
}

## Target Update Summary
{
  "no_sync_before_threshold": true,
  "simulation_deterministic": true,
  "sync_at_threshold": true,
  "sync_count_at_threshold": 1,
  "target_update_frequency": 2000,
  "target_update_unit": "optimizer_step",
  "threshold_step": 2000
}

## Checkpoint Metadata Summary
{
  "config_hash": "482a5772b7126ab3f6c6ed71782795f5a4de550299438ea0f75c6cc81143a308",
  "eval_trace_bank_id": "full-training-eval-bank",
  "keys_present": {
    "config_hash": true,
    "eval_trace_bank_id": true,
    "optimizer_step_count": true,
    "replay_size": true,
    "seed_bundle": true,
    "target_update_unit": true,
    "train_trace_bank_id": true
  },
  "metadata_valid": true,
  "optimizer_step_count": 47,
  "replay_size": 110,
  "seed_bundle": {
    "action_exploration_seed": 53,
    "evaluation_trace_generation_seed": 43,
    "model_initialization_seed": 19,
    "python_seed": 59,
    "readiness_probe_seed": 31,
    "replay_sampling_seed": 47,
    "torch_seed": 61,
    "training_trace_generation_seed": 41
  },
  "target_update_unit": "optimizer_step",
  "train_trace_bank_id": "full-training-train-bank"
}

## Behavior Safety Summary
{
  "no_baseline_comparison": true,
  "no_dependency_drift": true,
  "no_environment_contract_drift": true,
  "no_full_campaign": true,
  "no_paper_reproduction_claim": true,
  "no_policy_drift": true,
  "no_prior_artifact_rewrite": true,
  "no_reward_timing_change": true
}

## Remaining Blockers
[]