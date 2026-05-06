# Clarifications: Adaptive Policy and Offloading Decisions

## Scope Locks

- No DRL training, TorchRL, neural-network, replay-learning, LSTM, or model-switching changes are part of this feature.
- The adaptive policy is external to `HoodieGymEnvironment`; the environment does not execute policy logic internally.
- Illegal actions must not be silently remapped.
- Missing adaptive inputs must fall back deterministically to the canonical legal-action order.
- Any ranking heuristic that is not recovered directly from the paper must be documented as a conservative baseline, not as learned HOODIE behavior.
