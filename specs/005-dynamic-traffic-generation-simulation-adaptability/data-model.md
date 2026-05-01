# Data Model: Dynamic Traffic Generation & Simulation Adaptability

## Entities

### TrafficConfig

- **Fields**: `scenario_name`, `number_of_agents`, `episode_length`, `arrival_probability`, `slot_duration_seconds`, `timeout_slots`, `task_size_mbits_min`, `task_size_mbits_max`, `task_size_mbits_step`, `processing_density_gcycles_per_mbit`
- **Relationships**: Owns one preset definition and parameterizes one generated traffic trace.
- **Validation rules**: `scenario_name` must be one of the approved scenario presets; `arrival_probability` must be in `[0, 1]`; the size range must be ordered and step-aligned.

### TrafficScenarioPreset

- **Fields**: preset name plus a factory that returns a validated `TrafficConfig`
- **Relationships**: Maps the paper-backed presets to executable traffic configurations.
- **Validation rules**: `paper_default`, `moderate`, `heavy`, and `extreme` are the only accepted feature presets.

### TrafficTaskRecord

- **Fields**: `task_id`, `source_agent_id`, `arrival_slot`, `size`, `processing_density`, `timeout_length`, `absolute_deadline_slot`
- **Relationships**: Represents one Bernoulli-arrival task and maps directly to a `TraceTaskBlueprint` entry for environment consumption.
- **Validation rules**: Exactly one task is created for each successful Bernoulli trial; `arrival_slot` must be within the configured episode horizon; `absolute_deadline_slot` must be derived from the configured timeout.

### TrafficTrace

- **Fields**: `trace_id`, `seed`, `config`, `records`, `metadata`, `evaluation_trace`, `summary`
- **Relationships**: Owns the generated workload, trace metadata, the compatibility evaluation trace, and the summary metadata used by observability and tests.
- **Validation rules**: Records must be sorted deterministically by `arrival_slot`, `source_agent_id`, and `task_id`.

### TrafficSummary

- **Fields**: `scenario_name`, `seed`, `configured_arrival_probability`, `observed_arrival_probability`, `total_arrivals`, `arrivals_per_slot`, `arrivals_per_agent`, `task_size_mbits_range`
- **Relationships**: Derived from a generated trace and reused by quickstart, tests, and future adaptability features.
- **Validation rules**: `observed_arrival_probability = total_arrivals / (number_of_agents × episode_length)` for full-trace summaries.

### RollingTrafficSummary

- **Fields**: `window_slots`, `start_slot`, `end_slot`, `summary`
- **Relationships**: Optional view over `TrafficTrace.records` for future traffic-intensity inspection.
- **Validation rules**: The window must be clipped to available history rather than inventing missing data.

### EvaluationTrace compatibility carrier

- **Fields**: existing `trace_id`, `seed`, `tasks`, `metadata`
- **Relationships**: Serves as the existing environment-compatible workload surface for `HoodieGymEnvironment.reset(seed)`.
- **Validation rules**: The generated `tasks` tuple must contain the same deterministic ordering as `TrafficTrace.records`.

## State transitions

1. `TrafficConfig` or `TrafficScenarioPreset` is selected.
2. `TrafficGenerator` samples Bernoulli arrivals for every agent and slot.
3. The generator builds `TrafficTaskRecord` entries and sorts them deterministically.
4. `TrafficTrace` packages the records, summary, and `EvaluationTrace` compatibility payload.
5. `TraceSource` or the equivalent existing trace interface hands the workload to `HoodieGymEnvironment.reset(seed)`.
6. `HoodieGymEnvironment.step(action)` consumes the workload without any lifecycle change.

## Compatibility rules

- Paper traffic values are carried directly in the trace path; no hidden scaling factor is introduced.
- The generator does not own environment lifecycle control.
- Same-slot arrivals remain serialized by the existing environment ordering.
- The traffic observability layer reports load, not model switching.
