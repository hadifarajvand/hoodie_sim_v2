# Data Model: Feature 068

## BaselinePolicy

A policy implementation for one paper baseline.

Fields:

- name
- action selection rule
- deterministic or seeded behavior
- legal action handling

## PolicyContext

Shared policy input.

Fields:

- observation
- legal action mask
- trace history

## DelayCandidate

A candidate action used by MLEO.

Fields:

- action name
- legality
- queue delay
- transmission delay
- compute delay
- total delay
- fallback flag
- fallback reason

Rules:

- illegal candidates are excluded before ranking
- ranked candidates must have comparable total delay
- fallback use must be visible and tested

## BaselineFidelityReport

A small validation summary for baseline behavior.

Fields:

- baseline names
- registry status
- legality status
- differentiation status
- MLEO candidate summary
