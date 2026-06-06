# Phase 1 Runtime Tracing

## What This Does

Phase 1 adds traceability and validation artifacts only.

It does not change:

- queue math
- reward math
- topology legality
- learning behavior
- offloading policy behavior

## How to Run with Tracing

Run the simulator with a trace output directory:

```bash
python main.py --epochs 1 --log_folder log_folder --trace_output_dir outputs/phase1_traces
```

## Where Outputs Go

The trace exporter writes:

- `outputs/phase1_traces/task_lifecycle.csv`
- `outputs/phase1_traces/queue_trace.csv`
- `outputs/phase1_traces/action_trace.csv`
- `outputs/phase1_traces/episode_metrics.csv`

## How to Validate

Run:

```bash
python phase1_trace_validation.py outputs/phase1_traces
```

## What Phase 1 Does Not Claim

- It does not make the simulator paper-faithful.
- It does not generate paper figures.
- It does not change the learning algorithm.
- It does not fix reward semantics or queue semantics.

