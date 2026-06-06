# Research: Exposure-Matrix Review

## Decision 1: Passive diagnostics only
- Decision: The feature will not modify runtime code or add new legality instrumentation.
- Rationale: Feature 047 is intended to close an evidence gap, not change simulator behavior.
- Alternatives considered: Adding runtime mutation to emit legal masks; rejected because it changes behavior and belongs in a separate feature.

## Decision 2: Evidence source priority
- Decision: Legal action evidence will be sourced in this order: trace legality snapshot, environment action mask, approved public legality helper, then unavailable.
- Rationale: This preserves trace-backed legality where available and prevents fake zero counts.
- Alternatives considered: Falling back to zero counts; rejected because it overclaims coverage.

## Decision 3: Full-population matrix requirement
- Decision: Aggregate exposure metrics must come from the full decision-opportunity population, not sample slices.
- Rationale: Sample-derived aggregates cannot defend a verdict.
- Alternatives considered: Using representative samples as proxies; rejected because they misstate coverage.

## Decision 4: Routing rule
- Decision: Complete matrices route to `Feature 048 — Paper HOODIE Observation Vector`; incomplete legal evidence routes to legality evidence expansion before Feature 048.
- Rationale: This keeps the next step aligned with evidence completeness.
- Alternatives considered: Routing directly to runtime repair; rejected because repair is out of scope.

## Decision 5: Validation discipline
- Decision: Validate prior features via committed artifacts and safe tests only, avoiding dirty-worktree-sensitive report-generation tests.
- Rationale: The current feature must not depend on executing unstable or pointer-sensitive validation paths.
- Alternatives considered: Rerunning older report-generation tests; rejected because they add noise and brittle worktree coupling.

