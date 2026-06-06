# Research: Computation Delay and CPU Unit Validation

## Decision 1: Treat paper-backed unit evidence as the source of truth for semantics
- Decision: Use Feature 016 and Feature 025 registries plus OCR evidence to recover unit meanings, then compare them against runtime configuration.
- Rationale: The feature is a validation/contract pass, not a simulator redesign.
- Alternatives considered: Inferring from runtime behavior alone or from Feature 027 report output. Rejected because that would hide paper/runtime divergence.

## Decision 2: Model slot-duration mismatch explicitly
- Decision: If the recovered paper default is `Δ = 0.1 s` and runtime/report uses `1.0 s`, report the mismatch and only allow a narrow correction if evidence supports it and regression tests prove Feature 027 behavior remains stable.
- Rationale: Silent normalization would falsify the contract.
- Alternatives considered: Leaving runtime unchanged and calling it “close enough.” Rejected because it obscures a material timing discrepancy.

## Decision 3: Preserve unrecoverable CPU capacities when paper evidence is incomplete
- Decision: Report CPU capacities as unrecoverable unless the paper registry provides direct evidence.
- Rationale: Feature 028 must distinguish recovered semantics from invented constants.
- Alternatives considered: Reusing runtime defaults as if paper-backed. Rejected because that is fabrication.

## Decision 4: Use deterministic unit conversions with explicit policies
- Decision: Implement and test bits/Mbits, bps/Mbps, seconds/slots, and completion-slot calculations with explicit rounding behavior.
- Rationale: Determinism is required for reproducible validation.
- Alternatives considered: Floating-point “close enough” checks without policy documentation. Rejected because they make the contract ambiguous.

## Decision 5: Keep the feature scoped to analysis and narrowly targeted environment repair
- Decision: Prefer `src/analysis/computation_delay_cpu_unit_validation/` plus tests and reports; touch `src/environment/*` only if a unit bug is proven and the fix is minimal.
- Rationale: The feature is about validation and contract clarity, not broad runtime change.
- Alternatives considered: Reworking runtime compute logic broadly. Rejected because it violates scope and risks regressions.
