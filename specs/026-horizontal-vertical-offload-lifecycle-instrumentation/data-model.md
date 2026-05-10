# Data Model: Horizontal and Vertical Offload Lifecycle Instrumentation

## Offload Lifecycle Trace

Represents a task path trace with ordered lifecycle events.

### Fields
- `trace_id`: stable identifier for the trace
- `case_id`: differential audit case name
- `path_type`: horizontal or vertical offload
- `event_sequence`: ordered list of lifecycle events
- `event_payloads`: event-specific metadata for provenance and timing
- `final_outcome`: completed, dropped_timeout, or incomplete

### Validation Rules
- Event ordering must remain deterministic.
- The required event names must be representable without changing reward values or policy decisions.
- Missing later lifecycle events must be recorded as incomplete rather than flattened into a generic unsupported case.

## Instrumentation Summary

Represents the frozen audit summary for the feature.

### Fields
- `schema_version`
- `visible_events`
- `incomplete_events`
- `regression_checks`
- `remaining_blockers`
- `no_behavior_change_verified`
- `topology_boundaries_preserved`

### Validation Rules
- Must clearly separate observability gaps from topology or legality gaps.
- Must include explicit residual blockers if they remain after trace exposure.
- Must confirm whether rewards, metrics, and policy decisions were unchanged in equivalent execution.

## Audit Case

Represents one differential environment audit scenario.

### Fields
- `case_name`
- `classification_before`
- `classification_after`
- `visibility_status`
- `topology_status`
- `notes`

### Validation Rules
- Offload cases may move away from unsupported-trace only when observability is improved.
- Residual topology or legality blockers must be stated explicitly and not conflated with trace visibility.

