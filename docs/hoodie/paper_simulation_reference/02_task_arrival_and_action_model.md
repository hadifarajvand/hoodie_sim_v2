# 02 — Task Arrival, Task Features, and Action Model Contract

## 1. Task Arrival

### Paper says

At the start of each slot, every EA receives a new task with Bernoulli probability `P`.

```text
x_n(t) = 1 if a task arrives at EA n at slot t
x_n(t) = 0 otherwise
```

Default:

```text
P = 0.5
```

Figure sweeps use values such as:

```text
P = {0.1, 0.3, 0.5, 0.7, 0.9}
```

### Meaning

Arrival is per EA per slot. It is not one global task event per slot. In a 20-EA environment with 100 action slots and `P=0.5`, the expected number of arrivals is roughly `20*100*0.5=1000` before drain.

### Implementation requirement

The simulator must generate independent per-EA Bernoulli arrivals for each action slot. Sweep `P` must affect the arrival generator itself, not only output labels.

### Validation evidence

Artifacts must include:

- configured `P`;
- total possible arrival opportunities `N * action_slots`;
- total arrived tasks;
- arrived task count by EA;
- random seed;
- expected vs observed arrival-rate diagnostic.

### Failure symptom if missing

If traces have one task or zero completions per sweep point, the simulator is not running paper-scale validation. Figure 9/10 outputs will collapse or tie.

## 2. Task Features

### Paper says

Each task has:

```text
task ID u_n(t)
source EA n
arrival slot t
size eta_n(t)
processing density rho_n(t)
timeout phi_n
```

Default values:

```text
eta_n(t) ∈ [2, 2.1, ..., 5] Mbits
rho_n(t) = 0.297 gigacycles/Mbit
phi_n = 20 slots = 2 sec
```

If no task arrives:

```text
u_n(t)=0
eta_n(t)=0
```

### Implementation requirement

Every actual task must preserve:

- source EA;
- arrival slot;
- size;
- density;
- timeout;
- selected action;
- status;
- completion/drop time.

Task size must feed:

- local service time;
- transmission time;
- public queue load;
- public service time;
- reward/delay.

### Validation evidence

Artifacts must include task-size distribution and processing-density value used per experiment.

### Failure symptom if missing

If task size is only metadata or is not used in queue/service formulas, the simulator cannot reproduce delay/drop behavior.

## 3. Two-Level Action Semantics

### Paper says

HOODIE uses two decision modules.

First-level decision:

```text
d_n^(1)(t)=1 -> local/private queue
d_n^(1)(t)=0 -> offloading queue
```

Second-level decision if offloaded:

```text
d_n,k^(2)(t)=1 -> destination node k
```

Allowed destinations:

- another EA;
- Cloud.

Constraints:

- destination cannot equal source EA;
- at most one destination is selected;
- if local is selected, no offloading destination is active.

Action vector:

```text
a_n(t) = [d_n^(1)(t), D_n(t)]
```

### Implementation requirement

Represent actions with at least:

- source EA;
- level-1 local/offload decision;
- destination node if offloaded;
- path type: local, horizontal, vertical;
- legality flag;
- rejection reason for illegal action.

A coarse label may be used only as a derived field, not as the only source of truth.

### Validation evidence

Artifacts must show:

- action counts by path;
- destination counts;
- illegal self-offload rejection count;
- action distributions per policy;
- Figure 9b action counts preserving probability groups.

### Failure symptom if missing

If action identity loses destination information, HO, BCO, MLEO, and horizontal load behavior cannot be implemented correctly.
