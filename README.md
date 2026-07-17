# ECHO and HOODIE simulation — Figures 5–8

This is the single canonical repository for the ECHO thesis simulation and the reproduced HOODIE baseline.

## Current scientific goal

Verify the shared HOODIE runtime and learner, implement ECHO only as the limited extension locked by the current manuscript, then generate traceable empirical outputs for Figures 5–8.

ECHO changes only:

- ERT ordering for waiting private and outbound source queues;
- predicted-completion route filtering;
- minimum-lateness fallback when all routes are predicted late;
- the same effective mask during exploration, exploitation, and Double-DQN bootstrapping;
- one additional fixed realized deadline-drop penalty.

ECHO must not change the inherited neural observation, LSTM architecture, Dueling Double-DQN lifecycle, replay format, destination FIFO order, equal destination sharing, non-preemptive service, topology, task generation, or episode lifecycle.

## Canonical location

```text
Repository: hadifarajvand/hoodie_sim_v2
Branch:     main
Local:      /Users/hadi/Documents/GitHub/hoodie_sim_v2
Run root:   /Volumes/ADATA-1TB-External/echo_outputs
```

Do not create another repository, clone, fork, mirror, or worktree for this project unless explicitly requested.

## Fetch and install

```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2

git remote set-url origin https://github.com/hadifarajvand/hoodie_sim_v2.git
git fetch --prune origin main
git switch main
git reset --hard origin/main

python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'

bash scripts/echo/verify_single_repository.sh
```

Use `git reset --hard origin/main` only after confirming there is no local work that must be preserved.

## Verified bounded surfaces

Control-mechanism smoke:

```bash
rm -rf /Volumes/ADATA-1TB-External/echo_outputs/control-smoke
bash scripts/echo/run_verified_smoke.sh \
  /Volumes/ADATA-1TB-External/echo_outputs/control-smoke
```

Paired physical-kernel pilot:

```bash
rm -rf \
  /Volumes/ADATA-1TB-External/echo_outputs/paired-kernel-pilot \
  /Volumes/ADATA-1TB-External/echo_outputs/paired-kernel-pilot.zip \
  /Volumes/ADATA-1TB-External/echo_outputs/paired-kernel-pilot.zip.sha256

bash scripts/echo/run_paired_kernel_pilot.sh \
  /Volumes/ADATA-1TB-External/echo_outputs/paired-kernel-pilot

cd /Volumes/ADATA-1TB-External/echo_outputs
shasum -a 256 -c paired-kernel-pilot.zip.sha256
```

These outputs are validation evidence only and are labelled `NOT PAPER EVIDENCE`.

## Next execution stage

The next stage is application-surface verification through the installed `hoodie-experiments` CLI:

1. bounded real HOODIE training;
2. held-out evaluation;
3. checkpoint round-trip reload;
4. fixed-trace HOODIE versus ECHO-disabled differential execution;
5. malformed-input probes;
6. a real trained pilot with 2–3 seeds.

Do not start the paper-scale 10-seed × 200-held-out-episode campaign until the trained pilot and all lineage checks pass.

## Runtime storage and safety

All checkpoints, traces, logs, metrics, manifests, figures, and archives belong under:

```text
/Volumes/ADATA-1TB-External/echo_outputs
```

Never run or mutate `figures-8-11-7587c7c6382c`. Never use projected values as empirical evidence. Never use broad process-killing commands. Never force-push `main` during normal development.

See:

- `docs/echo/SINGLE_REPOSITORY_POLICY.md`
- `docs/scientific-contracts/`
- `configs/contracts/`
