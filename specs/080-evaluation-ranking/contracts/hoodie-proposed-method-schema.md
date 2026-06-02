# HOODIE Proposed Method Schema — Contracts

Defines the interface contracts for Feature 080 implementation.

## Data Contracts
- Task: id, size, type, deadline, arrival_time
- Edge Agent: node_id, queue_states, CPU_slots
- Queues: private, offloading, public
- Action: [local/offload, destination]
- Reward/Cost: Phi_priv(t), Phi_pub(t), drop cost C

## Interface Contracts
- DQN, Double DQN, Dueling DQN, LSTM must follow base paper interface.
- Replay memory interface.
- Epsilon-greedy training schedule.
- Inference mode epsilon=0.

## Notes
- All contracts enforce fidelity to base HOODIE paper.
- No thesis/DCQ modifications.