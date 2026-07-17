# ECHO/HOODIE scientific execution instructions

## Mission

Build one scientifically defensible shared simulator and learner for the reproduced HOODIE baseline and the locked ECHO extension, then generate traceable empirical outputs for ECHO Figures 5–8.

The current method, notation, algorithms, references, and evaluation protocol are structurally complete. The primary remaining work is verified implementation and empirical execution.

## Canonical repository

- Repository: `hadifarajvand/hoodie_sim_v2`
- Active branch: `main`
- Local checkout: `/Users/hadi/Documents/GitHub/hoodie_sim_v2`
- External run root: `/Volumes/ADATA-1TB-External/echo_outputs`

Do not create another repository, fork, mirror, clone, remote, or worktree for this project unless the user explicitly requests it.

Before modification or execution:

```bash
bash scripts/echo/verify_single_repository.sh
```

## Authoritative sources

Use, in order:

1. current ECHO TeX and matching source archive;
2. original HOODIE paper for inherited mechanics;
3. repository as implementation evidence only;
4. current pre-results PDF as visual cross-check only.

Never use projected spreadsheets, digitized curves, old method versions, old handoffs, or smoke outputs as expected empirical results.

## Locked ECHO boundary

ECHO may change only:

- ERT ordering for waiting private-source tasks;
- ERT ordering for waiting outbound-source tasks;
- predicted-completion route filtering;
- minimum-lateness fallback when all routes are late;
- the same effective mask during exploration, exploitation, and Double-DQN next-action selection;
- one additional fixed realized deadline-drop penalty.

ECHO must not change:

- the inherited neural observation;
- LSTM inputs or architecture;
- Dueling Double-DQN lifecycle;
- replay format;
- optimizer or target-copy behavior;
- destination FIFO ordering;
- equal destination-capacity sharing;
- active-service non-preemption;
- topology, task generation, or episode lifecycle.

ERT, lateness, and masks are deterministic control metadata and must not enter the encoded neural state.

## Evidence surface

Primary scientific verification must come from the installed application entrypoint:

```text
hoodie-experiments
```

Do not use unit tests or import-and-call snippets as the main evidence. Tests may support repairs, but every observed defect must be rechecked through the real CLI path that reaches learner, runtime, checkpointing, evaluation, aggregation, and generated external artifacts.

## Current execution sequence

1. verify the single repository and external run root;
2. implement learner-backed CLI commands for train, eval, diff, pilot, status, and run verification;
3. run bounded HOODIE training;
4. run held-out evaluation;
5. verify checkpoint restart and exact state round-trip;
6. run full-runtime HOODIE versus ECHO-disabled differential execution;
7. run malformed-input and trace-separation probes;
8. run a real trained pilot with 2–3 fixed seeds;
9. stop before the 10-seed × 200-held-out-episode paper campaign.

## Runtime and safety

- All generated checkpoints, traces, logs, metrics, figures, manifests, and archives belong under `/Volumes/ADATA-1TB-External/echo_outputs`.
- Never commit generated run state.
- Never run, resume, rename, import into, or mutate `figures-8-11-7587c7c6382c`.
- Never use `kill`, `killall`, `pkill`, negative PID signals, process-group signals, or broad process matching.
- Never force-push `main` during normal development.
- Never reduce the locked paper-scale protocol or substitute pilot results for manuscript evidence.
- No acceptance rule requires ECHO to outperform HOODIE.

## Required final proof for the trained pilot

Report:

- exact repository, branch, and commit;
- exact CLI commands and exit codes;
- stdout/stderr paths;
- backend and seed configuration;
- checkpoint paths and SHA-256 values;
- finite loss and replay-update evidence;
- held-out trace separation;
- checkpoint round-trip mismatch count;
- HOODIE/ECHO-disabled mismatch count;
- generated = successful + dropped;
- seed-level metrics and paired differences;
- PDF/SVG/300-dpi PNG paths;
- archive path and SHA-256;
- confirmation projected values were not used;
- confirmation paper-scale execution was not started;
- confirmation no PID was killed;
- confirmation the paused legacy campaign was untouched.
