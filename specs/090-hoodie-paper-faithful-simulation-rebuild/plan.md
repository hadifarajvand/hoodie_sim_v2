# Plan: Feature 090 HOODIE Paper-Faithful Simulation Rebuild

## Phase 1 — Reference Compliance Gate

Read all files in:

```text
docs/hoodie/paper_simulation_reference/
```

Before implementation, produce a mapping from each required mechanism to existing code or new code target.

## Phase 2 — Runtime First, Not Figures

Implement the core runtime before any figure output work:

1. slot loop;
2. action/drain split;
3. per-EA arrivals;
4. task registry;
5. pending lifecycle;
6. queue progression;
7. reward events.

Figure output work is blocked until runtime diagnostics pass.

## Phase 3 — Queue Mechanics

Implement and test:

- private queue waiting and service;
- offloading queue waiting and transmission;
- public queue insertion;
- active public queue discovery;
- public CPU sharing;
- completion/drop separation.

## Phase 4 — State and Reward

Implement:

- historical load matrix;
- public queue footprint;
- state snapshots;
- delayed reward collection;
- experience linkage.

## Phase 5 — Policies and Baselines

Implement/verify:

- HOODIE mode declaration;
- RO;
- FLC;
- VO;
- HO;
- BCO;
- MLEO with total latency estimates.

## Phase 6 — Training Boundary

Decide and report whether full training is implemented in this feature.

If not implemented:

- Figure 8 stays gated;
- Figure 11 stays gated;
- HOODIE is marked substitute/interface-only for Figure 9/10.

If implemented:

- produce training traces;
- produce replay/loss/epsilon diagnostics;
- produce with/without LSTM traces.

## Phase 7 — Validation Outputs

Generate Figure 9 and Figure 10 only from validation runtime, not transformed aggregates.

Figure 9 must use HOODIE-only validation. Figure 10 must use independent runs for every policy.

## Phase 8 — Non-Degeneracy and Reporting

Reject or flag outputs with:

- zero completions;
- one-task traces;
- all-policy ties;
- 100% drop saturation;
- missing denominators;
- missing sweep injection.

## Final Artifacts

Generate under:

```text
artifacts/feature_090_paper_faithful_simulation/
```

Required:

- `mechanism_coverage.json/csv/md`
- `runtime_validation_report.json/md`
- `queue_dynamics_validation.json/md`
- `state_reward_validation.json/md`
- `policy_distinctness_report.json/md`
- `mleo_latency_estimation_audit.json/md`
- `metric_diagnostics.json/csv/md`
- `figure_9_outputs.json/csv`
- `figure_10_outputs.json/csv`
- `figure_readiness_report.json/md`
- `feature_090_final_report.json/md`
