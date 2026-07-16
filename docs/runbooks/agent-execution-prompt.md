# Claude Code HOODIE run-and-watch prompt

You are the execution agent for the corrected HOODIE Figures 8–11 campaign.

Repository branch:
`chatgpt/experiment-correctness-20260716`

Paused legacy campaign — never touch:
`figures-8-11-7587c7c6382c`

## First interaction: select and test output storage

Your first response must ask the user for the absolute output-root path. Even if `HOODIE_RUN_ROOT` is already present, show it only as a candidate and ask the user to confirm or replace it.

Run:

```bash
python scripts/hoodie/validate_run_root.py --path '<USER_PATH>'
```

Show the resolved path, outside-repository check, write/read probe, atomic-replace probe, free space, required reserve, and pass/fail. Ask for an explicit yes before proceeding.

After confirmation:

```bash
python scripts/hoodie/validate_run_root.py \
  --path '<CONFIRMED_PATH>' \
  --write-env-file '<CONFIRMED_PATH>/.hoodie-run-root.env'
```

Source that file in every later Bash call that creates runtime output. Do not assume environment persistence across Claude Code tool calls.

## Preserve the tested runtime package

The tested branch intentionally installs the complete current runtime surface:

- `src.*` scientific implementation packages;
- the public `hoodie` forwarding package;
- entry point `src.hoodie.experiments.cli:main`.

Do not partially migrate `pyproject.toml` to install only `hoodie*`. That previously removed `src.agents`, `src.environment`, and other production dependencies and broke `production_campaign.py`.

Do not begin a repository-wide namespace migration during the simulation run. Fix a concrete failing import only when the bounded smoke or validation reproduces it.

## Safe checkout

Require a clean worktree. Do not reset, clean, stash, discard, or overwrite local changes.

```bash
git fetch origin chatgpt/experiment-correctness-20260716
git switch chatgpt/experiment-correctness-20260716 2>/dev/null \
  || git switch --track -c chatgpt/experiment-correctness-20260716 \
     origin/chatgpt/experiment-correctness-20260716
git merge --ff-only origin/chatgpt/experiment-correctness-20260716
git rev-parse HEAD
git rev-parse origin/chatgpt/experiment-correctness-20260716
```

The two SHAs must match.

## Mandatory bounded smoke

Before campaign validation, run:

```bash
bash scripts/hoodie/run_runtime_smoke.sh
```

This must genuinely execute:

- editable installation;
- public and runtime package imports;
- `production_campaign.py` import;
- one real recurrent-DDQN replay update with finite MSE loss;
- deterministic LSTM forward calls;
- destination-action fidelity tests;
- output-root validator tests;
- corrected matrix planning with exactly 17 training, 288 evaluation, and 305 total jobs;
- worker-selected backend contracts;
- valid HOODIE checkpoint dependencies and no baseline dependencies.

Do not continue when it fails. Diagnose the exact error, make the smallest correct fix, add regression coverage, commit, push normally to the same branch, fetch the resulting remote SHA, and rerun the smoke from a clean checkout.

Do not stop after saying “next fix.” Continue until the smoke passes or a true external resource/permission blocker requires the user.

## Full validation

After the smoke passes:

```bash
source '<CONFIRMED_PATH>/.hoodie-run-root.env'
bash scripts/hoodie/corrected_campaign.sh validate
```

Do not weaken scientific counts, episodes, slots, model dimensions, replay capacity, policies, or parameter sweeps. Fix concrete validation defects and rerun the smoke and complete validation.

## Start and watch the corrected campaign

This prompt authorizes the corrected run after the smoke and full validation pass.

Immediately revalidate storage:

```bash
source '<CONFIRMED_PATH>/.hoodie-run-root.env'
python scripts/hoodie/validate_run_root.py --path "$HOODIE_RUN_ROOT"
bash scripts/hoodie/corrected_campaign.sh storage-check
bash scripts/hoodie/corrected_campaign.sh export-training
```

Read `campaign.env` and the exported training bundle directory from the validated run root. Choose one compatible backend family for every training shard. Prefer CUDA, then MPS; use CPU only when the assigned host is practical.

For each training bundle, use a unique persistent work directory and run:

```bash
HOODIE_DEVICE='<DEVICE>' \
bash scripts/hoodie/run_shard_worker.sh \
  '<ABSOLUTE_BUNDLE_DIR>' \
  '<PERSISTENT_WORK_DIR>'
```

When a worker exits resumably, preserve the exact work directory and rerun the same command. Never import interrupted results.

Watch progress without signalling processes. Periodically run read-only status/storage commands and report concise milestones. Never use `kill`, `killall`, `pkill`, negative PID signals, process-group signals, or broad process matching.

After all 17 training bundles complete:

```bash
source '<CONFIRMED_PATH>/.hoodie-run-root.env'
bash scripts/hoodie/corrected_campaign.sh import-training
bash scripts/hoodie/corrected_campaign.sh export-evaluation
```

Execute every evaluation shard with persistent work directories. Then:

```bash
source '<CONFIRMED_PATH>/.hoodie-run-root.env'
bash scripts/hoodie/corrected_campaign.sh import-evaluation
bash scripts/hoodie/corrected_campaign.sh status
```

Finalize only when status proves 305/305 completed, zero failed, zero interrupted, zero missing, complete panel coverage, and exact checkpoint SHA dependencies:

```bash
source '<CONFIRMED_PATH>/.hoodie-run-root.env'
bash scripts/hoodie/corrected_campaign.sh finalize
```

## Storage and checkpoint safety

Maintain at least 20 GiB and 10% free space. Use one physical checkpoint per training job by default and one latest replay snapshot at most. Checkpoints must be atomic and must not embed task, decision, transition, aggregate, or figure datasets. Never write runtime output into Git.

## Final evidence

Report exact remote SHA, output root, smoke output, full validation result and pytest counts, corrected campaign ID, 17/288/305 counts, backend, training and evaluation completion counts, checkpoint sizes/hashes, final status, aggregate/verification/figure/bundle paths, and confirmation that no PID was killed and the paused legacy campaign was untouched.
