# Feature 078 Research

## Decision 1: Execute raw campaign rows before statistics

- Decision: Feature 078 produces raw execution rows only.
- Rationale: statistics require a complete raw dataset first.
- Rejected alternative: compute summaries during execution.
- Consequence: Feature 079 owns aggregation and confidence intervals.

## Decision 2: Consume Feature 077 contract

- Decision: campaign dimensions come from Feature 077.
- Rationale: execution must not redefine the experiment design.
- Rejected alternative: define a separate execution grid.
- Consequence: Feature 078 validates against Feature 077.

## Decision 3: Paper topology and runtime only

- Decision: topology mode remains `paper_figure_7`; runtime mode remains `paper`.
- Rationale: campaign execution must stay aligned with upstream paper-faithful semantics.
- Rejected alternative: mixed topology/runtime modes.
- Consequence: compatibility mode is forbidden.

## Decision 4: No ranking in Feature 078

- Decision: no winner, ranking, or superiority statement.
- Rationale: raw execution rows are not enough for statistical conclusions.
- Rejected alternative: rank methods immediately after execution.
- Consequence: interpretation moves to later features.

## Decision 5: Keep outputs controlled

- Decision: generated execution outputs must stay outside git unless explicitly approved.
- Rationale: raw campaign outputs can be large and should not pollute source control.
- Rejected alternative: commit generated outputs by default.
- Consequence: implementation must use ignored or approved output paths.
