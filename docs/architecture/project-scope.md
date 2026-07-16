# Project scope and canonical repository layout

## Primary scientific objective

The repository exists to implement and reproduce the HOODIE paper through one traceable path: frozen contracts, deterministic simulation, HOODIE training, baseline evaluation, exact checkpoint dependencies, panel-specific Figures 8–11 datasets, executable verification, and a reproducibility bundle.

A green status file is not a scientific result. Every pass condition must be derived from datasets, hashes, dependencies, and executable checks.

## Active scope

- HOODIE simulator, learning method, and required baselines
- immutable experiment matrix and source contracts
- distributed execution and completed-only import
- bounded checkpoint storage
- aggregation, verification, rendering, and release packaging
- unit, integration, and acceptance tests

ECHO thesis extensions, historical diagnostics, obsolete pilots, readiness reports, and generic agent frameworks are downstream, archived, or external. They must not participate in the active HOODIE runtime.

## Canonical layout

```text
src/hoodie/{agents,environment,policies,training,evaluation,experiments,storage,visualization}
tests/{unit,integration,acceptance}
configs/{paper,pilot,production}
docs/{architecture,plans,run-logs,scientific-contracts,runbooks}
resources/{papers/hoodie,references}
scripts/{audit,experiments}
artifacts/approved
```

Generated data belongs under an external `$HOODIE_RUN_ROOT`, never in tracked source.

## Authoritative modules

- campaign state: `hoodie.experiments.campaign`
- job execution: `hoodie.experiments.executor`
- distributed transport: `hoodie.experiments.distributed`
- scientific verification: `hoodie.experiments.verification`
- rendering: `hoodie.visualization.figures_8_11`
- checkpoints: `hoodie.storage.checkpoints`

Import-time patches, `*_v2.py` modules, competing campaign implementations, legacy `src.*` imports inside `src/hoodie`, and active ECHO dependencies are not canonical architecture.

## Mandatory gate

```bash
python scripts/audit/repository_consolidation_gate.py --check
```

No experiment may start until this gate and the full repository audit pass from a clean checkout.
