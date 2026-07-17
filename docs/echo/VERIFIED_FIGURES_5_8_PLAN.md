# ECHO verified Figures 5–8 program

## Status

This branch supersedes the previous HOODIE Figures 8–11 production objective.
The old corrected campaign and the paused legacy campaign are historical evidence
only. They are not inputs to ECHO empirical claims.

The branch currently contains an **executable mechanism smoke**, not final paper
results. Every smoke output is labelled `SMOKE ONLY — NOT PAPER-SCALE RESULT`.

## Authority order

1. `00_CURRENT/02_ECHO-Article_Current.tex` — binding ECHO method, algorithms,
   evaluation protocol, and Figures 5–8 contract.
2. `00_CURRENT/03_ECHO-Article_Current_Source.zip` — source archive and figure
   assets corresponding to the TeX.
3. `03_REFERENCE_PAPERS/HOODIE_paper.pdf` — authority only for mechanisms the
   current ECHO manuscript explicitly inherits.
4. Repository code — implementation evidence, never specification authority.
5. `00_CURRENT/01_ECHO-Article_Current_PreResults.pdf` — visual cross-check only.

Projected spreadsheets, old ECHO method versions, old execution plans, smoke
reports, digitized curves, and projected figures must never be used as expected
outputs or manuscript evidence.

## Locked boundary

ECHO changes only:

- ordering of **waiting** private-source tasks by ERT;
- ordering of **waiting** outbound-source tasks by end-to-end ERT;
- route filtering by predicted deadline-satisfied completion;
- deterministic minimum-lateness fallback when all physical routes are late;
- use of the same effective action mask in exploration, exploitation, and the
  online next-action selection of Double DQN;
- one fixed extra penalty for a realized deadline drop.

ECHO must not preempt active service, reorder destination queues, append ERT or
mask values to the neural observation, add predicted-risk penalties, or change
any inherited physical/learner mechanism.

## Repository audit finding

The historical runtime path under `src/environment/gym_adapter.py` is not yet an
authoritative ECHO implementation. It constructs an `echo_state_vector` that
contains ERT and mask features and uses simplified queue/load estimates. It must
not be used for final ECHO training until it is replaced or reconciled against
the locked contract and passes differential HOODIE-isolation tests.

The isolated package `src/echo_verified` is the new fail-closed control surface.
It exists so the locked mechanics can be tested independently before they are
connected to the physical kernel.

## Completed in this branch

- machine-readable method contract;
- machine-readable held-out evaluation protocol;
- machine-readable Figures 5–8 output contract;
- deterministic ERT source-queue selection;
- deterministic route filtering and all-late fallback;
- consistent masked exploration/exploitation/Double-DQN target selection;
- isolated fixed deadline-drop penalty;
- task-conservation assertion;
- ERT-in-observation detector;
- exported bounded smoke ledger and diagnostics;
- unit and integration tests;
- portable local runner.

## Remaining critical path

1. Freeze the exact current TeX/source ZIP and original HOODIE PDF with SHA-256.
2. Extract every inherited physical and learner equation into machine-readable
   contracts.
3. Replace the historical mixed runtime with one shared physical kernel.
4. Prove HOODIE against topology, task generation, queueing, equal sharing,
   timeout, reward, LSTM, Dueling Double-DQN, drain, and task-accounting tests.
5. Prove ECHO-disabled produces the same slot/task/replay records as HOODIE.
6. Connect `src.echo_verified` controls to the shared physical kernel without
   adding ERT to the neural observation.
7. Run a hand-calculated physical scenario and a paired pilot.
8. Freeze trace banks, seeds, training budgets, checkpoint selection, and the
   complete Figures 5–8 job matrix.
9. Train ECHO parameter candidates, freeze the selected configuration, and train
   ECHO, HOODIE, and ECHO-NoLSTM checkpoints.
10. Run at least 10 fixed seeds × 200 held-out episodes per seed using paired
    traces, aggregate seed means and 95% confidence intervals, and export all
    lineage-backed data and figures.

No full campaign may start before steps 1–7 pass.

## Local smoke

```bash
git fetch origin echo/verified-figures-5-8
git switch --track -c echo/verified-figures-5-8 \
  origin/echo/verified-figures-5-8

bash scripts/echo/run_verified_smoke.sh \
  /absolute/path/outside/the/repository/echo-verified-smoke
```

Outputs:

- `summary.json`
- `queue_decisions.csv`
- `route_decisions.csv`
- `destination_fifo.csv`
- `task_ledger.csv`
- `diagnostics.csv`
- `README.txt`

These outputs verify control semantics only. They are deliberately unsuitable
for replacing manuscript Figures 5–8.
