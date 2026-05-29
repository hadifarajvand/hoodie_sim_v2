# Feature Specification: 066 — Distributed Multi-Agent HOODIE Training Batch

## Intent

Migrate the training surface from the simplified single-trainer legacy contract to a paper-faithful distributed multi-agent HOODIE training contract using the Feature 065 state/action interfaces.

## Scope

- One DDQN model per Edge Agent
- Per-agent replay memory, policy, optimizer, and target network
- Paper-style epsilon-greedy schedule
- Shared-environment coordination layer
- Delayed reward assignment to the originating agent

## Non-Goals

- No paper reproduction claim
- No unsupported superiority claim
- No uncontrolled long training campaign
- No dependency changes

