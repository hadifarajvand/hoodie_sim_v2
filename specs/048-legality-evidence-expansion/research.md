# Research: Legality Evidence Expansion

## Decision 1: Passive legality evidence only

- **Decision**: Add passive legality evidence without changing action selection, rewards, timing, or queue semantics.
- **Rationale**: Feature 048 exists to expose missing legality data, not to fix behavior.
- **Alternatives considered**: Runtime repair and policy redesign were rejected because they would invalidate the evidence gap this feature is meant to close.

## Decision 2: Evidence source priority

- **Decision**: Use existing runtime info masks first, then the public legality helper if already available, then passive legality snapshots in lifecycle trace only if they can be exposed without semantic drift.
- **Rationale**: This preserves the no-semantics-change constraint while maximizing trace-backed evidence.
- **Alternatives considered**: Synthesizing legality from sample traces was rejected because it would create fake evidence.

## Decision 3: Behavior equivalence

- **Decision**: Compare every legality-capture run against a no-legality-capture baseline using the same seeds, same strategies, and the paper-default configuration.
- **Rationale**: The feature must prove that legality instrumentation does not alter selected actions or terminal outcomes.
- **Alternatives considered**: Single-run validation was rejected because it would not prove equivalence.

## Decision 4: Routing to Feature 049

- **Decision**: Route to `Feature 049 — Exposure-Matrix Rerun with Legality Evidence` only when coverage is sufficient and behavior equivalence passes.
- **Rationale**: Feature 049 depends on honest evidence completeness, not guesswork.
- **Alternatives considered**: Routing to training or observation-vector work was rejected because the exposure matrix rerun must happen first.

## Decision 5: Null handling

- **Decision**: Report unavailable legality as null/unavailable, not zero.
- **Rationale**: Zero would falsely imply a measured absence rather than missing evidence.
- **Alternatives considered**: Zero-filled defaults were rejected as scientifically invalid.

## Decision 6: Validation discipline

- **Decision**: Validate prior Features 044 through 047 through committed artifact checks only and avoid dirty-worktree-sensitive older report tests.
- **Rationale**: This preserves Feature 048 scope and avoids re-triggering worktree-sensitive report regeneration.
- **Alternatives considered**: Re-running older report-generation tests was rejected because it introduces unnecessary churn and can mutate unrelated artifacts.
