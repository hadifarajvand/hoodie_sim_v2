## Figure 10 Sweep Workflow Audit

This phase prepares baseline-only Figure 10 parameter sweeps. It does not run any simulation.

What this phase does:
- prints manual commands for baseline-only sweeps
- prepares small sweep config files
- adds a lightweight `trace_level: summary` mode to reduce trace volume
- keeps the sweep workflow diagnostic/baseline-review only

What it does not do:
- it does not run the 200-episode validation
- it does not train HOODIE
- it does not run HOODIE as an untrained model
- it does not generate plots
- it does not claim not full official HOODIE Figure 10 reproduction

Baseline-only scope:
- `RO`
- `FLC`
- `VO`
- `HO`
- `BCO`
- `MLEO`

HOODIE is intentionally excluded.

Sweep groups prepared:
- task arrival probability
- private/local CPU capacity
- timeout/deadline

Trace-size control:
- `trace_level: summary` is used to avoid writing `paper_state_trace.csv`, `queue_trace.csv`, and `mleo_candidate_latency_trace.csv` in sweep runs.
- This is a lightweight preparation step only; the user must run the printed commands manually.

Parameter note:
- The runtime timeout key remains inconsistent across the project (`timeout_delay_mins` vs slot-based contract wording).
- This phase does not silently guess a paper-faithful timeout conversion for the sweep commands.
- The audit explicitly records that this requires manual review if the user wants a strict paper-contract sweep.

Manual reproduction:
- use the printed commands from `scripts/prepare_figure10_baseline_sweeps.py`
- inspect `figure10_policy_metrics_summary.json` and `figure10_policy_readiness.json` after a run
- do not commit the generated sweep outputs
