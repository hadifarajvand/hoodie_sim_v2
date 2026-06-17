# EULS Phase 8 DAL Policy Context

## Purpose

Phase 8 exposes DAL advisories to policy and evaluation interfaces as optional input-only metadata.

DAL advisory context is input-only metadata. It does not alter legal action masking, final action selection, or EULS state transitions.

## DAL policy-context boundary

DAL remains a read-only advisory layer over EULS. PolicyContext can carry DAL advisory data, but policies are not required to consume it.

## PolicyContext addition

`PolicyContext` now includes an optional `dal_advisory` field.

## Backwards compatibility guarantees

- existing `PolicyContext` construction still works
- existing policies that ignore DAL continue to behave exactly as before
- `legal_action_mask` remains the source of legality
- action selection remains policy-controlled

## Read-only guarantees

- DAL advisories are computed from EULS state without mutation
- PolicyContext receives DAL as data only
- no task, queue, reward, or metric mutation is introduced

## Determinism / replay guarantees

- DAL advisory payloads are deterministic for a fixed EULS state
- replay hashes remain stable before and after DAL advisory access
- adding DAL to `PolicyContext` does not change EULS replay payloads

## Tests added

- `tests/unit/test_dal_policy_context.py`

## Non-inclusions

- no training
- no optimizer execution
- no target update integration
- no queue mutation
- no reward shaping
- no Figures 8-11

## Phase 9+ plan

Future phases may let specific policies optionally consume DAL advisories, but only as metadata input. The policy decision and EULS runtime contract remain separate.
