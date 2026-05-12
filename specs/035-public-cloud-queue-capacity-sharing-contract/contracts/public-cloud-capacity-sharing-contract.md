# Public/Cloud Capacity Sharing Contract

## Purpose

Define the runtime contract for splitting fixed public and cloud CPU capacity across active queue heads.

## Contract

### Host Pools

- Public EA host pools are keyed by destination `host_node_id`.
- Cloud queues belong to a single global host pool keyed as `"cloud"`.
- Public EA capacity and cloud capacity are separate pools.

### Capacity Allocation

- For each slot, identify the active queue head for every eligible queue.
- Group active heads by host pool.
- Split each host pool's capacity evenly across the active heads in that host pool.
- Use deterministic stable ordering for host groups and heads.
- Do not redistribute leftover capacity within the same slot.

### Scope Limits

- Do not change local/private execution.
- Do not change execution-time formulas.
- Do not change transmission delay.
- Do not change reward timing.
- Do not change topology legality.
