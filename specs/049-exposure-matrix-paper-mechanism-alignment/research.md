# Research: Exposure Matrix Rerun and Paper Mechanism Alignment

## Decision 1: Use Feature 048 legality evidence as the rerun basis

- Decision: The exposure matrix rerun will use Feature 048 legality evidence as the evidence source.
- Rationale: Feature 048 is the first feature that exposes trace-backed legality evidence without changing runtime behavior.
- Alternatives considered: Rerun without legality evidence; use representative samples only; defer the rerun to a later training feature.

## Decision 2: Treat Feature 047 as the baseline exposure artifact

- Decision: The committed Feature 047 report is the prior baseline artifact for comparison.
- Rationale: Feature 047 established the incomplete exposure state and the need for legality evidence.
- Alternatives considered: Use live reruns only; ignore Feature 047 and compare against raw traces.

## Decision 3: Keep the feature diagnostic and alignment-only

- Decision: The feature will not implement training, optimizer, replay, or target updates.
- Rationale: The user explicitly scoped this feature to readiness diagnostics before training is attempted.
- Alternatives considered: Start the training-contract bundle immediately; combine diagnostic work with training.

## Decision 4: Audit the observation vector and formula/unit contract as read-only checks

- Decision: The paper HOODIE observation vector and the timing/state formulas will be audited without changing runtime behavior.
- Rationale: The feature is intended to decide whether the simulator/network interface still matches the paper mechanism.
- Alternatives considered: Fix the runtime immediately; postpone audits until after training.

## Decision 5: Route runtime contradictions to a future repair feature

- Decision: If the audit shows a runtime semantic contradiction, the report will stop at a repair-required verdict and recommend a future repair feature.
- Rationale: The feature scope excludes runtime semantic changes unless separately approved later.
- Alternatives considered: Silently adjust the simulator contract; recommend training despite contradictions.
