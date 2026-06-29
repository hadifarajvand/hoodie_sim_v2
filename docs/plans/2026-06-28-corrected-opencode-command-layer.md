# Corrected OpenCode Command Layer Plan

## Objective

Replace the project-local OpenCode slash-command docs with thin orchestration wrappers that route through RuFlo's built-in agents, hive-mind, hooks, memory, and Graphify instead of duplicating local agent behavior.

## Non-goals

- no application/source-code changes
- no dependency installation
- no production deployment
- no deletion of files
- no changes to local `.opencode/agents/` stubs in this pass

## Current understanding

- `.opencode/commands/` already exists, but its command files are local wrappers around project-specific agents.
- `coordinator.md` is missing and needs to be added.
- The repo already has `docs/plans/` and `docs/run-logs/` scaffolding.
- This task is documentation/control-plane work, not app logic work.

## Task classification

refactor

## RuFlo status

Planned, not yet executed for this change.

## Hive/swarm status

Not required for file edits; the command content will reference RuFlo hive/swarm workflow.

## Graphify status

Not required for the markdown rewrite itself.

## Memory findings

None yet. No RuFlo memory query is needed to rewrite command docs.

## Graphify findings

None. This task does not touch application modules.

## Affected files/modules

- `.opencode/commands/coordinator.md`
- `.opencode/commands/plan.md`
- `.opencode/commands/graph-plan.md`
- `.opencode/commands/implement.md`
- `.opencode/commands/swarm-feature.md`
- `.opencode/commands/verify.md`
- `.opencode/commands/review.md`
- `.opencode/commands/security-review.md`
- `.opencode/commands/swarm-audit.md`
- `.opencode/commands/production-check.md`
- `docs/plans/2026-06-28-corrected-opencode-command-layer.md`
- `docs/run-logs/2026-06-28-corrected-opencode-command-layer.md`

## Selected RuFlo built-in agents

- hierarchical-coordinator
- planner
- coder
- tester
- reviewer
- memory-specialist
- system-architect
- code-analyzer
- backend-dev
- security-architect
- security-auditor
- performance-engineer
- production-validator
- researcher
- api-docs

## Implementation steps

1. Add the missing `coordinator.md`.
2. Rewrite each command doc to use RuFlo built-in agents and hooks instead of local fake agents.
3. Keep the commands thin and scoped to orchestration, planning, implementation, verification, review, audit, and production-readiness.
4. Add the run log after the rewrite is complete.

## Validation gates

- confirm the intended files changed only
- run `git diff --check`
- inspect the final diff for scope drift

## Review gates

- ensure no command references custom local agent implementations as the primary workflow
- ensure no command proposes deployment, secret reads, or destructive behavior
- ensure the command set matches the requested command names

## Security gates

- no secrets
- no production mutation
- no deletion

## Production gates

- none; this task is documentation-only

## Rollback strategy

- revert only the command markdown and the new plan/run-log docs if the rewrite drifts from the requested orchestration layer

## Acceptance criteria

- the requested command files exist and contain RuFlo-oriented wrappers
- no new fake agent layer is introduced
- the plan and run log are present
- the diff stays inside the command-layer/docs scope
