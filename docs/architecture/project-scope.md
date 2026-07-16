# Project scope and canonical repository layout

## Primary scientific objective

The repository exists to implement and reproduce the HOODIE paper through one traceable path:

1. frozen source contracts;
2. deterministic environment and traffic traces;
3. HOODIE training and baseline evaluation;
4. exact checkpoint dependencies;
5. panel-specific datasets for Figures 8–11;
6. executable verification;
7. final figures and a reproducibility bundle.

A green status file is not a scientific result. Every pass condition must be derived from datasets, hashes, dependencies, and executable checks.

## Scope boundaries

### Active

- HOODIE simulator and environment;
- HOODIE learning implementation;
- required baselines;
- training/evaluation job matrix;
- distributed shard transport;
- bounded checkpoint storage;
- scientific aggregation, verification, rendering, and release packaging;
- active unit, integration, and acceptance tests.

### Downstream or external

- ECHO thesis extensions;
- prior diagnostic campaigns;
- obsolete pilots and readiness reports;
- historical specifications and reconciliation transports;
- generic agent and orchestration frameworks.

ECHO may consume the completed HOODIE baseline later, but it must not alter the active HOODIE execution package or verification path.

## Canonical layout

```text
src/
  hoodie/
    agents/
    environment/
    policies/
    training/
    evaluation/
    experiments/
    storage/
    visualization/

tests/
  unit/
  integration/
  acceptance/

configs/
  paper/
  pilot/
  production/

docs/
  architecture/
  plans/
  run-logs/
  scientific-contracts/
  runbooks/

resources/
  papers/hoodie/
  references/

scripts/
  audit/
  experiments/

artifacts/
  approved/
```

The active package imports as `hoodie.*` from the `src/` layout. Top-level `hoodie/`, `tests_supported/`, `tests_historical/`, `*_patch.py`, and `*_v2.py` are not accepted in an execution-ready tree.

## Runtime layout

Generated data is external to Git:

```text
$HOODIE_RUN_ROOT/
  campaigns/
  distributed/
  worker-state/
  checkpoint-store/
  releases/
  logs/
  audits/
```

Production execution must refuse a run root inside the tracked repository. The run root must retain at least 20 GiB and 10% free space after each checkpoint write.

## Authoritative responsibilities

- campaign planning and state: `hoodie.experiments.campaign`
- matrix-job execution: `hoodie.experiments.executor`
- distributed bundles: `hoodie.experiments.distributed`
- verification: `hoodie.experiments.verification`
- rendering: `hoodie.visualization.figures_8_11`
- checkpoint storage: `hoodie.storage.checkpoints`

There must be one implementation of each responsibility. Import-time monkey patches and competing v2 modules are not canonical architecture.

## Mandatory consolidation gate

```bash
python scripts/audit/repository_consolidation_gate.py --check
```

The gate blocks experiment execution while tracked generated artifacts, legacy package/test roots, compatibility patches, legacy `src.*` imports, active ECHO dependencies, packaging inconsistencies, or missing canonical modules remain.

## Completion definition

Repository consolidation is complete when:

- the repository audit classifies every tracked file;
- the consolidation gate reports zero issues;
- runtime/tool state and historical generated artifacts are absent from Git;
- one package imports cleanly as `hoodie.*`;
- one pytest configuration discovers all active tests;
- one implementation owns each scientific responsibility;
- checkpoint writes are atomic and storage-bounded;
- a tiny clean-checkout pilot passes end to end;
- the immutable production matrix is unchanged after it is frozen;
- production runs use external storage and external compute;
- no unique scientific reference or evidence is lost.
