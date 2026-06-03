# Tasks for Feature 080 — HOODIE Proposed Method Implementation

Status summary: implemented 9, partial 1, missing 0.

## Implemented

1. [x] Implement hybrid action selection (local/horizontal/vertical).
2. [x] Implement private queue timing and completion logic.
3. [x] Implement offloading/public queue timing and processing logic.
4. [x] Implement reward and cost computation: Phi_priv, Phi_pub, drop cost C.
7. [x] Implement replay memory and batch sampling.
8. [x] Implement epsilon-greedy training schedule.
9. [x] Implement inference mode with epsilon=0.
10. [x] Implement Pub-Sub metadata handling.

## Partial

5. [x] Implement DQN interfaces, Double DQN target, Dueling DQN value/advantage.
6. [ ] Implement LSTM forecast/recovery interface. [partial]

## Missing

- None.

## Notes

- All tasks strictly follow the base HOODIE paper.
- No thesis/DCQ extensions included.
- Within task 5, the DQN interface, Double DQN target, and Dueling DQN value/advantage interface are implemented; only LSTM remains partial.
- Within task 8, the epsilon-greedy training schedule is now implemented; it still does not imply a full trainable learner stack.
