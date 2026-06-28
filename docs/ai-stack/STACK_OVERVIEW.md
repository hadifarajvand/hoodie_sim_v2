# Precision Development Swarm

## Stack roles

OpenCode:
- main execution cockpit
- reads files
- edits files
- runs tests/builds
- invokes commands
- uses specialist agents
- calls Graphify/RuFlo MCP only through policy

Graphify:
- structural memory
- codebase map
- dependency tracing
- architecture discovery
- impact analysis
- PR/file risk analysis where supported

RuFlo:
- hierarchical-mesh swarm coordination
- specialist agent routing
- procedural memory
- task/session hooks
- background workers
- post-task learning

CI:
- final validation
- lint/typecheck/test/build truth source

Human:
- approves production
- approves destructive operations
- approves secrets/cloud/billing/DNS changes

## Operating rule

Small task:
OpenCode only.

Cross-file task:
OpenCode + Graphify.

Large/refactor/audit task:
OpenCode + Graphify + RuFlo swarm.

Production/deployment:
OpenCode can inspect and prepare; CI validates; human approves.

## Never do by default

- full 15-agent swarm
- pure mesh topology
- all MCP tools enabled for all agents
- database write MCP
- production MCP
- unverified RuFlo MCP memory as canonical truth
- unbounded background workers during active coding
