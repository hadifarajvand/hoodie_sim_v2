# HOODIE Figures 8–11: 100-Episode ECHO Reproduction

This campaign reproduces the original HOODIE paper's Figure 8–11 panel structure while adding ECHO as the proposed method.

- Figure 8: ECHO learning-rate and discount-factor convergence sweeps.
- Figure 9: ECHO behavior and scalability using the original five subfigures and axes.
- Figure 10: ECHO compared with HOODIE, RO, FLC, VO, HO, BCO, and MLEO in all six original subfigures.
- Figure 11: ECHO versus ECHO-NoLSTM, with LSTM use as the only variant difference.

The run uses 100 training episodes per checkpoint, 100 deterministic held-out episodes per evaluation point, one seed, 110 slots, and the paper architecture (three 1024-unit hidden layers, ten-step lookback, and 20 LSTM cells). It is a preliminary reproduction, not the 5,000-episode multi-seed paper-evidence campaign.

Run or resume:

```bash
hoodie-experiments echo-base-figures-100 \
  --run-root /path/to/output-root \
  --campaign-id echo-hoodie-figures-8-11-100-001
```

Inspect progress without changing the campaign:

```bash
hoodie-experiments echo-base-figures-100-status \
  --run-root /path/to/output-root \
  --campaign-id echo-hoodie-figures-8-11-100-001
```

Training is atomically checkpointed after every episode. Each completed evaluation point is cached with its 100 per-episode summaries. Re-running the execution command resumes completed work.
