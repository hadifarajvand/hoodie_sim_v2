# HOODIE Paper Simulation Reference

Source: HOODIE paper PDF and OCR in `resources/papers/hoodie/`.

Purpose: this is the canonical repository reference for how the HOODIE paper simulation is structured. Read this before changing HOODIE simulator behavior.

## Core Simulation Model

The paper simulates a three-layer Cloud-Edge Continuum: IoT areas, Edge Agents, and one Cloud. There are `N` Edge Agents and one Cloud node indexed as `N+1`. Each task is non-divisible and must be processed as a whole locally, horizontally at another Edge Agent, or vertically at the Cloud.

Each Edge Agent has one private queue for local tasks, one offloading queue for tasks selected for offloading, and public queues for tasks received from other Edge Agents. The Cloud has public queues only. If EA 5 offloads to EA 3, the task goes to public queue 5 of EA 3.

The faithful runtime paths are:

- local: arrival -> private queue -> local CPU;
- horizontal: arrival -> offloading queue -> horizontal link -> public queue at another EA -> public CPU;
- vertical: arrival -> offloading queue -> vertical link -> public queue at Cloud -> cloud CPU.

## Time and Tasks

The paper uses time-slotted episodes. Default settings include `T=110` slots and slot duration `Delta=0.1 sec`. The first 100 slots are action slots and the final 10 slots drain queues and collect rewards for pending tasks.

At the start of each slot, every EA receives a task with Bernoulli probability `P`. Task size is sampled from `[2, 2.1, ..., 5] Mbits`, processing density is `0.297 gigacycles/Mbit`, and default timeout is `20 slots = 2 sec`.

## Decisions

Decision-making is two-level. First, `DM(1)` selects local processing or offloading. Second, if offloading was selected, `DM(2)` chooses a destination: another EA or the Cloud. A task cannot be offloaded to its own public queue and can be sent to at most one destination.

The action is therefore not merely a label. It contains the local/offload decision and the destination decision.

## Queues

Private queue waiting depends on previous private queue completion slots. Private completion is the minimum of actual local processing completion and timeout.

Offloading queue waiting depends on previous offloading queue completion slots. Offloading completion covers waiting and transmission only. Horizontal transmission uses `R_H=30 Mbps`; vertical transmission uses `R_V=10 Mbps`.

Public queues are source-specific. Public CPU is shared equally among active public queues. Each EA has public CPU `5 GHz`; the Cloud has `30 GHz`. This active-queue CPU sharing is essential and must not be replaced by a single generic queue.

## State and Reward

The HOODIE state includes task size, private waiting time, offloading waiting time, public queue footprint, and historical load matrix `L(t)` with lookback window `W=10`. The LSTM predicts upcoming load.

Reward is delayed until a task completes or drops. If no task arrived, reward is NaN. If a task completes before timeout, reward is negative delay cost. If it drops, reward is `-C`, with `C=40`.

## Training and Validation

The paper uses trained distributed DRL agents: DQN, Double-DQN, Dueling-DQN, LSTM, experience replay, target network, and epsilon-greedy exploration.

Default training parameters include `5000` episodes, replay memory `10000`, batch size `64`, learning rate `7e-7`, discount `0.99`, hidden layers `3 x 1024`, Adam optimizer, MSE loss, target update `2000`, LSTM lookback `10`, and LSTM hidden layer `1 x 20` cells.

Inference uses trained Q-models with epsilon fixed to zero. Figures 9 and 10 use 200 validation episodes.

## Figures

Figure 8 requires real training reward traces. Figure 9 requires trained HOODIE validation sweeps. Figure 10 compares HOODIE with RO, FLC, VO, HO, BCO, and MLEO over 200 validation episodes. Figure 11 requires trained with-LSTM and without-LSTM traces.

Figure 10 uses two regimes: delay figures use timeout `10 sec`; drop-ratio figures use timeout `2 sec`. Drop ratio is total dropped tasks divided by total arrived tasks across all EAs. Average delay is shown negative by convention, but raw delay must remain positive.

## Minimum Faithful Checklist

A paper-faithful simulator must implement: slotted episodes, Bernoulli arrivals, paper task sizes, processing density, timeout, private queue, offloading queue, public queues, active public CPU sharing, historical load matrix, LSTM forecast or truthful gate, delayed reward collection, HOODIE training/inference boundary, all official baselines, 200 validation episodes, and the Figure 10 timeout split.

If these are absent, outputs are current-simulator outputs only, not HOODIE paper reproduction evidence.
