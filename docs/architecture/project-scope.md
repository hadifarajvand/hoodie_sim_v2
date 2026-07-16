# Project scope and canonical repository layout

## Primary scientific objective

The repository exists to implement and reproduce the HOODIE paper through a single traceable path:

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

### Downstream or archived

- ECHO thesis extensions;
- prior diagnostic campaigns;
- obsolete pilots and readiness reports;
- historical specifications and reconciliation transports.

### External tooling

Claude, RuFlo, OpenCode, Graphify, and similar tools are installed and configured outside this repository. Their generated agents, commands, daemon state, metrics, and PID files are not project source.

## Canonical layout

```text
src/
  hoodie/                 scientific orchestration and public package
  agents/                 current learner implementations during migration
  environment/            physical simulator
  policies/               baseline policy implementations
  training/               training primitives
  evaluation/             evaluation primitives

tests/
  unit/
  integration/
  acceptance/
tests_supported/hoodie/   active compatibility suite during migration

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
  hoodie/

artifacts/
  approved/               small immutable manifests only
```

The temporary top-level `src.agents`, `src.environment`, and related imports remain compatibility paths while migration to `hoodie.*` is completed. New modules must use `hoodie.*` package paths where practical. No second implementation of a scientific responsibility may be introduced.

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
```

Production execution must refuse a run root inside the tracked repository unless an explicit test-only override is active.

## Authoritative responsibilities

- campaign planning and state: `hoodie.experiments.campaign`
- matrix-job execution: one authoritative executor selected by the CLI
- distributed bundles: `hoodie.experiments.distributed`
- verification and rendering: the scientific pipeline selected by the CLI
- checkpoint storage: `hoodie.storage.checkpoints`

Legacy compatibility modules may delegate to these implementations, but they must not implement competing behavior.

## Completion definition

Repository consolidation is complete when:

- the repository audit classifies every tracked file;
- runtime/tool state is absent from Git;
- all active tests are discovered by one pytest configuration;
- a clean editable install imports the package;
- checkpoint writes are atomic and storage-bounded;
- a tiny clean-checkout pilot passes end to end;
- the immutable production matrix is unchanged after it is frozen;
- the production run uses external storage and external compute;
- no unique scientific reference or evidence is lost.
