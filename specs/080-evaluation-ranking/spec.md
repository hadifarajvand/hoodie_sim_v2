# Feature 080 - HOODIE Proposed Method Implementation

## Goal

Implement and model the proposed method from the base HOODIE paper before ranking.

Feature 080 is no longer an evaluation-ranking feature. Ranking must wait until HOODIE_PROPOSED is implemented faithfully enough.

## Target

Target method: HOODIE_PROPOSED.

This means the proposed method from the base HOODIE paper only.

## Paper Components

Required components:
- hybrid local horizontal vertical action model
- private queue timing
- offloading queue timing
- public queue timing
- reward cost model
- distributed edge-agent decision model
- DQN interface
- Double DQN target rule
- Dueling DQN value advantage interface
- LSTM forecast interface
- replay memory interface
- epsilon greedy training schedule
- inference mode with epsilon zero
- Pub Sub recovery metadata

## Core Formula Set

Action:
- a_n(t) = [d_n^(1)(t), D_n(t)]

Reward:
- no task: omitted
- success: -Phi_n(t)
- thrown: -C

Local cost:
- Phi_priv = psi_priv - t + 1

Offloaded cost:
- Phi_pub = destination completion delay from task arrival

Learning:
- target values use Double DQN rule
- loss uses MSE between target and predicted Q values

## Output

- HOODIE proposed method model
- formula registry
- component coverage report
- implementation gap report
- readiness report

## Rules

- do not rank policies
- do not evaluate baselines
- do not introduce thesis method
- do not use DCQ
- do not claim full reproduction unless all required components pass

## Boundary

Feature 080 prepares HOODIE_PROPOSED for later evaluation.
