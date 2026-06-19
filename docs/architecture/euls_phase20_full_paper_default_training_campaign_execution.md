# EULS Phase 20: Full Paper-Default Training Campaign Execution

## Starting branch

- Feature branch: `060-full-paper-default-training-campaign-execution-v2`
- Base branch: `060a-real-trainer-reduced-budget-campaign-execution-validation`

## Scope

Feature 060 is the full configured campaign gate for the paper-default training path.
It is constrained to evidence collection, artifact emission, and explicit readiness reporting.

## Prerequisite gates

- Feature 059 gate must be passed.
- Feature 060A real-trainer reduced-budget validation must be passed.
- Feature 058 evaluation trace bank and baseline harness must be passed.

## Campaign contract

- Configured training budget: 1000 episodes
- Configured evaluation budget: 100 episodes
- Configured baseline evaluation budget: 100 episodes
- Episode length: 110
- Real trainer: required
- Replay mutation: allowed only through the approved trainer path
- Checkpoint artifact: metadata only, no binary checkpoint commit

## Safety and exclusions

This feature does not claim paper reproduction or performance superiority.
It does not modify EULS runtime semantics, DAL behavior, replay hashing, or policy defaults.
It does not authorize Figures 8-11.

## Final decision

The report must honestly return either a full-campaign pass verdict or a blocked verdict.
