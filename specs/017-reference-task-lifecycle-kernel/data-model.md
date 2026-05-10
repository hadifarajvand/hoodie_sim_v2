# Data Model: Reference Task Lifecycle Kernel

## Entities

### TaskIdentity

- **Purpose**: Stable identity for one hand-fed task.
- **Fields**:
  - `task_id`: deterministic identifier within the test fixture
  - `origin_edge_agent`: source edge-agent identifier
  - `destination_target`: local, peer edge agent, or cloud target
- **Relationships**: Owned by a single lifecycle trace and referenced by every ledger event for that task.
- **Validation Rules**:
  - Must be stable across a replay of the same test case.
  - Must be unique within a single ledger.

### TaskWorkload

- **Purpose**: Abstract workload inputs required for the reference lifecycle.
- **Fields**:
  - `task_size`: abstract work units or size token
  - `timeout_slot`: deterministic timeout boundary for the task
  - `current_slot`: current deterministic slot used by the test harness
- **Relationships**: Attached to `TaskIdentity`.
- **Validation Rules**:
  - Timeout slot must be comparable to the current slot.
  - Workload values are reference inputs, not simulator truth claims.

### ActionInput

- **Purpose**: Hand-fed action value passed into the transition API.
- **Fields**:
  - `action_type`: local compute, horizontal offload, or vertical offload
  - `destination_target`: local, peer edge agent, or cloud target as applicable
- **Relationships**: Applied to one task at a time.
- **Validation Rules**:
  - Must not encode policy selection.
  - Must not imply a learned agent.

### LedgerEvent

- **Purpose**: One deterministic observable event in the lifecycle ledger.
- **Fields**:
  - `sequence_index`: stable order position within the ledger
  - `slot`: slot in which the event occurred
  - `event_type`: created, selected_action, queued_private, queued_public, offloaded_cloud, transmission_started, transmission_completed, execution_started, execution_completed, dropped_timeout, or reward_emitted
  - `task_id`: reference to the task identity
  - `status`: optional terminal or in-flight state marker
- **Relationships**: Collected into a `TaskLedger`.
- **Validation Rules**:
  - Sequence indexes must be strictly increasing within one ledger.
  - Terminal events must appear at the end of the trace.

### TaskLedger

- **Purpose**: The ordered ledger emitted by the reference model.
- **Fields**:
  - `task_id`
  - `events`
  - `terminal_status`
  - `reward_emitted`
- **Relationships**: Contains many `LedgerEvent` items.
- **Validation Rules**:
  - Must be deterministic for identical inputs.
  - Must preserve the reference order defined in the spec.

## State Transitions

1. `created` initializes the ledger.
2. `selected_action` records the hand-fed action.
3. The path-specific lifecycle advances through queue, transmission, and execution events.
4. The terminal event is either `execution_completed` or `dropped_timeout`.
5. `reward_emitted` occurs only after the terminal event in the same terminal slot.

## Determinism Rules

- Same inputs must produce the same event sequence and the same terminal state.
- Same-slot ties must use a stable, documented sort rule.
- No hidden state may influence ledger ordering.

