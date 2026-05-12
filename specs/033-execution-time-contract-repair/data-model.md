# Data Model: Execution-Time Contract Repair

## ExecutionProgressRecord

- **task_id**: Identifier of the task being advanced
- **slot**: Simulator slot in which execution progress occurred
- **destination_kind**: One of local/private/self, public/edge/horizontal, cloud/vertical
- **cycles_before**: Remaining cycles before the slot
- **cycles_consumed**: Cycles consumed in the slot
- **cycles_after**: Remaining cycles after the slot
- **completed**: Whether the task is complete at the end of the slot

## Task Cycle State

- **cycles_required**: Total cycles required by the task
- **cycles_remaining**: Cycles still required after partial execution
- **completion_slot**: Slot in which completion is recorded
- **terminal_outcome**: Completed or dropped once resolved
- **reward_emitted**: Whether reward has already been emitted

## Destination Kind

- **local/private/self**: Uses the agent/private capacity
- **public/edge/horizontal**: Uses the public/edge capacity
- **cloud/vertical**: Uses the cloud capacity

## Validation Rules

- Cycles consumed in a slot cannot exceed the configured capacity for that destination kind.
- Cycles remaining must decrease monotonically until completion.
- Completion is recorded at the end of the slot where remaining cycles reach zero.
- Terminal outcome and reward emission remain gated by completion or drop.

