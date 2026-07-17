# Verified ECHO smoke output schema

All files produced by `scripts/echo/run_verified_smoke.sh` are bounded,
hand-checkable mechanism evidence and carry the label:

`SMOKE ONLY — NOT PAPER-SCALE RESULT`

- `summary.json`: pass/fail assertions, task conservation, control diagnostics.
- `queue_decisions.csv`: FIFO head, ERT-selected waiting task, fallback flag.
- `route_decisions.csv`: predicted completion, ERT, lateness, effective mask.
- `destination_fifo.csv`: source-indexed FIFO heads and equal capacity shares.
- `task_ledger.csv`: deadline-boundary success, drop, and fixed-penalty evidence.
- `diagnostics.csv`: route-filter fraction, fallback rate, queue-order changes,
  and measured deterministic-control runtime.

No smoke value may be copied into Figures 5–8 or used to support a manuscript
performance claim.
