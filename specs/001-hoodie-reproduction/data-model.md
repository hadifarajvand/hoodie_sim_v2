# Data Model: 001-hoodie-reproduction

## Task

- Fields: task id, source agent, arrival slot, size, processing density, timeout length, absolute
  deadline slot, selected action, resolved destination, queue state, start slot, completion slot,
  terminal outcome, reward-emitted state, and drop flag.
- Relationships: belongs to one source agent; may move through offloading queue, private queue, or a
  public queue; is replayable through the trace bank or paired-seed protocol; is evaluated by the
  shared environment and evaluation module.

## EdgeAgent

- Fields: agent id, local queue, offloading queue, set of public queues it can host, topology links,
  current workload snapshot.
- Relationships: owns or hosts tasks; emits actions through the shared policy interface.

## CloudNode

- Fields: node id, public queue set, processing capacity, reachable sources.
- Relationships: receives vertically offloaded tasks and participates in evaluation on the same
  metrics as edge agents.

## PrivateQueue

- Fields: owning agent id, ordered task list, current head task, waiting time state.
- Relationships: contains locally computed tasks for a single agent.

## PublicQueue

- Fields: host node id, source agent id, ordered task list, current head task, waiting time state,
  and routing label.
- Relationships: receives horizontally or vertically offloaded tasks that are routed by source agent;
  identity is uniquely determined by the (host_node_id, source_agent_id) pair so different sources
  can be tracked distinctly on the same host; FIFO order is preserved within each queue.

## OffloadingQueue

- Fields: owning agent id, ordered task list, resolved destination, transmission state.
- Relationships: holds tasks after action selection has resolved the destination; it represents
  waiting for transmission or service rather than deferred routing choice.

## TopologyGraph

- Fields: node set, legal adjacency, source-to-destination legality rules.
- Relationships: constrains which actions are valid for each source agent.

## Environment

- Fields: current slot, active tasks, queues, topology, trace mode, seed identifiers, episode state,
  and pending reward state.
- Relationships: owns the lifecycle of all tasks and mediates all policy actions.

## Policy

- Fields: policy name, decision scope, action set, trace compatibility flag.
- Relationships: consumes the environment observation and returns an action for the current task.

## Evaluation Module

- Fields: run identifiers, trace identifiers, seed identifiers, raw metrics, per-trace metrics,
  aggregate metrics, plot inputs.
- Relationships: consumes shared simulator outputs and produces comparable metrics for baselines and
  HOODIE.

## State Transitions

- Task: created -> queued -> executing -> completed or dropped, with reward state emitted after the
  terminal outcome is known.
- Queue item: pending -> admitted -> serviced -> completed or dropped.
- Episode: initialized -> running -> finalized.
