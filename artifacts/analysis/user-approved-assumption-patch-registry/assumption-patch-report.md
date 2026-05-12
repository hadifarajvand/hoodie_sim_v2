# User-Approved Assumption Patch Registry Report

- feature_id: `031-user-approved-assumption-patch-registry`
- schema_version: `1.0.0`
- registry_path: `resources/papers/hoodie/recovered/user-approved-assumption-registry.json`
- item_count: `8`
- final_verdict: `registry_created_with_runtime_approved_assumptions`

## Status Counts
- approved: `3`
- blocked_no_assumption: `1`
- proposed: `4`
- rejected: `0`

## Blocked Items
- `timeout_value` | `blocked_no_assumption` | runtime_use_allowed=False

## Proposed Items
- `EA_public_cpu_capacity` | `cpu_capacity_per_slot_edge = 64.0` | runtime_use_allowed=False
- `cloud_cpu_capacity` | `cpu_capacity_per_slot_cloud = 128.0` | runtime_use_allowed=False
- `cloud_data_rate` | `vertical data-rate assumption = 10 Mbps` | runtime_use_allowed=False
- `multi_agent_aggregation_reduction_order` | `sum rewards per agent per episode, then arithmetic mean across agents` | runtime_use_allowed=False

## Runtime-Usable Items
- `Figure_7_adjacency`
- `legal_horizontal_destinations`
- `EA_private_cpu_capacity`

## Final Verdict
registry_created_with_runtime_approved_assumptions
