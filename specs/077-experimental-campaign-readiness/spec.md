# Feature 077 - Experimental Campaign Readiness

## Goal

Define the experimental campaign design required after Feature 076. This feature does not execute experiments and does not create result artifacts. It records the campaign configuration readiness needed before any experimental run.

## Dependency on Feature 076

Feature 077 depends on `076-combined-baseline-proposed-comparative-readiness`.

Feature 076 provides:

- combined baseline + proposed matrix
- 7 policy/method IDs
- 7 scenario IDs
- 49 action-bound rows
- no superiority claim
- no final evaluation claim
- `compatibility_mode_used=False` for every row and aggregate
- paper-faithful runtime mode from prior features

## Required Policies / Methods

- `FLC`
- `VO`
- `HO`
- `RO`
- `BCO`
- `MLEO`
- `PROPOSED_DCQ`

## Required Scenarios

- `light_load_no_deadline_pressure`
- `tight_deadline_pressure`
- `legal_horizontal_offload`
- `illegal_horizontal_destination_attempt`
- `cloud_vertical_fallback`
- `timeout_drop_case`
- `mixed_local_horizontal_cloud_candidates`

## Campaign Dimensions

### Seeds

- Deterministic seed list
- Minimum seed count greater than zero
- Seed reproducibility rule
- Seed identity recorded in every future result row

### Workload / Load Levels

- `low`
- `medium`
- `high`

### Deadline Pressure Levels

- `relaxed`
- `moderate`
- `tight`

### Topology Mode

- `paper_figure_7`

### Runtime Mode

- `paper`

## Metric Schema

Future campaign results must support these metric fields:

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

## Future Statistical Summary Schema

Future aggregated summaries must support:

- `mean`
- `std`
- `min`
- `max`
- `count`
- `ci95_low`
- `ci95_high`

## Acceptance Criteria

- Feature 076 dependency is recorded.
- Required 7 policy/method IDs are recorded.
- Required 7 scenario IDs are recorded.
- Seed plan is deterministic and requires seed identity in every future result row.
- Workload levels are exactly `low`, `medium`, `high`.
- Deadline pressure levels are exactly `relaxed`, `moderate`, `tight`.
- Topology mode is exactly `paper_figure_7`.
- Runtime mode is exactly `paper`.
- `compatibility_mode_used` must remain `False`.
- No experiments are executed.
- No generated result artifacts are created.
- No superiority, statistical significance, full reproduction, final evaluation, or trained DRL/MADRL claims are made.

## Out of Scope

- Experiment execution
- Final results
- Model training
- Superiority claims
- Statistical significance claims
- Full paper reproduction claims
- `src/**` edits during the Spec Kit phase
- `tests/**` edits during the Spec Kit phase
- `artifacts/**`, `resources/**`, dependency file, and lock file edits

## Claim Boundary

- No training claim
- No superiority claim
- No final evaluation claim
- No statistical significance claim
- No full paper reproduction claim
