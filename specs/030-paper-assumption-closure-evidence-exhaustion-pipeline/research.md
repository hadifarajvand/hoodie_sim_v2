# Research: Paper Assumption Closure and Evidence Exhaustion Pipeline

## Decision 1: Evidence inventory source set
- **Decision**: Inventory paper OCR/PDF sources, recovered registries, and prior analysis reports from Features 025, 028, and 029, plus any earlier feature artifacts that contain unresolved paper items.
- **Rationale**: The feature must close the full paper-gap surface, not just the latest reports.
- **Alternatives considered**: Limiting the search to the explicitly named files was rejected because it could miss earlier unresolved items.

## Decision 2: Classification vocabulary
- **Decision**: Use the six clarified final statuses only: `recovered`, `partially_recovered`, `contradicted`, `assumption_backed_requires_user_approval`, `unrecoverable_after_evidence_exhaustion`, and `out_of_scope`.
- **Rationale**: A fixed vocabulary keeps the report machine-checkable and prevents semantic drift.
- **Alternatives considered**: Adding a manual-visual or paper-backed status was rejected because it weakens the required one-to-one mapping to final audit states.

## Decision 3: Confidence handling
- **Decision**: Track confidence as `high`, `medium`, `low`, or `invalid`; only `high` is runtime-usable without extra approval, while `low` and `invalid` are report-only until later approval.
- **Rationale**: This separates evidentiary strength from final status and prevents weak guesses from being treated as facts.
- **Alternatives considered**: Using only pass/fail evidence was rejected because the feature needs to preserve manual-review nuance.

## Decision 4: Figure 7 manual recovery policy
- **Decision**: Ambiguous Figure 7 edges are `unrecoverable_after_evidence_exhaustion`; individually defensible edges may be recorded with per-edge confidence.
- **Rationale**: This avoids encoding topology that the paper does not actually justify.
- **Alternatives considered**: Marking the whole graph partially recovered was rejected because it hides which edges are defensible and which are not.

## Decision 5: Report structure
- **Decision**: Emit a JSON report with a compact `summary` block and a single top-level `items` array, plus a Markdown companion for human review.
- **Rationale**: The report must be easy to validate mechanically while still being readable by reviewers.
- **Alternatives considered**: Separate arrays by status were rejected because they make the item inventory harder to compare and reconcile.

## Decision 6: Runtime boundary
- **Decision**: The pipeline is analysis-only and must not change simulator runtime behavior.
- **Rationale**: The feature’s purpose is evidence closure, not behavior mutation.
- **Alternatives considered**: Runtime repairs were deferred to later approved work because this feature must not silently adopt assumption-backed values.

