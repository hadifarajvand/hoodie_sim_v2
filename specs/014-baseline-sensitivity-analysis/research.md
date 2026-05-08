# Research: Baseline Sensitivity Analysis

## Decision 1: The analyzer will be read-only and artifact-driven

- Decision: The analysis layer will only read committed campaign, matrix, trace, and optional audit artifacts and will write separate sensitivity reports.
- Rationale: The feature is specifically a forensic explanation layer. Mutating or rerunning experiments would destroy the evidence being analyzed.
- Alternatives considered: Recomputing traces or regenerating campaigns. Rejected because the feature must explain existing outputs, not recreate them.

## Decision 2: Trace, policy, and scenario comparisons should be separated

- Decision: The report will distinguish trace collapse, policy behavior collapse, scenario output collapse, and saturation/aggregation masking as separate diagnostics.
- Rationale: The user explicitly wants to know which collapse mechanism is responsible. Blending them into one score would hide the distinction.
- Alternatives considered: One aggregate health score. Rejected because it would not explain what is collapsed.

## Decision 3: Moderate versus paper_default should be treated as an explicit comparison axis

- Decision: The analyzer will compare the `moderate` and `paper_default` traces directly by seed and report whether they are identical or only partially separated.
- Rationale: The baseline collapse report called out this pair specifically, and the sensitivity analysis must address that evidence directly.
- Alternatives considered: Comparing only aggregated scenario summaries. Rejected because summary-level comparison can mask trace identity.

## Decision 4: Policy equivalence should be derived from action and outcome signatures

- Decision: The analyzer will compare action distributions, terminal outcome distributions, and aggregate totals to detect identical or near-identical policy behavior.
- Rationale: The user needs to know whether several baselines are doing the same thing, not just whether their metrics are numerically close.
- Alternatives considered: Comparing only final metric averages. Rejected because averages can hide action collapse.

## Decision 5: Saturation diagnosis should remain diagnostic, not causal

- Decision: The analyzer will phrase saturation and timeout/finalization pressure as diagnostic signals, not proof of root cause.
- Rationale: The artifact set can support evidence of pressure or masking, but not a definitive simulator-level causal claim.
- Alternatives considered: Declaring a single causal explanation. Rejected because the evidence may support multiple plausible causes.

