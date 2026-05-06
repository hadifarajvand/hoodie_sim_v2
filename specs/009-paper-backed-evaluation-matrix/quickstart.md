# Quickstart: Paper-Backed Evaluation Matrix

## What this feature does

Runs the implemented policies across the paper-backed traffic scenarios and seeds through the shared `HoodieGymEnvironment` boundary, then writes auditable result artifacts.

## Typical flow

1. Create an evaluation matrix configuration with approved policy names, scenario names, and seeds.
2. Resolve each scenario through the scenario registry.
3. Resolve each policy through the policy registry.
4. Generate the traffic trace for the selected scenario and seed.
5. Execute the policy through the shared environment reset/step loop.
6. Store the per-run result record and update the aggregate summary.

## Guardrails

- Use only approved policy names.
- Use only paper-backed scenario names.
- Do not add a special path for any policy.
- Do not change metric formulas.
- Do not use parallel execution for the minimum complete version.

## Output

- Per-run records are written as machine-readable local artifacts.
- A summary artifact is written after the full serial matrix completes.
- Optional CSV output is allowed when it can be produced with standard library support.

## Notes

- No dependency installation is required for this feature.
- No pandas, matplotlib, or external trackers are needed.
- No dependency files were changed for this feature.
