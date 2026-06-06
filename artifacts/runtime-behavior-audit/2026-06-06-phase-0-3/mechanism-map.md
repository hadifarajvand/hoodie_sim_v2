# Mechanism Map

## 1. Vehicle / Task Generation

Present:

- `environment/task_generator.py` emits Bernoulli arrivals per server.
- `environment/task.py` stores size, arrival time, timeout, priority, density, drop penalty, origin, and target.

Not auditable enough:

- No explicit task lifecycle event log.
- No paper-style arrival diagnostics artifact.
- No per-task trace export.

## 2. Edge / Cloud Continuum

Present:

- `environment/server.py` creates private queue, offloading queue, and public queue manager.
- `environment/cloud.py` wraps a public queue manager over all servers.

Not auditable enough:

- Cloud semantics are aggregated, not a paper-contract runtime model.
- No explicit topology mode or Figure 7 contract representation.

## 3. Hybrid Offloading

Present:

- `environment/matchmaker.py` maps action indices to local or reachable offload targets.
- `environment/server.py` routes local vs offloaded tasks.

Missing / under-specified:

- No explicit paper legality contract.
- No source-specific public queue trace.
- No separate vertical offload model beyond discrete target selection.

## 4. Distributed / Multi-Agent DRL

Present:

- `decision_makers/agent.py` implements per-server DQN agents.
- Replay buffer, target network, epsilon-greedy policy, and LSTM history exist.

Not auditable enough:

- No training run manifest for paper figures.
- No 200-episode validation mode.
- No explicit separation between baseline policy logic and paper baselines.

## 5. Delay-Aware Decision-Making

Present:

- `decision_makers/rule_based.py` compares local versus foreign wait/service estimates.

Under-specified:

- Heuristic is not a paper-validated delay policy.
- No task-level delayed reward trace.

## 6. Queue Model

Present:

- `environment/queues.py` has private, offloading, and public queues.
- Timeout dropping exists.
- Waiting time is tracked for private and offloading queues.

Critical mismatch:

- Public queue CPU sharing is priority-weighted, not equal active-queue sharing.

## 7. Deadline / Drop Behavior

Present:

- Tasks carry timeout and drop penalty.
- Queue code drops timed-out tasks and returns a reward scalar.

Not auditable enough:

- Drop is not a task-level event trace.
- Completion and drop are not separated into explicit audit records.

## 8. Resource Allocation

Present:

- Private CPU capacities, public CPU capacities, and cloud computational capacity are configured in JSON.

Missing:

- Explicit service-rate/slot model.
- Equal active queue split.
- Resource allocation trace exports.

## 9. Reward Design

Present:

- Reward is computed in the environment and stored in transitions.

Critical mismatch:

- Reward is step-aggregated, not delayed and task-traceable.

## 10. Metrics and Evaluation

Present:

- Smoke output prints configuration and accumulated epoch reward.
- A `scheduler.pth` artifact is written.

Missing:

- Figure-data export.
- Runtime audit metrics.
- Paper-claim evidence for Figures 8/9/10/11.

## 11. Baselines

Available decision makers:

- `Agent`
- `AllHorizontal`
- `AllLocal`
- `AllVertical`
- `Random`
- `RoundRobin`
- `RuleBased`
- `SingleAgent`

Only some can be loosely mapped as proxies. Official baselines are **not** explicitly validated as:

- HOODIE
- RO
- FLC
- VO
- HO
- BCO
- MLEO

## 12. Reproducibility / Configuration

Present:

- JSON-driven hyperparameters.
- Scheduler serialization to `scheduler.pth`.

Not sufficient:

- No paper-faithful validation workflow.
- No explicit 200-episode evaluation contract.
- No figure-generation pipeline.

