# Bootstrap AI Stack Plan

## Objective

Create a project-local precision-first AI workflow layer for OpenCode, Graphify, and RuFlo without touching application/business logic.

## Non-goals

- no app feature changes
- no secret reads
- no production deployment
- no dependency installation for the app
- no destructive commands

## Current understanding

- The repo already had unrelated source/docs drift before bootstrap.
- OpenCode is installed locally.
- Graphify is installed locally and can generate `graphify-out/`.
- RuFlo is available through `npx` and now initialized locally.

## Affected files/modules

- `AGENTS.md`
- `opencode.jsonc`
- `.opencode/`
- `docs/ai-stack/`
- `docs/TESTING.md`
- `docs/DEPLOYMENT.md`
- `docs/decisions/0001-precision-development-stack.md`
- `docs/run-logs/`
- `.claude/` and `.claude-flow/` runtime files created by RuFlo
- `.mcp.json`
- `CLAUDE.md`

## Graphify needed?

Yes.

## RuFlo needed?

Yes.

## Agent roles needed

- coordinator
- graph-analyst
- tester
- reviewer
- security-auditor only for security-sensitive follow-up

## Implementation steps

1. Inspect environment and existing workflow files.
2. Create local workflow docs and OpenCode config.
3. Create specialist agent and slash-command scaffolding.
4. Generate a Graphify graph.
5. Initialize RuFlo runtime and memory.
6. Align runtime config with project policy.
7. Record validation and results.

## Validation gates

- file existence checks
- OpenCode version check
- Graphify availability and graph generation
- RuFlo availability, init, memory init, config get/set, memory store/search

## Rollback strategy

- Do not touch application source.
- Only remove bootstrap files if the user explicitly asks for rollback.

## Risks

- The repo already contains many unrelated modifications.
- RuFlo generated runtime files that needed manual alignment.
- Graphify graph generation required escalation after an initial sandbox permission failure.

## Acceptance criteria

- workflow docs exist
- OpenCode config exists
- Graphify graph exists
- RuFlo runtime is initialized
- seed memory entries are stored and searchable
- final validation report is written
