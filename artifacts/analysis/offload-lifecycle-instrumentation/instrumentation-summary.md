# Offload Lifecycle Instrumentation Summary

- schema_version: `1.0`
- no_behavior_change_verified: `True`
- topology_boundaries_preserved: `True`

## Visible Events
- `selected_action`
- `queued_public`
- `offloaded_cloud`
- `transmission_started`
- `transmission_completed`
- `execution_started`
- `execution_completed`
- `dropped_timeout`
- `reward_emitted`

## Incomplete Events
- `case-horizontal-offload`
- `case-vertical-offload`

## Regression Checks
- `feature_019`: `preserved`
- `feature_024`: `preserved`
- `figure_7_topology`: `unrecoverable`

## Remaining Blockers
- Topology-backed destination required for offload actions
- Topology-backed destination required for offload actions
