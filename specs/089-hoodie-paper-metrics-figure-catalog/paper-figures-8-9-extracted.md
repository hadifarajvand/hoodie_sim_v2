# Extracted HOODIE Paper Figures 8-9

This file is source-of-truth extraction for Feature 089. It was extracted from the HOODIE OCR and original PDF. Codex must use this catalog; it must not redo extraction as its main task.

## Table 4 Defaults

Unless a figure varies a parameter, use Table 4 defaults: P=0.5, R_H=30 Mbps, R_V=10 Mbps, task size [2,2.1,...,5] Mbits, processing density 0.297 gigacycles/Mbit, N=20, topology Figure 7, private/public EA CPU=5 GHz, cloud CPU=30 GHz, training episodes=5000, T=110, slot duration=0.1 sec, task timeout=20 slots=2 sec, learning rate=7e-7, gamma=0.99, Q hidden layers=3x1024, Adam, MSE, target update=2000, LSTM lookback=10, LSTM hidden=1x20, replay=10000, drop penalty=40, batch=64.

## Figure 8 Family: Learning Parameters and Convergence

Priority: `priority_3_training_or_lstm_required`. Catalog only for now. Do not generate deterministic runtime outputs unless trained HOODIE DRL exists.

### Figure 8a

- Metric/y-axis: accumulated or average reward in arbitrary units, negative by convention.
- x-axis: training episode, 0 to 5000.
- Curves: alpha_lr = 1e-9, 5e-9, 1e-8, 1e-7, 5e-7, 7e-7.
- Policy: HOODIE only.
- Setup: Table 4 defaults, P=0.5, N=20, Figure 7 topology.
- Requires training: yes.
- Requires LSTM: paper HOODIE includes LSTM.
- Output status: `later_training_required`.
- PDF verified: yes.
- Extraction confidence: high.

### Figure 8b

- Metric/y-axis: accumulated or average reward in arbitrary units, negative by convention.
- x-axis: training episode, 0 to 5000.
- Curves: gamma = 0.2, 0.4, 0.6, 0.8, 0.99.
- Policy: HOODIE only.
- Setup: Table 4 defaults except gamma sweep; optimal learning rate from Figure 8a.
- Requires training: yes.
- Requires LSTM: paper HOODIE includes LSTM.
- Output status: `later_training_required`.
- PDF verified: yes.
- Extraction confidence: high.

## Figure 9 Family: HOODIE Behavior and Scalability

Priority: `priority_2_hoodie_behavior_output`. These are HOODIE-only behavior/scalability figures. Implement after Priority 1 Figure 10, only with explicit Feature 086/080 claim boundary.

### Figure 9a

- Metric/y-axis: Average Reward (a.u.).
- x-axis: Task Arrival Probability P.
- PDF tick labels show 0, 0.3, 0.5, 0.7, 1; text and Figure 9b use 0.1, 0.3, 0.5, 0.7, 0.9. Use [0.1,0.3,0.5,0.7,0.9] for simulator output and record caveat.
- Curves: N=10, N=15, N=20 agents.
- Policy: HOODIE only.
- Validation: paper uses 200 validation episodes, exploitative actions.
- Output requirement: average_reward by P and N.
- Extraction confidence: medium due axis tick/text mismatch.

### Figure 9b

- Metric/y-axis: Actions Count.
- x-axis: Action Type.
- Categories: Local, Horizontal, Vertical.
- Bars: Task Prob=0.1, 0.3, 0.5, 0.7, 0.9.
- Policy: HOODIE only.
- Output requirement: action count and action share by P and action type.
- Extraction confidence: high.

### Figure 9c

- Metric/y-axis: Average Reward (a.u.).
- x-axis: CPU Computation Capacity (GHz).
- Sweep values: 4,5,6,7,8,9 GHz.
- Curves: N=10, N=15, N=20 agents.
- Policy: HOODIE only.
- Output requirement: average_reward by CPU capacity and N.
- Extraction confidence: high.

### Figure 9d

- Metric/y-axis: Average Reward (a.u.).
- x-axis: Number of Agents N.
- Sweep values: 10,15,20,25,30.
- Curves: Moderate Traffic, Heavy Traffic, Extreme Traffic.
- Moderate: task sizes 1-3 Mbits, P=0.5.
- Heavy: task sizes 2-5 Mbits, P=0.7.
- Extreme: task sizes 3-7 Mbits, P=0.9.
- Policy: HOODIE only.
- Output requirement: average_reward by N and traffic scenario.
- Blocker: requires varying N and workload-size range support.
- Extraction confidence: high.

### Figure 9e

- Metric/y-axis: Average Reward (a.u.).
- x-axis: Number of Agents N.
- Sweep values: 10,15,20,25,30.
- Curves: Balanced, Horizontal-centric, Vertical-centric.
- Balanced: R_H=10 Mbps, R_V=30 Mbps.
- Horizontal-centric: R_H=20 Mbps, R_V=20 Mbps.
- Vertical-centric: R_H=5 Mbps, R_V=40 Mbps.
- Policy: HOODIE only.
- Output requirement: average_reward by N and data-rate scenario.
- Blocker: requires varying N and data-rate support.
- Extraction confidence: high.
