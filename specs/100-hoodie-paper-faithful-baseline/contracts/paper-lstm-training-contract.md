# Paper LSTM and Training Contract

## Current Baseline Behavior

- LSTM is embedded inside DQN input handling.
- It is not exposed as a separate auditable forecasting/history pipeline.

## Target Behavior

- the runtime must expose auditable history inputs
- forecasting history must be inspectable
- LSTM use must be traceable in the training pipeline

## Training Requirements

- DQN / DDQN / Dueling DQN behavior must be specified
- replay memory contract must be explicit
- checkpoint contract must be explicit
- training trace contract must be explicit

