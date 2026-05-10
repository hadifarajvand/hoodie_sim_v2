# Research: Mechanism Repair

## Decisions

### 1. Repair Scope
- **Decision**: Repair only `case-timeout-drop`.
- **Rationale**: The committed Feature 018 audit identifies exactly one confirmed divergence with `likely_environment_bug`; the other findings are assumptions or instrumentation gaps.
- **Alternatives considered**: Include offload or ordering findings, but that would turn the feature into speculative simulator work.

### 2. Repair Boundary
- **Decision**: Treat the public environment adapter boundary as the owner of timeout/drop terminal accounting.
- **Rationale**: The public `step` lifecycle is where the environment finalizes tasks and emits delayed reward, so the smallest honest repair surface is the adapter boundary, not topology or runtime internals.
- **Alternatives considered**: Patch lower-level internals or the topology path. Rejected because those would broaden scope beyond the confirmed divergence.

### 3. Regression Test Shape
- **Decision**: Add a public `step`-lifecycle regression test that drives the timeout/drop case to finalization and asserts `terminal_outcome == dropped` and reward emission only at terminal finalization.
- **Rationale**: This proves the defect before repair and validates the delayed-reward contract without changing the public interface.
- **Alternatives considered**: Audit-only validation or trace injection. Rejected because the feature must prove the bug with a concrete regression.

### 4. Metrics Policy
- **Decision**: Treat metrics as read-only for this feature.
- **Rationale**: Feature 018 did not prove a metric formula bug, so changing metrics would be unrelated scope creep.
- **Alternatives considered**: Adjust metrics to make the divergence disappear. Rejected because the audit does not justify it.

### 5. Audit Regeneration
- **Decision**: Regenerate the Feature 018 differential audit after the repair.
- **Rationale**: The regenerated audit provides the before/after evidence chain for the repaired divergence.
- **Alternatives considered**: Keep the original audit only. Rejected because the feature explicitly wants post-repair audit evidence.

### 6. Non-Repair Findings
- **Decision**: Preserve offload instrumentation gaps and assumption gaps as unrepaired unless independently proven.
- **Rationale**: The committed audit does not authorize them as repair targets.
- **Alternatives considered**: Fix adjacent findings while in the environment code. Rejected as scope creep.

## Rationale Summary

The repair should be local, test-first, and audit-driven. The only justified code path change is the timeout/drop terminal accounting that caused the confirmed divergence. Everything else stays frozen unless a separate concrete bug is proven.
