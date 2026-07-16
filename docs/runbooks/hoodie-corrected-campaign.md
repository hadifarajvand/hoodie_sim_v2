# HOODIE corrected Figures 8–11 campaign runbook

## Safety boundary

This runbook creates and executes a new campaign whose ID starts with
`figures-8-11-corrected-`. It must never run, resume, import into, rename, or
otherwise mutate the paused legacy campaign `figures-8-11-7587c7c6382c`.
Legacy checkpoints whose backend is `legacy_unknown` remain unchanged.

The corrected scientific matrix contains 305 jobs:

- 17 training jobs;
- 288 evaluation jobs;
- destination-specific HOODIE actions for local execution, each legal horizontal
  Edge Agent, and the Cloud;
- one independent learner per Edge Agent;
- dependency-gated evaluation shards;
- a worker-selected tensor backend that is separate from the simulated CPU rates.

## 1. Validate and freeze the corrected campaign

From the repository root:

```bash
bash scripts/hoodie/corrected_campaign.sh validate
```

This command validates both shell entrypoints, installs the project, compiles the
supported Python modules, runs the scientific preflight, creates the deterministic
matrix and shard plan, validates all source contracts, runs the supported test
suite, verifies the 17/288/305 job counts and portable backend contract, and writes
the resolved campaign ID to:

```text
artifacts/hoodie/implementation_run/corrected_campaign/campaign.env
```

Do not continue if any command fails.

## 2. Export training bundles

```bash
bash scripts/hoodie/corrected_campaign.sh export-training
```

The default bundle directory is:

```text
artifacts/hoodie/distributed/corrected/input/training
```

Assign each training bundle to persistent external compute. A worker must check
out the exact `source_commit` stored in its `shard_manifest.json` and retain the
same work directory across retries.

Choose one tensor backend for **all 17 training shards**. The supported values are
`cpu`, `mps`, `cuda`, or an indexed CUDA device such as `cuda:0`. For example:

```bash
HOODIE_DEVICE=cuda:0 \
  bash scripts/hoodie/run_shard_worker.sh \
    /absolute/path/to/training-001 \
    /persistent/worker-state/training-001
```

When `HOODIE_DEVICE` is omitted, the worker uses CPU. The worker refuses a requested
CUDA or MPS device when that backend is unavailable.

A bounded worker allocation may append a maximum runtime in seconds. When the
script returns exit code 3, preserve the same work directory and run the same
command again. Partial-episode learner state is never serialized; execution rolls
back to the latest completed episode boundary before resuming. Never import an
`interrupted_resumable` result.

## 3. Collect and import completed training results

Place every completed training result directory under:

```text
artifacts/hoodie/distributed/corrected/results-training
```

Then run:

```bash
bash scripts/hoodie/corrected_campaign.sh import-training
```

The importer rejects empty directories, duplicate shard identities, incomplete
shards, inconsistent job results, checksum failures, and conflicting prior
imports. The command also requires exactly 17 scientifically complete training
checkpoints, rejects `legacy_unknown`, and rejects mixed CPU/CUDA/MPS training
histories. Evaluation bundles cannot be exported until this audit succeeds.

## 4. Export and execute evaluation bundles

```bash
bash scripts/hoodie/corrected_campaign.sh export-evaluation
```

Default bundle directory:

```text
artifacts/hoodie/distributed/corrected/input/evaluation
```

Execute each bundle on assigned external workers using the same persistent-worker
command. The evaluation bundle carries only its declared, completed checkpoint
dependencies. Checkpoints are loaded portably, but use one explicit
`HOODIE_DEVICE` policy across an evaluation batch to keep execution provenance
simple and reproducible.

## 5. Import evaluation results

Collect completed evaluation result directories under:

```text
artifacts/hoodie/distributed/corrected/results-evaluation
```

Then run:

```bash
bash scripts/hoodie/corrected_campaign.sh import-evaluation
bash scripts/hoodie/corrected_campaign.sh status
```

## 6. Finalize only after all 305 jobs are complete

```bash
bash scripts/hoodie/corrected_campaign.sh finalize
```

Finalization refuses an incomplete campaign. A successful finalization performs
aggregation, scientific verification, figure rendering, and release-bundle
export.

## Agent stop conditions

The execution agent must stop and report evidence rather than improvising when:

- validation or tests fail;
- the resolved campaign ID is the paused legacy ID or does not have the corrected
  prefix;
- a worker commit differs from the bundle source commit;
- a requested tensor backend is unavailable;
- a training result is incomplete;
- the training checkpoint count is not exactly 17;
- training checkpoints contain `legacy_unknown` or mixed backend families;
- an evaluation checkpoint dependency is unavailable;
- imported result hashes conflict;
- campaign status is not 305 completed jobs before finalization.

The agent must not force-push, target `main`, silently reduce episodes, shrink the
network, substitute smoke data, fabricate timing estimates, or merge incompatible
checkpoint histories.
