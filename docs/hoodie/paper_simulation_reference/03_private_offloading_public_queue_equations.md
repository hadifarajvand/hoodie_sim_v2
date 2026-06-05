# 03 — Private, Offloading, and Public Queue Equation Contract

This file defines the paper-faithful queue mechanics that must exist before Figure 9/10 outputs can be treated as HOODIE paper simulation outputs.

## 1. Private Queue

### Paper says

A task selected for local processing enters the private FIFO queue of its source EA.

Private waiting time:

```text
w_priv_n(t) = max(0, max_{t' < t}{psi_priv_n(t')} - t + 1)
```

Private queue exit slot:

```text
psi_priv_n(t) = min(
  t + w_priv_n(t) + ceil(eta_n(t) * rho_n(t) / (f_EA_priv_n * Delta)) - 1,
  t + phi_n(t) - 1
)
```

Default private CPU:

```text
f_EA_priv_n = 5 GHz
```

### Meaning

The first branch is successful local completion. The second branch is timeout. The task exits the queue either because it completed or because it reached the deadline.

### Implementation requirement

The simulator must store both:

- `queue_exit_slot`
- `task_status`: `completed` or `dropped_timeout`

It is wrong to store only a completion slot without preserving whether the task actually completed or timed out.

### Validation evidence

Artifacts must include:

- private queue waiting time;
- local service time;
- private queue exit slot;
- completion/drop reason;
- private completed count;
- private timeout/drop count.

### Failure symptom if missing

If completion and timeout are collapsed into one field, average delay and drop ratio become unreliable.

## 2. Offloading Queue

### Paper says

A task selected for offloading first enters the source EA offloading FIFO queue.

Offloading waiting time:

```text
w_off_n(t) = max(0, max_{t' < t}{psi_off_n(t')} - t + 1)
```

Data rates:

```text
horizontal R_H = 30 Mbps
vertical R_V = 10 Mbps
```

Offloading queue exit slot:

```text
psi_off_n(t) = min(
  t + w_off_n(t) + ceil(sum_k d_n,k^(2)(t) * eta_n(t) / (R_off_n,k * Delta)) - 1,
  t + phi_n(t) - 1
)
```

### Meaning

`psi_off_n(t)` is not final task computation completion. It is only the slot when transmission to the selected destination finishes, or when the task times out before successful transmission.

### Implementation requirement

The simulator must separate:

- source offloading queue waiting;
- transmission time;
- offloading queue exit status;
- destination public queue insertion time;
- final public computation completion/drop.

### Validation evidence

Artifacts must include:

- offloading queue wait;
- selected link type: horizontal or vertical;
- rate used: `R_H` or `R_V`;
- transmission slots;
- offloading exit status;
- public queue insertion if transmission succeeds.

### Failure symptom if missing

If offloading is treated as direct completion, horizontal/vertical delay will be too simple and MLEO/HOODIE behavior will not match the paper mechanism.

## 3. Public Queue Active Set

### Paper says

Public queues are source-specific. Public queue `n` at node `k` stores tasks that originated at EA `n` and were offloaded to node `k`.

A public queue is active at slot `t` if:

```text
eta_pub_n,k(t) > 0 OR l_pub_n,k(t-1) > 0
```

Let:

```text
A_k(t) = set of active public queues at node k
|A_k(t)| = active public queue count at node k
```

### Meaning

Public service is not independent per task. The node's public CPU is divided between currently active source-specific public queues.

### Implementation requirement

At every slot, for each destination node:

1. find all active public queues;
2. compute `|A_k(t)|`;
3. divide public CPU by active queue count;
4. reduce public queue workloads using the allocated CPU;
5. record final completion when the queued task workload reaches zero;
6. record timeout/drop if the original task deadline is exceeded.

### Validation evidence

Artifacts must include:

- active public queue count per node per slot;
- public CPU allocation per active public queue;
- queue length before/after service;
- completed public task IDs;
- timeout public task IDs.

### Failure symptom if missing

If public queues use a fixed service time or a single global queue, the simulator is not implementing HOODIE. Figure 9/10 may collapse, tie, or saturate.

## 4. Public Queue Length Update

### Paper says

For an EA destination, public queue length evolves as:

```text
l_pub_n,k(t) = max(
  0,
  l_pub_n,k(t-1) + eta_pub_n,k(t) - m_pub_n,k(t)
  - Delta * f_EA_pub_k / (rho_n(t) * |A_k(t)|)
)
```

For the Cloud, replace `f_EA_pub_k` with:

```text
f_Cloud = 30 GHz
```

Default public EA CPU:

```text
f_EA_pub_k = 5 GHz
```

### Implementation requirement

Represent public queue workload in a consistent unit. If bits are used, CPU service must be converted through processing density. If cycles are used, task size and density must be converted at queue insertion.

The code must document the unit used.

### Validation evidence

Artifacts must include:

- unit of queue length;
- incoming public workload;
- allocated CPU;
- service amount;
- remaining queue length;
- completion/drop status.

### Failure symptom if missing

Unit mismatch can create zero delays, impossible completions, or 100% drop saturation.

## 5. Completion vs Drop Status Contract

For every task and every queue path, the simulator must maintain:

```text
pending
transmitting
in_public_queue
completed
dropped_timeout
```

A task may exit a queue because it completed the required stage, or because it reached timeout. Those are not the same metric event.

### Validation evidence

Final episode artifacts must include:

- arrived count;
- completed count;
- dropped count;
- unresolved count;
- completion path breakdown;
- drop path breakdown.

### Failure symptom if missing

Metric denominators become wrong. Drop ratio and average delay become untrustworthy.
