# HOODIE Paper Simulation Reference Index

This directory is the canonical implementation reference for reproducing the HOODIE paper simulation process.

Read these files before changing HOODIE runtime, queue, policy, reward, training, validation, baseline, metric, or figure-generation behavior.

## Files

1. `01_system_and_runtime.md`
   - Cloud-Edge Continuum topology
   - Edge Agent internal structure
   - time-slotted episode model
   - task arrival model
   - task features
   - two-level action model

2. `02_queue_reward_state_model.md`
   - private queue
   - offloading queue
   - public queue
   - active public queue CPU sharing
   - historical load matrix
   - LSTM load forecast
   - state vector
   - delayed reward collection

3. `03_training_validation_and_figures.md`
   - DQN/DDQN/Dueling/LSTM training loop
   - epsilon-greedy schedule
   - inference mode
   - Table 4 parameters
   - Figure 8, Figure 9, Figure 10, Figure 11 requirements
   - official baselines
   - minimum faithful checklist

## Hard Rule

Do not tune simulator outputs to resemble the paper. Implement the same simulation process and let the outputs emerge from the simulation.

Correct implementation target:

```text
paper-faithful runtime -> training/inference boundary -> validation episodes -> metrics -> figures
```

Wrong implementation target:

```text
current aggregates -> paper-shaped CSV -> paper-shaped plot
```
