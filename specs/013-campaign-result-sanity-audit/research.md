# Research: Campaign Result Sanity Audit

## Decision 1: Read-only filesystem inspection is the audit boundary

- Decision: The audit layer will only read completed campaign artifacts and emit separate report artifacts.
- Rationale: The feature is explicitly forensic. Any mutation would contaminate the evidence being inspected.
- Alternatives considered: Re-running the campaign or patching the existing outputs in place. Rejected because both would obscure whether the original artifacts were consistent.

## Decision 2: Anomaly reporting should be categorical, not speculative

- Decision: The audit will surface anomaly categories for high drop ratio, weak scenario differentiation, near-identical policy outcomes, and accounting mismatches.
- Rationale: The problem statement already names the suspicious patterns. The audit should explain those signals without pretending to know a single causal root when the evidence is ambiguous.
- Alternatives considered: A single pass/fail flag or one inferred root cause. Rejected because they hide the distinction between symptoms and causes.

## Decision 3: Deterministic output must be keyed off sorted artifact discovery

- Decision: The audit report will sort discovered artifact paths and produce stable serialized output for the same inputs.
- Rationale: A forensic report that changes order across runs is harder to compare and trust.
- Alternatives considered: Timestamp-based ordering or discovery-order iteration. Rejected because both can vary without any real change in the inputs.

## Decision 4: Consistency checks must reconcile summaries against per-run artifacts

- Decision: The audit will compare campaign-level totals against the underlying per-run matrix artifacts and summary records.
- Rationale: Missing-finalization and accounting issues are only detectable by cross-checking aggregated totals against the source records.
- Alternatives considered: Checking the campaign summary alone. Rejected because summary-only checks cannot expose inconsistent rollups.

## Decision 5: The report should be both human-readable and machine-readable

- Decision: The audit will produce a text summary for reviewers and a structured artifact for automated checks.
- Rationale: Reviewers need fast forensic reading, while CI or future tooling needs deterministic machine inspection.
- Alternatives considered: Only a structured file or only prose. Rejected because each misses one audience.

