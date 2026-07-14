# ECHO–HOODIE Paired Pilot Evidence Gate

## Purpose

This gate replaces curve manipulation with a bounded run of the actual shared
simulator. It is the first evidence-producing step before any publication-scale
campaign.

## Scientific boundary

- Digitized HOODIE article curves are **not** inputs to the pilot.
- They remain external reproduction targets used only after the simulator emits
  its own HOODIE measurements.
- The pilot is not publication-grade evidence. It validates paired traces,
  method isolation, event-SMDP execution, task accounting, and artifact lineage.
- No result is required to make ECHO outperform HOODIE.

## Method isolation

Both methods use the same topology, physical slot kernel, runtime capacities,
and materialized task traces.

- `HOODIE` retains FIFO source queues and its legacy delayed task-reward path.
- `ECHO` alone receives deadline-valid action masking, deterministic ERT source
  queue reconstruction, minimum-lateness fallback, and the agent-specific
  event-epoch SMDP transition path.

## Paired pilot outputs

The pilot writes:

- `pilot_manifest.json`;
- `summary.csv`;
- `paired_trace_metrics.csv`;
- full raw ECHO evaluation JSON;
- full raw HOODIE evaluation JSON;
- per-trace metrics produced by the evaluation subsystem.

Every trace must satisfy

```text
completed_tasks + dropped_tasks = total_tasks
```

ECHO and HOODIE must have identical held-out `(trace_id, seed)` sets.
Training and held-out evaluation seeds must be disjoint.

## Scale handling contract

The article's scalability sweep uses one maximum-size architecture supporting
30 EAs. For a run with fewer EAs, absent-node feature blocks are zero padded,
corresponding actions are masked, and a node-presence indicator distinguishes
an absent node from a present node with zero load. A separate checkpoint is
trained for each network size; no zero-shot transfer claim is made. This pilot
uses the approved 20-EA topology and therefore validates the default operating
point, not the complete scalability sweep.

## Gate decision

The next step may begin only when CI shows:

1. event-SMDP unit tests pass;
2. ECHO/HOODIE training-isolation integration tests pass;
3. the paired-pilot integration test passes;
4. the bounded pilot completes;
5. the raw evidence artifact is downloadable and task accounting is exact.

After this gate, expand to multiple seeds and the article's parameter sweeps.
Do not replace manuscript projections until the authoritative campaign and its
confidence intervals are complete.
