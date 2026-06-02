# Validation Rules for Feature 080 — HOODIE Proposed Method Implementation

## Validation Checks
1. Action vector consistency: [local/offload, destination].
2. Queue timing and completion logic correctness.
3. Reward/cost computation correctness.
4. DQN, Double DQN, Dueling DQN, LSTM interfaces implemented.
5. Replay memory batching.
6. Epsilon-greedy schedule observed.
7. Inference mode epsilon=0.
8. Pub-Sub metadata handling.

## Notes
- All checks enforce base paper fidelity.
- No DCQ or thesis extensions.