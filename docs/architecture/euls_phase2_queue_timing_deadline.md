# EULS Phase 2 Queue, Timing, and Deadline Checklist

Phase 2 improves EULS queue/timing/deadline fidelity.
It does not yet claim full HOODIE Figures 8-11 reproduction.

## Current runtime lifecycle order

1. Accept the current action for the current task.
2. Admit the task into the relevant queue.
3. Progress offloading queues.
4. Progress execution queues.
5. Finalize terminal tasks and stage delayed reward.
6. Advance the slot counter.
7. Load the next eligible task.
8. Compute termination and truncation.

## Target Phase 2 lifecycle order

1. Accept the current action for the current task.
2. Admit the task into the relevant queue.
3. Sweep expirations deterministically at the current slot boundary.
4. Progress offloading queues.
5. Progress execution queues using slot-start eligible heads only.
6. Finalize terminal tasks and stage delayed reward.
7. Advance the slot counter.
8. Load the next eligible task.
9. Compute termination and truncation.

## Private queue semantics

- FIFO only.
- Local tasks may execute in the slot they are admitted if service is available.
- A later local task must not overtake an earlier local task.
- Expired waiting tasks must be dropped deterministically.

## Offloading queue semantics

- FIFO only.
- Offload admission is deterministic.
- Transmission completion should not grant same-slot public execution.
- Expired offloading heads must be dropped before public admission.

## Public and cloud queue semantics

- Public queues are source-indexed by originating EA.
- Cloud public queues preserve source identity.
- Service allocation is based on active heads at slot start.
- Newly admitted public tasks are not eligible for same-slot execution.
- A next head in the same queue must not receive same-slot service after the prior head completes.

## Deadline and drop semantics

- Tasks carry an absolute deadline.
- Expiration is deterministic and explicit.
- A task that misses the deadline is dropped and later completion is forbidden.
- Waiting tasks must not remain indefinitely after expiration.

## Delayed reward semantics

- Reward is emitted only after a terminal outcome exists.
- Reward is emitted once per terminal task.
- Terminal tasks are staged through pending reward emission before termination.
- Metrics must not double-count terminal outcomes or rewards.

## Termination and truncation semantics

- Terminated means no pending arrivals, no current task, no queued work, and no pending terminal rewards.
- Truncated means the slot horizon was reached before semantic completion.

## Known assumptions still deferred

- Exact paper-level public admission timing may need further audit.
- Fine-grained cloud scheduling evidence may still need tightening.
- Waiting-time and timeout semantics outside the queue heads are conservatively treated only where proven by tests.

## Explicitly not included in Phase 2

- DAL.
- DRL training changes.
- LSTM or recurrent policy changes.
- Figure 8-11 generation.
- New policy algorithms.
- DM1/DM2 restructuring.
- Baseline campaign repair.
- Paper result claims.
