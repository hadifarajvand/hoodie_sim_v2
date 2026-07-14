# Final ECHO–HOODIE Evaluation

This branch is the isolated implementation workspace for the final manuscript evaluation. The live Google Doc and the original HOODIE paper are the scientific authorities. Existing repository behavior is not accepted merely because it runs or passes historical tests.

## Final ECHO scope

ECHO differs from reproduced HOODIE only by:

1. non-preemptive ERT ordering of waiting private-queue and offloading-queue tasks;
2. ERT-based removal of routes predicted to miss the deadline;
3. minimum-lateness fallback when no route is predicted feasible;
4. one fixed deadline-drop penalty added to the original HOODIE reward.

The HOODIE state, LSTM, Dueling Double-DQN, replay memory, target network, epsilon schedule, destination public queues, equal capacity sharing, and training procedure remain unchanged.

## Prohibited shortcuts

- No surrogate or projected ECHO values.
- No digitized HOODIE values presented as reproduced outputs.
- No hard-coded plotted points or manual curve shaping.
- No ECHO state-vector expansion, SMDP path, new Q target, or new replay-transition semantics.
- No full campaign before the neutral kernel, HOODIE reproduction, and method-isolation gates pass.

## Execution gates

### Gate 1 — source lock

`configs/echo_final/source_lock.json` must pass its static contract test. The topology, sweep grids, default parameters, methods, metrics, deadline rule, statistical protocol, and figure numbering are frozen.

### Gate 2 — neutral physical kernel

Prove task conservation, exact deadline handling, transmission timing, non-preemptive local/transmission service, source-indexed public FIFO queues, and equal public-capacity sharing independently of any policy.

### Gate 3 — HOODIE reproduction

Replace compatibility preference/fallback behavior with the paper-defined distributed Dueling Double-DQN path. Verify the paper state/action representation, delayed task reward, checkpointing, deterministic evaluation, and all six baselines on the same kernel.

### Gate 4 — ECHO isolation

Add the four approved deltas behind explicit configuration flags. A runtime diff must prove that ECHO and HOODIE are otherwise identical.

### Gate 5 — pilot

Run one seed and a reduced training budget only to test learning, task conservation, trace equality, action legality, queue-order changes, filtering, fallback, reward delivery, output lineage, and renderability. Pilot numbers cannot enter the article.

### Gate 6 — full campaign

Run 5,000 training episodes where required, then 10 paired held-out seeds × 200 episodes per point. Freeze raw logs, seed aggregates, confidence intervals, and panel datasets before plotting.

### Gate 7 — manuscript closure

Render Figures 5–8 and the lambda_D sensitivity table from frozen datasets, insert measured findings, rebuild TeX/PDF, inspect the PDF, and retire superseded generated outputs.

## Approved figure numbering

- Figures 1–3: ECHO method figures.
- Figure 4: verified 20-EA topology.
- Figure 5: arrival-probability sweep.
- Figure 6: EA-capacity sweep.
- Figure 7: timeout sweep.
- Figure 8: five-configuration ablation.

## First executable target

The first runnable target is not the final campaign. It is a deterministic kernel and HOODIE smoke test that emits:

- immutable trace hash;
- generated/success/drop reconciliation;
- per-task decision and terminal records;
- queue-service order;
- action legality;
- checkpoint metadata;
- method-isolation report.
