# Data Model: Feature 072

## GoldenTraceScenario

Fields:

- `scenario_id`
- `name`
- `description`
- `inputs`
- `expected_outputs`
- `actual_outputs`
- `steps`
- `passed`

Validation:

- Scenario ID must be unique.
- Steps must not be empty.
- Expected and actual outputs must be comparable.

## GoldenTraceStep

Fields:

- `step_name`
- `input_snapshot`
- `actual_output`
- `expected_output`
- `passed`
- `evidence_source`

Required step names include:

- `task_arrival`
- `action_selection`
- `topology_legality`
- `deadline_computation`
- `terminal_state_assignment`
- `reward_emission`
- `expected_actual_comparison`

## TopologyTraceEvidence

Fields:

- `source_agent_id`
- `destination_agent_id`
- `neighbor_map_source`
- `is_neighbor`
- `is_self_destination`
- `final_legal`

Validation:

- Self-destination is illegal.
- Non-neighbor horizontal destination is illegal.
- Legal horizontal destination must exist in the Figure 7 neighbor map.

## DeadlineTraceEvidence

Fields:

- `arrival_slot`
- `phi`
- `absolute_deadline_slot`
- `completion_slot`
- `mode`
- `success_before_deadline`
- `terminal_status`

Validation:

- Paper mode uses strict completion before deadline.
- Completion at the deadline fails in paper mode.

## RewardTraceEvidence

Fields:

- `x_active`
- `terminal_status`
- `phi_value`
- `drop_penalty`
- `reward_value`
- `reward_slot`
- `mode`

Validation:

- Success reward is `-Phi`.
- Drop reward is `-C`.
- Inactive reward is explicit no-reward sentinel.
- Pending task cannot emit reward.

## Feature072Report

Fields:

- `feature_name`
- `status`
- `passed`
- `changed_files`
- `scenarios`
- `feature_068r_regression_status`
- `feature_069_regression_status`
- `feature_070_regression_status`
- `feature_071_regression_status`
- `paper_claim_boundary`
- `recommended_next_feature`

Validation:

- All scenarios must pass for report `passed=True`.
- All prior regression statuses must pass.
- No full paper reproduction claim is allowed.
