# 04 — State, Reward, Cost, and Delayed Collection Contract

## 1. Historical Load Matrix

### Paper says

The load of a node is the number of active public queues. Edge Controllers track load history for all EAs and the Cloud.

```text
L(t) shape = W × (N + 1)
W = 10
```

Each column corresponds to one node. Each row corresponds to a previous time slot in the lookback window.

### Meaning

The model observes recent public-load dynamics, not only instantaneous local queue length.

### Implementation requirement

The simulator must maintain per-slot active public queue counts for every EA and the Cloud. The state builder must be able to construct `L(t)` for every EA decision.

### Validation evidence

Artifacts must include:

- active public queue counts by node and slot;
- lookback window size;
- generated matrix shape;
- missing-padding policy at early slots.

### Failure symptom if missing

If load history is static, omitted, or fake, LSTM behavior and long-term HOODIE behavior are not paper-faithful.

## 2. LSTM Forecast Boundary

### Paper says

HOODIE uses LSTM to forecast upcoming load from `L(t)`.

### Implementation requirement

The simulator must explicitly declare one of:

- `trained_lstm`: real trained LSTM forecast is used;
- `deterministic_forecast_substitute`: not paper-faithful, but documented;
- `gated_no_lstm_trace`: LSTM-dependent figures remain gated.

### Validation evidence

Reports must include the forecast mode and whether Figure 8/11 claims are allowed.

### Failure symptom if missing

A deterministic interface can be mistaken for trained LSTM. This invalidates Figure 11 and weakens Figure 9/10 claims.

## 3. HOODIE State Vector

### Paper says

The state for EA `n` is:

```text
s_n(t) = [eta_n(t), w_priv_n(t), w_off_n(t), l_pub_n(t-1), L(t)]
```

### Meaning

The agent sees:

- current task size;
- private queue waiting time;
- offloading queue waiting time;
- its public queue footprint at other nodes;
- historical load matrix.

### Implementation requirement

State records must preserve enough fields to rebuild and audit the state used for every policy action.

### Validation evidence

Artifacts must include state summaries for sampled tasks, including all five state components.

### Failure symptom if missing

If HOODIE sees only a simplified action candidate table, it is not the paper state model.

## 4. Reward and Cost Model

### Paper says

Reward is negative cost.

```text
if no task arrived: reward = NaN
if task completed before timeout: reward = -Phi_n(t)
if task dropped: reward = -C
```

Default penalty:

```text
C = 40
```

Local cost:

```text
Phi_priv_n(t) = psi_priv_n(t) - t + 1
```

Offloaded cost:

```text
Phi_pub_n(t) = psi_pub_n,k(t') - t + 1
```

### Meaning

Offloaded task delay is measured from original arrival at the source EA to final completion at the destination public queue.

### Implementation requirement

Rewards must be attached to the original task/action only when the task completes or drops. Reward must not be guessed at action time unless the implementation is explicitly marked as an approximation.

### Validation evidence

Artifacts must include:

- original arrival slot;
- action slot;
- final completion/drop slot;
- reward collection slot;
- delay/cost;
- penalty flag.

### Failure symptom if missing

DQN training experiences become invalid and average reward trends cannot reproduce the paper behavior.

## 5. Delayed Reward Collection

### Paper says

At a slot, the system collects rewards for tasks that completed at that slot, including tasks that arrived earlier.

### Implementation requirement

The runtime must maintain a pending task registry:

```text
task_id -> original state, action, source, path, deadline, current status
```

When the task completes or drops, the reward event must be emitted and linked back to the original experience.

### Validation evidence

Artifacts must include:

- pending task count by slot;
- reward events by slot;
- tasks completed during drain;
- tasks dropped during drain;
- unresolved tasks after episode end.

### Failure symptom if missing

Reward and queue dynamics become same-slot approximations, which is not the paper's training process.
