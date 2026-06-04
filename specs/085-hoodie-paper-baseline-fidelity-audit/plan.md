# Plan — Feature 085 HOODIE Baseline Fidelity Audit and Formula Mapping

## Goal
Repair the audit outputs so the canonical baseline set uses `MLEO` instead of the legacy `MQO` label, and add a formal formula-to-code mapping matrix that supports full audit review.

## Step-by-Step Plan

1. Inspect the current runtime evaluation policies, report, manifest, and artifact bundle for any `MQO` labels that are still active.
2. Confirm the repository already contains a real `MLEO` policy implementation and map the audit outputs to that canonical label.
3. Update the runtime evaluation policy definitions so the active audit set becomes `HOODIE, RO, FLC, VO, HO, BCO, MLEO`.
4. Replace `MQO` with `MLEO` in all generated tables, policy coverage summaries, report sections, and validation outputs.
5. Build the baseline-mapping matrix that explains the canonical baseline names, legacy labels, code locations, and status.
6. Build the formula-to-code mapping matrix with explicit rows for task delay, task drop ratio, reward, offload delays, DQN/DDQN/Dueling, and LSTM interfaces.
7. Update the validation rules so the audit fails when `MQO` appears in active outputs or when formula mappings are incomplete.
8. Regenerate the full audit artifact bundle.
9. Verify the report, manifest, and metrics remain deterministic and match the paper-aligned baseline naming.
10. Prevent merge completion until the baseline correction and formula audit validations pass.

## Architecture Notes

- The audit uses the existing evaluation runner and runtime policies rather than introducing a new simulator.
- `HOODIE` remains the Feature 080 proposed method path.
- `MLEO` maps to the repository's minimum-latency-estimate offloading implementation.
- Any compatibility label must stay internal and must not leak into active audit outputs.

## Validation Strategy

- Unit tests verify policy labels, policy coverage, and formula mapping rows.
- Integration tests verify artifact generation and report rendering.
- Artifact validation rejects stale `MQO` labels and missing formula rows.
- Merge-gate validation remains closed until the audit is complete.
