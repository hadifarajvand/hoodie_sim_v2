# Feature 078 - Campaign Execution Engine

## Goal

Define and later implement the campaign execution layer after Feature 077.

Feature 078 turns the Feature 077 campaign design into raw execution rows. It does not produce statistical summaries, rankings, final evaluation, or paper-level conclusions.

## Dependencies

- Feature 077: `077-experimental-campaign-readiness`
- Feature 076: `076-combined-baseline-proposed-comparative-readiness`

## Required Policy IDs

- `FLC`
- `VO`
- `HO`
- `RO`
- `BCO`
- `MLEO`
- `PROPOSED_DCQ`

## Required Scenario IDs

- `light_load_no_deadline_pressure`
- `tight_deadline_pressure`
- `legal_horizontal_offload`
- `illegal_horizontal_destination_attempt`
- `cloud_vertical_fallback`
- `timeout_drop_case`
- `mixed_local_horizontal_cloud_candidates`

## Campaign Dimensions

- seed IDs: deterministic and non-empty
- workload levels: `low`, `medium`, `high`
- deadline pressure levels: `relaxed`, `moderate`, `tight`
- topology mode: `paper_figure_7`
- runtime mode: `paper`

## Expected Row Count

```text
7 * 7 * seed_count * 3 * 3 = 441 * seed_count
```

## Required Metrics

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

## Acceptance Criteria

- Feature 077 campaign contract is consumed.
- Feature 076 remains the readiness substrate.
- every campaign grid cell has one raw result row.
- row count equals `441 * seed_count`.
- every row records policy, scenario, seed, workload, deadline pressure, topology mode, runtime mode, selected action evidence, terminal status, and metrics.
- every row uses `paper_figure_7` topology.
- every row uses `paper` runtime mode.
- every row has `compatibility_mode_used=False`.
- output files are not committed unless explicitly allowed by scope rules.

## Out of Scope

- statistical summaries
- confidence intervals
- method ranking
- final evaluation report
- ablation study
- sensitivity analysis
- model training
- baseline policy rewrites
- proposed-method rewrites
- topology/runtime rewrites
- dependency or lock-file edits
