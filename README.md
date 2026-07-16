# HOODIE simulation and Figures 8–11 reproduction

This repository implements a scientifically traceable reproduction pipeline for the HOODIE paper.

## Main goal

Produce one correct, reproducible path from the frozen paper contracts to:

1. the HOODIE environment and learning method;
2. the required baseline policies;
3. dependency-safe training and evaluation;
4. panel-specific datasets for Figures 8–11;
5. executable scientific verification;
6. final traceable figures and a reproducibility bundle.

ECHO thesis development is downstream of this baseline. Generic agent frameworks, runtime orchestration state, historical reports, and generated experiment outputs are not part of the scientific runtime.

## Quick validation

```bash
python scripts/audit/full_repository_audit.py --check
bash scripts/hoodie/corrected_campaign.sh validate
```

Do not start a paper-scale run unless both commands pass.

## Run storage

Production and pilot runs must be stored outside the tracked repository:

```bash
export HOODIE_RUN_ROOT=/absolute/path/on/large-storage/hoodie-runs
```

The run root contains campaign data, checkpoints, replay snapshots, worker state, logs, aggregates, figures, and release bundles. These files are intentionally excluded from Git.

## Safety boundary

The paused legacy campaign `figures-8-11-7587c7c6382c` must never be run, resumed, renamed, imported into, or modified.

Do not use process-killing commands. Workers stop cooperatively at completed-episode boundaries.

## Repository policy

Keep source, tests, configs, scientific contracts, approved paper references, concise architecture documents, and small reproducibility manifests in Git.

Do not commit generated runs, checkpoints, replay buffers, raw datasets, PID files, daemon state, large logs, temporary transport payloads, caches, or generic agent-framework distributions.

See [docs/tracking-policy.md](docs/tracking-policy.md), [docs/architecture/project-scope.md](docs/architecture/project-scope.md), and [docs/runbooks/hoodie-corrected-campaign.md](docs/runbooks/hoodie-corrected-campaign.md).
