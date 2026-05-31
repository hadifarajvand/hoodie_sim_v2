# Feature 078 Data Model

## CampaignExecutionSeed

Fields:

- `seed_id`
- `seed_value`
- `source`

Rules:

- seed IDs are unique.
- seed values are deterministic.
- each result row records its seed ID.

## CampaignExecutionGridCell

Fields:

- `policy_id`
- `scenario_id`
- `seed_id`
- `workload_level`
- `deadline_pressure_level`
- `topology_mode`
- `runtime_mode`

Rules:

- policy IDs match Feature 077.
- scenario IDs match Feature 077.
- workload is one of `low`, `medium`, `high`.
- deadline pressure is one of `relaxed`, `moderate`, `tight`.
- topology mode is `paper_figure_7`.
- runtime mode is `paper`.

## CampaignExecutionResultRow

Fields:

- campaign identity fields
- selected action fields
- terminal status
- metric fields from Feature 077
- `compatibility_mode_used`
- execution provenance

Rules:

- every grid cell emits exactly one row.
- count metrics are non-negative integers.
- `compatibility_mode_used` is always `False`.
- action evidence is required.

## CampaignExecutionReport

Fields:

- `feature_id`
- `status`
- `passed`
- `dependency_features`
- `seed_count`
- `expected_row_count`
- `actual_row_count`
- `result_rows`
- `scope_evidence`
- `validation_summary`
- `claim_boundary`

Rules:

- dependencies include Feature 076 and Feature 077.
- expected row count equals `441 * seed_count`.
- actual row count equals expected row count.
- report does not include statistical summary or method ranking.
