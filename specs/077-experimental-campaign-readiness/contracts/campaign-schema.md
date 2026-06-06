# Campaign Schema

## Policy / Method IDs

- `FLC`
- `VO`
- `HO`
- `RO`
- `BCO`
- `MLEO`
- `PROPOSED_DCQ`

## Scenario IDs

- `light_load_no_deadline_pressure`
- `tight_deadline_pressure`
- `legal_horizontal_offload`
- `illegal_horizontal_destination_attempt`
- `cloud_vertical_fallback`
- `timeout_drop_case`
- `mixed_local_horizontal_cloud_candidates`

## Seed IDs

- Deterministic seed list required
- Seed count must be greater than zero
- Seed identity must be recorded in every future result row

## Workload Levels

- `low`
- `medium`
- `high`

## Deadline Pressure Levels

- `relaxed`
- `moderate`
- `tight`

## Modes

- Topology mode: `paper_figure_7`
- Runtime mode: `paper`

## Metric Fields

- `completed_count`
- `dropped_timeout_count`
- `dropped_unavailable_count`
- `deadline_violation_count`
- `illegal_action_rejection_count`
- `average_delay`
- `average_reward`
- `total_reward`
- `completion_rate`
- `timeout_drop_rate`
- `unavailable_drop_rate`
- `deadline_violation_rate`
- `compatibility_mode_used`

## Expected Grid Size Formula

```text
policy_count * scenario_count * seed_count * workload_count * deadline_pressure_count
```

Where:

- `policy_count = 7`
- `scenario_count = 7`
- `workload_count = 3`
- `deadline_pressure_count = 3`
- `seed_count` must be deterministic and greater than 0

Therefore:

```text
expected_grid_size = 7 * 7 * seed_count * 3 * 3 = 441 * seed_count
```
