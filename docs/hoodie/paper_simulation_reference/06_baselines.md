# 06 — Official Baseline Contract

Figure 10 compares HOODIE against exactly six official baselines:

```text
RO, FLC, VO, HO, BCO, MLEO
```

The active method set is:

```text
HOODIE, RO, FLC, VO, HO, BCO, MLEO
```

There must be no `ORIGINAL_HOODIE_BASELINE`, no `HOODIE_PROPOSED` duplicate method, and no `MQO` active paper baseline.

## 1. HOODIE

### Paper says

HOODIE is the proposed trained DRL method using DQN/DDQN/Dueling/LSTM and load forecasting.

### Implementation requirement

The simulator must label whether HOODIE is:

- trained paper-faithful policy;
- deterministic substitute;
- interface-only.

Only the trained policy can support paper reproduction claims.

## 2. RO — Random Offloader

### Paper says

Each agent randomly chooses local, vertical, or horizontal offloading with equal probability. If horizontal is selected, the destination EA is randomly selected with probability `1/(N-1)`.

### Implementation requirement

RO must produce stochastic actions and must not use queue or latency information.

### Validation evidence

Action distribution over many tasks should approximate equal local/vertical/horizontal selection, with horizontal destinations spread across legal EAs.

## 3. FLC — Full Local Computing

### Paper says

Each agent always processes all tasks locally.

### Implementation requirement

FLC must always select private queue/local execution.

### Validation evidence

All FLC actions are local. No offloading queue insertions should occur for FLC.

## 4. VO — Vertical Offloader

### Paper says

Each agent always offloads all tasks to the Cloud.

### Implementation requirement

VO must always select Cloud destination through the offloading queue and vertical link.

### Validation evidence

All VO tasks use vertical path and Cloud public queues.

## 5. HO — Horizontal Offloader

### Paper says

Each agent always offloads to another EA. Destination is selected with probability `1/(N-1)` unless topology restrictions are explicitly enforced.

### Implementation requirement

HO must never select local or Cloud. It must not self-offload. Destination legality must follow the topology contract.

### Validation evidence

All HO tasks use horizontal path and public queues at other EAs.

## 6. BCO — Balanced Cyclic Offloader

### Paper says

Each agent selects actions in round-robin order. Example for EA 1:

```text
1st task -> local
2nd task -> Cloud
3rd task -> EA 2
4th task -> EA 3
...
```

### Implementation requirement

BCO must preserve per-agent cyclic state. It must cycle through local, Cloud, and legal EA destinations.

### Validation evidence

Per-agent action sequence must match the round-robin cycle.

## 7. MLEO — Minimum Latency Estimation Offloader

### Paper says

MLEO estimates latency for every placement option and selects the option with minimum estimated total latency.

Options:

```text
private queue
public queue path at each other EA
public queue path at Cloud
```

For local, estimate private waiting plus local service. For offloaded options, estimate:

```text
offloading wait + transmission + public queue estimated wait/service
```

### Implementation requirement

MLEO must not be queue-length-only. It must not be `MQO`. It must compute total estimated latency over all legal options.

### Validation evidence

Artifacts must include candidate latency table for sampled tasks and selected minimum-latency option.

### Failure symptom if missing

If HOODIE and MLEO always tie, likely causes include untrained HOODIE, shared adapter behavior, insufficient environment dynamics, or wrong MLEO implementation.
