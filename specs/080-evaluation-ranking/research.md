# Research Notes for Feature 080 — HOODIE Proposed Method Implementation

This file documents the research references and notes necessary for implementing the HOODIE proposed method.

## References
- HOODIE paper: Hybrid Computation Offloading via Distributed Deep Reinforcement Learning in Delay-Aware Cloud-Edge Continuum
- OCR extraction notes

## Observations
- Hybrid offloading: local, horizontal, vertical
- Queue management: private (FIFO), offloaded/public (FIFO)
- Distributed DRL agents: DQN, Double DQN, Dueling DQN, LSTM
- Reward: delay cost Phi, drop cost C

## Notes
- Ensure fidelity with paper definitions.
- Do not include DCQ or thesis-related methods.