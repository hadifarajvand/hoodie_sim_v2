# Project AI Agent Instructions

## Mission

Use a precision-first workflow. Optimize for correctness, speed of implementation, repeatability, and verifiable results. Do not optimize primarily for token reduction.

## Stack

- OpenCode is the main executor.
- Graphify is the structural memory and architecture map.
- RuFlo is used for swarm coordination, hooks, procedural memory, routing, and background workers.
- CI/test/build output is the final truth.
- Humans approve production and irreversible actions.

OpenCode commands are the command surface.
RuFlo built-in agents are the real swarm workers.
Do not create duplicate OpenCode agents for RuFlo roles.
Custom OpenCode agents are allowed only for project-specific roles not covered by RuFlo.
Duplicate custom agents must stay archived under `.opencode/agents/_archived-ruflo-duplicates/`.

## Safety

Do not read or print secrets.
Do not edit `.env*`, private keys, certificates, or credential files.
Do not deploy production.
Do not modify DNS, billing, cloud resources, or production databases.
Do not delete files.
Do not commit or push unless explicitly asked.

## Default workflow

1. Inspect.
2. Create or update a plan in `docs/plans/`.
3. Use Graphify for architecture or cross-module tasks.
4. Use RuFlo only for large multi-agent work, audits, refactors, or repeated project workflows.
5. Implement minimal changes.
6. Run tests/build/lint/typecheck where available.
7. Review diff.
8. Write a run log in `docs/run-logs/`.

## Task routing

Small/local bug:
- OpenCode only.

Unknown architecture:
- Use Graphify first.

Feature touching multiple modules:
- Use `/graph-plan`, then `/swarm-feature`.

Security/auth/payment/backend/secrets:
- Add security-auditor review.
- Use read-only mode first.

Production/deployment:
- Use `/production-check`.
- No autonomous production deployment.

## Required proof

Before claiming completion, report:
- files created/changed
- commands run
- tests/build/lint/typecheck result
- known failures
- manual follow-up

<!-- AI_PRECISION_STACK_START -->
## AI Precision Stack Notes

- Keep the workflow layer project-local.
- Prefer `docs/ai-stack/` and `.opencode/` as the canonical sources for future agents.
- Use `docs/plans/` for every non-trivial task.
- Use `docs/run-logs/` for outcome capture after implementation or validation.
- Preserve unrelated worktree drift unless explicitly asked to resolve it.
<!-- AI_PRECISION_STACK_END -->
