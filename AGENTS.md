# HOODIE scientific execution instructions

## Mission

Build one scientifically defensible and reproducible HOODIE simulator that implements the paper environment, learning method, baselines, frozen Figures 8–11 experiments, traceable datasets, and verified figures.

The active priority is the HOODIE paper reproduction. ECHO development, generic agent frameworks, orchestration state, historical reports, and generated run artifacts must not alter or obscure the HOODIE execution path.

## Non-negotiable safety

- Never run, resume, import into, rename, or mutate the paused legacy campaign `figures-8-11-7587c7c6382c`.
- Never relabel `legacy_unknown` checkpoints.
- Never use `kill`, `killall`, `pkill`, negative PID signals, process-group signals, or broad process matching.
- Use foreground commands, cooperative stop requests, completed-episode checkpoint boundaries, and normal process exit.
- Never force-push and never push experiment work directly to `main`.
- Never reduce scientific episodes, slots, model dimensions, matrix rows, or policy coverage to make a production run finish faster.
- Never substitute smoke, pilot, cached, or fabricated outputs for paper-scale results.

## Repository boundaries

Git contains source, tests, configs, scientific contracts, approved references, concise documentation, and small reproducibility manifests.

Git must not contain:

- PID files or daemon state;
- generic Claude/RuFlo/OpenCode distributions;
- checkpoints, replay buffers, raw run datasets, worker directories, or campaign directories;
- large logs, temporary transport parts, caches, generated figures, historical diagnostic outputs, or superseded readiness reports.

Generated runs belong under `HOODIE_RUN_ROOT`, which must point outside the tracked repository for production execution.

## Consolidation requirement

Do not execute any experiment while the repository still contains competing execution paths or compatibility layers. The mandatory first gate is:

```bash
python scripts/audit/repository_consolidation_gate.py --check
```

A nonzero exit means the repository remains in audit/consolidation mode. Resolve every listed path before running training. In particular, remove or migrate:

- tracked generated artifacts outside `artifacts/approved/`;
- top-level `hoodie/`, `tests_supported/`, and `tests_historical/` active roots;
- `*_patch.py`, `*_v2.py`, and competing production-campaign implementations;
- `src.*` imports inside `src/hoodie/`;
- active ECHO dependencies in the HOODIE package;
- noncanonical setuptools and pytest configuration;
- missing canonical executor and visualization modules.

## Required workflow

1. Confirm a clean worktree and exact remote commit.
2. Run `python scripts/audit/repository_consolidation_gate.py --check`.
3. Run `python scripts/audit/full_repository_audit.py --check`.
4. Run `bash scripts/hoodie/corrected_campaign.sh validate`.
5. Inspect free disk space and configured run root.
6. Stop on any failed audit, test, contract, dependency, checksum, backend, or storage-budget check.
7. Execute training shards before evaluation shards.
8. Import completed shard bundles only.
9. Finalize only after the complete immutable matrix is scientifically complete.

## Required proof

Before claiming completion, report:

- exact branch and commit;
- consolidation-gate and repository-audit results;
- full active test result;
- matrix and shard counts;
- run-root and disk-budget result;
- training checkpoint inventory and backend audit;
- evaluation dependency and trace-fairness result;
- aggregate, verification, rendering, and release-bundle paths;
- confirmation that no PID was killed and the legacy campaign was untouched.
