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

The validator reports:

- task count consistency
- unique `task_id` coverage
- `selected_action` coverage by final status
- trace consistency warnings where the legacy runtime does not expose enough fields for a strict failure

## Metric Definitions

The episode metrics are computed from the traced task rows for a single episode.

| metric_name | numerator/source | denominator | interpretation | known limitation |
| --- | --- | --- | --- | --- |
| `average_latency` | sum of `latency` values from task lifecycle rows with non-null `latency` | count of task rows with non-null `latency` | mean end-to-end delay for finalized tasks that expose latency | pending tasks and tasks without terminal timestamps are excluded |
| `average_waiting_time` | sum of `waiting_time` values from task lifecycle rows with non-null `waiting_time` | count of task rows with non-null `waiting_time` | mean time spent waiting before service starts | tasks that never start service are excluded |
| `average_service_time` | sum of `service_time` values from task lifecycle rows with non-null `service_time` | count of task rows with non-null `service_time` | mean service duration for tasks that expose service time | tasks that never reach service completion are excluded |
| `drop_ratio` | `dropped_tasks` from episode metrics | `total_tasks` from episode metrics | fraction of generated tasks that ended in drop | if `total_tasks` is zero, the current code returns `0.0` |
| `average_queue_length` | sum of queue lengths recorded in queue traces for the episode | count of queue trace rows recorded for the episode | mean recorded queue length across all queue trace samples | this is a trace-sample average, not a time-weighted queue integral |
| `total_reward` | accumulated episode reward passed into the tracer | no additional denominator | total reward accumulated by the legacy runtime for the episode | still depends on the legacy reward path |
| `mean_reward` | `total_reward` passed into the tracer | number of recorded reward accumulations used by the caller | average reward reported by the runner for the episode | if no reward samples are accumulated, the caller currently falls back to `0.0` |

## What Phase 1 Does Not Claim

- It does not make the simulator paper-faithful.
- It does not generate paper figures.
- It does not change the learning algorithm.
- It does not fix reward semantics or queue semantics.

## Regression Note

Phase 1.1 does not currently provide a strict tracing-vs-no-tracing determinism check because the legacy runtime does not expose a clean external seed control for repeated identical runs. That is a limitation of the existing simulator, not a tracing claim. A future cleanup can add explicit seed plumbing and then compare paired runs.
