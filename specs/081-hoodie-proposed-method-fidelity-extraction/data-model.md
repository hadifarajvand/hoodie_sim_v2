# Data Model

## HoodieComponent

Fields:
- component_id
- component_name
- paper_definition
- paper_source
- current_implementation
- status
- gap
- required_repair

Statuses:
- implemented
- partial
- missing
- not_applicable

## FidelityMatrix

Fields:
- feature_id
- source_pdf
- source_ocr
- components
- summary

Required components:
- system_model
- architecture
- edge_agents
- state_space
- action_space
- reward_cost
- private_queue
- offloading_queue
- public_queue
- dqn_training
- double_dqn
- dueling_dqn
- lstm_forecast
- replay_memory
- inference
- pubsub_recovery
- baselines
- metrics
- simulation_parameters

## RepairPlan

Fields:
- component_id
- gap_type
- repair_action
- target_files
- tests_needed
