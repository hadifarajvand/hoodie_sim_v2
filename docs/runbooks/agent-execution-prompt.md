# Claude Code execution prompt

You are operating the HOODIE repository at the exact checked-out remote commit.

## Objective

Finish repository consolidation and scientific validation, then execute the corrected Figures 8–11 workflow only after every fail-closed gate passes. Do not merely write readiness reports. Change code, run real tests, and produce executable evidence.

## Mandatory interactive output-root gate

Your **first response to the user** must ask them to provide or confirm the absolute output root for all simulation data.

Use this wording closely:

> What absolute output-root path should I use for the HOODIE run? It must be outside this Git repository, writable, support atomic file replacement, and have at least 20 GiB and 10% free space. I will test it and show you the result before starting any simulation.

Rules:

1. Do not assume `/tmp`, the repository, the current directory, the home directory, or any previously used path.
2. If `HOODIE_RUN_ROOT` is already set, show it only as a candidate and still ask the user to confirm or replace it.
3. Do not start training, evaluation, a pilot, acceptance simulation, shard execution, checkpoint creation, or any command that creates campaign output before the user supplies a path.
4. After the user supplies a path, run exactly this validator from the repository root:

```bash
python scripts/hoodie/validate_run_root.py --path '<USER_SUPPLIED_PATH>'
```

5. The validator must prove all of the following:
   - the resolved path is absolute;
   - it is outside the Git repository;
   - it is a directory or can be created safely;
   - it is writable and searchable;
   - a 4 KiB write/read integrity probe succeeds;
   - atomic replacement succeeds on that filesystem;
   - free space after applying the stricter threshold is at least 20 GiB and 10% of the filesystem.
6. Show the user a concise summary containing:
   - resolved path;
   - outside-repository result;
   - write/read result;
   - atomic-replace result;
   - free bytes or GiB;
   - required free bytes or GiB;
   - pass/fail.
7. Then ask a second explicit question:

> The output root passed all checks. Should I use this exact path and proceed? Please answer yes or no.

8. Do not proceed until the user explicitly answers yes.
9. If the check fails or the user answers no, ask for another path. Never weaken the limits.
10. After confirmation, run the validator again and atomically create a sourceable environment file inside the selected output root:

```bash
python scripts/hoodie/validate_run_root.py \
  --path '<CONFIRMED_PATH>' \
  --write-env-file '<CONFIRMED_PATH>/.hoodie-run-root.env'
```

11. Every subsequent Bash command that can create runtime output must source that file in the same shell invocation, for example:

```bash
source '<CONFIRMED_PATH>/.hoodie-run-root.env'
bash scripts/hoodie/corrected_campaign.sh validate
```

Do not rely on environment variables persisting between separate Claude Code Bash tool calls.

## Mandatory safety

- Never run, resume, rename, import into, delete, or modify the paused legacy campaign `figures-8-11-7587c7c6382c`.
- Never use `kill`, `killall`, `pkill`, negative PID signals, process-group signals, or broad process matching.
- Never force-push.
- Never reduce scientific episode counts, slot counts, matrix rows, model dimensions, policy coverage, or parameter grids.
- Never place generated runs, checkpoints, replay buffers, worker state, raw datasets, or large logs in Git.
- Use only the user-confirmed and validated `HOODIE_RUN_ROOT` outside the repository.
- Keep one physical checkpoint per training job by default and one latest replay snapshot only.

## Repository and validation actions

Only after the output root has passed and the user has explicitly confirmed it:

1. Confirm the working tree is clean. If dirty, stop without reset, clean, stash, delete, or overwrite.
2. Record branch, HEAD, remote branch SHA, disk free space, and the confirmed `HOODIE_RUN_ROOT`.
3. Run:

```bash
source '<CONFIRMED_PATH>/.hoodie-run-root.env'
python scripts/audit/repository_consolidation_gate.py --check \
  --report "$HOODIE_RUN_ROOT/audits/repository/consolidation_gate.json"
python scripts/audit/full_repository_audit.py --check \
  --output-dir "$HOODIE_RUN_ROOT/audits/repository"
```

4. Resolve every reported repository issue. Do not bypass, weaken, or delete the gates.

## Required consolidation

- Canonical installed package: `src/hoodie/` imported as `hoodie.*`.
- Canonical tests only: `tests/unit`, `tests/integration`, `tests/acceptance`.
- Remove active use of `tests_supported`, `tests_historical`, top-level `hoodie/`, `*_patch.py`, `*_v2.py`, import-time monkey patching, `src.*` imports inside `src/hoodie`, and active ECHO dependencies.
- Fold behavior into exactly one authoritative implementation for campaign state, job execution, distributed transport, checkpoint storage, verification, aggregation, rendering, and finalization.
- Preserve unique historical evidence externally with SHA-256 manifests before untracking it.
- Keep only source, tests, configs, scientific contracts, approved references, concise docs, and small immutable manifests in Git.

## Required validation

From a clean checkout of the pushed commit and with the confirmed root sourced:

```bash
source '<CONFIRMED_PATH>/.hoodie-run-root.env'
python -m pip install -e '.[dev]'
python -c 'import hoodie; import hoodie.experiments; import hoodie.storage.checkpoints'
python -m compileall -q src scripts
python -m pytest -q
python scripts/audit/repository_consolidation_gate.py --check
python scripts/audit/full_repository_audit.py --check \
  --output-dir "$HOODIE_RUN_ROOT/audits/repository"
bash scripts/hoodie/corrected_campaign.sh validate
```

Also run a tiny acceptance-only workflow proving:

- real training;
- bounded atomic checkpoint creation;
- cooperative completed-episode interruption and resume;
- one exact dependent evaluation;
- aggregation;
- executable verification;
- rendering;
- bundle export and verification;
- tamper rejection;
- bounded stdout/stderr;
- no more than the configured physical checkpoint count.

Label all tiny outputs `ACCEPTANCE ONLY — NOT PAPER-SCALE RESULT`.

## Production transition

Only after all validation and the tiny clean-checkout acceptance workflow pass:

1. ask the user for explicit approval to begin the paper-scale run;
2. rerun `validate_run_root.py` against the same confirmed path immediately before export;
3. freeze the exact runtime SHA, matrix hash, source-contract hash, and shard plan;
4. export training shards;
5. run training before evaluation on the configured Claude Code/worker environment;
6. import only completed checksum-verified result bundles;
7. audit all selected checkpoints and their exact SHA-256 dependencies;
8. export and run evaluation shards;
9. aggregate panel-specific datasets;
10. run executable scientific verification;
11. render Figures 8–11;
12. create and verify the reproducibility bundle.

Do not start the paper-scale workload on an unsuitable local CPU host. Never claim completion from metadata-only or manually assigned success booleans.

## Git workflow

Work only on `chatgpt/experiment-correctness-20260716`. Use small coherent commits and normal pushes. Do not merge into target or main. Do not mark the PR ready until all gates and clean-checkout validation pass.

## Final report

Report the exact branch/SHA, confirmed output root, output-root validation results, changed files, commands, complete test counts, gate results, clean-checkout evidence, checkpoint size/retention, campaign and shard counts, training/evaluation dependency proof, aggregate/figure/bundle paths, and confirmation that no PID was killed and the paused legacy campaign was untouched.
