# Offload Lifecycle Instrumentation Summary

- schema_version: `1.0`
- paper_topology_status: `unrecoverable`
- no_paper_topology_fabrication: `True`
- no_behavior_change_verified: `True`
- topology_boundaries_preserved: `True`

## Schema Supported Events
- `selected_action`
- `queued_public`
- `offloaded_cloud`
- `transmission_started`
- `transmission_completed`
- `execution_started`
- `execution_completed`
- `dropped_timeout`
- `reward_emitted`

## Observed Default Audit Events
- `created`
- `selected_action:horizontal`
- `selected_action:vertical`
- `created`
- `created`
- `created`

## Observed Synthetic Fixture Events
- `horizontal`: selected_action, queued_public, transmission_started, transmission_completed, execution_started, execution_completed, reward_emitted, dropped_timeout
- `vertical`: selected_action, offloaded_cloud, transmission_started, transmission_completed, execution_started, execution_completed, reward_emitted, dropped_timeout

## Default Runtime Classification
- `case-horizontal-offload`: `blocked_by_runtime_topology_or_destination_fixture`
- `case-vertical-offload`: `blocked_by_runtime_topology_or_destination_fixture`

## Synthetic Fixture Trace Visibility
- `horizontal`: `fixture-backed lifecycle events observed beyond selected_action`
- `vertical`: `fixture-backed lifecycle events observed beyond selected_action`

## Regression Checks
- `feature_019`: `preserved`
- `feature_024`: `preserved`
- `figure_7_topology`: `unrecoverable`

## Remaining Topology Blockers
- Topology-backed destination required for offload actions
- Topology-backed destination required for offload actions
