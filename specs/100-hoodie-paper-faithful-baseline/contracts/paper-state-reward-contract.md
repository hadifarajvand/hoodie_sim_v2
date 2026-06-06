# Paper State and Reward Contract

## State Vector

- task features
- queue features
- historical load features
- action trace context

## Task Feature Vector

- task size
- arrival slot
- deadline slot
- source id
- selected action

## Queue Feature Vector

- private waiting time
- offloading waiting time
- public queue footprint
- active public queue count

## Historical Load Vector

- sliding load history over the last W slots

## Reward Contract

- rewards must be task-level and delayed
- each reward must be attributable to a specific task and action

## Why Step-Aggregated Reward Is Insufficient

Step-aggregated reward cannot prove:

- which task completed
- which task timed out
- which action caused the event
- when the reward should have been collected

That is insufficient for audit-grade paper fidelity.

