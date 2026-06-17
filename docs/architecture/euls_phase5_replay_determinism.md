# EULS Phase 5 Replay Determinism

## Scope

Phase 5 validates deterministic EULS execution. It does not claim HOODIE training reproduction. It does not claim Figures 8-11 reproduction.

## Deterministic input fields

The replay payload captures deterministic inputs and outcomes that affect EULS lifecycle behavior:

- trace identity
- seed
- episode length
- runtime mode and runtime parameters
- topology identity and queue-relevant configuration
- task blueprints and per-step lifecycle history
- queue-state snapshots
- terminal outcomes and delayed rewards
- aggregated metrics
- lifecycle trace events after volatile-field filtering

## Excluded volatile fields

The replay hash excludes values that can vary across machines or test runs without changing EULS semantics:

- wall-clock timestamps
- absolute file paths
- temporary directories
- object memory addresses
- unordered raw object repr strings
- machine-local workspace paths

## Replay event schema

The replay payload is built from deterministic EULS evidence:

- trace metadata and task blueprints
- queue snapshots for private, offloading, and public/cloud queues
- step history records with selected action and terminal outcome
- lifecycle trace event snapshots
- terminal metrics and pending terminal state

## Queue-state snapshot schema

Each queue snapshot records:

- queue kind
- host node id
- source agent id
- owner node id when applicable
- resolved destination when applicable
- current head admission slot
- ordered task snapshots

## Hash algorithm

The replay hash is SHA-256 over a canonical JSON encoding:

`json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)`

## Hash stability rules

- dictionary keys are sorted before hashing
- sets are normalized into sorted lists
- dataclasses are converted into plain deterministic structures
- volatile fields are removed before serialization
- queue/task ordering is preserved deterministically

## Known limitations

- This phase validates deterministic EULS replay, not training reproducibility.
- The replay payload is intentionally limited to EULS-relevant state.
- The hash does not attempt to encode unrelated repository or filesystem state.

## Explicit exclusions

- DAL
- DRL training
- LSTM
- Figures 8-11
- baseline campaign repair
- paper result claims
