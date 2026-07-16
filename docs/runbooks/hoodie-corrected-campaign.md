# HOODIE corrected Figures 8–11 campaign runbook

## Safety boundary

This runbook creates a new campaign whose ID starts with
`figures-8-11-corrected-`. It must never run, resume, import into, rename, delete,
or otherwise mutate the paused legacy campaign
`figures-8-11-7587c7c6382c`. Legacy checkpoints whose backend is
`legacy_unknown` remain unchanged.

Do not use process-killing commands. Workers stop cooperatively at completed
training-episode boundaries and resume from the same persistent work directory.

The corrected scientific matrix currently contains:

- 17 training jobs;
- 288 evaluation jobs;
- 305 jobs in total;
- one independent recurrent DDQN learner per Edge Agent;
- destination-specific actions for local execution, every topology-legal
  horizontal destination, and the Cloud;
- exact checkpoint dependencies for HOODIE evaluation;
- worker-selected CPU, CUDA, or MPS tensor execution that is separate from the
  simulated CPU-rate parameters.

## 1. Choose external runtime storage

All generated campaigns, checkpoints, replay snapshots, worker state, logs,
aggregates, figures, and release bundles must live outside the Git repository.
The filesystem must retain at least 20 GiB and 10% free space.

```bash
export HOODIE_RUN_ROOT=/absolute/path/on/large-storage/hoodie-runs
```

The worker checkpoint defaults are:

```bash
export HOODIE_MAX_CHECKPOINTS_PER_JOB=1
export HOODIE_MAX_CHECKPOINT_GB_PER_JOB=5
export HOODIE_MIN_FREE_GB=20
export HOODIE_MIN_FREE_FRACTION=0.10
export HOODIE_ESTIMATED_CHECKPOINT_MB=2048
```

One latest resumable checkpoint and one external replay snapshot are retained.
The final selected checkpoint is inference-only; replay and optimizer state are
removed after the final checkpoint has been written, load-tested, hashed, and
registered atomically.

## 2. Validate and freeze the corrected campaign

From a clean checkout of the exact remote execution commit:

```bash
bash scripts/hoodie/corrected_campaign.sh validate
```

This command:

1. checks both shell entrypoints;
2. installs the package;
3. inventories every tracked and untracked repository file;
4. rejects tracked runtime/tool/checkpoint files and duplicate critical entrypoints;
5. compiles source and audit scripts;
6. runs scientific preflight;
7. creates the deterministic matrix and shard plan under `HOODIE_RUN_ROOT`;
8. validates every source-contract mapping;
9. runs the complete active pytest configuration;
10. verifies the 17/288/305 counts and worker-selected backend contract;
11. checks storage reserves;
12. writes a validation marker bound to the exact Git commit.

Generated validation evidence is written under:

```text
$HOODIE_RUN_ROOT/audits/repository/
$HOODIE_RUN_ROOT/implementation_run/corrected_campaign/
```

Do not continue if the command fails. Do not manually create or edit the
validation marker.

## 3. Export training bundles

```bash
bash scripts/hoodie/corrected_campaign.sh export-training
```

The command refuses to export when:

- validation did not pass at the current Git commit;
- the destination directory is already nonempty;
- the run root no longer satisfies the disk reserve;
- the campaign ID is not a corrected campaign ID.

Bundles are written beneath:

```text
$HOODIE_RUN_ROOT/distributed/corrected/input/<campaign-id>/training/
```

## 4. Execute training shards

Choose one tensor backend for all 17 training shards. The worker requires an
explicit value:

```bash
export HOODIE_DEVICE=cuda:0   # preferred when assigned and available
# or: export HOODIE_DEVICE=mps
# or: export HOODIE_DEVICE=cpu
```

Run each assigned bundle with a persistent work directory inside
`HOODIE_RUN_ROOT`:

```bash
bash scripts/hoodie/run_shard_worker.sh \
  /absolute/path/to/training-001 \
  "$HOODIE_RUN_ROOT/worker-state/training-001"
```

A bounded allocation may append a maximum runtime in seconds. Exit code 3 means
that the shard is resumable but incomplete. Preserve the same work directory and
run the same command again. Never import an `interrupted_resumable` result.

Worker stdout is retained as a bounded diagnostic tail. Scientific progress is
stored in atomic status and progress files rather than an unbounded log.

## 5. Import and audit training

Collect completed training result directories under the configured training
results directory, then run:

```bash
bash scripts/hoodie/corrected_campaign.sh import-training
```

The importer rejects:

- empty or non-completed result bundles;
- checksum or inventory mismatches;
- duplicate shard identities;
- conflicting prior imports;
- incomplete scientific outputs;
- `legacy_unknown` checkpoints;
- mixed CPU/CUDA/MPS training histories;
- any checkpoint count other than 17.

Evaluation bundles cannot be exported until this audit succeeds.

## 6. Export and execute evaluation

```bash
bash scripts/hoodie/corrected_campaign.sh export-evaluation
```

Bundles are written beneath:

```text
$HOODIE_RUN_ROOT/distributed/corrected/input/<campaign-id>/evaluation/
```

Execute them with the same worker script and explicit backend policy. Every
HOODIE evaluation bundle carries only its declared, scientifically complete
checkpoint dependency. Baseline policies do not acquire a learned HOODIE
checkpoint.

## 7. Import evaluation and inspect status

```bash
bash scripts/hoodie/corrected_campaign.sh import-evaluation
bash scripts/hoodie/corrected_campaign.sh status
```

Do not finalize unless all 305 current matrix jobs are complete and no job is
failed, blocked, interrupted, or scientifically incomplete.

## 8. Finalize

```bash
bash scripts/hoodie/corrected_campaign.sh finalize
```

Finalization performs panel-specific aggregation, executable scientific
verification, rendering of Figures 8–11, and release-bundle export. It must fail
rather than write a success report when a required check fails.

## Agent stop conditions

Stop and report evidence rather than improvising when:

- repository audit, installation, compilation, preflight, contract validation,
  or any active test fails;
- the working tree is dirty or the local commit differs from the assigned remote
  commit;
- `HOODIE_RUN_ROOT` is missing, inside the repository, or below the disk reserve;
- the resolved campaign ID is the paused legacy ID or lacks the corrected prefix;
- a worker commit differs from the bundle source commit;
- a requested tensor backend is unavailable;
- a shard result is not completed;
- the training checkpoint count or backend audit fails;
- an exact evaluation dependency is unavailable;
- imported result hashes conflict;
- current campaign status is not 305/305 complete before finalization.

Never force-push, push experiment changes to `main`, reduce scientific work,
shrink the network, substitute smoke data, fabricate timing or results, delete
unique evidence, or signal unrelated processes.
