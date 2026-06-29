# RuFlo Native Migration Report

Date: 2026-06-28
Agent/tool: Codex

## Summary

The OpenCode command center is now the active orchestration layer, and the generic OpenCode agent stubs have been archived instead of deleted. The command docs now point at RuFlo built-in roles and coordination patterns rather than duplicate local agent definitions.

## Existing OpenCode commands

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

## Existing OpenCode agents

Archived duplicates now live under:

- `.opencode/agents/_archived-ruflo-duplicates/coordinator.md`
- `.opencode/agents/_archived-ruflo-duplicates/coder.md`
- `.opencode/agents/_archived-ruflo-duplicates/tester.md`
- `.opencode/agents/_archived-ruflo-duplicates/reviewer.md`
- `.opencode/agents/_archived-ruflo-duplicates/security-auditor.md`
- `.opencode/agents/_archived-ruflo-duplicates/performance-engineer.md`
- `.opencode/agents/_archived-ruflo-duplicates/graph-analyst.md`

## Duplicate custom agents archived

All current custom agents duplicated RuFlo-style built-ins or command-center roles:

- `coordinator.md`
- `coder.md`
- `tester.md`
- `reviewer.md`
- `security-auditor.md`
- `performance-engineer.md`
- `graph-analyst.md`

## Project-specific rules preserved

No meaningful project-specific rules were found in the archived agent files. They were generic role descriptions, so archiving them did not lose active project policy.

Preserved policy updates:

- `AGENTS.md` now states that OpenCode commands are the command surface, RuFlo built-ins are the real workers, duplicate agents must stay archived, and custom agents are only for project-specific roles.
- `docs/ai-stack/AGENT_POLICY.md` now declares RuFlo built-ins as the source of truth and explicitly lists roles that should not be duplicated.

## Files moved

- `.opencode/agents/coordinator.md`
- `.opencode/agents/coder.md`
- `.opencode/agents/tester.md`
- `.opencode/agents/reviewer.md`
- `.opencode/agents/security-auditor.md`
- `.opencode/agents/performance-engineer.md`
- `.opencode/agents/graph-analyst.md`

## Commands rewritten

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

## Validation

Executed:

- `find .opencode -maxdepth 3 -type f 2>/dev/null | sort || true`
- `find docs/ai-stack -maxdepth 2 -type f 2>/dev/null | sort || true`
- `find .opencode/commands -maxdepth 1 -type f | sort`
- `find .opencode/agents -maxdepth 2 -type f 2>/dev/null | sort || true`
- `git status --short || true`
- `npx ruflo@latest agent --help || true`
- `npx ruflo@latest agent list || true`
- `npx ruflo@latest daemon status || true`
- `npx ruflo@latest hive-mind status || true`

Results:

- The command directory contains the ten requested command files.
- The agent directory now contains only archived duplicates.
- `npx ruflo@latest` could not be verified in this environment because npm failed DNS resolution for `registry.npmjs.org` (`ENOTFOUND`).

## RuFlo built-ins verified

- Not verified locally in this environment because `npx ruflo@latest` could not reach the npm registry.

## Unavailable RuFlo agents

Not verified. The installed RuFlo CLI could not be queried due the network resolution failure above.

## Manual follow-up

- Re-run the RuFlo CLI checks in an environment with npm registry access.
- If you want to restore any archived agent, restore it explicitly from `.opencode/agents/_archived-ruflo-duplicates/`.

## Exact next command

`/coordinator "health check this AI command center and verify RuFlo native agent routing"`
