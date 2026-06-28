# Orchestra Plan

## Detected Repository State

- Repository root: `/Users/hadi/Documents/GitHub/hoodie_sim_v2`
- Branch: `049-exposure-matrix-paper-mechanism-alignment`
- Current HEAD: `ba8ecfde22e8d266e6466847d1e3783a0f80671d`
- Git state: dirty
- `AGENTS.md`: present
- `opencode.json`: present
- `.opencode/`: present
- `.claude-flow/`: present
- `.swarm/`: present
- `.mcp.json`: present
- `graphify`: installed at `/Users/hadi/.local/bin/graphify`
- `npx ruflo@latest`: not usable here because npm registry access is blocked
- `opencode mcp list`: failed with a local log-path filesystem error

## Active Stack Boundary

- Ruflo is the active conductor.
- Graphify is the repo intelligence map.
- OpenCode is the cockpit.
- MCPs are controlled tools.
- ECC is inactive/passive reference only.
- No secrets, no commit, no push, no training without approval.
- No source implementation during audit/planning.
- One integrator edits only during implementation.
- Specialist agents inspect/propose only.
- Graphify must be read before major analysis.
- Ruflo memory search starts serious tasks.
- Ruflo memory store captures important decisions.
- Swarm mode is for audits/planning/large cross-module work.

## Graphify Status

- `graphify-out/GRAPH_REPORT.md`: present
- Graph size: 17,961 nodes / 28,401 edges / 1,368 communities
- Graph built from commit: `ba8ecfde`
- Freshness: current graph matches the current HEAD prefix and is effectively fresh
- Semantic extraction status: skipped in the build report because no LLM API key was available
- Missing outputs from the build report: `graph.html`, `graph.svg`, `graph.graphml`, `wiki/index.md`
- Known limitation: Graphify is a structural map, not a proof layer for paper-faithful correctness

## Ruflo MCP Status

- Configured in `opencode.json`
- Live CLI access is blocked here by network resolution failure against `registry.npmjs.org`
- Result: Ruflo MCP memory is not connected in this session

## Memory Seed Status

- Not completed
- Reason: no live Ruflo MCP memory tool was reachable from this environment

## Wrapper Commands Created Or Updated

- Updated: `.opencode/commands/orchestra-start.md`
- Updated: `.opencode/commands/ruflo-save.md`
- Updated: `.opencode/commands/ruflo-search.md`
- Updated: `.opencode/commands/ruflo-plan.md`
- Updated: `.opencode/commands/ruflo-implement-phase.md`
- Updated: `.opencode/commands/ruflo-review.md`
- Added: `.opencode/commands/ruflo-swarm-audit.md`
- Added: `.opencode/commands/graphify-refresh.md`

## Swarm Status

- Not initialized in this setup pass
- Reason: Ruflo CLI bootstrap is blocked by network access, so no live swarm session could be started

## Agents Registered

- Not registered in this setup pass
- Reason: swarm could not be started

## Phase 0 Verification Plan Summary

- Verify the paper-to-code baseline boundary before any Phase 2 implementation
- Audit the paper-faithful baseline assumptions, topology legality, runtime scaling, and test coverage gaps
- Treat all uncertain claims as `TO_VERIFY`
- Do not touch simulator source until Phase 0 is explicitly approved

## Next Commands The User Should Run

1. `/orchestra-start hoodie_sim_v2 Phase 0 baseline fidelity`
2. `/ruflo-swarm-audit Phase 0 baseline fidelity and paper-code alignment readiness`
3. Review this plan and the Graphify report together
4. Approve or reject Phase 0 verification implementation
5. Run `/ruflo-implement-phase Phase 0 verification only` only after approval

## Approval Required Before Edits

- Any simulator source change
- Any config change outside the approved setup boundary
- Any dependency installation
- Any training run
- Any commit or push
- Any global configuration change
- Any attempt to expose or store secrets
