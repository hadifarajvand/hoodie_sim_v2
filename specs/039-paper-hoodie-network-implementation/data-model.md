# Data Model: Paper HOODIE Network Implementation

## Entities

### PaperHoodieNetworkConfig

- **Purpose**: Captures the architecture contract for the network surface.
- **Fields**:
  - `q_network_hidden_layers`
  - `lstm_lookback_w`
  - `lstm_num_layers`
  - `lstm_hidden_size`
  - `action_count`
  - `state_contract_ref`
  - `action_contract_ref`
  - `model_initialization_seed`
  - `dependency_status`
  - `dependency_blocked_reason`
- **Validation rules**:
  - `q_network_hidden_layers = [1024, 1024, 1024]`
  - `lstm_lookback_w = 10`
  - `lstm_num_layers = 1`
  - `lstm_hidden_size = 20`
  - `action_count = 3`
  - `q_network_hidden_layers` must be independent from LSTM configuration
  - `dependency_status` must be `dependency_blocked` when torch is unavailable

### LstmEncoder

- **Purpose**: Encodes the Feature 038 history window before the shared body.
- **Fields**:
  - `lookback_w`
  - `input_dim`
  - `hidden_size`
  - `num_layers`
- **Relationships**:
  - Feeds into `QNetworkBody`
  - Must preserve `batch_size x lookback_w x state_dim` semantics

### QNetworkBody

- **Purpose**: Shared MLP body for Q-value processing.
- **Fields**:
  - `hidden_layers`
  - `input_dim`
  - `output_dim`
- **Relationships**:
  - Consumes LSTM encoder output
  - Feeds both dueling heads

### DuelingHeads

- **Purpose**: Produce value and advantage branches.
- **Fields**:
  - `value_head_dim`
  - `advantage_head_dim`
  - `aggregation_rule`
- **Relationships**:
  - Combine into Q-values using `Q(s,a) = V(s) + A(s,a) - mean_a A(s,a)`

### OnlineTargetNetworkPair

- **Purpose**: Captures the online and target network instances and their compatibility contract.
- **Fields**:
  - `online_network`
  - `target_network`
  - `forward_api_shape`
  - `compatibility_verified`
- **Relationships**:
  - Both networks must share the same output action shape

### ShapeValidationReport

- **Purpose**: Records config separation, shape checks, deterministic initialization, and dependency status.
- **Fields**:
  - `feature_id`
  - `dependency_status`
  - `architecture_config`
  - `q_network_hidden_layers_verified`
  - `lstm_hidden_layers_verified`
  - `q_lstm_config_separation_verified`
  - `dueling_head_verified`
  - `double_dqn_api_verified`
  - `online_target_network_compatibility_verified`
  - `state_action_contract_refs`
  - `shape_validation_summary`
  - `deterministic_initialization_verified`
  - `no_training_started`
  - `no_optimizer_step`
  - `no_replay_execution`
  - `no_environment_contract_drift`
  - `no_reward_timing_change`
  - `no_policy_drift`
  - `no_dependency_drift`
  - `no_curve_fitting`
  - `no_paper_reproduction_claim`
  - `final_verdict`

## Validation Rules

- Q-network hidden layers and LSTM settings must be independently configurable.
- The architecture must reject reused `N_L` coupling between the Q-network and LSTM configuration.
- The model must preserve the Feature 038 three-action contract.
- Dependency status must be reported as blocked when torch is unavailable.
