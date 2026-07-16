# Repository Tracking Policy

This repository contains the active HOODIE scientific implementation, tests, frozen contracts, approved references, and concise reproducibility documentation. Generated execution state and historical diagnostic output live outside the active Git tree.

## Track in Git

- `src/hoodie/`
- `tests/unit/`
- `tests/integration/`
- `tests/acceptance/`
- `configs/`
- current architecture, plans, runbooks, and scientific contracts under `docs/`
- approved HOODIE contracts and paper references under `resources/papers/hoodie/`
- approved read-only references under `resources/references/`
- small immutable manifests under `artifacts/approved/`
- repository governance files such as `README.md`, `AGENTS.md`, `.gitignore`, and `pyproject.toml`

## Do not track

- campaign directories, worker state, raw datasets, replay buffers, or checkpoint payloads
- generated aggregate data and rendered outputs from intermediate attempts
- PID files, daemon state, sockets, logs, JSONL event streams, or local tool configuration
- `.claude/`, `.claude-flow/`, `.opencode/`, `.swarm/`, or `.mcp.json`
- `artifacts/analysis/`, `artifacts/control/`, `artifacts/reports/`, `artifacts/smoke/`, `artifacts/test_triage/`, reconciliation payloads, or superseded readiness reports
- temporary transport fragments, source-export workflows, virtual environments, caches, coverage output, and build artifacts
- generic agent-framework distributions

## Canonical active roots

The active Python package is `src/hoodie/` and imports as `hoodie.*`. The active test roots are exactly:

- `tests/unit/`
- `tests/integration/`
- `tests/acceptance/`

Top-level `hoodie/`, `tests_supported/`, and `tests_historical/` are migration or historical roots and must not remain in the execution-ready tree.

## Historical evidence

Unique historical evidence must not be deleted blindly. Hash and index it, then move it to external release/archive storage. Keep only a concise index or immutable approved manifest in Git.

## Required gates

Before any experiment:

```bash
python scripts/audit/repository_consolidation_gate.py --check
python scripts/audit/full_repository_audit.py --check
```

Both commands must pass from a clean checkout. A failing consolidation gate means the repository remains in audit mode and no training may start.

## Review rule

Before staging or merging a large change, verify that:

- no ignored or generated runtime files are staged;
- no nested repositories or local virtual environments remain;
- every tracked path has an explicit active purpose;
- no duplicate execution implementation or compatibility patch remains;
- all unique references and historical evidence have a documented destination.
