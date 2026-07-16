# Local agent execution prompt

You are operating the HOODIE repository at the exact checked-out remote commit.

## Objective

Finish repository consolidation and scientific validation, then execute the corrected Figures 8–11 workflow only after every fail-closed gate passes. Do not merely write readiness reports. Change code, run the real tests, and produce executable evidence.

## Mandatory safety

- Never run, resume, rename, import into, delete, or modify the paused legacy campaign `figures-8-11-7587c7c6382c`.
- Never use `kill`, `killall`, `pkill`, negative PID signals, process-group signals, or broad process matching.
- Never force-push.
- Never reduce scientific episode counts, slot counts, matrix rows, model dimensions, policy coverage, or parameter grids.
- Never place generated runs, checkpoints, replay buffers, worker state, raw datasets, or large logs in Git.
- Use `HOODIE_RUN_ROOT` outside the repository.
- Keep one physical checkpoint per training job by default and one latest replay snapshot only.

## First actions

1. Confirm the working tree is clean. If dirty, stop without reset, clean, stash, delete, or overwrite.
2. Record branch, HEAD, remote branch SHA, disk free space, and `HOODIE_RUN_ROOT`.
3. Run:

```bash
python scripts/audit/repository_consolidation_gate.py --check \
  --report "$HOODIE_RUN_ROOT/audits/repository/consolidation_gate.json"
python scripts/audit/full_repository_audit.py --check \
  --output-dir "$HOODIE_RUN_ROOT/audits/repository"
```

4. Resolve every reported issue in the repository. Do not bypass, weaken, or delete the gates.

## Required consolidation

- Canonical installed package: `src/hoodie/` imported as `hoodie.*`.
- Canonical tests only: `tests/unit`, `tests/integration`, `tests/acceptance`.
- Remove active use of `tests_supported`, `tests_historical`, top-level `hoodie/`, `*_patch.py`, `*_v2.py`, import-time monkey patching, `src.*` imports inside `src/hoodie`, and active ECHO dependencies.
- Fold behavior into exactly one authoritative implementation for campaign state, job execution, distributed transport, checkpoint storage, verification, aggregation, rendering, and finalization.
- Preserve unique historical evidence externally with SHA-256 manifests before untracking it.
- Keep only source, tests, configs, scientific contracts, approved references, concise docs, and small immutable manifests in Git.

## Required validation

From a clean checkout of the pushed commit:

```bash
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

1. freeze the exact runtime SHA, matrix hash, source-contract hash, and shard plan;
2. export training shards;
3. run training before evaluation on the configured external worker environment;
4. import only completed checksum-verified result bundles;
5. audit all selected checkpoints and their exact SHA-256 dependencies;
6. export and run evaluation shards;
7. aggregate panel-specific datasets;
8. run executable scientific verification;
9. render Figures 8–11;
10. create and verify the reproducibility bundle.

Do not start the paper-scale workload on an unsuitable local CPU host. Use the user's configured external compute/agent environment. Never claim completion from metadata-only or manually assigned success booleans.

## Git workflow

Work only on `chatgpt/experiment-correctness-20260716`. Use small coherent commits and normal pushes. Do not merge into target or main. Do not mark the PR ready until all gates and clean-checkout validation pass.

## Final report

Report exact branch/SHA, changed files, commands, complete test counts, gate results, clean-checkout evidence, checkpoint size/retention, storage root, campaign and shard counts, training/evaluation dependency proof, aggregate/figure/bundle paths, and confirmation that no PID was killed and the paused legacy campaign was untouched.
