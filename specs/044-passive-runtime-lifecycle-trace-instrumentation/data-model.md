# Data Model: Passive Runtime Lifecycle Trace Instrumentation

## LifecycleTraceEvent

- **Purpose**: Represent one passive lifecycle moment observed during a simulator run.
- **Fields**:
  - `event_type`
  - `slot`
  - `task_id`
  - `source_agent_id`
  - `selected_action`
  - `destination`
  - `queue_type`
  - `host_node_id`
  - `arrival_slot`
  - `absolute_deadline_slot`
  - `task_age_slots`
  - `size_mbits`
  - `processing_density_gcycles_per_mbit`
  - `cycles_required_gcycles`
  - `cycles_before_gcycles`
  - `cycles_consumed_gcycles`
  - `cycles_after_gcycles`
  - `compute_capacity_gcycles_per_slot`
  - `transmission_started_at`
  - `transmission_completed_at`
  - `transmission_delay_slots`
  - `terminal_outcome`
  - `reward`
  - `reward_available`
  - `pending_at_horizon`
  - `legality_snapshot`
  - `trace_source_component`
- **Validation rules**:
  - Events MUST be passive and reflect observed simulator state only.
  - Fields MAY be omitted when they are not applicable to the event type, but the schema must remain stable.
  - `execution_progress` events MUST include cycle before/after accounting and capacity for the slot.

## LifecycleTraceRecorder

- **Purpose**: Collect passive trace events during a run.
- **Fields**:
  - `enabled`
  - `events`
  - `source_component_name`
  - `run_id`
  - `seed`
  - `paper_default_runtime_tag`
- **Relationships**:
  - Owns a sequence of `LifecycleTraceEvent` records.
  - Is read by the analysis runner and report builder after a run completes.
- **Validation rules**:
  - Recorder MUST be opt-in and disabled by default where feasible.
  - Recorder MUST not mutate task outcomes, reward timing, or execution state.

## TraceCoverageSummary

- **Purpose**: Summarize whether the trace observed enough lifecycle stages to support Feature 043 diagnosis.
- **Fields**:
  - `generated_observed`
  - `admitted_observed`
  - `transmission_observed`
  - `execution_observed`
  - `completion_observed`
  - `drop_observed`
  - `reward_observed`
  - `pending_observed`
  - `ordering_resolved`
- **Validation rules**:
  - Summary MUST distinguish incomplete evidence from confirmed ordering.

## InstrumentationReadinessReport

- **Purpose**: State whether trace evidence is sufficient for downstream diagnosis.
- **Fields**:
  - `feature_id`
  - `trace_coverage_summary`
  - `behavior_equivalence_checks`
  - `trace_sources`
  - `completion_diagnosis_readiness`
  - `final_verdict`
- **Validation rules**:
  - Report MUST not claim paper reproduction.
  - Report MUST not imply runtime repair occurred.
