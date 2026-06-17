# EULS Phase 7 DAL Advisory Layer

## Purpose

DAL is a deterministic advisory layer over EULS state. It estimates deadline pressure, queue pressure, and rough action-family feasibility signals for use by future policies or learners.

DAL is advisory only. It does not select actions, mutate runtime state, or participate in training.

## Boundary

DAL owns:

- deadline pressure estimation
- remaining slack / urgency indicators
- queue pressure indicators
- offload / public / cloud congestion indicators
- rough feasibility hints for local, horizontal, and vertical action families
- structured advisory payload generation
- deterministic advisory hashing compatibility when needed

DAL does not own:

- task admission
- queue mutation
- deadline or drop decisions
- terminal reward emission
- metrics counting
- policy optimization
- DRL training
- action masking legality
- final action selection
- Figures 8-11

## Inputs

DAL reads EULS state only:

- current slot
- current task
- absolute deadline slot
- private queue load
- offloading queue load
- public queue load
- total queue load
- queue identity and ordering state as exposed by EULS

## Outputs

DAL returns a deterministic advisory payload with:

- deadline pressure label
- remaining slack
- queue pressure counts
- feasibility labels
- advisory notes

## Read-only guarantee

DAL does not call EULS mutators and does not alter tasks, queues, rewards, metrics, traces, or selected actions.

## Deterministic guarantee

For the same EULS state and task, DAL produces the same advisory payload.

## Replay compatibility

Calling DAL must not change EULS replay payloads or hashes.

## Non-inclusions

- no policy training
- no optimizer execution
- no reward shaping
- no queue admission changes
- no deadline policy changes
- no paper reproduction claim

## Phase 8+ integration plan

Future phases may connect DAL advisories to a policy or learner as an input-only signal, but the advisory layer remains separate from EULS execution.
