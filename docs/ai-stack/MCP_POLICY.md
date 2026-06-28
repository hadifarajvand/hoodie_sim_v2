# MCP Policy

MCP tools are capability surfaces. Expose them selectively.

## Default principle

Read/search tools are safer.
Write/action tools require tighter control.
Production tools are disabled by default.

## Recommended MCP layout

graphify_mcp:
- enabled for planner
- enabled for graph-analyst
- enabled for reviewer
- enabled for coder only when needed

ruflo_mcp:
- enabled for coordinator
- enabled for swarm commands
- enabled for memory specialist

docs/context MCP:
- enabled for researcher/planner only

github_mcp:
- enabled only for reviewer/release agent
- write actions require explicit approval

database_mcp:
- disabled by default
- read-only only when explicitly approved

production_mcp:
- disabled by default
- no autonomous production mutation

## Forbidden default MCP actions

- production deploy
- DNS mutation
- billing mutation
- cloud resource mutation
- secret rotation
- production database write
- email sending without explicit approval
- file deletion without explicit approval

## Validation

Before enabling any MCP server:
1. identify server purpose
2. list tools exposed
3. classify tools as read/write/destructive
4. restrict to specific agents
5. document in this file

## Template only

If the OpenCode schema supports MCP entries, keep them commented or template-only until verified.
