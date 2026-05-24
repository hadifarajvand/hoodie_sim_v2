# Research: Selected-Action Family and Per-Action Outcome Evidence Expansion

## Decision 1: Treat selected-action family evidence as first-class passive trace data

- **Decision**: Model the selected action family as an explicit passive evidence stream with availability status and trace-backed counts by family.
- **Rationale**: Feature 049 failed because counts were inferred or replaced by placeholders instead of being evidenced.
- **Alternatives considered**:
  - Infer selected family from legality-only coverage. Rejected because legality does not prove what was selected.
  - Emit hardcoded zero counts when no family data exists. Rejected because it hides missing evidence.

## Decision 2: Use deterministic join keys for selected-action-to-task and selected-action-to-outcome joins

- **Decision**: Join on strategy, seed, slot, agent_id, task_id, and a deterministic decision-event identifier or equivalent passive key.
- **Rationale**: The evidence must remain traceable across task lifecycle events without depending on runtime inference.
- **Alternatives considered**:
  - Join by action index alone. Rejected because it is not stable enough for trace reconstruction.
  - Join by terminal status only. Rejected because it cannot separate multiple selected actions in the same run.

## Decision 3: Treat missing outcome joins as unavailable evidence

- **Decision**: Report completion, drop, and pending counts/rates only when the selected action can be joined to terminal lifecycle state.
- **Rationale**: Feature 049 must not recommend readiness from fake zero outcome rates.
- **Alternatives considered**:
  - Fill missing rates with zero. Rejected because it is a placeholder, not evidence.
  - Estimate missing outcomes from averages. Rejected because this would be sample-derived.

## Decision 4: Keep behavior-equivalence checks deduplicated and passive

- **Decision**: Record each behavior-equivalence check once, by unique name, and use passive evidence only.
- **Rationale**: The feature must prove the evidence capture did not alter outcomes, not repeat the same check in multiple ways.
- **Alternatives considered**:
  - Duplicate checks per strategy and seed. Rejected because it adds noise without better evidence.
  - Rely on narrative assertions. Rejected because the result must be machine-auditable.

## Decision 5: Block Feature 049 rerun readiness unless all evidence gates pass

- **Decision**: The report may recommend the Feature 049 rerun only when selected-action family evidence is available, per-action outcome joins are available, and internal consistency is verified.
- **Rationale**: The downstream rerun is only meaningful if it can be backed by trace evidence.
- **Alternatives considered**:
  - Recommend Feature 050 even with partial evidence. Rejected because it would recreate the same blocker.

