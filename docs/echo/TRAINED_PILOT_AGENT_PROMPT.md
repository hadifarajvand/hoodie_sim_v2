# Agent prompt: learner-backed CLI verification and trained pilot

Copy everything below into the execution agent from the canonical checkout.

---

You are the execution agent for the ECHO Figures 5–8 project.

## Canonical location

Use exactly one repository and one local checkout:

```text
Repository: hadifarajvand/hoodie_sim_v2
Branch: main
Checkout: /Users/hadi/Documents/GitHub/hoodie_sim_v2
External run root: /Volumes/ADATA-1TB-External/echo_outputs
```

Do not create another repository, clone, fork, mirror, worktree, or remote.
Do not switch to a historical branch.
Do not change `origin`.
Do not force-push.
Do not write generated run output into Git.
Do not touch `figures-8-11-7587c7c6382c`.
Do not use `kill`, `killall`, `pkill`, negative PID signals, process-group signals, or broad process matching.
Do not start the paper-scale 10-seed × 200-held-out-episode campaign.

## First commands

```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2
bash scripts/echo/verify_single_repository.sh
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
```

Required:

- branch is `main`;
- fetch and push origin point to `hadifarajvand/hoodie_sim_v2`;
- worktree is clean before the first source edit;
- local and remote main initially match.

A dirty worktree containing changes made by you during this task is not an external blocker. Inspect, complete, validate, commit, and push those task-owned changes to `main`. Never discard unrelated user work.

## Evidence surface

Use the installed application entrypoint as the primary evidence surface:

```text
hoodie-experiments
```

Do not begin with pytest.
Do not use import-and-call snippets as scientific evidence.
Tests may support a repair after an observed application failure, but the real CLI command that exposed the defect must always be rerun.

The CLI path must reach the actual learner, shared physical runtime, replay, checkpoint storage, restart, held-out evaluation, differential comparison, aggregation, and external figure export.

## Locked method

ECHO may change only:

1. ERT ordering for waiting private-source tasks;
2. ERT ordering for waiting outbound-source tasks;
3. route filtering based on predicted completion;
4. minimum-lateness fallback when all physical routes are predicted late;
5. the same effective action mask during exploration, exploitation, and Double-DQN online next-action selection;
6. one additional fixed realized deadline-drop penalty.

ECHO must not change:

- the inherited neural observation;
- LSTM inputs or architecture;
- Dueling Double-DQN lifecycle;
- replay structure;
- optimizer or target-copy schedule;
- destination FIFO order;
- equal destination-capacity sharing;
- active-service non-preemption;
- topology, task generation, or episode lifecycle.

ERT, lateness, completion predictions, and masks may be exported as deterministic control diagnostics, but they must not enter the encoded neural state.

## Required CLI commands

Implement these subcommands on the canonical `hoodie-experiments` entrypoint:

```text
hoodie-experiments echo-train
hoodie-experiments echo-eval
hoodie-experiments echo-diff
hoodie-experiments echo-pilot
hoodie-experiments echo-status
hoodie-experiments echo-verify-run
```

Each command must:

- require an absolute `--run-root` outside the repository;
- print structured JSON status to stdout;
- capture exact arguments, code SHA, backend, seed configuration, trace IDs and hashes, episode counts, checkpoint paths, and output paths;
- write atomically;
- produce manifests and `SHA256SUMS`;
- reject stale or incompatible checkpoints;
- preserve `generated = successful + dropped`;
- never produce a completed marker after failure.

## Correct the historical full-runtime path

Before trained ECHO execution, remove or bypass historical behavior that conflicts with the locked manuscript:

- ECHO-specific event-SMDP training lifecycle;
- ERT appended to observations;
- `echo_state_vector` used by the learner;
- `echo_candidate_ert` used as neural input;
- `echo_deadline_mask` used as neural input;
- predicted-risk reward penalties;
- destination-queue reordering;
- preemption;
- inconsistent masks between action selection and Double-DQN bootstrapping;
- policy-name prefix checks used as the sole ECHO control switch.

Use an explicit ECHO control configuration. The encoded neural observation for HOODIE, ECHO, and ECHO-disabled must have the same schema and dimensions.

## External run directory

Create one unique run directory:

```bash
RUN_ROOT="/Volumes/ADATA-1TB-External/echo_outputs/trained-app-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$RUN_ROOT"
printf '%s\n' "$RUN_ROOT" > "$RUN_ROOT/ACTIVE_RUN_ROOT.txt"
```

Use MPS when available and compatible; otherwise use CPU. Record the selected backend and the reason for fallback.

## Run sequence

### 1. Bounded real HOODIE training

Run through `hoodie-experiments echo-train` with approximately:

- seed `101`;
- 12–20 training episodes;
- 110 total slots;
- 10 drain slots;
- moderate traffic;
- timeout 20;
- real recurrent Dueling Double-DQN;
- real replay updates;
- bounded checkpoint retention.

Capture stdout and stderr with `tee` inside the run root.

Required evidence:

- exact command;
- exit code;
- device;
- seed and trace hashes;
- replay size;
- finite loss values;
- learner and target update counters;
- checkpoint path and SHA-256;
- generated/successful/dropped accounting.

### 2. Held-out evaluation

Run `hoodie-experiments echo-eval` in a new process using the saved checkpoint, a disjoint evaluation seed, and trace hashes absent from training.

Export:

- task records;
- episode records;
- generated/successful/dropped counts;
- drop ratio;
- successful-task delay;
- action distribution;
- trace manifest;
- command log;
- run manifest;
- `SHA256SUMS`.

### 3. Checkpoint round-trip

Restart from the saved checkpoint and compare:

- online tensors;
- target tensors;
- optimizer state;
- replay state and counters;
- learner counters;
- epsilon;
- training configuration;
- source commit;
- action vocabulary;
- observation schema;
- resumed held-out metrics.

Write:

```text
differential/checkpoint-roundtrip/report.json
differential/checkpoint-roundtrip/mismatches.jsonl
```

Required mismatch count: `0`.

### 4. Full-runtime HOODIE versus ECHO-disabled differential

Run identical fixed training and evaluation traces through:

```text
A. HOODIE
B. ECHO with every ECHO control explicitly disabled
```

Compare emitted application artifacts:

- observations;
- encoded neural states;
- actions;
- masks;
- resolved destinations;
- queue and transmission events;
- completion slots;
- drops;
- rewards;
- replay transitions;
- loss sequence;
- online tensors;
- target tensors;
- optimizer state;
- replay state;
- aggregate metrics.

Always write a mismatch ledger, including when it is empty.
Required mismatch count: `0`.

### 5. Failure probes

Run and capture expected nonzero exits for:

- empty seed list;
- duplicate seed;
- stale checkpoint;
- incompatible checkpoint;
- output root inside Git;
- held-out trace reused from training;
- ECHO-disabled configuration with one ECHO control still enabled;
- the same fixed trace run twice.

Expected-invalid commands must print structured errors and must not leave completed markers or valid-looking checkpoints.

### 6. Real trained pilot

After all previous gates pass, run `hoodie-experiments echo-pilot` using:

- seeds `101,202,303`;
- methods `ECHO,HOODIE,ECHO_NO_LSTM`;
- moderate and high-tight scenarios;
- 12–20 real training episodes per seed and method;
- 20 held-out episodes per seed;
- identical paired traces;
- disjoint training and evaluation traces;
- identical resources and learning budgets.

Label every output:

```text
TRAINED PILOT — NOT PAPER EVIDENCE
```

Export:

- real checkpoints and SHA-256 sidecars;
- checkpoint manifests;
- losses and replay summaries;
- transitions;
- task, episode, and seed records;
- paired ECHO–HOODIE differences;
- means and 95% confidence intervals across seed-level measurements;
- completion-estimation error;
- route-filter fraction;
- fallback frequency;
- queue-order differences;
- action distributions;
- ECHO runtime overhead;
- PDF figures;
- SVG figures;
- 300-dpi PNG figures;
- manifest;
- `SHA256SUMS`;
- ZIP archive and SHA-256 sidecar.

No acceptance rule requires ECHO to beat HOODIE.

## Commit and rerun from clean main

Do not commit generated outputs.

After the CLI implementation is coherent:

```bash
git diff --check
git status --short
git add <source-config-doc paths only>
git diff --cached --check
git commit -m "ECHO: add learner-backed CLI trained-pilot workflow"
git push origin main
```

Never force-push.

Then require:

```bash
git status --short
git fetch origin main
git rev-parse HEAD
git rev-parse origin/main
```

The worktree must be clean and both SHAs must match. Rerun the decisive CLI commands from that exact pushed commit.

## Watch the run

Do not launch and abandon a command.

Prefer foreground execution. When an operation exceeds the shell timeout:

- use the single unique run directory;
- record the exact PID in that run directory;
- stream stdout/stderr to one log;
- inspect only that exact PID;
- tail the log periodically;
- query `hoodie-experiments echo-status`;
- inspect manifests and free storage;
- never start a duplicate process without proving the first exited;
- never terminate it with broad process commands.

Report milestones:

- CLI implemented;
- HOODIE training started;
- finite learner updates observed;
- checkpoint written and hashed;
- held-out evaluation complete;
- checkpoint round-trip passed;
- HOODIE/ECHO-disabled differential passed;
- each pilot seed/method completed;
- aggregation complete;
- figures exported;
- archive checksum verified.

## Stop condition

Continue until the bounded trained pilot completes or a genuine external storage, hardware, credential, or permission blocker occurs.

Normal code, packaging, CLI, learner, runtime, trace, checkpoint, aggregation, or figure failures are not external blockers. Diagnose, repair, and rerun the real CLI command.

Do not start the paper-scale campaign.

The final report must include:

- canonical repository and final main SHA;
- proof no second repository or remote was created;
- exact CLI commands and exit codes;
- stdout/stderr paths;
- external output tree;
- backend;
- replay and finite-loss evidence;
- checkpoint hashes;
- round-trip mismatch count;
- HOODIE/ECHO-disabled mismatch count;
- failure-probe results;
- held-out trace separation;
- task conservation;
- trained pilot metrics and paired differences;
- figure paths;
- archive path and SHA-256;
- confirmation projected values were not used;
- confirmation paper-scale execution was not started;
- confirmation no PID was killed;
- confirmation `figures-8-11-7587c7c6382c` was untouched.
