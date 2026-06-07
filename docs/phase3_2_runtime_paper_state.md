# Phase 3.2 Runtime Paper State Repair

This phase repairs runtime-side paper state emission so the simulator exports a native per-agent paper-state trace instead of reconstructing everything later from lifecycle rows.

## What changed

- `main.py` now emits `paper_state_trace.csv` from the live environment loop.
- `phase1_tracing.py` now stores a structured paper-state record for each agent and time slot.
- `environment/environment.py` now exposes runtime paper-state fields directly from live queues and task state.
- `training/trace_dataset.py` now prefers `paper_state_trace.csv` and builds `next_state` from the next runtime snapshot for the same agent.

## Emitted fields

Each paper-state row includes:

- `episode_id`
- `time`
- `agent_id`
- `task_id`
- `eta_n`
- `w_priv_n`
- `w_off_n`
- `l_pub_n_prev_json`
- `active_load_vector_json`
- `L_t_json`
- `predicted_next_load_json`
- `predicted_next_load_method`
- `paper_lstm_forecast`
- `unavailable_fields_json`
- `approximation_warnings_json`
- `state_vector_json`
- `state_dim`

## Waiting time method

- `w_priv_n` and `w_off_n` come from the runtime queue waiting-time counters exposed by `Server.get_waiting_times()`.
- These are runtime estimates, not queue-length proxies.
- If a queue cannot provide a waiting-time value, the field is marked unavailable instead of being silently replaced by queue length.

## Active-load matrix

- `L(t)` is exported as a `W x (N+1)` rolling active-load matrix.
- Each row is one previous slot.
- Each column represents one compute node: edge nodes `0..N-1`, cloud node `N`.
- The active-load vector is derived from live queue occupancy, not from raw queue-length history.

## Predicted next load

- The runtime uses a `persistence_baseline` forecast for `predicted_next_load`.
- `paper_lstm_forecast` is `false`.
- This keeps the trace explicit without pretending a paper-faithful LSTM forecast exists yet.

## Next-state construction

- `training/trace_dataset.py` pairs each paper-state row with the next row for the same agent and episode.
- That means `next_state` comes from the next runtime snapshot, not from `state.copy()`.
- Terminal rows without a `t+1` snapshot are handled explicitly.

## TraceDataset source choice

- If `paper_state_trace.csv` exists, it is the preferred source.
- Otherwise the loader falls back to legacy lifecycle reconstruction.

## Remaining gaps

- The persistence forecast is still not the final paper LSTM.
- Waiting-time and active-load fields are runtime-native, but the paper may require a stricter forecasting pipeline later.
- Full paper-faithful Phase 3 training remains incomplete.
