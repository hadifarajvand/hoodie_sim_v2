# Paper Queue Contract

## Queue Semantics

- private queue
- offloading queue
- public queue
- public queue manager

## Public CPU Sharing

Target behavior:

- equal active-queue sharing if supported by the paper contract

Current baseline behavior:

- priority-weighted sharing

That baseline behavior is a known gap and must not be described as paper-faithful.

## Completion vs Timeout

- completion and timeout must be distinct outcomes
- queue exit is not enough to declare final task completion

