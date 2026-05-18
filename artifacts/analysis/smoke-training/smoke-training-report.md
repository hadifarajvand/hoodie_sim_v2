# Smoke Training Report

- feature_id: `040-smoke-training`
- dependency_status: `available_existing_torch`
- final_verdict: `smoke_training_passed`
- no_paper_reproduction_claim: `True`
- no_curve_fitting: `True`
- no_full_training: `True`
- no_campaign_execution: `True`
- no_baseline_comparison: `True`
- no_target_update_execution: `True`
- no_dependency_drift: `True`
- no_environment_contract_drift: `True`
- no_policy_drift: `True`
- no_reward_timing_change: `True`

## Smoke Scope
{
  "baseline_comparison": false,
  "campaign_execution": false,
  "dependency_files_changed": false,
  "environment_rollout_requested": false,
  "environment_rollout_used": false,
  "fixture_first": true,
  "fixture_transitions_used": true,
  "full_training": false,
  "paper_reproduction": false,
  "reward_timing_changed": false,
  "smoke_only": true,
  "target_update_executed": false,
  "target_update_sync_executed": false
}

## Smoke Batch Summary
{
  "batch_size": 2,
  "data_source": "smoke_fixture",
  "non_terminal_count": 1,
  "pending_count": 1,
  "reward_bearing_count": 1,
  "seed_signature": "smoke=40|python=40|torch=40|model=19",
  "terminal_count": 1
}

## Optimizer Step Summary
{
  "learning_rate": 7e-07,
  "optimizer_name": "Adam",
  "optimizer_step_count": 1,
  "target_update_executed": false,
  "target_update_sync_executed": false
}

## Loss Summary
{
  "is_finite": true,
  "loss_mode": "smoke_mse",
  "loss_value": 100.01139831542969
}

## Parameter Update Summary
{
  "all_checked_finite": true,
  "changed_parameter_count": 14,
  "changed_parameter_names": [
    "encoder.weight_ih_l0",
    "encoder.weight_hh_l0",
    "encoder.bias_ih_l0",
    "encoder.bias_hh_l0",
    "q_body.0.weight",
    "q_body.0.bias",
    "q_body.2.weight",
    "q_body.2.bias",
    "q_body.4.weight",
    "q_body.4.bias",
    "value_head.weight",
    "value_head.bias",
    "advantage_head.weight",
    "advantage_head.bias"
  ],
  "step_count": 1,
  "target_parameters_changed": false
}

## Deterministic Repeatability
{
  "comparison_signature": {
    "delayed_reward_contract_verified": {
      "non_terminal_reward_available_false": true,
      "pending_at_horizon_is_non_terminal": true,
      "terminal_reward_available_true": true
    },
    "dependency_status": "available_existing_torch",
    "feature_038_training_readiness_block_respected": true,
    "loss_summary": {
      "is_finite": true,
      "loss_mode": "smoke_mse",
      "loss_value": 100.01139831542969
    },
    "network_contract_verified": {
      "action_count": 3,
      "double_dqn_api_enabled": true,
      "dueling_enabled": true,
      "feature_039_model_surface": true,
      "input_shape": [
        2,
        10,
        3
      ],
      "lookback_w": 10,
      "online_target_api_compatible": true,
      "output_shape": [
        2,
        3
      ],
      "state_dim": 3,
      "uses_feature_039_api": true
    },
    "no_baseline_comparison": true,
    "no_campaign_execution": true,
    "no_curve_fitting": true,
    "no_dependency_drift": true,
    "no_environment_contract_drift": true,
    "no_full_training": true,
    "no_paper_reproduction_claim": true,
    "no_policy_drift": true,
    "no_reward_timing_change": true,
    "no_target_update_execution": true,
    "optimizer_step_summary": {
      "learning_rate": 7e-07,
      "optimizer_name": "Adam",
      "optimizer_step_count": 1,
      "target_update_executed": false,
      "target_update_sync_executed": false
    },
    "parameter_update_summary": {
      "all_checked_finite": true,
      "changed_parameter_count": 14,
      "changed_parameter_names": [
        "encoder.weight_ih_l0",
        "encoder.weight_hh_l0",
        "encoder.bias_ih_l0",
        "encoder.bias_hh_l0",
        "q_body.0.weight",
        "q_body.0.bias",
        "q_body.2.weight",
        "q_body.2.bias",
        "q_body.4.weight",
        "q_body.4.bias",
        "value_head.weight",
        "value_head.bias",
        "advantage_head.weight",
        "advantage_head.bias"
      ],
      "step_count": 1,
      "target_parameters_changed": false
    },
    "replay_contract_verified": {
      "data_source": "smoke_fixture",
      "legal_action_mask_metadata": true,
      "no_fake_terminal_rewards": true,
      "non_terminal_reward_available_false": true,
      "pending_at_horizon_preserved": true,
      "smoke_fixture_not_simulator_evidence": true,
      "terminal_reward_available_true": true
    },
    "seed_protocol_verified": {
      "model_initialization_seed": 19,
      "python_seed": 40,
      "seed_signature": "smoke=40|python=40|torch=40|model=19",
      "smoke_seed": 40,
      "torch_seed": 40
    },
    "smoke_batch_summary": {
      "batch_size": 2,
      "data_source": "smoke_fixture",
      "non_terminal_count": 1,
      "pending_count": 1,
      "reward_bearing_count": 1,
      "seed_signature": "smoke=40|python=40|torch=40|model=19",
      "terminal_count": 1
    },
    "smoke_scope": {
      "baseline_comparison": false,
      "campaign_execution": false,
      "dependency_files_changed": false,
      "environment_rollout_requested": false,
      "environment_rollout_used": false,
      "fixture_first": true,
      "fixture_transitions_used": true,
      "full_training": false,
      "paper_reproduction": false,
      "reward_timing_changed": false,
      "smoke_only": true,
      "target_update_executed": false,
      "target_update_sync_executed": false
    },
    "target_update_blocked_reason": "Feature 038 target-update frequency iteration unit remains unresolved_pending_user_approval; Feature 040 instantiates the target network but does not sync or update it."
  },
  "repeat_signature": {
    "delayed_reward_contract_verified": {
      "non_terminal_reward_available_false": true,
      "pending_at_horizon_is_non_terminal": true,
      "terminal_reward_available_true": true
    },
    "dependency_status": "available_existing_torch",
    "feature_038_training_readiness_block_respected": true,
    "loss_summary": {
      "is_finite": true,
      "loss_mode": "smoke_mse",
      "loss_value": 100.01139831542969
    },
    "network_contract_verified": {
      "action_count": 3,
      "double_dqn_api_enabled": true,
      "dueling_enabled": true,
      "feature_039_model_surface": true,
      "input_shape": [
        2,
        10,
        3
      ],
      "lookback_w": 10,
      "online_target_api_compatible": true,
      "output_shape": [
        2,
        3
      ],
      "state_dim": 3,
      "uses_feature_039_api": true
    },
    "no_baseline_comparison": true,
    "no_campaign_execution": true,
    "no_curve_fitting": true,
    "no_dependency_drift": true,
    "no_environment_contract_drift": true,
    "no_full_training": true,
    "no_paper_reproduction_claim": true,
    "no_policy_drift": true,
    "no_reward_timing_change": true,
    "no_target_update_execution": true,
    "optimizer_step_summary": {
      "learning_rate": 7e-07,
      "optimizer_name": "Adam",
      "optimizer_step_count": 1,
      "target_update_executed": false,
      "target_update_sync_executed": false
    },
    "parameter_update_summary": {
      "all_checked_finite": true,
      "changed_parameter_count": 14,
      "changed_parameter_names": [
        "encoder.weight_ih_l0",
        "encoder.weight_hh_l0",
        "encoder.bias_ih_l0",
        "encoder.bias_hh_l0",
        "q_body.0.weight",
        "q_body.0.bias",
        "q_body.2.weight",
        "q_body.2.bias",
        "q_body.4.weight",
        "q_body.4.bias",
        "value_head.weight",
        "value_head.bias",
        "advantage_head.weight",
        "advantage_head.bias"
      ],
      "step_count": 1,
      "target_parameters_changed": false
    },
    "replay_contract_verified": {
      "data_source": "smoke_fixture",
      "legal_action_mask_metadata": true,
      "no_fake_terminal_rewards": true,
      "non_terminal_reward_available_false": true,
      "pending_at_horizon_preserved": true,
      "smoke_fixture_not_simulator_evidence": true,
      "terminal_reward_available_true": true
    },
    "seed_protocol_verified": {
      "model_initialization_seed": 19,
      "python_seed": 40,
      "seed_signature": "smoke=40|python=40|torch=40|model=19",
      "smoke_seed": 40,
      "torch_seed": 40
    },
    "smoke_batch_summary": {
      "batch_size": 2,
      "data_source": "smoke_fixture",
      "non_terminal_count": 1,
      "pending_count": 1,
      "reward_bearing_count": 1,
      "seed_signature": "smoke=40|python=40|torch=40|model=19",
      "terminal_count": 1
    },
    "smoke_scope": {
      "baseline_comparison": false,
      "campaign_execution": false,
      "dependency_files_changed": false,
      "environment_rollout_requested": false,
      "environment_rollout_used": false,
      "fixture_first": true,
      "fixture_transitions_used": true,
      "full_training": false,
      "paper_reproduction": false,
      "reward_timing_changed": false,
      "smoke_only": true,
      "target_update_executed": false,
      "target_update_sync_executed": false
    },
    "target_update_blocked_reason": "Feature 038 target-update frequency iteration unit remains unresolved_pending_user_approval; Feature 040 instantiates the target network but does not sync or update it."
  },
  "same_seed_match": true
}

## Prerequisite Checks
- **branch**: True (git branch --show-current == 040-smoke-training)
- **not_main**: True (current branch != main)
- **main_equals_origin_main**: True (main == origin/main)
- **main_equals_feature_039**: True (main == 039-paper-hoodie-network-implementation-complete^{})
- **prerequisite_diff_empty**: True (diff between 039-paper-hoodie-network-implementation-complete^{} and main is empty)
- **feature_dir_exists**: True (specs/040-smoke-training/ exists)
- **pointer_matches_feature**: True (.specify/feature.json points to specs/040-smoke-training)
- **pointer_not_staged**: True (.specify/feature.json must not be staged)
- **pointer_not_in_main_head**: True (.specify/feature.json must not appear in git diff --name-only main...HEAD)

## Contract Checks
- **network_contract_verified**: {'feature_039_model_surface': True, 'input_shape': [2, 10, 3], 'output_shape': [2, 3], 'state_dim': 3, 'action_count': 3, 'lookback_w': 10, 'dueling_enabled': True, 'double_dqn_api_enabled': True, 'online_target_api_compatible': True, 'uses_feature_039_api': True}
- **replay_contract_verified**: {'data_source': 'smoke_fixture', 'legal_action_mask_metadata': True, 'non_terminal_reward_available_false': True, 'terminal_reward_available_true': True, 'pending_at_horizon_preserved': True, 'no_fake_terminal_rewards': True, 'smoke_fixture_not_simulator_evidence': True}
- **delayed_reward_contract_verified**: {'non_terminal_reward_available_false': True, 'terminal_reward_available_true': True, 'pending_at_horizon_is_non_terminal': True}
- **seed_protocol_verified**: {'smoke_seed': 40, 'python_seed': 40, 'torch_seed': 40, 'model_initialization_seed': 19, 'seed_signature': 'smoke=40|python=40|torch=40|model=19'}
- **target_update_blocked_reason**: Feature 038 target-update frequency iteration unit remains unresolved_pending_user_approval; Feature 040 instantiates the target network but does not sync or update it.
