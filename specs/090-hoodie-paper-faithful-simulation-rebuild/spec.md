# Feature 090: HOODIE Paper-Faithful Simulation Rebuild

## Purpose

Feature 090 rebuilds the simulator mechanisms so they follow the HOODIE paper simulation process. This feature is not about making numerical outputs match the paper. It is about making the simulation mechanism match the paper: runtime, tasks, queues, rewards, training boundary, baselines, validation episodes, metrics, and figures.

Primary reference:

```text
docs/hoodie/paper_simulation_reference/
```

Every implementation task must cite the relevant reference file before changing simulator behavior.

## Problem

Feature 089 proved that the repository can emit paper-style figures, but the simulator is not paper-faithful. Observed defects include all-policy ties, HOODIE/MLEO ties, zero-delay collapse, 100% drop saturation, Figure 9 approximation tags, and gated Figure 8/11 traces.

## Goals

- Implement the paper's time-slotted runtime.
- Implement paper task arrival and task features.
- Implement paper private/offloading/public queue mechanics.
- Implement public active-queue CPU sharing.
- Implement delayed reward collection.
- Implement official baselines correctly.
- Define HOODIE trained/substitute/gated boundary honestly.
- Generate Figure 9/10 from validation episodes once mechanisms are active.
- Keep Figure 8/11 gated unless real training/LSTM traces exist.

## Non-Goals

- No thesis method.
- No DCQ.
- No custom queue redesign.
- No output-sync tuning.
- No fabricated training curves.
- No fabricated LSTM ablation curves.
- No paper reproduction claim until all mechanism checks pass.

## Required Method Groups

Feature 090 is split into internal task groups:

- 090-A: paper-faithful environment/runtime without full DRL training.
- 090-B: official baselines and MLEO on that runtime.
- 090-C: HOODIE training/inference boundary.
- 090-D: Figure 9/10 validation outputs.
- 090-E: Figure 8/11 training/LSTM outputs if traces exist; otherwise gated.

## Functional Requirements

### FR-001 Runtime

The simulator must run 110-slot episodes with 100 action slots and 10 drain slots.

### FR-002 Arrivals

For every EA and every action slot, sample Bernoulli task arrival with probability P.

### FR-003 Task Records

Each task must store ID, source EA, arrival slot, size, density, timeout, action, destination, status, queue path, completion/drop slot, and reward.

### FR-004 Queues

The simulator must implement private, offloading, and source-specific public queues.

### FR-005 Public CPU Sharing

At every slot and destination node, public CPU must be divided across active source-specific public queues.

### FR-006 Completion/Drop Separation

Task queue exit must record whether the task completed or timed out/dropped. A slot alone is insufficient.

### FR-007 Delayed Reward

Reward must be attached when the task completes/drops, linked back to original state/action.

### FR-008 State

HOODIE state must include task size, private wait, offloading wait, public queue footprint, and historical load matrix.

### FR-009 LSTM Boundary

The simulator must declare forecast mode: trained LSTM, deterministic substitute, or gated.

### FR-010 Baselines

Active policy set must be HOODIE, RO, FLC, VO, HO, BCO, MLEO. No MQO and no ORIGINAL_HOODIE_BASELINE.

### FR-011 MLEO

MLEO must estimate total latency: private wait/service or offloading wait + transmission + public wait/service.

### FR-012 Validation

Figure 9/10 must run validation episodes, ideally 200, or report explicit test mode.

### FR-013 Figure 10 Regimes

10a-c use timeout 10 sec. 10d-e use timeout 2 sec. 10f sweeps 1.6-2.4 sec.

### FR-014 Metrics

Metrics must emit arrived/completed/dropped denominators. Drop ratio is dropped/arrived. Delay is arrival-to-final-completion over completed tasks.

## Acceptance Criteria

- Mechanism coverage artifact maps every paper mechanism to code.
- Runtime diagnostics prove slots, arrivals, queues, and drain phase are active.
- Queue diagnostics prove public CPU sharing is active.
- Policy diagnostics prove baseline behavior and MLEO latency table.
- Metric diagnostics prove denominators and non-degeneracy checks.
- Figure readiness report declares each figure ready, partial, or gated.
- No output-sync tuning is performed.

## Final Verdicts

Use one:

```text
feature_090_paper_faithful_simulation_ready
feature_090_paper_faithful_simulation_partial
feature_090_paper_faithful_simulation_blocked
```
