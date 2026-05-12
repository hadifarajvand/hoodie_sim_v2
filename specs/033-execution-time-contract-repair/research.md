# Research: Execution-Time Contract Repair

## Decision 1: Execution accounting must be per-slot and destination-specific

- **Decision**: Local/private, public/edge, and cloud execution each consume at most the configured per-slot compute capacity for that destination.
- **Rationale**: This preserves Feature 032 capacities and prevents one-slot completion from inflating throughput or suppressing timeout behavior.
- **Alternatives considered**: Keep the local shortcut for backward compatibility. Rejected because it preserves the invalid behavior the feature is meant to fix.

## Decision 2: Remove the local/private shortcut in `step_execution`

- **Decision**: Delete the branch that consumes all remaining cycles immediately when local/private tasks exceed capacity.
- **Rationale**: The shortcut breaks delay semantics, timeout/drop behavior, and reward timing consistency.
- **Alternatives considered**: Limit only public/cloud. Rejected because the bug is local/private-specific but the contract must be uniform across destinations.

## Decision 3: Keep completion recorded at the end of the finishing slot

- **Decision**: When a task consumes its last cycles in slot `t`, completion is recorded at the end of slot `t`.
- **Rationale**: This preserves the existing environment step contract while making the boundary explicit and testable.
- **Alternatives considered**: Shift completion to `t+1`. Rejected because it silently changes reward timing.

## Decision 4: Preserve runtime model unless tests prove conflict

- **Decision**: `SharedRuntimeParameters` / `advance_shared_runtime` remain unchanged unless a test demonstrates they conflict with the repaired execution accounting.
- **Rationale**: The feature scope is execution-time correctness, not a broad runtime-model rewrite.
- **Alternatives considered**: Rewrite the whole runtime model now. Rejected because it expands scope without evidence.

