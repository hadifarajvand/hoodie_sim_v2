# Feature Specification: 067 — Paper Traffic, Queue, and Communication Fidelity Batch

## Intent

Upgrade simulator fidelity toward the HOODIE paper’s traffic, queue, timeout, link-delay, and inter-agent communication model.

## Scope

- Bernoulli task arrivals per Edge Agent per slot
- Paper task-size set and processing-density contract
- Timeout semantics aligned to `arrival_slot + timeout_phi - 1`
- Per-link horizontal and vertical delay model
- Edge Controller / Pub-Sub load-sharing abstraction
- Delayed-message recovery using previous LSTM/queue values
- Queue-fidelity compatibility with Features 065 and 066

## Non-Goals

- No paper reproduction claim
- No unsupported superiority claim
- No uncontrolled training campaign
- No dependency changes

