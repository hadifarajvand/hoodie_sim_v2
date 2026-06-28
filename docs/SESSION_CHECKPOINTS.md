# Session Checkpoints

Checkpoints are written only after user approval.

## Template

- Date:
- Scope:
- Changed files:
- Decisions:
- Validation run:
- Failed checks:
- Next actions:

## OpenCode + Graphify Bootstrap Completion (2026-06-26)

- Date: 2026-06-26
- Scope: Complete project-local OpenCode, Ruflo, and Graphify workflow bootstrap and validation
- Changed files:
  - `AGENTS.md`
  - `docs/GRAPHIFY_USAGE.md`
  - `docs/PROJECT_CONTEXT.md`
  - `docs/SESSION_CHECKPOINTS.md`
  - `.opencode/commands/build-fix.md`
  - `.opencode/commands/docs-update.md`
  - `.opencode/commands/graphify.md`
  - `.opencode/commands/architecture-map.md`
  - `.opencode/commands/simulation-plan.md`
  - `.opencode/commands/dataset-audit.md`
  - `.opencode/commands/experiment-runner.md`
  - `.opencode/commands/result-validation.md`
  - `.opencode/agents/planner.md`
  - `.opencode/agents/architect.md`
  - `.opencode/agents/frontend-reviewer.md`
  - `.opencode/agents/backend-reviewer.md`
  - `.opencode/agents/database-reviewer.md`
  - `.opencode/agents/code-reviewer.md`
  - `.opencode/agents/test-reviewer.md`
  - `.opencode/agents/docs-updater.md`
  - `.opencode/agents/graphify-navigator.md`
  - `.opencode/agents/python-reviewer.md`
  - `.opencode/agents/simulation-reviewer.md`
  - `.opencode/agents/reproducibility-reviewer.md`
  - `.opencode/skills/opencode-workflow/SKILL.md`
  - `.opencode/skills/graphify-workflow/SKILL.md`
  - `.opencode/skills/python-research/SKILL.md`
  - `.opencode/skills/security-review/SKILL.md`
  - `.opencode/skills/verification-loop/SKILL.md`
  - `.opencode/skills/checkpointing/SKILL.md`
  - `.opencode/skills/web-engineering/SKILL.md`
  - `scripts/changed-files-summary.sh`
  - `scripts/project-status-summary.sh`
  - `scripts/secret-safe-inspection.sh`
  - `scripts/verification-runner.sh`
  - `scripts/graphify-query-safe.sh`
- Decisions:
  - Keep project-local OpenCode/Ruflo/Graphify as the primary workflow surface
  - Use `scripts/graphify-query-safe.sh` for graph questions instead of raw grep
  - Rebuild the graph with `graphify cluster-only .` and raise `GRAPHIFY_VIZ_NODE_LIMIT` to generate HTML for the large corpus
  - Keep hooks and MCP templates disabled-by-default
  - Keep secrets out of config and config templates
- Validation run:
  - `opencode --version` -> `1.17.11`
  - `opencode debug config` -> merged global + project-local config loaded
  - `opencode mcp list` -> no MCP servers configured
  - `graphify install --project --platform opencode` -> project-scoped install path completed
  - `graphify opencode install` -> graphify plugin already registered, hook written
  - `graphify cluster-only .` -> graph updated, HTML skipped at default node limit
  - `GRAPHIFY_VIZ_NODE_LIMIT=20000 graphify cluster-only .` -> `graph.json`, `GRAPH_REPORT.md`, and `graph.html` updated
  - `scripts/graphify-query-safe.sh "What is this project about?"` -> success
  - `scripts/graphify-query-safe.sh "What are the main components and how do they connect?"` -> success
- Failed checks:
  - `graphify cluster-only .` skipped HTML at the default viz node limit
  - `opencode debug config` and `opencode mcp list` required a writable log path under `~/.local/share/opencode/log/` in this environment
- Next actions:
  - Keep using the local commands/agents/skills now that the workflow is installed
  - Re-run `graphify update .` after source edits if the graph becomes stale
  - Add MCP servers only when secrets and policies are explicitly approved

## OpenCode + Graphify Bootstrap (2026-06-26)

- Date: 2026-06-26
- Scope: Full project-local OpenCode + Graphify integration validation and documentation
- Changed files:
  - `.graphifyignore` (created)
  - `docs/GRAPHIFY_USAGE.md` (created)
  - `docs/PROJECT_CONTEXT.md` (updated)
  - `scripts/graphify-query-safe.sh` (created)
  - `AGENTS.md` (graphify install updated)
- Decisions:
  - Project-local OpenCode structure already exists under `.opencode/` with commands, agents, skills, tools, hooks, plugins
  - Graphify knowledge graph rebuilt (no-cluster mode) with 13779 nodes, 27381 edges
  - Safe query wrapper created at `scripts/graphify-query-safe.sh`
  - Graphify project-local install completed (skill, plugin, AGENTS.md section)
  - opencode.jsonc already has proper permissions with secret safety, edit gates, and dangerous-command requiring approval
  - Ruflo provides the orchestration MCP surface for additional coordination commands
  - Global skill catalog has 100+ skills; project-local hoodie-research-workflow skill installed
  - All hooks remain disabled-by-default (templates)
  - All MCP servers remain disabled-by-default (templates)
  - No commits or pushes performed
- Validation run:
  - `opencode --version`: 1.17.11 (OK)
  - `opencode debug config`: shows full config with permissions (OK)
  - `opencode mcp list`: no MCP servers (expected, OK)
  - `graphify --help`: available at ~/.local/bin/graphify (OK)
  - `graphify-out/graph.json`: exists, 13779 nodes (OK)
  - `graphify-out/GRAPH_REPORT.md`: exists (OK)
  - `graphify-out/graph.html`: exists (OK)
  - `scripts/graphify-query-safe.sh "What is this project about?"`: ran successfully, returned 20 nodes (OK)
  - `scripts/graphify-query-safe.sh "main components and connections"`: ran successfully, returned 88 nodes (OK)
- Failed checks: None
- Next actions:
  - Set GEMINI_API_KEY or equivalent for full semantic graph extraction (docs/papers/images)
  - Optionally enable hooks/MCP when needed
  - Run `graphify .` for full semantic rebuild when API key is available

## Dependency Verification + IMPLEMENTATION_PLAN Update (2026-06-26)

- Date: 2026-06-26
- Scope: Verify `.venv` dependency completeness for simulation/testing; update IMPLEMENTATION_PLAN with environment details
- Changed files:
  - `.venv/lib/python3.14/site-packages/numpy-2.5.0` (installed)
  - `.venv/lib/python3.14/site-packages/matplotlib-3.11.0` (installed)
  - `.venv/lib/python3.14/site-packages/pandas-3.0.3` (installed)
  - `docs/research-simulation/IMPLEMENTATION_PLAN.md` (section renumbered, environment section added)
  - `.ai/NEXT_ACTIONS.md` (updated)
  - `.ai/DECISIONS.md` (updated)
  - `.ai/PROJECT_MEMORY.md` (updated with venv info and known risks)
  - `docs/SESSION_CHECKPOINTS.md` (checkpoint appended)
- Decisions:
  - NumPy is installed in `.venv`; not required by core simulation (graceful fallback in `src/seed.py`) but needed by analysis scripts
  - `.venv/bin/python` is the exclusive interpreter for all simulation and testing
  - `IMPLEMENTATION_PLAN.md` is the single source of truth for the 7-phase roadmap (Phase 0–7)
- Validation run:
  - `grep "import numpy" src/` → only `src/seed.py` (try/except with graceful fallback)
  - No root-level `requirements.txt`, `setup.py`, or `pyproject.toml` found
  - `.venv/bin/python -c "import torch, numpy"` → PyTorch 2.12.1, NumPy 2.5.0 (OK)
  - `.venv/bin/python -c "import matplotlib, pandas"` → Matplotlib 3.11.0, Pandas 3.0.3 (OK)
- Failed checks: None
- Next actions:
  - Proceed with **Phase 0**: baseline fidelity audit & config correction
  - First fix: `configs/runtime_model.yml` capacities (1 → 0.5/0.5/3.0)
  - Then smoke test: `.venv/bin/python -m src.cli validation --config configs/smoke/smoke_validation_flc_hoodie.json`
