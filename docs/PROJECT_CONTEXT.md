# Project Context

This repository implements and validates HOODIE edge/cloud simulation and research workflows.

Current detected stack:

- Python source and pytest-style tests.
- Research artifacts and paper-alignment reports.
- SpecKit feature workflow.
- Project-local OpenCode/Ruflo/Graphify workflow under `.opencode/`.

No active frontend/backend/API/database stack has been detected. Treat web-app workflows as future scope until real package/config files appear.

## Main Directories

| Directory | Purpose |
|---|---|
| `src/` | Source code (agents, environment, simulation, training, analysis) |
| `tests/` | pytest test suite (unit, integration) |
| `configs/` | Simulation configuration files |
| `docs/` | Project documentation, Graphify usage, session checkpoints |
| `specs/` | SpecKit feature specifications (078-nnn) |
| `artifacts/` | Research analysis outputs and campaign bundles |
| `resources/` | Reference data and resources |
| `graphify-out/` | Generated knowledge graph |

## Key Documentation Files

| File | Purpose |
|---|---|
| `AGENTS.md` | Agent instructions and rules |
| `docs/GRAPHIFY_USAGE.md` | Graphify usage guide |
| `docs/PROJECT_CONTEXT.md` | This file |
| `docs/SESSION_CHECKPOINTS.md` | Session checkpoint log |

## Graph Status

- Graph exists: `graphify-out/graph.json` (~16MB, 13916 nodes, 23966 edges)
- Report: `graphify-out/GRAPH_REPORT.md`
- Visualization: `graphify-out/graph.html`
- Safe query wrapper: `scripts/graphify-query-safe.sh`

## OpenCode Status

- OpenCode v1.17.11 with `freellmapi/auto` model
- Project-local `.opencode/` with commands, agents, skills, tools, hooks, plugins
- Ruflo MCP is wired into the OpenCode config for orchestration
- Global skill catalog: 100+ skills at `~/.opencode/skills/`
- MCP: Ruflo configured; additional templates remain available

## Installed Workflow Surface

- Local commands include build-fix, docs-update, graphify, architecture-map, simulation-plan, dataset-audit, experiment-runner, and result-validation.
- Local agents now include planner, architect, code-reviewer, test-reviewer, graphify-navigator, simulation-reviewer, reproducibility-reviewer, and the existing HOODIE-specific reviewers.
- Local skills now include OpenCode workflow, Ruflo workflow, Graphify workflow, Python/research guidance, security review, verification loop, checkpointing, and future web engineering guidance.
- Project-local script wrappers exist for graph queries, changed-file summaries, project status summaries, safe inspection, and verification.
