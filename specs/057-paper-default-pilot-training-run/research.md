# Research: Feature 057

## Decision: use a controlled three-episode pilot

Feature 055 used a one-episode smoke run. Feature 057 should use a small multi-episode pilot, with suggested defaults:

```text
pilot_episodes = 3
pilot_episode_length = 110
```

This is large enough to validate replay and optimizer growth beyond the smoke run, while still remaining below full-campaign scale.

## Decision: no baseline comparison

This pilot validates training mechanics only. It must not compare against baselines or claim performance.

## Decision: no paper reproduction claim

A pilot run is not a paper reproduction. It must route to evaluation harness work, not to reproduction reporting.

## Decision: metadata-only checkpoint evidence is acceptable

Feature 057 should validate checkpoint metadata schema and consistency. Saved model files are not required unless a later feature explicitly scopes checkpoint persistence.
