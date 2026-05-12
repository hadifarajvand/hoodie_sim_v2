# User-Approved Assumption Patch Registry Report

- feature_id: `031-user-approved-assumption-patch-registry`
- schema_version: `1.0.0`
- registry_path: `resources/papers/hoodie/recovered/user-approved-assumption-registry.json`
- item_count: `8`
- final_verdict: `registry_created_no_runtime_approved_assumptions`

## Status Counts
- approved: `0`
- blocked_no_assumption: `3`
- proposed: `5`
- rejected: `0`

## Blocked Items
- `Figure_7_adjacency` | `blocked_no_assumption` | runtime_use_allowed=False
- `legal_horizontal_destinations` | `blocked_no_assumption` | runtime_use_allowed=False
- `timeout_value` | `blocked_no_assumption` | runtime_use_allowed=False

## Proposed Items
- `EA_private_cpu_capacity` | `cpu_capacity_per_slot_agent = 32.0` | runtime_use_allowed=False
- `EA_public_cpu_capacity` | `cpu_capacity_per_slot_edge = 64.0` | runtime_use_allowed=False
- `cloud_cpu_capacity` | `cpu_capacity_per_slot_cloud = 128.0` | runtime_use_allowed=False
- `cloud_data_rate` | `vertical data-rate assumption = 10 Mbps` | runtime_use_allowed=False
- `multi_agent_aggregation_reduction_order` | `sum rewards per agent per episode, then arithmetic mean across agents` | runtime_use_allowed=False

## Runtime-Usable Items
- none

## Final Verdict
registry_created_no_runtime_approved_assumptions
