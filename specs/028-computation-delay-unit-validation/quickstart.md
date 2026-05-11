# Quickstart: Computation Delay and CPU Unit Validation

## Inputs
- `artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.json`
- `resources/papers/hoodie/recovered/paper-parameter-registry.json`
- `artifacts/analysis/link-rate-transmission-delay-contract/link-rate-contract-report.json`
- `artifacts/analysis/offload-lifecycle-instrumentation/instrumentation-summary.json`
- `resources/papers/hoodie/ocr/merged.tex`

## Validation Flow
1. Read the paper evidence and runtime compute/time configuration.
2. Recover or classify unit meanings for task size, processing density, CPU capacities, and slot duration.
3. Compare paper Δ against runtime Δ and classify any mismatch.
4. Validate computation-delay and completion-slot formulas with deterministic examples.
5. Run the regression tests for Feature 019, Feature 024, and Feature 027.
6. Generate `artifacts/analysis/computation-delay-cpu-unit-validation/unit-validation-report.json` and `.md`.

## Report Expectations
- Distinguish `recovered`, `unrecoverable`, `mismatched`, `repaired`, and `blocked` items.
- Include both paper and runtime Δ values when they differ.
- State whether the runtime correction was narrowly applied or blocked.
- Preserve Feature 027 visibility if the Δ correction affects link-rate report regeneration.
- Bind the runtime audit to `src/environment/compute_config.py`, `src/environment/traffic_config.py`, `src/environment/link_rate_config.py`, and the Feature 027 report so the analysis cannot accidentally audit only a proxy layer.

## Test Expectations
- Unit conversion tests must cover bits/Mbits, bps/Mbps, seconds/slots, and slots/seconds.
- Computation-delay tests must cover `cycles_required` and completion-slot logic.
- CPU-capacity tests must verify unrecoverable handling.
- Regression tests must prove Feature 019 timeout/drop, Feature 024 deterministic trace behavior, and Feature 027 link-rate contracts remain intact.

## Decision Rule
- If the paper-backed evidence supports `Δ = 0.1 s`, a narrow repair is allowed.
- If the repair cannot be isolated without broad behavior drift, report a blocker instead of silently mutating the simulator.
