# Research: Feature 069

## Decision 1: Feature 069 starts as a mechanism contract, not a code repair

Decision: The first step is to define the Spec Kit package before implementation.

Rationale: Prior repair work showed that implementation without a hard Spec Kit contract can produce green tests while weakening earlier behavior.

Rejected alternative: Direct implementation. Rejected because the mechanism layer touches topology, queues, reward timing, timeout/drop, and reporting.

## Decision 2: Topology and neighbor graph evidence must be explicit

Decision: Coordination graph work must use existing topology/action-space evidence or record a blocker.

Rationale: The paper mechanism registry marks structured topology evidence as incomplete, so implementation must not invent topology semantics.

Rejected alternative: Hard-code a new graph. Rejected because it would create unapproved assumptions.

## Decision 3: Synchronization is validated as a sequence

Decision: Time-slot progression, action application, queue update, completion, drop, and reward timing must be audited as a sequence.

Rationale: Mechanism fidelity depends on ordering, not just individual helper functions.

Rejected alternative: Isolated helper tests only. Rejected because they miss integration drift.

## Decision 4: Delayed reward stays within known contracts

Decision: The reward path must be audited against existing reward timing contracts and unresolved equation ambiguity must be recorded.

Rationale: The exact reward equation is not fully reconstructed in the available mechanism registry evidence.

Rejected alternative: Invent a reward equation. Rejected because it would overclaim paper fidelity.

## Decision 5: Congestion and queue pressure must remain placement-compatible

Decision: Queue-pressure evidence must distinguish local/private, horizontal/public, and cloud placement paths and remain compatible with Feature 068R policies.

Rationale: Feature 068R introduced placement-aware baselines; mechanism fidelity must not collapse those choices back to family-only evidence.

Rejected alternative: Family-only queue pressure. Rejected because it would hide placement-level behavior.

## Decision 6: Timeout/drop accounting is evidence-first

Decision: Timeout/drop behavior must be validated or recorded as a blocker before paper-level claims are made.

Rationale: The registry marks timeout/drop details as high-risk and partially unresolved.

Rejected alternative: Treat current runtime accounting as paper-faithful by default. Rejected because that is fake fidelity.

## Decision 7: Reports separate verified facts from assumptions

Decision: The final mechanism report must separate verified behavior, compatibility fallback, assumption-backed behavior, and blockers.

Rationale: This preserves claim safety and makes future thesis/paper writing defensible.

Rejected alternative: Single pass/fail report only. Rejected because it hides unresolved mechanism risk.

## Decision 8: No generated campaign artifact refresh in Feature 069

Decision: Feature 069 implementation may create targeted analysis evidence only if approved by the implementation tasks, but it must not regenerate campaign outputs.

Rationale: Mechanism fidelity is a contract layer, not a new campaign run.

Rejected alternative: Refresh campaign artifacts. Rejected because it contaminates scope and makes review noisy.
