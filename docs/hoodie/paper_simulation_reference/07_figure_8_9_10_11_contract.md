# 07 — Figure 8/9/10/11 Generation Contract

This file defines when outputs for Figures 8, 9, 10, and 11 may be called paper-faithful. It is not a plotting-style guide. It is a simulation-output contract.

## 1. Figure 8 — Training Convergence

### Paper says

Figure 8 is produced from real HOODIE training traces.

### Figure 8a

```text
x-axis: Training Episode, 0..5000
y-axis: Average Reward / accumulated reward
series: alpha_lr = 1e-9, 5e-9, 1e-8, 1e-7, 5e-7, 7e-7
```

### Figure 8b

```text
x-axis: Training Episode, 0..5000
y-axis: Average Reward / accumulated reward
series: gamma = 0.2, 0.4, 0.6, 0.8, 0.99
```

### Implementation requirement

Figure 8 requires actual training. If real training traces do not exist, Figure 8 must remain gated.

### Failure symptom if missing

A deterministic validation trace, placeholder, or synthetic curve must not be used as Figure 8 evidence.

## 2. Figure 9 — HOODIE Behavior and Scalability

### Paper says

Figure 9 uses optimally trained HOODIE Q-models and 200 validation episodes. It analyzes HOODIE only, not baselines.

### Figure 9a

```text
metric: average reward
x-axis: task arrival probability P
series: N = 10, 15, 20
sweep: P = 0.1, 0.3, 0.5, 0.7, 0.9
```

Expected behavior: reward becomes more negative as P increases.

### Figure 9b

```text
metric: action count
x-axis: action type Local, Horizontal, Vertical
groups: P = 0.1, 0.3, 0.5, 0.7, 0.9
```

Expected behavior: horizontal offloading is frequently preferred; vertical can increase under heavier load.

### Figure 9c

```text
metric: average reward
x-axis: CPU computation capacity, 4..9 GHz
series: N = 10, 15, 20
```

Expected behavior: higher CPU capacity improves reward.

### Figure 9d

```text
metric: average reward
x-axis: N = 10, 15, 20, 25, 30
series: Moderate, Heavy, Extreme traffic
```

Traffic definitions:

```text
Moderate: task size 1-3 Mbits, P=0.5
Heavy: task size 2-5 Mbits, P=0.7
Extreme: task size 3-7 Mbits, P=0.9
```

### Figure 9e

```text
metric: average reward
x-axis: N = 10, 15, 20, 25, 30
series: Balanced, Horizontal-centric, Vertical-centric
```

Data-rate definitions:

```text
Balanced: R_H=10 Mbps, R_V=30 Mbps
Horizontal-centric: R_H=20 Mbps, R_V=20 Mbps
Vertical-centric: R_H=5 Mbps, R_V=40 Mbps
```

### Implementation requirement

Figure 9 generation must be based on HOODIE validation episodes after training, or explicitly marked as current-simulator/non-paper-faithful. The N sweep must actually change number of EAs. Traffic and data-rate scenarios must actually change runtime configuration.

### Failure symptom if missing

If Figure 9 is generated from deterministic approximations, it may be useful for debugging but cannot support paper behavior claims.

## 3. Figure 10 — Baseline Comparative Analysis

### Paper says

Figure 10 compares seven policies over 200 validation episodes:

```text
HOODIE, RO, FLC, VO, HO, BCO, MLEO
```

Metrics:

```text
average computation delay
drop ratio
```

### Critical timeout split

```text
Figure 10a-c delay plots: timeout = 10 sec
Figure 10d-e drop-ratio plots: timeout = 2 sec
Figure 10f: timeout sweep = 1.6, 1.8, 2.0, 2.2, 2.4 sec
```

This split is mandatory. Using the same timeout regime for all Figure 10 plots is wrong.

### Figure 10a

```text
metric: average delay
x-axis: P = 0.1, 0.3, 0.5, 0.7, 0.9
y-axis: negative seconds for plotting only
```

### Figure 10b

```text
metric: average delay
x-axis: CPU = 3, 4, 5, 6, 7 GHz
timeout: 10 sec
```

### Figure 10c

```text
metric: average delay
x-axis: timeout = 9.6, 9.8, 10.0, 10.2, 10.4 sec
```

### Figure 10d

```text
metric: drop ratio
x-axis: P = 0.1, 0.3, 0.5, 0.7, 0.9
timeout: 2 sec
```

### Figure 10e

```text
metric: drop ratio
x-axis: CPU = 3, 4, 5, 6, 7 GHz
timeout: 2 sec
```

### Figure 10f

```text
metric: drop ratio
x-axis: timeout = 1.6, 1.8, 2.0, 2.2, 2.4 sec
```

### Implementation requirement

For every sweep point and every policy:

- run independent validation episodes;
- record arrived/completed/dropped denominators;
- compute raw positive delay internally;
- apply negative delay only as a plot transform;
- compute drop ratio as dropped / arrived.

### Failure symptom if missing

All-policy ties, zero delays, one-task traces, zero completions, or 100% drop saturation across all policies are signs of simulation or adapter failure.

## 4. Figure 11 — LSTM Ablation

### Paper says

Figure 11 compares HOODIE with and without LSTM.

```text
x-axis: Training Episode, 0..3000
y-axis: Average Delay sec
series: Without LSTM, With LSTM
setup: N=20, P=0.3, task deadline=1 sec
```

Reported behavior:

```text
With LSTM around 0.35 sec
Without LSTM around 0.48 sec
```

### Implementation requirement

Figure 11 requires two trained variants: with LSTM and without LSTM. If those traces do not exist, Figure 11 must remain gated.

### Failure symptom if missing

A static comparison, deterministic forecast interface, or validation-only curve is not Figure 11.
