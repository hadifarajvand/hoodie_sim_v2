# Feature 077 Research

## Decision 1: Campaign readiness before execution

- Decision: Define the campaign configuration before any experiments run.
- Rationale: readiness must be fixed before execution to avoid ad hoc campaign drift.
- Rejected alternative: execute first and document later.
- Consequence: the feature remains documentation-only and cannot produce results.

## Decision 2: Deterministic seed plan

- Decision: Require a deterministic seed list with recorded seed identity.
- Rationale: reproducibility is a prerequisite for any later campaign evaluation.
- Rejected alternative: random or implicit seed selection.
- Consequence: every future result row must carry seed provenance.

## Decision 3: Three workload levels

- Decision: Use exactly `low`, `medium`, and `high`.
- Rationale: a bounded load grid is sufficient for readiness and keeps the campaign tractable.
- Rejected alternative: open-ended workload definitions.
- Consequence: future grid validation remains simple and deterministic.

## Decision 4: Three deadline pressure levels

- Decision: Use exactly `relaxed`, `moderate`, and `tight`.
- Rationale: deadline pressure must be discretized to align with the readiness matrix.
- Rejected alternative: continuous or arbitrary deadline scales.
- Consequence: later campaign cells can be enumerated and validated cleanly.

## Decision 5: Paper Figure 7 topology only

- Decision: Lock topology mode to `paper_figure_7`.
- Rationale: the experimental campaign must stay aligned with the paper topology already validated upstream.
- Rejected alternative: alternative topology modes.
- Consequence: future campaign rows remain topology-consistent.

## Decision 6: Paper runtime mode only

- Decision: Lock runtime mode to `paper`.
- Rationale: the campaign is meant to measure paper-faithful behavior, not compatibility shortcuts.
- Rejected alternative: compatibility or mixed runtime modes.
- Consequence: future campaign rows stay comparable and non-compatibility-based.

## Decision 7: No ranking or winner yet

- Decision: Do not rank methods or declare a winner in this feature.
- Rationale: campaign readiness must not become an analysis claim.
- Rejected alternative: produce comparative winners now.
- Consequence: later analysis must be explicit and separately validated.

## Decision 8: No statistical claim yet

- Decision: Do not make statistical significance claims in Feature 077.
- Rationale: the feature has no executed experiments yet.
- Rejected alternative: preemptive significance language.
- Consequence: the claim boundary stays strict.

## Decision 9: No final evaluation yet

- Decision: Do not frame this feature as final evaluation.
- Rationale: Feature 077 only prepares the campaign; it does not run it.
- Rejected alternative: final-evaluation wording.
- Consequence: the output remains a readiness artifact only.
