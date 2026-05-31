# Feature 078 - Campaign Execution Engine

## Goal

Implement runtime-backed campaign execution for the campaign design defined by Feature 077.

Feature 078 must not merely expand Feature 076 readiness rows across seeds, workload levels, and deadline pressure levels. That shortcut is not acceptable as campaign execution.

Feature 078 must execute each campaign grid cell through the existing controlled scenario / policy / runtime helpers, then emit raw action-bound execution rows.

Feature 078 still does not produce statistical summaries, confidence intervals, ranking, final evaluation, or paper-level conclusions.

## Dependencies

- Feature 077: `077-experimental-campaign-readiness`
- Feature 076: `076-combined-baseline-proposed-comparative-readiness`
- Existing controlled scenario substrate from Feature 073
- Existing baseline policy comparison substrate from Feature 074
- Existing proposed method substrate from Feature 075
- Existing paper-faithful runtime semantics from Features 070 and 071

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

## Runtime-Backed Execution Requirement

Each campaign cell must be evaluated by calling a real execution path that recomputes the selected action, terminal status, reward, and metrics for that cell.

Forbidden shortcut:

```text
Feature 076 row + seed/workload/deadline expansion = Feature 078 execution row
```

Required behavior:

```text
campaign grid cell -> policy/proposed decision path -> paper runtime helper -> terminal status and metrics -> raw execution row
```

If workload or deadline pressure modifiers cannot yet alter the underlying runtime scenario, they must still be recorded explicitly as controlled execution dimensions and marked as currently deterministic modifiers. Do not hide this limitation.

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
- Feature 076 remains a dependency and readiness reference only.
- Feature 076 rows are not copied as Feature 078 result rows.
- every campaign grid cell has one raw result row.
- row count equals `441 * seed_count`.
- every row records policy, scenario, seed, workload, deadline pressure, topology mode, runtime mode, selected action evidence, terminal status, reward, metrics, and execution provenance.
- every row uses `paper_figure_7` topology.
- every row uses `paper` runtime mode.
- every row has `compatibility_mode_used=False`.
- every row records whether workload/deadline modifiers affected runtime or were deterministic labels.
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

## Claim Boundary

Feature 078 may claim runtime-backed raw campaign execution only if result rows are generated through execution helpers, not copied from Feature 076 readiness rows.
