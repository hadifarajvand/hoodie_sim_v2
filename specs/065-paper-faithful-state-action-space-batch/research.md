# Research: Feature 065

## Decision: repair state/action contracts before training migration

Feature 065 repairs the paper-facing state and action contracts before any training migration work. It is a contract and adapter feature, not a training feature.

## Decision: destination-specific actions are mandatory

The paper-facing action space must map to exact destinations, not only family-level labels. Feature 066 will bind training to this contract.

## Decision: load history is `W × (N+1)`

The load-history contract must expose a `W × (N+1)` matrix with `W = 10` by default and `N = 20` edge agents plus Cloud.

## Decision: waiting-time exactness must be reported

Waiting-time values may use deterministic queue-head approximations if exact queue timestamps are not available, but exactness and source must be reported explicitly.

