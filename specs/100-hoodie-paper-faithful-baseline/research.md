# Research Summary

## What Phase 0.3 Established

The Phase 0.3 audit established that the current promoted baseline is a legacy HOODIE simulator stack, not a paper-faithful runtime implementation.

Key facts:

- the core runtime files match the promoted baseline snapshot exactly
- public queue CPU sharing is priority-weighted
- reward is step-aggregated
- LSTM is embedded in DQN input handling
- no figure-generation workflow is present
- no 200-episode validation mode is present

## What Remains Unresolved

- no explicit paper-faithful slot/drain runtime contract
- no delayed reward attribution
- no auditable historical load pipeline
- no Figure 7 topology contract artifact
- no verified baseline registry for the paper baselines
- no first-class validation workflow for 200 episodes

## Why This Spec Exists

This spec package exists to freeze the paper-faithful target before simulator changes are attempted. It is a contract, not an implementation.

