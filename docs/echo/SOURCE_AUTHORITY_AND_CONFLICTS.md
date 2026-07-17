# ECHO source authority and conflict register

## Locked authority

1. `02_ECHO-Article_Current.tex` is binding for the ECHO method, equations,
   Algorithms 1–2, event order, evaluation protocol, and Figures 5–8.
2. `03_ECHO-Article_Current_Source.zip` supports the same TeX and assets.
3. `HOODIE_paper.pdf` is authoritative only for mechanisms the current ECHO TeX
   explicitly inherits.
4. Repository code is implementation evidence, not specification authority.
5. The current pre-results PDF is a visual cross-check only.

Exact source identifiers and SHA-256 values are recorded in
`configs/echo/authoritative_source_lock.json`.

## Superseded design choices

The following older choices conflict with the current TeX and are forbidden in
new implementation and tests:

| Superseded choice | Current binding rule |
|---|---|
| predicted-risk reward term | only one fixed extra penalty for a realized deadline drop |
| ERT clipping | no ERT clipping is part of the current method |
| appending ERT or masks to the neural observation | inherited HOODIE observation remains unchanged |
| feature-normalization changes specific to ECHO | inherited state preprocessing remains unchanged |
| destination queue reordering | destination source-indexed queues remain FIFO |
| active-service preemption | source computation and transmission remain non-preemptive |
| random action when all routes are late | deterministic minimum-lateness fallback with fixed route-index tie-break |
| mask only during greedy inference | the same effective mask is used for exploration, exploitation, and Double-DQN online next-action selection |
| Figure 8 as broad mechanism ablation | Figure 8 compares ECHO and ECHO-NoLSTM only; other ablations are supplementary |

## Current repository conflict

The historical mixed runtime under `src/environment/gym_adapter.py` exposes
`echo_state_vector`, `echo_candidate_ert`, and `echo_deadline_mask` in the
observation path. That path must not be used for final ECHO training because it
violates the locked no-ERT-in-state boundary. The isolated
`src/echo_verified` package is fail-closed scaffolding for verified controls and
a transparent paired physical-kernel pilot while the shared production kernel
is reconstructed and differentially tested.

## Evidence boundary

Deterministic mechanism smoke and paired physical-kernel pilot outputs are
labelled non-paper evidence. They may validate wiring, accounting, and control
semantics, but they may not replace Figures 5–8 or support superiority claims.
