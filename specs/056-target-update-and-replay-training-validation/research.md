# Research: Feature 056

## Decision: validate target sync by deterministic threshold simulation

The approved target-update contract uses `optimizer_step` as the target-update unit and frequency `2000`. A small Feature 055 smoke run produced optimizer steps but no target sync, which is correct below threshold.

A full 2000-step live training run would be too large for this validation feature. Therefore Feature 056 may use deterministic threshold simulation around the trainer contract to prove schedule behavior:

- no sync for steps `1..1999`
- sync at step `2000`
- target-sync count increments exactly at the threshold

This validates the contract without running a full campaign.

## Decision: validate replay sampling with controlled replay data

Replay insertion was already observed in Feature 055. Feature 056 should validate replay sampling using controlled replay data or the existing replay buffer API to prove sampled fields and delayed reward semantics.

## Decision: no reproduction claim

This feature validates mechanics only. It must not compare against HOODIE paper metrics or claim reproduction.
