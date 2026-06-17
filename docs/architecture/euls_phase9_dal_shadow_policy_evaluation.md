# Phase 9 DAL Shadow Policy and Evaluation

Phase 9 adds a deterministic DAL shadow policy as an explicit opt-in consumer of DAL advisory metadata.

## Purpose

The shadow policy provides a safe evaluation path that can inspect `PolicyContext.dal_advisory` and return a legal action without training, optimization, or EULS mutation.

## Shadow-policy boundary

DAL remains advisory.
The DAL shadow policy is an explicit opt-in non-learning policy consumer.
It does not train and does not mutate EULS.

## Registry behavior

The policy registry now exposes an explicit `DAL_SHADOW` name.
Existing default policy names and aliases remain unchanged.
`DAL_SHADOW` is opt-in only and does not replace `HOODIE`, `FLC`, or any existing policy.

## Determinism guarantee

The shadow policy is deterministic for a given `PolicyContext`.
It uses only the provided legal-action mask and optional DAL advisory metadata.

## Replay compatibility

The shadow policy is read-only from the EULS perspective.
It does not mutate queues, tasks, rewards, metrics, or replay artifacts.

## No-training guarantee

The shadow policy does not import training or optimizer code and does not execute learning logic.

## Tests added

This phase adds unit tests for:

- legal-action enforcement
- read-only advisory handling
- deterministic fallback behavior
- deadline-pressure preference
- queue-pressure preference
- registry opt-in behavior
- replay hash stability

## Non-inclusions

This phase does not include:

- DRL training
- optimizer execution
- target-network updates
- LSTM
- Figures 8–11
- baseline campaign repair
- reward shaping
- queue mutation
- deadline/drop behavior changes

## Known limitations

The shadow policy is a simple deterministic consumer, not an optimized controller.
It is intended for evaluation and interface validation only.
