# Validation Rules: Feature 087

## Scope Rule

Feature 087 is output comparison only. It must not introduce:

- thesis method;
- DCQ;
- custom queue redesign;
- new proposed method;
- unvalidated full empirical reproduction claim.

## Feature 086 Boundary Rule

All Feature 086 documented approximations must be carried into Feature 087 reports and comparison caveats.

A ready output-comparison verdict does not erase those approximations.

## Policy Rule

Active policies must remain exactly:

```text
HOODIE
RO
FLC
VO
HO
BCO
MLEO
```

Invalid active labels must not appear in Feature 087 active outputs:

```text
MQO
Minimum Queue Offloader
ORIGINAL_HOODIE_BASELINE
HOODIE_PROPOSED
```

## Metric Rule

Allowed paper-comparison candidates:

```text
task_completion_delay
task_drop_ratio
completion_rate
average_reward
total_reward
throughput
```

Repository diagnostics unless paper directly supports them:

```text
timeout_drop_rate
unavailable_drop_rate
deadline_violation_rate
queue_stability_score
illegal_action_rejection_count
```

Repository diagnostics must not be headline paper-comparison metrics.

## Paper Extraction Rule

Every paper output item must record:

- source location;
- item type;
- metric;
- policy set;
- scenario/x-axis;
- extraction method;
- confidence;
- whether numeric comparison is possible.

## Comparison Status Rule

Every comparison row must use one of:

```text
aligned
partially_aligned
divergent
not_comparable
```

`not_comparable` must explain why.

## Final Verdict Rule

Final report must declare exactly one:

```text
paper_output_comparison_ready
paper_output_comparison_partial
paper_output_comparison_blocked
```

`paper_output_comparison_ready` is allowed only if all required artifacts exist and no blocking extraction/comparison issue remains.

`paper_output_comparison_partial` is appropriate when comparison can proceed for some outputs but not all paper figures/tables.

`paper_output_comparison_blocked` is required if paper outputs cannot be extracted or simulator outputs cannot be matched to paper metrics.
