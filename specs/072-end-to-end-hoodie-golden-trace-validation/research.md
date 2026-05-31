# Research: Feature 072

## Decision 1: Validate deterministic traces before evaluation batches

Decision: Feature 072 validates deterministic semantic traces before any campaign or baseline evaluation work.

Rationale: Feature 070 recovered evidence and Feature 071 aligned helper semantics. The next risk is integration drift: individual helpers can be correct while the end-to-end path is wrong.

Rejected alternative: Start evaluation batches immediately. Rejected because that would generate numbers before proving the semantic path.

## Decision 2: Use Feature 071 helpers, do not duplicate formulas

Decision: Deadline and reward calculations must call Feature 071 helper functions.

Rationale: Duplicating formulas inside the trace package creates a second truth source.

Rejected alternative: Reimplement deadline/reward formulas in the trace package. Rejected as drift-prone.

## Decision 3: Use Feature 070 Figure 7 topology

Decision: Horizontal legality scenarios must use the recovered Figure 7 neighbor map.

Rationale: Feature 070 recovered structured topology evidence; Feature 072 must prove it works in a trace context.

Rejected alternative: Use a complete graph or hand-coded free-form topology. Rejected because that hides the actual topology constraint.

## Decision 4: Keep compatibility as boundary evidence only

Decision: Golden traces default to paper mode. Compatibility is tested only to prove it is not default.

Rationale: Feature 071 made compatibility explicit. Feature 072 must not accidentally validate legacy mode as the main path.

## Decision 5: Do not rewrite runtime

Decision: Feature 072 creates a read-only validation package.

Rationale: Runtime semantics are Feature 071's responsibility. Feature 072 validates them end-to-end using deterministic examples.
