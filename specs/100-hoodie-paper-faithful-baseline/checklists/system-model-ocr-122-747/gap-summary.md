# Gap Summary

This audit package records what the repository can currently support and what still blocks a paper-faithful HOODIE claim.

## Critical Blockers

- `state_dim=2` is not the paper state vector. The paper state needs task size, private wait, offloading wait, public-queue footprint, and historical load matrix context.
- `action_count=5` is not a paper-validated action space for the `N=20` setup. It is a proxy action representation, not the full paper contract.
- Reward is still partly reconstructed from traces. That is useful for auditing, but it is not yet a native delayed reward event stream in the runtime.
- Pub-sub / recovery behavior is described in the paper but is not convincingly simulated in the current runtime evidence.
- The repository does not yet provide paper-grade 200-episode validation or Figures 8-11 workflows.

## Important Gaps Before Figures

- Public queue CPU sharing needed an explicit repair and audit. The legacy code was not enough.
- The LSTM is not yet a fully auditable forecasting/history pipeline. It is present, but still wired through the legacy agent stack.
- Table 4 parameter values exist in multiple places, but there is not yet a single authoritative contract binding the code to the paper parameter registry.
- Baseline aliases exist, but they are not guaranteed to be paper-perfect reimplementations.

## Acceptable Approximations for Smoke Validation

- Reconstructed transition datasets from task lifecycle traces.
- Trace-based reward reconstruction for audit purposes.
- Smoke-level training runs that prove the code path executes.
- Proxy baseline labels, provided they are not misrepresented as paper-perfect implementations.

## Implementation Risks

- OCR ambiguity can cause false confidence if the checklist is treated as a visual match rather than a contract.
- Legacy trace reconstruction can hide missing runtime fields if the audit is not explicit about unavailable values.
- Reusing old code paths without a contract boundary can keep proxy behavior alive while pretending the system is paper-faithful. That would be trash engineering.

## Already Covered by Earlier Phases

- Phase 1 added task lifecycle, queue, action, and episode tracing.
- Phase 2 repaired public CPU sharing, reward reconstruction, adjacency legality checks, and baseline policy proxies.
- Phase 3 added trace-derived training scaffolding and smoke training execution.

## Bottom Line

The repository now has enough structure to audit, trace, and smoke-test the workflow, but it does not yet justify a paper-faithful end-to-end claim. The missing pieces are runtime contract fidelity, paper-grade validation, and figure-generation workflows.

