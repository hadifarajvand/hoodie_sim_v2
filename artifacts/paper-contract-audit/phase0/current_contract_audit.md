# Current Contract Audit

## Scope
- `main.py`
- `phase2_mechanisms.py`
- `phase1_tracing.py`
- `environment/environment.py`
- `environment/action_model.py`
- `hyperparameters/hyperparameters.json`
- `resources/papers/hoodie/ocr/merged.tex`

## Findings

| Item | Classification | Evidence | Notes |
|---|---|---|---|
| Official policy aliases | paper_faithful | `main.py`, `decision_makers/baselines.py`, `phase2_mechanisms.py` | HOODIE, RO, FLC, VO, HO, BCO are mapped to explicit official identities. |
| MLEO identity | unverified | `decision_makers/baselines.py` | MLEO is gated with a loud `NotImplementedError`; it is not silently proxied. |
| Trace CSVs emitted by `TraceRecorder` | proxy | `phase1_tracing.py`, `environment/environment.py` | `task_lifecycle.csv`, `queue_trace.csv`, `action_trace.csv`, `paper_state_trace.csv`, `episode_metrics.csv` are emitted, but the contract still depends on runtime state quality. |
| `paper_state_trace` LSTM forecast | proxy | `training/trace_dataset.py`, `artifacts/phase4_validation/state_lstm_summary.json` | The validation artifacts still show persistence fallback in the current evaluation path. |
| MLEO candidate-wise latency tracing | missing | `phase2_mechanisms.py` | The current code writes a sample placeholder, not a paper-grade candidate contract. |
| Delayed reward traceability | proxy | `phase2_mechanisms.py`, `training/trace_dataset.py` | Reward reconstruction exists, but the system is not yet a full paper-faithful delayed-reward event pipeline. |
| Figure 8–11 generation | missing/out of scope | repo audit context | Not implemented in this phase and intentionally excluded. |

## Current policy aliases
- HOODIE -> Agent
- RO -> Random
- FLC -> AllLocal
- VO -> AllVertical
- HO -> AllHorizontal
- BCO -> BalancedCyclicOffloader
- MLEO -> MinimumLatencyEstimationOffloader (gated, not paper-faithful yet)

## Current trace CSVs emitted
- `task_lifecycle.csv`
- `queue_trace.csv`
- `action_trace.csv`
- `paper_state_trace.csv`
- `episode_metrics.csv`

## Notes
- Figure 8–11 generation is explicitly out of scope for this phase.
- `paper_state_trace` is not yet proof of paper-faithful LSTM forecasting.
- MLEO must not be used for official Figure 10 evaluation until the real candidate-wise latency implementation exists.
