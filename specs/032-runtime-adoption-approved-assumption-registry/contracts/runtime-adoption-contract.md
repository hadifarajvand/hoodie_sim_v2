# Runtime Adoption Contract

## Scope

This contract defines the runtime adoption boundaries for Feature 032. It covers approved compute capacities, topology legality, link-rate adoption, timeout validation, and reward aggregation helper semantics.

## Inputs

- Approved assumption snapshot from Feature 031.
- Feature 031 assumption registry JSON.
- Feature 031 assumption patch report JSON.

## Runtime Contract Rules

- Adopt `cpu_capacity_per_slot_agent = 0.5`, `cpu_capacity_per_slot_edge = 0.5`, and `cpu_capacity_per_slot_cloud = 3.0`.
- Load Figure 7 adjacency directly from the approved registry snapshot.
- Enforce neighbor-only horizontal offload and forbid self-offload.
- Keep vertical/cloud offload legal independently of horizontal adjacency.
- Use `R_V = 10 Mbps` for cloud-facing vertical link rate.
- Use `timeout_slots = 20`, `slot_duration_seconds = 0.1`, and `timeout_seconds = 2.0`.
- Aggregate rewards by per-agent episode terminal sum followed by arithmetic mean across agents.
- Exclude no-task, NaN, and omitted slots from numeric aggregation.
- Preserve delayed reward emission and do not change reward timing.

## Outputs

- Updated runtime configuration values.
- Updated topology legality results.
- Updated link-rate and timeout validations.
- Updated shared aggregation helper behavior.
- Adoption report with provenance and validation evidence.

## Non-Goals

- No training changes.
- No neural-network changes.
- No dependency changes.
- No campaign reruns.
- No paper-recovery claims.

