# ECHO full-matrix execution smoke

The command below is the mandatory execution gate before any paper-scale ECHO
campaign:

```bash
hoodie-experiments echo-full-matrix-smoke \
  --run-root /absolute/path/outside/the/repository \
  --campaign-id echo-full-matrix-smoke-001
```

It executes the real simulator and compact real learners across every operating
point in the current ECHO manuscript. It does not synthesize, digitize, project,
or interpolate result curves.

The comparison hierarchy is locked as follows:

- Figure 7: ECHO, reproduced HOODIE, RO, FLC, VO, HO, BCO, and MLEO.
- Figure 8 only: ECHO and ECHO-NoLSTM.
- Figures 5 and 6: ECHO learning-parameter, behavior, and scalability panels.
- Figure 4: the topology used by the simulator.

The smoke executes all 15 panels but uses one seed, three training episodes,
one held-out episode per point, 16 slots, and compact networks. Its output is
always labelled `FULL-MATRIX EXECUTION SMOKE — NOT PAPER EVIDENCE`.

The paper campaign remains a separate, gated run: 5,000 training episodes,
10 fixed seeds, 200 held-out episodes per seed and operating point, 110 slots
(100 decision plus 10 drain), 3×1024 networks, replay capacity 10,000, batch
size 64, and target copy period 2,000.

Acceptance requires paired traces, task conservation, all eight Figure 7
methods at every point, the correct Figure 8 ablation boundary, checkpoint and
configuration provenance, panel/seed/mean-CI CSV files, and PDF/SVG/300-dpi PNG
exports for Figures 4–8.
