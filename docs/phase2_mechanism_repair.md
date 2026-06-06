# Phase 2 Mechanism Repair

This phase repairs the paper-facing runtime mechanisms without introducing training, figure generation, or the later validation pipeline.

## Queue formulas

### Private queue

- The private queue continues to process one task stream per server.
- Completion remains represented by `completion_time` and `service_end_time`.
- Drop remains represented by `drop_time` and `drop_reason`.
- Trace fields are preserved from Phase 1.

### Offloading queue

- Horizontal offloading remains adjacency constrained by the connection matrix.
- Offloaded tasks continue to carry `task_id`, origin, and target server identity.

### Public queue CPU sharing

- Public CPU is now split dynamically by the number of active public queues.
- Allocation is equal per active queue, not weighted by task priority.

## Reward assignment

- The runtime reward path remains unchanged for the learning loop.
- Phase 2 adds a task-traceable reward reconstruction artifact by `task_id`.
- Completed tasks map to a negative delay-style reward.
- Dropped tasks map to the fixed drop penalty used by the legacy runtime.

## Action legality

- Action mapping remains explicit through the matchmaker.
- Baseline aliases are exposed for paper-facing names.
- Horizontal legality is still governed by the connection matrix.

## Baseline policy notes

The selectable names now include:

- `HOODIE`
- `RO`
- `FLC`
- `VO`
- `HO`
- `BCO`
- `MLEO`

These are registry aliases over the existing legacy implementations. They are not a claim of paper-perfect baseline recreation.

## Legacy limitations

- The learning stack is still the original repository implementation.
- Phase 2 does not add 200-episode evaluation.
- Phase 2 does not generate paper figures.
- Phase 2 does not replace the existing DRL pipeline.
